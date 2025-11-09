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

    # Status constants - V12.0: Status System Redesign
    STATUS_REQUEST = 'Request'
    STATUS_QUOTE_APPROVAL = 'Quote & Approval'
    STATUS_APPROVED_POP = 'Approved (POP Received)'
    STATUS_QUEUED = 'Queued (Scheduled for Cutting)'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    # V12.0: Legacy statuses removed from VALID_STATUSES (migrated in database)
    # Legacy constants kept for backward compatibility in code
    STATUS_QUOTE = 'Quote'  # Migrated to STATUS_QUOTE_APPROVAL
    STATUS_APPROVED = 'Approved'  # Migrated to STATUS_APPROVED_POP

    VALID_STATUSES = [
        STATUS_REQUEST,
        STATUS_QUOTE_APPROVAL,
        STATUS_APPROVED_POP,
        STATUS_QUEUED,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED
    ]

    # Production Automation: Stage constants (parallel to status, for workflow management)
    STAGE_QUOTES_APPROVAL = 'QuotesAndApproval'
    STAGE_WAITING_MATERIAL = 'WaitingOnMaterial'
    STAGE_CUTTING = 'Cutting'
    STAGE_READY_PICKUP = 'ReadyForPickup'
    STAGE_DELIVERED = 'Delivered'

    VALID_STAGES = [
        STAGE_QUOTES_APPROVAL,
        STAGE_WAITING_MATERIAL,
        STAGE_CUTTING,
        STAGE_READY_PICKUP,
        STAGE_DELIVERED
    ]

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default=STATUS_QUOTE, index=True)

    # Production Automation: Stage tracking (workflow state with timing)
    stage = db.Column(db.String(50), nullable=False, default=STAGE_QUOTES_APPROVAL, index=True)
    stage_last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

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
    material_thickness = db.Column(db.Numeric(10, 3))  # in mm - Phase 10
    material_quantity_sheets = db.Column(db.Integer)
    parts_quantity = db.Column(db.Integer)
    estimated_cut_time = db.Column(db.Integer)  # in minutes
    number_of_bins = db.Column(db.Integer)
    drawing_creation_time = db.Column(db.Integer)  # in minutes

    # Production Automation: Material requirements (enhanced tracking)
    thickness_mm = db.Column(db.String(10), index=True)  # From THICKNESS_OPTIONS_MM constant
    sheet_size = db.Column(db.String(32))  # e.g., "3000x1500"
    sheets_required = db.Column(db.Integer, default=0)
    target_complete_date = db.Column(db.DateTime, nullable=True)

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

    # V12.0: Status System Redesign - New Fields
    # On Hold Management (independent flag - can be set on any status)
    on_hold = db.Column(db.Boolean, default=False, index=True)
    on_hold_reason = db.Column(db.Text)
    on_hold_date = db.Column(db.Date)

    # Quote Expiry Timer (30-day auto-cancel)
    quote_expiry_date = db.Column(db.Date, index=True)
    quote_reminder_sent = db.Column(db.Boolean, default=False)

    # Cancellation Management
    cancellation_reason = db.Column(db.Text)
    can_reinstate = db.Column(db.Boolean, default=False, index=True)

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
            # V12.0: Status system redesign fields
            'on_hold': self.on_hold,
            'on_hold_reason': self.on_hold_reason,
            'on_hold_date': self.on_hold_date.isoformat() if self.on_hold_date else None,
            'quote_expiry_date': self.quote_expiry_date.isoformat() if self.quote_expiry_date else None,
            'quote_reminder_sent': self.quote_reminder_sent,
            'cancellation_reason': self.cancellation_reason,
            'can_reinstate': self.can_reinstate,
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

    # V12.0: Status System Redesign - New Properties and Methods

    @property
    def is_ready_for_quote_approval(self):
        """
        Check if project can advance from Request to Quote & Approval.

        Required fields:
        - Project name
        - Client assigned
        - Material type
        - Material thickness
        - At least one DXF file uploaded

        Returns:
            bool: True if all required fields are filled
        """
        return all([
            self.name,
            self.client_id,
            self.material_type,
            self.material_thickness,
            len(self.design_files) > 0
        ])

    @property
    def is_quote_expired(self):
        """
        Check if quote has expired (past quote_expiry_date).

        Returns:
            bool: True if quote_expiry_date is in the past
        """
        if self.quote_expiry_date and not self.pop_received:
            from datetime import date
            return date.today() > self.quote_expiry_date
        return False

    @property
    def days_until_quote_expiry(self):
        """
        Calculate days until quote expires.

        Returns:
            int: Days remaining (positive) or days overdue (negative)
            None: No expiry date set or POP already received
        """
        if self.quote_expiry_date and not self.pop_received:
            from datetime import date
            delta = self.quote_expiry_date - date.today()
            return delta.days
        return None

    @property
    def quote_expiry_warning_level(self):
        """
        Get warning level for quote expiry.

        Returns:
            str: 'expired', 'critical' (<=5 days), 'warning' (<=10 days), 'normal', or None
        """
        days = self.days_until_quote_expiry
        if days is None:
            return None
        if days < 0:
            return 'expired'
        if days <= 5:
            return 'critical'
        if days <= 10:
            return 'warning'
        return 'normal'

    def calculate_quote_expiry_date(self, days=30):
        """
        Calculate and set quote expiry date (quote_date + days).

        Args:
            days (int): Number of days until expiry (default: 30)

        This method should be called when:
        - Status changes to Quote & Approval
        - Quote is reinstated
        """
        if self.quote_date:
            from datetime import timedelta
            self.quote_expiry_date = self.quote_date + timedelta(days=days)
        else:
            self.quote_expiry_date = None

    def set_on_hold(self, reason, performed_by='admin'):
        """
        Put project on hold with reason.

        Args:
            reason (str): Reason for putting project on hold
            performed_by (str): User who performed the action
        """
        from datetime import date
        self.on_hold = True
        self.on_hold_reason = reason
        self.on_hold_date = date.today()

        # Log activity
        from app.services.activity_logger import log_activity
        log_activity('PROJECT', self.id, 'PUT_ON_HOLD', {
            'reason': reason,
            'on_hold_date': self.on_hold_date.isoformat()
        }, performed_by)

    def resume_from_hold(self, performed_by='admin'):
        """
        Resume project from on-hold status.

        Args:
            performed_by (str): User who performed the action
        """
        self.on_hold = False
        old_reason = self.on_hold_reason
        self.on_hold_reason = None
        self.on_hold_date = None

        # Log activity
        from app.services.activity_logger import log_activity
        log_activity('PROJECT', self.id, 'RESUMED_FROM_HOLD', {
            'previous_reason': old_reason
        }, performed_by)

    def cancel_with_reason(self, reason, performed_by='admin'):
        """
        Cancel project with reason and mark as can_reinstate.

        Args:
            reason (str): Reason for cancellation
            performed_by (str): User who performed the action
        """
        self.status = self.STATUS_CANCELLED
        self.cancellation_reason = reason
        self.can_reinstate = True

        # Log activity
        from app.services.activity_logger import log_activity
        log_activity('PROJECT', self.id, 'CANCELLED', {
            'reason': reason,
            'can_reinstate': True
        }, performed_by)

    def reinstate(self, performed_by='admin'):
        """
        Reinstate a cancelled project back to Quote & Approval with new 30-day period.

        Args:
            performed_by (str): User who performed the action

        Returns:
            bool: True if reinstated successfully, False if cannot reinstate
        """
        if self.status != self.STATUS_CANCELLED or not self.can_reinstate:
            return False

        from datetime import date, timedelta

        # Reinstate to Quote & Approval
        self.status = self.STATUS_QUOTE_APPROVAL
        self.quote_date = date.today()
        self.quote_expiry_date = date.today() + timedelta(days=30)
        self.quote_reminder_sent = False
        self.can_reinstate = False
        old_reason = self.cancellation_reason
        self.cancellation_reason = None

        # Log activity
        from app.services.activity_logger import log_activity
        log_activity('PROJECT', self.id, 'REINSTATED', {
            'previous_cancellation_reason': old_reason,
            'new_quote_date': self.quote_date.isoformat(),
            'new_expiry_date': self.quote_expiry_date.isoformat()
        }, performed_by)

        return True


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
    product_files = db.relationship('ProductFile', backref='product', lazy=True, cascade='all, delete-orphan')

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


