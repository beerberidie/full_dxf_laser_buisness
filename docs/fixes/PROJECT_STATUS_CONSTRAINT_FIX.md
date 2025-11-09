# Project Status CHECK Constraint Fix

## 🐛 Issue Summary

**Error:** `sqlite3.IntegrityError: CHECK constraint failed: status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled')`

**Root Cause:** Mismatch between the Project model's `VALID_STATUSES` and the database CHECK constraint.

---

## 📋 Problem Analysis

### What Happened

1. **Phase 9 Enhancement** added new project status values to the `Project` model:
   - `'Request'`
   - `'Quote & Approval'`
   - `'Approved (POP Received)'`
   - `'Queued (Scheduled for Cutting)'`

2. **Model Updated** (`app/models/business.py` lines 90-114):
   ```python
   # Status constants - Enhanced workflow for Phase 9
   STATUS_REQUEST = 'Request'
   STATUS_QUOTE_APPROVAL = 'Quote & Approval'
   STATUS_APPROVED_POP = 'Approved (POP Received)'
   STATUS_QUEUED = 'Queued (Scheduled for Cutting)'
   STATUS_IN_PROGRESS = 'In Progress'
   STATUS_COMPLETED = 'Completed'
   STATUS_CANCELLED = 'Cancelled'
   
   # Legacy status constants (for backward compatibility)
   STATUS_QUOTE = 'Quote'
   STATUS_APPROVED = 'Approved'
   
   VALID_STATUSES = [
       STATUS_REQUEST,
       STATUS_QUOTE_APPROVAL,
       STATUS_APPROVED_POP,
       STATUS_QUEUED,
       STATUS_IN_PROGRESS,
       STATUS_COMPLETED,
       STATUS_CANCELLED,
       # Legacy statuses
       STATUS_QUOTE,
       STATUS_APPROVED
   ]
   ```

3. **Database NOT Updated** - The Phase 9 migration (`migrations/schema_v9_project_enhancements.sql`) added new columns but **did NOT update the CHECK constraint**.

4. **Constraint Still Restricts** to old values only:
   ```sql
   CHECK (status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled'))
   ```

### Where the Error Occurs

The error occurs when trying to update a project with one of the new status values:

```python
# In app/routes/projects.py line 104
status = request.form.get('status', Project.STATUS_REQUEST).strip()  # Defaults to 'Request'

# Later when saving...
project.status = status  # 'Request'
db.session.commit()  # ❌ IntegrityError!
```

**Error Message:**
```
Error updating project: (sqlite3.IntegrityError) CHECK constraint failed: status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled')
[SQL: UPDATE projects SET status=?, notes=?, updated_at=? WHERE projects.id = ?]
[parameters: ('Request', 'None', '2025-10-20 05:42:11.195271', 49)]
```

---

## ✅ Solution

### Migration Script Created

**File:** `migrations/schema_v9_1_fix_project_status_constraint.sql`

This migration:
1. Creates a new `projects_new` table with updated CHECK constraint
2. Copies all existing data from `projects` to `projects_new`
3. Drops the old `projects` table
4. Renames `projects_new` to `projects`
5. Recreates all indexes
6. Updates schema version to `9.1`

**Updated CHECK Constraint:**
```sql
CHECK (status IN (
    'Request',                          -- New Phase 9 status
    'Quote & Approval',                 -- New Phase 9 status
    'Approved (POP Received)',          -- New Phase 9 status
    'Queued (Scheduled for Cutting)',   -- New Phase 9 status
    'In Progress',
    'Completed',
    'Cancelled',
    'Quote',                            -- Legacy status (backward compatibility)
    'Approved'                          -- Legacy status (backward compatibility)
))
```

### Application Script Created

**File:** `scripts/apply_status_constraint_fix.py`

This Python script:
- ✅ Checks current schema version
- ✅ Verifies the constraint issue exists
- ✅ Creates automatic database backup
- ✅ Applies the migration
- ✅ Verifies migration success
- ✅ Tests new status values
- ✅ Provides detailed output and error handling

---

## 🚀 How to Apply the Fix

### Step 1: Review the Migration

```bash
# View the migration SQL
cat migrations/schema_v9_1_fix_project_status_constraint.sql
```

### Step 2: Run the Migration Script

```bash
# Apply the fix (includes automatic backup)
python scripts/apply_status_constraint_fix.py
```

