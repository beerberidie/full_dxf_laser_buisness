# 📋 MANUAL TESTING CHECKLIST

This checklist guides you through manually testing all Production Automation features in the browser.

---

## 🚀 BEFORE YOU START

1. **Restart the Flask application** to ensure all fixes are loaded:
   ```bash
   # Kill any running Flask processes
   # Then start fresh:
   python run.py
   ```

2. **Open browser** to: `http://127.0.0.1:5000`

3. **Have these test users ready:**
   - **Admin:** garason / (password)
   - **Manager:** kieran / (password)
   - **Manager:** dalan / (password)
   - **Operator:** operator1 / (password)

---

## ✅ TEST 1: DAILY REPORTS

**Login as:** garason (admin) or kieran/dalan (manager)

### Steps:
1. Navigate to `/reports/daily`
2. **Verify:** You see the "Daily Reports" page
3. **Verify:** You see a "Generate Daily Report" button at the top
4. Click "Generate Daily Report"
5. **Verify:** Success message appears
6. **Verify:** New report appears in the list
7. Click on the report to view details
8. **Verify:** Report shows these fields:
   - Report Date
   - Runs Count
   - Total Sheets Used
   - Total Parts Produced
   - Total Cut Time (minutes)
   - Report Body (detailed text)

### Expected Results:
- ✅ Generate button is visible
- ✅ Report is created successfully
- ✅ All statistics fields are displayed
- ✅ Report body contains formatted text

### Current Status:
- Report will show 0 runs, 0 sheets, 0 parts (expected - no laser runs yet)
- This is normal for a new system

---

## ✅ TEST 2: NOTIFICATION BELL ICON

**Login as:** garason (admin) or kieran/dalan (manager)

### Steps:
1. Select "PC Mode" from the mode switcher
2. **Verify:** Bell icon appears in top-right header
3. **Verify:** Bell icon shows a count badge (may be 0)
4. Click the bell icon
5. **Verify:** Dropdown opens showing notifications
6. **Verify:** Dropdown shows "No notifications" (expected - projects are 0 days in stage)
7. Click the bell icon again
8. **Verify:** Dropdown closes

### Expected Results:
- ✅ Bell icon is visible for admin/manager users
- ✅ Bell icon has count badge
- ✅ Dropdown opens and closes on click
- ✅ Dropdown shows notification list or "No notifications"

### Current Status:
- No notifications will be shown (expected - all projects just got stages populated)
- Notifications will appear after projects exceed stage time limits

---

## ✅ TEST 3: PHONE MODE (Operator View)

**Login as:** operator1 (operator)

### Steps:
1. Select "Phone Mode" from the mode switcher
2. **Verify:** You see the Phone Mode interface
3. **Verify:** Interface is mobile-friendly (large buttons, simple layout)
4. **Verify:** You see a list of projects available to cut
5. **Verify:** Each project shows:
   - Project code
   - Client name
   - Description
   - "Start Run" button

