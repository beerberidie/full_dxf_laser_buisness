# 🚀 PRODUCTION AUTOMATION - DEPLOYMENT GUIDE

**Date:** 2025-10-28  
**Status:** ✅ Implementation Complete - Ready for Deployment

---

## 📋 OVERVIEW

This guide provides step-by-step instructions for deploying the Production Automation system to your Laser OS application.

**What was implemented:**
- Phone Mode for operators
- Bell icon notification system
- Daily report generation
- Outbound client message drafts
- Background scheduler for automation
- RBAC (Role-Based Access Control)

---

## ✅ COMPLETED STEPS

### 1. Dependencies Installation ✅
```bash
pip install apscheduler pytz
```
**Status:** ✅ Already installed

### 2. Database Migration ✅
```bash
python migrations/production_automation_migration.py
```
**Status:** ✅ Migration completed successfully

**Backup created:** `data/laser_os.db.backup_20251028_093736`

**Changes applied:**
- Added `role`, `is_active_operator`, `display_name` to `users` table
- Added `stage`, `stage_last_updated` to `projects` table
- Added `started_at`, `ended_at`, `sheets_used`, `sheet_size`, `thickness_mm` to `laser_runs` table
- Added `sheet_size`, `thickness_mm` to `inventory_items` table
- Created `notifications` table
- Created `daily_reports` table
- Created `outbound_drafts` table
- Created `extra_operators` table

### 3. Code Implementation ✅
**Status:** ✅ All code files created and modified

**Files Created:** 24 files
**Files Modified:** 7 files

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Start the Application

**Option A: Development Mode (Recommended for Testing)**
```bash
# Activate virtual environment
venv\Scripts\activate

# Set environment to development
$env:FLASK_ENV = "development"

# Run the application
python run.py
```

**Option B: Production Mode**
```bash
# Activate virtual environment
venv\Scripts\activate

# Ensure production config is set in .env or environment variables:
# - SECRET_KEY (must be changed from default)
# - MAIL_USERNAME (for email functionality)
# - MAIL_PASSWORD (for email functionality)

# Run with production config
python wsgi.py
```

### Step 2: Verify Application Startup

Check the console output for:
```
[SCHEDULER] Background scheduler started
[SCHEDULER] Daily report generation: 07:30 SAST
[SCHEDULER] Project notifications: Every hour
[SCHEDULER] Low stock check: Every 6 hours
```

### Step 3: Initialize User Roles

**IMPORTANT:** Existing users need to have their roles set.

**Option A: Via Python Shell**
```python
from app import create_app, db
from app.models.auth import User

app = create_app('development')
with app.app_context():
    # Set admin role
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.role = 'admin'
        admin.display_name = 'Administrator'
    
    # Set manager role
    manager = User.query.filter_by(username='manager').first()
    if manager:
        manager.role = 'manager'
        manager.display_name = 'Manager Name'
    
    # Set operator role
    operator = User.query.filter_by(username='operator').first()
    if operator:
        operator.role = 'operator'
        operator.is_active_operator = True
        operator.display_name = 'Operator Name'
    
    db.session.commit()
    print("✅ User roles updated successfully")
```

**Option B: Via SQL (if you prefer)**
```sql
-- Set admin role
UPDATE users SET role = 'admin', display_name = 'Administrator' WHERE username = 'admin';

-- Set manager role
UPDATE users SET role = 'manager', display_name = 'Manager Name' WHERE username = 'manager';

-- Set operator role
UPDATE users SET role = 'operator', is_active_operator = 1, display_name = 'Operator Name' WHERE username = 'operator';
```

### Step 4: Test Phone Mode

1. Login as an operator user
2. You should be redirected to mode selection
3. Select "Phone Mode"
4. Verify you see the phone mode interface
5. Try starting a run (if you have projects ready to cut)

### Step 5: Test Notifications

1. Login as admin or manager
2. Click the bell icon in the header
3. Verify the notification dropdown appears
4. Create a test project in "QuotesAndApproval" stage
5. Wait for hourly notification job OR manually trigger evaluation
6. Verify notification appears

### Step 6: Test Daily Reports

1. Navigate to Reports → Daily Reports
2. Click "Generate Today's Report"
3. Verify report is generated
4. Check that it shows runs, materials, warnings

### Step 7: Test Drafts

1. Navigate to Communications → Drafts
2. Verify any auto-generated drafts appear
3. Try editing a draft
4. Mark a draft as sent

---

## 🔧 CONFIGURATION

### Scheduler Configuration

The scheduler runs three jobs:

1. **Daily Report Generation**
   - Time: 07:30 SAST (South African Standard Time)
   - Frequency: Daily
   - Function: Generates report for previous day

