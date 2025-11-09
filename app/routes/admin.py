"""
Admin Routes for Laser OS Tier 1

This module handles all admin-related routes:
- User management (list, create, edit, delete)
- Role assignment
- Login history viewing
- Account management (lock/unlock, activate/deactivate)
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.auth import User, Role, UserRole, LoginHistory
from app.forms.auth import UserForm, ResetPasswordForm
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/users')
@admin_required
def users():
    """
    List all users in the system.
    
    Shows user information including:
    - Username, email, full name
    - Roles
    - Account status (active/inactive, locked)
    - Last login
    """
    # Get all users ordered by username
    users = User.query.order_by(User.username).all()
    
    return render_template('admin/users/list.html', users=users)


@bp.route('/users/new', methods=['GET', 'POST'])
@admin_required
def new_user():
    """
    Create a new user account.
    
    Allows admin to:
    - Set username, email, full name
    - Set initial password
    - Assign roles
    - Set account status
    """
    form = UserForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            is_active=form.is_active.data,
            is_superuser=form.is_superuser.data
        )
        
        # Set password
        user.set_password(form.password.data)
        
        # Add to database
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Assign roles
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    assigned_by=current_user.id
                )
                db.session.add(user_role)
        
        # Commit changes
        db.session.commit()
        
        flash(f'User "{user.username}" created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/users/form.html', form=form, user=None)


@bp.route('/users/<int:id>')
@admin_required
def user_detail(id):
    """
    View detailed information about a user.
    
    Shows:
    - User information
    - Assigned roles
    - Login history
    - Account status
    """
    user = User.query.get_or_404(id)
    
    # Get login history (last 20 entries)
    login_history = LoginHistory.query.filter_by(user_id=id).order_by(
        LoginHistory.login_time.desc()
    ).limit(20).all()
    
    return render_template('admin/users/detail.html', user=user, login_history=login_history)


@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    """
    Edit an existing user account.
    
    Allows admin to:
    - Update username, email, full name
    - Change roles
    - Update account status
    - Note: Password is changed separately via reset_password
    """
    user = User.query.get_or_404(id)
    
    # Prevent editing own account (use profile instead)
    if user.id == current_user.id:
        flash('Please use your profile page to edit your own account.', 'warning')
        return redirect(url_for('auth.profile'))
    
    form = UserForm(user=user, obj=user)
    
    if form.validate_on_submit():
        # Update user information
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.is_active = form.is_active.data
        user.is_superuser = form.is_superuser.data
        
        # Update password if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        # Update roles
        # Remove existing roles
        UserRole.query.filter_by(user_id=user.id).delete()
        
        # Add new roles
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    assigned_by=current_user.id
                )
                db.session.add(user_role)
        
        # Commit changes
        db.session.commit()
        
        flash(f'User "{user.username}" updated successfully!', 'success')
        return redirect(url_for('admin.user_detail', id=user.id))
    
    # Pre-populate roles
    if request.method == 'GET':
        form.roles.data = [role.id for role in user.roles]
    
    return render_template('admin/users/form.html', form=form, user=user)


@bp.route('/users/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    """
    Delete a user account.
    
    Prevents:
    - Deleting own account
    - Deleting the last admin user
    """
    user = User.query.get_or_404(id)
    
    # Prevent deleting own account
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    # Prevent deleting last admin
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role and user.has_role('admin'):
        admin_count = User.query.join(UserRole).filter(
            UserRole.role_id == admin_role.id
        ).count()
        
        if admin_count <= 1:
            flash('Cannot delete the last administrator account.', 'error')
            return redirect(url_for('admin.users'))
    
    # Delete user
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:id>/reset-password', methods=['GET', 'POST'])
@admin_required
def reset_password(id):
    """
    Reset a user's password (admin function).
    
    Allows admin to set a new password for any user.
    """
    user = User.query.get_or_404(id)
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Set new password
        user.set_password(form.new_password.data)
        
        # Unlock account if locked
        if user.is_locked():
            user.unlock_account()
        
        db.session.commit()
        
        flash(f'Password reset successfully for user "{user.username}".', 'success')
        return redirect(url_for('admin.user_detail', id=user.id))
    
    return render_template('admin/users/reset_password.html', form=form, user=user)


@bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@admin_required
def toggle_active(id):
    """
    Toggle user account active status.
    
    Activates inactive accounts or deactivates active accounts.
    """
    user = User.query.get_or_404(id)
    
    # Prevent deactivating own account
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    # Toggle status
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User "{user.username}" {status} successfully.', 'success')
    
    return redirect(url_for('admin.user_detail', id=user.id))


@bp.route('/users/<int:id>/unlock', methods=['POST'])
@admin_required
def unlock_user(id):
    """
    Unlock a locked user account.
    
    Resets failed login attempts and removes account lock.
    """
    user = User.query.get_or_404(id)
    
    if not user.is_locked():
        flash(f'User "{user.username}" is not locked.', 'info')
        return redirect(url_for('admin.user_detail', id=user.id))
    
    # Unlock account
    user.unlock_account()
    db.session.commit()
    
    flash(f'User "{user.username}" unlocked successfully.', 'success')
    return redirect(url_for('admin.user_detail', id=user.id))


@bp.route('/login-history')
@admin_required
def login_history():
    """
    View system-wide login history.
    
    Shows all login attempts (successful and failed) across all users.
    """
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Query login history
    pagination = LoginHistory.query.order_by(
        LoginHistory.login_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/login_history.html', pagination=pagination)

