# Profiles Migration - Quick Start Guide

## 🚀 Quick Start

### Prerequisites

1. **Clients Already Imported**
   - All clients must exist in database with correct client codes
   - Verify: `python run.py` → Navigate to Clients page
   - Client codes must match folder names (e.g., `CL-0001`)

2. **Source Directory Structure**
   ```
   profiles_import/
   ├── CL-0001/
   │   └── 1.Projects/
   │       ├── 0001-Project Name-10.15.2025/
   │       │   ├── 0001-Part1-Galv-1mm-x1.dxf
   │       │   ├── 0001-Part1-Galv-1mm-x1.lbrn2
   │       │   └── quote.pdf
   │       └── 0002-Another Project-10.16.2025/
   │           └── ...
   ├── CL-0002/
   │   └── 1.Projects/
   │       └── ...
   ```

3. **Database Backup**
   ```bash
   # Windows
   copy data\laser_os.db data\laser_os_backup_before_profiles.db
   
   # Linux/Mac
   cp data/laser_os.db data/laser_os_backup_before_profiles.db
   ```

---

## 📝 Step-by-Step Process

### Step 1: Validate Source Data

**Dry run to check for issues:**

```bash
python migrate_profiles.py --source ./profiles_import --validate-only --verbose
```

**Expected Output:**
```
📋 Profiles Migration - Validation Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Scanning directory: ./profiles_import

✅ Found 5 client folders
✅ Found 47 project folders
✅ Found 234 files

📊 Validation Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Clients:
  ✓ CL-0001: Acme Corp (12 projects)
  ✓ CL-0002: Tech Solutions (8 projects)
  ✓ CL-0003: Manufacturing Co (15 projects)
  ✗ CL-0099: NOT FOUND IN DATABASE
  
Projects:
  ✓ 45 projects parsed successfully
  ⚠ 2 projects have parsing warnings
  
Files:
  ✓ 156 design files (.dxf, .lbrn2)
  ✓ 78 document files (.pdf, .jpg, etc.)
  
⚠️ Warnings:
  - CL-0001/0005-Project-invalid-date: Could not parse date
  - CL-0002/0003-Part-MS-2mm-x5.dxf: Unusual thickness value
  
❌ Errors:
  - CL-0099: Client not found in database
  
💡 Recommendation:
  - Import missing client CL-0099 before migration
  - Review warnings (non-critical)
```

### Step 2: Fix Issues

**If clients are missing:**
```bash
# Add missing clients via web interface or CSV import
python bulk_import.py --clients missing_clients.csv
```

**If folder names are invalid:**
- Rename folders to match pattern: `{number}-{description}-{date}`
- Example: `0001-Gas Cover box-10.15.2025`

### Step 3: Test with Single Client

**Import one client to test:**

```bash
python migrate_profiles.py --source ./profiles_import --client CL-0001 --verbose
```

**Expected Output:**
```
📋 Profiles Migration - Import Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Target: Client CL-0001 only

⏳ Importing projects...

✅ [1/12] Project 0001-Gas Cover box-10.15.2025
   └─ Created: JB-2025-10-CL0001-001
   └─ Files: 2 design, 1 document

✅ [2/12] Project 0002-Brackets Set-10.16.2025
   └─ Created: JB-2025-10-CL0001-002
   └─ Files: 1 design, 0 documents

...

📊 Import Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Projects:
  ✓ 12 imported successfully
  ✗ 0 failed
  ⊘ 0 skipped (duplicates)
  
Files:
  ✓ 24 design files uploaded
  ✓ 8 documents uploaded
  ✗ 0 failed
  
Time: 45 seconds
```

### Step 4: Verify Test Import

**Check in web interface:**
```bash
python run.py
# Open http://localhost:5000
```

1. Navigate to **Projects** page
2. Filter by client: CL-0001
3. Verify all 12 projects appear
4. Click on a project
5. Check files are attached
6. Verify metadata (material, thickness, etc.)

**If issues found:**
```bash
# Delete test projects (manual or via SQL)
# Fix issues in migration script
# Re-run test import
```

### Step 5: Full Migration

**Import all clients:**

```bash
python migrate_profiles.py --source ./profiles_import --all --verbose
```

**Monitor progress:**
```
⏳ Importing projects... [████████░░] 80% (38/47)
   Current: CL-0004/0008-Signage Letters-10.20.2025
   Elapsed: 2m 15s | Remaining: ~35s
```

### Step 6: Verify Results

**Check migration report:**

The script generates: `migration_report_YYYYMMDD_HHMMSS.txt`

