# COMPREHENSIVE BROWSER TESTING SCRIPT
## Production Automation Blueprint Verification

**Date:** 2025-10-28  
**Purpose:** Manual browser testing to verify ALL Production Automation features work correctly

---

## PRE-TESTING SETUP

1. **Start the Flask application:**
   ```bash
   python run.py
   ```

2. **Open browser to:** `http://localhost:5000`

3. **Test users available:**
   - Admin user: `admin` / (password from database)
   - Manager user: (check database for manager role)
   - Operator user: (check database for operator role)

---

## TEST PHASE 1: AUTHENTICATION & MODE SELECTION

### Test 1.1: Login Flow
- [ ] Navigate to `http://localhost:5000`
- [ ] Enter valid credentials
- [ ] Click "Login"
- [ ] **EXPECTED:** Redirected to Mode Selection page (`/auth/select-mode`)
- [ ] **VERIFY:** Page shows two large cards: "PC Mode" and "Phone Mode"
- [ ] **VERIFY:** PC Mode card lists features (Dashboard, Clients, Projects, etc.)
- [ ] **VERIFY:** Phone Mode card lists features (Production Run Logging, etc.)

### Test 1.2: PC Mode Selection
- [ ] Click "PC Mode" button
- [ ] **EXPECTED:** Redirected to Dashboard (`/dashboard` or `/`)
- [ ] **VERIFY:** Full sidebar navigation visible
- [ ] **VERIFY:** Dashboard content loads

### Test 1.3: Phone Mode Selection
- [ ] Logout and login again
- [ ] On Mode Selection page, click "Phone Mode"
- [ ] **EXPECTED:** Redirected to Phone Home (`/phone/home`)
- [ ] **VERIFY:** Mobile-optimized UI loads
- [ ] **VERIFY:** Shows list of jobs ready to cut

### Test 1.4: Session Persistence
- [ ] Select PC Mode
- [ ] Navigate to different pages (Clients, Projects, etc.)
- [ ] **VERIFY:** UI mode stays in PC mode (sidebar visible)
- [ ] Logout and login, select Phone Mode
- [ ] **VERIFY:** UI mode stays in Phone mode (mobile UI)

---

## TEST PHASE 2: PHONE MODE PRODUCTION LOGGING

### Test 2.1: View Available Jobs
- [ ] Login and select Phone Mode
- [ ] Navigate to `/phone/home`
- [ ] **VERIFY:** Shows list of projects with status "Queued" or "Ready to Cut"
- [ ] **VERIFY:** Each job shows: Project name, Client, Material/Thickness/Sheet Size
- [ ] **VERIFY:** Each job has "Start Run" button

### Test 2.2: Start a Production Run
- [ ] Click "Start Run" on a job
- [ ] **EXPECTED:** Redirected to run active page
- [ ] **VERIFY:** Shows run details (project, operator, start time)
- [ ] **VERIFY:** Shows form to end run with fields:
   - Sheets Used (number input)
   - Notes (textarea)
   - "End Run" button

### Test 2.3: End a Production Run
- [ ] Fill in "Sheets Used" (e.g., 3)
- [ ] Add notes (e.g., "Test run completed successfully")
- [ ] Click "End Run"
- [ ] **EXPECTED:** Run marked as completed
- [ ] **VERIFY:** Redirected back to `/phone/home`
- [ ] **VERIFY:** Inventory deducted by sheets used
- [ ] **VERIFY:** LaserRun record created with ended_at timestamp

### Test 2.4: Verify Inventory Deduction
- [ ] Navigate to `/inventory` (PC Mode)
- [ ] Find the material/thickness/sheet size used in the run
- [ ] **VERIFY:** Quantity decreased by sheets used
- [ ] Check inventory transactions
- [ ] **VERIFY:** Transaction record shows deduction with reference to LaserRun

---

## TEST PHASE 3: NOTIFICATIONS SYSTEM (BELL ICON)

### Test 3.1: Bell Icon Visibility
- [ ] Login in PC Mode
- [ ] Look at top navigation bar
- [ ] **VERIFY:** Bell icon (🔔) visible in header
- [ ] **VERIFY:** Badge shows count of unresolved notifications (if any exist)

### Test 3.2: View Notifications
- [ ] Click bell icon
- [ ] **EXPECTED:** Dropdown/overlay opens showing notification list
- [ ] **VERIFY:** Shows notifications with:
   - Type (approval_wait, material_block, low_stock, etc.)
   - Message
   - Link to related project/inventory item
   - "Resolve" button

