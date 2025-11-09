# Import Quick Reference Card

## 🚀 Quick Commands

### Generate Templates
```bash
python bulk_import.py --generate-templates
```

### Validate Data
```bash
# Quick validation
python validate_import_data.py clients.csv projects.csv ./files

# Full validation with bulk import script
python bulk_import.py --validate-only --clients clients.csv --projects projects.csv
```

### Backup Database
```bash
# Windows
copy data\laser_os.db data\laser_os_backup.db

# Linux/Mac
cp data/laser_os.db data/laser_os_backup.db
```

### Import Clients Only
```bash
python bulk_import.py --clients clients.csv
```

### Import Projects Only
```bash
python bulk_import.py --projects projects.csv --files-dir ./my_files
```

### Import Everything
```bash
python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./my_files
```

## 📋 CSV Format Quick Reference

### Clients CSV

**Required:**
- `name` - Client company name

**Optional:**
- `client_code` - Leave blank for auto-generation
- `contact_person`, `email`, `phone`, `address`, `notes`

**Example:**
```csv
client_code,name,contact_person,email,phone,address,notes
,Acme Corp,John Smith,john@acme.com,+27 11 123 4567,"123 Main St",VIP client
```

### Projects CSV

**Required:**
- `client_code` - Must match existing client (e.g., CL-0001)
- `name` - Project name

**Important Optional:**
- `project_code` - Leave blank for auto-generation
- `status` - Quote | Approved | In Progress | Completed | Cancelled
- `quote_date`, `due_date` - YYYY-MM-DD or DD/MM/YYYY
- `quoted_price` - Numeric only
- `material_type` - e.g., "Mild Steel 3mm"
- `dxf_files` - Comma-separated: "file1.dxf,file2.dxf"
- `quote_files`, `invoice_files`, `pop_files`, `image_files`

**Example:**
```csv
client_code,name,status,quote_date,quoted_price,material_type,dxf_files,quote_files
CL-0001,Brackets,Approved,2024-01-15,1500.00,Mild Steel 3mm,dxf/brackets.dxf,quotes/quote_001.pdf
```

## 📁 File Organization

```
my_import_files/
├── dxf/              # DXF design files
├── quotes/           # Quote documents (PDF, DOC, XLS)
├── invoices/         # Invoice documents
├── pops/             # Proof of payment (PDF, JPG, PNG)
├── delivery_notes/   # Delivery notes
└── images/           # Project images (JPG, PNG)
```

**File Path Rules:**
- Use forward slashes: `dxf/file.dxf` ✅ not `dxf\file.dxf` ❌
- Relative to files directory: `dxf/file.dxf` ✅ not `C:/full/path/file.dxf` ❌
- Multiple files: `"file1.dxf,file2.dxf"` (use quotes if commas)

## ⚡ Workflow

### Standard Import Process
```bash
# 1. Generate templates
python bulk_import.py --generate-templates

# 2. Edit CSV files with your data
# (Edit clients_import_template.csv and projects_import_template.csv)

# 3. Organize files
# (Create directory structure and copy files)

# 4. Validate
python validate_import_data.py clients_import_template.csv projects_import_template.csv ./files

# 5. Backup
copy data\laser_os.db data\laser_os_backup.db

# 6. Import
python bulk_import.py --all --clients clients_import_template.csv --projects projects_import_template.csv --files-dir ./files

# 7. Verify
python run.py
# Open http://localhost:5000 and check data
```

### Test First Approach (Recommended)
```bash
# 1. Create test CSV with 2-3 records
# 2. Validate test data
python validate_import_data.py test_clients.csv test_projects.csv ./test_files

# 3. Backup
copy data\laser_os.db data\laser_os_backup.db

# 4. Import test data
python bulk_import.py --all --clients test_clients.csv --projects test_projects.csv --files-dir ./test_files

# 5. Verify in web interface
# 6. If good, restore backup and import full data
# 7. If issues, restore backup and fix problems
```

## 🔍 Common Issues

