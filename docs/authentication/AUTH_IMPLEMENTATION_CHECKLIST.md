# Authentication & Authorization Implementation Checklist
## Laser OS Tier 1 - Quick Reference Guide

**Related Document:** `AUTHENTICATION_AUTHORIZATION_DESIGN.md`  
**Date:** 2025-10-17

---

## Pre-Implementation Checklist

- [ ] Read complete design document (`AUTHENTICATION_AUTHORIZATION_DESIGN.md`)
- [ ] Backup current database (`data/laser_os.db`)
- [ ] Create git branch for auth implementation
- [ ] Review current application structure
- [ ] Identify all routes that need protection

---

## Phase 1: Foundation Setup

### 1.1 Install Dependencies
```bash
pip install Flask-Login==0.6.3
pip install Flask-WTF==1.2.1
pip install WTForms==3.1.1
pip install email-validator==2.1.0
pip freeze > requirements.txt
```

- [ ] Dependencies installed
- [ ] Requirements.txt updated
- [ ] Virtual environment activated

### 1.2 Create Directory Structure
```bash
mkdir -p app/models
mkdir -p app/forms
mkdir -p app/routes/admin
mkdir -p app/templates/auth
mkdir -p app/templates/admin
mkdir -p scripts
```

- [ ] Directories created
- [ ] Structure verified

### 1.3 Create Model Files

**Files to create:**
- [ ] `app/models/__init__.py`
- [ ] `app/models/auth.py` (User, Role, UserRole, LoginHistory models)
- [ ] `app/models/business.py` (move existing models here)

**Action:** Copy model code from design document Appendix A

### 1.4 Update Configuration

**File:** `config.py`

Add authentication configuration:
- [ ] SECRET_KEY configuration
- [ ] Session security settings
- [ ] Remember me settings
- [ ] Account lockout settings
- [ ] Password requirements

**Action:** Copy config additions from design document Appendix G

---

## Phase 2: Authentication Setup

### 2.1 Initialize Flask-Login

**File:** `app/__init__.py`

- [ ] Import LoginManager
- [ ] Initialize login_manager
- [ ] Configure login_manager settings
- [ ] Add user_loader callback
- [ ] Register auth blueprint

**Action:** Follow Phase 3 in design document

### 2.2 Create Forms

**File:** `app/forms/auth.py`

- [ ] LoginForm
- [ ] RegistrationForm
- [ ] ChangePasswordForm

**Action:** Copy form code from design document Phase 5

### 2.3 Create Authentication Routes

**File:** `app/routes/auth.py`

- [ ] Login route (GET/POST)
- [ ] Logout route
- [ ] Helper functions (log_successful_login, log_failed_login, log_logout)

**Action:** Copy route code from design document Phase 4

### 2.4 Create Login Template

**File:** `app/templates/auth/login.html`

- [ ] Create login form template
- [ ] Add styling
- [ ] Test form rendering

**Action:** Copy template from design document Appendix C

### 2.5 Update Base Template

**File:** `app/templates/base.html`

- [ ] Add user info display in header
- [ ] Add login/logout links
- [ ] Show current user role

**Action:** Follow Appendix E in design document

---

## Phase 3: Authorization Setup

### 3.1 Create Decorators

**File:** `app/utils/decorators.py`

- [ ] role_required decorator
- [ ] permission_required decorator
- [ ] admin_required decorator

**Action:** Copy decorator code from design document Phase 6

### 3.2 Protect Routes

**Apply decorators to existing routes based on permissions matrix:**

**Clients Routes** (`app/routes/clients.py`):
- [ ] list_clients - @login_required
- [ ] create_client - @role_required('admin', 'manager')
- [ ] edit_client - @role_required('admin', 'manager')
- [ ] delete_client - @role_required('admin', 'manager')