class ProductFile(db.Model):
    """Product file model representing DXF and LightBurn files uploaded for products."""

    __tablename__ = 'product_files'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_type = db.Column(db.String(50), default='dxf')  # 'dxf' or 'lbrn2'
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    uploaded_by = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ProductFile {self.original_filename}>'

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
            'product_id': self.product_id,
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
    operator = db.Column(db.String(100), index=True)  # Legacy field - kept for backward compatibility
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id', ondelete='SET NULL'), index=True)
    preset_id = db.Column(db.Integer, db.ForeignKey('machine_settings_presets.id', ondelete='SET NULL'), index=True)
    cut_time_minutes = db.Column(db.Integer)
    material_type = db.Column(db.String(100))
    material_thickness = db.Column(db.Numeric(10, 3))
    sheet_count = db.Column(db.Integer, default=1)
    parts_produced = db.Column(db.Integer)
    machine_settings = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='Completed')

    # Production Automation: Enhanced run tracking
    started_at = db.Column(db.DateTime, nullable=True, index=True)  # When run started (Phone Mode)
    ended_at = db.Column(db.DateTime, nullable=True)  # When run ended (Phone Mode)
    sheets_used = db.Column(db.Integer, default=0)  # Actual sheets consumed (for inventory deduction)
    sheet_size = db.Column(db.String(32))  # e.g., "3000x1500"
    thickness_mm = db.Column(db.String(10))  # From THICKNESS_OPTIONS_MM constant

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    operator_obj = db.relationship('Operator', back_populates='laser_runs')
    preset = db.relationship('MachineSettingsPreset', back_populates='laser_runs')

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
            'operator': self.operator,  # Legacy field
            'operator_id': self.operator_id,
            'operator_name': self.operator_obj.name if self.operator_obj else None,
            'preset_id': self.preset_id,
            'preset_name': self.preset.preset_name if self.preset else None,
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

    @property
    def operator_display(self):
        """Return operator name from relationship or legacy field."""
        if self.operator_obj:
            return self.operator_obj.name
        return self.operator if self.operator else "Unknown"

    @property
    def preset_display(self):
        """Return preset name if available."""
        if self.preset:
            return self.preset.preset_name
        return None


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

    # Production Automation: Enhanced sheet tracking
    sheet_size = db.Column(db.String(32), index=True)  # e.g., "3000x1500"
    thickness_mm = db.Column(db.String(10), index=True)  # From THICKNESS_OPTIONS_MM constant

    # Blueprint terminology aliases (properties for backward compatibility)
    @property
    def count(self):
        """Alias for quantity_on_hand (blueprint terminology)."""
        return int(self.quantity_on_hand) if self.quantity_on_hand else 0

    @count.setter
    def count(self, value):
        """Setter for count alias."""
        self.quantity_on_hand = value

    @property
    def min_required(self):
        """Alias for reorder_level (blueprint terminology)."""
        return int(self.reorder_level) if self.reorder_level else 0

    @min_required.setter
    def min_required(self, value):
        """Setter for min_required alias."""
        self.reorder_level = value

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
    TYPE_OTHER = 'Other'
    TYPE_IMAGE = 'Image'

    VALID_TYPES = [TYPE_QUOTE, TYPE_INVOICE, TYPE_POP, TYPE_DELIVERY_NOTE, TYPE_OTHER, TYPE_IMAGE]

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