### Test 3.3: Resolve Notification
- [ ] Click "Resolve" on a notification
- [ ] **EXPECTED:** Notification marked as resolved
- [ ] **VERIFY:** Notification removed from list
- [ ] **VERIFY:** Bell icon count decreases

### Test 3.4: Auto-Generated Notifications
- [ ] Create a project and set stage to "QuotesAndApproval"
- [ ] Set `stage_last_updated` to 5 days ago (manually in database or wait)
- [ ] Run notification evaluation (scheduler or manual trigger)
- [ ] **VERIFY:** New notification created with type "approval_wait"
- [ ] **VERIFY:** Notification appears in bell dropdown

---

## TEST PHASE 4: DAILY REPORT GENERATION

### Test 4.1: View Daily Reports List
- [ ] Navigate to `/reports/daily`
- [ ] **VERIFY:** Page shows list of previously generated daily reports
- [ ] **VERIFY:** Each report shows: Date, Runs Count, Sheets Used, Parts Produced
- [ ] **VERIFY:** "Generate Daily Report" button visible (for admin/manager roles)

### Test 4.2: Manual Report Generation
- [ ] Click "Generate Daily Report" button
- [ ] **EXPECTED:** New report generated
- [ ] **VERIFY:** Report appears in list
- [ ] **VERIFY:** Report shows:
   - Production summary (runs, sheets, parts, cut time)
   - Blocked projects (waiting on material)
   - Clients to notify (approval wait, pickup wait)
   - Low stock items

### Test 4.3: View Report Details
- [ ] Click on a report to view details
- [ ] **VERIFY:** Full report body displayed
- [ ] **VERIFY:** Report includes all sections:
   - PRODUCTION SUMMARY
   - BLOCKED PROJECTS
   - CLIENTS TO NOTIFY
   - LOW STOCK ITEMS

### Test 4.4: Export Report as .txt
- [ ] On report detail page, look for "Export" or "Download" button
- [ ] Click export button
- [ ] **EXPECTED:** `.txt` file downloads
- [ ] **VERIFY:** File contains plain text version of report
- [ ] **VERIFY:** File is readable and properly formatted

### Test 4.5: Scheduled Report Generation
- [ ] Check scheduler logs for "Generate Daily Report" job
- [ ] **VERIFY:** Job scheduled for 07:30 SAST (Africa/Johannesburg timezone)
- [ ] **VERIFY:** Job runs automatically at scheduled time
- [ ] **VERIFY:** New report created in database

---

## TEST PHASE 5: COMMUNICATIONS DRAFTS

### Test 5.1: View Drafts List
- [ ] Navigate to `/comms` or `/communications`
- [ ] Look for "Drafts" tab or section
- [ ] **VERIFY:** Shows list of auto-generated draft messages
- [ ] **VERIFY:** Each draft shows: Client, Channel (WhatsApp/Email), Preview, Status (Sent/Unsent)

### Test 5.2: View Draft Details
- [ ] Click on a draft to view details
- [ ] **VERIFY:** Shows full message body
- [ ] **VERIFY:** Shows client contact info
- [ ] **VERIFY:** Shows channel hint (WhatsApp/Email)
- [ ] **VERIFY:** "Mark as Sent" button visible

### Test 5.3: Mark Draft as Sent
- [ ] Click "Mark as Sent" button
- [ ] **EXPECTED:** Draft marked as sent
- [ ] **VERIFY:** `sent` field set to True
- [ ] **VERIFY:** `sent_at` timestamp recorded
- [ ] **VERIFY:** Draft moves to "Sent" section or shows "Sent" badge

### Test 5.4: Auto-Generated Drafts
- [ ] Complete a production run
- [ ] **VERIFY:** Draft message auto-generated for client (e.g., "Your order is ready for pickup")
- [ ] **VERIFY:** Draft appears in Communications drafts list

---

## TEST PHASE 6: PROJECT STAGE TRACKING

### Test 6.1: View Project Stages
- [ ] Navigate to `/projects`
- [ ] Click on a project to view details
- [ ] **VERIFY:** Project shows current stage (QuotesAndApproval, WaitingOnMaterial, Cutting, etc.)
- [ ] **VERIFY:** Shows "Stage Last Updated" timestamp

