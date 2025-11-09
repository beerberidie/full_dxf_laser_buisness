# COMPREHENSIVE BROWSER TESTING CHECKLIST
**Date:** 2025-10-28  
**Purpose:** Verify all Production Automation features work correctly in browser  
**Estimated Total Time:** 90 minutes

---

## SETUP INSTRUCTIONS

### Prerequisites:
1. Start Flask application: `python run.py`
2. Open browser and navigate to: `http://127.0.0.1:5000`
3. Login with admin credentials
4. Have database with test data (projects, inventory, notifications)

---

## TEST 1: DAILY REPORT SECTION ON REPORTS PAGE ⭐ CRITICAL
**Priority:** CRITICAL (Just Fixed)  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Navigate to Reports page**
   - URL: `http://127.0.0.1:5000/reports`
   - Expected: Page loads successfully

2. **Verify 5 report cards are displayed**
   - Expected cards:
     1. 📈 Production Summary
     2. ⚡ Efficiency Metrics
     3. 📦 Inventory Report
     4. 👥 Client & Project Report
     5. 📋 Daily Report ← **NEW CARD**

3. **Verify Daily Report card content**
   - Expected title: "📋 Daily Report"
   - Expected description: "View automated daily operational briefs generated at 07:30 SAST."
   - Expected bullet points:
     - What needs to be cut today
     - What material needs to be ordered
     - Which clients need to be notified
     - Blocked projects requiring attention
   - Expected buttons:
     - "View Daily Reports" (blue button)
     - "Generate Now" (green button)

4. **Test "View Daily Reports" button**
   - Click: "View Daily Reports"
   - Expected URL: `http://127.0.0.1:5000/reports/daily`
   - Expected: List of daily reports displayed

5. **Test "Generate Now" button**
   - Click: "Generate Now"
   - Expected: Flash message "Daily report generated for YYYY-MM-DD"
   - Expected: Redirect to specific daily report view
   - Expected URL: `http://127.0.0.1:5000/reports/daily/YYYY-MM-DD`

### Success Criteria:
- ✅ All 5 cards visible on Reports page
- ✅ Daily Report card displays correctly
- ✅ Both buttons work and navigate correctly
- ✅ No console errors

---

## TEST 2: DAILY REPORT .TXT EXPORT ⭐ CRITICAL
**Priority:** CRITICAL (Just Fixed)  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Navigate to Daily Reports list**
   - URL: `http://127.0.0.1:5000/reports/daily`
   - Expected: List of daily reports displayed

2. **Click on a specific report**
   - Click: Any report date link
   - Expected URL: `http://127.0.0.1:5000/reports/daily/YYYY-MM-DD`
   - Expected: Report details displayed

3. **Verify "Download as .txt" button exists**
   - Expected: Green "Download as .txt" button visible
   - Expected: Button positioned before "Print" button
   - Expected: Download icon (📥) displayed

4. **Test download functionality**
   - Click: "Download as .txt"
   - Expected: File download starts
   - Expected filename: `DailyReport_YYYY-MM-DD.txt`
   - Expected: File downloads to browser's download folder

5. **Verify downloaded file content**
   - Open: Downloaded .txt file in text editor
   - Expected: File contains report body text
   - Expected: Text is readable (UTF-8 encoding)
   - Expected: Content matches what's displayed on web page

### Success Criteria:
- ✅ Download button visible and styled correctly
- ✅ File downloads with correct filename
- ✅ File content matches report body
- ✅ No errors during download

---

## TEST 3: DASHBOARD ATTENTION CARDS
**Priority:** HIGH  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Navigate to Dashboard**
   - URL: `http://127.0.0.1:5000/dashboard`
   - Expected: Dashboard loads successfully

2. **Verify 4 attention cards are displayed**
   - Expected cards at top of page:
     1. 📦 Low Stock (X items)
     2. ⏳ Waiting on Approval (X projects)
     3. 📋 Ready for Pickup (X projects)
     4. 🚧 Blocked Projects (X projects)

3. **Verify card counts are correct**
   - Compare counts with actual data:
     - Low Stock: Count unresolved `low_stock` notifications
     - Waiting on Approval: Count unresolved `approval_wait` notifications
     - Ready for Pickup: Count unresolved `pickup_wait` notifications
     - Blocked Projects: Count unresolved `material_block` notifications

