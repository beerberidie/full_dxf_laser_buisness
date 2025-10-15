"""
Laser OS Phase 9 - Communications Routes

This module handles all communication-related routes (Email, WhatsApp, Notifications).
Provides unified communication hub with auto-linking to clients and projects.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app import db
from app.models import Communication, CommunicationAttachment, Client, Project
from app.services.activity_logger import log_activity
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from pathlib import Path

bp = Blueprint('comms', __name__, url_prefix='/communications')


@bp.route('/')
def index():
    """
    List all communications with optional filtering.
    
    Query Parameters:
        comm_type: Filter by communication type (Email, WhatsApp, Notification)
        direction: Filter by direction (Inbound, Outbound)
        client_id: Filter by client ID
        project_id: Filter by project ID
        status: Filter by status
        is_linked: Filter by linking status (true/false)
        search: Search term for subject or body
        page: Page number for pagination
    
    Returns:
        Rendered template with communications list
    """
    # Get query parameters
    comm_type = request.args.get('comm_type', '').strip()
    direction = request.args.get('direction', '').strip()
    client_id = request.args.get('client_id', type=int)
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status', '').strip()
    is_linked = request.args.get('is_linked', '').strip()
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Build query
    query = Communication.query
    
    # Apply filters
    if comm_type:
        query = query.filter_by(comm_type=comm_type)
    
    if direction:
        query = query.filter_by(direction=direction)
    
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if is_linked:
        query = query.filter_by(is_linked=(is_linked.lower() == 'true'))
    
    if search:
        query = query.filter(
            db.or_(
                Communication.subject.ilike(f'%{search}%'),
                Communication.body.ilike(f'%{search}%'),
                Communication.from_address.ilike(f'%{search}%'),
                Communication.to_address.ilike(f'%{search}%')
            )
        )
    
    # Order by created date (newest first)
    query = query.order_by(Communication.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    communications = pagination.items
    
    # Get all clients and projects for filter dropdowns
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.created_at.desc()).limit(100).all()
    
    return render_template(
        'comms/list.html',
        communications=communications,
        clients=clients,
        projects=projects,
        pagination=pagination,
        comm_types=Communication.VALID_TYPES,
        directions=Communication.VALID_DIRECTIONS,
        statuses=Communication.VALID_STATUSES,
        selected_comm_type=comm_type,
        selected_direction=direction,
        selected_client_id=client_id,
        selected_project_id=project_id,
        selected_status=status,
        selected_is_linked=is_linked,
        search=search
    )


@bp.route('/<int:id>')
def detail(id):
    """
    View communication details.
    
    Args:
        id: Communication ID
    
    Returns:
        Rendered template with communication details
    """
    communication = Communication.query.get_or_404(id)
    
    # Get all clients and projects for linking dropdowns
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.created_at.desc()).limit(100).all()
    
    return render_template(
        'comms/detail.html',
        communication=communication,
        clients=clients,
        projects=projects
    )


@bp.route('/new', methods=['GET', 'POST'])
def new_communication():
    """
    Create a new communication (email or notification).
    
    GET: Display the new communication form
    POST: Process the form and create the communication
    
    Returns:
        GET: Rendered form template
        POST: Redirect to communication detail page
    """
    if request.method == 'POST':
        # Get form data
        comm_type = request.form.get('comm_type', Communication.TYPE_EMAIL).strip()
        direction = request.form.get('direction', Communication.DIRECTION_OUTBOUND).strip()
        client_id = request.form.get('client_id', type=int) or None
        project_id = request.form.get('project_id', type=int) or None
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        to_address = request.form.get('to_address', '').strip()
        
        # Validate required fields
        if not subject:
            flash('Subject is required.', 'error')
            clients = Client.query.order_by(Client.name).all()
            projects = Project.query.order_by(Project.created_at.desc()).limit(100).all()
            return render_template('comms/form.html', communication=None, clients=clients, projects=projects)
        
        if comm_type == Communication.TYPE_EMAIL and not to_address:
            flash('Recipient email address is required for emails.', 'error')
            clients = Client.query.order_by(Client.name).all()
            projects = Project.query.order_by(Project.created_at.desc()).limit(100).all()
            return render_template('comms/form.html', communication=None, clients=clients, projects=projects)
        
        # Auto-populate from_address for outbound emails
        from_address = None
        if comm_type == Communication.TYPE_EMAIL and direction == Communication.DIRECTION_OUTBOUND:
            from_address = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@laseros.local')
        
        # Create communication
        communication = Communication(
            comm_type=comm_type,
            direction=direction,
            client_id=client_id,
            project_id=project_id,
            subject=subject,
            body=body or None,
            from_address=from_address,
            to_address=to_address or None,
            status=Communication.STATUS_PENDING,
            is_linked=(client_id is not None or project_id is not None)
        )
        
        try:
            db.session.add(communication)
            db.session.commit()
            
            # Log activity
            log_activity(
                'COMMUNICATION',
                communication.id,
                'CREATED',
                {'type': comm_type, 'subject': subject, 'direction': direction}
            )
            
            flash(f'Communication created successfully.', 'success')
            return redirect(url_for('comms.detail', id=communication.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating communication: {str(e)}', 'error')
            clients = Client.query.order_by(Client.name).all()
            projects = Project.query.order_by(Project.created_at.desc()).limit(100).all()
            return render_template('comms/form.html', communication=None, clients=clients, projects=projects)
    
    # GET request - show form
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.created_at.desc()).limit(100).all()
    return render_template('comms/form.html', communication=None, clients=clients, projects=projects)


@bp.route('/<int:id>/link', methods=['POST'])
def link_communication(id):
    """
    Link a communication to a client and/or project.
    
    Args:
        id: Communication ID
    
    Form Data:
        client_id: Client ID to link to (optional)
        project_id: Project ID to link to (optional)
    
    Returns:
        Redirect to communication detail page
    """
    communication = Communication.query.get_or_404(id)
    
    client_id = request.form.get('client_id', type=int) or None
    project_id = request.form.get('project_id', type=int) or None
    
    # Update linking
    communication.client_id = client_id
    communication.project_id = project_id
    communication.is_linked = (client_id is not None or project_id is not None)
    communication.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()

        # Phase 9: Use enhanced activity logger
        from app.services.activity_logger import log_communication_link
        log_communication_link(
            communication.id,
            client_id=client_id,
            project_id=project_id
        )

        flash('Communication linked successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error linking communication: {str(e)}', 'error')

    return redirect(url_for('comms.detail', id=id))


@bp.route('/<int:id>/unlink', methods=['POST'])
def unlink_communication(id):
    """
    Unlink a communication from client and project.
    
    Args:
        id: Communication ID
    
    Returns:
        Redirect to communication detail page
    """
    communication = Communication.query.get_or_404(id)
    
    communication.client_id = None
    communication.project_id = None
    communication.is_linked = False
    communication.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()

        # Phase 9: Use enhanced activity logger
        from app.services.activity_logger import log_communication_unlink
        log_communication_unlink(communication.id)

        flash('Communication unlinked successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error unlinking communication: {str(e)}', 'error')

    return redirect(url_for('comms.detail', id=id))

