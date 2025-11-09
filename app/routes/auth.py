"""
Authentication Routes for Laser OS Tier 1

This module handles all authentication-related routes:
- Login
- Logout
- Change password
- Profile
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.models.auth import User, LoginHistory
from app.models.business import Operator
from app.forms.auth import LoginForm, ChangePasswordForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page.
    
    Handles user authentication with:
    - Username/password verification
    - Account lockout after failed attempts
    - Login history tracking
    - Session management
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Query user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists
        if not user:
            # Log failed login attempt (no user)
            log_failed_login(form.username.data, 'Invalid username')
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if account is locked
        if user.is_locked():
            log_failed_login(form.username.data, 'Account locked', user.id)
            flash('Account is locked due to too many failed login attempts. Please try again later.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if account is active
        if not user.is_active:
            log_failed_login(form.username.data, 'Account disabled', user.id)
            flash('Your account has been disabled. Please contact an administrator.', 'error')
            return redirect(url_for('auth.login'))
        
        # Verify password
        if not user.check_password(form.password.data):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.lock_account(duration_minutes=30)
                db.session.commit()
                log_failed_login(form.username.data, 'Too many failed attempts - account locked', user.id)
                flash('Too many failed login attempts. Your account has been locked for 30 minutes.', 'error')
            else:
                db.session.commit()
                log_failed_login(form.username.data, 'Invalid password', user.id)
                remaining = 5 - user.failed_login_attempts
                flash(f'Invalid username or password. {remaining} attempts remaining.', 'error')
            
            return redirect(url_for('auth.login'))
        
        # Successful login
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Log user in
        login_user(user, remember=form.remember_me.data)

        # CRITICAL FIX: Auto-bind operator identity to session
        # Check if user has an associated operator profile
        if hasattr(user, 'operator_profile') and user.operator_profile:
            session['operator_id'] = user.operator_profile.id
            session['operator_name'] = user.operator_profile.name
        else:
            # Clear operator session data if no profile exists
            session.pop('operator_id', None)
            session.pop('operator_name', None)

        # Log successful login
        log_successful_login(user)

        # Flash success message
        flash(f'Welcome back, {user.full_name or user.username}!', 'success')

        # Production Automation: Redirect to mode selection instead of dashboard
        # Check if there's a specific next page requested
        next_page = request.args.get('next')
        if next_page and urlparse(next_page).netloc == '':
            # If there's a valid next page, go there
            return redirect(next_page)
        else:
            # Otherwise, go to mode selection
            return redirect(url_for('auth.select_mode'))
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """
    User logout.
    
    Logs out the current user and updates login history.
    """
    # Update logout time in login history
    if current_user.is_authenticated:
        # Find the most recent login session
        last_login = LoginHistory.query.filter_by(
            user_id=current_user.id,
            success=True,
            logout_time=None
        ).order_by(LoginHistory.login_time.desc()).first()

        if last_login:
            last_login.logout_time = datetime.utcnow()
            db.session.commit()

    # Clear operator session data
    session.pop('operator_id', None)
    session.pop('operator_name', None)

    # Production Automation: Clear UI mode
    session.pop('ui_mode', None)

    # Log out user
    logout_user()

    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/profile')
@login_required
def profile():
    """
    User profile page.
    
    Displays user information and recent login history.
    """
    # Get recent login history
    recent_logins = LoginHistory.query.filter_by(
        user_id=current_user.id,
        success=True
    ).order_by(LoginHistory.login_time.desc()).limit(10).all()
    
    return render_template('auth/profile.html', recent_logins=recent_logins)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password page.
    
    Allows users to change their own password.
    """
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html', form=form)
        
        # Set new password
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form)


# Helper functions

def log_successful_login(user):
    """
    Log a successful login attempt.
    
    Args:
        user (User): User who logged in
    """
    login_record = LoginHistory(
        user_id=user.id,
        login_time=datetime.utcnow(),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        success=True,
        session_id=session.get('_id')
    )
    db.session.add(login_record)
    db.session.commit()


def log_failed_login(username, reason, user_id=None):
    """
    Log a failed login attempt.
    
    Args:
        username (str): Username that was attempted
        reason (str): Reason for failure
        user_id (int): User ID if user exists, None otherwise
    """
    login_record = LoginHistory(
        user_id=user_id,
        login_time=datetime.utcnow(),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        success=False,
        failure_reason=f'{username}: {reason}'
    )
    db.session.add(login_record)
    db.session.commit()


# ============================================================================
# Production Automation: Mode Selection
# ============================================================================

@bp.route('/select-mode', methods=['GET', 'POST'])
@login_required
def select_mode():
    """
    Mode selection page - choose between PC Mode and Phone Mode.

    PC Mode: Full dashboard with sidebar navigation (for managers and admins)
    Phone Mode: Mobile operator UI for production logging (for operators)

    After login, users are directed here to choose their interface mode.
    """
    if request.method == 'POST':
        chosen_mode = request.form.get('mode')

        if chosen_mode == 'pc':
            session['ui_mode'] = 'pc'
            flash('Switched to PC Mode - Full Dashboard', 'success')
            return redirect(url_for('main.dashboard'))
        elif chosen_mode == 'phone':
            session['ui_mode'] = 'phone'
            flash('Switched to Phone Mode - Production Logging', 'success')
            return redirect(url_for('phone.home'))
        else:
            flash('Invalid mode selection', 'error')
            return redirect(url_for('auth.select_mode'))

    # GET request - show mode selection page
    # Determine recommended mode based on user role
    recommended_mode = 'phone' if current_user.role == 'operator' else 'pc'

    return render_template('auth/select_mode.html', recommended_mode=recommended_mode)

