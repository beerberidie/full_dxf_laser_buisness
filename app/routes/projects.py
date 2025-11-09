"""
Laser OS Tier 1 - Projects Routes

This module handles all project/job-related routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_file
from flask_login import login_required
from app import db
from app.models import Project, Client, ActivityLog, ProjectDocument, QueueItem
from app.services.id_generator import generate_project_code
from app.services.activity_logger import log_activity
from app.utils.decorators import role_required
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import zipfile
from io import BytesIO

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('/')
@login_required
def index():
    """
    List all projects with optional filtering.

    Query Parameters:
        search: Search term for project name or code
        client_id: Filter by client ID
        status: Filter by project status
        on_hold: Filter for on-hold projects (V12.0)
        expiring_soon: Filter for quotes expiring soon (V12.0)
        page: Page number for pagination

    Returns:
        Rendered template with project list
    """
    # Get query parameters
    search = request.args.get('search', '').strip()
    client_id = request.args.get('client_id', type=int)
    status = request.args.get('status', '').strip()
    on_hold_filter = request.args.get('on_hold', type=int) == 1  # V12.0
    expiring_soon_filter = request.args.get('expiring_soon', type=int) == 1  # V12.0
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

    # V12.0: On-hold filter
    if on_hold_filter:
        query = query.filter_by(on_hold=True)

    # V12.0: Expiring soon filter (quotes expiring in ≤10 days)
    if expiring_soon_filter:
        from datetime import date, timedelta
        expiry_threshold = date.today() + timedelta(days=10)
        query = query.filter(
            Project.status == Project.STATUS_QUOTE_APPROVAL,
            Project.quote_expiry_date.isnot(None),
            Project.quote_expiry_date <= expiry_threshold,
            Project.pop_received == False
        )

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
        on_hold_filter=on_hold_filter,  # V12.0
        expiring_soon_filter=expiring_soon_filter,  # V12.0
        statuses=Project.VALID_STATUSES
    )



@bp.route('/new', methods=['GET', 'POST'])
@role_required('admin', 'manager')
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
        material_thickness = request.form.get('material_thickness', type=float) or None  # Phase 10
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
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

        if not name:
            flash('Project name is required.', 'error')
            clients = Client.query.order_by(Client.name).all()
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

        # Get client
        client = Client.query.get(client_id)
        if not client:
            flash('Invalid client selected.', 'error')
            clients = Client.query.order_by(Client.name).all()
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

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
                material_types = current_app.config.get('MATERIAL_TYPES', [])
                return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

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
            material_thickness=material_thickness,  # Phase 10
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

            # V12.0: Check if project can be auto-advanced to Quote & Approval
            if current_app.config.get('AUTO_ADVANCE_TO_QUOTE', True) and project.status == Project.STATUS_REQUEST:
                from app.services.status_automation import auto_advance_to_quote_approval
                from flask_login import current_user

                performed_by = current_user.username if current_user.is_authenticated else 'System (Auto)'
                result = auto_advance_to_quote_approval(project, performed_by=performed_by)

                if result['advanced']:
                    flash(f'✓ {result["message"]}', 'success')
                elif result['reasons']:
                    # Show what's missing (informational, not an error)
                    missing = ', '.join(result['reasons'])
                    flash(f'ℹ️ To auto-advance to Quote & Approval, complete: {missing}', 'info')

            return redirect(url_for('projects.detail', id=project.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
            clients = Client.query.order_by(Client.name).all()
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=None, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

    # GET request - show form
    clients = Client.query.order_by(Client.name).all()
    material_types = current_app.config.get('MATERIAL_TYPES', [])  # Phase 9
    return render_template('projects/form.html', project=None, clients=clients,
                         statuses=Project.VALID_STATUSES, material_types=material_types)


@bp.route('/<int:id>')
@login_required
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
@role_required('admin', 'manager')
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
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

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
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

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
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

        if project.notes != notes:
            project.notes = notes or None
            changes.append('notes updated')

        # Phase 9 & 10: Material and production details
        material_type = request.form.get('material_type', '').strip() or None
        material_thickness = request.form.get('material_thickness', type=float) or None  # Phase 10
        material_quantity_sheets = request.form.get('material_quantity_sheets', type=int) or None
        parts_quantity = request.form.get('parts_quantity', type=int) or None
        estimated_cut_time = request.form.get('estimated_cut_time', type=int) or None
        drawing_creation_time = request.form.get('drawing_creation_time', type=int) or None
        number_of_bins = request.form.get('number_of_bins', type=int) or None
        scheduled_cut_date_str = request.form.get('scheduled_cut_date', '').strip()

        if project.material_type != material_type:
            changes.append(f'material_type: {project.material_type} → {material_type}')
            project.material_type = material_type

        if project.material_thickness != material_thickness:
            changes.append(f'material_thickness: {project.material_thickness} → {material_thickness}')
            project.material_thickness = material_thickness

        if project.material_quantity_sheets != material_quantity_sheets:
            changes.append(f'material_quantity_sheets: {project.material_quantity_sheets} → {material_quantity_sheets}')
            project.material_quantity_sheets = material_quantity_sheets

        if project.parts_quantity != parts_quantity:
            changes.append(f'parts_quantity: {project.parts_quantity} → {parts_quantity}')
            project.parts_quantity = parts_quantity

        if project.estimated_cut_time != estimated_cut_time:
            changes.append(f'estimated_cut_time: {project.estimated_cut_time} → {estimated_cut_time}')
            project.estimated_cut_time = estimated_cut_time

        if project.drawing_creation_time != drawing_creation_time:
            changes.append(f'drawing_creation_time: {project.drawing_creation_time} → {drawing_creation_time}')
            project.drawing_creation_time = drawing_creation_time

        if project.number_of_bins != number_of_bins:
            changes.append(f'number_of_bins: {project.number_of_bins} → {number_of_bins}')
            project.number_of_bins = number_of_bins

        # Parse scheduled cut date
        try:
            if scheduled_cut_date_str:
                new_scheduled_cut_date = datetime.strptime(scheduled_cut_date_str, '%Y-%m-%d').date()
                if project.scheduled_cut_date != new_scheduled_cut_date:
                    changes.append(f'scheduled_cut_date: {project.scheduled_cut_date} → {new_scheduled_cut_date}')
                    project.scheduled_cut_date = new_scheduled_cut_date
            elif project.scheduled_cut_date:
                changes.append('scheduled_cut_date cleared')
                project.scheduled_cut_date = None
        except ValueError as e:
            flash(f'Invalid scheduled cut date format: {e}', 'error')
            clients = Client.query.order_by(Client.name).all()
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

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

            # V12.0: Check if project can be auto-advanced to Quote & Approval after edit
            if current_app.config.get('AUTO_ADVANCE_TO_QUOTE', True) and project.status == Project.STATUS_REQUEST:
                from app.services.status_automation import auto_advance_to_quote_approval
                from flask_login import current_user

                performed_by = current_user.username if current_user.is_authenticated else 'System (Auto)'
                result = auto_advance_to_quote_approval(project, performed_by=performed_by)

                if result['advanced']:
                    flash(f'✓ {result["message"]}', 'success')

            return redirect(url_for('projects.detail', id=project.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
            clients = Client.query.order_by(Client.name).all()
            material_types = current_app.config.get('MATERIAL_TYPES', [])
            return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)

    # GET request - show form
    clients = Client.query.order_by(Client.name).all()
    material_types = current_app.config.get('MATERIAL_TYPES', [])
    return render_template('projects/form.html', project=project, clients=clients, statuses=Project.VALID_STATUSES, material_types=material_types)



@bp.route('/<int:id>/status', methods=['POST'])
@role_required('admin', 'manager', 'operator')
def update_status(id):
    """
    Update project status (AJAX endpoint).

    V12.0: Enhanced with status transition validation and auto-advance logic.

    Args:
        id: Project ID

    Returns:
        JSON response
    """
    from flask_login import current_user
    from app.services.status_automation import validate_status_transition, auto_advance_to_quote_approval

    project = Project.query.get_or_404(id)

    new_status = request.form.get('status', '').strip()

    if new_status not in Project.VALID_STATUSES:
        return {'success': False, 'error': 'Invalid status'}, 400

    old_status = project.status

    # V12.0: Validate status transition
    validation = validate_status_transition(project, new_status)

    if not validation['valid']:
        return {
            'success': False,
            'error': validation['message'],
            'missing_fields': validation['missing_fields'],
            'warnings': validation['warnings']
        }, 400

    # Update status
    project.status = new_status
    project.updated_at = datetime.utcnow()

    # V12.0: Auto-set dates and calculate expiry based on status
    if new_status == Project.STATUS_QUOTE_APPROVAL:
        if not project.quote_date:
            project.quote_date = date.today()
        project.calculate_quote_expiry_date(days=current_app.config.get('QUOTE_EXPIRY_DAYS', 30))

    elif new_status == Project.STATUS_APPROVED_POP:
        if not project.approval_date:
            project.approval_date = date.today()

    elif new_status == Project.STATUS_COMPLETED:
        if not project.completion_date:
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
@role_required('admin', 'manager')
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


def auto_add_to_queue(project):
    """
    Automatically add a project to the production queue.

    This function is called when POP is marked as received.
    It creates a QueueItem with sensible defaults.

    Args:
        project: Project instance to add to queue

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if project is already in active queue
        existing = QueueItem.query.filter_by(
            project_id=project.id,
            status=QueueItem.STATUS_QUEUED
        ).first()

        if existing:
            return False, f'Project {project.project_code} is already in the queue'

        # Also check for in-progress items
        in_progress = QueueItem.query.filter_by(
            project_id=project.id,
            status=QueueItem.STATUS_IN_PROGRESS
        ).first()

        if in_progress:
            return False, f'Project {project.project_code} is already in progress'

        # Get next queue position
        max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
        next_position = max_position + 1

        # Determine scheduled date (today or next business day)
        scheduled_date = date.today()

        # If it's late in the day or weekend, schedule for next business day
        # For now, we'll just use today - can be enhanced later

        # Create queue item with sensible defaults
        queue_item = QueueItem(
            project_id=project.id,
            queue_position=next_position,
            status=QueueItem.STATUS_QUEUED,
            priority=QueueItem.PRIORITY_NORMAL,
            scheduled_date=scheduled_date,
            estimated_cut_time=project.estimated_cut_time if project.estimated_cut_time else None,
            notes='Automatically added to queue when POP was received',
            added_by='System (Auto)'
        )

        db.session.add(queue_item)
        db.session.flush()  # Get the queue_item.id

        # Log activity
        log_activity(
            entity_type='QUEUE',
            entity_id=queue_item.id,
            action='ADDED',
            details=f'Automatically added project {project.project_code} to queue at position {next_position} (POP received)',
            user='System (Auto)'
        )

        return True, f'Project automatically added to queue at position {next_position}'

    except Exception as e:
        return False, f'Error auto-adding to queue: {str(e)}'


