"""
Laser OS Tier 1 - Database Models

This module defines SQLAlchemy models for all database tables.
Models will be added incrementally across phases.
"""

from datetime import datetime
from app import db
from sqlalchemy import event


class Client(db.Model):
    """
    Client model representing customers.
    
    Attributes:
        id: Primary key
        client_code: Unique code (CL-xxxx format)
        name: Client company name
        contact_person: Primary contact name
        email: Contact email
        phone: Contact phone number
        address: Physical/postal address
        notes: Additional notes
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True, cascade='all, delete-orphan')
    communications = db.relationship('Communication', backref='client', lazy=True)  # Phase 9

    def __repr__(self):
        return f'<Client {self.client_code}: {self.name}>'
    
    def to_dict(self):
        """Convert client to dictionary."""
        return {
            'id': self.id,
            'client_code': self.client_code,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Project(db.Model):
    """
    Project/Job model representing customer projects.

    Attributes:
        id: Primary key
        project_code: Unique code (JB-yyyy-mm-CLxxxx-### format)
        client_id: Foreign key to clients table
        name: Project name/description
        description: Detailed project description
        status: Project status (Quote, Approved, In Progress, Completed, Cancelled)
        quote_date: Date quote was created
        approval_date: Date project was approved
        due_date: Project due date
        completion_date: Date project was completed
        quoted_price: Initial quoted price
        final_price: Final invoiced price
        notes: Additional notes
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'projects'

    # Status constants - Enhanced workflow for Phase 9
    STATUS_REQUEST = 'Request'
    STATUS_QUOTE_APPROVAL = 'Quote & Approval'
    STATUS_APPROVED_POP = 'Approved (POP Received)'
    STATUS_QUEUED = 'Queued (Scheduled for Cutting)'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    # Legacy status constants (for backward compatibility)
    STATUS_QUOTE = 'Quote'
    STATUS_APPROVED = 'Approved'

    VALID_STATUSES = [
        STATUS_REQUEST,
        STATUS_QUOTE_APPROVAL,
        STATUS_APPROVED_POP,
        STATUS_QUEUED,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
        # Legacy statuses
        STATUS_QUOTE,
        STATUS_APPROVED
    ]

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default=STATUS_QUOTE, index=True)

    # Timeline
    quote_date = db.Column(db.Date)
    approval_date = db.Column(db.Date)
    due_date = db.Column(db.Date, index=True)
    completion_date = db.Column(db.Date)

    # Pricing
    quoted_price = db.Column(db.Numeric(10, 2))
    final_price = db.Column(db.Numeric(10, 2))

    # Additional info
    notes = db.Column(db.Text)

    # Phase 9: Material and production details
    material_type = db.Column(db.String(100), index=True)
    material_quantity_sheets = db.Column(db.Integer)
    parts_quantity = db.Column(db.Integer)
    estimated_cut_time = db.Column(db.Integer)  # in minutes
    number_of_bins = db.Column(db.Integer)
    drawing_creation_time = db.Column(db.Integer)  # in minutes

    # Phase 9: POP (Proof of Payment) tracking
    pop_received = db.Column(db.Boolean, default=False, index=True)
    pop_received_date = db.Column(db.Date)
    pop_deadline = db.Column(db.Date, index=True)  # Auto-calculated: POP date + 3 days

    # Phase 9: Client notification tracking
    client_notified = db.Column(db.Boolean, default=False)
    client_notified_date = db.Column(db.DateTime)

    # Phase 9: Delivery confirmation tracking
    delivery_confirmed = db.Column(db.Boolean, default=False)
    delivery_confirmed_date = db.Column(db.Date)

    # Phase 9: Scheduling
    scheduled_cut_date = db.Column(db.Date, index=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project_products = db.relationship('ProjectProduct', backref='project', lazy=True, cascade='all, delete-orphan')
    design_files = db.relationship('DesignFile', backref='project', lazy=True, cascade='all, delete-orphan')
    queue_items = db.relationship('QueueItem', backref='project', lazy=True, cascade='all, delete-orphan')
    laser_runs = db.relationship('LaserRun', backref='project', lazy=True, cascade='all, delete-orphan')
    # Phase 9: New relationships
    documents = db.relationship('ProjectDocument', backref='project', lazy=True, cascade='all, delete-orphan')
    communications = db.relationship('Communication', backref='project', lazy=True)
    # quotes = db.relationship('Quote', backref='project', lazy=True, cascade='all, delete-orphan')  # Phase 7
    # invoices = db.relationship('Invoice', backref='project', lazy=True, cascade='all, delete-orphan')  # Phase 7

    def __repr__(self):
        return f'<Project {self.project_code}: {self.name}>'

    def to_dict(self):
        """Convert project to dictionary."""
        return {
            'id': self.id,
            'project_code': self.project_code,
            'client_id': self.client_id,
            'client_code': self.client.client_code if self.client else None,
            'client_name': self.client.name if self.client else None,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'quote_date': self.quote_date.isoformat() if self.quote_date else None,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'quoted_price': float(self.quoted_price) if self.quoted_price else None,
            'final_price': float(self.final_price) if self.final_price else None,
            'notes': self.notes,
            # Phase 9: Material and production details
            'material_type': self.material_type,
            'material_quantity_sheets': self.material_quantity_sheets,
            'parts_quantity': self.parts_quantity,
            'estimated_cut_time': self.estimated_cut_time,
            'number_of_bins': self.number_of_bins,
            'drawing_creation_time': self.drawing_creation_time,
            # Phase 9: POP tracking
            'pop_received': self.pop_received,
            'pop_received_date': self.pop_received_date.isoformat() if self.pop_received_date else None,
            'pop_deadline': self.pop_deadline.isoformat() if self.pop_deadline else None,
            # Phase 9: Notification tracking
            'client_notified': self.client_notified,
            'client_notified_date': self.client_notified_date.isoformat() if self.client_notified_date else None,
            # Phase 9: Delivery tracking
            'delivery_confirmed': self.delivery_confirmed,
            'delivery_confirmed_date': self.delivery_confirmed_date.isoformat() if self.delivery_confirmed_date else None,
            # Phase 9: Scheduling
            'scheduled_cut_date': self.scheduled_cut_date.isoformat() if self.scheduled_cut_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def is_overdue(self):
        """Check if project is overdue."""
        if self.due_date and self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
            from datetime import date
            return date.today() > self.due_date
        return False

    @property
    def days_until_due(self):
        """Calculate days until due date."""
        if self.due_date and self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
            from datetime import date
            delta = self.due_date - date.today()
            return delta.days
        return None

    # Phase 9: New properties and methods

    @property
    def is_ready_for_quote(self):
        """
        Check if project has all required fields for quote generation.

        Required fields:
        - Material type
        - Material quantity (sheets)
        - Parts quantity
        - Estimated cut time
        - At least one DXF file uploaded
        """
        return all([
            self.material_type,
            self.material_quantity_sheets,
            self.parts_quantity,
            self.estimated_cut_time,
            len(self.design_files) > 0
        ])

    @property
    def is_within_pop_deadline(self):
        """
        Check if project is within 3-day POP deadline.

        Returns True if:
        - No POP deadline set (not applicable)
        - Today is on or before the deadline
        - Project is completed or cancelled (deadline no longer applies)
        """
        if self.pop_deadline and self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
            from datetime import date
            return date.today() <= self.pop_deadline
        return True

    @property
    def days_until_pop_deadline(self):
        """
        Calculate days until POP deadline.

        Returns:
        - Positive number: days remaining
        - Negative number: days overdue
        - None: no deadline set or project completed/cancelled
        """
        if self.pop_deadline and self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
            from datetime import date
            delta = self.pop_deadline - date.today()
            return delta.days
        return None

    @property
    def estimated_cut_time_hours(self):
        """Convert estimated cut time from minutes to hours (formatted)."""
        if self.estimated_cut_time:
            hours = self.estimated_cut_time // 60
            minutes = self.estimated_cut_time % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return None

    @property
    def drawing_creation_time_hours(self):
        """Convert drawing creation time from minutes to hours (formatted)."""
        if self.drawing_creation_time:
            hours = self.drawing_creation_time // 60
            minutes = self.drawing_creation_time % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return None

    def calculate_pop_deadline(self):
        """
        Calculate and set POP deadline (POP received date + 3 days).

        This method should be called whenever pop_received_date is set.
        The 3-day rule ensures projects are scheduled for cutting within
        3 business days of receiving proof of payment.
        """
        if self.pop_received_date:
            from datetime import timedelta
            self.pop_deadline = self.pop_received_date + timedelta(days=3)
        else:
            self.pop_deadline = None


class ActivityLog(db.Model):
    """
    Activity log model for audit trail.
    
    Tracks all significant actions in the system for compliance and debugging.
    
    Attributes:
        id: Primary key
        entity_type: Type of entity (CLIENT, PROJECT, FILE, etc.)
        entity_id: ID of the entity
        action: Action performed (CREATED, UPDATED, DELETED, etc.)
        user: Username who performed the action
        details: JSON string with additional details
        ip_address: IP address of the user
        created_at: Timestamp of the action
    """
    
    __tablename__ = 'activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(100), default='admin', nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<ActivityLog {self.entity_type}:{self.entity_id} {self.action}>'
    
    def to_dict(self):
        """Convert activity log to dictionary."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'user': self.user,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Setting(db.Model):
    """
    Settings model for application configuration.
    
    Stores key-value pairs for application settings that can be
    modified without code changes.
    
    Attributes:
        key: Setting key (primary key)
        value: Setting value
        description: Description of the setting
        updated_at: Last update timestamp
    """
    
    __tablename__ = 'settings'
    
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
    
    @staticmethod
    def get(key, default=None):
        """Get a setting value by key."""
        setting = Setting.query.get(key)
        return setting.value if setting else default
    
    @staticmethod
    def set(key, value, description=None):
        """Set a setting value."""
        setting = Setting.query.get(key)
        if setting:
            setting.value = value
            if description:
                setting.description = description
            setting.updated_at = datetime.utcnow()
        else:
            setting = Setting(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting


# ============================================================================
# Event Listeners for Auto-Generation
# ============================================================================

@event.listens_for(Client, 'before_insert')
def generate_client_code_before_insert(mapper, connection, target):
    """
    Auto-generate client code before inserting a new client.

    This event listener ensures that every client gets a unique code
    even when created programmatically without explicitly setting the code.
    """
    if not target.client_code:
        # Query for the last client code using the session
        from sqlalchemy import select, text

        # Use raw SQL to get the highest client code
        result = connection.execute(
            text("SELECT client_code FROM clients ORDER BY client_code DESC LIMIT 1")
        )
        row = result.fetchone()

        if row and row[0]:
            # Extract number from CL-xxxx format
            try:
                last_number = int(row[0].split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            # No clients yet, start from 1
            new_number = 1

        # Format as CL-xxxx with zero padding
        target.client_code = f'CL-{new_number:04d}'


@event.listens_for(Project, 'before_insert')
def generate_project_code_before_insert(mapper, connection, target):
    """
    Auto-generate project code before inserting a new project.

    Format: JB-yyyy-mm-CLxxxx-###
    Example: JB-2025-10-CL0001-001
    """
    if not target.project_code:
        from sqlalchemy import select, text
        from datetime import datetime

        # Get client code
        result = connection.execute(
            text("SELECT client_code FROM clients WHERE id = :client_id"),
            {'client_id': target.client_id}
        )
        row = result.fetchone()

        if not row:
            raise ValueError(f"Client with ID {target.client_id} not found")

        client_code = row[0]

        # Get current year and month
        now = datetime.utcnow()
        year = now.year
        month = f'{now.month:02d}'

        # Clean client code (remove hyphen for compact format)
        client_part = client_code.replace('-', '')

        # Build prefix
        prefix = f'JB-{year}-{month}-{client_part}'

        # Count existing projects with this prefix
        result = connection.execute(
            text("SELECT COUNT(*) FROM projects WHERE project_code LIKE :prefix"),
            {'prefix': f'{prefix}-%'}
        )
        count = result.fetchone()[0]

        # Generate new code
        new_number = count + 1
        target.project_code = f'{prefix}-{new_number:03d}'


class Product(db.Model):
    """Product/SKU model representing laser-cut products."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material = db.Column(db.String(100))
    thickness = db.Column(db.Numeric(10, 3))  # in mm
    unit_price = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project_products = db.relationship('ProjectProduct', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.sku_code}: {self.name}>'

    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'sku_code': self.sku_code,
            'name': self.name,
            'description': self.description,
            'material': self.material,
            'thickness': float(self.thickness) if self.thickness else None,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProjectProduct(db.Model):
    """Junction table for many-to-many relationship between projects and products."""

    __tablename__ = 'project_products'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2))  # Price at time of adding to project
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ProjectProduct project_id={self.project_id} product_id={self.product_id} qty={self.quantity}>'

    @property
    def total_price(self):
        """Calculate total price for this line item."""
        if self.unit_price and self.quantity:
            return float(self.unit_price) * self.quantity
        return 0.0

    def to_dict(self):
        """Convert project product to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_price': self.total_price,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Event listener for auto-generating SKU codes
@event.listens_for(Product, 'before_insert')
def generate_sku_code_before_insert(mapper, connection, target):
    """Auto-generate SKU code before inserting a new product."""
    if not target.sku_code:
        from sqlalchemy import text

        # Get material prefix (first 2 letters, uppercase)
        material_prefix = 'XX'  # Default
        if target.material:
            # Clean material name and get first 2 letters
            material_clean = target.material.replace(' ', '').replace('-', '')
            material_prefix = material_clean[:2].upper()

        # Get thickness part (convert to integer mm, e.g., 1.5mm -> 15)
        thickness_part = '00'  # Default
        if target.thickness:
            thickness_mm = int(float(target.thickness) * 10)  # 1.5 -> 15, 3.0 -> 30
            thickness_part = f'{thickness_mm:02d}'

        # Build prefix: SKU-{MATERIAL}{THICKNESS}-
        prefix = f'SKU-{material_prefix}{thickness_part}-'

        # Count existing products with this prefix
        result = connection.execute(
            text("SELECT COUNT(*) FROM products WHERE sku_code LIKE :prefix"),
            {'prefix': f'{prefix}%'}
        )
        count = result.fetchone()[0]

        # Generate new code
        new_number = count + 1
        target.sku_code = f'{prefix}{new_number:04d}'


class DesignFile(db.Model):
    """Design file model representing DXF files uploaded for projects."""

    __tablename__ = 'design_files'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_type = db.Column(db.String(50), default='dxf')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    uploaded_by = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<DesignFile {self.original_filename}>'

    @property
    def file_size_mb(self):
        """Return file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def file_extension(self):
        """Return file extension."""
        import os
        return os.path.splitext(self.original_filename)[1].lower()

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'file_type': self.file_type,
            'file_extension': self.file_extension,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'uploaded_by': self.uploaded_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class QueueItem(db.Model):
    """Queue item model representing jobs in the production queue."""

    __tablename__ = 'queue_items'

    # Status constants
    STATUS_QUEUED = 'Queued'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    # Priority constants
    PRIORITY_LOW = 'Low'
    PRIORITY_NORMAL = 'Normal'
    PRIORITY_HIGH = 'High'
    PRIORITY_URGENT = 'Urgent'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    queue_position = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default=STATUS_QUEUED, index=True)
    priority = db.Column(db.String(20), default=PRIORITY_NORMAL)
    scheduled_date = db.Column(db.Date, index=True)
    estimated_cut_time = db.Column(db.Integer)  # in minutes
    notes = db.Column(db.Text)
    added_by = db.Column(db.String(100))
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    laser_runs = db.relationship('LaserRun', backref='queue_item', lazy=True)

    def __repr__(self):
        return f'<QueueItem {self.id} - {self.project.project_code if self.project else "No Project"}>'

    @property
    def is_active(self):
        """Check if queue item is active (not completed or cancelled)."""
        return self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]

    @property
    def duration_in_queue(self):
        """Calculate how long the item has been in queue (in days)."""
        if self.completed_at:
            end_time = self.completed_at
        else:
            end_time = datetime.utcnow()

        delta = end_time - self.added_at
        return delta.days

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_code': self.project.project_code if self.project else None,
            'queue_position': self.queue_position,
            'status': self.status,
            'priority': self.priority,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'estimated_cut_time': self.estimated_cut_time,
            'notes': self.notes,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_active': self.is_active,
            'duration_in_queue': self.duration_in_queue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class LaserRun(db.Model):
    """Laser run model representing completed laser cutting runs."""

    __tablename__ = 'laser_runs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    queue_item_id = db.Column(db.Integer, db.ForeignKey('queue_items.id', ondelete='SET NULL'), index=True)
    run_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    operator = db.Column(db.String(100), index=True)
    cut_time_minutes = db.Column(db.Integer)
    material_type = db.Column(db.String(100))
    material_thickness = db.Column(db.Numeric(10, 3))
    sheet_count = db.Column(db.Integer, default=1)
    parts_produced = db.Column(db.Integer)
    machine_settings = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='Completed')

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<LaserRun {self.id} - {self.project.project_code if self.project else "No Project"}>'

    @property
    def cut_time_hours(self):
        """Return cut time in hours."""
        if self.cut_time_minutes:
            return round(self.cut_time_minutes / 60, 2)
        return 0

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_code': self.project.project_code if self.project else None,
            'queue_item_id': self.queue_item_id,
            'run_date': self.run_date.isoformat() if self.run_date else None,
            'operator': self.operator,
            'cut_time_minutes': self.cut_time_minutes,
            'cut_time_hours': self.cut_time_hours,
            'material_type': self.material_type,
            'material_thickness': float(self.material_thickness) if self.material_thickness else None,
            'sheet_count': self.sheet_count,
            'parts_produced': self.parts_produced,
            'machine_settings': self.machine_settings,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class InventoryItem(db.Model):
    """Inventory item model representing materials and consumables."""

    __tablename__ = 'inventory_items'

    # Category constants
    CATEGORY_SHEET_METAL = 'Sheet Metal'
    CATEGORY_GAS = 'Gas'
    CATEGORY_CONSUMABLES = 'Consumables'
    CATEGORY_TOOLS = 'Tools'
    CATEGORY_OTHER = 'Other'

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    material_type = db.Column(db.String(100), index=True)
    thickness = db.Column(db.Numeric(10, 3))
    unit = db.Column(db.String(20), nullable=False)
    quantity_on_hand = db.Column(db.Numeric(10, 3), nullable=False, default=0)
    reorder_level = db.Column(db.Numeric(10, 3), default=0)
    reorder_quantity = db.Column(db.Numeric(10, 3))
    unit_cost = db.Column(db.Numeric(10, 2))
    supplier_name = db.Column(db.String(255))
    supplier_contact = db.Column(db.String(255))
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    transactions = db.relationship('InventoryTransaction', backref='inventory_item', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<InventoryItem {self.item_code} - {self.name}>'

    @property
    def is_low_stock(self):
        """Check if item is below reorder level."""
        if self.reorder_level:
            return float(self.quantity_on_hand) <= float(self.reorder_level)
        return False

    @property
    def stock_value(self):
        """Calculate total stock value."""
        if self.unit_cost:
            return float(self.quantity_on_hand) * float(self.unit_cost)
        return 0

    def adjust_stock(self, quantity, transaction_type, performed_by=None, notes=None, reference_type=None, reference_id=None):
        """Adjust stock quantity and create transaction record."""
        self.quantity_on_hand = float(self.quantity_on_hand) + quantity

        transaction = InventoryTransaction(
            inventory_item_id=self.id,
            transaction_type=transaction_type,
            quantity=quantity,
            unit_cost=self.unit_cost,
            reference_type=reference_type,
            reference_id=reference_id,
            performed_by=performed_by,
            notes=notes
        )

        db.session.add(transaction)
        return transaction

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'item_code': self.item_code,
            'name': self.name,
            'category': self.category,
            'material_type': self.material_type,
            'thickness': float(self.thickness) if self.thickness else None,
            'unit': self.unit,
            'quantity_on_hand': float(self.quantity_on_hand),
            'reorder_level': float(self.reorder_level) if self.reorder_level else None,
            'reorder_quantity': float(self.reorder_quantity) if self.reorder_quantity else None,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'supplier_name': self.supplier_name,
            'supplier_contact': self.supplier_contact,
            'location': self.location,
            'notes': self.notes,
            'is_low_stock': self.is_low_stock,
            'stock_value': self.stock_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class InventoryTransaction(db.Model):
    """Inventory transaction model representing stock movements."""

    __tablename__ = 'inventory_transactions'

    # Transaction type constants
    TYPE_PURCHASE = 'Purchase'
    TYPE_USAGE = 'Usage'
    TYPE_ADJUSTMENT = 'Adjustment'
    TYPE_RETURN = 'Return'
    TYPE_WASTE = 'Waste'

    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False, index=True)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    performed_by = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<InventoryTransaction {self.id} - {self.transaction_type}>'

    @property
    def transaction_value(self):
        """Calculate transaction value."""
        if self.unit_cost:
            return abs(float(self.quantity)) * float(self.unit_cost)
        return 0

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'inventory_item_id': self.inventory_item_id,
            'item_code': self.inventory_item.item_code if self.inventory_item else None,
            'item_name': self.inventory_item.name if self.inventory_item else None,
            'transaction_type': self.transaction_type,
            'quantity': float(self.quantity),
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'transaction_value': self.transaction_value,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'performed_by': self.performed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Quote(db.Model):
    """Quote model representing customer quotes."""

    __tablename__ = 'quotes'

    # Status constants
    STATUS_DRAFT = 'Draft'
    STATUS_SENT = 'Sent'
    STATUS_ACCEPTED = 'Accepted'
    STATUS_REJECTED = 'Rejected'
    STATUS_EXPIRED = 'Expired'

    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    quote_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default=STATUS_DRAFT, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade='all, delete-orphan')

    def calculate_totals(self):
        """Calculate quote totals from line items."""
        self.subtotal = sum(float(item.line_total) for item in self.items)
        self.tax_amount = float(self.subtotal) * (float(self.tax_rate or 0) / 100)
        self.total_amount = float(self.subtotal) + float(self.tax_amount)

    def __repr__(self):
        return f'<Quote {self.quote_number}>'


