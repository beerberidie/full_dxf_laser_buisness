# Laser OS - Bulk Import Guide

## 🎯 Quick Start

This guide will help you import your existing client information and project data into Laser OS.

## ✅ Pre-Import Checklist

Before you begin, ensure:

1. **Database is initialized and running**
   ```bash
   # Check database exists
   python check_db_schema.py
   ```

2. **Application is working**
   ```bash
   # Test the application
   python run.py
   # Visit http://localhost:5000 in your browser
   ```

3. **You have your data ready**
   - Client contact information
   - Project details
   - Associated files (DXF, quotes, invoices, POPs, images)

## 📋 Step-by-Step Import Process

### Step 1: Generate Import Templates

Run the template generator to create CSV templates and documentation:

```bash
python bulk_import.py --generate-templates
```

This creates:
- `clients_import_template.csv` - Template for client data
- `projects_import_template.csv` - Template for project data
- `IMPORT_README.md` - Detailed field documentation

### Step 2: Prepare Your Client Data

Edit `clients_import_template.csv` with your client information:

**Required Fields:**
- `name` - Client company name

**Optional Fields:**
- `client_code` - Leave blank to auto-generate (CL-0001, CL-0002, etc.)
- `contact_person` - Primary contact name
- `email` - Contact email
- `phone` - Contact phone number
- `address` - Full address
- `notes` - Any additional notes

**Example:**
```csv
client_code,name,contact_person,email,phone,address,notes
,Acme Corporation,John Smith,john@acme.com,+27 11 123 4567,"123 Main St, Johannesburg",Preferred customer
,Tech Solutions,Jane Doe,jane@tech.co.za,+27 21 987 6543,"456 Oak Ave, Cape Town",Net 30 terms
```

### Step 3: Organize Your Project Files

Create a directory structure for your files:

```
my_import_files/
├── dxf/
│   ├── project1_part1.dxf
│   ├── project1_part2.dxf
│   └── project2_design.dxf
├── quotes/
│   ├── quote_001.pdf
│   └── quote_002.pdf
├── invoices/
│   ├── invoice_001.pdf
│   └── invoice_002.pdf
├── pops/
│   ├── pop_001.pdf
│   └── pop_002.jpg
├── delivery_notes/
│   └── delivery_001.pdf
└── images/
    ├── project1_photo1.jpg
    ├── project1_photo2.jpg
    └── project2_finished.jpg
```

**File Organization Tips:**
- Use descriptive filenames
- Keep related files in appropriate subdirectories
- Supported formats:
  - **DXF files**: .dxf
  - **Documents**: .pdf, .doc, .docx, .xlsx, .xls
  - **Images**: .jpg, .jpeg, .png

### Step 4: Prepare Your Project Data

Edit `projects_import_template.csv` with your project information:

**Required Fields:**
- `client_code` - Must match an existing client (e.g., CL-0001)
- `name` - Project name/description

**Important Optional Fields:**
- `status` - Quote | Approved | In Progress | Completed | Cancelled
- `quote_date` - Format: YYYY-MM-DD or DD/MM/YYYY
- `quoted_price` - Numbers only (e.g., 1500.00)
- `material_type` - e.g., "Mild Steel 3mm"
- `dxf_files` - Comma-separated file paths relative to files directory
- `quote_files` - Quote document paths
- `invoice_files` - Invoice document paths
- `pop_files` - Proof of payment document paths
- `image_files` - Image file paths

**Example:**
```csv
client_code,name,description,status,quote_date,quoted_price,material_type,material_quantity_sheets,parts_quantity,estimated_cut_time,dxf_files,quote_files,image_files
CL-0001,Custom Brackets,Mounting brackets for equipment,Approved,2024-01-15,1500.00,Mild Steel 3mm,2,50,120,dxf/project1_part1.dxf,quotes/quote_001.pdf,images/project1_photo1.jpg
CL-0001,Signage Letters,Company logo letters,Completed,2024-01-10,2500.00,Stainless Steel 2mm,3,25,180,"dxf/project1_part1.dxf,dxf/project1_part2.dxf","quotes/quote_002.pdf","images/project1_photo1.jpg,images/project1_photo2.jpg"
```

**File Path Format:**
- Use forward slashes (/) even on Windows
- Paths are relative to the `--files-dir` directory
- Multiple files: separate with commas
- Enclose in quotes if using commas: `"file1.dxf,file2.dxf"`

### Step 5: Validate Your Data

**ALWAYS validate before importing!**

```bash
python bulk_import.py --validate-only --clients clients_import_template.csv --projects projects_import_template.csv
```

This will:
- Check all required fields are present
- Validate data formats (dates, emails, etc.)
- Verify client codes exist for projects
- Report any errors without making changes

**Fix any errors reported before proceeding!**

