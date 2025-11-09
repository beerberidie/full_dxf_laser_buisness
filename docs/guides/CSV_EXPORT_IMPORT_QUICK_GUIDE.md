# CSV Export/Import Quick Reference Guide

**Quick guide for exporting, editing, and re-importing project data**

---

## 🚀 Quick Start: Export → Edit → Re-Import

### **1. Export Projects to CSV**
```bash
python export_projects_to_csv.py
```
**Output:** `data/exports/projects_export_2025-10-17_HHMMSS.csv`

### **2. Edit in Excel/Google Sheets**
- Open the CSV file
- Make your changes
- Save the file

### **3. Preview Changes**
```bash
python update_projects_from_csv.py data/exports/projects_export_2025-10-17_HHMMSS.csv --preview
```

### **4. Apply Updates**
```bash
python update_projects_from_csv.py data/exports/projects_export_2025-10-17_HHMMSS.csv
```

---

## 📋 Command Reference

### **Export Commands**

```bash
# Export all projects
python export_projects_to_csv.py
```

**Output Location:** `data/exports/projects_export_YYYY-MM-DD_HHMMSS.csv`

---

### **Update Commands**

```bash
# Update existing projects only (safe default)
python update_projects_from_csv.py projects.csv

# Preview changes without updating
python update_projects_from_csv.py projects.csv --preview

# Validate data only (dry run)
python update_projects_from_csv.py projects.csv --validate-only

# Update existing and create new projects
python update_projects_from_csv.py projects.csv --create-new
```

---

## 📊 What Can You Update?

### ✅ **Updatable Fields**

**Basic Info:**
- name, description, status, notes

**Timeline:**
- quote_date, approval_date, due_date, completion_date, scheduled_cut_date

**Pricing:**
- quoted_price, final_price

**Material:**
- material_type, material_thickness, material_quantity_sheets, parts_quantity

**Production:**
- estimated_cut_time, drawing_creation_time, number_of_bins

**POP Tracking:**
- pop_received, pop_received_date, pop_deadline

**Notifications:**
- client_notified, client_notified_date

**Delivery:**
- delivery_confirmed, delivery_confirmed_date

### ❌ **Cannot Update**
- project_code (used for matching)
- client_code (cannot move project to different client)
- created_at, updated_at (auto-managed)
- design_files_count, documents_count (read-only)

---

## 🎯 Common Tasks

### **Update Project Statuses**
1. Export: `python export_projects_to_csv.py`
2. Open CSV in Excel
3. Change `status` column (e.g., "Completed" → "In Progress")
4. Save file
5. Preview: `python update_projects_from_csv.py file.csv --preview`
6. Apply: `python update_projects_from_csv.py file.csv`

### **Update Prices**
1. Export projects
2. Update `quoted_price` or `final_price` columns
3. Preview and apply

### **Add Material Information**
1. Export projects
2. Fill in `material_type`, `material_thickness_mm`, `parts_quantity`
3. Preview and apply

### **Update Due Dates**
1. Export projects
2. Update `due_date` column (format: YYYY-MM-DD)
3. Preview and apply

---

## 📝 Data Format Tips

### **Dates**
✅ **Correct:**
- `2025-10-17`
- `17/10/2025`
- `10/17/2025`

❌ **Incorrect:**
- `Oct 17, 2025`
- `17-Oct-2025`

### **Booleans**
✅ **Correct:**
- `Yes` / `No`
- `true` / `false`
- `1` / `0`
- `Y` / `N`

❌ **Incorrect:**
- `TRUE` / `FALSE` (works but use lowercase)
- `X` / blank

### **Numbers**
✅ **Correct:**
- `1500.00`
- `1500`
- `1,500.00` (commas removed automatically)

❌ **Incorrect:**
- `$1500`
- `R1500`

---

## ⚠️ Important Notes

### **Required Field**
- `project_code` - **MUST** be present to match existing projects

### **Column Names**
- Script auto-maps different column name formats
- `project_name` → `name` (automatic)
- `estimated_cut_time_minutes` → `estimated_cut_time` (automatic)
- No need to rename columns!

### **Safety**
- Always use `--preview` first to see what will change
- Changes are transactional (all or nothing)
- Errors are logged and reported

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Project not found" | Check project_code is correct, or use `--create-new` |
| "No changes detected" | Verify you changed values in CSV |
| "Could not parse date" | Use format YYYY-MM-DD |
| "Boolean not recognized" | Use Yes/No, true/false, or 1/0 |

---

## 📊 Example Workflow

### **Scenario: Update 10 projects to "In Progress" status**

```bash
# Step 1: Export
python export_projects_to_csv.py

# Step 2: Edit in Excel
# - Open data/exports/projects_export_2025-10-17_090915.csv
# - Filter to the 10 projects you want
# - Change status column to "In Progress"
# - Save file

# Step 3: Preview
python update_projects_from_csv.py data/exports/projects_export_2025-10-17_090915.csv --preview

# Output shows:
# Project: JB-2025-10-CL0005-014
#   status: Completed → In Progress
# ... (9 more)

# Step 4: Apply
python update_projects_from_csv.py data/exports/projects_export_2025-10-17_090915.csv

# Output shows:
# ✅ Projects Updated: 10
# ⏭️  Projects Skipped (no changes): 39
```

---

## 📈 Summary Statistics

After update, you'll see:

```
======================================================================
UPDATE SUMMARY
======================================================================

✅ Projects Updated: 10        ← Successfully updated
➕ Projects Created: 0         ← New projects (with --create-new)
⏭️  Projects Skipped: 39       ← No changes detected
❓ Projects Not Found: 0       ← project_code not in database

======================================================================
```

---

## 🎉 Quick Tips

1. **Always preview first:** `--preview` flag shows changes without applying
2. **Use Excel formulas:** Calculate values, find/replace, etc.
3. **Filter in Excel:** Only update specific projects
4. **Keep backups:** Export creates timestamped files automatically
5. **Check summary:** Review statistics after update

---

## 📞 Need Help?

### **View Help:**
```bash
python update_projects_from_csv.py --help
```

### **Common Commands:**
```bash
# Export
python export_projects_to_csv.py

# Preview update
python update_projects_from_csv.py file.csv --preview

# Apply update
python update_projects_from_csv.py file.csv

# Create new projects too
python update_projects_from_csv.py file.csv --create-new
```

---

**That's it! Export → Edit → Re-Import made easy! 🚀**

