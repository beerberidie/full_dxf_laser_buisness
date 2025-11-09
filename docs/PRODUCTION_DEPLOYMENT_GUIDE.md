# Production Deployment Guide - Laser OS Tier 1

**Version:** 1.0  
**Last Updated:** October 18, 2025  
**Target Audience:** System Administrators, DevOps Engineers

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Security Configuration](#security-configuration)
5. [Email Configuration](#email-configuration)
6. [Backup Automation](#backup-automation)
7. [Web Server Setup](#web-server-setup)
8. [Production Deployment Checklist](#production-deployment-checklist)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying to production, ensure you have:

- ✅ Python 3.11 or higher installed
- ✅ Virtual environment created and activated
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ Database initialized with sample data (if needed)
- ✅ HTTPS/SSL certificate (for production web server)
- ✅ SMTP server credentials (for email functionality)
- ✅ Backup storage location configured
- ✅ Administrator/root access (for scheduling tasks)

---

## Environment Configuration

### Step 1: Create Production `.env` File

The `.env.example` file contains all configuration options with placeholder values. Create your production environment file:

```bash
# Copy the example file
cp .env.example .env

# On Windows:
copy .env.example .env
```

### Step 2: Generate a Strong SECRET_KEY

The `SECRET_KEY` is critical for session security and must be unique and random.

**Method 1: Using Python (Recommended)**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

This will output a 64-character hexadecimal string like:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Method 2: Using PowerShell (Windows)**

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

**Method 3: Using OpenSSL (Linux/Mac)**

```bash
openssl rand -hex 32
```

### Step 3: Edit `.env` File

Open `.env` in a text editor and configure the following:

```bash
# ============================================================================
# CRITICAL SECURITY SETTINGS
# ============================================================================

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production  # IMPORTANT: Set to 'production' for production!
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE  # Replace with generated key

# Database Configuration
DATABASE_URL=sqlite:///data/laser_os.db  # Or PostgreSQL/MySQL URL for production

# ============================================================================
# EMAIL CONFIGURATION (Required for notifications)
# ============================================================================

MAIL_SERVER=smtp.gmail.com  # Your SMTP server
MAIL_PORT=587  # 587 for TLS, 465 for SSL
MAIL_USE_TLS=True  # True for port 587, False for port 465
MAIL_USE_SSL=False  # False for port 587, True for port 465
MAIL_USERNAME=your-email@example.com  # Your email address
MAIL_PASSWORD=your-app-password  # Your email password or app-specific password
MAIL_DEFAULT_SENDER=your-email@example.com  # Default sender address

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

SESSION_COOKIE_SECURE=True  # MUST be True in production with HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/laser_os.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=10

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

ITEMS_PER_PAGE=20
COMMUNICATIONS_PER_PAGE=50
MAX_CONTENT_LENGTH=52428800  # 50MB max upload size

# ============================================================================
# DEVELOPMENT ONLY (Set to False in production)
# ============================================================================

SQLALCHEMY_ECHO=False  # Set to False in production
TEMPLATES_AUTO_RELOAD=False  # Set to False in production
```

### Step 4: Secure the `.env` File

**CRITICAL:** The `.env` file contains sensitive credentials and must be protected.

```bash
# Linux/Mac: Set restrictive permissions
chmod 600 .env

# Windows: Set file permissions via Properties
# Right-click .env → Properties → Security → Advanced
# Remove all users except the application user
```

**Add to `.gitignore`:**

Verify that `.env` is in your `.gitignore` file to prevent accidental commits:

```bash
# Check if .env is ignored
git check-ignore .env

# If not, add it to .gitignore
echo ".env" >> .gitignore
```

---

## Database Setup

### Option 1: SQLite (Development/Small Production)

SQLite is suitable for small to medium deployments (< 100 concurrent users).

```bash
# Database is already configured in .env
DATABASE_URL=sqlite:///data/laser_os.db

# Ensure data directory exists
mkdir -p data

# Initialize database (if not already done)
python scripts/init_database.py
```

### Option 2: PostgreSQL (Recommended for Production)

PostgreSQL is recommended for larger deployments with high concurrency.

**Install PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib

# macOS
brew install postgresql
```

**Create Database:**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE laser_os_production;
CREATE USER laser_os_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE laser_os_production TO laser_os_user;
\q
```

**Update `.env`:**

```bash
DATABASE_URL=postgresql://laser_os_user:your_secure_password@localhost/laser_os_production
```

**Install PostgreSQL Driver:**

```bash
pip install psycopg2-binary
```

**Migrate Data (if migrating from SQLite):**

```bash
# Export SQLite data
python scripts/export_database.py --output data/export.sql

# Import to PostgreSQL
psql -U laser_os_user -d laser_os_production -f data/export.sql
```

---

## Security Configuration

### 1. Generate Strong SECRET_KEY

See [Step 2: Generate a Strong SECRET_KEY](#step-2-generate-a-strong-secretkey) above.

### 2. Enable HTTPS/SSL

**CRITICAL:** Production deployments MUST use HTTPS to protect user credentials and session cookies.

**Obtain SSL Certificate:**

- **Option 1:** Let's Encrypt (Free) - `certbot`
- **Option 2:** Commercial SSL provider (Comodo, DigiCert, etc.)
- **Option 3:** Self-signed certificate (for internal use only)

**Configure Web Server (see [Web Server Setup](#web-server-setup))**

### 3. Set Secure Session Cookies

In `.env`:

```bash
SESSION_COOKIE_SECURE=True  # Requires HTTPS
SESSION_COOKIE_HTTPONLY=True  # Prevents JavaScript access
SESSION_COOKIE_SAMESITE=Lax  # CSRF protection
```

### 4. Configure Login Security

In `.env`:

```bash
MAX_LOGIN_ATTEMPTS=5  # Lock account after 5 failed attempts
LOCKOUT_DURATION_MINUTES=30  # Lock for 30 minutes
```

### 5. Disable Debug Mode

In `.env`:

```bash
FLASK_ENV=production  # NEVER use 'development' in production
SQLALCHEMY_ECHO=False  # Disable SQL query logging
TEMPLATES_AUTO_RELOAD=False  # Disable template auto-reload
```

---

## Email Configuration

Email is required for:
- Password reset requests
- Client communication notifications
- System alerts and reports

### Gmail Configuration (Example)

**Step 1: Enable 2-Factor Authentication**

1. Go to Google Account settings
2. Security → 2-Step Verification → Enable

**Step 2: Generate App Password**

1. Google Account → Security → App passwords
2. Select "Mail" and "Other (Custom name)"
3. Enter "Laser OS" and click Generate
4. Copy the 16-character password

**Step 3: Configure `.env`**

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password  # From Step 2
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Office 365 Configuration (Example)

```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@yourdomain.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@yourdomain.com
```

### Custom SMTP Server

```bash
MAIL_SERVER=mail.yourdomain.com
MAIL_PORT=587  # or 465 for SSL
MAIL_USE_TLS=True  # or False if using SSL
MAIL_USE_SSL=False  # or True if using SSL
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=your-smtp-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### Test Email Configuration

```bash
python -c "from app import create_app, mail; from flask_mail import Message; app = create_app(); app.app_context().push(); msg = Message('Test Email', recipients=['test@example.com'], body='Email configuration is working!'); mail.send(msg); print('✓ Email sent successfully')"
```

---

## Backup Automation

### Windows: Task Scheduler

**Method 1: Automated Installation (Recommended)**

Run the PowerShell installation script as Administrator:

```powershell
# Open PowerShell as Administrator
# Navigate to project directory
cd C:\path\to\laser_os

# Run installation script
powershell -ExecutionPolicy Bypass -File scripts\install_backup_schedule_windows.ps1
```

This will:
- Create a scheduled task named "LaserOS_DailyBackup"
- Schedule daily backups at 2:00 AM
- Configure the task to run even if the computer is on battery power

**Method 2: Manual Installation**

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task"
3. Name: `LaserOS_DailyBackup`
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
6. Program: `C:\path\to\laser_os\scripts\schedule_backup_windows.bat`
7. Start in: `C:\path\to\laser_os`
8. Finish and verify

**Test the Backup:**

```powershell
# Run the task manually
schtasks /Run /TN "LaserOS_DailyBackup"

# Check backup logs
type logs\backup.log
```

### Linux/Mac: Cron

**Step 1: Make Script Executable**

```bash
chmod +x scripts/schedule_backup_linux.sh
```

**Step 2: Edit Crontab**

```bash
crontab -e
```

**Step 3: Add Cron Job**

Add this line to run backups daily at 2:00 AM:

```bash
0 2 * * * /path/to/laser_os/scripts/schedule_backup_linux.sh
```

**Step 4: Verify Cron Job**

```bash
# List cron jobs
crontab -l

# Check cron logs (Ubuntu/Debian)
grep CRON /var/log/syslog

# Check backup logs
tail -f logs/backup.log
```

### Backup Retention Policy

By default, backups are kept for 30 days. To change this:

**Edit the batch/shell script:**

```bash
# Windows: scripts\schedule_backup_windows.bat
python scripts\backup_database.py --keep 60  # Keep 60 days

# Linux/Mac: scripts/schedule_backup_linux.sh
python scripts/backup_database.py --keep 60  # Keep 60 days
```

### Backup Storage Recommendations

- **Local Backups:** `data/backups/` (default)
- **Network Storage:** Mount network drive and update backup script
- **Cloud Storage:** Use `rclone` or cloud provider CLI to sync backups
- **Offsite Backups:** Copy backups to remote server via `rsync` or `scp`

**Example: Sync to Cloud Storage (after backup)**

```bash
# Add to schedule_backup_windows.bat or schedule_backup_linux.sh
rclone sync data/backups/ remote:laser_os_backups/
```

---

## Web Server Setup

### Option 1: Waitress (Simple, Windows-friendly)

Waitress is a production-ready WSGI server that works well on Windows.

**Install:**

```bash
pip install waitress
```

**Create `run_production.py`:**

```python
from waitress import serve
from app import create_app

app = create_app()

if __name__ == '__main__':
    print('Starting Laser OS Tier 1 on http://0.0.0.0:8080')
    serve(app, host='0.0.0.0', port=8080, threads=4)
```

**Run:**

```bash
python run_production.py
```

**Create Windows Service (Optional):**

Use `NSSM` (Non-Sucking Service Manager) to run as a Windows service:

```powershell
# Download NSSM from https://nssm.cc/download
nssm install LaserOS "C:\path\to\venv\Scripts\python.exe" "C:\path\to\laser_os\run_production.py"
nssm start LaserOS
```

### Option 2: Gunicorn (Linux/Mac)

Gunicorn is a popular WSGI server for Linux/Mac.

**Install:**

```bash
pip install gunicorn
```

**Run:**

```bash
gunicorn -w 4 -b 0.0.0.0:8080 "app:create_app()"
```

**Create Systemd Service:**

Create `/etc/systemd/system/laser_os.service`:

```ini
[Unit]
Description=Laser OS Tier 1
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/laser_os
Environment="PATH=/path/to/laser_os/venv/bin"
ExecStart=/path/to/laser_os/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**

```bash
sudo systemctl enable laser_os
sudo systemctl start laser_os
sudo systemctl status laser_os
```

### Option 3: Nginx + Gunicorn (Recommended for Production)

**Install Nginx:**

```bash
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

**Configure Nginx:**

Create `/etc/nginx/sites-available/laser_os`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Static Files
    location /static {
        alias /path/to/laser_os/app/static;
        expires 30d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site:**

```bash
sudo ln -s /etc/nginx/sites-available/laser_os /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Production Deployment Checklist

Use this checklist to verify your production deployment:

### Security

- [ ] `SECRET_KEY` changed to strong random value (64+ characters)
- [ ] `FLASK_ENV` set to `production`
- [ ] `SESSION_COOKIE_SECURE` set to `True` (requires HTTPS)
- [ ] `SQLALCHEMY_ECHO` set to `False`
- [ ] `TEMPLATES_AUTO_RELOAD` set to `False`
- [ ] `.env` file permissions restricted (chmod 600 on Linux/Mac)
- [ ] `.env` file added to `.gitignore`
- [ ] HTTPS/SSL certificate installed and configured
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Database credentials are strong and unique

### Email

- [ ] `MAIL_SERVER` configured with valid SMTP server
- [ ] `MAIL_USERNAME` and `MAIL_PASSWORD` set
- [ ] Email sending tested successfully
- [ ] Default sender address configured

### Backups

- [ ] Automated backups scheduled (Task Scheduler or cron)
- [ ] Backup retention policy configured
- [ ] Backup directory has sufficient disk space
- [ ] Backup restore tested successfully
- [ ] Offsite backup strategy implemented (optional but recommended)

### Performance

- [ ] Database indexes applied (`migrations/schema_v11_indexes.sql`)
- [ ] Static files served by web server (Nginx) or CDN
- [ ] Logging configured with rotation
- [ ] Performance monitoring enabled

### Monitoring

- [ ] Application logs reviewed (`logs/laser_os.log`)
- [ ] Backup logs reviewed (`logs/backup.log`)
- [ ] Error tracking configured (optional: Sentry, Rollbar)
- [ ] Uptime monitoring configured (optional: UptimeRobot, Pingdom)

### Testing

- [ ] All features tested in production environment
- [ ] User authentication tested
- [ ] Email notifications tested
- [ ] File uploads tested
- [ ] Database queries tested
- [ ] Backup and restore tested

---

## Monitoring and Maintenance

### Log Files

**Application Logs:**
- Location: `logs/laser_os.log`
- Rotation: 10 files × 10MB each
- Review: Weekly

**Backup Logs:**
- Location: `logs/backup.log`
- Rotation: 10 files × 10MB each
- Review: Weekly

**Web Server Logs:**
- Nginx: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- Review: Weekly

### Performance Monitoring

See `docs/PERFORMANCE_MONITORING_GUIDE.md` for detailed instructions.

### Database Maintenance

**SQLite:**

```bash
# Vacuum database (reclaim space)
sqlite3 data/laser_os.db "VACUUM;"

# Analyze database (update statistics)
sqlite3 data/laser_os.db "ANALYZE;"
```

**PostgreSQL:**

```bash
# Vacuum and analyze
psql -U laser_os_user -d laser_os_production -c "VACUUM ANALYZE;"
```

### Backup Verification

**Monthly:** Test backup restore process

```bash
# Restore to test database
python scripts/restore_database.py --backup laser_os_backup_YYYYMMDD_HHMMSS.db --target data/test_restore.db

# Verify data integrity
python scripts/verify_database.py --database data/test_restore.db
```

---

## Troubleshooting

### Issue: Application won't start

**Check:**
1. Virtual environment activated
2. All dependencies installed (`pip install -r requirements.txt`)
3. `.env` file exists and is readable
4. Database file exists and is readable
5. Logs directory exists

**Solution:**

```bash
# Verify environment
python -c "from app import create_app; app = create_app(); print('✓ Application OK')"
```

### Issue: Email not sending

**Check:**
1. SMTP credentials correct
2. SMTP server accessible (firewall, network)
3. App-specific password used (Gmail)
4. TLS/SSL settings correct

**Solution:**

```bash
# Test SMTP connection
python -c "import smtplib; server = smtplib.SMTP('smtp.gmail.com', 587); server.starttls(); server.login('user@gmail.com', 'password'); print('✓ SMTP OK')"
```

### Issue: Backups not running

**Windows:**

```powershell
# Check task status
schtasks /Query /TN "LaserOS_DailyBackup" /V /FO LIST

# Check task history
Get-ScheduledTask -TaskName "LaserOS_DailyBackup" | Get-ScheduledTaskInfo

# Run manually
schtasks /Run /TN "LaserOS_DailyBackup"
```

**Linux/Mac:**

```bash
# Check cron logs
grep CRON /var/log/syslog | grep backup

# Test script manually
./scripts/schedule_backup_linux.sh
```

### Issue: Database locked

**SQLite only:**

```bash
# Check for processes using database
lsof data/laser_os.db  # Linux/Mac
handle data\laser_os.db  # Windows (Sysinternals)

# Kill processes and restart application
```

### Issue: Performance degradation

**Check:**
1. Database indexes applied
2. Log files not too large
3. Disk space available
4. Memory usage normal

**Solution:**

```bash
# Vacuum database
sqlite3 data/laser_os.db "VACUUM;"

# Rotate logs
python scripts/rotate_logs.py

# Check disk space
df -h  # Linux/Mac
wmic logicaldisk get size,freespace,caption  # Windows
```

---

## Additional Resources

- **Application Documentation:** `docs/README.md`
- **Quick Wins Summary:** `docs/QUICK_WINS_IMPLEMENTATION_SUMMARY.md`
- **System Status Report:** `docs/features/SYSTEM_STATUS_REPORT.md`
- **Performance Monitoring:** `docs/PERFORMANCE_MONITORING_GUIDE.md`
- **Backup Scripts:** `scripts/backup_database.py`, `scripts/restore_database.py`

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review application logs (`logs/laser_os.log`)
3. Check GitHub issues (if applicable)
4. Contact system administrator

---

**Document Version:** 1.0  
**Last Updated:** October 18, 2025  
**Next Review:** November 18, 2025

