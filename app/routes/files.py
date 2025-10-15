"""
File management routes for DXF file uploads and management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from app import db
from app.models import DesignFile, Project, ActivityLog
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

bp = Blueprint('files', __name__, url_prefix='/files')


def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed_extensions = {'.dxf', '.DXF'}
    return os.path.splitext(filename)[1] in allowed_extensions


def get_upload_folder(project_id):
    """Get upload folder for a project."""
    base_folder = current_app.config.get('UPLOAD_FOLDER', 'data/files/projects')
    project_folder = os.path.join(base_folder, str(project_id))
    
    # Create folder if it doesn't exist
    os.makedirs(project_folder, exist_ok=True)
    
    return project_folder


def generate_stored_filename(original_filename):
    """Generate a unique stored filename."""
    # Get file extension
    ext = os.path.splitext(original_filename)[1]
    
    # Generate unique filename with timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{timestamp}_{unique_id}{ext}"


@bp.route('/upload/<int:project_id>', methods=['POST'])
def upload(project_id):
    """Upload a file to a project."""
    # Get project
    project = Project.query.get_or_404(project_id)
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('projects.detail', id=project_id))
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('projects.detail', id=project_id))
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        flash('Only DXF files are allowed', 'error')
        return redirect(url_for('projects.detail', id=project_id))
    
    try:
        # Get original filename
        original_filename = secure_filename(file.filename)
        
        # Generate stored filename
        stored_filename = generate_stored_filename(original_filename)
        
        # Get upload folder
        upload_folder = get_upload_folder(project_id)
        
        # Full file path
        file_path = os.path.join(upload_folder, stored_filename)
        
        # Save file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Get notes from form
        notes = request.form.get('notes', '').strip()
        
        # Create database record
        design_file = DesignFile(
            project_id=project_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            file_type='dxf',
            uploaded_by='System',  # TODO: Add user authentication
            notes=notes if notes else None
        )
        
        db.session.add(design_file)
        db.session.commit()
        
        # Log activity
        activity = ActivityLog(
            entity_type='FILE',
            entity_id=design_file.id,
            action='UPLOADED',
            details=f'Uploaded file: {original_filename} ({design_file.file_size_mb} MB) to project {project.project_code}',
            user='System'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'File "{original_filename}" uploaded successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error uploading file: {str(e)}', 'error')
        
        # Clean up file if it was saved
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return redirect(url_for('projects.detail', id=project_id))


@bp.route('/<int:file_id>')
def detail(file_id):
    """View file details."""
    design_file = DesignFile.query.get_or_404(file_id)
    
    # Get activity logs
    logs = ActivityLog.query.filter_by(
        entity_type='FILE',
        entity_id=file_id
    ).order_by(ActivityLog.created_at.desc()).all()
    
    return render_template('files/detail.html', file=design_file, logs=logs)


@bp.route('/download/<int:file_id>')
def download(file_id):
    """Download a file."""
    design_file = DesignFile.query.get_or_404(file_id)
    
    # Check if file exists
    if not os.path.exists(design_file.file_path):
        flash('File not found on disk', 'error')
        return redirect(url_for('projects.detail', id=design_file.project_id))
    
    try:
        # Log activity
        activity = ActivityLog(
            entity_type='FILE',
            entity_id=file_id,
            action='DOWNLOADED',
            details=f'Downloaded file: {design_file.original_filename}',
            user='System'
        )
        db.session.add(activity)
        db.session.commit()
        
        # Send file
        return send_file(
            design_file.file_path,
            as_attachment=True,
            download_name=design_file.original_filename
        )
        
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('projects.detail', id=design_file.project_id))


@bp.route('/delete/<int:file_id>', methods=['POST'])
def delete(file_id):
    """Delete a file."""
    design_file = DesignFile.query.get_or_404(file_id)
    project_id = design_file.project_id
    original_filename = design_file.original_filename
    file_path = design_file.file_path
    
    try:
        # Log activity before deletion
        activity = ActivityLog(
            entity_type='FILE',
            entity_id=file_id,
            action='DELETED',
            details=f'Deleted file: {original_filename}',
            user='System'
        )
        db.session.add(activity)
        
        # Delete from database
        db.session.delete(design_file)
        db.session.commit()
        
        # Delete physical file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        flash(f'File "{original_filename}" deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting file: {str(e)}', 'error')
    
    return redirect(url_for('projects.detail', id=project_id))


@bp.route('/list/<int:project_id>')
def list_files(project_id):
    """List all files for a project (API endpoint)."""
    project = Project.query.get_or_404(project_id)
    
    files = DesignFile.query.filter_by(project_id=project_id).order_by(
        DesignFile.upload_date.desc()
    ).all()
    
    return jsonify({
        'project_id': project_id,
        'project_code': project.project_code,
        'total_files': len(files),
        'files': [f.to_dict() for f in files]
    })

