# Pre-Import Checklist

Use this checklist to ensure you're ready to import your data into Laser OS.

## ✅ System Readiness

- [ ] **Database is initialized**
  ```bash
  python check_db_schema.py
  ```
  Expected: Should show all tables including clients, projects, design_files, project_documents

- [ ] **Application runs successfully**
  ```bash
  python run.py
  ```
  Expected: Server starts on http://localhost:5000 without errors

- [ ] **Can access web interface**
  - Open browser to http://localhost:5000
  - Navigate to Clients page
  - Navigate to Projects page
  - Verify pages load correctly

## ✅ Data Preparation

- [ ] **Generated import templates**
  ```bash
  python bulk_import.py --generate-templates
  ```
  Expected files created:
  - clients_import_template.csv
  - projects_import_template.csv
  - IMPORT_README.md

- [ ] **Reviewed template structure**
  - Opened clients_import_template.csv
  - Opened projects_import_template.csv
  - Read IMPORT_README.md
  - Understand required vs optional fields

- [ ] **Prepared client data**
  - Created/edited clients CSV file
  - All clients have names (required)
  - Email addresses include @ symbol
  - Client codes left blank for auto-generation (or use existing format CL-XXXX)
  - No duplicate client codes

- [ ] **Prepared project data**
  - Created/edited projects CSV file
  - All projects have client_code (required)
  - All projects have name (required)
  - Client codes match clients in your clients CSV
  - Project codes left blank for auto-generation (or use existing format)
  - Status values are valid: Quote, Approved, In Progress, Completed, Cancelled
  - Dates in correct format: YYYY-MM-DD or DD/MM/YYYY
  - Prices are numeric (no currency symbols)

## ✅ File Organization

- [ ] **Created files directory structure**
  ```
  my_import_files/
  ├── dxf/
  ├── quotes/
  ├── invoices/
  ├── pops/
  ├── delivery_notes/
  └── images/
  ```

- [ ] **Copied all DXF files to dxf/ folder**
  - Files have .dxf extension
  - Filenames match references in projects CSV

- [ ] **Copied all quote documents to quotes/ folder**
  - Supported formats: PDF, DOC, DOCX, XLS, XLSX
  - Filenames match references in projects CSV

- [ ] **Copied all invoice documents to invoices/ folder**
  - Supported formats: PDF, DOC, DOCX, XLS, XLSX
  - Filenames match references in projects CSV

- [ ] **Copied all POP documents to pops/ folder**
  - Supported formats: PDF, JPG, JPEG, PNG
  - Filenames match references in projects CSV

- [ ] **Copied all delivery notes to delivery_notes/ folder**
  - Supported formats: PDF, DOC, DOCX
  - Filenames match references in projects CSV

- [ ] **Copied all images to images/ folder**
  - Supported formats: JPG, JPEG, PNG
  - Filenames match references in projects CSV

- [ ] **Verified file paths in CSV**
  - Paths use forward slashes (/) not backslashes (\)
  - Paths are relative to files directory (e.g., dxf/file.dxf not C:/full/path/file.dxf)
  - Multiple files separated by commas
  - Paths with commas are enclosed in quotes

## ✅ Data Validation

- [ ] **Ran validation script**
  ```bash
  python validate_import_data.py clients.csv projects.csv ./my_import_files
  ```
  Expected: "ALL VALIDATIONS PASSED!"

- [ ] **Fixed any validation errors**
  - Reviewed all error messages
  - Corrected data in CSV files
  - Re-ran validation until passing

- [ ] **Reviewed validation warnings**
  - Checked all warnings
  - Decided if warnings are acceptable
  - Made corrections if needed

- [ ] **Verified file references**
  - All referenced files exist
  - File paths are correct
  - No typos in filenames

## ✅ Safety Measures

- [ ] **Backed up database**
  ```bash
  # Windows
  copy data\laser_os.db data\laser_os_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db
  
  # Linux/Mac
  cp data/laser_os.db data/laser_os_backup_$(date +%Y%m%d).db
  ```

- [ ] **Backed up CSV files**
  - Copied clients CSV to safe location
  - Copied projects CSV to safe location

- [ ] **Backed up files directory**
  - Copied entire files directory to safe location

- [ ] **Tested with small dataset first** (recommended)
  - Created test CSV with 2-3 clients
  - Created test CSV with 2-3 projects
  - Ran import on test data
  - Verified results in web interface
  - Restored from backup if needed

## ✅ Import Execution

- [ ] **Ready to import clients**
  ```bash
  python bulk_import.py --clients clients.csv
  ```

- [ ] **Ready to import projects**
  ```bash
  python bulk_import.py --projects projects.csv --files-dir ./my_import_files
  ```

- [ ] **OR ready to import everything**
  ```bash
  python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./my_import_files
  ```

## ✅ Post-Import Verification

- [ ] **Reviewed console output**
  - Checked import summary statistics
  - Noted any errors or warnings
  - Verified counts match expectations

- [ ] **Verified clients in web interface**
  - Opened http://localhost:5000/clients
  - All clients appear in list
  - Client details are correct
  - Contact information is accurate

- [ ] **Verified projects in web interface**
  - Opened http://localhost:5000/projects
  - All projects appear in list
  - Projects linked to correct clients
  - Project details are correct

- [ ] **Verified files are attached**
  - Opened individual project detail pages
  - DXF files appear in Design Files section
  - Documents appear in Project Documents section
  - Can download/view files
  - File counts match expectations

- [ ] **Checked for missing data**
  - Compared import summary to expected counts
  - Investigated any skipped records
  - Verified all important data imported

## 🚨 Troubleshooting

If you encounter issues:

### Validation Fails
- [ ] Read error messages carefully
- [ ] Check CSV file format (UTF-8 encoding)
- [ ] Verify required fields are present
- [ ] Check data formats (dates, emails, etc.)
- [ ] Fix errors and re-validate

### Import Fails
- [ ] Check console error messages
- [ ] Verify database is accessible
- [ ] Ensure no other processes are using database
- [ ] Check file permissions
- [ ] Restore from backup and try again

### Files Not Uploading
- [ ] Verify files exist in specified locations
- [ ] Check file paths in CSV (relative to --files-dir)
- [ ] Ensure file extensions are supported
- [ ] Check file permissions
- [ ] Verify disk space available

### Data Missing After Import
- [ ] Check import summary for skipped records
- [ ] Look for duplicate codes (skipped automatically)
- [ ] Verify client codes match between CSVs
- [ ] Check console output for errors
- [ ] Review error log

## 📞 Need Help?

If you're stuck:

1. **Review documentation**
   - BULK_IMPORT_GUIDE.md - Step-by-step guide
   - IMPORT_README.md - Field documentation
   - DATA_IMPORT_SUMMARY.md - System overview

2. **Check error messages**
   - Read console output carefully
   - Error messages usually indicate the problem
   - Fix one error at a time

3. **Test with small dataset**
   - Create CSV with 1-2 records
   - Test import process
   - Verify results
   - Scale up once working

4. **Restore from backup**
   - If something goes wrong
   - Restore database from backup
   - Fix issues and try again

## ✨ Ready to Import!

Once all checkboxes are checked, you're ready to import your data!

**Recommended import order:**
1. Validate data
2. Backup database
3. Import clients
4. Verify clients in web interface
5. Import projects with files
6. Verify projects and files in web interface

**Good luck with your import!** 🚀

