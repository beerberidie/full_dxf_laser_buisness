"""
Authentication Models for Laser OS Tier 1

This module contains all authentication and authorization related models:
- User: User accounts with authentication
- Role: User roles for RBAC
- UserRole: Many-to-many relationship between users and roles
- LoginHistory: Audit trail for login attempts
"""

from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    
    Inherits from UserMixin to provide Flask-Login required methods:
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()
    """
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User information
    full_name = db.Column(db.String(200))
    display_name = db.Column(db.String(120))  # Production Automation: Display name for operators

    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)

    # Production Automation: Role-based access control
    # Values: "operator", "manager", "admin"
    role = db.Column(db.String(50), default='operator', nullable=False, index=True)

    # Production Automation: Operator status
    # True if this user can be selected as an operator for laser runs
    is_active_operator = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime)
    
    # Relationships
    roles = db.relationship(
        'Role',
        secondary='user_roles',
        primaryjoin='User.id==UserRole.user_id',
        secondaryjoin='Role.id==UserRole.role_id',
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    login_history = db.relationship('LoginHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """
        Check if user has a specific role.
        
        Args:
            role_name (str): Name of the role to check
            
        Returns:
            bool: True if user has the role, False otherwise
        """
        return self.roles.filter_by(name=role_name).first() is not None
    
    def has_permission(self, permission):
        """
        Check if user has a specific permission.
        
        Args:
            permission (str): Permission code to check
            
        Returns:
            bool: True if user has the permission, False otherwise
        """
        # Superuser has all permissions
        if self.is_superuser:
            return True
        
        # Check all user's roles for the permission
        for role in self.roles:
            if permission in role.get_permissions():
                return True
        
        return False
    
    def get_primary_role(self):
        """
        Get the user's primary (highest priority) role.
        
        Returns:
            Role: The primary role or None
        """
        # Priority order: admin > manager > operator > viewer
        role_priority = ['admin', 'manager', 'operator', 'viewer']
        
        for role_name in role_priority:
            role = self.roles.filter_by(name=role_name).first()
            if role:
                return role
        
        return None
    
    def is_locked(self):
        """
        Check if the account is currently locked.
        
        Returns:
            bool: True if account is locked, False otherwise
        """
        if self.locked_until is None:
            return False
        
        return datetime.utcnow() < self.locked_until
    
    def lock_account(self, duration_minutes=30):
        """
        Lock the account for a specified duration.
        
        Args:
            duration_minutes (int): Number of minutes to lock the account
        """
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self):
        """Unlock the account and reset failed login attempts."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    # Note: is_authenticated and is_active are provided by UserMixin
    # and use the is_active column directly


class Role(db.Model):
    """
    Role model for role-based access control (RBAC).
    
    Roles define sets of permissions that can be assigned to users.
    """
    __tablename__ = 'roles'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Role information
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Permissions stored as JSON
    permissions = db.Column(db.Text)  # JSON array of permission codes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def get_permissions(self):
        """
        Get the list of permissions for this role.
        
        Returns:
            list: List of permission codes
        """
        if not self.permissions:
            return []
        
        try:
            return json.loads(self.permissions)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_permissions(self, permissions_list):
        """
        Set the permissions for this role.
        
        Args:
            permissions_list (list): List of permission codes
        """
        self.permissions = json.dumps(permissions_list)
    
    def add_permission(self, permission):
        """
        Add a permission to this role.
        
        Args:
            permission (str): Permission code to add
        """
        perms = self.get_permissions()
        if permission not in perms:
            perms.append(permission)
            self.set_permissions(perms)
    
    def remove_permission(self, permission):
        """
        Remove a permission from this role.
        
        Args:
            permission (str): Permission code to remove
        """
        perms = self.get_permissions()
        if permission in perms:
            perms.remove(permission)
            self.set_permissions(perms)


class UserRole(db.Model):
    """
    Association table for many-to-many relationship between users and roles.
    
    Tracks when roles were assigned and by whom.
    """
    __tablename__ = 'user_roles'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    
    # Metadata
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Unique constraint to prevent duplicate role assignments
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )
    
    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'


class LoginHistory(db.Model):
    """
    Login history model for audit trail and security monitoring.
    
    Tracks all login attempts (successful and failed) for compliance and security.
    """
    __tablename__ = 'login_history'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key (nullable to allow logging failed attempts for non-existent users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    
    # Login information
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    logout_time = db.Column(db.DateTime)
    
    # Request information
    ip_address = db.Column(db.String(45))  # IPv6 max length
    user_agent = db.Column(db.Text)
    
    # Login status
    success = db.Column(db.Boolean, default=True, nullable=False)
    failure_reason = db.Column(db.String(200))
    
    # Session information
    session_id = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<LoginHistory user_id={self.user_id} time={self.login_time} success={self.success}>'

