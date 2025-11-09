"""
Message Templates Routes for Laser OS.

Handles CRUD operations for message templates.
Supports template creation, editing, deletion, and preview.

Phase 2 Implementation - Message Templates.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import MessageTemplate, Client, Project
from app.utils.decorators import role_required
from app.services.activity_logger import log_activity
from app.services.template_renderer import render_template as render_msg_template, get_available_placeholders


bp = Blueprint('templates', __name__)


@bp.route('/')
@login_required
@role_required('admin', 'manager', 'operator')
def list_templates():
    """List all message templates."""
    # Get filter parameters
    template_type = request.args.get('type', '')
    is_active = request.args.get('active', '')
    search = request.args.get('search', '')
    
    # Build query
    query = MessageTemplate.query
    
    # Apply filters
    if template_type:
        query = query.filter_by(template_type=template_type)
    
    if is_active == 'true':
        query = query.filter_by(is_active=True)
    elif is_active == 'false':
        query = query.filter_by(is_active=False)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                MessageTemplate.name.ilike(search_pattern),
                MessageTemplate.description.ilike(search_pattern),
                MessageTemplate.subject_template.ilike(search_pattern)
            )
        )
    
    # Order by name
    templates = query.order_by(MessageTemplate.name).all()
    
    # Get template types for filter dropdown
    template_types = db.session.query(MessageTemplate.template_type).distinct().all()
    template_types = [t[0] for t in template_types]
    
    return render_template(
        'templates/list.html',
        templates=templates,
        template_types=template_types,
        current_type=template_type,
        current_active=is_active,
        current_search=search
    )


@bp.route('/<int:template_id>')
@login_required
@role_required('admin', 'manager', 'operator')
def view_template(template_id):
    """View template details."""
    template = MessageTemplate.query.get_or_404(template_id)
    
    # Get available placeholders
    placeholders = get_available_placeholders()
    
    return render_template(
        'templates/detail.html',
        template=template,
        placeholders=placeholders
    )


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
def new_template():
    """Create a new message template."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        template_type = request.form.get('template_type', '').strip()
        subject_template = request.form.get('subject_template', '').strip()
        body_template = request.form.get('body_template', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validate
        if not name:
            flash('Template name is required', 'error')
            return redirect(url_for('templates.new_template'))
        
        if not template_type:
            flash('Template type is required', 'error')
            return redirect(url_for('templates.new_template'))
        
        if not subject_template:
            flash('Subject template is required', 'error')
            return redirect(url_for('templates.new_template'))
        
        if not body_template:
            flash('Body template is required', 'error')
            return redirect(url_for('templates.new_template'))
        
        # Check for duplicate name
        existing = MessageTemplate.query.filter_by(name=name).first()
        if existing:
            flash(f'Template with name "{name}" already exists', 'error')
            return redirect(url_for('templates.new_template'))
        
        # Create template
        template = MessageTemplate(
            name=name,
            template_type=template_type,
            subject_template=subject_template,
            body_template=body_template,
            description=description or None,
            is_active=is_active,
            created_by_id=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        # Log activity
        log_activity('TEMPLATE', template.id, 'CREATED', {
            'name': name,
            'template_type': template_type
        })
        
        flash(f'Template "{name}" created successfully', 'success')
        return redirect(url_for('templates.view_template', template_id=template.id))
    
    # GET request - show form
    # Get available placeholders
    placeholders = get_available_placeholders()
    
    # Get template type constants
    template_types = [
        ('project_complete', 'Project Complete'),
        ('order_confirmed', 'Order Confirmed'),
        ('quote_sent', 'Quote Sent'),
        ('invoice_sent', 'Invoice Sent'),
        ('payment_reminder', 'Payment Reminder'),
        ('delivery_notification', 'Delivery Notification'),
        ('custom', 'Custom'),
    ]
    
    return render_template(
        'templates/form.html',
        template=None,
        placeholders=placeholders,
        template_types=template_types
    )


@bp.route('/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
def edit_template(template_id):
    """Edit an existing message template."""
    template = MessageTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        template_type = request.form.get('template_type', '').strip()
        subject_template = request.form.get('subject_template', '').strip()
        body_template = request.form.get('body_template', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validate
        if not name:
            flash('Template name is required', 'error')
            return redirect(url_for('templates.edit_template', template_id=template_id))
        
        if not template_type:
            flash('Template type is required', 'error')
            return redirect(url_for('templates.edit_template', template_id=template_id))
        
        if not subject_template:
            flash('Subject template is required', 'error')
            return redirect(url_for('templates.edit_template', template_id=template_id))
        
        if not body_template:
            flash('Body template is required', 'error')
            return redirect(url_for('templates.edit_template', template_id=template_id))
        
        # Check for duplicate name (excluding current template)
        existing = MessageTemplate.query.filter(
            MessageTemplate.name == name,
            MessageTemplate.id != template_id
        ).first()
        if existing:
            flash(f'Template with name "{name}" already exists', 'error')
            return redirect(url_for('templates.edit_template', template_id=template_id))
        
        # Update template
        template.name = name
        template.template_type = template_type
        template.subject_template = subject_template
        template.body_template = body_template
        template.description = description or None
        template.is_active = is_active
        
        db.session.commit()
        
        # Log activity
        log_activity('TEMPLATE', template.id, 'UPDATED', {
            'name': name,
            'template_type': template_type
        })
        
        flash(f'Template "{name}" updated successfully', 'success')
        return redirect(url_for('templates.view_template', template_id=template.id))
    
    # GET request - show form
    # Get available placeholders
    placeholders = get_available_placeholders()
    
    # Get template type constants
    template_types = [
        ('project_complete', 'Project Complete'),
        ('order_confirmed', 'Order Confirmed'),
        ('quote_sent', 'Quote Sent'),
        ('invoice_sent', 'Invoice Sent'),
        ('payment_reminder', 'Payment Reminder'),
        ('delivery_notification', 'Delivery Notification'),
        ('custom', 'Custom'),
    ]
    
    return render_template(
        'templates/form.html',
        template=template,
        placeholders=placeholders,
        template_types=template_types
    )


@bp.route('/<int:template_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'manager')
def delete_template(template_id):
    """Delete a message template."""
    template = MessageTemplate.query.get_or_404(template_id)

    template_name = template.name

    # Log activity before deletion
    log_activity('TEMPLATE', template.id, 'DELETED', {
        'name': template_name,
        'template_type': template.template_type
    })

    db.session.delete(template)
    db.session.commit()

    flash(f'Template "{template_name}" deleted successfully', 'success')
    return redirect(url_for('templates.list_templates'))


@bp.route('/<int:template_id>/preview', methods=['POST'])
@login_required
@role_required('admin', 'manager', 'operator')
def preview_template(template_id):
    """Preview a template with sample data."""
    template = MessageTemplate.query.get_or_404(template_id)

    # Get optional IDs from request
    client_id = request.form.get('client_id', type=int)
    project_id = request.form.get('project_id', type=int)

    # Render template
    try:
        rendered_subject = render_msg_template(
            template.subject_template,
            client_id=client_id,
            project_id=project_id
        )

        rendered_body = render_msg_template(
            template.body_template,
            client_id=client_id,
            project_id=project_id
        )

        return jsonify({
            'success': True,
            'subject': rendered_subject,
            'body': rendered_body
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/<int:template_id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin', 'manager')
def toggle_active(template_id):
    """Toggle template active status."""
    template = MessageTemplate.query.get_or_404(template_id)

    template.is_active = not template.is_active
    db.session.commit()

    status = 'activated' if template.is_active else 'deactivated'

    # Log activity
    log_activity('TEMPLATE', template.id, 'STATUS_CHANGED', {
        'name': template.name,
        'is_active': template.is_active
    })

    flash(f'Template "{template.name}" {status} successfully', 'success')
    return redirect(url_for('templates.view_template', template_id=template.id))


# API Endpoints for template integration
@bp.route('/api/active', methods=['GET'])
@login_required
def api_active_templates():
    """API endpoint to get active templates."""
    templates = MessageTemplate.query.filter_by(is_active=True).order_by(MessageTemplate.name).all()

    return jsonify([{
        'id': t.id,
        'name': t.name,
        'template_type': t.template_type,
        'subject_template': t.subject_template,
        'body_template': t.body_template
    } for t in templates])

