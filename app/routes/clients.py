"""
Laser OS Tier 1 - Client Routes

This module defines routes for client management (CRUD operations).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Client
from app.services.id_generator import generate_client_code
from app.services.activity_logger import log_activity
from app.utils.decorators import role_required

bp = Blueprint('clients', __name__, url_prefix='/clients')


@bp.route('/')
@login_required
def list_clients():
    """
    List all clients with optional search and pagination.
    
    Query Parameters:
        search (str): Search term for name, code, or contact
        page (int): Page number for pagination
    
    Returns:
        Rendered template with client list
    """
    # Get search parameter
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Build query
    query = Client.query
    
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                Client.name.like(search_filter),
                Client.client_code.like(search_filter),
                Client.contact_person.like(search_filter),
                Client.email.like(search_filter)
            )
        )
    
    # Order by most recent first
    query = query.order_by(Client.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    clients = pagination.items
    
    return render_template(
        'clients/list.html',
        clients=clients,
        pagination=pagination,
        search=search
    )


@bp.route('/new', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def new_client():
    """
    Create a new client.
    
    GET: Display the new client form
    POST: Process the form and create the client
    
    Returns:
        GET: Rendered form template
        POST: Redirect to client detail page
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validate required fields
        if not name:
            flash('Client name is required.', 'error')
            return render_template('clients/form.html', client=None)
        
        # Generate client code
        client_code = generate_client_code()
        
        # Create client
        client = Client(
            client_code=client_code,
            name=name,
            contact_person=contact_person or None,
            email=email or None,
            phone=phone or None,
            address=address or None,
            notes=notes or None
        )
        
        try:
            db.session.add(client)
            db.session.commit()
            
            # Log activity
            log_activity(
                'CLIENT',
                client.id,
                'CREATED',
                {'name': client.name, 'code': client.client_code}
            )
            
            flash(f'Client {client.client_code} created successfully.', 'success')
            return redirect(url_for('clients.detail', id=client.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating client: {str(e)}', 'error')
            return render_template('clients/form.html', client=None)
    
    # GET request - show form
    return render_template('clients/form.html', client=None)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """
    Display client details.

    Args:
        id (int): Client ID

    Returns:
        Rendered template with client details
    """
    from app.models import Project

    client = Client.query.get_or_404(id)

    # Get all projects for this client, ordered by created date (newest first)
    projects = Project.query.filter_by(client_id=client.id).order_by(Project.created_at.desc()).all()

    # Get recent activities for this client
    from app.services.activity_logger import get_entity_activities
    activities = get_entity_activities('CLIENT', client.id, limit=20)

    return render_template(
        'clients/detail.html',
        client=client,
        projects=projects,
        activities=activities
    )


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def edit(id):
    """
    Edit an existing client.
    
    Args:
        id (int): Client ID
    
    Returns:
        GET: Rendered form template
        POST: Redirect to client detail page
    """
    client = Client.query.get_or_404(id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validate required fields
        if not name:
            flash('Client name is required.', 'error')
            return render_template('clients/form.html', client=client)
        
        # Track changes for activity log
        changes = {}
        if client.name != name:
            changes['name'] = {'old': client.name, 'new': name}
        if client.contact_person != contact_person:
            changes['contact_person'] = {'old': client.contact_person, 'new': contact_person}
        if client.email != email:
            changes['email'] = {'old': client.email, 'new': email}
        if client.phone != phone:
            changes['phone'] = {'old': client.phone, 'new': phone}
        
        # Update client
        client.name = name
        client.contact_person = contact_person or None
        client.email = email or None
        client.phone = phone or None
        client.address = address or None
        client.notes = notes or None
        
        try:
            db.session.commit()
            
            # Log activity if there were changes
            if changes:
                log_activity('CLIENT', client.id, 'UPDATED', changes)
            
            flash(f'Client {client.client_code} updated successfully.', 'success')
            return redirect(url_for('clients.detail', id=client.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating client: {str(e)}', 'error')
            return render_template('clients/form.html', client=client)
    
    # GET request - show form
    return render_template('clients/form.html', client=client)


@bp.route('/<int:id>/delete', methods=['POST'])
@role_required('admin', 'manager')
def delete(id):
    """
    Delete a client.
    
    Args:
        id (int): Client ID
    
    Returns:
        Redirect to client list page
    """
    client = Client.query.get_or_404(id)
    
    # Store info for logging
    client_code = client.client_code
    client_name = client.name
    
    try:
        # Log activity before deletion
        log_activity(
            'CLIENT',
            client.id,
            'DELETED',
            {'code': client_code, 'name': client_name}
        )
        
        db.session.delete(client)
        db.session.commit()
        
        flash(f'Client {client_code} deleted successfully.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting client: {str(e)}', 'error')
    
    return redirect(url_for('clients.list_clients'))