class QuoteItem(db.Model):
    """Quote line item model."""

    __tablename__ = 'quote_items'

    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id', ondelete='CASCADE'), nullable=False, index=True)
    item_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<QuoteItem {self.id}: {self.description}>'


class Invoice(db.Model):
    """Invoice model representing customer invoices."""

    __tablename__ = 'invoices'

    # Status constants
    STATUS_DRAFT = 'Draft'
    STATUS_SENT = 'Sent'
    STATUS_PAID = 'Paid'
    STATUS_PARTIAL = 'Partially Paid'
    STATUS_OVERDUE = 'Overdue'
    STATUS_CANCELLED = 'Cancelled'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id', ondelete='SET NULL'))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default=STATUS_DRAFT, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    payment_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')

    @property
    def balance_due(self):
        """Calculate balance due."""
        return float(self.total_amount) - float(self.amount_paid or 0)

    def calculate_totals(self):
        """Calculate invoice totals from line items."""
        self.subtotal = sum(float(item.line_total) for item in self.items)
        self.tax_amount = float(self.subtotal) * (float(self.tax_rate or 0) / 100)
        self.total_amount = float(self.subtotal) + float(self.tax_amount)

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class InvoiceItem(db.Model):
    """Invoice line item model."""

    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False, index=True)
    item_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<InvoiceItem {self.id}: {self.description}>'