### Expected Results:
- ✅ Phone Mode interface loads
- ✅ Projects are listed
- ✅ Interface is touch-friendly
- ✅ No bell icon (operators don't use notifications)

### Current Status:
- Projects in "ReadyToCut" or "Cutting" stages will appear
- Currently 0 projects in these stages (all are Complete or QuotesAndApproval)

---

## ✅ TEST 4: START AND END LASER RUN

**Login as:** operator1 (operator)  
**Prerequisites:** Need a project in "ReadyToCut" stage

### Steps:
1. In Phone Mode, find a project with "Start Run" button
2. Click "Start Run"
3. **Verify:** Run starts successfully
4. **Verify:** You see the active run screen with:
   - Project details
   - Timer showing elapsed time
   - "End Run" button
5. Click "End Run"
6. **Verify:** Form appears asking for:
   - Sheets used
   - Parts produced
   - Notes (optional)
7. Fill in the form and submit
8. **Verify:** Run ends successfully
9. **Verify:** You return to the project list

### Expected Results:
- ✅ Run starts without errors
- ✅ Active run screen shows project details
- ✅ Timer updates in real-time
- ✅ End run form appears
- ✅ Run is saved to database

### Current Status:
- Need to manually change a project to "ReadyToCut" stage first
- Or create a new project and advance it through stages

---

## ✅ TEST 5: NOTIFICATIONS PAGE

**Login as:** garason (admin) or kieran/dalan (manager)

### Steps:
1. Navigate to `/notifications/`
2. **Verify:** You see the "Notifications" page
3. **Verify:** Page shows notification list (may be empty)
4. **Verify:** Page has filter options:
   - All / Active / Resolved
   - Notification type filters

### Expected Results:
- ✅ Notifications page loads
- ✅ Filter options are visible
- ✅ List shows notifications or "No notifications"

### Current Status:
- No notifications yet (expected)
- Notifications will appear when:
  - Projects exceed stage time limits
  - Inventory items are low stock
  - Presets are missing

---

## ✅ TEST 6: COMMUNICATION DRAFTS

**Login as:** garason (admin) or kieran/dalan (manager)

### Steps:
1. Navigate to `/communications/drafts`
2. **Verify:** You see the "Outbound Drafts" page
3. **Verify:** Page shows draft list (may be empty)
4. **Verify:** Each draft shows:
   - Client name
   - Subject
   - Template type
   - Created date
   - Actions (Edit, Send, Delete)

### Expected Results:
- ✅ Drafts page loads
- ✅ Draft list is displayed
- ✅ Action buttons are visible

### Current Status:
- No drafts yet (expected)
- Drafts are auto-generated when:
  - Project reaches "Complete" stage (Collection Ready message)
  - POP is received (Order Confirmed message)

---

## ✅ TEST 7: OPERATOR DROPDOWNS

**Login as:** garason (admin)

### Steps:
1. Navigate to any page with operator selection (e.g., create laser run manually)
2. **Verify:** Operator dropdown shows all active operators:
   - garason (Garason)
   - kieran (Kieran)
   - dalan (Dalan)
   - operator1 (Operator 1)
   - viewer1 (Viewer 1)

### Expected Results:
- ✅ All 5 users appear in operator dropdown
- ✅ Display names are shown correctly
- ✅ Only users with `is_active_operator=True` appear

### Current Status:
- All 5 users have `is_active_operator=True`
- All should appear in dropdowns

---

## 🎯 TESTING PRIORITIES

### High Priority (Test First)
1. ✅ Daily Reports - Verify generate button and report display
2. ✅ Notification Bell - Verify icon appears and dropdown works
3. ✅ Phone Mode - Verify interface loads for operators

### Medium Priority (Test After High)
4. ✅ Notifications Page - Verify page loads and filters work
5. ✅ Communication Drafts - Verify page loads

### Low Priority (Test When You Have Test Data)
6. ✅ Start/End Laser Run - Requires project in ReadyToCut stage
7. ✅ Operator Dropdowns - Test when creating laser runs

---

## 🐛 WHAT TO LOOK FOR

### Common Issues to Watch For:
- ❌ **500 Internal Server Error** - Indicates a Python exception
- ❌ **404 Not Found** - Route not registered correctly
- ❌ **Template Not Found** - Missing template file
- ❌ **Undefined Variable** - Missing context variable
- ❌ **Database Error** - Schema mismatch or missing column

### Good Signs:
- ✅ Pages load without errors
- ✅ Buttons and links work
- ✅ Data is displayed correctly
- ✅ Forms submit successfully
- ✅ Success/error messages appear

---

## 📝 REPORTING ISSUES

If you find any issues during manual testing, please report:

1. **What you were doing** (exact steps)
2. **What you expected** to happen
3. **What actually happened** (error message, wrong behavior, etc.)
4. **Which user** you were logged in as
5. **Screenshot** if possible

---

## ✅ COMPLETION CHECKLIST

Mark each test as you complete it:

- [ ] Test 1: Daily Reports
- [ ] Test 2: Notification Bell Icon
- [ ] Test 3: Phone Mode Interface
- [ ] Test 4: Start and End Laser Run
- [ ] Test 5: Notifications Page
- [ ] Test 6: Communication Drafts
- [ ] Test 7: Operator Dropdowns

---

**Happy Testing!** 🚀

If all tests pass, the Production Automation system is fully operational and ready for production use!

