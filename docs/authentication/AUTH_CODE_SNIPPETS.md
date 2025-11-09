# Authentication & Authorization Code Snippets
## Quick Reference for Common Tasks

**Related Documents:**
- `AUTHENTICATION_AUTHORIZATION_DESIGN.md` - Complete design document
- `AUTH_IMPLEMENTATION_CHECKLIST.md` - Implementation checklist

---

## Table of Contents

1. [Route Protection](#route-protection)
2. [Template Permission Checks](#template-permission-checks)
3. [User Management](#user-management)
4. [Password Operations](#password-operations)
5. [Session Management](#session-management)
6. [Login History](#login-history)
7. [Common Patterns](#common-patterns)

---

## Route Protection

### Require Login Only

```python
from flask_login import login_required

@bp.route('/dashboard')
@login_required
def dashboard():
    """Any authenticated user can access."""
    return render_template('dashboard.html')
```

### Require Specific Role

```python
from app.utils.decorators import role_required

@bp.route('/clients/create', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def create_client():
    """Only admin and manager can access."""
    # ... your code ...
```

### Require Admin Only

```python
from app.utils.decorators import admin_required

@bp.route('/admin/users')
@admin_required
def manage_users():
    """Only admin can access."""
    # ... your code ...
```

### Require Specific Permission

```python
from app.utils.decorators import permission_required

@bp.route('/reports/export')
@permission_required('export_data')
def export_report():
    """Only users with export_data permission can access."""
    # ... your code ...
```

### Multiple Decorators

```python
from flask_login import login_required
from app.utils.decorators import role_required

@bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager', 'operator')
def edit_project(id):
    """Authenticated users with specific roles can access."""
    # ... your code ...
```

---

## Template Permission Checks

### Check if User is Authenticated

```html
{% if current_user.is_authenticated %}
    <p>Welcome, {{ current_user.full_name }}!</p>
{% else %}
    <a href="{{ url_for('auth.login') }}">Login</a>
{% endif %}
```

### Check User Role

```html
{% if current_user.has_role('admin') %}
    <a href="{{ url_for('admin.users') }}" class="btn btn-primary">Manage Users</a>
{% endif %}
```

### Check Multiple Roles

```html
{% if current_user.has_role('admin') or current_user.has_role('manager') %}
    <a href="{{ url_for('clients.create') }}" class="btn btn-primary">Create Client</a>
{% endif %}
```

### Check Permission

```html
{% if current_user.has_permission('delete_all') %}
    <button class="btn btn-danger" onclick="deleteItem()">Delete</button>
{% endif %}
```

### Show Different Content by Role

```html
{% if current_user.has_role('admin') %}
    <div class="admin-panel">
        <!-- Admin-only content -->
    </div>
{% elif current_user.has_role('manager') %}
    <div class="manager-panel">
        <!-- Manager content -->
    </div>
{% elif current_user.has_role('operator') %}
    <div class="operator-panel">
        <!-- Operator content -->
    </div>
{% else %}
    <div class="viewer-panel">
        <!-- Viewer content -->
    </div>
{% endif %}
```

### Display User Info

```html
<div class="user-info">
    <span class="username">{{ current_user.username }}</span>
    <span class="role">{{ current_user.get_primary_role()|title }}</span>
    <a href="{{ url_for('auth.logout') }}">Logout</a>
</div>
```

---

## User Management

### Create New User (Python Shell or Script)

```python
from app import db
from app.models.auth import User, Role

# Create user
user = User(
    username='john_doe',
    email='john@example.com',
    full_name='John Doe',
    is_active=True
)
user.set_password('SecurePassword123')

# Assign role
operator_role = Role.query.filter_by(name='operator').first()
user.roles.append(operator_role)

# Save to database
db.session.add(user)
db.session.commit()

print(f"User {user.username} created successfully")
```

### Create User in Route

```python
from flask import request, flash, redirect, url_for
from app import db
from app.models.auth import User, Role
from app.forms.auth import RegistrationForm

@bp.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            is_active=True
        )
        user.set_password(form.password.data)
        
        # Assign default role
        viewer_role = Role.query.filter_by(name='viewer').first()
        if viewer_role:
            user.roles.append(viewer_role)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} created successfully', 'success')
        return redirect(url_for('admin.users_list'))
    
    return render_template('admin/user_form.html', form=form)
```

### Update User

```python
@bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users_list'))
    
    return render_template('admin/user_form.html', user=user)
```

### Delete User

```python
@bp.route('/admin/users/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    # Prevent deleting superuser
    if user.is_superuser:
        flash('Cannot delete superuser account', 'error')
        return redirect(url_for('admin.users_list'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully', 'success')
    return redirect(url_for('admin.users_list'))
```

### Assign Role to User

```python
@bp.route('/admin/users/<int:user_id>/assign-role/<int:role_id>', methods=['POST'])
@admin_required
def assign_role(user_id, role_id):
    user = User.query.get_or_404(user_id)
    role = Role.query.get_or_404(role_id)
    
    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
        flash(f'Role {role.display_name} assigned to {user.username}', 'success')
    else:
        flash(f'User already has role {role.display_name}', 'info')
    
    return redirect(url_for('admin.user_detail', id=user_id))
```

### Remove Role from User

```python
@bp.route('/admin/users/<int:user_id>/remove-role/<int:role_id>', methods=['POST'])
@admin_required
def remove_role(user_id, role_id):
    user = User.query.get_or_404(user_id)
    role = Role.query.get_or_404(role_id)
    
    if role in user.roles:
        user.roles.remove(role)
        db.session.commit()
        flash(f'Role {role.display_name} removed from {user.username}', 'success')
    else:
        flash(f'User does not have role {role.display_name}', 'info')
    
    return redirect(url_for('admin.user_detail', id=user_id))
```

---

## Password Operations

### Change Password (User Self-Service)

```python
from flask_login import current_user
from app.forms.auth import ChangePasswordForm

@bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
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
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/change_password.html', form=form)
```

### Reset Password (Admin)

```python
@bp.route('/admin/users/<int:id>/reset-password', methods=['POST'])
@admin_required
def reset_password(id):
    user = User.query.get_or_404(id)
    
    # Generate temporary password
    import secrets
    temp_password = secrets.token_urlsafe(12)
    
    user.set_password(temp_password)
    db.session.commit()
    
    # In production, send email with temp password
    flash(f'Password reset. Temporary password: {temp_password}', 'success')
    
    return redirect(url_for('admin.user_detail', id=id))
```

### Validate Password Strength

```python
import re

def validate_password_strength(password):
    """Validate password meets security requirements."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain special character")
    
    return len(errors) == 0, errors

# Usage in form validation
from wtforms.validators import ValidationError

def validate_password(form, field):
    valid, errors = validate_password_strength(field.data)
    if not valid:
        raise ValidationError(' '.join(errors))
```

---

## Session Management

### Get Current User Info

```python
from flask_login import current_user

@bp.route('/profile')
@login_required
def profile():
    user_info = {
        'username': current_user.username,
        'email': current_user.email,
        'full_name': current_user.full_name,
        'roles': [role.display_name for role in current_user.roles],
        'last_login': current_user.last_login
    }
    return render_template('profile.html', user=user_info)
```

### Check Session Status

```python
from flask import session
from flask_login import current_user

@bp.route('/session-info')
@login_required
def session_info():
    info = {
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id,
        'session_id': session.get('_id'),
        'permanent': session.permanent
    }
    return jsonify(info)
```

### Extend Session

```python
from flask import session
from datetime import timedelta

@bp.route('/extend-session', methods=['POST'])
@login_required
def extend_session():
    session.permanent = True
    session.modified = True
    flash('Session extended', 'success')
    return redirect(url_for('main.dashboard'))
```

---

## Login History

### View User Login History

```python
from app.models.auth import LoginHistory

@bp.route('/admin/users/<int:id>/login-history')
@admin_required
def user_login_history(id):
    user = User.query.get_or_404(id)
    
    history = LoginHistory.query.filter_by(user_id=id)\
        .order_by(LoginHistory.login_time.desc())\
        .limit(50)\
        .all()
    
    return render_template('admin/login_history.html', user=user, history=history)
```

### View All Failed Login Attempts

```python
@bp.route('/admin/security/failed-logins')
@admin_required
def failed_logins():
    failed = LoginHistory.query.filter_by(success=False)\
        .order_by(LoginHistory.login_time.desc())\
        .limit(100)\
        .all()
    
    return render_template('admin/failed_logins.html', attempts=failed)
```

### Get Login Statistics

```python
from sqlalchemy import func
from datetime import datetime, timedelta

@bp.route('/admin/security/stats')
@admin_required
def login_stats():
    # Last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    stats = {
        'total_logins': LoginHistory.query.filter(
            LoginHistory.login_time >= thirty_days_ago,
            LoginHistory.success == True
        ).count(),
        
        'failed_attempts': LoginHistory.query.filter(
            LoginHistory.login_time >= thirty_days_ago,
            LoginHistory.success == False
        ).count(),
        
        'unique_users': db.session.query(func.count(func.distinct(LoginHistory.user_id)))\
            .filter(LoginHistory.login_time >= thirty_days_ago).scalar(),
        
        'active_sessions': LoginHistory.query.filter(
            LoginHistory.logout_time == None,
            LoginHistory.success == True
        ).count()
    }
    
    return render_template('admin/login_stats.html', stats=stats)
```

---

## Common Patterns

### Redirect After Login

```python
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # ... authentication logic ...
    
    if user_authenticated:
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
```

### Require Login with Custom Message

```python
from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps

def login_required_with_message(message):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(message, 'warning')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@bp.route('/sensitive-data')
@login_required_with_message('You must be logged in to view sensitive data')
def sensitive_data():
    # ... your code ...
```

### Check Permission in View

```python
from flask import abort

@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    # Check permission manually
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to delete projects', 'error')
        abort(403)
    
    # ... delete logic ...
```

### Activity Logging with User

```python
from app.services.activity_logger import log_activity
from flask_login import current_user

@bp.route('/clients/<int:id>/edit', methods=['POST'])
@role_required('admin', 'manager')
def edit_client(id):
    client = Client.query.get_or_404(id)
    
    # ... update client ...
    
    # Log with current user
    log_activity(
        entity_type='CLIENT',
        entity_id=client.id,
        action='UPDATED',
        details=f'Client {client.name} updated by {current_user.username}',
        user=current_user.username
    )
    
    db.session.commit()
    flash('Client updated successfully', 'success')
    return redirect(url_for('clients.detail', id=id))
```

### Conditional Template Include

```html
<!-- base.html -->
{% if current_user.is_authenticated %}
    {% include 'partials/user_menu.html' %}
{% else %}
    {% include 'partials/guest_menu.html' %}
{% endif %}
```

### Role-Based Navigation

```html
<!-- Navigation menu -->
<nav>
    <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
    
    {% if current_user.is_authenticated %}
        <a href="{{ url_for('clients.list_clients') }}">Clients</a>
        <a href="{{ url_for('projects.index') }}">Projects</a>
        
        {% if current_user.has_role('admin') or current_user.has_role('manager') %}
            <a href="{{ url_for('quotes.index') }}">Quotes</a>
            <a href="{{ url_for('invoices.index') }}">Invoices</a>
        {% endif %}
        
        {% if current_user.has_role('admin') %}
            <a href="{{ url_for('admin.users') }}">User Management</a>
        {% endif %}
    {% endif %}
</nav>
```

---

## Quick Commands

### Flask Shell Commands

```bash
# Start Flask shell
flask shell

# Create user
from app.models.auth import User, Role
user = User(username='test', email='test@example.com')
user.set_password('password')
db.session.add(user)
db.session.commit()

# Assign role
role = Role.query.filter_by(name='operator').first()
user.roles.append(role)
db.session.commit()

# Check user roles
user = User.query.filter_by(username='test').first()
print([r.name for r in user.roles])

# Unlock account
user.unlock_account()

# Deactivate user
user.is_active = False
db.session.commit()
```

---

**End of Code Snippets**

For complete implementation details, refer to `AUTHENTICATION_AUTHORIZATION_DESIGN.md`.

