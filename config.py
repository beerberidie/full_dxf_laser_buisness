"""
Laser OS Tier 1 - Configuration

This module defines configuration classes for different environments.
"""

import os
from pathlib import Path

# Base directory
basedir = Path(__file__).parent.absolute()


class Config:
    """Base configuration class with common settings."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    # Store the database path
    DATABASE_PATH = str(basedir / 'data' / 'laser_os.db')

    # For Windows absolute paths, SQLite URIs need special handling:
    # - On Windows: sqlite:////C:/path/to/db.db (4 slashes + forward slashes)
    # - On Unix: sqlite:////absolute/path/to/db.db (4 slashes)
    # Convert backslashes to forward slashes and use 4 slashes for absolute paths
    _db_path_normalized = DATABASE_PATH.replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{_db_path_normalized}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(basedir / 'data' / 'files')
    DOCUMENTS_FOLDER = os.environ.get('DOCUMENTS_FOLDER') or str(basedir / 'data' / 'documents')  # Phase 9: Project documents
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 52428800))  # 50MB default
    ALLOWED_EXTENSIONS = {'dxf', 'lbrn2', 'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}  # Phase 10: Added lbrn2
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xlsx', 'xls'}  # Phase 9: Document types
    
    # Company Settings
    COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Laser OS')
    TIMEZONE = os.environ.get('TIMEZONE', 'Africa/Johannesburg')
    OPERATING_HOURS = os.environ.get('OPERATING_HOURS', 'Mon-Thu 07:00-16:00, Fri 07:00-14:30')
    
    # Business Rules
    DEFAULT_SLA_DAYS = int(os.environ.get('DEFAULT_SLA_DAYS', 3))
    LOW_STOCK_THRESHOLD = int(os.environ.get('LOW_STOCK_THRESHOLD', 3))
    POP_DEADLINE_DAYS = int(os.environ.get('POP_DEADLINE_DAYS', 3))  # Phase 9: Days after POP to schedule cutting

    # Phase 9: Scheduling Configuration
    MAX_HOURS_PER_DAY = int(os.environ.get('MAX_HOURS_PER_DAY', 8))  # Maximum working hours per day for capacity planning

    # Module N: File Ingest & Extract System
    MODULE_N_ENABLED = os.environ.get('MODULE_N_ENABLED', 'false').lower() == 'true'
    MODULE_N_URL = os.environ.get('MODULE_N_URL', 'http://localhost:8081')
    MODULE_N_TIMEOUT = int(os.environ.get('MODULE_N_TIMEOUT', 30))
    MODULE_N_AUTO_PROCESS = os.environ.get('MODULE_N_AUTO_PROCESS', 'true').lower() == 'true'
    UPCOMING_DEADLINE_DAYS = int(os.environ.get('UPCOMING_DEADLINE_DAYS', 3))  # Days ahead to check for upcoming deadlines

    # Phase 9: Material Types (configurable list)
    # Phase 10: Added Carbon Steel and Zinc
    MATERIAL_TYPES = [
        'Aluminum',
        'Brass',
        'Carbon Steel',
        'Copper',
        'Galvanized Steel',
        'Mild Steel',
        'Stainless Steel',
        'Vastrap',
        'Zinc',
        'Other'
    ]

    # Phase 9: Document Types (configurable list)
    DOCUMENT_TYPES = [
        'Quote',
        'Invoice',
        'Proof of Payment',
        'Delivery Note',
        'Other',
        'Image'
    ]

    # Phase 9: Communication Types (configurable list)
    COMMUNICATION_TYPES = [
        'Email',
        'Phone',
        'WhatsApp',
        'SMS',
        'In-Person',
        'Notification'
    ]

    # DXF Filename Pattern
    DXF_FILENAME_PATTERN = r'^[A-Z0-9]{2,8}-[a-zA-Z0-9_-]+-[A-Z]{2,4}-[0-9.]+(?:mm)?-[0-9]+\.dxf$'

    # Phase 9: Email Configuration (for Communications module)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')

    # Sage Business Cloud Accounting Integration
    SAGE_CLIENT_ID = os.environ.get('SAGE_CLIENT_ID')
    SAGE_CLIENT_SECRET = os.environ.get('SAGE_CLIENT_SECRET')
    SAGE_REDIRECT_URI = os.environ.get('SAGE_REDIRECT_URI', 'http://127.0.0.1:5000/sage/oauth/callback')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@laseros.local')
    MAIL_MAX_EMAILS = int(os.environ.get('MAIL_MAX_EMAILS', 50))  # Max emails per connection

    # Phase 9: Pagination Configuration
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))  # Default items per page for lists
    COMMUNICATIONS_PER_PAGE = int(os.environ.get('COMMUNICATIONS_PER_PAGE', 25))  # Communications list pagination

    # V12.0: Status System Redesign Configuration
    AUTO_ADVANCE_TO_QUOTE = os.environ.get('AUTO_ADVANCE_TO_QUOTE', 'True').lower() in ('true', '1', 'yes')
    QUOTE_EXPIRY_DAYS = int(os.environ.get('QUOTE_EXPIRY_DAYS', 30))  # Days until quote expires
    QUOTE_REMINDER_DAYS = int(os.environ.get('QUOTE_REMINDER_DAYS', 25))  # Send reminder at this many days
    AUTO_CANCEL_EXPIRED_QUOTES = os.environ.get('AUTO_CANCEL_EXPIRED_QUOTES', 'True').lower() in ('true', '1', 'yes')
    AUTO_QUEUE_ON_POP = os.environ.get('AUTO_QUEUE_ON_POP', 'True').lower() in ('true', '1', 'yes')

    # V12.0: Notification Configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@laseros.com')
    SCHEDULER_EMAIL = os.environ.get('SCHEDULER_EMAIL', 'scheduler@laseros.com')
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() in ('true', '1', 'yes')
    ENABLE_SMS_NOTIFICATIONS = os.environ.get('ENABLE_SMS_NOTIFICATIONS', 'False').lower() in ('true', '1', 'yes')
    ENABLE_WHATSAPP_NOTIFICATIONS = os.environ.get('ENABLE_WHATSAPP_NOTIFICATIONS', 'False').lower() in ('true', '1', 'yes')

    # V12.0: Background Scheduler Configuration
    ENABLE_BACKGROUND_SCHEDULER = os.environ.get('ENABLE_BACKGROUND_SCHEDULER', 'True').lower() in ('true', '1', 'yes')
    QUOTE_EXPIRY_CHECK_HOUR = int(os.environ.get('QUOTE_EXPIRY_CHECK_HOUR', 9))  # Check at 9 AM daily
    QUOTE_REMINDER_CHECK_HOUR = int(os.environ.get('QUOTE_REMINDER_CHECK_HOUR', 10))  # Send reminders at 10 AM daily

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/laser_os.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10485760))  # 10MB default
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 10))  # Keep 10 backups

    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        # Create necessary directories
        os.makedirs(Path(app.config['DATABASE_PATH']).parent, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(Path(app.config['UPLOAD_FOLDER']) / 'clients', exist_ok=True)
        os.makedirs(Path(app.config['UPLOAD_FOLDER']) / 'reports', exist_ok=True)

        # Create logs directory
        os.makedirs('logs', exist_ok=True)

        # Phase 9: Create documents directory structure
        os.makedirs(app.config['DOCUMENTS_FOLDER'], exist_ok=True)
        os.makedirs(Path(app.config['DOCUMENTS_FOLDER']) / 'quotes', exist_ok=True)
        os.makedirs(Path(app.config['DOCUMENTS_FOLDER']) / 'invoices', exist_ok=True)
        os.makedirs(Path(app.config['DOCUMENTS_FOLDER']) / 'pops', exist_ok=True)
        os.makedirs(Path(app.config['DOCUMENTS_FOLDER']) / 'delivery_notes', exist_ok=True)

        # Log configuration status (development only)
        if app.config.get('DEBUG'):
            Config._log_config_status(app)

    @staticmethod
    def _log_config_status(app):
        """Log configuration status for debugging (development only)."""
        print("\n" + "="*70)
        print("LASER OS - CONFIGURATION STATUS")
        print("="*70)

        # Environment
        print(f"\n📋 Environment: {app.config.get('ENV', 'unknown')}")
        print(f"🐛 Debug Mode: {app.config.get('DEBUG', False)}")

        # Database
        print(f"\n💾 Database: {app.config.get('DATABASE_PATH', 'not set')}")

        # File Storage
        print(f"\n📁 Upload Folder: {app.config.get('UPLOAD_FOLDER', 'not set')}")
        print(f"📄 Documents Folder: {app.config.get('DOCUMENTS_FOLDER', 'not set')}")
        print(f"📦 Max Upload Size: {app.config.get('MAX_UPLOAD_SIZE', 0) / 1024 / 1024:.1f} MB")

        # Email Configuration
        mail_configured = bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
        print(f"\n📧 Email Configured: {'✓ Yes' if mail_configured else '✗ No (using defaults)'}")
        if mail_configured:
            print(f"   Server: {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}")
            print(f"   Username: {app.config.get('MAIL_USERNAME')}")

        # Business Rules
        print(f"\n⚙️  Business Rules:")
        print(f"   POP Deadline: {app.config.get('POP_DEADLINE_DAYS', 3)} days")
        print(f"   Max Hours/Day: {app.config.get('MAX_HOURS_PER_DAY', 8)} hours")
        print(f"   Default SLA: {app.config.get('DEFAULT_SLA_DAYS', 3)} days")

        # Material Types
        material_count = len(app.config.get('MATERIAL_TYPES', []))
        print(f"\n🔧 Material Types: {material_count} configured")

        print("="*70 + "\n")

    @staticmethod
    def validate_production_config(app):
        """
        Validate production configuration.
        Raises ValueError if critical settings are missing or invalid.
        """
        errors = []

        # Check SECRET_KEY
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            errors.append('SECRET_KEY must be changed in production')

        # Check email configuration
        if not app.config.get('MAIL_USERNAME'):
            errors.append('MAIL_USERNAME is not set (email functionality will not work)')

        if not app.config.get('MAIL_PASSWORD'):
            errors.append('MAIL_PASSWORD is not set (email functionality will not work)')

        # Check file paths exist
        if not os.path.exists(app.config.get('UPLOAD_FOLDER', '')):
            errors.append(f"Upload folder does not exist: {app.config.get('UPLOAD_FOLDER')}")

        if not os.path.exists(app.config.get('DOCUMENTS_FOLDER', '')):
            errors.append(f"Documents folder does not exist: {app.config.get('DOCUMENTS_FOLDER')}")

        # Return validation results
        if errors:
            error_msg = "Production configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)

        return True


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Production-specific settings
    # Disable detailed error pages in production
    PROPAGATE_EXCEPTIONS = False

    @staticmethod
    def init_app(app):
        """Initialize production app with validation."""
        Config.init_app(app)

        # Validate production configuration
        try:
            Config.validate_production_config(app)
            print("✓ Production configuration validated successfully")
        except ValueError as e:
            print(f"\n{'='*70}")
            print("⚠️  PRODUCTION CONFIGURATION ERROR")
            print(f"{'='*70}")
            print(str(e))
            print(f"{'='*70}\n")
            raise


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

