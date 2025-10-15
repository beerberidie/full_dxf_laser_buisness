# Laser OS - Configuration Guide

## Overview

This guide explains all configuration options available in Laser OS, including environment variables, configuration classes, and best practices for different deployment scenarios.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Variables](#environment-variables)
3. [Configuration Classes](#configuration-classes)
4. [Phase 9 Enhancements](#phase-9-enhancements)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Edit Configuration

Edit `.env` with your settings:

```bash
# Minimum required for development
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# For email functionality (optional in development)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Generate Secret Key

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Environment Variables

### Flask Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Environment mode (`development`, `production`, `testing`) |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | **REQUIRED IN PRODUCTION** - Secret key for sessions and CSRF |

**⚠️ IMPORTANT:** Always change `SECRET_KEY` in production!

---

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `data/laser_os.db` | Path to SQLite database file |

**Note:** The database directory will be created automatically if it doesn't exist.

---

### File Storage Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `UPLOAD_FOLDER` | `data/files` | Path for DXF file uploads |
| `DOCUMENTS_FOLDER` | `data/documents` | Path for project documents (Phase 9) |
| `MAX_UPLOAD_SIZE` | `52428800` (50MB) | Maximum file upload size in bytes |

**Folder Structure:**
```
data/
├── files/              # DXF files
│   ├── clients/
│   └── reports/
└── documents/          # Project documents (Phase 9)
    ├── quotes/
    ├── invoices/
    ├── pops/           # Proof of Payment
    └── delivery_notes/
```

---

### Company Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `COMPANY_NAME` | `Laser OS` | Company name for branding |
| `TIMEZONE` | `Africa/Johannesburg` | Timezone for date/time display |
| `OPERATING_HOURS` | `Mon-Thu 07:00-16:00, Fri 07:00-14:30` | Operating hours display |

---

### Business Rules

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_SLA_DAYS` | `3` | Default Service Level Agreement in days |
| `LOW_STOCK_THRESHOLD` | `3` | Inventory low stock alert threshold |
| `POP_DEADLINE_DAYS` | `3` | Days after POP received to schedule cutting (Phase 9) |
| `MAX_HOURS_PER_DAY` | `8` | Maximum working hours per day for capacity planning (Phase 9) |
| `UPCOMING_DEADLINE_DAYS` | `3` | Days ahead to check for upcoming deadlines (Phase 9) |

---

### Email Configuration (Phase 9)

**Required for Communications Module**

| Variable | Default | Description |
|----------|---------|-------------|
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server hostname |
| `MAIL_PORT` | `587` | SMTP server port |
| `MAIL_USE_TLS` | `True` | Use TLS encryption |
| `MAIL_USE_SSL` | `False` | Use SSL encryption |
| `MAIL_USERNAME` | None | **REQUIRED** - Email account username |
| `MAIL_PASSWORD` | None | **REQUIRED** - Email account password |
| `MAIL_DEFAULT_SENDER` | `noreply@laseros.local` | Default sender email address |
| `MAIL_MAX_EMAILS` | `50` | Maximum emails per SMTP connection |

#### Gmail Configuration

For Gmail, you need to use an **App Password** (not your regular password):

1. Go to https://myaccount.google.com/apppasswords
2. Generate a new app password
3. Use the generated password in `MAIL_PASSWORD`

**Example:**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

#### Other Email Providers

**Office 365:**
```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

**Outlook.com:**
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

**Custom SMTP:**
```bash
MAIL_SERVER=mail.yourdomain.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

---

### Pagination Configuration (Phase 9)

| Variable | Default | Description |
|----------|---------|-------------|
| `ITEMS_PER_PAGE` | `20` | Default items per page for lists |
| `COMMUNICATIONS_PER_PAGE` | `25` | Communications list pagination |

---

## Configuration Classes

### DevelopmentConfig

**Used for:** Local development

**Features:**
- Debug mode enabled
- Detailed error pages
- Auto-reload on code changes
- Configuration status logging

**Activate:**
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows CMD
$env:FLASK_ENV="development"  # Windows PowerShell
```

---

### ProductionConfig

**Used for:** Production deployment

**Features:**
- Debug mode disabled
- Production error handling
- Configuration validation
- Security checks

**Activate:**
```bash
export FLASK_ENV=production  # Linux/Mac
set FLASK_ENV=production     # Windows CMD
$env:FLASK_ENV="production"  # Windows PowerShell
```

**⚠️ Production Checklist:**
- [ ] `SECRET_KEY` is set to a strong random value
- [ ] `MAIL_USERNAME` and `MAIL_PASSWORD` are configured
- [ ] Database backups are configured
- [ ] File storage has sufficient space
- [ ] HTTPS is enabled (if deployed to web)

---

### TestingConfig

**Used for:** Automated testing

**Features:**
- In-memory database
- CSRF disabled
- Fast test execution

**Activate:**
```bash
export FLASK_ENV=testing  # Linux/Mac
set FLASK_ENV=testing     # Windows CMD
$env:FLASK_ENV="testing"  # Windows PowerShell
```

---

## Phase 9 Enhancements

### New Configuration Options

Phase 9 added the following configuration enhancements:

#### 1. **Document Management**
- `DOCUMENTS_FOLDER` - Separate folder for project documents
- `ALLOWED_DOCUMENT_EXTENSIONS` - Valid document file types
- Automatic folder structure creation

#### 2. **Email Communications**
- Complete SMTP configuration
- Gmail support with App Passwords
- Rate limiting with `MAIL_MAX_EMAILS`

#### 3. **Scheduling & Capacity Planning**
- `POP_DEADLINE_DAYS` - Enforce 3-day POP rule
- `MAX_HOURS_PER_DAY` - Capacity planning
- `UPCOMING_DEADLINE_DAYS` - Deadline alerts

#### 4. **Material Types**
- Configurable material list in `config.py`
- Default: Mild Steel, Stainless Steel, Aluminum, Brass, Copper, Galvanized Steel, Other

#### 5. **Document Types**
- Configurable document types in `config.py`
- Default: Quote, Invoice, Proof of Payment, Delivery Note, Other

#### 6. **Communication Types**
- Configurable communication channels in `config.py`
- Default: Email, Phone, WhatsApp, SMS, In-Person, Notification

---

## Production Deployment

### Step 1: Environment Setup

Create production `.env` file:

```bash
# Production Configuration
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets.token_hex(32)>

# Database
DATABASE_PATH=/var/www/laser_os/data/laser_os.db

# File Storage
UPLOAD_FOLDER=/var/www/laser_os/data/files
DOCUMENTS_FOLDER=/var/www/laser_os/data/documents
MAX_UPLOAD_SIZE=52428800

# Company Settings
COMPANY_NAME=Your Company Name
TIMEZONE=Africa/Johannesburg
OPERATING_HOURS=Mon-Fri 08:00-17:00

# Email (REQUIRED)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourcompany.com
```

### Step 2: Validation

The application will automatically validate production configuration on startup. If any critical settings are missing, it will display an error and refuse to start.

**Validation Checks:**
- ✓ SECRET_KEY is not the default value
- ✓ MAIL_USERNAME is set
- ✓ MAIL_PASSWORD is set
- ✓ Upload folder exists
- ✓ Documents folder exists

### Step 3: Run Application

```bash
# Using Waitress (recommended for Windows)
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app

# Using Gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

---

## Troubleshooting

### Email Not Sending

**Problem:** Emails are not being sent

**Solutions:**
1. Check `MAIL_USERNAME` and `MAIL_PASSWORD` are set
2. For Gmail, use App Password (not regular password)
3. Check SMTP server and port are correct
4. Verify TLS/SSL settings
5. Check firewall allows outbound SMTP connections

### File Upload Errors

**Problem:** File uploads fail

**Solutions:**
1. Check `UPLOAD_FOLDER` and `DOCUMENTS_FOLDER` exist
2. Verify folder permissions (write access)
3. Check `MAX_UPLOAD_SIZE` is sufficient
4. Verify file extension is in `ALLOWED_EXTENSIONS` or `ALLOWED_DOCUMENT_EXTENSIONS`

### Configuration Not Loading

**Problem:** Environment variables not being read

**Solutions:**
1. Ensure `.env` file exists in project root
2. Install `python-dotenv` package
3. Restart the application
4. Check for typos in variable names

### Production Validation Fails

**Problem:** Application won't start in production

**Solutions:**
1. Review error message for specific missing settings
2. Ensure all required variables are set in `.env`
3. Generate a new `SECRET_KEY`
4. Configure email settings
5. Create necessary directories

---

## Configuration Reference

### Complete .env Template

See `.env.example` for a complete, commented template with all available configuration options.

### Accessing Configuration in Code

```python
from flask import current_app

# Get configuration value
max_size = current_app.config['MAX_UPLOAD_SIZE']
material_types = current_app.config['MATERIAL_TYPES']
pop_deadline = current_app.config['POP_DEADLINE_DAYS']
```

### Adding Custom Configuration

To add custom configuration:

1. Add to `config.py` in the `Config` class:
```python
MY_CUSTOM_SETTING = os.environ.get('MY_CUSTOM_SETTING', 'default_value')
```

2. Add to `.env.example` with documentation:
```bash
# My Custom Setting
MY_CUSTOM_SETTING=default_value
```

3. Use in your code:
```python
from flask import current_app
value = current_app.config['MY_CUSTOM_SETTING']
```

---

## Support

For additional help:
- Review the main `README.md`
- Check Phase implementation summaries
- Review test files for usage examples