| Issue | Solution |
|-------|----------|
| "Client not found" | Import clients before projects |
| "File not found" | Check file path is relative to --files-dir |
| "Invalid date format" | Use YYYY-MM-DD or DD/MM/YYYY |
| "Invalid status" | Use exact names: Quote, Approved, In Progress, Completed, Cancelled |
| "Client code already exists" | Normal - duplicates are skipped. Remove client_code to create new |
| Validation fails | Read error messages, fix CSV, re-validate |

## 📊 Import Summary Explained

```
Clients imported: 25      # Successfully added
Clients skipped: 2        # Already existed or had errors
Projects imported: 48     # Successfully added
Projects skipped: 1       # Already existed or had errors
Files uploaded: 156       # Successfully uploaded and linked
Files failed: 0           # Could not upload (file not found, etc.)
Total errors: 0           # Number of errors encountered
```

## ✅ Validation Checklist

Before importing:
- [ ] CSV files have correct headers
- [ ] All required fields filled (name for clients, client_code + name for projects)
- [ ] Client codes in projects CSV match clients CSV
- [ ] Dates in correct format (YYYY-MM-DD)
- [ ] Status values are valid
- [ ] File paths are relative and use forward slashes
- [ ] All referenced files exist
- [ ] Database backed up

## 🎯 Field Formats

| Field Type | Format | Example |
|------------|--------|---------|
| Client Code | CL-XXXX | CL-0001 |
| Project Code | JB-yyyy-mm-CLxxxx-### | JB-2024-01-CL0001-001 |
| Date | YYYY-MM-DD or DD/MM/YYYY | 2024-01-15 or 15/01/2024 |
| Price | Numeric only | 1500.00 |
| Boolean | true/false or yes/no | true |
| File List | Comma-separated | "file1.dxf,file2.dxf" |
| Status | Exact name | Quote, Approved, In Progress, Completed, Cancelled |

## 🛠️ Troubleshooting Commands

### Check Database
```bash
python check_db_schema.py
```

### Test Application
```bash
python run.py
# Visit http://localhost:5000
```

### View Import Templates
```bash
# Windows
type clients_import_template.csv
type projects_import_template.csv

# Linux/Mac
cat clients_import_template.csv
cat projects_import_template.csv
```

### Restore Database
```bash
# Windows
copy data\laser_os_backup.db data\laser_os.db

# Linux/Mac
cp data/laser_os_backup.db data/laser_os.db
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `BULK_IMPORT_GUIDE.md` | Complete step-by-step guide |
| `IMPORT_README.md` | Detailed field documentation |
| `DATA_IMPORT_SUMMARY.md` | System overview and assessment |
| `PRE_IMPORT_CHECKLIST.md` | Pre-import checklist |
| `IMPORT_QUICK_REFERENCE.md` | This file - quick reference |
| `clients_import_template.csv` | Client data template |
| `projects_import_template.csv` | Project data template |

## 💡 Pro Tips

1. **Always validate first** - Catch errors before importing
2. **Always backup** - Safety first!
3. **Test with small dataset** - Verify process works
4. **Use templates** - Start from generated templates
5. **Check client codes** - Must match between CSVs
6. **Organize files first** - Clear structure helps
7. **Use forward slashes** - Even on Windows
8. **Leave codes blank** - Auto-generation is easier
9. **Read error messages** - They tell you what's wrong
10. **Verify after import** - Check web interface

## 🎓 Learning Path

1. **Read BULK_IMPORT_GUIDE.md** - Understand the process
2. **Generate templates** - See the format
3. **Review IMPORT_README.md** - Learn field details
4. **Create test data** - 2-3 records
5. **Validate test data** - Practice validation
6. **Import test data** - Practice import
7. **Verify results** - Check web interface
8. **Scale up** - Import full dataset

## ⚡ Speed Run (Experienced Users)

```bash
# Generate, edit, validate, backup, import, verify
python bulk_import.py --generate-templates
# (Edit CSVs and organize files)
python validate_import_data.py clients.csv projects.csv ./files
copy data\laser_os.db data\laser_os_backup.db
python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./files
python run.py
```

---

**Keep this reference handy during your import process!**

