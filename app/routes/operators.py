"""
Laser OS - Operators Routes

This module defines routes for managing machine operators.
Phase 10 Implementation.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Operator, User, LaserRun
from app.utils.decorators import role_required
from datetime import datetime

bp = Blueprint('operators', __name__, url_prefix='/operators')


@bp.route('/')
@login_required
def list():
    """
    List all operators.
    
    Query Parameters:
        search (str): Search term for operator name
        active (str): Filter by active status ('1' for active, '0' for inactive)
    
    Returns:
        Rendered template with operator list
    """
    # Get filter parameters
    search = request.args.get('search', '').strip()
    active_filter = request.args.get('active', '').strip()
    
    # Build query
    query = Operator.query
    
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                Operator.name.like(search_filter),
                Operator.email.like(search_filter)
            )
        )
    
    if active_filter:
        is_active = active_filter == '1'
        query = query.filter(Operator.is_active == is_active)
    
    # Order by name
    query = query.order_by(Operator.name)
    
    operators = query.all()
    
    return render_template('operators/list.html',
                         operators=operators,
                         search=search,
                         active_filter=active_filter)


@bp.route('/new', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def new():
    """Create a new operator."""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            user_id = request.form.get('user_id', '').strip() or None
            is_active = request.form.get('is_active') == 'on'
            
            # Validate required fields
            if not name:
                flash('Operator name is required.', 'error')
                users = User.query.filter_by(is_active=True).order_by(User.username).all()
                return render_template('operators/form.html', operator=None, users=users, action='new')
            
            # Check if operator name already exists
            existing = Operator.query.filter_by(name=name).first()
            if existing:
                flash(f'Operator with name "{name}" already exists.', 'error')
                users = User.query.filter_by(is_active=True).order_by(User.username).all()
                return render_template('operators/form.html', operator=None, users=users, action='new')
            
            # Create operator
            operator = Operator(
                name=name,
                email=email,
                phone=phone,
                user_id=int(user_id) if user_id else None,
                is_active=is_active
            )
            
            db.session.add(operator)
            db.session.commit()
            
            flash(f'Operator "{name}" created successfully!', 'success')
            return redirect(url_for('operators.detail', id=operator.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating operator: {str(e)}', 'error')
            users = User.query.filter_by(is_active=True).order_by(User.username).all()
            return render_template('operators/form.html', operator=None, users=users, action='new')
    
    # GET request - show form
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    return render_template('operators/form.html', operator=None, users=users, action='new')


@bp.route('/<int:id>')
@login_required
def detail(id):
    """View operator details."""
    operator = Operator.query.get_or_404(id)
    
    # Get recent laser runs by this operator
    recent_runs = operator.laser_runs.order_by(LaserRun.run_date.desc()).limit(10).all()
    
    return render_template('operators/detail.html',
                         operator=operator,
                         recent_runs=recent_runs)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def edit(id):
    """Edit an operator."""
    operator = Operator.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip() or None
            phone = request.form.get('phone', '').strip() or None
            user_id = request.form.get('user_id', '').strip() or None
            is_active = request.form.get('is_active') == 'on'
            
            # Validate required fields
            if not name:
                flash('Operator name is required.', 'error')
                users = User.query.filter_by(is_active=True).order_by(User.username).all()
                return render_template('operators/form.html', operator=operator, users=users, action='edit')
            
            # Check if operator name already exists (excluding current operator)
            existing = Operator.query.filter(
                Operator.name == name,
                Operator.id != id
            ).first()
            if existing:
                flash(f'Operator with name "{name}" already exists.', 'error')
                users = User.query.filter_by(is_active=True).order_by(User.username).all()
                return render_template('operators/form.html', operator=operator, users=users, action='edit')
            
            # Update operator
            operator.name = name
            operator.email = email
            operator.phone = phone
            operator.user_id = int(user_id) if user_id else None
            operator.is_active = is_active
            operator.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Operator "{name}" updated successfully!', 'success')
            return redirect(url_for('operators.detail', id=operator.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating operator: {str(e)}', 'error')
            users = User.query.filter_by(is_active=True).order_by(User.username).all()
            return render_template('operators/form.html', operator=operator, users=users, action='edit')
    
    # GET request - show form
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    return render_template('operators/form.html', operator=operator, users=users, action='edit')


@bp.route('/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete(id):
    """Delete an operator."""
    operator = Operator.query.get_or_404(id)
    
    try:
        # Check if operator has laser runs
        run_count = operator.laser_run_count
        if run_count > 0:
            flash(f'Cannot delete operator "{operator.name}" - has {run_count} laser run(s). Consider deactivating instead.', 'error')
            return redirect(url_for('operators.detail', id=id))
        
        name = operator.name
        db.session.delete(operator)
        db.session.commit()
        
        flash(f'Operator "{name}" deleted successfully.', 'success')
        return redirect(url_for('operators.list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting operator: {str(e)}', 'error')
        return redirect(url_for('operators.detail', id=id))


@bp.route('/<int:id>/toggle-active', methods=['POST'])
@role_required('admin', 'manager')
def toggle_active(id):
    """Toggle operator active status."""
    operator = Operator.query.get_or_404(id)
    
    try:
        operator.is_active = not operator.is_active
        operator.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = "activated" if operator.is_active else "deactivated"
        flash(f'Operator "{operator.name}" {status} successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating operator status: {str(e)}', 'error')
    
    return redirect(url_for('operators.detail', id=id))