```
═══════════════════════════════════════════════════════════
PROFILES MIGRATION REPORT
═══════════════════════════════════════════════════════════

Date: 2025-10-16 14:30:45
Source: ./profiles_import
Mode: Full Import

SUMMARY
───────────────────────────────────────────────────────────
Clients Processed:     5
Projects Imported:     45
Projects Failed:       0
Projects Skipped:      2 (duplicates)

Files Uploaded:        232
  - Design Files:      154
  - Documents:         78
Files Failed:          2

Execution Time:        5m 23s

DETAILS
───────────────────────────────────────────────────────────

✓ CL-0001: Acme Corp
  Projects: 12/12 imported
  Files: 48 uploaded
  
✓ CL-0002: Tech Solutions
  Projects: 8/8 imported
  Files: 32 uploaded
  
...

ERRORS
───────────────────────────────────────────────────────────
[None]

WARNINGS
───────────────────────────────────────────────────────────
- CL-0001/0005: Date parsing failed, used current date
- CL-0003/0012/image.jpg: File size exceeds 50MB, skipped

RECOMMENDATIONS
───────────────────────────────────────────────────────────
✓ Migration completed successfully
✓ All critical data imported
⚠ Review 2 warnings above
⚠ Manually upload large files if needed

═══════════════════════════════════════════════════════════
```

**Verify in database:**

```bash
python check_migration.py
```

This script checks:
- Project count matches
- All files accessible
- No orphaned records
- Relationships intact

---

## 🔧 Command Reference

### Validation Commands

```bash
# Validate all
python migrate_profiles.py --source ./profiles_import --validate-only

# Validate with verbose output
python migrate_profiles.py --source ./profiles_import --validate-only --verbose

# Dry run (alias for validate-only)
python migrate_profiles.py --source ./profiles_import --dry-run
```

### Import Commands

```bash
# Import specific client
python migrate_profiles.py --source ./profiles_import --client CL-0001

# Import all clients
python migrate_profiles.py --source ./profiles_import --all

# Import with verbose logging
python migrate_profiles.py --source ./profiles_import --all --verbose

# Import with custom log file
python migrate_profiles.py --source ./profiles_import --all --log migration.log
```

### Utility Commands

```bash
# Generate migration report only (after import)
python migrate_profiles.py --report-only

# Check migration status
python check_migration.py

# Rollback last migration (if needed)
python rollback_migration.py --confirm
```

---

## ⚠️ Troubleshooting

### Issue: "Client CL-XXXX not found"

**Solution:**
1. Import missing client first
2. Or skip that client: `--exclude CL-XXXX`

### Issue: "Invalid folder name format"

**Solution:**
Rename folder to match pattern:
```
Wrong: "Project 1 - Gas Box"
Right: "0001-Gas Box-10.15.2025"
```

### Issue: "File already exists"

**Solution:**
- Script skips duplicates by default
- Use `--overwrite` to replace existing files
- Use `--skip-duplicates` to skip silently

### Issue: "Permission denied"

**Solution:**
```bash
# Windows: Run as administrator
# Linux/Mac: Check file permissions
chmod -R 755 profiles_import/
```

### Issue: "Database locked"

**Solution:**
```bash
# Close any open database connections
# Stop the web server
# Re-run migration
```

---

## 📊 Expected Results

### Database Changes

**Before Migration:**
- Clients: 5
- Projects: 0
- Design Files: 0
- Documents: 0

**After Migration:**
- Clients: 5 (unchanged)
- Projects: 47 (new)
- Design Files: 156 (new)
- Documents: 78 (new)

### File System Changes

**New directories created:**
```
data/
├── files/
│   └── projects/
│       ├── 1/  (project_id)
│       ├── 2/
│       ├── 3/
│       └── ...
└── documents/
    ├── quotes/
    ├── invoices/
    ├── pops/
    ├── delivery_notes/
    └── other/
```

**Source files:**
- Original files remain unchanged
- Files are COPIED, not moved
- Safe to delete source after verification

---

## ✅ Post-Migration Checklist

- [ ] Migration report generated and reviewed
- [ ] All projects visible in web interface
- [ ] Files accessible and downloadable
- [ ] Metadata correctly populated
- [ ] No errors in migration log
- [ ] Database backup created
- [ ] Source files backed up
- [ ] Team notified of new data

---

## 🆘 Getting Help

### Check Logs

```bash
# View migration log
cat migration_YYYYMMDD_HHMMSS.log

# View last 50 lines
tail -n 50 migration_YYYYMMDD_HHMMSS.log

# Search for errors
grep "ERROR" migration_YYYYMMDD_HHMMSS.log
```

### Debug Mode

```bash
# Run with maximum verbosity
python migrate_profiles.py --source ./profiles_import --all --verbose --debug
```

### Manual Verification

```bash
# Check database directly
sqlite3 data/laser_os.db

# Count projects
SELECT COUNT(*) FROM projects;

# Check recent projects
SELECT project_code, name, created_at 
FROM projects 
ORDER BY created_at DESC 
LIMIT 10;

# Check files
SELECT COUNT(*) FROM design_files;
SELECT COUNT(*) FROM project_documents;
```

---

## 📞 Support

If you encounter issues:

1. **Check this guide** - Most common issues covered
2. **Review migration report** - Contains detailed error info
3. **Check logs** - Full details of what happened
4. **Restore backup** - If needed, restore and try again
5. **Contact support** - Provide migration report and logs

---

**Document Version**: 1.0  
**Created**: 2025-10-16  
**Last Updated**: 2025-10-16