**Projects Routes** (`app/routes/projects.py`):
- [ ] index - @login_required
- [ ] create - @role_required('admin', 'manager')
- [ ] edit - @role_required('admin', 'manager', 'operator')
- [ ] delete - @role_required('admin', 'manager')
- [ ] toggle_pop - @role_required('admin', 'manager', 'operator')

**Products Routes** (`app/routes/products.py`):
- [ ] index - @login_required
- [ ] create - @role_required('admin', 'manager')
- [ ] edit - @role_required('admin', 'manager')
- [ ] delete - @role_required('admin', 'manager')

**Queue Routes** (`app/routes/queue.py`):
- [ ] index - @login_required
- [ ] add_to_queue - @role_required('admin', 'manager', 'operator')
- [ ] start_job - @role_required('admin', 'manager', 'operator')
- [ ] complete_job - @role_required('admin', 'manager', 'operator')
- [ ] remove_from_queue - @role_required('admin', 'manager')

**Inventory Routes** (`app/routes/inventory.py`):
- [ ] index - @login_required
- [ ] add_stock - @role_required('admin', 'manager', 'operator')
- [ ] edit_stock - @role_required('admin', 'manager', 'operator')
- [ ] delete_stock - @role_required('admin', 'manager')

**Quotes/Invoices Routes**:
- [ ] View - @login_required
- [ ] Create/Edit/Delete - @role_required('admin', 'manager')

**Communications Routes**:
- [ ] View - @login_required
- [ ] Send - @role_required('admin', 'manager', 'operator')
- [ ] Delete - @role_required('admin', 'manager')

**Reports Routes**:
- [ ] View - @login_required
- [ ] Generate - @role_required('admin', 'manager', 'operator')
- [ ] Export - @role_required('admin', 'manager')

**Presets Routes**:
- [ ] View - @login_required
- [ ] Create/Edit/Delete - @role_required('admin', 'manager')

### 3.3 Add Template Permission Checks

**Update templates to show/hide elements based on roles:**

Example:
```html
{% if current_user.has_role('admin') or current_user.has_role('manager') %}
    <a href="{{ url_for('clients.create_client') }}" class="btn btn-primary">Create Client</a>
{% endif %}
```

- [ ] Dashboard template
- [ ] Clients templates
- [ ] Projects templates
- [ ] Products templates
- [ ] Queue templates
- [ ] Other templates

---

## Phase 4: User Management

### 4.1 Create Admin Routes

**File:** `app/routes/admin.py`

- [ ] users_list route
- [ ] create_user route
- [ ] edit_user route
- [ ] delete_user route
- [ ] assign_role route
- [ ] login_history route

### 4.2 Create Admin Templates

**Files to create:**
- [ ] `app/templates/admin/users_list.html`
- [ ] `app/templates/admin/user_form.html`
- [ ] `app/templates/admin/user_detail.html`
- [ ] `app/templates/admin/login_history.html`

**Action:** Use template from design document Appendix D as reference

### 4.3 Add Admin Navigation

**File:** `app/templates/base.html`

- [ ] Add "Admin" menu item (visible only to admins)
- [ ] Add dropdown with user management links

---

## Phase 5: Database Migration

### 5.1 Create Database Tables

```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

- [ ] Tables created successfully
- [ ] Verify tables in database

### 5.2 Initialize Roles and Admin User

```bash
python scripts/init_auth.py
```

- [ ] Script created (copy from Appendix B)
- [ ] Script executed successfully
- [ ] Roles created (admin, manager, operator, viewer)
- [ ] Admin user created
- [ ] Admin credentials saved securely

**Admin Credentials:**
- Username: _______________
- Password: _______________ (stored securely)
- Email: _______________

---

## Phase 6: Security Hardening

### 6.1 Enable CSRF Protection

**File:** `app/__init__.py`

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
csrf.init_app(app)
```

- [ ] CSRF protection enabled
- [ ] All forms include {{ form.hidden_tag() }}

### 6.2 Add Rate Limiting

```bash
pip install Flask-Limiter
```