4. **Test card links**
   - Click: "View Details" on Low Stock card
   - Expected: Navigate to filtered notifications view
   - Expected URL: `http://127.0.0.1:5000/notifications?type=low_stock`
   - Repeat for other cards

5. **Verify card styling**
   - Expected: Warning/alert styling (yellow/orange background)
   - Expected: Cards stand out visually
   - Expected: Responsive layout on mobile

### Success Criteria:
- ✅ All 4 attention cards visible
- ✅ Counts match database data
- ✅ Links navigate to correct filtered views
- ✅ Styling is visually distinct

---

## TEST 4: BELL ICON NOTIFICATIONS
**Priority:** HIGH  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Verify bell icon in header**
   - Expected: Bell icon (🔔) visible in top navigation
   - Expected: Badge showing count of unresolved notifications
   - Expected: Badge color indicates urgency (red if > 0)

2. **Test bell icon click**
   - Click: Bell icon
   - Expected: Dropdown menu appears
   - Expected: List of recent unresolved notifications
   - Expected: Each notification shows:
     - Type icon
     - Message text
     - Timestamp
     - Link to related item

3. **Test notification link**
   - Click: Any notification in dropdown
   - Expected: Navigate to related project/inventory item
   - Expected: Notification context is clear

4. **Test "View All Notifications" link**
   - Click: "View All Notifications" at bottom of dropdown
   - Expected URL: `http://127.0.0.1:5000/notifications`
   - Expected: Full notifications list displayed

5. **Test resolve notification**
   - Navigate to: `http://127.0.0.1:5000/notifications`
   - Click: "Resolve" button on any notification
   - Expected: Notification marked as resolved
   - Expected: Notification removed from list
   - Expected: Bell icon count decrements

### Success Criteria:
- ✅ Bell icon displays with correct count
- ✅ Dropdown shows recent notifications
- ✅ Links navigate correctly
- ✅ Resolve functionality works

---

## TEST 5: PHONE MODE COMPLETE WORKFLOW
**Priority:** HIGH  
**Estimated Time:** 15 minutes

### Test Steps:
1. **Login as operator**
   - Logout current user
   - Login with operator credentials
   - Expected: Redirect to mode selection page

2. **Select Phone Mode**
   - URL: `http://127.0.0.1:5000/auth/select-mode`
   - Click: "Phone Mode" button
   - Expected URL: `http://127.0.0.1:5000/phone/home`
   - Expected: List of active projects/queue items

3. **Start a run**
   - Click: "Start Run" on any project
   - Expected: Form to enter run details
   - Fill in:
     - Material type
     - Thickness
     - Sheet size
     - Estimated sheets
   - Click: "Start Run"
   - Expected: Run created with status="running"
   - Expected: Redirect to active run view

4. **View active run**
   - Expected URL: `http://127.0.0.1:5000/phone/run/<run_id>`
   - Expected: Run details displayed
   - Expected: Preset information shown (read-only)
   - Expected: "End Run" button visible

5. **End run**
   - Enter: Actual sheets used
   - Enter: Parts produced
   - Enter: Any notes
   - Click: "End Run"
   - Expected: Run status updated to "completed"
   - Expected: Inventory deducted by sheets_used
   - Expected: Project stage updated
   - Expected: Redirect to phone home

6. **Verify inventory deduction**
   - Navigate to: `http://127.0.0.1:5000/inventory`
   - Find: Material/thickness/size used in run
   - Expected: Quantity decreased by sheets_used
   - Expected: Low stock notification created if below reorder level

### Success Criteria:
- ✅ Mode selection works
- ✅ Phone Mode UI is mobile-friendly
- ✅ Run start/end workflow completes
- ✅ Inventory deducted correctly
- ✅ Project stage updated
- ✅ Notifications created if needed

---

## TEST 6: DAILY REPORT AUTO-GENERATION
**Priority:** MEDIUM  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Check scheduler status**
   - Verify: APScheduler is running
   - Expected: Scheduler logs show job scheduled for 07:30 SAST

2. **Manual generation test**
   - Navigate to: `http://127.0.0.1:5000/reports`
   - Click: "Generate Now" on Daily Report card
   - Expected: Report generated for current date
   - Expected: Flash message confirms generation

