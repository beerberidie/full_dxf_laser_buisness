"""
Module N - File Validation Utilities
Validates uploaded files for security and compatibility
"""

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

# Maximum file sizes (bytes)
MAX_FILE_SIZES = {
    'dxf': 50 * 1024 * 1024,      # 50 MB
    'lbrn2': 50 * 1024 * 1024,    # 50 MB
    'pdf': 20 * 1024 * 1024,      # 20 MB
    'excel': 10 * 1024 * 1024,    # 10 MB
    'image': 10 * 1024 * 1024,    # 10 MB
    'text': 5 * 1024 * 1024,      # 5 MB
    'word': 10 * 1024 * 1024,     # 10 MB
    'default': 50 * 1024 * 1024   # 50 MB
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/dxf',
    'application/octet-stream',  # DXF, LBRN2
    'application/pdf',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
    'image/gif',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

# Allowed extensions
ALLOWED_EXTENSIONS = {
    '.dxf', '.DXF',
    '.lbrn2', '.LBRN2',
    '.pdf', '.PDF',
    '.xlsx', '.xls', '.XLSX', '.XLS',
    '.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF',
    '.txt', '.TXT',
    '.doc', '.docx', '.DOC', '.DOCX'
}


async def validate_file(file: UploadFile) -> Dict[str, Any]:
    """
    Validate uploaded file.
    
    Checks:
    - File extension
    - File size
    - MIME type
    - Content verification
    
    Args:
        file: FastAPI UploadFile object
    
    Returns:
        Dict with 'valid' (bool) and 'error' (str) keys
    """
    # Check extension
    ext = Path(file.filename).suffix
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Invalid file extension: {ext} for file {file.filename}")
        return {
            'valid': False,
            'error': f'File extension not allowed: {ext}. Allowed: {", ".join(sorted(set([e.lower() for e in ALLOWED_EXTENSIONS])))}'
        }
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Reset file pointer
    await file.seek(0)
    
    # Check file size
    file_type = ext.lower().replace('.', '')
    if file_type in ['xlsx', 'xls']:
        file_type = 'excel'
    elif file_type in ['jpg', 'jpeg', 'png', 'gif']:
        file_type = 'image'
    elif file_type in ['doc', 'docx']:
        file_type = 'word'
    
    max_size = MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['default'])
    
    if file_size > max_size:
        logger.warning(f"File too large: {file_size} bytes (max: {max_size}) for {file.filename}")
        return {
            'valid': False,
            'error': f'File too large: {file_size:,} bytes (max: {max_size:,} bytes = {max_size // 1024 // 1024} MB)'
        }
    
    # Check MIME type (if python-magic is available)
    try:
        if MAGIC_AVAILABLE:
            mime = magic.from_buffer(content, mime=True)
            logger.info(f"Detected MIME type: {mime} for {file.filename}")
        else:
            mime = 'application/octet-stream'  # Default if magic not available
            logger.warning("python-magic not available, skipping MIME type detection")
        
        if mime not in ALLOWED_MIME_TYPES:
            # Allow some exceptions for DXF/LBRN2
            if ext.lower() not in ['.dxf', '.lbrn2']:
                logger.warning(f"Invalid MIME type: {mime} for {file.filename}")
                return {
                    'valid': False,
                    'error': f'MIME type not allowed: {mime}'
                }
    except Exception as e:
        logger.error(f"MIME type detection failed for {file.filename}: {str(e)}")
        # Continue without MIME validation if magic fails
        pass
    
    # Additional content validation
    if ext.lower() == '.dxf':
        # Check for DXF header
        if not content.startswith(b'0\r\nSECTION') and not content.startswith(b'0\nSECTION'):
            logger.warning(f"Invalid DXF file format for {file.filename}")
            return {
                'valid': False,
                'error': 'Invalid DXF file format (missing SECTION header)'
            }
    
    elif ext.lower() == '.lbrn2':
        # Check for XML header
        if not content.startswith(b'<?xml') and not content.startswith(b'<LightBurnProject'):
            logger.warning(f"Invalid LBRN2 file format for {file.filename}")
            return {
                'valid': False,
                'error': 'Invalid LBRN2 file format (not XML)'
            }
    
    elif ext.lower() == '.pdf':
        # Check for PDF header
        if not content.startswith(b'%PDF'):
            logger.warning(f"Invalid PDF file format for {file.filename}")
            return {
                'valid': False,
                'error': 'Invalid PDF file format (missing %PDF header)'
            }
    
    logger.info(f"File validation passed for {file.filename} ({file_size:,} bytes)")
    return {'valid': True, 'error': None}


def detect_file_type(filename: str, mode: str = "AUTO") -> str:
    """
    Detect file type from filename extension.
    
    Args:
        filename: Name of the file
        mode: Processing mode (AUTO or specific type)
    
    Returns:
        File type string ('dxf', 'pdf', 'excel', etc.)
    """
    if mode != "AUTO":
        return mode.lower()
    
    ext = Path(filename).suffix.lower()
    
    type_map = {
        '.dxf': 'dxf',
        '.lbrn2': 'lbrn2',
        '.pdf': 'pdf',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.txt': 'text',
        '.doc': 'word',
        '.docx': 'word'
    }
    
    return type_map.get(ext, 'unknown')


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    from werkzeug.utils import secure_filename
    return secure_filename(filename)

