# Sage Agent MVP - Implementation Checklist

**Version:** 1.0  
**Date:** 2025-10-10  
**Reference:** See `MVP_BLUEPRINT.md` for detailed implementation guide

---

## Quick Start

This checklist provides a task-by-task breakdown of the MVP implementation. Check off items as you complete them.

---

## Phase 1: OAuth 2.0 Correction & Token Management ⚠️ CRITICAL

**Priority:** CRITICAL  
**Estimated Time:** 2-3 days  
**Dependencies:** None

### Task 1.1: Fix OAuth URLs

- [ ] Update `backend/app/oauth.py` line 20:
  - [ ] Change authorize URL to `https://www.sageone.com/oauth2/auth/central?filter=apiv3.1`
- [ ] Update `backend/app/oauth.py` line 34:
  - [ ] Change token URL to `https://oauth.accounting.sage.com/token`
- [ ] Add `country=za` parameter to OAuth request
- [ ] Add `filter=apiv3.1` parameter to OAuth request
- [ ] Test OAuth flow redirects to correct Sage URL

### Task 1.2: Add Token Expiry Tracking

- [ ] Update `auth_callback` function in `backend/app/oauth.py`
- [ ] Calculate `expires_at` from `expires_in` (300 seconds)
- [ ] Store `expires_at` in Connection model
- [ ] Add required headers to token request
- [ ] Fetch available businesses after OAuth
- [ ] Change connection status to `pending_business_selection`
- [ ] Redirect to business selection page
- [ ] Test token expiry is correctly calculated

### Task 1.3: Implement Token Refresh Mechanism

- [ ] Create new file `backend/app/token_manager.py`
- [ ] Implement `TokenManager` class
- [ ] Implement `refresh_token()` method
- [ ] Implement `is_token_expired()` method with 60-second buffer
- [ ] Implement `get_valid_token()` method
- [ ] Test token refresh with expired token
- [ ] Verify new refresh token is stored

### Task 1.4: Update SageV31Client to Use Token Manager

- [ ] Import `TokenManager` in `backend/app/sage_v31.py`
- [ ] Update `_request()` method to call `get_valid_token()`
- [ ] Add X-Business header if `business_id` is set
- [ ] Add 401 error handling with token refresh retry
- [ ] Test automatic token refresh on API calls
- [ ] Test 401 retry logic

**Phase 1 Acceptance Criteria:**
- [ ] OAuth URLs point to correct Sage endpoints
- [ ] Token expiry is calculated and stored
- [ ] Tokens are automatically refreshed before expiry
- [ ] 401 errors trigger token refresh and retry
- [ ] New refresh tokens are stored after each refresh

---

## Phase 2: X-Business Context Management ⚠️ CRITICAL

**Priority:** CRITICAL  
**Estimated Time:** 2 days  
**Dependencies:** Phase 1

### Task 2.1: Update Database Schema

- [ ] Verify `business_id` field exists in Connection model
- [ ] Create new `Business` model in `backend/app/db.py`
- [ ] Add fields: id, connection_id, tenant_id, name, country, currency, is_selected
- [ ] Run database migration or recreate tables
- [ ] Test Business model creation

### Task 2.2: Create Business Selection Endpoint

- [ ] Create new file `backend/app/routes_business.py`
- [ ] Implement `list_businesses()` endpoint
- [ ] Implement `select_business()` endpoint
- [ ] Register router in `backend/app/main.py`
- [ ] Test listing businesses from Sage API
- [ ] Test selecting a business updates connection

### Task 2.3: Build Business Selection UI

- [ ] Create new file `frontend/src/pages/SelectBusiness.jsx`
- [ ] Implement business list fetching
- [ ] Implement business selection handler
- [ ] Add navigation to main app after selection
- [ ] Style business cards with hover effects
- [ ] Test business selection flow end-to-end

**Phase 2 Acceptance Criteria:**
- [ ] Business ID stored in Connection model
- [ ] X-Business header included in all API requests
- [ ] User can select business after OAuth
- [ ] Business selection UI is intuitive
- [ ] Selected business persists across sessions

---

## Phase 3: South African Localization 🔥 HIGH

**Priority:** HIGH  
**Estimated Time:** 2 days  
**Dependencies:** Phase 1, Phase 2

### Task 3.1: Create South African Defaults

- [ ] Create new file `backend/app/za_defaults.py`
- [ ] Define `DEFAULT_CURRENCY = "ZAR"`
- [ ] Define `VAT_RATES` dictionary (STANDARD, ZERO, EXEMPT)
- [ ] Define `PAYMENT_TERMS` dictionary
- [ ] Implement `get_invoice_template()` function
- [ ] Implement `calculate_vat()` function
- [ ] Write unit tests for VAT calculation
- [ ] Test invoice template generation