3. **Verify report content**
   - Expected sections in report:
     - **What needs to be cut today:** Projects in ReadyToCut stage
     - **What material needs to be ordered:** Low stock items
     - **Which clients need to be notified:** Overdue projects
     - **Blocked projects:** Projects in WaitingOnMaterial stage

4. **Verify report saved to database**
   - Navigate to: `http://127.0.0.1:5000/reports/daily`
   - Expected: New report appears in list
   - Expected: Report date is today
   - Expected: Generated timestamp is recent

5. **Test duplicate generation**
   - Click: "Generate Now" again
   - Expected: Either:
     - New report replaces old one for same date, OR
     - Error message "Report already exists for today"

### Success Criteria:
- ✅ Manual generation works
- ✅ Report contains all required sections
- ✅ Report saved to database
- ✅ Duplicate handling works correctly

---

## TEST 7: COMMUNICATIONS DRAFTS AUTO-GENERATION
**Priority:** MEDIUM  
**Estimated Time:** 15 minutes

### Test Steps:
1. **Create test project in QuotesAndApproval stage**
   - Navigate to: `http://127.0.0.1:5000/projects/new`
   - Create: New project
   - Set: stage = "QuotesAndApproval"
   - Set: stage_last_updated = 5 days ago (manually in DB or via Python shell)

2. **Trigger notification evaluation**
   - Option A: Wait for scheduler to run
   - Option B: Manually trigger via Python shell:
     ```python
     from app.services.notification_logic import evaluate_notifications_for_project
     from app.models import Project
     project = Project.query.filter_by(stage='QuotesAndApproval').first()
     evaluate_notifications_for_project(project)
     ```

3. **Verify notification created**
   - Navigate to: `http://127.0.0.1:5000/notifications`
   - Expected: `approval_wait` notification for project
   - Expected: Message indicates project overdue

4. **Verify draft auto-generated**
   - Navigate to: `http://127.0.0.1:5000/communications/drafts`
   - Expected: Draft message for client
   - Expected: Draft contains:
     - Project name
     - Client name
     - Polite follow-up message
     - Channel hint (WhatsApp/Email)

5. **Test mark draft as sent**
   - Click: "Mark as Sent" on draft
   - Expected: Draft marked as sent
   - Expected: sent_at timestamp updated
   - Expected: Draft removed from pending list

6. **Test edit draft**
   - Create: Another overdue project
   - Wait: For draft to be generated
   - Click: "Edit" on draft
   - Modify: Message text
   - Click: "Save"
   - Expected: Draft updated with new text

7. **Test delete draft**
   - Click: "Delete" on any draft
   - Expected: Confirmation prompt
   - Confirm: Delete
   - Expected: Draft removed from database

### Success Criteria:
- ✅ Overdue projects trigger notifications
- ✅ Drafts auto-generated for overdue stages
- ✅ Draft content is appropriate
- ✅ Mark as sent works
- ✅ Edit and delete work

---

## TEST 8: INVENTORY DEDUCTION ON RUN COMPLETION
**Priority:** MEDIUM  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Record initial inventory**
   - Navigate to: `http://127.0.0.1:5000/inventory`
   - Find: Material you'll use in test run
   - Record: Current quantity_on_hand
   - Example: Mild Steel, 3mm, 1220x2440 = 50 sheets

2. **Start and complete a run**
   - Follow: Phone Mode workflow (Test 5)
   - Use: 5 sheets in the run
   - Complete: Run successfully

3. **Verify inventory deducted**
   - Navigate to: `http://127.0.0.1:5000/inventory`
   - Find: Same material
   - Expected: quantity_on_hand = 45 (50 - 5)

4. **Test low stock notification**
   - Set: reorder_level = 46 (above current quantity)
   - Complete: Another run using 1 sheet
   - Expected: quantity_on_hand = 44
   - Expected: Low stock notification created
   - Navigate to: `http://127.0.0.1:5000/notifications`
   - Expected: `low_stock` notification for this material

5. **Test inventory underflow protection**
   - Set: quantity_on_hand = 2
   - Complete: Run using 5 sheets
   - Expected: Inventory deducts to 0 (not negative)
   - Expected: Low stock notification created