class Operator(db.Model):
    """
    Operator model representing machine operators.

    Attributes:
        id: Primary key
        name: Operator name (unique)
        email: Contact email (optional)
        phone: Contact phone (optional)
        user_id: Link to User account (Phase 10)
        is_active: Active status (default True)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'operators'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    # Phase 10: Link to User account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    laser_runs = db.relationship('LaserRun', back_populates='operator_obj', lazy='dynamic')
    user = db.relationship('User', backref='operator_profile', foreign_keys=[user_id])

    def __repr__(self):
        return f'<Operator {self.id}: {self.name}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'user_id': self.user_id,
            'user_username': self.user.username if self.user else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def status_text(self):
        """Return human-readable status."""
        return "Active" if self.is_active else "Inactive"

    @property
    def laser_run_count(self):
        """Return count of laser runs by this operator."""
        return self.laser_runs.count()


class MachineSettingsPreset(db.Model):
    """
    Machine Settings Preset model representing predefined laser cutting parameters.

    Attributes:
        id: Primary key
        preset_name: Unique preset name
        material_type: Material type (e.g., "Mild Steel", "Stainless Steel")
        thickness: Material thickness in mm
        description: Optional description

        Cutting Parameters:
        nozzle: Nozzle type/size
        cut_speed: Cutting speed in mm/min
        nozzle_height: Nozzle height in mm

        Gas Settings:
        gas_type: Gas type (e.g., "Oxygen", "Nitrogen", "Air")
        gas_pressure: Gas pressure in bar

        Power Settings:
        peak_power: Peak power in watts
        actual_power: Actual power in watts
        duty_cycle: Duty cycle percentage
        pulse_frequency: Pulse frequency in Hz

        Beam Settings:
        beam_width: Beam width in mm
        focus_position: Focus position in mm

        Timing Settings:
        laser_on_delay: Laser on delay in seconds
        laser_off_delay: Laser off delay in seconds

        Additional Settings:
        pierce_time: Pierce time in seconds
        pierce_power: Pierce power in watts
        corner_power: Corner power in watts

        Metadata:
        is_active: Active status
        notes: Additional notes
        created_by: Creator name
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'machine_settings_presets'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Identification
    preset_name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    material_type = db.Column(db.String(100), nullable=False, index=True)
    thickness = db.Column(db.Numeric(10, 3), nullable=False, index=True)
    description = db.Column(db.Text)

    # Cutting Parameters
    nozzle = db.Column(db.String(50))
    cut_speed = db.Column(db.Numeric(10, 2))
    nozzle_height = db.Column(db.Numeric(10, 3))

    # Gas Settings
    gas_type = db.Column(db.String(50))
    gas_pressure = db.Column(db.Numeric(10, 2))

    # Power Settings
    peak_power = db.Column(db.Numeric(10, 2))
    actual_power = db.Column(db.Numeric(10, 2))
    duty_cycle = db.Column(db.Numeric(5, 2))
    pulse_frequency = db.Column(db.Numeric(10, 2))

    # Beam Settings
    beam_width = db.Column(db.Numeric(10, 3))
    focus_position = db.Column(db.Numeric(10, 3))

    # Timing Settings
    laser_on_delay = db.Column(db.Numeric(10, 3))
    laser_off_delay = db.Column(db.Numeric(10, 3))

    # Additional Settings
    pierce_time = db.Column(db.Numeric(10, 3))
    pierce_power = db.Column(db.Numeric(10, 2))
    corner_power = db.Column(db.Numeric(10, 2))

    # Metadata
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    laser_runs = db.relationship('LaserRun', back_populates='preset', lazy='dynamic')

    def __repr__(self):
        return f'<MachineSettingsPreset {self.id}: {self.preset_name}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'preset_name': self.preset_name,
            'material_type': self.material_type,
            'thickness': float(self.thickness) if self.thickness else None,
            'description': self.description,
            # Cutting Parameters
            'nozzle': self.nozzle,
            'cut_speed': float(self.cut_speed) if self.cut_speed else None,
            'nozzle_height': float(self.nozzle_height) if self.nozzle_height else None,
            # Gas Settings
            'gas_type': self.gas_type,
            'gas_pressure': float(self.gas_pressure) if self.gas_pressure else None,
            # Power Settings
            'peak_power': float(self.peak_power) if self.peak_power else None,
            'actual_power': float(self.actual_power) if self.actual_power else None,
            'duty_cycle': float(self.duty_cycle) if self.duty_cycle else None,
            'pulse_frequency': float(self.pulse_frequency) if self.pulse_frequency else None,
            # Beam Settings
            'beam_width': float(self.beam_width) if self.beam_width else None,
            'focus_position': float(self.focus_position) if self.focus_position else None,
            # Timing Settings
            'laser_on_delay': float(self.laser_on_delay) if self.laser_on_delay else None,
            'laser_off_delay': float(self.laser_off_delay) if self.laser_off_delay else None,
            # Additional Settings
            'pierce_time': float(self.pierce_time) if self.pierce_time else None,
            'pierce_power': float(self.pierce_power) if self.pierce_power else None,
            'corner_power': float(self.corner_power) if self.corner_power else None,
            # Metadata
            'is_active': self.is_active,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def status_text(self):
        """Return human-readable status."""
        return "Active" if self.is_active else "Inactive"

    @property
    def material_description(self):
        """Return formatted material description."""
        return f"{self.material_type} {self.thickness}mm"

    @property
    def laser_run_count(self):
        """Return count of laser runs using this preset."""
        return self.laser_runs.count()

    def get_settings_dict(self):
        """
        Get all machine settings as a dictionary (excluding metadata).
        Useful for populating forms or comparing settings.
        """
        return {
            'nozzle': self.nozzle,
            'cut_speed': float(self.cut_speed) if self.cut_speed else None,
            'nozzle_height': float(self.nozzle_height) if self.nozzle_height else None,
            'gas_type': self.gas_type,
            'gas_pressure': float(self.gas_pressure) if self.gas_pressure else None,
            'peak_power': float(self.peak_power) if self.peak_power else None,
            'actual_power': float(self.actual_power) if self.actual_power else None,
            'duty_cycle': float(self.duty_cycle) if self.duty_cycle else None,
            'pulse_frequency': float(self.pulse_frequency) if self.pulse_frequency else None,
            'beam_width': float(self.beam_width) if self.beam_width else None,
            'focus_position': float(self.focus_position) if self.focus_position else None,
            'laser_on_delay': float(self.laser_on_delay) if self.laser_on_delay else None,
            'laser_off_delay': float(self.laser_off_delay) if self.laser_off_delay else None,
            'pierce_time': float(self.pierce_time) if self.pierce_time else None,
            'pierce_power': float(self.pierce_power) if self.pierce_power else None,
            'corner_power': float(self.corner_power) if self.corner_power else None,
        }