@bp.route('/<int:id>/toggle-pop', methods=['POST'])
@role_required('admin', 'manager')
def toggle_pop(id):
    """
    Toggle POP received status and calculate deadline.

    Phase 10: When POP is marked as received, automatically schedules the project
    if inventory is available and all material information is complete.

    V12.0: Enhanced with status update to "Approved (POP Received)" and notifications.

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

        # V12.0: Update status to "Approved (POP Received)" if currently in "Quote & Approval"
        if project.status == Project.STATUS_QUOTE_APPROVAL:
            project.status = Project.STATUS_APPROVED_POP
            project.approval_date = date.today()
            flash(f'✓ POP marked as received. Status updated to "Approved (POP Received)". Deadline: {project.pop_deadline}', 'success')
        else:
            flash(f'✓ POP marked as received. Deadline: {project.pop_deadline}', 'success')
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

        # V12.0: Send notification when POP is received
        if project.pop_received:
            from app.services.notification_service import send_pop_received_notice
            try:
                send_pop_received_notice(project)
            except Exception as e:
                current_app.logger.error(f'Failed to send POP received notification: {e}')

        # Phase 10: Automatically schedule when POP is received (with inventory check)
        if project.pop_received and current_app.config.get('AUTO_QUEUE_ON_POP', True):
            from app.services.auto_scheduler import auto_schedule_project
            from app.services.inventory_service import get_material_ordering_suggestions
            from flask_login import current_user

            performed_by = current_user.username if current_user.is_authenticated else 'System (Auto)'
            result = auto_schedule_project(project, performed_by=performed_by)

            if result['scheduled']:
                flash(f'✅ {result["message"]} - Inventory reserved', 'success')
            else:
                # Show reasons why not scheduled
                if 'Already in queue' in result['reasons']:
                    flash(f'ℹ️ {result["message"]}', 'info')
                else:
                    reasons_text = '; '.join(result['reasons'])
                    flash(f'⚠️ Not auto-scheduled: {reasons_text}', 'warning')

                    # Check if insufficient inventory and show ordering suggestion
                    if any('Insufficient' in reason for reason in result['reasons']):
                        ordering = get_material_ordering_suggestions(project)
                        if ordering['needs_ordering']:
                            flash(f'💡 Suggestion: {ordering["message"]}', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating POP status: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/<int:id>/toggle-notified', methods=['POST'])
@role_required('admin', 'manager', 'operator')
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


@bp.route('/<int:id>/toggle-hold', methods=['POST'])
@role_required('admin', 'manager')
def toggle_hold(id):
    """
    Toggle project on-hold status.

    V12.0: New endpoint for on-hold management.

    Args:
        id: Project ID

    Returns:
        Redirect to project detail page
    """
    from flask_login import current_user

    project = Project.query.get_or_404(id)

    if project.on_hold:
        # Resume from hold
        try:
            performed_by = current_user.username if current_user.is_authenticated else 'admin'
            project.resume_from_hold(performed_by=performed_by)
            db.session.commit()
            flash(f'✓ Project resumed from on-hold status.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error resuming project: {str(e)}', 'error')
    else:
        # Put on hold - get reason from form
        reason = request.form.get('reason', '').strip()

        if not reason:
            flash('Please provide a reason for putting the project on hold.', 'warning')
            return redirect(url_for('projects.detail', id=id))

        try:
            performed_by = current_user.username if current_user.is_authenticated else 'admin'
            project.set_on_hold(reason=reason, performed_by=performed_by)
            db.session.commit()
            flash(f'✓ Project put on hold: {reason}', 'info')
        except Exception as e:
            db.session.rollback()
            flash(f'Error putting project on hold: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/<int:id>/reinstate', methods=['POST'])
@role_required('admin', 'manager')
def reinstate(id):
    """
    Reinstate a cancelled project back to Quote & Approval with new 30-day period.

    V12.0: New endpoint for reinstating cancelled projects.

    Args:
        id: Project ID

    Returns:
        Redirect to project detail page
    """
    from flask_login import current_user

    project = Project.query.get_or_404(id)

    # Check if project can be reinstated
    if project.status != Project.STATUS_CANCELLED:
        flash('Only cancelled projects can be reinstated.', 'warning')
        return redirect(url_for('projects.detail', id=id))

    if not project.can_reinstate:
        flash('This project cannot be reinstated. It may have been manually cancelled without reinstate permission.', 'warning')
        return redirect(url_for('projects.detail', id=id))

    try:
        performed_by = current_user.username if current_user.is_authenticated else 'admin'
        success = project.reinstate(performed_by=performed_by)

        if success:
            db.session.commit()
            flash(
                f'✓ Project reinstated! Status: Quote & Approval. '
                f'New quote expires: {project.quote_expiry_date}',
                'success'
            )
        else:
            flash('Failed to reinstate project. Please check project status.', 'error')

    except Exception as e:
        db.session.rollback()
        flash(f'Error reinstating project: {str(e)}', 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/<int:id>/toggle-delivery', methods=['POST'])
@role_required('admin', 'manager', 'operator')
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
@role_required('admin', 'manager', 'operator')
def upload_document(id):
    """
    Upload one or more project documents (Quote, Invoice, POP, Delivery Note).

    Args:
        id: Project ID

    Form Data:
        document_type: Type of document
        files: File(s) to upload (supports multiple)
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

    # Check if files were uploaded (support both 'files' and 'file' for backward compatibility)
    files = request.files.getlist('files')
    if not files or (len(files) == 1 and files[0].filename == ''):
        # Fallback to single file upload for backward compatibility
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                files = [file]
            else:
                flash('No file uploaded.', 'error')
                return redirect(url_for('projects.detail', id=id))
        else:
            flash('No file uploaded.', 'error')
            return redirect(url_for('projects.detail', id=id))

    # Phase 9: Use document service for upload
    from app.services.document_service import save_documents

    result = save_documents(
        files=files,
        project_id=project.id,
        document_type=document_type,
        notes=notes or None,
        uploaded_by='admin'  # TODO: Get from session when auth is implemented
    )

    # Display flash messages
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')

    # Show individual error messages for failed uploads
    if result['failed_count'] > 0:
        for error_msg in result['errors'][:5]:  # Limit to first 5 errors
            flash(error_msg, 'error')

        if len(result['errors']) > 5:
            flash(f"... and {len(result['errors']) - 5} more errors", 'error')

    return redirect(url_for('projects.detail', id=id))


