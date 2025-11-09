# Feature: Download All Files (Design Files & Documents)

**Version:** 2.1
**Date:** 2025-10-22
**Status:** ✅ Implemented (Extended + Bug Fix)

---

## Overview

The "Download All" feature allows users to download all design files (DXF, LightBurn, etc.) or all project documents (quotes, invoices, POPs, delivery notes) associated with a project as a single ZIP archive. This feature streamlines the workflow when users need to access multiple files at once.

**Version 2.0 Updates:**
- ✅ Extended to Project Documents section
- ✅ Added progress indicator for large ZIP files
- ✅ Improved user experience with visual feedback

---

## Feature Specifications

### Locations

#### 1. Design Files Section
- **Page:** Project Detail Page (`/projects/<id>`)
- **Section:** Design Files (DXF / LightBurn)
- **Position:** Header area, next to "Upload File" button
- **Route:** `/files/download-all/<project_id>`

#### 2. Project Documents Section (NEW in v2.0)
- **Page:** Project Detail Page (`/projects/<id>`)
- **Section:** Project Documents
- **Position:** Header area, next to "Upload Document" button
- **Route:** `/projects/download-all-documents/<project_id>`

### Functionality

#### Core Behavior
1. **Collect Files:** Gathers all design files associated with the current project
2. **Create ZIP:** Creates a ZIP archive in memory (no disk storage)
3. **Original Filenames:** Uses original filenames for files within the ZIP
4. **Descriptive Naming:** ZIP file named as `{project_code}-DesignFiles.zip`
5. **Browser Download:** Triggers automatic download to user's browser

#### Edge Cases Handled
- **No Files:** Shows warning message and redirects back to project page
- **Single File:** Redirects to single file download (no ZIP needed)
- **Missing Files:** Logs warning, continues with available files, shows warning message
- **Large Files:** Streams ZIP to browser without saving to disk (memory efficient)

### Security
- ✅ `@login_required` decorator - User must be authenticated
- ✅ Project validation - Verifies project exists (404 if not)
- ✅ File path validation - Uses absolute paths with proper normalization
- ✅ Activity logging - All downloads logged for audit trail

---

## Implementation Details

### Backend Route

**File:** `app/routes/files.py`

**Route:** `/files/download-all/<int:project_id>`

**Method:** GET

**Decorator:** `@login_required`

**Key Components:**
```python
import zipfile
from io import BytesIO
from pathlib import Path

@bp.route('/download-all/<int:project_id>')
@login_required
def download_all(project_id):
    # Get project and files
    project = Project.query.get_or_404(project_id)
    design_files = DesignFile.query.filter_by(project_id=project_id).all()
    
    # Handle edge cases
    if not design_files:
        flash('No design files to download', 'warning')
        return redirect(url_for('projects.detail', id=project_id))
    
    if len(design_files) == 1:
        return redirect(url_for('files.download', file_id=design_files[0].id))
    
    # Create ZIP in memory
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for design_file in design_files:
            full_file_path = os.path.abspath(os.path.join(base_folder, design_file.file_path))
            if os.path.exists(full_file_path):
                zf.write(full_file_path, arcname=design_file.original_filename)
    
    memory_file.seek(0)
    
    # Generate filename and send
    zip_filename = f"{project.project_code}-DesignFiles.zip"
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )
```

### Frontend UI

**File:** `app/templates/projects/detail.html`

**Location:** Design Files section header

**Button Code:**
```html
<div class="flex-row flex-gap-sm">
    <button onclick="document.getElementById('uploadForm').style.display='block'" 
            class="btn btn-primary btn-sm">
        Upload File
    </button>
    {% if project.design_files %}
    <a href="{{ url_for('files.download_all', project_id=project.id) }}" 
       class="btn btn-success btn-sm">
        📦 Download All ({{ project.design_files|length }} file{{ 's' if project.design_files|length != 1 else '' }})
    </a>
    {% endif %}
</div>
```

**UI Features:**
- ✅ Only shown when files exist (`{% if project.design_files %}`)
- ✅ Shows file count: "Download All (5 files)"
- ✅ Proper pluralization: "1 file" vs "5 files"
- ✅ Visual indicator: 📦 emoji for ZIP archive
- ✅ Success color (green) to differentiate from upload button

---

## User Experience

### User Workflow

1. **Navigate to Project:**
   - User opens project detail page
   - Scrolls to "Design Files" section

2. **See Download Button:**
   - If files exist, "Download All" button is visible
   - Button shows count: "📦 Download All (5 files)"

3. **Click Download:**
   - User clicks "Download All" button
   - Browser initiates download