**Expected Output:**
```
================================================================================
Project Status CHECK Constraint Fix Migration
================================================================================

Database path: instance/laser_os.db
Current schema version: 9.0

Verifying constraint issue...

Current projects table schema:
--------------------------------------------------------------------------------
CREATE TABLE projects (
    ...
    CHECK (status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled'))
)
--------------------------------------------------------------------------------

✗ New status values NOT in CHECK constraint - migration needed

================================================================================
Do you want to proceed with the migration? (yes/no): yes

Creating backup: instance/laser_os.db.backup_20251020_123456
✓ Backup created successfully

Applying migration: migrations/schema_v9_1_fix_project_status_constraint.sql
✓ Migration applied successfully

Verifying migration success...
✓ Schema version updated to: 9.1
✓ All new status values present in CHECK constraint

New valid statuses:
  - Request
  - Quote & Approval
  - Approved (POP Received)
  - Queued (Scheduled for Cutting)

Testing new status values...
✓ Successfully created project with status: Request
✓ Test project cleaned up

================================================================================
✓ Migration completed successfully!
✓ Database backup saved at: instance/laser_os.db.backup_20251020_123456
================================================================================
```

### Step 3: Verify the Fix

After running the migration, test creating/updating a project with the new status values:

1. Navigate to Projects → New Project
2. Select status "Request" from dropdown
3. Save the project
4. ✅ Should save successfully without IntegrityError

---

## 📊 Status Values Reference

### New Phase 9 Statuses

| Status | Constant | Description |
|--------|----------|-------------|
| `Request` | `STATUS_REQUEST` | Initial project request |
| `Quote & Approval` | `STATUS_QUOTE_APPROVAL` | Quote sent, awaiting approval |
| `Approved (POP Received)` | `STATUS_APPROVED_POP` | Approved with proof of payment |
| `Queued (Scheduled for Cutting)` | `STATUS_QUEUED` | Scheduled in production queue |

### Existing Statuses

| Status | Constant | Description |
|--------|----------|-------------|
| `In Progress` | `STATUS_IN_PROGRESS` | Currently being worked on |
| `Completed` | `STATUS_COMPLETED` | Project finished |
| `Cancelled` | `STATUS_CANCELLED` | Project cancelled |

### Legacy Statuses (Backward Compatibility)

| Status | Constant | Description |
|--------|----------|-------------|
| `Quote` | `STATUS_QUOTE` | Legacy quote status |
| `Approved` | `STATUS_APPROVED` | Legacy approved status |

---

## 🔍 Related Files

### Model Definition
- `app/models/business.py` (lines 90-114) - Project status constants

### Routes Using Status
- `app/routes/projects.py` (line 104) - Create project with default status
- `app/routes/projects.py` (line 465-509) - Update status endpoint
- `app/routes/projects.py` (lines 81, 126, 132, etc.) - Form rendering with statuses

### Templates
- `app/templates/projects/form.html` (lines 85-101) - Status dropdown
- `ui_package/templates/projects/form.html` (lines 85-101) - Status dropdown

### Migrations
- `migrations/schema_v2_projects.sql` (line 39) - Original CHECK constraint
- `migrations/schema_v9_project_enhancements.sql` - Phase 9 migration (missing constraint update)
- `migrations/schema_v9_1_fix_project_status_constraint.sql` - **FIX migration**

### Tests
- `tests/test_phase9_models.py` (lines 34-58) - Tests for new status constants

---

## ⚠️ Important Notes

1. **Automatic Backup:** The migration script automatically creates a backup before applying changes
2. **Data Preservation:** All existing project data is preserved during migration
3. **Backward Compatibility:** Legacy status values are maintained for existing projects
4. **Index Recreation:** All indexes are recreated after table migration
5. **Schema Version:** Schema version is updated from `9.0` to `9.1`

---

## 🎯 Prevention

To prevent similar issues in the future:

1. **Always update CHECK constraints** when adding new enum-like values
2. **Test migrations** with actual database operations, not just model changes
3. **Include constraint updates** in the same migration that adds new status constants
4. **Document valid values** in both model and migration files

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Migration script runs without errors
- [ ] Database backup created successfully
- [ ] Schema version updated to 9.1
- [ ] Can create project with status "Request"
- [ ] Can update project to status "Quote & Approval"
- [ ] Can update project to status "Approved (POP Received)"
- [ ] Can update project to status "Queued (Scheduled for Cutting)"
- [ ] Existing projects with legacy statuses still work
- [ ] Status dropdown shows all valid options
- [ ] No IntegrityError when saving projects

---

**Migration Created:** 2025-10-20  
**Issue Resolved:** Project status CHECK constraint mismatch  
**Schema Version:** 9.0 → 9.1