### Task 3.2: Enhance Invoice Creation Endpoint

- [ ] Add imports to `backend/app/routes_sage.py`
- [ ] Create `InvoiceLineItem` Pydantic model
- [ ] Create `CreateInvoiceRequest` Pydantic model
- [ ] Create `InvoicePreview` Pydantic model
- [ ] Implement `preview_sales_invoice()` endpoint
- [ ] Update `create_sales_invoice()` to use ZA template
- [ ] Add notes field support
- [ ] Test preview endpoint
- [ ] Test invoice creation with ZAR and 15% VAT

### Task 3.3: Create Settings Initialization

- [ ] Add `initialize_za_defaults()` endpoint to `backend/app/routes_settings.py`
- [ ] Store invoice defaults in settings
- [ ] Store VAT rates in settings
- [ ] Store payment terms in settings
- [ ] Test initialization endpoint
- [ ] Verify settings are retrievable

**Phase 3 Acceptance Criteria:**
- [ ] ZAR currency set as default
- [ ] ZA_STANDARD (15%) VAT rate configured
- [ ] Payment terms (30 days default) configured
- [ ] Invoice template includes all required fields
- [ ] VAT calculation is accurate

---

## Phase 4: Audit Logging & Preview/Confirm Pattern 🔥 HIGH

**Priority:** HIGH  
**Estimated Time:** 2 days  
**Dependencies:** Phase 3

### Task 4.1: Create Audit Service

- [ ] Create new file `backend/app/audit_service.py`
- [ ] Implement `AuditService` class
- [ ] Implement `create_log()` method
- [ ] Implement `update_log()` method
- [ ] Implement `get_logs()` method
- [ ] Test audit log creation
- [ ] Test audit log updates

### Task 4.2: Integrate Audit Logging into Invoice Creation

- [ ] Import `AuditService` in `backend/app/routes_sage.py`
- [ ] Update `create_sales_invoice()` to create audit log
- [ ] Add `audit_log_id` parameter support
- [ ] Update audit log on success
- [ ] Update audit log on failure
- [ ] Implement `get_audit_logs()` endpoint
- [ ] Test audit logging for successful creation
- [ ] Test audit logging for failed creation

**Phase 4 Acceptance Criteria:**
- [ ] All write operations create audit logs
- [ ] Preview creates log with status="preview"
- [ ] Confirm updates log to status="confirmed"
- [ ] Success/failure status recorded
- [ ] Request and response data stored

---

## Phase 5: Incremental Sync Mechanism 📊 MEDIUM

**Priority:** MEDIUM  
**Estimated Time:** 2 days  
**Dependencies:** Phase 1, Phase 2

### Task 5.1: Create Sync Service

- [ ] Create new file `backend/app/sync_service.py`
- [ ] Implement `SyncService` class
- [ ] Implement `get_cursor()` method
- [ ] Implement `update_cursor()` method
- [ ] Implement `sync_sales_invoices()` method
- [ ] Implement `sync_contacts()` method
- [ ] Implement `sync_all()` method
- [ ] Test cursor storage and retrieval
- [ ] Test incremental sync

### Task 5.2: Create Sync Endpoints

- [ ] Create new file `backend/app/routes_sync.py`
- [ ] Implement `sync_sales_invoices()` endpoint
- [ ] Implement `sync_contacts()` endpoint
- [ ] Implement `sync_all()` endpoint with background tasks
- [ ] Implement `sync_status()` endpoint
- [ ] Register router in `backend/app/main.py`
- [ ] Test sync endpoints
- [ ] Test background sync

**Phase 5 Acceptance Criteria:**
- [ ] Sync cursors stored per resource
- [ ] `updated_or_created_since` parameter used
- [ ] Incremental sync reduces API calls
- [ ] Background sync option available
- [ ] Sync status visible to users

---

## Security Enhancements 🔒

**Priority:** HIGH (before production)  
**Estimated Time:** 1 day

- [ ] Create `backend/app/crypto.py` for token encryption
- [ ] Implement `TokenEncryption` class
- [ ] Encrypt tokens before storing in database
- [ ] Decrypt tokens when retrieving from database
- [ ] Update CORS configuration for production
- [ ] Implement rate limiting (`backend/app/rate_limit.py`)
- [ ] Add input validation with Pydantic models
- [ ] Add CSRF protection
- [ ] Test token encryption/decryption
- [ ] Test rate limiting

---

## UI Components 🎨

**Priority:** MEDIUM  
**Estimated Time:** 3-4 days

### OAuth Connection Flow
- [ ] Create `frontend/src/components/OAuthConnect.jsx`
- [ ] Add Sage logo
- [ ] Add connection button
- [ ] Add security badges
- [ ] Test OAuth initiation

