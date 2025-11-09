# Quick Start Guide - Product File Uploads

## 🚀 Getting Started in 5 Minutes

### Step 1: Verify Installation
```bash
# Run the test script
python test_product_files.py
```

**Expected Output:**
```
✅ ALL CRITICAL TESTS PASSED
Product file upload functionality is ready!
```

---

### Step 2: Start the Server
```bash
python app.py
```

Navigate to: `http://localhost:5000`

---

### Step 3: Create a Product (if needed)

1. Click **"Products"** in navigation
2. Click **"+ New Product"**
3. Fill in:
   - **Name:** "Test Bracket"
   - **SKU Code:** "BRK-001"
   - **Material:** Select "Mild Steel"
   - **Thickness:** 3.0
4. Click **"Create Product"**

---

### Step 4: Upload Your First File

1. On the product detail page, click **"Upload File"**
2. The upload form will appear
3. Click **"Select File"** and choose a .dxf or .lbrn2 file
4. (Optional) Add notes like "Original design file"
5. Click **"Upload"**

**Success!** Your file is now uploaded and appears in the files table.

---

### Step 5: Download a File

1. Find the file in the files table
2. Click the **"Download"** button
3. File downloads with its original filename

---

### Step 6: Delete a File

1. Find the file in the files table
2. Click the **"Delete"** button
3. Confirm the deletion
4. File is removed from both database and disk

---

## 📋 Features at a Glance

### ✅ What You Can Do

- **Upload Files:** .dxf and .lbrn2 files up to 50 MB
- **Multiple Files:** Each product can have multiple files
- **Download Files:** Download with original filename
- **Delete Files:** Remove files you no longer need
- **Add Notes:** Optional notes for each file
- **View File Info:** See file type, size, upload date
- **Track Activity:** All file operations are logged

### 📊 Where to Find Things

**Product List Page:**
- Shows file count badge for products with files
- Blue badge shows number of files

**Product Detail Page:**
- "Product Files" card shows all files
- Upload button to add new files
- Files table with download/delete actions

**Activity Log:**
- Shows all file operations
- Upload, download, and delete events

---

## 🎯 Common Tasks

### Upload Multiple Files to One Product

1. Go to product detail page
2. Click "Upload File"
3. Select first file, add notes, upload
4. Click "Upload File" again
5. Select second file, add notes, upload
6. Repeat as needed

### Replace a File

1. Download the old file (backup)
2. Delete the old file
3. Upload the new file with same/similar name

### Organize Files with Notes

When uploading, use notes to describe:
- "Original customer design"
- "Modified for production"
- "Version 2 - updated dimensions"
- "Final approved design"

---

## 🔍 Troubleshooting

### Upload Fails

**Problem:** "Only DXF and LightBurn (.lbrn2) files are allowed"
- **Solution:** Check file extension is .dxf or .lbrn2

**Problem:** File too large
- **Solution:** Maximum file size is 50 MB

### Download Fails

**Problem:** "File not found on disk"
- **Solution:** File may have been manually deleted from disk
- Check `data/files/products/{product_id}/` folder

### Delete Fails

**Problem:** Permission error
- **Solution:** Check file permissions on the files folder

---

## 📁 File Storage Structure

```
data/
└── files/
    └── products/
        ├── 1/
        │   ├── 20251016_143022_a1b2c3d4.dxf
        │   └── 20251016_143045_e5f6g7h8.lbrn2
        ├── 2/
        │   └── 20251016_144000_i9j0k1l2.dxf
        └── 3/
            └── 20251016_145000_m3n4o5p6.lbrn2
```

**Structure:**
- Each product has its own folder (product ID)
- Files have unique names (timestamp + UUID)
- Original filenames stored in database

---

## 🔐 Security Notes

**File Validation:**
- Only .dxf and .lbrn2 files accepted
- File size limited to 50 MB
- Filenames sanitized for security

**File Storage:**
- Files stored outside web root
- Unique filenames prevent overwrites
- Relative paths in database

---

## 📊 Database Tables

### product_files Table

Stores metadata about uploaded files:

| Field | Description |
|-------|-------------|
| id | Unique file ID |
| product_id | Which product owns this file |
| original_filename | Original name when uploaded |
| stored_filename | Unique name on disk |
| file_path | Relative path to file |
| file_size | Size in bytes |
| file_type | 'dxf' or 'lbrn2' |
| upload_date | When uploaded |
| uploaded_by | Who uploaded (future feature) |
| notes | Optional notes |

---

## 🎨 UI Elements

### File Type Badges

- **DXF Files:** Blue badge with "DXF"
- **LightBurn Files:** Green badge with "LBRN2"

### File Count Badge

- **Products List:** Blue badge showing "X file(s)"
- Only shown if product has files

### Upload Form

- Hidden by default
- Click "Upload File" to show
- Click "Cancel" to hide

---

## 📝 Activity Logging

All file operations are logged:

**FILE_UPLOADED:**
```
Uploaded file: bracket_design.dxf (2.5 MB) to product BRK-001
```

**FILE_DOWNLOADED:**
```
Downloaded file: bracket_design.dxf
```

**FILE_DELETED:**
```
Deleted file: bracket_design.dxf
```

---

## 🧪 Testing Checklist

Use this checklist to verify everything works:

- [ ] Upload a .dxf file
- [ ] Upload a .lbrn2 file
- [ ] Add notes to a file
- [ ] Download a file
- [ ] Delete a file
- [ ] View file count in product list
- [ ] Check activity log shows file operations
- [ ] Try uploading invalid file type (should fail)
- [ ] Upload multiple files to one product
- [ ] Verify files persist after server restart

---

## 📞 Need Help?

**Documentation:**
- `PRODUCT_FILES_IMPLEMENTATION.md` - Detailed technical documentation
- `PRODUCTS_ENHANCEMENT_SUMMARY.md` - Complete summary of changes

**Test Script:**
```bash
python test_product_files.py
```

**Check Database:**
```bash
sqlite3 data/laser_os.db
sqlite> SELECT * FROM product_files;
```

**Check Files on Disk:**
```bash
# Windows
dir data\files\products

# Linux/Mac
ls -la data/files/products
```

---

## ✅ Quick Verification

**Is it working?**

1. ✅ Test script passes
2. ✅ Can upload .dxf file
3. ✅ Can upload .lbrn2 file
4. ✅ Can download file
5. ✅ Can delete file
6. ✅ File count shows in product list
7. ✅ Activity log shows operations

**If all checked:** 🎉 **You're ready to go!**

---

## 🚀 Production Deployment

**Before deploying:**

1. ✅ Run test script
2. ✅ Test all file operations
3. ✅ Verify file permissions
4. ✅ Check disk space
5. ✅ Backup database
6. ✅ Test with real files

**After deploying:**

1. Monitor disk usage
2. Check activity logs
3. Verify file uploads work
4. Test downloads work
5. Ensure backups include files folder

---

**Happy file uploading!** 📁✨