@bp.route('/document/<int:doc_id>/delete', methods=['POST'])
@role_required('admin', 'manager')
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


@bp.route('/download-all-documents/<int:project_id>')
@login_required
@role_required('admin', 'manager', 'operator', 'viewer')
def download_all_documents(project_id):
    """Download all project documents as a ZIP archive."""
    # Get project
    project = Project.query.get_or_404(project_id)

    # Get all documents for this project
    documents = ProjectDocument.query.filter_by(project_id=project_id).order_by(
        ProjectDocument.upload_date.desc()
    ).all()

    # Handle edge case: no documents
    if not documents:
        flash('No documents to download for this project', 'warning')
        return redirect(url_for('projects.detail', id=project_id))

    # Handle edge case: single document - redirect to single document download
    if len(documents) == 1:
        # Since there's no individual download route yet, we'll create the ZIP anyway
        # TODO: Add individual document download route and redirect here
        pass

    try:
        # Create ZIP file in memory
        memory_file = BytesIO()

        # Track statistics for logging
        files_added = 0
        files_missing = 0
        total_size = 0

        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for document in documents:
                # ProjectDocument.file_path contains the full absolute path
                # (unlike DesignFile which stores relative paths)
                full_file_path = os.path.abspath(document.file_path)

                # Check if file exists
                if not os.path.exists(full_file_path):
                    current_app.logger.warning(f"Document file not found: {full_file_path}")
                    files_missing += 1
                    continue

                # Add file to ZIP with original filename
                # Prefix with document type to organize files
                arcname = f"{document.document_type}/{document.original_filename}"
                zf.write(full_file_path, arcname=arcname)
                files_added += 1
                total_size += document.file_size

                current_app.logger.info(f"Added to ZIP: {arcname}")

        # Check if any files were added
        if files_added == 0:
            flash('No documents could be added to the archive. Files may be missing from disk.', 'error')
            return redirect(url_for('projects.detail', id=project_id))

        # Seek to beginning of BytesIO buffer
        memory_file.seek(0)

        # Generate ZIP filename using project code
        zip_filename = f"{project.project_code}-Documents.zip"

        # Log activity
        activity = ActivityLog(
            entity_type='PROJECT',
            entity_id=project_id,
            action='DOWNLOAD_ALL_DOCUMENTS',
            details=f'Downloaded {files_added} project documents as ZIP archive ({round(total_size / (1024 * 1024), 2)} MB total)',
            user='System'  # TODO: Use current_user when available
        )
        db.session.add(activity)
        db.session.commit()

        # Show warning if some files were missing
        if files_missing > 0:
            flash(f'Warning: {files_missing} document(s) were missing and not included in the archive', 'warning')

        # Send ZIP file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )

    except Exception as e:
        current_app.logger.error(f"Error creating ZIP archive for project {project_id} documents: {str(e)}")
        flash(f'Error creating ZIP archive: {str(e)}', 'error')
        return redirect(url_for('projects.detail', id=project_id))

