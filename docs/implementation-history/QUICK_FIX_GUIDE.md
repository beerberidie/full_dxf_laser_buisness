# Quick Fix Guide - Project Status IntegrityError

## Problem
Getting this error when updating projects:
```
sqlite3.IntegrityError: CHECK constraint failed: status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled')
```

## Cause
Database CHECK constraint doesn't include new Phase 9 status values like 'Request'.

## Solution (2 minutes)

### Option 1: Automated Fix (Recommended)

```bash
# Run the migration script (includes automatic backup)
python scripts/apply_status_constraint_fix.py
```

Type `yes` when prompted. Done! ✅

### Option 2: Manual SQL Fix

If you prefer to run SQL directly:

```bash
# 1. Backup your database first!
cp instance/laser_os.db instance/laser_os.db.backup

# 2. Apply the migration
sqlite3 instance/laser_os.db < migrations/schema_v9_1_fix_project_status_constraint.sql
```

## Verify It Worked

1. Try creating a new project with status "Request"
2. Should save without errors ✅

## What Changed

The database now accepts these new status values:
- ✅ Request
- ✅ Quote & Approval
- ✅ Approved (POP Received)
- ✅ Queued (Scheduled for Cutting)

Plus all the original statuses still work.

## Need Help?

See detailed documentation: `docs/fixes/PROJECT_STATUS_CONSTRAINT_FIX.md`