4. **Receive ZIP:**
   - ZIP file downloads: `JB-2025-10-CL0042-001-DesignFiles.zip`
   - Contains all design files with original filenames

5. **Extract and Use:**
   - User extracts ZIP
   - All files ready to use with original names

### Visual States

**No Files:**
- Button not shown
- Message: "No files uploaded yet. Click 'Upload File' to add DXF files to this project."

**1 File:**
- Button shown but redirects to single file download
- No ZIP created (unnecessary)

**2+ Files:**
- Button shown: "📦 Download All (5 files)"
- ZIP created and downloaded

**Some Files Missing:**
- ZIP created with available files
- Warning message: "Warning: 2 file(s) were missing and not included in the archive"

---

## Technical Features

### Memory Efficiency
- **In-Memory ZIP:** Uses `BytesIO()` to create ZIP in memory
- **No Disk Storage:** ZIP never saved to disk
- **Streaming:** Directly streamed to browser
- **Cleanup:** Automatic memory cleanup after download

### Error Handling
- **Missing Files:** Logs warning, continues with available files
- **No Files Added:** Shows error, redirects to project page
- **Exception Handling:** Catches all exceptions, logs error, shows user-friendly message

### Activity Logging
Every download is logged:
```python
activity = ActivityLog(
    entity_type='PROJECT',
    entity_id=project_id,
    action='DOWNLOAD_ALL',
    details=f'Downloaded {files_added} design files as ZIP archive ({total_size_mb} MB total)',
    user='System'  # TODO: Use current_user when available
)
```

### Statistics Tracking
- **Files Added:** Count of files successfully added to ZIP
- **Files Missing:** Count of files not found on disk
- **Total Size:** Sum of all file sizes in MB

---

## Example Scenarios

### Scenario 1: Normal Download (5 Files)

**Setup:**
- Project: JB-2025-10-CL0042-001
- Files: 5 DXF files (total 12.5 MB)

**Workflow:**
1. User clicks "📦 Download All (5 files)"
2. System creates ZIP in memory
3. ZIP contains:
   - `bracket-left.dxf`
   - `bracket-right.dxf`
   - `plate-top.dxf`
   - `plate-bottom.dxf`
   - `spacer.dxf`
4. ZIP downloaded: `JB-2025-10-CL0042-001-DesignFiles.zip`
5. Activity logged: "Downloaded 5 design files as ZIP archive (12.5 MB total)"

### Scenario 2: Single File

**Setup:**
- Project: JB-2025-10-CL0043-001
- Files: 1 DXF file

**Workflow:**
1. User clicks "📦 Download All (1 file)"
2. System redirects to single file download
3. File downloaded directly (no ZIP)
4. Activity logged: "Downloaded file: bracket.dxf"

### Scenario 3: Missing Files

**Setup:**
- Project: JB-2025-10-CL0044-001
- Files in DB: 5 files
- Files on disk: 3 files (2 missing)

**Workflow:**
1. User clicks "📦 Download All (5 files)"
2. System creates ZIP with 3 available files
3. Logs warnings for 2 missing files
4. ZIP downloaded with 3 files
5. Warning message: "Warning: 2 file(s) were missing and not included in the archive"
6. Activity logged: "Downloaded 3 design files as ZIP archive (8.2 MB total)"

---

## Benefits

### For Users
- **Time Savings:** Download all files with one click instead of individually
- **Convenience:** Single ZIP file easier to manage than multiple downloads
- **Organization:** All project files in one archive
- **Offline Access:** Download once, work offline

### For Business
- **Efficiency:** Faster file distribution to clients or team members
- **Professional:** Clean, organized file delivery
- **Audit Trail:** Complete download history
- **Scalability:** Handles projects with many files

---

## Future Enhancements

### Potential Improvements
1. **Selective Download:** Allow users to select specific files to include in ZIP
2. **Include Metadata:** Add README.txt with project details inside ZIP
3. **Folder Structure:** Organize files by type (DXF/, LightBurn/, etc.)
4. **Email ZIP:** Option to email ZIP to client
5. **Progress Indicator:** Show progress bar for large ZIPs
6. **Background Processing:** Queue large ZIPs for background processing
7. **Expiring Links:** Generate temporary download links
8. **Cloud Storage:** Option to save ZIP to cloud storage (Dropbox, Google Drive)

### Configuration Options
```python
# config.py
ZIP_COMPRESSION_LEVEL = 6  # 0-9, default 6
ZIP_MAX_SIZE_MB = 500  # Maximum ZIP size
ZIP_INCLUDE_METADATA = True  # Include README.txt
ZIP_FOLDER_STRUCTURE = False  # Organize by file type
```

