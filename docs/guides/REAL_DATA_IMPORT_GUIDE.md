# Real Business Data Import Guide

## 🎯 Overview

This guide will help you prepare your Laser OS application for importing your real business data by:
1. Creating a backup of the current state
2. Cleaning all test/placeholder data
3. Importing your real client data
4. Importing your real project data

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Your client data prepared in CSV format
- [ ] Your project data prepared in CSV format
- [ ] All project files organized (DXF, quotes, invoices, POPs, images)
- [ ] Reviewed the import templates to understand the format
- [ ] Read the BULK_IMPORT_GUIDE.md for detailed instructions

## 🚀 Step-by-Step Process

### Step 1: Create Database Backup

**Purpose:** Protect your current application state before making changes.

**Command:**
```bash
python cleanup_database.py
```

**What happens:**
- Creates a timestamped backup: `data/laser_os_backup_YYYYMMDD_HHMMSS.db`
- Displays backup file size for verification
- Confirms backup was created successfully

**Expected output:**
```
✅ Database backed up to: data/laser_os_backup_20241015_143022.db
   Backup size: 245,760 bytes
```

**Verification:**
- Check that the backup file exists in the `data/` directory
- Note the backup filename for potential restoration

---

### Step 2: Clean Test/Placeholder Data

**Purpose:** Remove all existing test data while preserving the database schema.

**Command:**
```bash
python cleanup_database.py
```

**What happens:**
1. **Backs up database** (automatic safety measure)
2. **Shows current data counts:**
   - Clients
   - Projects
   - Design files
   - Project documents
   - Communications
3. **Asks for confirmation** (type 'yes' to proceed)
4. **Deletes all data** from all tables
5. **Cleans file storage** directories
6. **Verifies schema** is intact
7. **Shows final summary**

**Expected output:**
```
================================================================================
LASER OS - DATABASE CLEANUP SCRIPT
================================================================================

⚠️  WARNING: This will delete ALL data from the database!
   - All clients will be removed
   - All projects will be removed
   - All design files will be removed
   - All project documents will be removed
   - All communications will be removed
   - All files in storage directories will be removed

   The database schema will be preserved.

================================================================================

Type 'yes' to continue with cleanup: yes

================================================================================
STEP 1: BACKING UP DATABASE
================================================================================
✅ Database backed up to: data/laser_os_backup_20241015_143022.db
   Backup size: 245,760 bytes

================================================================================
STEP 2: CLEANING DATABASE DATA
================================================================================

📊 Current record counts:
   clients: 3
   projects: 5
   design_files: 2
   project_documents: 3
   communications: 0
   communication_attachments: 0

🗑️  Deleting data...
   ✅ Deleted 0 records from communication_attachments
   ✅ Deleted 0 records from communications
   ✅ Deleted 3 records from project_documents
   ✅ Deleted 2 records from design_files
   ✅ Deleted 5 records from projects
   ✅ Deleted 3 records from clients
   ✅ Reset auto-increment counters

📊 Record counts after cleanup:
   clients: 0
   projects: 0
   design_files: 0
   project_documents: 0
   communications: 0
   communication_attachments: 0

✅ All tables successfully cleaned!

================================================================================
VERIFYING DATABASE SCHEMA
================================================================================

📋 Checking required tables:
   ✅ clients
   ✅ projects
   ✅ design_files
   ✅ project_documents
   ✅ communications
   ✅ communication_attachments

✅ Database schema is intact!

================================================================================
STEP 3: CLEANING FILE STORAGE
================================================================================
✅ Cleaned: data/files/projects
✅ Cleaned: data/documents/quotes
✅ Cleaned: data/documents/invoices
✅ Cleaned: data/documents/pops
✅ Cleaned: data/documents/delivery_notes

📊 Files removed: 15
📊 Directories removed: 5

================================================================================
✅ CLEANUP COMPLETE!
================================================================================

📁 Backup saved to: data/laser_os_backup_20241015_143022.db

✅ Database is now empty and ready for fresh data import
✅ Database schema is intact
✅ File storage directories are cleaned

🚀 You can now import your real business data using:
   python bulk_import.py --all --clients clients_import_template_full.csv --projects projects_import_template_full.csv
```

**Verification:**
- All record counts should be 0
- All required tables should be present (✅)
- File storage directories should be empty

