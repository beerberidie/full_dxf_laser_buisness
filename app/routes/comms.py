"""
Laser OS Phase 9 - Communications Routes

This module handles all communication-related routes (Email, WhatsApp, Notifications).
Provides unified communication hub with auto-linking to clients and projects.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from app import db
from app.models import Communication, CommunicationAttachment, Client, Project
from app.services.activity_logger import log_activity
from app.utils.decorators import role_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from pathlib import Path

bp = Blueprint('comms', __name__, url_prefix='/communications')


@bp.route('/')
@login_required
def index():
    """
    List all communications with optional filtering.

    Query Parameters:
        channel: Communication channel (whatsapp, gmail, outlook, teams)
        comm_type: Filter by communication type (Email, WhatsApp, Notification)
        direction: Filter by direction (Inbound, Outbound)
        client_id: Filter by client ID
        project_id: Filter by project ID
        status: Filter by status
        is_linked: Filter by linking status (true/false)
        search: Search term for subject or body
        page: Page number for pagination

    Returns:
        Rendered template with communications list or channel-specific page
    """
    # Get channel parameter
    channel = request.args.get('channel', '').strip().lower()

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

    # V12.0: Apply channel-specific filtering
    # Note: Communication model does not have a 'channel' field.
    # Gmail and Outlook tabs both show Email communications.
    # To distinguish between them in the future, add a 'channel' field to the database.
    if channel == 'whatsapp':
        query = query.filter_by(comm_type='WhatsApp')
    elif channel in ['gmail', 'outlook']:
        # Both Gmail and Outlook show all Email communications
        # since we don't have a channel field to distinguish them
        query = query.filter_by(comm_type='Email')
    elif channel == 'teams':
        # Teams channel - filter for Teams communications (future implementation)
        # For now, filter by a non-existent type to show empty state
        # When Teams integration is added, change this to filter_by(comm_type='Teams')
        query = query.filter_by(comm_type='Teams')  # Will return empty results

    # Apply additional filters
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

    # V12.0: Use unified list template with tabbed interface for all channels
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
@login_required
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
@role_required('admin', 'manager', 'operator')
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
@role_required('admin', 'manager', 'operator')
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
@role_required('admin', 'manager', 'operator')
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


# Production Automation: Outbound Drafts Routes

@bp.route('/drafts')
@login_required
def drafts():
    """List all outbound message drafts."""
    from app.services.comms_drafts import get_pending_drafts, get_sent_drafts, get_draft_statistics

    show_sent = request.args.get('show_sent', 'false') == 'true'

    if show_sent:
        drafts_list = get_sent_drafts()
    else:
        drafts_list = get_pending_drafts()

    stats = get_draft_statistics()

    return render_template('comms/drafts.html',
                         drafts=drafts_list,
                         show_sent=show_sent,
                         stats=stats)


@bp.route('/drafts/<int:draft_id>/send', methods=['POST'])
@login_required
def send_draft(draft_id):
    """Mark a draft as sent."""
    from app.services.comms_drafts import mark_draft_as_sent

    success = mark_draft_as_sent(draft_id)

    if success:
        flash('Draft marked as sent.', 'success')
    else:
        flash('Draft not found.', 'error')

    return redirect(url_for('comms.drafts'))


@bp.route('/drafts/<int:draft_id>/delete', methods=['POST'])
@login_required
def delete_draft(draft_id):
    """Delete a draft."""
    from app.services.comms_drafts import delete_draft

    success = delete_draft(draft_id)

    if success:
        flash('Draft deleted.', 'success')
    else:
        flash('Draft not found.', 'error')

    return redirect(url_for('comms.drafts'))


@bp.route('/drafts/<int:draft_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_draft(draft_id):
    """Edit a draft."""
    from app.services.comms_drafts import update_draft
    from app.models.business import OutboundDraft

    draft = OutboundDraft.query.get_or_404(draft_id)

    if request.method == 'POST':
        body_text = request.form.get('body_text')
        channel_hint = request.form.get('channel_hint')

        success = update_draft(draft_id, body_text=body_text, channel_hint=channel_hint)

        if success:
            flash('Draft updated.', 'success')
            return redirect(url_for('comms.drafts'))
        else:
            flash('Error updating draft.', 'error')

    return render_template('comms/edit_draft.html', draft=draft)