### Test 6.2: Stage Transitions
- [ ] Edit a project and change stage
- [ ] **EXPECTED:** `stage_last_updated` timestamp updates to current time
- [ ] **VERIFY:** Stage change recorded
- [ ] **VERIFY:** Notifications re-evaluated for new stage

### Test 6.3: Stage Escalation Limits
- [ ] Create test project in "QuotesAndApproval" stage
- [ ] Set `stage_last_updated` to 5 days ago
- [ ] Run notification evaluation
- [ ] **VERIFY:** Notification created (QuotesAndApproval limit is 4 days)
- [ ] **VERIFY:** Notification type is "approval_wait"

---

## TEST PHASE 7: SECURITY & RBAC

### Test 7.1: Admin Role Access
- [ ] Login as admin user
- [ ] **VERIFY:** Can access all pages (Dashboard, Clients, Projects, Queue, Inventory, Reports, Communications, Admin)
- [ ] **VERIFY:** Can edit Presets
- [ ] **VERIFY:** Can edit Inventory
- [ ] **VERIFY:** Can generate Daily Reports

### Test 7.2: Manager Role Access
- [ ] Login as manager user
- [ ] **VERIFY:** Can access Dashboard, Projects, Queue, Reports, Communications
- [ ] **VERIFY:** Can view Inventory and low stock
- [ ] **VERIFY:** CANNOT edit Presets
- [ ] **VERIFY:** Can generate Daily Reports

### Test 7.3: Operator Role Access
- [ ] Login as operator user
- [ ] **VERIFY:** Can access Phone Mode
- [ ] **VERIFY:** Can start/end production runs
- [ ] **VERIFY:** Can view presets (read-only)
- [ ] **VERIFY:** CANNOT edit Presets or Inventory
- [ ] **VERIFY:** CANNOT access Admin pages

---

## TEST PHASE 8: UI/UX ELEMENTS

### Test 8.1: Favicon
- [ ] Open application in browser
- [ ] Look at browser tab
- [ ] **VERIFY:** Custom favicon visible (laser cutting icon)
- [ ] **VERIFY:** Favicon shows on all pages

### Test 8.2: Sidebar Navigation
- [ ] Login in PC Mode
- [ ] **VERIFY:** Sidebar shows all navigation items:
   - Dashboard
   - Clients
   - Projects
   - Queue
   - Inventory
   - Reports
   - Communications
   - Admin (if admin/manager role)

### Test 8.3: Dashboard Attention Cards
- [ ] Navigate to Dashboard
- [ ] **VERIFY:** Shows attention cards for:
   - Low Stock items
   - Projects waiting on client approval
   - Projects ready for pickup
   - Projects blocked (waiting on material)
- [ ] **VERIFY:** Each card shows count and link to details

### Test 8.4: Responsive Design
- [ ] Resize browser window to mobile size
- [ ] **VERIFY:** UI adapts to mobile layout
- [ ] **VERIFY:** Phone Mode optimized for touch
- [ ] **VERIFY:** Buttons large enough for touch input

---

## TEST PHASE 9: DATA INTEGRITY

### Test 9.1: Project Stages Populated
- [ ] Navigate to `/projects`
- [ ] **VERIFY:** All projects have a stage assigned (not NULL)
- [ ] **VERIFY:** Stage values are valid (QuotesAndApproval, WaitingOnMaterial, Cutting, Complete)

### Test 9.2: User Roles Assigned
- [ ] Navigate to `/admin/users` (if admin)
- [ ] **VERIFY:** All users have roles assigned (admin, manager, operator)
- [ ] **VERIFY:** No users with NULL role

### Test 9.3: Inventory Items Exist
- [ ] Navigate to `/inventory`
- [ ] **VERIFY:** Inventory items exist for common materials
- [ ] **VERIFY:** Each item has: material_type, thickness_mm, sheet_size, quantity_on_hand, reorder_level

---

## ISSUES FOUND DURING TESTING

**Record any issues found here:**

| Test # | Issue Description | Severity | Expected | Actual |
|--------|------------------|----------|----------|--------|
|        |                  |          |          |        |

---

## TESTING SUMMARY

- **Total Tests:** ___
- **Passed:** ___
- **Failed:** ___
- **Blocked:** ___

**Overall Status:** ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

**Tester:** _______________  
**Date:** _______________  
**Notes:** _______________