### Invoice Creation Form
- [ ] Create `frontend/src/pages/CreateInvoice.jsx`
- [ ] Add customer selector
- [ ] Add date pickers
- [ ] Add line items management
- [ ] Add VAT calculation display
- [ ] Add preview button
- [ ] Add create button
- [ ] Test form validation
- [ ] Test invoice creation

### Invoice Preview Modal
- [ ] Create `frontend/src/components/InvoicePreviewModal.jsx`
- [ ] Display invoice summary
- [ ] Add confirm button
- [ ] Add cancel button
- [ ] Test preview display

### Contact Management
- [ ] Create `frontend/src/pages/Contacts.jsx`
- [ ] Add contact list table
- [ ] Add search functionality
- [ ] Add filter dropdown
- [ ] Add new contact button
- [ ] Test contact listing

### Settings Page
- [ ] Create `frontend/src/pages/Settings.jsx`
- [ ] Add connection status display
- [ ] Add invoice defaults configuration
- [ ] Add sync settings
- [ ] Test settings updates

### Audit Log Viewer
- [ ] Create `frontend/src/pages/AuditLogs.jsx`
- [ ] Add audit log table
- [ ] Add filters
- [ ] Add pagination
- [ ] Test audit log display

---

## Configuration & Setup ⚙️

**Priority:** CRITICAL (before deployment)  
**Estimated Time:** 1 day

- [ ] Register Sage Developer account
- [ ] Create Sage application
- [ ] Save Client ID and Client Secret
- [ ] Get Sage trial account (South Africa)
- [ ] Extend trial for development
- [ ] Set up test data in Sage
- [ ] Copy `.env.example` to `.env`
- [ ] Update `.env` with Sage credentials
- [ ] Initialize database
- [ ] Initialize ZA defaults
- [ ] Test OAuth flow end-to-end

---

## Testing 🧪

**Priority:** HIGH  
**Estimated Time:** 2 days

### Unit Tests
- [ ] Write tests for `za_defaults.py`
- [ ] Write tests for `token_manager.py`
- [ ] Write tests for `audit_service.py`
- [ ] Write tests for `sync_service.py`
- [ ] Run all unit tests
- [ ] Achieve >80% code coverage

### Integration Tests
- [ ] Write tests for OAuth flow
- [ ] Write tests for invoice creation
- [ ] Write tests for contact management
- [ ] Write tests for sync endpoints
- [ ] Run all integration tests

### Manual Testing
- [ ] Test OAuth connection flow
- [ ] Test business selection
- [ ] Test invoice creation
- [ ] Test token refresh (wait 5+ minutes)
- [ ] Test error handling
- [ ] Test audit logging
- [ ] Test sync functionality

---

## Deployment 🚀

**Priority:** CRITICAL (for production)  
**Estimated Time:** 2-3 days

### Infrastructure Setup
- [ ] Provision server (AWS/DigitalOcean/Azure)
- [ ] Install PostgreSQL
- [ ] Install Redis
- [ ] Configure firewall
- [ ] Set up domain name
- [ ] Obtain SSL certificate

### Database Migration
- [ ] Create PostgreSQL database
- [ ] Update DATABASE_URL
- [ ] Run migrations
- [ ] Test database connection

### Backend Deployment
- [ ] Choose deployment method (Docker or systemd)
- [ ] Create Dockerfile (if using Docker)
- [ ] Create docker-compose.yml (if using Docker)
- [ ] Create systemd service (if using systemd)
- [ ] Deploy backend
- [ ] Test backend health check

### Frontend Deployment
- [ ] Build frontend for production
- [ ] Install Nginx
- [ ] Configure Nginx
- [ ] Deploy frontend
- [ ] Test frontend access

### Monitoring Setup
- [ ] Set up application logging
- [ ] Set up Sentry for error tracking
- [ ] Set up health monitoring
- [ ] Set up database backups
- [ ] Test monitoring alerts

---

## Production Checklist ✅

**Before going live:**

- [ ] All Phase 1-5 tasks completed
- [ ] All security enhancements implemented
- [ ] All tests passing
- [ ] Production environment configured
- [ ] SSL certificate installed
- [ ] Monitoring and logging active
- [ ] Backup strategy in place
- [ ] Documentation updated
- [ ] Team trained on system
- [ ] Rollback plan prepared

---

## Progress Tracking

**Overall Progress:** 0 / 150+ tasks

**Phase 1:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Phase 2:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Phase 3:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Phase 4:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Phase 5:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Security:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**UI:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Testing:** ☐ Not Started | ◐ In Progress | ✓ Complete  
**Deployment:** ☐ Not Started | ◐ In Progress | ✓ Complete  

---

**Last Updated:** 2025-10-10  
**Next Review:** [Date]  
**Completed By:** [Name]