# ============================================================================
# Phase 9: New Models for Project Enhancements & Communications
# ============================================================================


class ProjectDocument(db.Model):
    """
    Project document model for quotes, invoices, POPs, and delivery notes.

    This model stores project-related documents separately from DXF design files.
    Supports future quote parsing capabilities for auto-extracting pricing data.

    Attributes:
        id: Primary key
        project_id: Foreign key to projects table
        document_type: Type of document (Quote, Invoice, Proof of Payment, Delivery Note)
        original_filename: Original uploaded filename
        stored_filename: Unique filename for storage
        file_path: Full path to stored file
        file_size: File size in bytes
        upload_date: When the document was uploaded
        uploaded_by: Username who uploaded the document
        is_parsed: Whether the document has been parsed (for quotes)
        parsed_data: JSON data extracted from document (future feature)
        notes: Additional notes about the document
        created_at: Creation timestamp
    """

    __tablename__ = 'project_documents'

    # Document type constants
    TYPE_QUOTE = 'Quote'
    TYPE_INVOICE = 'Invoice'
    TYPE_POP = 'Proof of Payment'
    TYPE_DELIVERY_NOTE = 'Delivery Note'

    VALID_TYPES = [TYPE_QUOTE, TYPE_INVOICE, TYPE_POP, TYPE_DELIVERY_NOTE]

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    document_type = db.Column(db.String(50), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    uploaded_by = db.Column(db.String(100))

    # Future: Quote parsing capabilities
    is_parsed = db.Column(db.Boolean, default=False)
    parsed_data = db.Column(db.Text)  # JSON format

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ProjectDocument {self.id}: {self.document_type} for Project {self.project_id}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_code': self.project.project_code if self.project else None,
            'document_type': self.document_type,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'uploaded_by': self.uploaded_by,
            'is_parsed': self.is_parsed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def file_size_formatted(self):
        """Format file size in human-readable format."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class Communication(db.Model):
    """
    Communication model for unified communication hub.

    Tracks all communications (Email, WhatsApp, Notifications) in one place.
    Supports auto-linking to clients and projects based on email/phone matching.
    Future: AI parsing to auto-detect client requests and project references.

    Attributes:
        id: Primary key
        comm_type: Type of communication (Email, WhatsApp, Notification)
        direction: Direction (Inbound, Outbound)
        client_id: Foreign key to clients table (nullable, can be linked later)
        project_id: Foreign key to projects table (nullable, can be linked later)
        subject: Email subject or message title
        body: Message body/content
        from_address: Sender email or phone number
        to_address: Recipient email or phone number
        status: Status (Pending, Sent, Delivered, Failed, Read)
        sent_at: When the message was sent
        received_at: When the message was received
        read_at: When the message was read
        has_attachments: Whether the communication has attachments
        is_linked: Whether successfully linked to client/project
        metadata: Additional data in JSON format (message IDs, thread IDs, etc.)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'communications'

    # Type constants
    TYPE_EMAIL = 'Email'
    TYPE_WHATSAPP = 'WhatsApp'
    TYPE_NOTIFICATION = 'Notification'

    VALID_TYPES = [TYPE_EMAIL, TYPE_WHATSAPP, TYPE_NOTIFICATION]

    # Direction constants
    DIRECTION_INBOUND = 'Inbound'
    DIRECTION_OUTBOUND = 'Outbound'

    VALID_DIRECTIONS = [DIRECTION_INBOUND, DIRECTION_OUTBOUND]

    # Status constants
    STATUS_PENDING = 'Pending'
    STATUS_SENT = 'Sent'
    STATUS_DELIVERED = 'Delivered'
    STATUS_FAILED = 'Failed'
    STATUS_READ = 'Read'

    VALID_STATUSES = [STATUS_PENDING, STATUS_SENT, STATUS_DELIVERED, STATUS_FAILED, STATUS_READ]

    id = db.Column(db.Integer, primary_key=True)
    comm_type = db.Column(db.String(20), nullable=False, index=True)
    direction = db.Column(db.String(10), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='SET NULL'), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'), index=True)
    subject = db.Column(db.String(500))
    body = db.Column(db.Text)
    from_address = db.Column(db.String(255))
    to_address = db.Column(db.String(255))
    status = db.Column(db.String(50), default=STATUS_PENDING, index=True)
    sent_at = db.Column(db.DateTime)
    received_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    has_attachments = db.Column(db.Boolean, default=False)
    is_linked = db.Column(db.Boolean, default=False, index=True)
    comm_metadata = db.Column(db.Text)  # JSON format - renamed from 'metadata' to avoid SQLAlchemy reserved word
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    attachments = db.relationship('CommunicationAttachment', backref='communication', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Communication {self.id}: {self.comm_type} - {self.subject}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'comm_type': self.comm_type,
            'direction': self.direction,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'project_id': self.project_id,
            'project_code': self.project.project_code if self.project else None,
            'subject': self.subject,
            'body': self.body,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'has_attachments': self.has_attachments,
            'is_linked': self.is_linked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def preview_text(self):
        """Get preview text (first 100 characters of body)."""
        if self.body:
            return self.body[:100] + '...' if len(self.body) > 100 else self.body
        return ''


class CommunicationAttachment(db.Model):
    """
    Communication attachment model for email attachments.

    Stores files attached to communications (emails, etc.).

    Attributes:
        id: Primary key
        communication_id: Foreign key to communications table
        original_filename: Original uploaded filename
        stored_filename: Unique filename for storage
        file_path: Full path to stored file
        file_size: File size in bytes
        file_type: MIME type or file extension
        created_at: Creation timestamp
    """

    __tablename__ = 'communication_attachments'

    id = db.Column(db.Integer, primary_key=True)
    communication_id = db.Column(db.Integer, db.ForeignKey('communications.id', ondelete='CASCADE'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<CommunicationAttachment {self.id}: {self.original_filename}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'communication_id': self.communication_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_formatted': self.file_size_formatted,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def file_size_formatted(self):
        """Format file size in human-readable format."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


# ============================================================================
# Event Listeners and Auto-generation Logic
# ============================================================================
# Note: Existing event listeners for Client and Project code generation
# are already defined earlier in this file and remain unchanged.
