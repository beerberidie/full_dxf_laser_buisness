"""
Laser OS Tier 1 - Projects Routes

This module handles all project/job-related routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app import db
from app.models import Project, Client, ActivityLog, ProjectDocument
from app.services.id_generator import generate_project_code
from app.services.activity_logger import log_activity
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
import os
from pathlib import Path

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('/')
def index():
    """
    List all projects with optional filtering.

    Query Parameters:
        search: Search term for project name or code
        client_id: Filter by client ID
        status: Filter by project status
        page: Page number for pagination

    Returns:
        Rendered template with project list
    """
    # Get query parameters
    search = request.args.get('search', '').strip()
    client_id = request.args.get('client_id', type=int)
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Build query
    query = Project.query

    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Project.name.ilike(f'%{search}%'),
                Project.project_code.ilike(f'%{search}%'),
                Project.description.ilike(f'%{search}%')
            )
        )

    if client_id:
        query = query.filter_by(client_id=client_id)

    if status:
        query = query.filter_by(status=status)

    # Order by created date (newest first)
    query = query.order_by(Project.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    projects = pagination.items

    # Get all clients for filter dropdown
    clients = Client.query.order_by(Client.name).all()

    return render_template(
        'projects/list.html',
        projects=projects,
        clients=clients,
        pagination=pagination,
        search=search,
        selected_client_id=client_id,
        selected_status=status,
        statuses=Project.VALID_STATUSES
    )



@bp.route('/new', methods=['GET', 'POST'])
def new_project():
    """
    Create a new project.

    GET: Display the new project form
    POST: Process the form and create the project

    Returns:
        GET: Rendered form template
        POST: Redirect to project detail page
    """
    if request.method == 'POST':
        # Get form data
        client_id = request.form.get('client_id', type=int)
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', Project.STATUS_REQUEST).strip()  # Phase 9: Default to REQUEST
        quote_date_str = request.form.get('quote_date', '').strip()
        approval_date_str = request.form.get('approval_date', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        quoted_price_str = request.form.get('quoted_price', '').strip()
        notes = request.form.get('notes', '').strip()

        # Phase 9: New fields
        material_type = request.form.get('material_type', '').strip() or None
        material_quantity_sheets = request.form.get('material_quantity_sheets', type=int) or None
        parts_quantity = request.form.get('parts_quantity', type=int) or None
        estimated_cut_time = request.form.get('estimated_cut_time', type=int) or None
        drawing_creation_time = request.form.get('drawing_creation_time', type=int) or None
        number_of_bins = request.form.get('number_of_bins', type=int) or None
        scheduled_cut_date_str = request.form.get('scheduled_cut_date', '').strip()

        # Validate required fields
        if not client_id:
            flash('Client is required.', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES)

        if not name:
            flash('Project name is required.', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES)

        # Get client
        client = Client.query.get(client_id)
        if not client:
            flash('Invalid client selected.', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES)

        # Generate project code
        project_code = generate_project_code(client.client_code)

        # Parse dates
        quote_date = None
        approval_date = None
        due_date = None
        scheduled_cut_date = None  # Phase 9

        try:
            if quote_date_str:
                quote_date = datetime.strptime(quote_date_str, '%Y-%m-%d').date()
            if approval_date_str:
                approval_date = datetime.strptime(approval_date_str, '%Y-%m-%d').date()
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            if scheduled_cut_date_str:  # Phase 9
                scheduled_cut_date = datetime.strptime(scheduled_cut_date_str, '%Y-%m-%d').date()
        except ValueError as e:
            flash(f'Invalid date format: {e}', 'error')
            clients = Client.query.order_by(Client.name).all()
            material_types = current_app.config.get('MATERIAL_TYPES', [])  # Phase 9
            return render_template('projects/form.html', project=None, clients=clients,
                                 statuses=Project.VALID_STATUSES, material_types=material_types)

        # Parse price
        quoted_price = None
        if quoted_price_str:
            try:
                quoted_price = float(quoted_price_str)
            except ValueError:
                flash('Invalid price format.', 'error')
                clients = Client.query.order_by(Client.name).all()
                return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES)

        # Create project
        project = Project(
            project_code=project_code,
            client_id=client_id,
            name=name,
            description=description or None,
            status=status,
            quote_date=quote_date,
            approval_date=approval_date,
            due_date=due_date,
            quoted_price=quoted_price,
            notes=notes or None,
            # Phase 9: New fields
            material_type=material_type,
            material_quantity_sheets=material_quantity_sheets,
            parts_quantity=parts_quantity,
            estimated_cut_time=estimated_cut_time,
            drawing_creation_time=drawing_creation_time,
            number_of_bins=number_of_bins,
            scheduled_cut_date=scheduled_cut_date
        )

        try:
            db.session.add(project)
            db.session.commit()

            # Log activity
            log_activity(
                'PROJECT',
                project.id,
                'CREATED',
                {'name': project.name, 'code': project.project_code, 'client': client.name}
            )

            flash(f'Project {project.project_code} created successfully.', 'success')
            return redirect(url_for('projects.detail', id=project.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES)

    # GET request - show form
    clients = Client.query.order_by(Client.name).all()
    material_types = current_app.config.get('MATERIAL_TYPES', [])  # Phase 9
    return render_template('projects/form.html', project=None, clients=clients,
                         statuses=Project.VALID_STATUSES, material_types=material_types)


@bp.route('/<int:id>')
def detail(id):
    """
    View project details.

    Args:
        id: Project ID

    Returns:
        Rendered template with project details
    """
    project = Project.query.get_or_404(id)

    # Get activity logs for this project
    logs = ActivityLog.query.filter_by(
        entity_type='PROJECT',
        entity_id=id
    ).order_by(ActivityLog.created_at.desc()).all()

    # Phase 9: Pass today's date for deadline calculations
    return render_template('projects/detail.html', project=project, logs=logs, today=date.today())



@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """
    Edit a project.

    Args:
        id: Project ID

    Returns:
        GET: Rendered edit form
        POST: Redirect to project detail page
    """
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', '').strip()
        quote_date_str = request.form.get('quote_date', '').strip()
        approval_date_str = request.form.get('approval_date', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        completion_date_str = request.form.get('completion_date', '').strip()
        quoted_price_str = request.form.get('quoted_price', '').strip()
        final_price_str = request.form.get('final_price', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate required fields
        if not name:
            flash('Project name is required.', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES)

        # Track changes for activity log
        changes = []

        if project.name != name:
            changes.append(f'name: "{project.name}" → "{name}"')
            project.name = name

        if project.description != description:
            project.description = description or None
            changes.append('description updated')

        if project.status != status:
            changes.append(f'status: {project.status} → {status}')
            project.status = status

        # Parse dates
        try:
            if quote_date_str:
                new_quote_date = datetime.strptime(quote_date_str, '%Y-%m-%d').date()
                if project.quote_date != new_quote_date:
                    changes.append(f'quote_date: {project.quote_date} → {new_quote_date}')
                    project.quote_date = new_quote_date
            elif project.quote_date:
                changes.append('quote_date cleared')
                project.quote_date = None

            if approval_date_str:
                new_approval_date = datetime.strptime(approval_date_str, '%Y-%m-%d').date()
                if project.approval_date != new_approval_date:
                    changes.append(f'approval_date: {project.approval_date} → {new_approval_date}')
                    project.approval_date = new_approval_date
            elif project.approval_date:
                changes.append('approval_date cleared')
                project.approval_date = None

            if due_date_str:
                new_due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                if project.due_date != new_due_date:
                    changes.append(f'due_date: {project.due_date} → {new_due_date}')
                    project.due_date = new_due_date
            elif project.due_date:
                changes.append('due_date cleared')
                project.due_date = None

            if completion_date_str:
                new_completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                if project.completion_date != new_completion_date:
                    changes.append(f'completion_date: {project.completion_date} → {new_completion_date}')
                    project.completion_date = new_completion_date
            elif project.completion_date:
                changes.append('completion_date cleared')
                project.completion_date = None

        except ValueError as e:
            flash(f'Invalid date format: {e}', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES)

        # Parse prices
        try:
            if quoted_price_str:
                new_quoted_price = float(quoted_price_str)
                if project.quoted_price != new_quoted_price:
                    changes.append(f'quoted_price: {project.quoted_price} → {new_quoted_price}')
                    project.quoted_price = new_quoted_price
            elif project.quoted_price:
                changes.append('quoted_price cleared')
                project.quoted_price = None

            if final_price_str:
                new_final_price = float(final_price_str)
                if project.final_price != new_final_price:
                    changes.append(f'final_price: {project.final_price} → {new_final_price}')
                    project.final_price = new_final_price
            elif project.final_price:
                changes.append('final_price cleared')
                project.final_price = None

        except ValueError:
            flash('Invalid price format.', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES)

        if project.notes != notes:
            project.notes = notes or None
            changes.append('notes updated')

        # Update timestamp
        project.updated_at = datetime.utcnow()

        try:
            db.session.commit()

            # Log activity
            if changes:
                log_activity(
                    'PROJECT',
                    project.id,
                    'UPDATED',
                    {'changes': ', '.join(changes)}
                )

            flash(f'Project {project.project_code} updated successfully.', 'success')
            return redirect(url_for('projects.detail', id=project.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
            clients = Client.query.order_by(Client.name).all()
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES)

    # GET request - show form
    clients = Client.query.order_by(Client.name).all()
    return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES)



@bp.route('/<int:id>/status', methods=['POST'])
def update_status(id):
    """
    Update project status (AJAX endpoint).

    Args:
        id: Project ID

    Returns:
        JSON response
    """
    project = Project.query.get_or_404(id)

    new_status = request.form.get('status', '').strip()

    if new_status not in Project.VALID_STATUSES:
        return {'success': False, 'error': 'Invalid status'}, 400

    old_status = project.status
    project.status = new_status
    project.updated_at = datetime.utcnow()

    # Auto-set dates based on status
    if new_status == Project.STATUS_APPROVED and not project.approval_date:
        project.approval_date = date.today()
    elif new_status == Project.STATUS_COMPLETED and not project.completion_date:
        project.completion_date = date.today()

    try:
        db.session.commit()

        # Log activity
        log_activity(
            'PROJECT',
            project.id,
            'STATUS_CHANGED',
            {'old_status': old_status, 'new_status': new_status}
        )

        return {'success': True, 'status': new_status}

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """
    Delete a project.

    Args:
        id: Project ID

    Returns:
        Redirect to project list
    """
    project = Project.query.get_or_404(id)
    project_code = project.project_code
    project_name = project.name

    try:
        # Log activity before deletion
        log_activity(
            'PROJECT',
            project.id,
            'DELETED',
            {'code': project_code, 'name': project_name}
        )

        db.session.delete(project)
        db.session.commit()

        flash(f'Project {project_code} deleted successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'error')

    return redirect(url_for('projects.index'))


# ============================================================================
# Phase 9: New Routes for POP, Notifications, Delivery, and Documents
# ============================================================================


@bp.route('/<int:id>/toggle-pop', methods=['POST'])
def toggle_pop(id):
    """
    Toggle POP received status and calculate deadline.

    Args:
        id: Project ID

    Returns:
        Redirect to project detail page
    """
    project = Project.query.get_or_404(id)

    # Toggle POP received
    project.pop_received = not project.pop_received

    if project.pop_received:
        # Set POP received date to today
        project.pop_received_date = date.today()
        # Calculate POP deadline (3 days from today)
        project.calculate_pop_deadline()
        flash(f'POP marked as received. Deadline: {project.pop_deadline}', 'success')
    else:
        # Clear POP dates
        project.pop_received_date = None
        project.pop_deadline = None
        flash('POP marked as not received.', 'info')

    project.updated_at = datetime.utcnow()

    try:
        db.session.commit()

        # Phase 9: Use enhanced activity logger
        from app.services.activity_logger import log_pop_status_change
        log_pop_status_change(
            project.id,
            project.pop_received,
            project.pop_received_date
        )
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating POP status: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/<int:id>/toggle-notified', methods=['POST'])
def toggle_notified(id):
    """
    Toggle client notified status.

    Args:
        id: Project ID

    Returns:
        Redirect to project detail page
    """
    project = Project.query.get_or_404(id)

    # Toggle client notified
    project.client_notified = not project.client_notified

    if project.client_notified:
        # Set notification date to today
        project.client_notified_date = date.today()
        flash('Client marked as notified.', 'success')
    else:
        # Clear notification date
        project.client_notified_date = None
        flash('Client notification cleared.', 'info')

    project.updated_at = datetime.utcnow()

    try:
        db.session.commit()

        # Phase 9: Use enhanced activity logger
        from app.services.activity_logger import log_notification_status_change
        log_notification_status_change(
            project.id,
            project.client_notified,
            project.client_notified_date
        )
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating notification status: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/<int:id>/toggle-delivery', methods=['POST'])
def toggle_delivery(id):
    """
    Toggle delivery confirmed status.

    Args:
        id: Project ID

    Returns:
        Redirect to project detail page
    """
    project = Project.query.get_or_404(id)

    # Toggle delivery confirmed
    project.delivery_confirmed = not project.delivery_confirmed

    if project.delivery_confirmed:
        # Set delivery date to today
        project.delivery_confirmed_date = date.today()
        flash('Delivery marked as confirmed.', 'success')
    else:
        # Clear delivery date
        project.delivery_confirmed_date = None
        flash('Delivery confirmation cleared.', 'info')

    project.updated_at = datetime.utcnow()

    try:
        db.session.commit()

        # Phase 9: Use enhanced activity logger
        from app.services.activity_logger import log_delivery_status_change
        log_delivery_status_change(
            project.id,
            project.delivery_confirmed,
            project.delivery_confirmed_date
        )
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating delivery status: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/<int:id>/upload-document', methods=['POST'])
def upload_document(id):
    """
    Upload a project document (Quote, Invoice, POP, Delivery Note).

    Args:
        id: Project ID

    Form Data:
        document_type: Type of document
        file: File to upload
        notes: Optional notes

    Returns:
        Redirect to project detail page
    """
    project = Project.query.get_or_404(id)

    document_type = request.form.get('document_type', '').strip()
    notes = request.form.get('notes', '').strip()

    # Validate document type
    if document_type not in ProjectDocument.VALID_TYPES:
        flash('Invalid document type.', 'error')
        return redirect(url_for('projects.detail', id=id))

    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('projects.detail', id=id))

    file = request.files['file']

    # Phase 9: Use document service for upload
    from app.services.document_service import save_document

    result = save_document(
        file=file,
        project_id=project.id,
        document_type=document_type,
        notes=notes or None,
        uploaded_by='admin'  # TODO: Get from session when auth is implemented
    )

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/document/<int:doc_id>/delete', methods=['POST'])
def delete_document(doc_id):
    """
    Delete a project document.

    Args:
        doc_id: Document ID

    Returns:
        Redirect to project detail page
    """
    document = ProjectDocument.query.get_or_404(doc_id)
    project_id = document.project_id

    # Phase 9: Use document service for deletion
    from app.services.document_service import delete_document as delete_doc_service

    result = delete_doc_service(
        document_id=doc_id,
        deleted_by='admin'  # TODO: Get from session when auth is implemented
    )

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('projects.detail', id=project_id))

