"""
Document Service for Laser OS.

This service handles document upload, validation, storage, and deletion
for project documents (quotes, invoices, POPs, delivery notes).

Phase 9 Implementation.
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app

from app import db
from app.models import ProjectDocument, Project
from app.services.activity_logger import log_activity


def allowed_file(filename: str, allowed_extensions: Optional[set] = None) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file to check
        allowed_extensions: Set of allowed extensions (defaults to config)
    
    Returns:
        bool: True if file extension is allowed
    
    Example:
        >>> allowed_file('quote.pdf')
        True
        >>> allowed_file('malware.exe')
        False
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_DOCUMENT_EXTENSIONS', {'pdf', 'jpg', 'png'})
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_size_mb(file: FileStorage) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file: FileStorage object
    
    Returns:
        float: File size in MB
    """
    # Seek to end to get size
    file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    # Seek back to beginning
    file.seek(0)
    return size_bytes / (1024 * 1024)


def generate_unique_filename(original_filename: str, project_id: int, document_type: str) -> str:
    """
    Generate a unique filename for a document.
    
    Args:
        original_filename: Original filename from upload
        project_id: Project ID
        document_type: Type of document (Quote, Invoice, etc.)
    
    Returns:
        str: Unique filename
    
    Example:
        >>> generate_unique_filename('quote.pdf', 1, 'Quote')
        'project_1_quote_20240115_143022_abc123.pdf'
    """
    # Get file extension
    extension = ''
    if '.' in original_filename:
        extension = '.' + original_filename.rsplit('.', 1)[1].lower()
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create hash of original filename for uniqueness
    hash_suffix = hashlib.md5(original_filename.encode()).hexdigest()[:6]
    
    # Sanitize document type
    doc_type_safe = document_type.lower().replace(' ', '_')
    
    # Construct filename
    filename = f'project_{project_id}_{doc_type_safe}_{timestamp}_{hash_suffix}{extension}'
    
    return filename


def get_document_folder(document_type: str) -> Path:
    """
    Get the folder path for a document type.

    Args:
        document_type: Type of document (Quote, Invoice, Proof of Payment, Delivery Note, Other, Image)

    Returns:
        Path: Path to the document folder
    """
    base_folder = Path(current_app.config['DOCUMENTS_FOLDER'])

    # Map document types to folder names
    folder_map = {
        'Quote': 'quotes',
        'Invoice': 'invoices',
        'Proof of Payment': 'pops',
        'Delivery Note': 'delivery_notes',
        'Other': 'other',
        'Image': 'images'
    }

    folder_name = folder_map.get(document_type, 'other')
    return base_folder / folder_name


def save_documents(
    files: list,
    project_id: int,
    document_type: str,
    notes: Optional[str] = None,
    uploaded_by: str = 'admin'
) -> Dict[str, Any]:
    """
    Save multiple document files and create database records.

    Args:
        files: List of FileStorage objects from request.files.getlist()
        project_id: Project ID to link the documents
        document_type: Type of document (Quote, Invoice, Proof of Payment, Delivery Note)
        notes: Optional notes about the documents (applies to all)
        uploaded_by: Username of uploader (default: 'admin')

    Returns:
        dict: Result with 'success', 'message', 'uploaded_count', 'failed_count', 'errors'

    Example:
        >>> files = request.files.getlist('files')
        >>> result = save_documents(files, project_id=1, document_type='Quote')
        >>> print(f"Uploaded {result['uploaded_count']} files")
    """
    uploaded_count = 0
    failed_count = 0
    error_messages = []
    document_ids = []

    for file in files:
        # Skip empty filenames
        if not file or file.filename == '':
            continue

        # Use the single file save_document function
        result = save_document(file, project_id, document_type, notes, uploaded_by)

        if result['success']:
            uploaded_count += 1
            document_ids.append(result['document_id'])
        else:
            failed_count += 1
            error_messages.append(f"{file.filename}: {result['message']}")

    # Build response message
    if uploaded_count > 0 and failed_count == 0:
        message = f'{uploaded_count} document(s) uploaded successfully'
        success = True
    elif uploaded_count > 0 and failed_count > 0:
        message = f'{uploaded_count} document(s) uploaded, {failed_count} failed'
        success = True  # Partial success
    elif failed_count > 0:
        message = f'{failed_count} document(s) failed to upload'
        success = False
    else:
        message = 'No files to upload'
        success = False

    return {
        'success': success,
        'message': message,
        'uploaded_count': uploaded_count,
        'failed_count': failed_count,
        'errors': error_messages,
        'document_ids': document_ids
    }