### Step 6: Import Clients

Import your client data first:

```bash
python bulk_import.py --clients clients_import_template.csv
```

The script will:
- Auto-generate client codes if not provided
- Skip duplicate clients (based on client_code)
- Report success/failure for each record
- Show summary statistics

### Step 7: Import Projects and Files

Import projects with associated files:

```bash
python bulk_import.py --projects projects_import_template.csv --files-dir ./my_import_files
```

The script will:
- Auto-generate project codes if not provided
- Link projects to existing clients
- Upload and link all specified files
- Organize files in the correct directories
- Report progress and any errors

### Step 8: Import Everything at Once (Alternative)

You can import both clients and projects in one command:

```bash
python bulk_import.py --all --clients clients_import_template.csv --projects projects_import_template.csv --files-dir ./my_import_files
```

## 🔍 Verification

After import, verify your data:

1. **Check the console output**
   - Review the import summary
   - Note any errors or warnings
   - Verify counts match your expectations

2. **Check the web interface**
   ```bash
   python run.py
   ```
   - Visit http://localhost:5000
   - Navigate to Clients page - verify all clients imported
   - Navigate to Projects page - verify all projects imported
   - Click on individual projects to verify files are attached

3. **Check the database directly** (optional)
   ```bash
   python check_db.py
   ```

## 📊 Understanding the Import Summary

After import, you'll see a summary like:

```
================================================================================
IMPORT SUMMARY
================================================================================
Clients imported: 25
Clients skipped: 2
Projects imported: 48
Projects skipped: 1
Files uploaded: 156
Files failed: 0
Total errors: 0
================================================================================
```

**What the numbers mean:**
- **Imported**: Successfully added to database
- **Skipped**: Already existed (based on code) or had errors
- **Files uploaded**: Successfully copied and linked
- **Files failed**: Could not be uploaded (file not found, etc.)
- **Errors**: Total number of errors encountered

## ⚠️ Common Issues and Solutions

### Issue: "Client not found"
**Solution:** Import clients before projects. Projects must reference existing client codes.

### Issue: "File not found: /path/to/file.dxf"
**Solutions:**
- Verify the file exists in the specified location
- Check the path is relative to `--files-dir`
- Use forward slashes (/) in paths
- Check for typos in filenames

### Issue: "Invalid date format"
**Solutions:**
- Use YYYY-MM-DD format (e.g., 2024-01-15)
- Or DD/MM/YYYY format (e.g., 15/01/2024)
- Leave blank if date is not available

### Issue: "Invalid status"
**Solution:** Use exact status names:
- Quote
- Approved
- In Progress
- Completed
- Cancelled

### Issue: "Client code already exists"
**Solution:** This is normal - the script skips duplicates. If you want to update existing clients, you'll need to do that manually through the web interface.

### Issue: "Row X: Error importing project: ..."
**Solutions:**
- Check the specific error message
- Verify all required fields are present
- Check data formats match requirements
- Ensure client_code references an existing client

## 🔄 Re-running Imports

The import script is **idempotent** for codes:
- Existing client codes are skipped (not updated)
- Existing project codes are skipped (not updated)
- Files are always uploaded (duplicates possible)

**To re-import:**
1. Remove the `client_code` or `project_code` from CSV
2. The script will generate new codes
3. Or manually delete records from database first

## 💾 Backup Recommendation

**ALWAYS backup your database before bulk imports:**

```bash
# Windows
copy data\laser_os.db data\laser_os_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db

# Linux/Mac
cp data/laser_os.db data/laser_os_backup_$(date +%Y%m%d).db
```

## 📚 Additional Resources

- **IMPORT_README.md** - Detailed field documentation
- **clients_import_template.csv** - Client import template
- **projects_import_template.csv** - Project import template
- **README.md** - Main application documentation
- **USAGE_GUIDE.md** - Application usage guide

## 🆘 Getting Help

If you encounter issues:

1. Check the error messages carefully
2. Review this guide and IMPORT_README.md
3. Verify your CSV format matches the templates
4. Try validating with `--validate-only` first
5. Test with a small subset of data first

## 📝 Best Practices

1. **Start small** - Test with 2-3 clients and projects first
2. **Validate always** - Use `--validate-only` before importing
3. **Backup first** - Always backup your database
4. **Organize files** - Use a clear directory structure
5. **Check results** - Verify data in web interface after import
6. **Keep originals** - Don't delete your original CSV files
7. **Document codes** - Keep a record of generated client/project codes

## ✨ Success!

Once your data is imported:
- All clients are accessible in the Clients section
- All projects are linked to their respective clients
- All files are uploaded and accessible from project detail pages
- You can start using Laser OS for your daily operations!

---

**Need to import more data later?** Just repeat the process with new CSV files!