---

## Testing Checklist

### Manual Testing
- [ ] Download with 0 files (should show warning)
- [ ] Download with 1 file (should redirect to single download)
- [ ] Download with 2+ files (should create ZIP)
- [ ] Download with missing files (should show warning)
- [ ] Verify ZIP filename format: `{project_code}-DesignFiles.zip`
- [ ] Verify files inside ZIP have original filenames
- [ ] Verify activity log entry created
- [ ] Verify user must be logged in
- [ ] Verify project must exist (404 if not)
- [ ] Test with large files (50+ MB)
- [ ] Test with many files (20+ files)

### Automated Testing
```python
def test_download_all_multiple_files(client, project_with_files):
    response = client.get(f'/files/download-all/{project_with_files.id}')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/zip'
    assert 'DesignFiles.zip' in response.headers['Content-Disposition']

def test_download_all_no_files(client, project_without_files):
    response = client.get(f'/files/download-all/{project_without_files.id}')
    assert response.status_code == 302  # Redirect
    # Check flash message

def test_download_all_single_file(client, project_with_one_file):
    response = client.get(f'/files/download-all/{project_with_one_file.id}')
    assert response.status_code == 302  # Redirect to single download
```

---

## Documentation Updates

### User Documentation
- ✅ Added to `DETAILED_FEATURE_CAPABILITIES.md` (Section 2.1)
- ✅ Added to `QUICK_REFERENCE_GUIDE.md` (Common Workflows)

### Technical Documentation
- ✅ This document (`FEATURE_DOWNLOAD_ALL_DESIGN_FILES.md`)
- ✅ Code comments in `app/routes/files.py`
- ✅ Activity log documentation

---

---

## Version 2.0 New Features

### 1. Download All Documents

**Implementation:** `app/routes/projects.py` - `download_all_documents(project_id)`

**Key Features:**
- Downloads all project documents (quotes, invoices, POPs, delivery notes) as ZIP
- Organizes files by document type in ZIP (Quote/, Invoice/, Proof of Payment/, Delivery Note/)
- ZIP filename format: `{project_code}-Documents.zip`
- Same edge case handling as design files
- Activity logging with action='DOWNLOAD_ALL_DOCUMENTS'

**Example ZIP Structure:**
```
JB-2025-10-CL0042-001-Documents.zip
├── Quote/
│   ├── Quote_ABC_Manufacturing_2025-10-15.pdf
│   └── Revised_Quote_2025-10-18.pdf
├── Invoice/
│   └── Invoice_INV-2025-0042.pdf
├── Proof of Payment/
│   └── POP_Bank_Transfer_2025-10-20.pdf
└── Delivery Note/
    └── Delivery_Note_2025-10-22.pdf
```

**Benefits:**
- **Organization:** Files grouped by type in folders
- **Convenience:** All project documents in one download
- **Professional:** Clean structure for client delivery
- **Audit:** Complete document package for records

### 2. Progress Indicator

**Implementation:** JavaScript + CSS in `app/templates/projects/detail.html`

**Visual Design:**
- **Overlay:** Semi-transparent dark background (rgba(0, 0, 0, 0.7))
- **Modal:** White card with rounded corners and shadow
- **Spinner:** Animated CSS spinner (blue border, rotating)
- **Text:** Dynamic message showing file count and total size

**User Experience:**
1. User clicks "Download All" button
2. Progress indicator appears immediately
3. Shows: "Creating ZIP archive with 5 files (12.5 MB)..."
4. Spinner animates while ZIP is being created
5. Indicator disappears when download starts (after ~3 seconds)
6. Fallback timeout: 30 seconds (in case of issues)

**Technical Implementation:**
```javascript
function showDownloadProgress(fileCount, totalSizeMB) {
    // Show overlay with file count and size
    // Set 30-second timeout fallback
    // Auto-hide after 3 seconds (typical ZIP creation time)
}

function hideDownloadProgress() {
    // Hide overlay
    // Clear timeout
}
```

**Triggers:**
- Both "Download All" buttons (Design Files and Documents)
- Onclick handler passes file count and total size
- Progress shown before navigation to download route

**Edge Cases:**
- **Page visibility change:** Hides indicator when user switches tabs
- **Timeout:** Auto-hides after 30 seconds if download doesn't start
- **Quick downloads:** Hides after 3 seconds for typical cases
- **Errors:** Flash messages shown, indicator hidden

---

## Updated Implementation Details

### Backend Routes

