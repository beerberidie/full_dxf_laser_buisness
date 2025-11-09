"""
Laser OS Tier 1 - Database Models Package

This package contains all SQLAlchemy models organized by domain:
- auth: Authentication and authorization models (User, Role, etc.)
- business: Business models (Client, Project, Product, etc.)
- sage: Sage Business Cloud Accounting integration models

This __init__.py allows importing models from both:
- from app.models import Client  (backward compatible)
- from app.models.business import Client  (new structure)
"""

# Import authentication models
from app.models.auth import User, Role, UserRole, LoginHistory

# Import business models
from app.models.business import (
    Client, Project, Product, ProductFile, DesignFile,
    ProjectDocument, QueueItem, LaserRun, InventoryItem,
    InventoryTransaction, Quote, QuoteItem, Invoice,
    InvoiceItem, Communication, CommunicationAttachment,
    Operator, MachineSettingsPreset, ActivityLog, Setting,
    ProjectProduct, MessageTemplate,
    # Production Automation models
    Notification, DailyReport, OutboundDraft, ExtraOperator
)

# Import Sage integration models
from app.models.sage import (
    SageConnection, SageBusiness, SageSyncCursor, SageAuditLog
)

# Export all models for backward compatibility
__all__ = [
    # Authentication models
    'User',
    'Role',
    'UserRole',
    'LoginHistory',

    # Business models
    'Client',
    'Project',
    'Product',
    'ProductFile',
    'ProjectProduct',
    'DesignFile',
    'ProjectDocument',
    'QueueItem',
    'LaserRun',
    'InventoryItem',
    'InventoryTransaction',
    'Quote',
    'QuoteItem',
    'Invoice',
    'InvoiceItem',
    'Communication',
    'CommunicationAttachment',
    'MessageTemplate',
    'Operator',
    'MachineSettingsPreset',
    'ActivityLog',
    'Setting',

    # Production Automation models
    'Notification',
    'DailyReport',
    'OutboundDraft',
    'ExtraOperator',

    # Sage integration models
    'SageConnection',
    'SageBusiness',
    'SageSyncCursor',
    'SageAuditLog',
]