### Success Criteria:
- ✅ Inventory deducts correctly
- ✅ Low stock notifications created
- ✅ Underflow protection works
- ✅ Inventory transactions logged

---

## TEST 9: STAGE ESCALATION AND NOTIFICATION CREATION
**Priority:** MEDIUM  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Test QuotesAndApproval escalation (> 4 days)**
   - Create: Project in QuotesAndApproval stage
   - Set: stage_last_updated = 5 days ago
   - Trigger: Notification evaluation
   - Expected: `approval_wait` notification created
   - Expected: Draft message auto-generated

2. **Test WaitingOnMaterial escalation (> 2 days)**
   - Create: Project in WaitingOnMaterial stage
   - Set: stage_last_updated = 3 days ago
   - Trigger: Notification evaluation
   - Expected: `material_block` notification created

3. **Test Cutting escalation (> 1 day)**
   - Create: Project in Cutting stage
   - Set: stage_last_updated = 2 days ago
   - Trigger: Notification evaluation
   - Expected: `cutting_stall` notification created

4. **Test ReadyForPickup escalation (> 2 days)**
   - Create: Project in ReadyForPickup stage
   - Set: stage_last_updated = 3 days ago
   - Trigger: Notification evaluation
   - Expected: `pickup_wait` notification created
   - Expected: Draft message auto-generated

5. **Test auto-clear when stage changes**
   - Change: Project stage from QuotesAndApproval to Cutting
   - Trigger: Notification evaluation
   - Expected: Old `approval_wait` notification auto-cleared
   - Expected: resolved = True, auto_cleared = True

### Success Criteria:
- ✅ All stage escalations trigger correctly
- ✅ Timing limits match blueprint (4d, 2d, 1d, 2d)
- ✅ Notifications created with correct type
- ✅ Auto-clear works when stage changes

---

## TEST 10: PRESET AUTO-ATTACH AND READ-ONLY IN PHONE MODE
**Priority:** LOW  
**Estimated Time:** 10 minutes

### Test Steps:
1. **Create preset**
   - Navigate to: `http://127.0.0.1:5000/presets`
   - Create: New preset
   - Set: material_type = "Mild Steel"
   - Set: thickness_mm = "3.0"
   - Set: Other preset parameters

2. **Create project with matching material**
   - Navigate to: `http://127.0.0.1:5000/projects/new`
   - Create: New project
   - Set: material_type = "Mild Steel"
   - Set: thickness_mm = "3.0"
   - Expected: Preset auto-attached to project

3. **Verify preset in Phone Mode**
   - Login: As operator
   - Select: Phone Mode
   - Start: Run on project with preset
   - Expected: Preset information displayed
   - Expected: Preset fields are read-only (no edit buttons)
   - Expected: Preset parameters visible (speed, power, frequency, etc.)

4. **Test preset edit protection**
   - Try: Accessing preset edit URL directly
   - URL: `http://127.0.0.1:5000/presets/<id>/edit`
   - Expected: Access denied (requires admin role)
   - Expected: Redirect or error message

### Success Criteria:
- ✅ Preset auto-attaches to project
- ✅ Preset displays in Phone Mode
- ✅ Preset is read-only in Phone Mode
- ✅ Edit protection works

---

## SUMMARY CHECKLIST

### Critical Tests (Must Pass):
- [ ] Test 1: Daily Report Section on Reports Page
- [ ] Test 2: Daily Report .txt Export
- [ ] Test 3: Dashboard Attention Cards
- [ ] Test 4: Bell Icon Notifications

### High Priority Tests:
- [ ] Test 5: Phone Mode Complete Workflow
- [ ] Test 6: Daily Report Auto-Generation
- [ ] Test 7: Communications Drafts Auto-Generation

### Medium Priority Tests:
- [ ] Test 8: Inventory Deduction on Run Completion
- [ ] Test 9: Stage Escalation and Notification Creation
- [ ] Test 10: Preset Auto-Attach and Read-Only

---

## ISSUE TRACKING

### Issues Found During Testing:

| Test # | Issue Description | Severity | Status |
|--------|------------------|----------|--------|
|        |                  |          |        |

### Notes:
- Record any issues found during testing
- Include screenshots if helpful
- Note browser and OS used for testing

---

**END OF BROWSER TESTING CHECKLIST**