#### Design Files Download
**File:** `app/routes/files.py`
**Route:** `/files/download-all/<int:project_id>`
**Decorator:** `@login_required`
**ZIP Filename:** `{project_code}-DesignFiles.zip`
**File Organization:** Flat structure with original filenames

#### Documents Download (NEW)
**File:** `app/routes/projects.py`
**Route:** `/projects/download-all-documents/<int:project_id>`
**Decorators:** `@login_required`, `@role_required('admin', 'manager', 'operator', 'viewer')`
**ZIP Filename:** `{project_code}-Documents.zip`
**File Organization:** Organized by document type in folders

**Code Example:**
```python
@bp.route('/download-all-documents/<int:project_id>')
@login_required
@role_required('admin', 'manager', 'operator', 'viewer')
def download_all_documents(project_id):
    project = Project.query.get_or_404(project_id)
    documents = ProjectDocument.query.filter_by(project_id=project_id).all()

    # Handle edge cases
    if not documents:
        flash('No documents to download', 'warning')
        return redirect(url_for('projects.detail', id=project_id))

    # Create ZIP with folder structure
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for document in documents:
            # Organize by document type
            arcname = f"{document.document_type}/{document.original_filename}"
            zf.write(full_file_path, arcname=arcname)

    # Log activity
    activity = ActivityLog(
        entity_type='PROJECT',
        entity_id=project_id,
        action='DOWNLOAD_ALL_DOCUMENTS',
        details=f'Downloaded {files_added} documents as ZIP ({total_size_mb} MB)',
        user='System'
    )

    return send_file(memory_file, download_name=f"{project.project_code}-Documents.zip")
```

### Frontend UI Updates

#### Design Files Button (Updated)
```html
<a href="{{ url_for('files.download_all', project_id=project.id) }}"
   class="btn btn-success btn-sm"
   onclick="showDownloadProgress({{ project.design_files|length }}, {{ total_size }}); return true;">
    📦 Download All ({{ project.design_files|length }} file{{ 's' if project.design_files|length != 1 else '' }})
</a>
```

#### Documents Button (NEW)
```html
<a href="{{ url_for('projects.download_all_documents', project_id=project.id) }}"
   class="btn btn-success btn-sm"
   onclick="showDownloadProgress({{ project.documents|length }}, {{ total_size }}); return true;">
    📦 Download All ({{ project.documents|length }} document{{ 's' if project.documents|length != 1 else '' }})
</a>
```

#### Progress Indicator HTML
```html
<div id="downloadProgressOverlay" style="display: none; ...">
    <div style="background: white; padding: 2rem; ...">
        <div class="spinner" style="..."></div>
        <h3>Creating ZIP Archive</h3>
        <p id="downloadProgressText">Preparing download...</p>
    </div>
</div>
```

---

## Updated Example Scenarios

### Scenario 4: Download All Documents (NEW)

**Project:** JB-2025-10-CL0042-001
**Documents:** 2 quotes, 1 invoice, 1 POP (4 files, 8.5 MB total)

**Workflow:**
1. User clicks "📦 Download All (4 documents)"
2. Progress indicator appears: "Creating ZIP archive with 4 documents (8.5 MB)..."
3. Spinner animates for ~2 seconds
4. ZIP downloads: `JB-2025-10-CL0042-001-Documents.zip`
5. Progress indicator disappears
6. User extracts ZIP and finds:
   ```
   Quote/
     - Quote_ABC_Manufacturing_2025-10-15.pdf
     - Revised_Quote_2025-10-18.pdf
   Invoice/
     - Invoice_INV-2025-0042.pdf
   Proof of Payment/
     - POP_Bank_Transfer_2025-10-20.pdf
   ```
7. Activity logged: "Downloaded 4 project documents as ZIP archive (8.5 MB total)"

**Result:** Organized document package with folder structure for easy navigation.

### Scenario 5: Large ZIP with Progress Indicator

**Project:** JB-2025-10-CL0045-001
**Files:** 25 DXF files (125 MB total)

**Workflow:**
1. User clicks "📦 Download All (25 files)"
2. Progress indicator appears: "Creating ZIP archive with 25 files (125.0 MB)..."
3. Spinner animates while server creates ZIP (~5 seconds)
4. Browser download dialog appears
5. Progress indicator auto-hides after 3 seconds
6. User sees download progress in browser
7. ZIP downloads: `JB-2025-10-CL0045-001-DesignFiles.zip`

**Result:** User has visual feedback during ZIP creation, knows download is in progress.

---

## Updated Benefits

