"""
Sage Integration Models for Laser OS

This module contains all Sage Business Cloud Accounting integration models:
- SageConnection: OAuth connection and token management
- SageBusiness: Sage business contexts for multi-business support
- SageSyncCursor: Incremental sync tracking
- SageAuditLog: Audit trail for Sage operations
"""

from datetime import datetime, timedelta
from app import db
import json


class SageConnection(db.Model):
    """
    Sage OAuth connection model for managing authentication tokens.
    
    Stores OAuth 2.0 tokens and manages token refresh for Sage API access.
    Each user can have one active Sage connection.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        access_token: OAuth access token (encrypted in production)
        refresh_token: OAuth refresh token (encrypted in production)
        token_type: Token type (usually 'Bearer')
        expires_at: Token expiration timestamp
        scope: OAuth scope granted
        is_active: Connection status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'sage_connections'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    
    # OAuth tokens (TODO: Encrypt in production)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    token_type = db.Column(db.String(50), default='Bearer', nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    scope = db.Column(db.String(500))
    
    # Connection status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('sage_connection', uselist=False))
    businesses = db.relationship('SageBusiness', backref='connection', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('SageAuditLog', backref='connection', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SageConnection user_id={self.user_id} active={self.is_active}>'
    
    def is_token_expired(self, buffer_seconds=60):
        """
        Check if the access token is expired or will expire soon.
        
        Args:
            buffer_seconds (int): Buffer time in seconds before actual expiry (default: 60)
            
        Returns:
            bool: True if token is expired or will expire within buffer time
        """
        if not self.expires_at:
            return True
        return datetime.utcnow() >= (self.expires_at - timedelta(seconds=buffer_seconds))
    
    def to_dict(self):
        """Convert connection to dictionary (excluding sensitive tokens)."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SageBusiness(db.Model):
    """
    Sage Business model for multi-business context management.
    
    Stores information about Sage businesses that the user has access to.
    Users can have multiple businesses and select which one to work with.
    
    Attributes:
        id: Primary key
        connection_id: Foreign key to sage_connections table
        sage_business_id: Sage's unique business ID (used in X-Business header)
        name: Business name
        displayed_as: Business display name from Sage
        is_selected: Whether this is the currently selected business
        metadata: Additional business metadata (JSON)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'sage_businesses'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Connection relationship
    connection_id = db.Column(db.Integer, db.ForeignKey('sage_connections.id'), nullable=False, index=True)
    
    # Sage business information
    sage_business_id = db.Column(db.String(100), nullable=False, index=True)
    name = db.Column(db.String(200))
    displayed_as = db.Column(db.String(200))
    
    # Selection status
    is_selected = db.Column(db.Boolean, default=False, nullable=False)

    # Additional metadata (JSON) - renamed to avoid SQLAlchemy reserved attribute
    business_metadata = db.Column(db.Text)  # Stores JSON string
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sync_cursors = db.relationship('SageSyncCursor', backref='business', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint: one business per connection
    __table_args__ = (
        db.UniqueConstraint('connection_id', 'sage_business_id', name='uq_connection_business'),
    )
    
    def __repr__(self):
        return f'<SageBusiness {self.sage_business_id}: {self.name}>'
    
    def get_metadata(self):
        """Parse and return metadata as dictionary."""
        if self.business_metadata:
            try:
                return json.loads(self.business_metadata)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_metadata(self, data):
        """Set metadata from dictionary."""
        if data:
            self.business_metadata = json.dumps(data)
        else:
            self.business_metadata = None
    
    def to_dict(self):
        """Convert business to dictionary."""
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'sage_business_id': self.sage_business_id,
            'name': self.name,
            'displayed_as': self.displayed_as,
            'is_selected': self.is_selected,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SageSyncCursor(db.Model):
    """
    Sage Sync Cursor model for incremental data synchronization.
    
    Tracks the last sync timestamp for each resource type to enable
    efficient incremental syncing using Sage's updated_or_created_since parameter.
    
    Attributes:
        id: Primary key
        business_id: Foreign key to sage_businesses table
        resource_type: Type of resource (e.g., 'sales_invoices', 'contacts')
        last_sync_at: Timestamp of last successful sync
        cursor_value: Cursor value for pagination (if applicable)
        sync_status: Status of last sync (success, failed, in_progress)
        error_message: Error message if sync failed
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'sage_sync_cursors'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Business relationship
    business_id = db.Column(db.Integer, db.ForeignKey('sage_businesses.id'), nullable=False, index=True)
    
    # Resource information
    resource_type = db.Column(db.String(100), nullable=False, index=True)
    
    # Sync tracking
    last_sync_at = db.Column(db.DateTime)
    cursor_value = db.Column(db.String(500))
    sync_status = db.Column(db.String(50), default='pending', nullable=False)  # pending, in_progress, success, failed
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint: one cursor per business per resource type
    __table_args__ = (
        db.UniqueConstraint('business_id', 'resource_type', name='uq_business_resource'),
    )
    
    def __repr__(self):
        return f'<SageSyncCursor business_id={self.business_id} resource={self.resource_type}>'
    
    def to_dict(self):
        """Convert sync cursor to dictionary."""
        return {
            'id': self.id,
            'business_id': self.business_id,
            'resource_type': self.resource_type,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'cursor_value': self.cursor_value,
            'sync_status': self.sync_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SageAuditLog(db.Model):
    """
    Sage Audit Log model for tracking all Sage API operations.
    
    Provides compliance and traceability for all write operations
    (create, update, delete) performed through the Sage integration.
    
    Attributes:
        id: Primary key
        connection_id: Foreign key to sage_connections table
        user_id: Foreign key to users table
        operation_type: Type of operation (create, update, delete, read)
        resource_type: Type of resource (e.g., 'sales_invoice', 'contact')
        resource_id: Sage resource ID
        status: Operation status (preview, confirmed, success, failed)
        request_data: Request payload (JSON)
        response_data: Response data (JSON)
        error_message: Error message if operation failed
        created_at: Operation timestamp
    """
    
    __tablename__ = 'sage_audit_logs'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    connection_id = db.Column(db.Integer, db.ForeignKey('sage_connections.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Operation information
    operation_type = db.Column(db.String(50), nullable=False, index=True)  # create, update, delete, read
    resource_type = db.Column(db.String(100), nullable=False, index=True)  # sales_invoice, contact, etc.
    resource_id = db.Column(db.String(100), index=True)  # Sage resource ID
    
    # Operation status
    status = db.Column(db.String(50), nullable=False, index=True)  # preview, confirmed, success, failed
    
    # Request/Response data (JSON)
    request_data = db.Column(db.Text)  # Stores JSON string
    response_data = db.Column(db.Text)  # Stores JSON string
    error_message = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('sage_audit_logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SageAuditLog {self.operation_type} {self.resource_type} status={self.status}>'
    
    def get_request_data(self):
        """Parse and return request data as dictionary."""
        if self.request_data:
            try:
                return json.loads(self.request_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_request_data(self, data):
        """Set request data from dictionary."""
        if data:
            self.request_data = json.dumps(data)
        else:
            self.request_data = None
    
    def get_response_data(self):
        """Parse and return response data as dictionary."""
        if self.response_data:
            try:
                return json.loads(self.response_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_response_data(self, data):
        """Set response data from dictionary."""
        if data:
            self.response_data = json.dumps(data)
        else:
            self.response_data = None
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'user_id': self.user_id,
            'operation_type': self.operation_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'status': self.status,
            'request_data': self.get_request_data(),
            'response_data': self.get_response_data(),
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

