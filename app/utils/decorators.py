"""
Authorization Decorators for Laser OS Tier 1

This module contains custom decorators for role-based access control:
- @login_required: Require user to be logged in (from Flask-Login)
- @role_required: Require user to have specific role(s)
- @permission_required: Require user to have specific permission(s)
- @admin_required: Require user to be admin
"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to require specific role(s) for a route.
    
    Usage:
        @bp.route('/admin/users')
        @role_required('admin')
        def manage_users():
            pass
        
        @bp.route('/clients/create')
        @role_required('admin', 'manager')
        def create_client():
            pass
    
    Args:
        *roles: Variable number of role names (strings)
    
    Returns:
        Decorated function that checks user roles before execution
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            # Superuser has access to everything
            if current_user.is_superuser:
                return f(*args, **kwargs)
            
            # Check if user has any of the required roles
            has_role = False
            for role in roles:
                if current_user.has_role(role):
                    has_role = True
                    break
            
            if not has_role:
                flash('You do not have permission to access this page.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def permission_required(*permissions):
    """
    Decorator to require specific permission(s) for a route.
    
    Usage:
        @bp.route('/reports/export')
        @permission_required('export_data')
        def export_report():
            pass
        
        @bp.route('/settings')
        @permission_required('manage_settings', 'view_logs')
        def settings():
            pass
    
    Args:
        *permissions: Variable number of permission codes (strings)
    
    Returns:
        Decorated function that checks user permissions before execution
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            # Superuser has all permissions
            if current_user.is_superuser:
                return f(*args, **kwargs)
            
            # Check if user has all required permissions
            for permission in permissions:
                if not current_user.has_permission(permission):
                    flash('You do not have permission to access this page.', 'error')
                    abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to require admin role for a route.
    
    This is a convenience decorator equivalent to @role_required('admin')
    
    Usage:
        @bp.route('/admin/settings')
        @admin_required
        def admin_settings():
            pass
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function that checks for admin role before execution
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin or superuser
        if not (current_user.is_superuser or current_user.has_role('admin')):
            flash('You must be an administrator to access this page.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def active_user_required(f):
    """
    Decorator to require user to be active (not locked or disabled).
    
    Usage:
        @bp.route('/profile')
        @active_user_required
        def profile():
            pass
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function that checks user is active before execution
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user account is active
        if not current_user.is_active:
            flash('Your account has been disabled. Please contact an administrator.', 'error')
            return redirect(url_for('auth.logout'))
        
        # Check if user account is locked
        if current_user.is_locked():
            flash('Your account is temporarily locked. Please try again later.', 'error')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    
    return decorated_function