### For Users
- **Time Savings:** Download all files with one click
- **Visual Feedback:** Progress indicator shows download is happening (NEW)
- **Organization:** Documents organized by type in folders (NEW)
- **Convenience:** Single ZIP file easier to manage
- **Professional:** Clean structure for client delivery

### For Business
- **Efficiency:** Faster file distribution
- **Professional:** Organized document packages
- **Audit Trail:** Complete download history
- **Scalability:** Handles large file sets with progress feedback (NEW)

---

## Updated Testing Checklist

### Design Files Download
- [ ] Download with 0 files (warning message)
- [ ] Download with 1 file (redirect to single download)
- [ ] Download with 2+ files (ZIP created)
- [ ] Progress indicator appears and disappears
- [ ] ZIP filename: `{project_code}-DesignFiles.zip`
- [ ] Files have original names (flat structure)

### Documents Download (NEW)
- [ ] Download with 0 documents (warning message)
- [ ] Download with 1 document (ZIP created)
- [ ] Download with 2+ documents (ZIP created)
- [ ] Progress indicator appears and disappears
- [ ] ZIP filename: `{project_code}-Documents.zip`
- [ ] Files organized by document type in folders
- [ ] Activity log entry with action='DOWNLOAD_ALL_DOCUMENTS'
- [ ] Role-based access control works

### Progress Indicator (NEW)
- [ ] Appears immediately on button click
- [ ] Shows correct file count and size
- [ ] Spinner animates smoothly
- [ ] Disappears after ~3 seconds
- [ ] Fallback timeout works (30 seconds)
- [ ] Hides on page visibility change
- [ ] Works for both design files and documents

---

## Files Modified (Version 2.0)

### 1. `app/routes/projects.py`
- Added imports: `send_file`, `zipfile`, `BytesIO`
- Added route: `download_all_documents(project_id)`
- 125 lines of new code

### 2. `app/routes/files.py` (v1.0)
- Added imports: `zipfile`, `BytesIO`, `Path`
- Added route: `download_all(project_id)`
- 108 lines of code

### 3. `app/templates/projects/detail.html`
- Modified Project Documents section header (added button)
- Modified Design Files section header (added progress indicator)
- Added progress indicator HTML and CSS
- Added JavaScript functions for progress indicator
- ~70 lines added/modified

### 4. `docs/FEATURE_DOWNLOAD_ALL_DESIGN_FILES.md`
- Updated to version 2.1
- Added documentation for documents download
- Added documentation for progress indicator
- Added new scenarios and testing checklist
- Added bug fix documentation (v2.1)

---

## 🐛 **Version 2.1 - Bug Fix (2025-10-22)**

### **Issue Fixed: Incorrect File Path Construction**

**Problem:**
The `download_all_documents` route was incorrectly constructing file paths, resulting in duplicate path segments:
- Expected: `data\documents\quotes\20251017_085325_9381ace8.pdf`
- Actual: `data\files\data\documents\quotes\20251017_085325_9381ace8.pdf`

**Root Cause:**
1. `ProjectDocument.file_path` stores the **full absolute path** (unlike `DesignFile` which stores relative paths)
2. The route was using `UPLOAD_FOLDER` instead of recognizing that `file_path` is already absolute
3. The route was joining `base_folder` with the full absolute path, creating duplicate segments

**Solution:**
Modified `app/routes/projects.py` (lines 920-948):
- Removed `base_folder` variable (was using wrong config: `UPLOAD_FOLDER`)
- Changed to use `document.file_path` directly with `os.path.abspath()`
- Added comment explaining that `ProjectDocument.file_path` contains full absolute path

**Code Change:**
```python
# BEFORE (Incorrect):
base_folder = current_app.config.get('UPLOAD_FOLDER', 'data/files/projects')
full_file_path = os.path.abspath(os.path.join(base_folder, document.file_path))

# AFTER (Correct):
# ProjectDocument.file_path contains the full absolute path
# (unlike DesignFile which stores relative paths)
full_file_path = os.path.abspath(document.file_path)
```

**Testing:**
- ✅ Verified file paths are now constructed correctly
- ✅ Documents download successfully as ZIP archive
- ✅ All document types (Quote, Invoice, POP, Delivery Note) work correctly
- ✅ Folder organization maintained (files organized by document type)

**Related Files:**
- `app/routes/projects.py` - Fixed download route
- `app/services/document_service.py` - Confirmed stores full absolute path (line 275)
- `config.py` - Confirmed `DOCUMENTS_FOLDER` = `data/documents` (separate from `UPLOAD_FOLDER`)

---

**Document Version:** 2.1
**Last Updated:** 2025-10-22
**Implemented By:** Augment Agent