**File:** `app/__init__.py`

- [ ] Flask-Limiter installed
- [ ] Limiter configured
- [ ] Applied to login route

### 6.3 Add Security Headers

**File:** `app/__init__.py`

- [ ] after_request handler added
- [ ] Security headers configured
- [ ] Headers tested

### 6.4 Configure Session Security

**File:** `config.py`

- [ ] SESSION_COOKIE_SECURE = True (for HTTPS)
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] SESSION_COOKIE_SAMESITE = 'Lax'
- [ ] PERMANENT_SESSION_LIFETIME configured

### 6.5 Add Password Validation

**File:** `app/utils/validators.py`

- [ ] Password strength validator created
- [ ] Applied to registration form
- [ ] Applied to change password form

---

## Phase 7: Testing

### 7.1 Unit Tests

**File:** `tests/test_auth.py`

- [ ] Test password hashing
- [ ] Test user roles
- [ ] Test permissions
- [ ] Test account lockout
- [ ] All tests passing

### 7.2 Integration Tests

- [ ] Test login flow
- [ ] Test logout flow
- [ ] Test failed login attempts
- [ ] Test account lockout
- [ ] Test role-based access
- [ ] All tests passing

### 7.3 Manual Testing

**Test as Admin:**
- [ ] Login successful
- [ ] Can access all features
- [ ] Can manage users
- [ ] Can create/edit/delete all entities

**Test as Manager:**
- [ ] Login successful
- [ ] Can create/edit/delete business entities
- [ ] Cannot access user management
- [ ] Cannot access admin settings

**Test as Operator:**
- [ ] Login successful
- [ ] Can edit production data
- [ ] Can manage queue
- [ ] Cannot delete entities

**Test as Viewer:**
- [ ] Login successful
- [ ] Can view all data
- [ ] Cannot edit anything
- [ ] Cannot delete anything

**Test Security:**
- [ ] Failed login attempts tracked
- [ ] Account locks after 5 failed attempts
- [ ] Locked account shows appropriate message
- [ ] Session expires after configured time
- [ ] Remember me works correctly
- [ ] CSRF protection working
- [ ] Unauthorized access blocked (403 error)

---

## Phase 8: Network Configuration

### 8.1 Local Network Access

**Configure for LAN access:**

- [ ] Update run.py/wsgi.py to bind to 0.0.0.0
- [ ] Configure firewall to allow port 8080
- [ ] Test access from another computer on LAN
- [ ] Document server IP address: _______________

### 8.2 VPN Setup (Choose One)

**Option A: WireGuard**
- [ ] WireGuard installed on server
- [ ] Server keys generated
- [ ] Client keys generated
- [ ] Server configured
- [ ] Client configured
- [ ] VPN connection tested
- [ ] Application accessible via VPN

**Option B: OpenVPN**
- [ ] OpenVPN installed
- [ ] PKI initialized
- [ ] Server certificate created
- [ ] Client certificates created
- [ ] Server configured
- [ ] Client configured
- [ ] VPN connection tested
- [ ] Application accessible via VPN

**Option C: Tailscale**
- [ ] Tailscale installed on server
- [ ] Tailscale installed on clients
- [ ] Devices connected to same network
- [ ] Application accessible via Tailscale IP

### 8.3 HTTPS/SSL Setup

**Development (Self-Signed):**
- [ ] Certificate generated
- [ ] Flask configured for HTTPS
- [ ] HTTPS tested

