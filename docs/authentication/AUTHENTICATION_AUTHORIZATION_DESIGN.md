# Multi-User Authentication & Authorization System Design
## Laser OS Tier 1 - Network Access & Role-Based Permissions

**Document Version:** 1.0  
**Date:** 2025-10-17  
**Status:** Design & Implementation Plan

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [User Roles & Permissions Matrix](#user-roles--permissions-matrix)
4. [Database Schema](#database-schema)
5. [Authentication Flow](#authentication-flow)
6. [Technical Implementation](#technical-implementation)
7. [Network Access Configuration](#network-access-configuration)
8. [Security Best Practices](#security-best-practices)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Guide](#deployment-guide)
12. [Appendices](#appendices)

---

## Executive Summary

### Overview
This document outlines the design and implementation plan for adding multi-user authentication and role-based authorization to the Laser OS Tier 1 application. The system will support secure local and remote network access with granular permission controls.

### Key Features
- ✅ **Secure Authentication** - Password hashing with bcrypt, session management
- ✅ **Role-Based Access Control (RBAC)** - 4 user roles with granular permissions
- ✅ **Network Access** - Local LAN and secure remote access support
- ✅ **Session Security** - Secure cookies, CSRF protection, session timeout
- ✅ **Audit Trail** - Login tracking and activity logging
- ✅ **User Management** - Admin interface for user CRUD operations

### Technology Stack
- **Flask-Login** - Session management and user authentication
- **Werkzeug Security** - Password hashing (bcrypt)
- **Flask-WTF** - Form handling and CSRF protection
- **SQLAlchemy** - User and role data models
- **Flask-Principal** (Optional) - Advanced permission management

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Web Browser  │  │ Web Browser  │  │ Web Browser  │          │
│  │ (Local LAN)  │  │ (Remote VPN) │  │ (Remote VPN) │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │ HTTPS            │ HTTPS            │ HTTPS
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────┐
│         │         NETWORK LAYER                │                 │
│  ┌──────▼──────┐    ┌─────▼──────┐    ┌──────▼──────┐          │
│  │ Local LAN   │    │ VPN Tunnel │    │ VPN Tunnel  │          │
│  │ 192.168.x.x │    │ (Encrypted)│    │ (Encrypted) │          │
│  └──────┬──────┘    └─────┬──────┘    └──────┬──────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                   APPLICATION LAYER                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Flask Application (Waitress)                   │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Authentication Middleware (Flask-Login)             │  │  │
│  │  │  - Login Manager                                     │  │  │
│  │  │  - Session Management                                │  │  │
│  │  │  - User Loader                                       │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Authorization Middleware (Custom Decorators)        │  │  │
│  │  │  - Role Checking                                     │  │  │
│  │  │  - Permission Validation                             │  │  │
│  │  │  - Route Protection                                  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Business Logic Layer                                │  │  │
│  │  │  - Clients, Projects, Products, Queue, etc.          │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                      DATA LAYER                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM                                            │  │
│  └────────────────────────────┬───────────────────────────────┘  │
│  ┌────────────────────────────▼───────────────────────────────┐  │
│  │  SQLite Database (laser_os.db)                             │  │
│  │  - users                                                   │  │
│  │  - roles                                                   │  │
│  │  - user_roles (association table)                         │  │
│  │  - login_history                                           │  │
│  │  - ... (existing tables)                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Flask-Login** | User session management, login/logout, remember me |
| **Werkzeug Security** | Password hashing and verification (bcrypt) |
| **Custom Decorators** | Role-based route protection (@role_required) |
| **User Model** | User data, authentication methods, role relationships |
| **Role Model** | Role definitions and permission mappings |
| **Login History** | Audit trail for security and compliance |

---

## User Roles & Permissions Matrix

### Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                         ADMIN/BOSS                               │
│  Full system access - All CRUD operations - User management     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                          MANAGER                                 │
│  Business operations - Create/Edit/Delete - No user management  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                          OPERATOR                                │
│  Production operations - Limited editing - No deletion          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                           VIEWER                                 │
│  Read-only access - View data - No modifications                │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Permissions Matrix

| Feature/Action | Admin | Manager | Operator | Viewer |
|----------------|-------|---------|----------|--------|
| **Dashboard** |
| View Dashboard | ✅ | ✅ | ✅ | ✅ |
| View Statistics | ✅ | ✅ | ✅ | ✅ |
| **Clients** |
| View Clients | ✅ | ✅ | ✅ | ✅ |
| Create Client | ✅ | ✅ | ❌ | ❌ |
| Edit Client | ✅ | ✅ | ❌ | ❌ |
| Delete Client | ✅ | ✅ | ❌ | ❌ |
| **Projects** |
| View Projects | ✅ | ✅ | ✅ | ✅ |
| Create Project | ✅ | ✅ | ❌ | ❌ |
| Edit Project | ✅ | ✅ | ✅ | ❌ |
| Delete Project | ✅ | ✅ | ❌ | ❌ |
| Toggle POP Status | ✅ | ✅ | ✅ | ❌ |
| Upload Documents | ✅ | ✅ | ✅ | ❌ |
| **Products** |
| View Products | ✅ | ✅ | ✅ | ✅ |
| Create Product | ✅ | ✅ | ❌ | ❌ |
| Edit Product | ✅ | ✅ | ❌ | ❌ |
| Delete Product | ✅ | ✅ | ❌ | ❌ |
| Upload DXF Files | ✅ | ✅ | ✅ | ❌ |
| **Queue** |
| View Queue | ✅ | ✅ | ✅ | ✅ |
| Add to Queue | ✅ | ✅ | ✅ | ❌ |
| Reorder Queue | ✅ | ✅ | ✅ | ❌ |
| Start/Complete Job | ✅ | ✅ | ✅ | ❌ |
| Remove from Queue | ✅ | ✅ | ❌ | ❌ |
| **Inventory** |
| View Inventory | ✅ | ✅ | ✅ | ✅ |
| Add Stock | ✅ | ✅ | ✅ | ❌ |
| Edit Stock | ✅ | ✅ | ✅ | ❌ |
| Delete Stock | ✅ | ✅ | ❌ | ❌ |
| **Quotes & Invoices** |
| View Quotes/Invoices | ✅ | ✅ | ✅ | ✅ |
| Create Quote/Invoice | ✅ | ✅ | ❌ | ❌ |
| Edit Quote/Invoice | ✅ | ✅ | ❌ | ❌ |
| Delete Quote/Invoice | ✅ | ✅ | ❌ | ❌ |
| Generate PDF | ✅ | ✅ | ✅ | ❌ |
| **Communications** |
| View Communications | ✅ | ✅ | ✅ | ✅ |
| Send Communication | ✅ | ✅ | ✅ | ❌ |
| Delete Communication | ✅ | ✅ | ❌ | ❌ |
| **Reports** |
| View Reports | ✅ | ✅ | ✅ | ✅ |
| Generate Reports | ✅ | ✅ | ✅ | ❌ |
| Export Data | ✅ | ✅ | ❌ | ❌ |
| **Presets** |
| View Presets | ✅ | ✅ | ✅ | ✅ |
| Create Preset | ✅ | ✅ | ❌ | ❌ |
| Edit Preset | ✅ | ✅ | ❌ | ❌ |
| Delete Preset | ✅ | ✅ | ❌ | ❌ |
| **User Management** |
| View Users | ✅ | ❌ | ❌ | ❌ |
| Create User | ✅ | ❌ | ❌ | ❌ |
| Edit User | ✅ | ❌ | ❌ | ❌ |
| Delete User | ✅ | ❌ | ❌ | ❌ |
| Assign Roles | ✅ | ❌ | ❌ | ❌ |
| View Login History | ✅ | ❌ | ❌ | ❌ |
| **System Settings** |
| View Settings | ✅ | ❌ | ❌ | ❌ |
| Edit Settings | ✅ | ❌ | ❌ | ❌ |
| View Activity Logs | ✅ | ✅ | ❌ | ❌ |

### Permission Codes

For programmatic permission checking:

```python
PERMISSIONS = {
    'admin': [
        'view_all', 'create_all', 'edit_all', 'delete_all',
        'manage_users', 'manage_settings', 'view_logs'
    ],
    'manager': [
        'view_all', 'create_business', 'edit_business', 'delete_business',
        'view_logs'
    ],
    'operator': [
        'view_all', 'edit_production', 'manage_queue', 'upload_files'
    ],
    'viewer': [
        'view_all'
    ]
}
```

---

## Database Schema

### New Tables

#### 1. Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until DATETIME,
    CONSTRAINT check_username_length CHECK (length(username) >= 3),
    CONSTRAINT check_email_format CHECK (email LIKE '%_@_%._%')
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
```

#### 2. Roles Table

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions TEXT,  -- JSON string of permissions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_role_name CHECK (name IN ('admin', 'manager', 'operator', 'viewer'))
);

CREATE INDEX idx_roles_name ON roles(name);
```

#### 3. User_Roles Association Table

```sql
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,  -- user_id of admin who assigned
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
```

#### 4. Login_History Table

```sql
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME,
    ip_address VARCHAR(45),  -- IPv6 compatible
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    failure_reason VARCHAR(200),
    session_id VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_login_history_user_id ON login_history(user_id);
CREATE INDEX idx_login_history_login_time ON login_history(login_time);
CREATE INDEX idx_login_history_success ON login_history(success);
```

### SQLAlchemy Models

See [Appendix A](#appendix-a-sqlalchemy-models) for complete model definitions.

---

## Authentication Flow

### Login Flow Diagram

```
┌──────────────┐
│ User visits  │
│ /login page  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Display login form   │
│ - Username           │
│ - Password           │
│ - Remember Me        │
└──────┬───────────────┘
       │
       │ User submits credentials
       ▼
┌──────────────────────────────────┐
│ Validate form data               │
│ - Check CSRF token               │
│ - Validate required fields       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Query user by username           │
└──────┬───────────────────────────┘
       │
       ├─── User not found ──────────┐
       │                             │
       ▼                             ▼
┌──────────────────────┐    ┌───────────────────┐
│ User exists?         │    │ Log failed attempt│
└──────┬───────────────┘    │ Flash error       │
       │                    │ Redirect to login │
       │ Yes                └───────────────────┘
       ▼
┌──────────────────────────────────┐
│ Check if account is locked       │
│ (failed_login_attempts >= 5)     │
└──────┬───────────────────────────┘
       │
       ├─── Account locked ──────────┐
       │                             │
       ▼                             ▼
┌──────────────────────┐    ┌───────────────────┐
│ Account active?      │    │ Flash locked msg  │
└──────┬───────────────┘    │ Redirect to login │
       │                    └───────────────────┘
       │ Yes
       ▼
┌──────────────────────────────────┐
│ Verify password hash             │
│ check_password_hash()            │
└──────┬───────────────────────────┘
       │
       ├─── Invalid password ────────┐
       │                             │
       ▼                             ▼
┌──────────────────────┐    ┌───────────────────┐
│ Password valid?      │    │ Increment failed  │
└──────┬───────────────┘    │ attempts counter  │
       │                    │ Log failed attempt│
       │ Yes                │ Flash error       │
       ▼                    └───────────────────┘
┌──────────────────────────────────┐
│ Reset failed_login_attempts = 0  │
│ Update last_login timestamp      │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Create session with Flask-Login  │
│ login_user(user, remember=True)  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Log successful login             │
│ - IP address                     │
│ - User agent                     │
│ - Session ID                     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Flash success message            │
│ Redirect to dashboard            │
└──────────────────────────────────┘
```

### Logout Flow

```
User clicks logout → Clear session → Log logout time → Redirect to login
```

### Session Management

- **Session Duration**: 24 hours (configurable)
- **Remember Me**: 30 days (configurable)
- **Session Storage**: Server-side (Flask session)
- **Session Security**: HTTPOnly, Secure (HTTPS), SameSite=Lax

---

## Technical Implementation

### Phase 1: Install Dependencies

Add to `requirements.txt`:

```txt
# Authentication & Authorization
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0
```

Install:
```bash
pip install Flask-Login Flask-WTF WTForms email-validator
```

### Phase 2: Create Database Models

Create `app/models/auth.py`:

```python
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json


class User(UserMixin, db.Model):
    """User model for authentication."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref='users', lazy='dynamic')
    login_history = db.relationship('LoginHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Check if account is locked."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration."""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.session.commit()
    
    def unlock_account(self):
        """Unlock account."""
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter_by(name=role_name).first() is not None
    
    def has_permission(self, permission):
        """Check if user has a specific permission."""
        for role in self.roles:
            if permission in role.get_permissions():
                return True
        return self.is_superuser
    
    def get_primary_role(self):
        """Get user's primary (highest) role."""
        role_hierarchy = ['admin', 'manager', 'operator', 'viewer']
        for role_name in role_hierarchy:
            if self.has_role(role_name):
                return role_name
        return 'viewer'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model):
    """Role model for RBAC."""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_permissions(self):
        """Get list of permissions from JSON."""
        if self.permissions:
            return json.loads(self.permissions)
        return []
    
    def set_permissions(self, permissions_list):
        """Set permissions as JSON string."""
        self.permissions = json.dumps(permissions_list)
    
    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(db.Model):
    """Association table for User-Role many-to-many relationship."""
    
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )


class LoginHistory(db.Model):
    """Login history for audit trail."""

    __tablename__ = 'login_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    logout_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    success = db.Column(db.Boolean, default=True, nullable=False, index=True)
    failure_reason = db.Column(db.String(200))
    session_id = db.Column(db.String(255))

    def __repr__(self):
        return f'<LoginHistory user_id={self.user_id} at {self.login_time}>'
```

### Phase 3: Initialize Flask-Login

Update `app/__init__.py`:

```python
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    # ... existing code ...

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'

    # User loader callback
    from app.models.auth import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ... rest of existing code ...

    # Register auth blueprint
    from app.routes import auth
    app.register_blueprint(auth.bp)
```

### Phase 4: Create Authentication Routes

Create `app/routes/auth.py`:

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import db
from app.models.auth import User, LoginHistory
from app.forms.auth import LoginForm, RegistrationForm, ChangePasswordForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Log failed attempt if user not found
        if user is None:
            log_failed_login(form.username.data, 'User not found')
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))

        # Check if account is locked
        if user.is_locked():
            flash('Account is locked due to too many failed login attempts. Please try again later.', 'error')
            return redirect(url_for('auth.login'))

        # Check if account is active
        if not user.is_active:
            flash('Account is disabled. Please contact administrator.', 'error')
            return redirect(url_for('auth.login'))

        # Verify password
        if not user.check_password(form.password.data):
            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.lock_account(duration_minutes=30)
                flash('Account locked due to too many failed attempts. Try again in 30 minutes.', 'error')
            else:
                remaining = 5 - user.failed_login_attempts
                flash(f'Invalid password. {remaining} attempts remaining.', 'error')

            db.session.commit()
            log_failed_login(user.username, 'Invalid password', user.id)
            return redirect(url_for('auth.login'))

        # Successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create session
        login_user(user, remember=form.remember_me.data)

        # Log successful login
        log_successful_login(user)

        flash(f'Welcome back, {user.full_name or user.username}!', 'success')

        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')

        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout."""
    # Log logout time
    if current_user.is_authenticated:
        log_logout(current_user)

    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


def log_successful_login(user):
    """Log successful login attempt."""
    login_record = LoginHistory(
        user_id=user.id,
        login_time=datetime.utcnow(),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        success=True,
        session_id=session.get('_id')
    )
    db.session.add(login_record)
    db.session.commit()


def log_failed_login(username, reason, user_id=None):
    """Log failed login attempt."""
    if user_id:
        login_record = LoginHistory(
            user_id=user_id,
            login_time=datetime.utcnow(),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=False,
            failure_reason=reason
        )
        db.session.add(login_record)
        db.session.commit()


def log_logout(user):
    """Update logout time for current session."""
    last_login = LoginHistory.query.filter_by(
        user_id=user.id,
        session_id=session.get('_id')
    ).order_by(LoginHistory.login_time.desc()).first()

    if last_login:
        last_login.logout_time = datetime.utcnow()
        db.session.commit()
```

### Phase 5: Create WTForms

Create `app/forms/auth.py`:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.auth import User


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """User registration form (admin only)."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    full_name = StringField('Full Name', validators=[Length(max=200)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
```

### Phase 6: Create Authorization Decorators

Create `app/utils/decorators.py`:

```python
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to require specific role(s) for a route.

    Usage:
        @role_required('admin')
        @role_required('admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))

            # Superusers bypass role checks
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


def permission_required(permission):
    """
    Decorator to require specific permission for a route.

    Usage:
        @permission_required('delete_all')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))

            if not current_user.has_permission(permission):
                flash('You do not have permission to perform this action.', 'error')
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required('admin')(f)
```

### Phase 7: Protect Existing Routes

Update existing route files to add authentication and authorization:

**Example: `app/routes/clients.py`**

```python
from flask_login import login_required
from app.utils.decorators import role_required

# View clients - all authenticated users
@bp.route('/')
@login_required
def list_clients():
    # ... existing code ...

# Create client - admin and manager only
@bp.route('/create', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def create_client():
    # ... existing code ...

# Edit client - admin and manager only
@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def edit_client(id):
    # ... existing code ...

# Delete client - admin and manager only
@bp.route('/<int:id>/delete', methods=['POST'])
@role_required('admin', 'manager')
def delete_client(id):
    # ... existing code ...
```

Apply similar patterns to all routes based on the permissions matrix.

---

## Network Access Configuration

### Local Network Access (LAN)

#### Configuration

1. **Bind to Network Interface**

Update `run.py` or `wsgi.py`:

```python
# For development (Flask built-in server)
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=True
    )

# For production (Waitress)
from waitress import serve
serve(app, host='0.0.0.0', port=8080, threads=4)
```

2. **Firewall Configuration**

**Windows Firewall:**
```powershell
# Allow inbound traffic on port 8080
New-NetFirewallRule -DisplayName "Laser OS Web App" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

**Linux (ufw):**
```bash
sudo ufw allow 8080/tcp
```

3. **Access from LAN**

Users can access via:
- `http://192.168.1.100:8080` (replace with server IP)
- `http://laser-os.local:8080` (if mDNS/Bonjour configured)

#### Network Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    Office LAN (192.168.1.0/24)              │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Router/      │      │ Laser OS     │                    │
│  │ Firewall     │◄────►│ Server       │                    │
│  │ 192.168.1.1  │      │ 192.168.1.100│                    │
│  └──────┬───────┘      └──────────────┘                    │
│         │                                                   │
│         │                                                   │
│  ┌──────┴───────────────────────────────────┐              │
│  │                                           │              │
│  ▼                    ▼                      ▼              │
│ ┌────────┐      ┌────────┐            ┌────────┐           │
│ │ PC 1   │      │ PC 2   │            │ PC 3   │           │
│ │.101    │      │.102    │            │.103    │           │
│ └────────┘      └────────┘            └────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Remote Access (VPN)

#### Option 1: WireGuard VPN (Recommended)

**Advantages:**
- Modern, fast, secure
- Easy to configure
- Cross-platform support
- Low overhead

**Setup Steps:**

1. **Install WireGuard on Server**

```bash
# Ubuntu/Debian
sudo apt install wireguard

# Windows
# Download from https://www.wireguard.com/install/
```

2. **Generate Keys**

```bash
# Server keys
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Client keys (for each remote user)
wg genkey | tee client1_private.key | wg pubkey > client1_public.key
```

3. **Configure Server** (`/etc/wireguard/wg0.conf`)

```ini
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <server_private_key>

# Client 1
[Peer]
PublicKey = <client1_public_key>
AllowedIPs = 10.0.0.2/32

# Client 2
[Peer]
PublicKey = <client2_public_key>
AllowedIPs = 10.0.0.3/32
```

4. **Configure Client** (`client.conf`)

```ini
[Interface]
PrivateKey = <client_private_key>
Address = 10.0.0.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = <server_public_key>
Endpoint = <server_public_ip>:51820
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
```

5. **Start VPN**

```bash
# Server
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0

# Client
wg-quick up client
```

6. **Access Application**

Once connected to VPN, access via:
- `http://192.168.1.100:8080` (LAN IP)
- `http://10.0.0.1:8080` (VPN IP)

#### Option 2: OpenVPN

**Advantages:**
- Mature, well-tested
- Extensive documentation
- Enterprise-grade

**Setup:** See [Appendix B](#appendix-b-openvpn-setup) for detailed configuration.

#### Option 3: Tailscale (Easiest)

**Advantages:**
- Zero-configuration mesh VPN
- Built on WireGuard
- Free for personal use
- Automatic NAT traversal

**Setup:**

1. Install Tailscale on server and clients
2. Sign in with same account
3. Access via Tailscale IP (e.g., `http://100.64.0.1:8080`)

**Website:** https://tailscale.com

### HTTPS/SSL Configuration

#### Development (Self-Signed Certificate)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=laser-os.local"
```

Update `run.py`:

```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=('cert.pem', 'key.pem')
    )
```

#### Production (Let's Encrypt)

**Using Nginx Reverse Proxy:**

1. **Install Nginx and Certbot**

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

2. **Configure Nginx** (`/etc/nginx/sites-available/laser-os`)

```nginx
server {
    listen 80;
    server_name laser-os.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Get SSL Certificate**

```bash
sudo certbot --nginx -d laser-os.yourdomain.com
```

4. **Auto-Renewal**

```bash
sudo systemctl enable certbot.timer
```

---

## Security Best Practices

### 1. Password Security

**Requirements:**
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, symbols (recommended)
- Password strength meter on registration
- Prevent common passwords

**Implementation:**

```python
import re

def validate_password_strength(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"

    if not re.search(r'[0-9]', password):
        return False, "Password must contain number"

    # Check against common passwords
    common_passwords = ['password', '12345678', 'qwerty', 'admin']
    if password.lower() in common_passwords:
        return False, "Password is too common"

    return True, "Password is strong"
```

### 2. Session Security

**Configuration in `config.py`:**

```python
class Config:
    # Session security
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Remember me duration
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
```

### 3. CSRF Protection

**Enable in all forms:**

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    # ... existing code ...
    csrf.init_app(app)
```

### 4. Rate Limiting

**Install Flask-Limiter:**

```bash
pip install Flask-Limiter
```

**Configure:**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply to login route
@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    # ... existing code ...
```

### 5. Security Headers

**Add security headers:**

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 6. Input Validation

**Always validate and sanitize user input:**

```python
from markupsafe import escape

# Escape HTML in user input
safe_input = escape(user_input)

# Validate email format
from email_validator import validate_email, EmailNotValidError

try:
    valid = validate_email(email)
    email = valid.email
except EmailNotValidError as e:
    flash(str(e), 'error')
```

### 7. Database Security

**Best practices:**
- Use parameterized queries (SQLAlchemy handles this)
- Never store sensitive data in plain text
- Regular backups
- Encrypt database file (optional)

### 8. Logging and Monitoring

**Log security events:**

```python
import logging

security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Log failed login attempts
security_logger.warning(f'Failed login attempt for user {username} from {ip_address}')

# Log privilege escalation attempts
security_logger.warning(f'User {user.username} attempted to access admin page')
```

### 9. Regular Updates

**Keep dependencies updated:**

```bash
pip list --outdated
pip install --upgrade Flask Flask-Login Flask-SQLAlchemy
```

### 10. Backup Strategy

**Automated backups:**

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
DB_FILE="/path/to/data/laser_os.db"

# Create backup
cp "$DB_FILE" "$BACKUP_DIR/laser_os_$DATE.db"

# Keep only last 30 days
find "$BACKUP_DIR" -name "laser_os_*.db" -mtime +30 -delete
```

**Cron job:**
```cron
0 2 * * * /path/to/backup_database.sh
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Install dependencies (Flask-Login, Flask-WTF)
- [ ] Create database models (User, Role, UserRole, LoginHistory)
- [ ] Run database migrations
- [ ] Create initial roles and admin user

### Phase 2: Authentication (Week 1-2)
- [ ] Initialize Flask-Login
- [ ] Create login/logout routes
- [ ] Create login form and template
- [ ] Implement password hashing
- [ ] Add login history tracking
- [ ] Test authentication flow

### Phase 3: Authorization (Week 2)
- [ ] Create authorization decorators
- [ ] Define permission matrix
- [ ] Protect existing routes
- [ ] Add role checking to templates
- [ ] Test authorization rules

### Phase 4: User Management (Week 3)
- [ ] Create user management routes (admin only)
- [ ] Create user CRUD forms
- [ ] Create user list/detail templates
- [ ] Add role assignment interface
- [ ] Test user management

### Phase 5: Security Hardening (Week 3-4)
- [ ] Add CSRF protection
- [ ] Implement rate limiting
- [ ] Add security headers
- [ ] Configure session security
- [ ] Add password strength validation
- [ ] Test security measures

### Phase 6: Network Configuration (Week 4)
- [ ] Configure for LAN access
- [ ] Set up VPN (WireGuard/OpenVPN/Tailscale)
- [ ] Configure HTTPS/SSL
- [ ] Test remote access
- [ ] Document network setup

### Phase 7: Testing & Documentation (Week 4-5)
- [ ] Write unit tests for auth
- [ ] Write integration tests
- [ ] Create user documentation
- [ ] Create admin documentation
- [ ] Conduct security audit

### Phase 8: Deployment (Week 5)
- [ ] Deploy to production server
- [ ] Configure production settings
- [ ] Set up monitoring
- [ ] Train users
- [ ] Go live

---

## Testing Strategy

### Unit Tests

**Test authentication:**

```python
# tests/test_auth.py
import pytest
from app.models.auth import User
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_password_hashing(app):
    with app.app_context():
        user = User(username='test', email='test@example.com')
        user.set_password('password123')
        assert user.password_hash != 'password123'
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')

def test_user_roles(app):
    with app.app_context():
        user = User(username='test', email='test@example.com')
        role = Role(name='admin', display_name='Administrator')
        db.session.add(user)
        db.session.add(role)
        db.session.commit()

        user.roles.append(role)
        db.session.commit()

        assert user.has_role('admin')
        assert not user.has_role('manager')
```

### Integration Tests

**Test login flow:**

```python
def test_login_logout(client):
    # Create test user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Test login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Welcome back' in response.data

    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'logged out' in response.data
```

### Security Tests

**Test authorization:**

```python
def test_admin_required(client):
    # Create regular user
    user = User(username='user', email='user@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Login as regular user
    client.post('/auth/login', data={
        'username': 'user',
        'password': 'password'
    })

    # Try to access admin page
    response = client.get('/admin/users')
    assert response.status_code == 403
```

---

## Deployment Guide

### Production Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG = False
- [ ] Configure HTTPS/SSL
- [ ] Enable session security settings
- [ ] Set up firewall rules
- [ ] Configure VPN for remote access
- [ ] Set up automated backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Create admin user
- [ ] Test all authentication flows
- [ ] Test all authorization rules
- [ ] Document credentials securely

### Environment Variables

Create `.env` file:

```bash
# Flask
SECRET_KEY=<generate-strong-random-key>
FLASK_ENV=production

# Database
DATABASE_PATH=/path/to/production/laser_os.db

# Session
SESSION_COOKIE_SECURE=True
PERMANENT_SESSION_LIFETIME=86400  # 24 hours in seconds

# Email (for password reset, notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Generate SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

### Production Server (Waitress)

**Install:**
```bash
pip install waitress
```

**Run:**
```python
# wsgi.py
from waitress import serve
from app import create_app

app = create_app('production')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080, threads=4)
```

**Systemd Service** (`/etc/systemd/system/laser-os.service`):

```ini
[Unit]
Description=Laser OS Web Application
After=network.target

[Service]
User=laser-os
WorkingDirectory=/opt/laser-os
Environment="PATH=/opt/laser-os/venv/bin"
ExecStart=/opt/laser-os/venv/bin/python wsgi.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable laser-os
sudo systemctl start laser-os
```

---

## Appendices

### Appendix A: Complete Model Integration

**Update `app/models.py` to import auth models:**

```python
# At the top of app/models.py
from app.models.auth import User, Role, UserRole, LoginHistory

# Or create app/models/__init__.py and import all models
```

**Create `app/models/__init__.py`:**

```python
from app.models.auth import User, Role, UserRole, LoginHistory
from app.models.business import Client, Project, Product, DesignFile, QueueItem, LaserRun, InventoryItem

__all__ = [
    'User', 'Role', 'UserRole', 'LoginHistory',
    'Client', 'Project', 'Product', 'DesignFile', 'QueueItem', 'LaserRun', 'InventoryItem'
]
```

### Appendix B: Database Migration Script

**Create initial roles and admin user:**

```python
# scripts/init_auth.py
"""Initialize authentication system with roles and admin user."""

from app import create_app, db
from app.models.auth import User, Role
import getpass

def init_roles():
    """Create default roles."""
    roles_data = [
        {
            'name': 'admin',
            'display_name': 'Administrator',
            'description': 'Full system access including user management',
            'permissions': ['view_all', 'create_all', 'edit_all', 'delete_all', 'manage_users', 'manage_settings', 'view_logs']
        },
        {
            'name': 'manager',
            'display_name': 'Manager',
            'description': 'Business operations access without user management',
            'permissions': ['view_all', 'create_business', 'edit_business', 'delete_business', 'view_logs']
        },
        {
            'name': 'operator',
            'display_name': 'Operator',
            'description': 'Production operations access',
            'permissions': ['view_all', 'edit_production', 'manage_queue', 'upload_files']
        },
        {
            'name': 'viewer',
            'display_name': 'Viewer',
            'description': 'Read-only access to all data',
            'permissions': ['view_all']
        }
    ]

    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description']
            )
            role.set_permissions(role_data['permissions'])
            db.session.add(role)
            print(f"✓ Created role: {role_data['display_name']}")
        else:
            print(f"ℹ Role already exists: {role_data['display_name']}")

    db.session.commit()
    print("\n✓ Roles initialized successfully")


def create_admin_user():
    """Create initial admin user."""
    print("\n" + "="*60)
    print("CREATE ADMIN USER")
    print("="*60)

    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("⚠ Admin user already exists")
        return

    # Get admin details
    username = input("Admin username [admin]: ").strip() or 'admin'
    email = input("Admin email: ").strip()
    full_name = input("Full name: ").strip()

    # Get password
    while True:
        password = getpass.getpass("Password (min 8 chars): ")
        password2 = getpass.getpass("Confirm password: ")

        if password != password2:
            print("✗ Passwords don't match. Try again.")
            continue

        if len(password) < 8:
            print("✗ Password must be at least 8 characters. Try again.")
            continue

        break

    # Create admin user
    admin = User(
        username=username,
        email=email,
        full_name=full_name,
        is_active=True,
        is_superuser=True
    )
    admin.set_password(password)

    # Assign admin role
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        admin.roles.append(admin_role)

    db.session.add(admin)
    db.session.commit()

    print(f"\n✓ Admin user '{username}' created successfully")
    print(f"  Email: {email}")
    print(f"  Role: Administrator")
    print("\n⚠ Keep these credentials secure!")


def main():
    """Main initialization function."""
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("LASER OS - AUTHENTICATION SYSTEM INITIALIZATION")
        print("="*60)

        # Create tables
        print("\nCreating database tables...")
        db.create_all()
        print("✓ Database tables created")

        # Initialize roles
        print("\nInitializing roles...")
        init_roles()

        # Create admin user
        create_admin_user()

        print("\n" + "="*60)
        print("✓ INITIALIZATION COMPLETE")
        print("="*60)
        print("\nYou can now start the application and log in with your admin credentials.")
        print("Access the application at: http://localhost:5000/auth/login")
        print("\n")


if __name__ == '__main__':
    main()
```

**Run the script:**

```bash
python scripts/init_auth.py
```

### Appendix C: Login Template

**Create `app/templates/auth/login.html`:**

```html
{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <div class="auth-header">
            <h2>Welcome to Laser OS</h2>
            <p>Please log in to continue</p>
        </div>

        <form method="POST" action="{{ url_for('auth.login') }}" class="auth-form">
            {{ form.hidden_tag() }}

            <div class="form-group">
                {{ form.username.label(class="form-label") }}
                {{ form.username(class="form-control", placeholder="Enter your username", autofocus=true) }}
                {% if form.username.errors %}
                    <div class="form-error">
                        {% for error in form.username.errors %}
                            <span>{{ error }}</span>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>

            <div class="form-group">
                {{ form.password.label(class="form-label") }}
                {{ form.password(class="form-control", placeholder="Enter your password") }}
                {% if form.password.errors %}
                    <div class="form-error">
                        {% for error in form.password.errors %}
                            <span>{{ error }}</span>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>

            <div class="form-group form-check">
                {{ form.remember_me(class="form-check-input") }}
                {{ form.remember_me.label(class="form-check-label") }}
            </div>

            <div class="form-group">
                {{ form.submit(class="btn btn-primary btn-block") }}
            </div>
        </form>

        <div class="auth-footer">
            <p>Laser OS Tier 1 - Secure Access</p>
        </div>
    </div>
</div>

<style>
.auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    padding: 2rem;
}

.auth-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 2rem;
    width: 100%;
    max-width: 400px;
}

.auth-header {
    text-align: center;
    margin-bottom: 2rem;
}

.auth-header h2 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.auth-header p {
    margin: 0;
    color: #666;
}

.auth-form .form-group {
    margin-bottom: 1.5rem;
}

.auth-form .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
}

.auth-form .form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.auth-form .form-control:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
}

.auth-form .form-check {
    display: flex;
    align-items: center;
}

.auth-form .form-check-input {
    margin-right: 0.5rem;
}

.auth-form .btn-block {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    font-weight: 500;
}

.auth-footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
    color: #666;
    font-size: 0.875rem;
}

.form-error {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}
</style>
{% endblock %}
```

### Appendix D: User Management Templates

**Create `app/templates/admin/users_list.html`:**

```html
{% extends "base.html" %}

{% block title %}User Management{% endblock %}

{% block content %}
<div class="page-header">
    <h1>User Management</h1>
    <a href="{{ url_for('admin.create_user') }}" class="btn btn-primary">
        <i class="icon-plus"></i> Create New User
    </a>
</div>

<div class="users-table">
    <table class="table">
        <thead>
            <tr>
                <th>Username</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Roles</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td>{{ user.username }}</td>
                <td>{{ user.full_name or '-' }}</td>
                <td>{{ user.email }}</td>
                <td>
                    {% for role in user.roles %}
                        <span class="badge badge-{{ role.name }}">{{ role.display_name }}</span>
                    {% endfor %}
                </td>
                <td>
                    {% if user.is_active %}
                        <span class="status-active">Active</span>
                    {% else %}
                        <span class="status-inactive">Inactive</span>
                    {% endif %}
                </td>
                <td>{{ user.last_login|datetime if user.last_login else 'Never' }}</td>
                <td>
                    <a href="{{ url_for('admin.edit_user', id=user.id) }}" class="btn btn-sm btn-secondary">Edit</a>
                    {% if not user.is_superuser %}
                        <form method="POST" action="{{ url_for('admin.delete_user', id=user.id) }}" style="display:inline;">
                            {{ csrf_token() }}
                            <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Are you sure?')">Delete</button>
                        </form>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

### Appendix E: Template Context Processor

**Add user context to all templates:**

```python
# In app/__init__.py

def register_context_processors(app):
    """Register context processors to inject variables into templates."""

    @app.context_processor
    def inject_settings():
        """Inject common settings into all templates."""
        from flask_login import current_user
        return {
            'company_name': app.config.get('COMPANY_NAME', 'Laser OS'),
            'current_year': __import__('datetime').datetime.now().year,
            'current_user': current_user
        }
```

**Update `base.html` to show user info:**

```html
<!-- In header section -->
<div class="user-info">
    {% if current_user.is_authenticated %}
        <span class="user-name">{{ current_user.full_name or current_user.username }}</span>
        <span class="user-role">{{ current_user.get_primary_role()|title }}</span>
        <a href="{{ url_for('auth.logout') }}" class="btn btn-sm btn-outline">Logout</a>
    {% else %}
        <a href="{{ url_for('auth.login') }}" class="btn btn-sm btn-primary">Login</a>
    {% endif %}
</div>
```

### Appendix F: OpenVPN Setup

**Server Configuration:**

1. **Install OpenVPN:**
```bash
sudo apt install openvpn easy-rsa
```

2. **Initialize PKI:**
```bash
make-cadir ~/openvpn-ca
cd ~/openvpn-ca
./easyrsa init-pki
./easyrsa build-ca
./easyrsa gen-dh
./easyrsa build-server-full server nopass
```

3. **Server Config** (`/etc/openvpn/server.conf`):
```
port 1194
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
server 10.8.0.0 255.255.255.0
push "route 192.168.1.0 255.255.255.0"
keepalive 10 120
cipher AES-256-CBC
user nobody
group nogroup
persist-key
persist-tun
status openvpn-status.log
verb 3
```

4. **Client Config** (`client.ovpn`):
```
client
dev tun
proto udp
remote <server-public-ip> 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca ca.crt
cert client.crt
key client.key
cipher AES-256-CBC
verb 3
```

### Appendix G: Configuration Reference

**Complete `config.py` additions:**

```python
class Config:
    # ... existing config ...

    # Authentication
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Session Configuration
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', 24)))

    # Remember Me Configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=int(os.environ.get('REMEMBER_COOKIE_DAYS', 30)))
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes')
    REMEMBER_COOKIE_HTTPONLY = True

    # Account Lockout
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_DURATION = int(os.environ.get('ACCOUNT_LOCKOUT_DURATION', 30))  # minutes

    # Password Requirements
    MIN_PASSWORD_LENGTH = int(os.environ.get('MIN_PASSWORD_LENGTH', 8))
    REQUIRE_PASSWORD_COMPLEXITY = os.environ.get('REQUIRE_PASSWORD_COMPLEXITY', 'True').lower() in ('true', '1', 'yes')
```

### Appendix H: Quick Reference Commands

**Database Operations:**

```bash
# Create all tables
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Initialize auth system
python scripts/init_auth.py

# Create database backup
cp data/laser_os.db data/laser_os_backup_$(date +%Y%m%d).db
```

**User Management (Python Shell):**

```python
# Start Flask shell
flask shell

# Create user
from app.models.auth import User, Role
user = User(username='john', email='john@example.com', full_name='John Doe')
user.set_password('password123')
db.session.add(user)
db.session.commit()

# Assign role
role = Role.query.filter_by(name='operator').first()
user.roles.append(role)
db.session.commit()

# Deactivate user
user.is_active = False
db.session.commit()

# Reset password
user.set_password('newpassword')
db.session.commit()

# Unlock account
user.unlock_account()
```

**Network Commands:**

```bash
# Check if port is open
netstat -an | grep 8080

# Test local access
curl http://localhost:8080

# Test LAN access
curl http://192.168.1.100:8080

# Check firewall rules (Windows)
netsh advfirewall firewall show rule name="Laser OS Web App"

# Check firewall rules (Linux)
sudo ufw status
```

---

## Summary

This document provides a comprehensive design and implementation plan for adding multi-user authentication and role-based authorization to the Laser OS Tier 1 application. The system includes:

✅ **Secure Authentication**
- Password hashing with bcrypt
- Session management with Flask-Login
- Login history and audit trail
- Account lockout protection

✅ **Role-Based Authorization**
- 4 user roles (Admin, Manager, Operator, Viewer)
- Granular permission matrix
- Custom decorators for route protection
- Template-level permission checking

✅ **Network Access**
- Local LAN configuration
- VPN options (WireGuard, OpenVPN, Tailscale)
- HTTPS/SSL setup
- Reverse proxy configuration

✅ **Security Best Practices**
- CSRF protection
- Rate limiting
- Security headers
- Input validation
- Regular backups

✅ **Implementation Roadmap**
- 8-phase implementation plan
- Detailed code examples
- Testing strategy
- Deployment guide

### Next Steps

1. **Review this document** with your team
2. **Set up development environment** with required dependencies
3. **Follow the implementation roadmap** phase by phase
4. **Test thoroughly** at each phase
5. **Deploy to production** with proper security measures
6. **Train users** on the new authentication system

### Support Resources

- Flask-Login Documentation: https://flask-login.readthedocs.io/
- Flask-WTF Documentation: https://flask-wtf.readthedocs.io/
- WireGuard Documentation: https://www.wireguard.com/
- OWASP Security Guidelines: https://owasp.org/

---

**Document End**

*For questions or clarifications, refer to the specific sections above or consult the Flask and security documentation.*


