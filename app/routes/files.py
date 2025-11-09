"""
File management routes for DXF file uploads and management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required
from app import db
from app.models import DesignFile, Project, ActivityLog
from app.utils.decorators import role_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import zipfile
from io import BytesIO
from pathlib import Path

bp = Blueprint('files', __name__, url_prefix='/files')


def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed_extensions = {'.dxf', '.DXF', '.lbrn2', '.LBRN2'}
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
@role_required('admin', 'manager', 'operator')
def upload(project_id):
    """Upload one or more files to a project."""
    # Get project
    project = Project.query.get_or_404(project_id)

    # Check if files were uploaded (support both 'files' and 'file' for backward compatibility)
    files = request.files.getlist('files')
    if not files or (len(files) == 1 and files[0].filename == ''):
        # Fallback to single file upload for backward compatibility
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                files = [file]
            else:
                flash('No file selected', 'error')
                return redirect(url_for('projects.detail', id=project_id))
        else:
            flash('No file selected', 'error')
            return redirect(url_for('projects.detail', id=project_id))

    # Get notes from form (applies to all files)
    notes = request.form.get('notes', '').strip()

    # Track upload results
    uploaded_count = 0
    failed_count = 0
    error_messages = []

    # Process each file
    for file in files:
        # Skip empty filenames
        if file.filename == '':
            continue

        # Check if file type is allowed
        if not allowed_file(file.filename):
            failed_count += 1
            error_messages.append(f'{file.filename}: Only DXF and LightBurn (.lbrn2) files are allowed')
            continue

        try:
            # Get original filename
            original_filename = secure_filename(file.filename)

            # Generate stored filename
            stored_filename = generate_stored_filename(original_filename)

            # Get upload folder
            upload_folder = get_upload_folder(project_id)

            # Full file path for saving
            full_file_path = os.path.join(upload_folder, stored_filename)

            # Save file
            file.save(full_file_path)

            # Get file size
            file_size = os.path.getsize(full_file_path)

            # Store relative path in database (relative to UPLOAD_FOLDER)
            # Format: {project_id}/{stored_filename}
            relative_path = os.path.join(str(project_id), stored_filename)

            # Detect file type from extension
            file_ext = os.path.splitext(original_filename)[1].lower()
            if file_ext in ['.lbrn2', '.LBRN2']:
                file_type = 'lbrn2'
            else:
                file_type = 'dxf'

            # Create database record
            design_file = DesignFile(
                project_id=project_id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=relative_path,  # Store relative path
                file_size=file_size,
                file_type=file_type,  # Set correct file type
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

            uploaded_count += 1

        except Exception as e:
            db.session.rollback()
            failed_count += 1
            error_messages.append(f'{file.filename}: {str(e)}')

            # Clean up file if it was saved
            if 'full_file_path' in locals() and os.path.exists(full_file_path):
                os.remove(full_file_path)

    # Display appropriate flash messages
    if uploaded_count > 0:
        if uploaded_count == 1:
            flash(f'1 file uploaded successfully', 'success')
        else:
            flash(f'{uploaded_count} files uploaded successfully', 'success')

    if failed_count > 0:
        if failed_count == 1:
            flash(f'1 file failed to upload', 'error')
        else:
            flash(f'{failed_count} files failed to upload', 'error')

        # Show individual error messages
        for error_msg in error_messages[:5]:  # Limit to first 5 errors
            flash(error_msg, 'error')

        if len(error_messages) > 5:
            flash(f'... and {len(error_messages) - 5} more errors', 'error')

    return redirect(url_for('projects.detail', id=project_id))


@bp.route('/<int:file_id>')
@login_required
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
@login_required
def download(file_id):
    """Download a file."""
    design_file = DesignFile.query.get_or_404(file_id)

    # Construct full file path from relative path stored in database
    base_folder = current_app.config.get('UPLOAD_FOLDER')

    # Ensure we use absolute path with proper normalization
    full_file_path = os.path.abspath(os.path.join(base_folder, design_file.file_path))

    # Debug logging
    current_app.logger.info(f"Download request for file {file_id}")
    current_app.logger.info(f"  Relative path: {design_file.file_path}")
    current_app.logger.info(f"  Base folder: {base_folder}")
    current_app.logger.info(f"  Full path: {full_file_path}")
    current_app.logger.info(f"  File exists: {os.path.exists(full_file_path)}")

    # Check if file exists
    if not os.path.exists(full_file_path):
        flash(f'File not found on disk: {design_file.original_filename}', 'error')
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

        # Send file with absolute path - use Path for better Windows compatibility
        from pathlib import Path
        file_path_obj = Path(full_file_path)

        return send_file(
            file_path_obj,
            as_attachment=True,
            download_name=design_file.original_filename
        )

    except Exception as e:
        current_app.logger.error(f"Error downloading file {file_id}: {str(e)}")
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('projects.detail', id=design_file.project_id))


@bp.route('/delete/<int:file_id>', methods=['POST'])
@role_required('admin', 'manager')
def delete(file_id):
    """Delete a file."""
    design_file = DesignFile.query.get_or_404(file_id)
    project_id = design_file.project_id
    original_filename = design_file.original_filename

    # Construct full file path from relative path
    base_folder = current_app.config.get('UPLOAD_FOLDER')
    full_file_path = os.path.join(base_folder, design_file.file_path)

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
        if os.path.exists(full_file_path):
            os.remove(full_file_path)

        flash(f'File "{original_filename}" deleted successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting file: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=project_id))


@bp.route('/list/<int:project_id>')
@login_required
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


@bp.route('/download-all/<int:project_id>')
@login_required
def download_all(project_id):
    """Download all design files for a project as a ZIP archive."""
    # Get project
    project = Project.query.get_or_404(project_id)

    # Get all design files for this project
    design_files = DesignFile.query.filter_by(project_id=project_id).order_by(
        DesignFile.upload_date.desc()
    ).all()

    # Handle edge case: no files
    if not design_files:
        flash('No design files to download for this project', 'warning')
        return redirect(url_for('projects.detail', id=project_id))

    # Handle edge case: single file - redirect to single file download
    if len(design_files) == 1:
        return redirect(url_for('files.download', file_id=design_files[0].id))

    try:
        # Create ZIP file in memory
        memory_file = BytesIO()

        # Get base folder for file paths
        base_folder = current_app.config.get('UPLOAD_FOLDER')

        # Track statistics for logging
        files_added = 0
        files_missing = 0
        total_size = 0

        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for design_file in design_files:
                # Construct full file path
                full_file_path = os.path.abspath(os.path.join(base_folder, design_file.file_path))

                # Check if file exists
                if not os.path.exists(full_file_path):
                    current_app.logger.warning(f"File not found: {full_file_path}")
                    files_missing += 1
                    continue

                # Add file to ZIP with original filename
                # Use arcname to set the filename inside the ZIP
                zf.write(full_file_path, arcname=design_file.original_filename)
                files_added += 1
                total_size += design_file.file_size

                current_app.logger.info(f"Added to ZIP: {design_file.original_filename}")

        # Check if any files were added
        if files_added == 0:
            flash('No files could be added to the archive. Files may be missing from disk.', 'error')
            return redirect(url_for('projects.detail', id=project_id))

        # Seek to beginning of BytesIO buffer
        memory_file.seek(0)

        # Generate ZIP filename using project code
        zip_filename = f"{project.project_code}-DesignFiles.zip"

        # Log activity
        activity = ActivityLog(
            entity_type='PROJECT',
            entity_id=project_id,
            action='DOWNLOAD_ALL',
            details=f'Downloaded {files_added} design files as ZIP archive ({round(total_size / (1024 * 1024), 2)} MB total)',
            user='System'  # TODO: Use current_user when available
        )
        db.session.add(activity)
        db.session.commit()

        # Show warning if some files were missing
        if files_missing > 0:
            flash(f'Warning: {files_missing} file(s) were missing and not included in the archive', 'warning')

        # Send ZIP file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )

    except Exception as e:
        current_app.logger.error(f"Error creating ZIP archive for project {project_id}: {str(e)}")
        flash(f'Error creating ZIP archive: {str(e)}', 'error')
        return redirect(url_for('projects.detail', id=project_id))