class MessageTemplate(db.Model):
    """
    Message Template model for reusable communication templates.

    Supports placeholders for dynamic content like {{client_name}}, {{project_code}}, etc.
    Used for automated and manual email sending.

    Attributes:
        id: Primary key
        name: Template name (e.g., "Collection Ready", "Quote Sent")
        template_type: Type/category (e.g., "project_complete", "quote_sent", "order_confirmed")
        subject_template: Email subject with placeholders
        body_template: Email body with placeholders
        description: Template description/purpose
        is_active: Whether template is active and available for use
        created_by_id: User who created the template
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Placeholders:
        {{client_name}} - Client name
        {{client_code}} - Client code
        {{client_email}} - Client email
        {{client_phone}} - Client phone
        {{project_code}} - Project code
        {{project_name}} - Project name
        {{project_status}} - Project status
        {{collection_date}} - Calculated collection date
        {{quote_total}} - Quote total amount
        {{invoice_total}} - Invoice total amount
        {{company_name}} - Company name from config
        {{current_date}} - Current date
        {{current_time}} - Current time
    """

    __tablename__ = 'message_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    template_type = db.Column(db.String(50), nullable=False, index=True)
    subject_template = db.Column(db.String(500), nullable=False)
    body_template = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    created_by = db.relationship('User', backref='message_templates', foreign_keys=[created_by_id])

    # Template type constants
    TYPE_PROJECT_COMPLETE = 'project_complete'
    TYPE_ORDER_CONFIRMED = 'order_confirmed'
    TYPE_QUOTE_SENT = 'quote_sent'
    TYPE_INVOICE_SENT = 'invoice_sent'
    TYPE_PAYMENT_REMINDER = 'payment_reminder'
    TYPE_DELIVERY_NOTIFICATION = 'delivery_notification'
    TYPE_CUSTOM = 'custom'

    def __repr__(self):
        return f'<MessageTemplate {self.name}>'

    def to_dict(self):
        """Convert template to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'subject_template': self.subject_template,
            'body_template': self.body_template,
            'description': self.description,
            'is_active': self.is_active,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.username if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================================================
# Production Automation Models
# ============================================================================


class Notification(db.Model):
    """
    Notification model for bell icon alerts.

    Tracks alerts for:
    - Overdue project stages (approval_wait, material_block, cutting_stall, pickup_wait)
    - Low inventory stock (low_stock)
    - Missing presets (preset_missing)

    Notifications auto-clear when conditions resolve.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys (nullable - notification may relate to project OR inventory)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=True, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=True, index=True)

    # Notification details
    notif_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: approval_wait, material_block, cutting_stall, pickup_wait, low_stock, preset_missing

    message = db.Column(db.String(500), nullable=False)

    # Status
    resolved = db.Column(db.Boolean, nullable=False, default=False, index=True)
    auto_cleared = db.Column(db.Boolean, nullable=False, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship('Project', backref='notifications')
    inventory_item = db.relationship('InventoryItem', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.id}: {self.notif_type} - {self.message[:50]}>'

    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_code': self.project.project_code if self.project else None,
            'inventory_item_id': self.inventory_item_id,
            'inventory_item_name': self.inventory_item.name if self.inventory_item else None,
            'notif_type': self.notif_type,
            'message': self.message,
            'resolved': self.resolved,
            'auto_cleared': self.auto_cleared,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }


