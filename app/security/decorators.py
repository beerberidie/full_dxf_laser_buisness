"""
Security Decorators for Laser OS Production Automation.

This module provides role-based access control (RBAC) decorators to protect routes
based on user roles.

Roles:
- operator: Access to Phone Mode only; cannot edit Presets or Inventory
- manager: Access to Dashboard, Projects, Queue, Reports, Communications; can view Inventory but cannot edit Presets
- admin: Full access to all modules, can edit Presets and Inventory

Usage:
    from app.security.decorators import require_role, require_any_role
    
    @app.route('/admin/settings')
    @login_required
    @require_role('admin')
    def admin_settings():
        return render_template('admin/settings.html')
    
    @app.route('/inventory/edit/<int:id>')
    @login_required
    @require_any_role('admin', 'manager')
    def edit_inventory(id):
        return render_template('inventory/edit.html')
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def require_role(*allowed_roles):
    """
    Decorator to require specific user role(s) for route access.
    
    Args:
        *allowed_roles: Variable number of role names (strings) that are allowed
        
    Returns:
        Decorated function that checks user role before execution
        
    Raises:
        403: If user doesn't have required role
        401: If user is not authenticated
        
    Example:
        @require_role('admin')
        def admin_only_view():
            pass
            
        @require_role('admin', 'manager')
        def admin_or_manager_view():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Check if user has required role
            if current_user.role not in allowed_roles:
                flash(f'Access denied. This page requires one of the following roles: {", ".join(allowed_roles)}', 'danger')
                abort(403)
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(*allowed_roles):
    """
    Alias for require_role for better readability when multiple roles are allowed.
    
    Args:
        *allowed_roles: Variable number of role names (strings) that are allowed
        
    Returns:
        Decorated function that checks user role before execution
        
    Example:
        @require_any_role('admin', 'manager')
        def view_reports():
            pass
    """
    return require_role(*allowed_roles)


def is_operator():
    """
    Check if current user has operator role.
    
    Returns:
        bool: True if user is authenticated and has operator role
    """
    return current_user.is_authenticated and current_user.role == 'operator'


def is_manager():
    """
    Check if current user has manager role.
    
    Returns:
        bool: True if user is authenticated and has manager role
    """
    return current_user.is_authenticated and current_user.role == 'manager'


def is_admin():
    """
    Check if current user has admin role.
    
    Returns:
        bool: True if user is authenticated and has admin role
    """
    return current_user.is_authenticated and current_user.role == 'admin'


def can_edit_presets():
    """
    Check if current user can edit machine presets.
    
    Only admins can edit presets.
    
    Returns:
        bool: True if user can edit presets
    """
    return current_user.is_authenticated and current_user.role == 'admin'


def can_edit_inventory():
    """
    Check if current user can edit inventory.
    
    Admins and managers can edit inventory.
    
    Returns:
        bool: True if user can edit inventory
    """
    return current_user.is_authenticated and current_user.role in ['admin', 'manager']


def can_access_phone_mode():
    """
    Check if current user can access phone mode.
    
    All authenticated users can access phone mode, but it's primarily for operators.
    
    Returns:
        bool: True if user can access phone mode
    """
    return current_user.is_authenticated


def can_access_pc_mode():
    """
    Check if current user can access PC mode dashboard.
    
    Managers and admins can access PC mode.
    
    Returns:
        bool: True if user can access PC mode
    """
    return current_user.is_authenticated and current_user.role in ['admin', 'manager']


def can_generate_reports():
    """
    Check if current user can generate reports.
    
    Managers and admins can generate reports.
    
    Returns:
        bool: True if user can generate reports
    """
    return current_user.is_authenticated and current_user.role in ['admin', 'manager']