---

### Step 3: Prepare Your Client Data

**File:** `clients_import_template_full.csv`

**Format:**
```csv
client_code,name,contact_person,email,phone,address,notes
,ABC Manufacturing,John Smith,john@abc.com,+27 11 123 4567,"123 Industrial Rd, JHB",Preferred customer
,XYZ Corp,Jane Doe,jane@xyz.co.za,+27 21 987 6543,"456 Business St, CPT",Net 30 terms
```

**Required fields:**
- `name` - Client company name

**Optional fields:**
- `client_code` - Leave blank to auto-generate (CL-0001, CL-0002, etc.)
- `contact_person` - Primary contact name
- `email` - Contact email address
- `phone` - Contact phone number
- `address` - Full physical address
- `notes` - Any additional notes or special instructions

**Tips:**
- Leave `client_code` blank for auto-generation
- Use consistent formatting for phone numbers
- Include full addresses for better record keeping
- Add notes for special terms, preferences, or important information

---

### Step 4: Prepare Your Project Data

**File:** `projects_import_template_full.csv`

**Format:**
```csv
client_code,name,description,status,quote_date,quoted_price,material_type,dxf_files,quote_files
CL-0001,Custom Brackets,Laser cut mounting brackets,Completed,2024-01-15,1500.00,Mild Steel 3mm,dxf/brackets.dxf,quotes/quote_001.pdf
CL-0002,Company Signage,Logo letters for building,In Progress,2024-02-01,3500.00,Stainless Steel 2mm,dxf/signage.dxf,quotes/quote_002.pdf
```

**Required fields:**
- `client_code` - Must match a client from your clients CSV (e.g., CL-0001)
- `name` - Project name/description

**Important optional fields:**
- `project_code` - Leave blank to auto-generate
- `description` - Detailed project description
- `status` - Quote | Approved | In Progress | Completed | Cancelled
- `quote_date` - Date quote was provided (YYYY-MM-DD or DD/MM/YYYY)
- `quoted_price` - Quoted price (numeric only, no currency symbols)
- `final_price` - Final invoiced price
- `material_type` - Material specification (e.g., "Mild Steel 3mm")
- `material_quantity_sheets` - Number of sheets used
- `parts_quantity` - Number of parts produced
- `estimated_cut_time` - Estimated cutting time in minutes
- `dxf_files` - Comma-separated DXF file paths
- `quote_files` - Comma-separated quote document paths
- `invoice_files` - Comma-separated invoice document paths
- `pop_files` - Comma-separated proof of payment paths
- `image_files` - Comma-separated image file paths

**Tips:**
- Client codes must match exactly (case-sensitive)
- Leave `project_code` blank for auto-generation
- Use YYYY-MM-DD format for dates (most reliable)
- File paths should be relative to your files directory
- Use forward slashes (/) in file paths
- Enclose multiple files in quotes: `"file1.dxf,file2.dxf"`

---

### Step 5: Organize Your Project Files

**Directory structure:**
```
my_business_files/
├── dxf/
│   ├── project1_brackets.dxf
│   ├── project2_signage.dxf
│   └── project3_panels.dxf
├── quotes/
│   ├── quote_001.pdf
│   ├── quote_002.pdf
│   └── quote_003.pdf
├── invoices/
│   ├── invoice_001.pdf
│   └── invoice_002.pdf
├── pops/
│   ├── pop_001.pdf
│   └── pop_002.jpg
└── images/
    ├── project1_finished.jpg
    └── project2_progress.jpg
```

**File organization tips:**
- Use descriptive filenames
- Keep related files in appropriate subdirectories
- Ensure filenames match references in your projects CSV
- Supported formats:
  - DXF: .dxf
  - Documents: .pdf, .doc, .docx, .xlsx, .xls
  - Images: .jpg, .jpeg, .png

---

### Step 6: Validate Your Data

**Before importing, always validate!**

```bash
python validate_import_data.py clients_import_template_full.csv projects_import_template_full.csv ./my_business_files
```

**What this checks:**
- CSV file structure and headers
- Required fields are present
- Data formats (dates, emails, etc.)
- Client codes in projects match clients CSV
- Status values are valid
- File references exist in the files directory