class DailyReport(db.Model):
    """
    Daily Report model for automated 07:30 SAST reports.

    Stores generated daily reports containing:
    - Projects ready to cut
    - Low stock items
    - Blocked projects (waiting on material)
    - Active notifications requiring attention
    """
    __tablename__ = 'daily_reports'

    id = db.Column(db.Integer, primary_key=True)

    # Report metadata
    report_date = db.Column(db.Date, nullable=False, index=True)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Report statistics
    runs_count = db.Column(db.Integer, nullable=False, default=0)
    total_sheets_used = db.Column(db.Integer, nullable=False, default=0)
    total_parts_produced = db.Column(db.Integer, nullable=False, default=0)
    total_cut_time_minutes = db.Column(db.Float, nullable=False, default=0.0)

    # Report content (plain text format)
    report_body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<DailyReport {self.id} - {self.report_date.strftime("%Y-%m-%d")}>'

    def to_dict(self):
        """Convert daily report to dictionary."""
        return {
            'id': self.id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'runs_count': self.runs_count,
            'total_sheets_used': self.total_sheets_used,
            'total_parts_produced': self.total_parts_produced,
            'total_cut_time_minutes': self.total_cut_time_minutes,
            'report_body': self.report_body,
        }


class OutboundDraft(db.Model):
    """
    Outbound Draft model for auto-generated client messages.

    Created automatically when:
    - Project stage exceeds time limit (e.g., QuotesAndApproval > 4 days)
    - System needs to suggest client follow-up

    Drafts appear in Communications module for review/editing before sending.
    """
    __tablename__ = 'outbound_drafts'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)

    # Message details
    channel_hint = db.Column(db.String(20), nullable=False, default='whatsapp')
    # Suggested channel: whatsapp, email, sms

    body_text = db.Column(db.Text, nullable=False)

    # Status
    sent = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    sent_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship('Project', backref='outbound_drafts')
    client = db.relationship('Client', backref='outbound_drafts')

    def __repr__(self):
        return f'<OutboundDraft {self.id} - Project {self.project.project_code if self.project else "N/A"}>'

    def to_dict(self):
        """Convert outbound draft to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_code': self.project.project_code if self.project else None,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'channel_hint': self.channel_hint,
            'body_text': self.body_text,
            'sent': self.sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
        }


class ExtraOperator(db.Model):
    """
    Extra Operator model for non-login operators.

    Allows tracking operators who don't have User accounts but need to be
    recorded for laser runs (e.g., temporary workers, contractors).

    Optional feature - can be used alongside User-based operators.
    """
    __tablename__ = 'extra_operators'

    id = db.Column(db.Integer, primary_key=True)

    # Operator details
    name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExtraOperator {self.id}: {self.name}>'

    def to_dict(self):
        """Convert extra operator to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# Event Listeners and Auto-generation Logic
# ============================================================================
# Note: Existing event listeners for Client and Project code generation
# are already defined earlier in this file and remain unchanged.
