# Laser OS - Tier 1 MVP

**Laser Cutting Business Automation System**

A comprehensive web-based system for managing laser cutting operations, from client intake to job completion.

## Overview

Laser OS is a Flask-based web application designed to streamline laser cutting business operations. It provides complete workflow management from client onboarding through project execution, with features for quoting, scheduling, inventory tracking, and reporting.

### Target Operation
- **Machine**: Golden Laser X3 with CypCut software
- **Location**: South Africa (KwaZulu-Natal)
- **Business Model**: B2B recurring contracts with standardized SKU-based products

## Features

### Phase 1: Client Management ✅ (COMPLETE)
- Client CRUD operations with auto-generated CL-xxxx codes
- Contact information management
- Activity logging and audit trail
- Search and pagination

### Phase 2: Project/Job Management (NEXT)
- Project creation with JB-yyyy-mm-client-### codes
- Status workflow management
- Due date tracking with SLA
- Client-project relationships

### Phase 3: File Management & DXF Handling
- DXF file upload and parsing
- File metadata extraction
- Organized file storage by client/project
- File validation

### Phase 4: Quotes, Approvals & Invoices
- Quote generation and tracking
- Approval workflow (drawing + quote + payment)
- Invoice creation
- PDF generation

### Phase 5: Schedule Queue & Laser Runs
- Job queue management
- Drag-and-drop scheduling
- Laser run logging
- Cut time and material tracking

### Phase 6: Inventory & Material Tracking
- Material inventory management
- Stock level tracking
- Low stock alerts
- Inventory event logging

### Phase 7: Reporting & Dashboard
- Enhanced dashboard with analytics
- Custom reports
- Parameter integration
- Business intelligence

## Technology Stack

- **Backend**: Flask 3.0.0, Python 3.8+
- **Database**: SQLite 3.x
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Templates**: Jinja2 3.1.2
- **PDF Generation**: WeasyPrint 60.1
- **DXF Parsing**: ezdxf 1.1.0
- **Production Server**: Waitress 2.1.2
- **Testing**: pytest 7.4.3

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd full_dxf_laser_buisness

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup

```bash
# Run the setup script
python setup_phase1.py

# Or manually:
# 1. Copy environment file
copy .env.example .env

# 2. Initialize database
python run.py init_db

# 3. Seed initial data
python run.py seed_db
```

### 4. Run

```bash
# Development server
python run.py

# Production server
python wsgi.py
```

Visit `http://localhost:5000` in your browser.

## Project Structure

```
full_dxf_laser_buisness/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # Database models
│   ├── routes/               # Route blueprints
│   │   ├── main.py          # Dashboard routes
│   │   └── clients.py       # Client routes
│   ├── services/             # Business logic
│   │   ├── id_generator.py  # ID generation
│   │   └── activity_logger.py # Activity logging
│   ├── utils/                # Utilities
│   │   ├── validators.py    # Validation functions
│   │   └── helpers.py       # Helper functions
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html        # Base template
│   │   ├── dashboard.html   # Dashboard
│   │   ├── clients/         # Client templates
│   │   └── errors/          # Error pages
│   └── static/               # Static files
│       ├── css/main.css     # Stylesheet
│       └── js/main.js       # JavaScript
├── migrations/               # Database migrations
│   ├── schema_v1.sql        # Database schema
│   └── seed_data.sql        # Seed data
├── tests/                    # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── test_models.py       # Model tests
│   ├── test_services.py     # Service tests
│   └── test_routes.py       # Route tests
├── data/                     # Data directory
│   ├── laser_os.db          # SQLite database
│   └── files/               # File storage
├── config.py                 # Configuration
├── run.py                    # Development server
├── wsgi.py                   # Production WSGI
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_PATH=data/laser_os.db
UPLOAD_FOLDER=data/files
COMPANY_NAME=Your Company Name
```

### Configuration Classes

- **DevelopmentConfig**: Debug enabled, verbose logging
- **ProductionConfig**: Debug disabled, secure settings
- **TestingConfig**: In-memory database, CSRF disabled

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## Production Deployment

### Using Waitress (Recommended for Windows)

```bash
# Set environment
set FLASK_ENV=production
set SECRET_KEY=your-secure-secret-key

# Run with Waitress
python wsgi.py
```

### Using systemd (Linux)

Create `/etc/systemd/system/laser-os.service`:

```ini
[Unit]
Description=Laser OS Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/full_dxf_laser_buisness
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/path/to/venv/bin/python wsgi.py

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable laser-os
sudo systemctl start laser-os
```

## Database Management

### CLI Commands

```bash
# Initialize database
python run.py init_db

# Seed with initial data
python run.py seed_db

# Reset database (WARNING: Deletes all data)
python run.py reset_db

# Flask shell (for manual database operations)
flask shell
```

### Backup

```bash
# Backup database
copy data\laser_os.db data\laser_os_backup_YYYYMMDD.db

# Restore from backup
copy data\laser_os_backup_YYYYMMDD.db data\laser_os.db
```

## Documentation

- **PHASE1_README.md**: Detailed Phase 1 documentation
- **laser_ops_business_automation_master_blueprint_dxf_ops_os.md**: Original blueprint
- **Implementation Blueprint**: Comprehensive implementation plan

## Support & Contribution

This is a proprietary system. For support or questions, contact the development team.

## License

Proprietary - All rights reserved

## Version

**Current Version**: 1.0.0 (Phase 1 Complete)  
**Last Updated**: October 2025