def save_document(
    file: FileStorage,
    project_id: int,
    document_type: str,
    notes: Optional[str] = None,
    uploaded_by: str = 'admin'
) -> Dict[str, Any]:
    """
    Save a document file and create database record.

    Args:
        file: FileStorage object from request.files
        project_id: Project ID to link the document
        document_type: Type of document (Quote, Invoice, Proof of Payment, Delivery Note)
        notes: Optional notes about the document
        uploaded_by: Username of uploader (default: 'admin')

    Returns:
        dict: Result with 'success', 'message', and optionally 'document_id', 'document'

    Example:
        >>> from werkzeug.datastructures import FileStorage
        >>> file = request.files['file']
        >>> result = save_document(file, project_id=1, document_type='Quote')
        >>> if result['success']:
        ...     print(f"Document saved: {result['document'].filename}")
    """
    try:
        # Validate file
        if not file:
            return {'success': False, 'message': 'No file provided'}
        
        if file.filename == '':
            return {'success': False, 'message': 'No file selected'}
        
        if not allowed_file(file.filename):
            allowed = current_app.config.get('ALLOWED_DOCUMENT_EXTENSIONS', {'pdf'})
            return {
                'success': False,
                'message': f'File type not allowed. Allowed types: {", ".join(allowed)}'
            }
        
        # Check file size
        file_size_mb = get_file_size_mb(file)
        max_size_mb = current_app.config.get('MAX_UPLOAD_SIZE', 52428800) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            return {
                'success': False,
                'message': f'File too large. Maximum size: {max_size_mb:.1f} MB'
            }
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return {'success': False, 'message': f'Project {project_id} not found'}
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename, project_id, document_type)
        
        # Get document folder
        document_folder = get_document_folder(document_type)
        document_folder.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = document_folder / unique_filename
        
        # Save file to disk
        file.save(str(file_path))

        # Get actual file size in bytes after saving
        file_size_bytes = file_path.stat().st_size

        # Create database record
        document = ProjectDocument(
            project_id=project_id,
            document_type=document_type,
            stored_filename=unique_filename,
            original_filename=original_filename,
            file_path=str(file_path),
            file_size=file_size_bytes,
            notes=notes,
            uploaded_by=uploaded_by
        )
        
        db.session.add(document)
        db.session.commit()

        # Log activity
        log_activity(
            'PROJECT_DOCUMENT',
            document.id,
            'UPLOADED',
            {
                'project_id': project_id,
                'project_code': project.project_code,
                'document_type': document_type,
                'filename': original_filename,
                'size_mb': round(file_size_bytes / (1024 * 1024), 2)
            },
            user=uploaded_by
        )
        
        return {
            'success': True,
            'message': f'{document_type} uploaded successfully',
            'document_id': document.id,
            'document': document
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Failed to save document: {str(e)}'
        }


def delete_document(document_id: int, deleted_by: str = 'admin') -> Dict[str, Any]:
    """
    Delete a document file and database record.
    
    Args:
        document_id: ID of the document to delete
        deleted_by: Username of person deleting (default: 'admin')
    
    Returns:
        dict: Result with 'success' and 'message'
    
    Example:
        >>> result = delete_document(document_id=5)
        >>> if result['success']:
        ...     print("Document deleted successfully")
    """
    try:
        # Get document
        document = ProjectDocument.query.get(document_id)
        if not document:
            return {'success': False, 'message': f'Document {document_id} not found'}
        
        # Store info for logging
        project_id = document.project_id
        project_code = document.project.project_code if document.project else 'Unknown'
        document_type = document.document_type
        filename = document.original_filename
        
        # Delete file from disk
        file_path = Path(document.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                # Log error but continue with database deletion
                print(f'Warning: Could not delete file {file_path}: {e}')
        
        # Delete database record
        db.session.delete(document)
        db.session.commit()
        
        # Log activity
        log_activity(
            'PROJECT_DOCUMENT',
            document_id,
            'DELETED',
            {
                'project_id': project_id,
                'project_code': project_code,
                'document_type': document_type,
                'filename': filename
            },
            user=deleted_by
        )
        
        return {
            'success': True,
            'message': f'{document_type} deleted successfully'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Failed to delete document: {str(e)}'
        }


def get_project_documents(project_id: int, document_type: Optional[str] = None) -> list:
    """
    Get all documents for a project, optionally filtered by type.
    
    Args:
        project_id: Project ID
        document_type: Optional document type filter
    
    Returns:
        list: List of ProjectDocument objects
    
    Example:
        >>> documents = get_project_documents(project_id=1, document_type='Quote')
        >>> for doc in documents:
        ...     print(f"{doc.document_type}: {doc.original_filename}")
    """
    query = ProjectDocument.query.filter_by(project_id=project_id)

    if document_type:
        query = query.filter_by(document_type=document_type)

    return query.order_by(ProjectDocument.upload_date.desc()).all()


def validate_document_upload(file: FileStorage, document_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a document upload without saving it.
    
    Args:
        file: FileStorage object
        document_type: Type of document
    
    Returns:
        tuple: (is_valid, error_message)
    
    Example:
        >>> valid, error = validate_document_upload(file, 'Quote')
        >>> if not valid:
        ...     print(f"Validation error: {error}")
    """
    # Check file exists
    if not file or file.filename == '':
        return False, 'No file selected'
    
    # Check file extension
    if not allowed_file(file.filename):
        allowed = current_app.config.get('ALLOWED_DOCUMENT_EXTENSIONS', {'pdf'})
        return False, f'File type not allowed. Allowed types: {", ".join(allowed)}'
    
    # Check file size
    file_size_mb = get_file_size_mb(file)
    max_size_mb = current_app.config.get('MAX_UPLOAD_SIZE', 52428800) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        return False, f'File too large. Maximum size: {max_size_mb:.1f} MB'
    
    # Check document type is valid
    from app.models import ProjectDocument
    if document_type not in ProjectDocument.VALID_TYPES:
        return False, f'Invalid document type. Must be one of: {", ".join(ProjectDocument.VALID_TYPES)}'

    return True, None