**Production (Let's Encrypt):**
- [ ] Domain name configured
- [ ] Nginx installed
- [ ] Nginx configured as reverse proxy
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Auto-renewal configured
- [ ] HTTPS tested

---

## Phase 9: Deployment

### 9.1 Production Configuration

**File:** `.env`

- [ ] SECRET_KEY generated (strong random value)
- [ ] FLASK_ENV=production
- [ ] SESSION_COOKIE_SECURE=True
- [ ] Database path configured
- [ ] Email settings configured (if needed)

### 9.2 Production Server Setup

**Using Waitress:**
- [ ] Waitress installed
- [ ] wsgi.py configured
- [ ] Systemd service created
- [ ] Service enabled and started
- [ ] Service tested

### 9.3 Backup Strategy

- [ ] Backup script created
- [ ] Cron job configured
- [ ] Test backup restoration
- [ ] Document backup location: _______________

### 9.4 Monitoring

- [ ] Application logs configured
- [ ] Security logs configured
- [ ] Error monitoring set up
- [ ] Login history reviewed regularly

---

## Phase 10: Documentation & Training

### 10.1 User Documentation

- [ ] Login instructions created
- [ ] Password reset instructions created
- [ ] Role descriptions documented
- [ ] User guide created

### 10.2 Admin Documentation

- [ ] User management guide created
- [ ] Role assignment guide created
- [ ] Security best practices documented
- [ ] Troubleshooting guide created

### 10.3 Training

- [ ] Admin training completed
- [ ] Manager training completed
- [ ] Operator training completed
- [ ] Viewer training completed

---

## Post-Implementation Checklist

### Security Audit
- [ ] All routes protected appropriately
- [ ] All forms have CSRF protection
- [ ] Password requirements enforced
- [ ] Session security configured
- [ ] Security headers in place
- [ ] Rate limiting configured
- [ ] HTTPS enabled (production)

### Functionality Verification
- [ ] All user roles work as expected
- [ ] Permissions matrix followed correctly
- [ ] Login/logout working
- [ ] User management working
- [ ] Audit trail (login history) working
- [ ] Account lockout working

### Performance
- [ ] Application performance acceptable
- [ ] Database queries optimized
- [ ] No N+1 query issues
- [ ] Session storage efficient

### Documentation
- [ ] All code documented
- [ ] User guide complete
- [ ] Admin guide complete
- [ ] Network setup documented
- [ ] Credentials stored securely

---

## Troubleshooting Common Issues

### Issue: Cannot log in
- [ ] Check username/password correct
- [ ] Check account is active
- [ ] Check account not locked
- [ ] Check database connection

### Issue: 403 Forbidden errors
- [ ] Check user has correct role
- [ ] Check decorator applied correctly
- [ ] Check user is authenticated

### Issue: CSRF token errors
- [ ] Check CSRF protection enabled
- [ ] Check form includes {{ form.hidden_tag() }}
- [ ] Check session working

### Issue: Cannot access from LAN
- [ ] Check server binding to 0.0.0.0
- [ ] Check firewall allows port
- [ ] Check correct IP address used

### Issue: VPN not connecting
- [ ] Check VPN service running
- [ ] Check firewall allows VPN port
- [ ] Check keys/certificates correct
- [ ] Check configuration files

---

## Success Criteria

✅ **Authentication Working:**
- Users can log in with username/password
- Sessions persist correctly
- Remember me works
- Logout works
- Failed attempts tracked
- Account lockout works

✅ **Authorization Working:**
- All routes protected appropriately
- Role-based access enforced
- Permissions matrix followed
- Unauthorized access blocked

✅ **Network Access Working:**
- Local LAN access works
- Remote VPN access works
- HTTPS configured (production)

✅ **Security Hardened:**
- CSRF protection enabled
- Rate limiting configured
- Security headers set
- Passwords hashed
- Sessions secure

✅ **User Management Working:**
- Admins can create users
- Admins can assign roles
- Admins can view login history
- Users can change passwords

---

## Sign-Off

**Implementation Completed By:** _______________  
**Date:** _______________  
**Tested By:** _______________  
**Date:** _______________  
**Approved By:** _______________  
**Date:** _______________

---

**Notes:**

Use this checklist alongside the main design document (`AUTHENTICATION_AUTHORIZATION_DESIGN.md`) for step-by-step implementation guidance.