2. **Project Notification Evaluation**
   - Time: Every hour at :00
   - Frequency: Hourly
   - Function: Checks for overdue projects and creates notifications

3. **Low Stock Check**
   - Time: Every 6 hours
   - Frequency: Every 6 hours
   - Function: Checks inventory and creates low stock notifications

### Stage Escalation Time Limits

- **QuotesAndApproval:** 4 days
- **WaitingOnMaterial:** 2 days
- **Cutting:** 1 day
- **ReadyForPickup:** 2 days

### Role Permissions

**Operator:**
- Phone Mode only
- Cannot edit Presets or Inventory
- Can log production runs

**Manager:**
- Dashboard, Projects, Queue, Reports, Communications
- Can view Inventory but cannot edit
- Cannot edit Presets
- Can view notifications

**Admin:**
- Full access to all modules
- Can edit Presets and Inventory
- Can manage users and roles

---

## 🧪 TESTING CHECKLIST

### Phone Mode Testing
- [ ] Login as operator redirects to mode selection
- [ ] Can select Phone Mode
- [ ] Phone mode shows active jobs
- [ ] Can start a run
- [ ] Run timer displays correctly
- [ ] Can end run with sheets used
- [ ] Inventory deducts correctly after run

### Notification Testing
- [ ] Bell icon appears in header
- [ ] Notification count badge shows correct count
- [ ] Dropdown shows unresolved notifications
- [ ] Can mark notification as resolved
- [ ] Auto-clear works when condition resolves
- [ ] Stage escalation creates notifications

### Daily Report Testing
- [ ] Can manually generate report
- [ ] Report shows correct data (runs, materials, warnings)
- [ ] Report list displays all reports
- [ ] Can view individual report
- [ ] Print functionality works

### Drafts Testing
- [ ] Drafts list shows pending and sent
- [ ] Can edit draft
- [ ] Can mark draft as sent
- [ ] Can delete draft
- [ ] Auto-generated drafts appear for overdue projects

### Scheduler Testing
- [ ] Scheduler starts on app startup
- [ ] Daily report generates at 07:30 SAST
- [ ] Hourly notification evaluation runs
- [ ] Low stock check runs every 6 hours

---

## 🐛 TROUBLESHOOTING

### Issue: Scheduler not starting
**Solution:** Check that APScheduler and pytz are installed:
```bash
pip install apscheduler pytz
```

### Issue: Database errors about missing columns
**Solution:** Run the migration script:
```bash
python migrations/production_automation_migration.py
```

### Issue: Users can't access certain features
**Solution:** Verify user roles are set correctly (see Step 3)

### Issue: Notifications not appearing
**Solution:** 
1. Check that projects have `stage` and `stage_last_updated` set
2. Wait for hourly notification job or manually trigger
3. Verify notification count API endpoint works: `/notifications/count`

### Issue: Phone mode not showing
**Solution:**
1. Verify user has `role = 'operator'`
2. Check that phone blueprint is registered
3. Verify templates exist in `app/templates/phone/`

---

## 📊 MONITORING

### Check Scheduler Status

Look for these log messages in console:
```
[SCHEDULER] Background scheduler started
[SCHEDULER] Daily report generation: 07:30 SAST
[SCHEDULER] Project notifications: Every hour
[SCHEDULER] Low stock check: Every 6 hours
```

### Check Notification Count

API endpoint: `GET /notifications/count`

Returns:
```json
{
  "count": 5
}
```

### Check Daily Report Generation

Check `daily_reports` table:
```sql
SELECT * FROM daily_reports ORDER BY report_date DESC LIMIT 5;
```

---

## 🔄 ROLLBACK PROCEDURE

If you need to rollback the changes:

1. **Stop the application**

2. **Restore database from backup:**
```bash
# Backup is at: data/laser_os.db.backup_20251028_093736
copy data\laser_os.db.backup_20251028_093736 data\laser_os.db
```

3. **Revert code changes** (if needed)

---

## 📚 NEXT STEPS

After successful deployment:

1. **User Training**
   - Train operators on Phone Mode
   - Train managers on notification system
   - Train admins on daily reports and drafts

2. **Data Population**
   - Set project stages for existing projects
   - Set user roles for all users
   - Configure inventory sheet sizes and thicknesses

3. **Monitoring**
   - Monitor scheduler logs
   - Check daily report generation
   - Verify notification accuracy

4. **Optional Enhancements** (Future)
   - Automated message templates triggered by milestones
   - Inbound email parsing
   - User-specific communication routing
   - Automatic queue addition when POP received

---

## ✅ DEPLOYMENT COMPLETE

Once all steps are completed and tested, the Production Automation system is fully deployed and operational!

**Support:** Refer to `docs/PRODUCTION_AUTOMATION_IMPLEMENTATION_PLAN.md` for technical details.

