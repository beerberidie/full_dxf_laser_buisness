# Where to Upload DXF and LightBurn Files to Products

## 📍 Location of File Upload

The file upload functionality for products is available in **TWO locations**:

---

## ✅ Option 1: Product Detail Page (Recommended)

This is the **main location** for uploading files.

### How to Access:
1. Go to **Products** (in navigation)
2. Click on any product to view its details
3. Scroll down to the **"Product Files"** section
4. Click the **"Upload File"** button
5. The upload form will appear
6. Select your .dxf or .lbrn2 file
7. Add optional notes
8. Click **"Upload"**

### Features:
- ✅ Upload multiple files
- ✅ See all uploaded files in a table
- ✅ Download files
- ✅ Delete files
- ✅ View file details (type, size, date)

---

## ✅ Option 2: Product Edit Page

You can also upload files when **editing** an existing product.

### How to Access:
1. Go to **Products** (in navigation)
2. Click **"Edit"** on any product
3. Scroll down to the **"Design Files"** section
4. You'll see:
   - List of current files (if any)
   - **"+ Add File"** button
5. Click **"+ Add File"**
6. The upload form will appear
7. Select your .dxf or .lbrn2 file
8. Add optional notes
9. Click **"Upload File"**

### Features:
- ✅ Upload files while editing product info
- ✅ See current files
- ✅ Download or delete existing files
- ✅ All in one place

---

## ❌ NOT Available: New Product Page

**Important:** You **cannot** upload files when creating a **new** product.

### Why?
- The product must exist in the database first (needs a product ID)
- Files are associated with a specific product ID
- The ID is only generated after saving the product

### What You'll See:
When creating a new product, you'll see this message:

```
Design Files
ℹ️ Note: You can upload DXF and LightBurn files after creating the product.
```

### Workflow:
1. Create the product first (fill in name, material, thickness, etc.)
2. Click **"Create Product"**
3. You'll be redirected to the product detail page
4. Now you can upload files using the **"Upload File"** button

---

## 🎯 Quick Guide: Upload Your First File

### Step-by-Step:

1. **Go to Products List:**
   - Click **"Products"** in the top navigation
   - URL: `http://127.0.0.1:5000/products/`

2. **Choose a Product:**
   - If you have products: Click on any product name or **"View"** button
   - If no products: Click **"+ New Product"** to create one first

3. **Find the Upload Section:**
   - On the product detail page, scroll down
   - Look for the **"Product Files"** card
   - You'll see a count like "Product Files (0)" or "Product Files (2)"

4. **Upload a File:**
   - Click the **"Upload File"** button (blue button in the card header)
   - A form will appear below
   - Click **"Select File"** and choose your .dxf or .lbrn2 file
   - (Optional) Add notes like "Original design" or "Version 2"
   - Click **"Upload"**

5. **Success!**
   - The file will appear in the files table
   - You'll see: filename, type badge, size, upload date
   - You can now download or delete it

---

## 📊 Visual Layout

### Product Detail Page Structure:

```
┌─────────────────────────────────────────┐
│ Product Information                     │
│ • SKU Code: PRD-001                     │
│ • Name: Test Bracket                    │
│ • Material: Mild Steel                  │
│ • Thickness: 3.0mm                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Product Files (2)    [Upload File] ←──  │ Click here!
├─────────────────────────────────────────┤
│                                         │
│ 📄 bracket_v1.dxf                       │
│    DXF | 2.5 MB | 2025-10-16 12:30     │
│    [Download] [Delete]                  │
│                                         │
│ 📄 bracket_v2.lbrn2                     │
│    LBRN2 | 1.8 MB | 2025-10-16 13:45   │
│    [Download] [Delete]                  │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Projects Using This Product             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Activity Log                            │
└─────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### "I don't see the Upload File button"

**Check:**
1. Are you on the **product detail page**? (URL should be `/products/1` or similar)
2. Scroll down - the "Product Files" section is below "Product Information"
3. Make sure you're not on the product **list** page (that only shows file counts)

### "I can't upload files on the New Product page"

**Solution:**
- This is expected behavior
- Create the product first, then upload files
- See the workflow above

### "The upload form doesn't appear"

**Check:**
1. Did you click the **"Upload File"** button?
2. The form is hidden by default and appears when you click the button
3. Try refreshing the page

### "Upload fails"

**Check:**
1. File extension must be .dxf or .lbrn2
2. File size must be under 50 MB
3. Make sure you selected a file

---

## 📝 File Upload Locations Summary

| Location | Can Upload? | When to Use |
|----------|-------------|-------------|
| **New Product Page** | ❌ No | N/A - Create product first |
| **Product Detail Page** | ✅ Yes | **Best option** - Full file management |
| **Product Edit Page** | ✅ Yes | When editing product info |
| **Product List Page** | ❌ No | Only shows file counts |

---

## 🎨 What You'll See

### On Product List Page:
- **Files column** shows: "2 file(s)" in a blue badge
- Click on product to see/manage files

### On Product Detail Page:
- **"Product Files (X)"** card with upload button
- Table of all files with download/delete buttons
- Upload form (appears when you click "Upload File")

### On Product Edit Page:
- **"Design Files"** section at the bottom
- List of current files
- **"+ Add File"** button to upload more

---

## ✅ Quick Checklist

To upload a file, you need:
- [ ] An existing product (create one if needed)
- [ ] A .dxf or .lbrn2 file (under 50 MB)
- [ ] To be on the product detail or edit page
- [ ] To click the "Upload File" or "+ Add File" button

---

**Need Help?**
- See `QUICK_START_PRODUCT_FILES.md` for detailed guide
- See `PRODUCT_FILES_IMPLEMENTATION.md` for technical details

---

**Happy uploading!** 📁✨