**Expected output:**
```
================================================================================
LASER OS - IMPORT DATA VALIDATOR
================================================================================

================================================================================
VALIDATING CLIENTS CSV
================================================================================
✅ Found 25 rows in clients_import_template_full.csv
✅ All required columns present
✅ Clients CSV validation passed!

================================================================================
VALIDATING PROJECTS CSV
================================================================================
✅ Found 48 rows in projects_import_template_full.csv
✅ All required columns present
✅ Projects CSV validation passed!

================================================================================
✅ ALL VALIDATIONS PASSED!
================================================================================

You can now run the import:
  python bulk_import.py --all --clients clients_import_template_full.csv --projects projects_import_template_full.csv --files-dir ./my_business_files
```

**If validation fails:**
- Read error messages carefully
- Fix issues in your CSV files
- Re-run validation until it passes
- Do NOT proceed to import until validation passes

---

### Step 7: Import Your Real Data

**Import clients first:**
```bash
python bulk_import.py --clients clients_import_template_full.csv
```

**Then import projects with files:**
```bash
python bulk_import.py --projects projects_import_template_full.csv --files-dir ./my_business_files
```

**Or import everything at once:**
```bash
python bulk_import.py --all --clients clients_import_template_full.csv --projects projects_import_template_full.csv --files-dir ./my_business_files
```

**Expected output:**
```
================================================================================
LASER OS - BULK IMPORT TOOL
================================================================================

Importing clients from: clients_import_template_full.csv
Importing projects from: projects_import_template_full.csv
Files directory: ./my_business_files

================================================================================
IMPORTING CLIENTS
================================================================================
Processing 25 clients...
✅ Imported client: ABC Manufacturing (CL-0001)
✅ Imported client: XYZ Corp (CL-0002)
...

================================================================================
IMPORTING PROJECTS
================================================================================
Processing 48 projects...
✅ Imported project: Custom Brackets (JB-2024-01-CL0001-001)
   - Uploaded 1 DXF file
   - Uploaded 1 quote document
✅ Imported project: Company Signage (JB-2024-02-CL0002-001)
   - Uploaded 1 DXF file
   - Uploaded 1 quote document
...

================================================================================
IMPORT SUMMARY
================================================================================
Clients imported: 25
Clients skipped: 0
Projects imported: 48
Projects skipped: 0
Files uploaded: 156
Files failed: 0
Total errors: 0
================================================================================

✅ Import completed successfully!
```

---

### Step 8: Verify the Import

**Check the web interface:**
```bash
python run.py
```

**Visit:** http://localhost:5000

**Verify:**
1. **Clients page** - All clients appear with correct information
2. **Projects page** - All projects appear and are linked to correct clients
3. **Project details** - Click on projects to verify:
   - Project information is correct
   - DXF files are attached
   - Documents are attached
   - Images are attached
   - Can download/view files

**Check import summary:**
- Imported counts match your expectations
- No errors reported
- All files uploaded successfully

---

## 🔄 If Something Goes Wrong

### Restore from Backup

If you need to restore the database:

```bash
# Windows
copy data\laser_os_backup_YYYYMMDD_HHMMSS.db data\laser_os.db

# Linux/Mac
cp data/laser_os_backup_YYYYMMDD_HHMMSS.db data/laser_os.db
```

Replace `YYYYMMDD_HHMMSS` with your actual backup timestamp.

### Common Issues

| Issue | Solution |
|-------|----------|
| Validation fails | Fix errors in CSV, re-validate |
| Client not found | Ensure client_code in projects matches clients CSV |
| File not found | Check file paths are relative to --files-dir |
| Import errors | Review error messages, fix data, try again |

---

## ✅ Success Checklist

After import, verify:
- [ ] All clients imported (check count in web interface)
- [ ] All projects imported (check count in web interface)
- [ ] Projects linked to correct clients
- [ ] All files uploaded and accessible
- [ ] Can view/download files from project pages
- [ ] No errors in import summary
- [ ] Data looks correct in web interface

---

## 📞 Next Steps

Once your real data is imported:
1. ✅ Verify all data in the web interface
2. ✅ Test key workflows (create quote, track project, etc.)
3. ✅ Delete old backup files if everything looks good
4. ✅ Start using Laser OS for your daily operations!

---

**You're ready to import your real business data!** 🚀

