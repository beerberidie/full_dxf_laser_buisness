# Code Changes Summary
**Date:** 2025-10-16  
**Project:** Laser OS Enhancement Implementation

---

## Overview

This document provides a line-by-line breakdown of all code changes required to implement the requested features.

---

## 1. Simple Label and Field Changes

### 1.1 Projects Form Template - "Number of Bins" → "Number of Bends"

**File:** `app/templates/projects/form.html`  
**Lines:** 215-226

**Current Code:**
```html
<div class="form-group">
    <label for="number_of_bins" class="form-label">Number of Bins</label>
    <input
        type="number"
        id="number_of_bins"
        name="number_of_bins"
        class="form-control"
        value="{{ project.number_of_bins if project and project.number_of_bins else '' }}"
        min="0"
        placeholder="e.g., 2"
    >
    <small class="form-help">Number of bins for storage</small>
</div>
```

**New Code:**
```html
<div class="form-group">
    <label for="number_of_bins" class="form-label">Number of Bends</label>
    <input
        type="number"
        id="number_of_bins"
        name="number_of_bins"
        class="form-control"
        value="{{ project.number_of_bins if project and project.number_of_bins else '' }}"
        min="0"
        placeholder="e.g., 2"
    >
    <small class="form-help">Number of bends required</small>
</div>
```

**Changes:**
- Line 215: "Number of Bins" → "Number of Bends"
- Line 225: "Number of bins for storage" → "Number of bends required"

---

### 1.2 Projects Form Template - Add Material Thickness Field

**File:** `app/templates/projects/form.html`  
**Location:** After line 182 (after material_quantity_sheets field)

**New Code to Insert:**
```html
<div class="form-group">
    <label for="material_thickness" class="form-label">Material Thickness (mm)</label>
    <input
        type="number"
        id="material_thickness"
        name="material_thickness"
        class="form-control"
        value="{{ project.material_thickness if project and project.material_thickness else '' }}"
        step="0.1"
        min="0"
        placeholder="e.g., 3.0"
    >
    <small class="form-help">Thickness of material in millimeters</small>
</div>
```

---

### 1.3 Projects Detail Template - "Number of Bins" → "Number of Bends"

**File:** `app/templates/projects/detail.html`  
**Lines:** 256-257

**Current Code:**
```html
<dt>Number of Bins</dt>
<dd>{{ project.number_of_bins or '-' }}</dd>
```

**New Code:**
```html
<dt>Number of Bends</dt>
<dd>{{ project.number_of_bins or '-' }}</dd>
```

---

### 1.4 Projects Detail Template - Add Material Thickness Display

**File:** `app/templates/projects/detail.html`  
**Location:** After line 249 (after Material Quantity display)

**New Code to Insert:**
```html
<dt>Material Thickness</dt>
<dd>{{ project.material_thickness ~ ' mm' if project.material_thickness else '-' }}</dd>
```

---

### 1.5 Laser Run Form - "Sheet Count" → "Raw Material Count"

**File:** `app/templates/queue/run_form.html`  
**Line:** 71

**Current Code:**
```html
<label for="sheet_count">Sheet Count:</label>
```

**New Code:**
```html
<label for="sheet_count">Raw Material Count:</label>
```

---

## 2. File Upload Enhancement

### 2.1 Update Allowed File Extensions

**File:** `config.py`  
**Line:** 36

**Current Code:**
```python
ALLOWED_EXTENSIONS = {'dxf', 'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
```

**New Code:**
```python
ALLOWED_EXTENSIONS = {'dxf', 'lbrn2', 'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
```

---

### 2.2 Update File Upload Validation

**File:** `app/routes/files.py`  
**Lines:** 16-19

**Current Code:**
```python
def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed_extensions = {'.dxf', '.DXF'}
    return os.path.splitext(filename)[1] in allowed_extensions
```

**New Code:**
```python
def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed_extensions = {'.dxf', '.DXF', '.lbrn2', '.LBRN2'}
    return os.path.splitext(filename)[1] in allowed_extensions
```

---

### 2.3 Update File Upload Form

**File:** `app/templates/projects/detail.html`  
**Lines:** 515-520

**Current Code:**
```html
<h3 class="upload-form-title">Upload DXF File</h3>
<form action="{{ url_for('files.upload', project_id=project.id) }}" method="POST" enctype="multipart/form-data">
    <div class="form-group">
        <label for="file">Select File (DXF only):</label>
        <input type="file" id="file" name="file" accept=".dxf,.DXF" required class="form-control">
        <small class="text-muted">Maximum file size: 50 MB</small>
```

**New Code:**
```html
<h3 class="upload-form-title">Upload Design File</h3>
<form action="{{ url_for('files.upload', project_id=project.id) }}" method="POST" enctype="multipart/form-data">
    <div class="form-group">
        <label for="file">Select File (DXF or LightBurn):</label>
        <input type="file" id="file" name="file" accept=".dxf,.DXF,.lbrn2,.LBRN2" required class="form-control">
        <small class="text-muted">Accepted: DXF, LBRN2 | Maximum file size: 50 MB</small>
```

---

### 2.4 Update Section Header

**File:** `app/templates/projects/detail.html`  
**Line:** 507

**Current Code:**
```html
<h2>Design Files (DXF)</h2>
```

**New Code:**
```html
<h2>Design Files (DXF / LightBurn)</h2>
```

---

## 3. Backend Route Updates

### 3.1 Projects Route - Handle Material Thickness

**File:** `app/routes/projects.py`  
**Location:** After line 113 (in new_project function)

**Current Code:**
```python
number_of_bins = request.form.get('number_of_bins', type=int) or None
scheduled_cut_date_str = request.form.get('scheduled_cut_date', '').strip()
```

**New Code:**
```python
number_of_bins = request.form.get('number_of_bins', type=int) or None
material_thickness = request.form.get('material_thickness', type=float) or None
scheduled_cut_date_str = request.form.get('scheduled_cut_date', '').strip()
```

**Location:** Line 187 (in Project creation)

**Current Code:**
```python
number_of_bins=number_of_bins,
scheduled_cut_date=scheduled_cut_date
```

**New Code:**
```python
number_of_bins=number_of_bins,
material_thickness=material_thickness,
scheduled_cut_date=scheduled_cut_date
```

**Similar changes needed in `edit()` function around lines 280-320**

---

### 3.2 Queue Route - Pass Additional Data to Template

**File:** `app/routes/queue.py`  
**Lines:** 358-363 (in new_run function)

**Current Code:**
```python
# Get active queue items for this project
queue_items = QueueItem.query.filter_by(project_id=project_id).filter(
    QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
).all()

return render_template('queue/run_form.html', project=project, queue_items=queue_items)
```

**New Code:**
```python
# Get active queue items for this project
queue_items = QueueItem.query.filter_by(project_id=project_id).filter(
    QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
).all()

# Get material types from config
material_types = current_app.config.get('MATERIAL_TYPES', [])

# Get active operators
from app.models import Operator
operators = Operator.get_active_operators()

return render_template('queue/run_form.html', 
                      project=project, 
                      queue_items=queue_items,
                      material_types=material_types,
                      operators=operators)
```

---

## 4. Model Updates

### 4.1 Add Material Thickness to Project Model

**File:** `app/models.py`  
**Location:** After line 141 (after number_of_bins)

**Current Code:**
```python
number_of_bins = db.Column(db.Integer)
drawing_creation_time = db.Column(db.Integer)  # in minutes
```

**New Code:**
```python
number_of_bins = db.Column(db.Integer)
material_thickness = db.Column(db.Numeric(10, 3))  # in mm
drawing_creation_time = db.Column(db.Integer)  # in minutes
```

---

### 4.2 Add Preset ID to LaserRun Model

**File:** `app/models.py`  
**Location:** After line 753 (after queue_item_id)

**Current Code:**
```python
queue_item_id = db.Column(db.Integer, db.ForeignKey('queue_items.id', ondelete='SET NULL'), index=True)
run_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
```

**New Code:**
```python
queue_item_id = db.Column(db.Integer, db.ForeignKey('queue_items.id', ondelete='SET NULL'), index=True)
preset_id = db.Column(db.Integer, db.ForeignKey('machine_settings_presets.id', ondelete='SET NULL'), index=True)
run_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
```

---

## 5. Template Updates for Dropdowns

### 5.1 Convert Material Type to Dropdown

**File:** `app/templates/queue/run_form.html`  
**Lines:** 55-60

**Current Code:**
```html
<!-- Material Type -->
<div class="form-group">
    <label for="material_type">Material Type:</label>
    <input type="text" id="material_type" name="material_type" 
           class="form-control" placeholder="e.g., Mild Steel">
</div>
```

**New Code:**
```html
<!-- Material Type -->
<div class="form-group">
    <label for="material_type">Material Type:</label>
    <select id="material_type" name="material_type" class="form-control">
        <option value="">Select material...</option>
        {% for material in material_types %}
        <option value="{{ material }}">{{ material }}</option>
        {% endfor %}
    </select>
</div>
```

---

### 5.2 Convert Operator to Dropdown

**File:** `app/templates/queue/run_form.html`  
**Lines:** 41-46

**Current Code:**
```html
<!-- Operator -->
<div class="form-group">
    <label for="operator">Operator:</label>
    <input type="text" id="operator" name="operator" class="form-control" 
           placeholder="Operator name">
</div>
```

**New Code:**
```html
<!-- Operator -->
<div class="form-group">
    <label for="operator">Operator:</label>
    <select id="operator" name="operator" class="form-control">
        <option value="">Select operator...</option>
        {% for op in operators %}
        <option value="{{ op.name }}">{{ op.name }}</option>
        {% endfor %}
    </select>
</div>
```

---

## 6. Auto-populate Estimated Cut Time

### 6.1 Update Add to Queue Form

**File:** `app/templates/projects/detail.html`  
**Lines:** 57-61

**Current Code:**
```html
<div class="form-group">
    <label for="estimated_cut_time">Estimated Cut Time (minutes):</label>
    <input type="number" id="estimated_cut_time" name="estimated_cut_time"
           class="form-control" min="0" placeholder="e.g., 45">
</div>
```

**New Code:**
```html
<div class="form-group">
    <label for="estimated_cut_time">Estimated Cut Time (minutes):</label>
    <input type="number" id="estimated_cut_time" name="estimated_cut_time"
           class="form-control" min="0" placeholder="e.g., 45"
           value="{{ project.estimated_cut_time if project.estimated_cut_time else '' }}">
</div>
```

---

## 7. Database Migration

### 7.1 Create Migration File

**File:** `migrations/schema_v10_enhancements.sql` (NEW FILE)

See TECHNICAL_SPECIFICATION.md Section 1 for complete SQL.

---

### 7.2 Create Migration Script

**File:** `apply_phase10_migration.py` (NEW FILE)

See TECHNICAL_SPECIFICATION.md Section 5.2 for complete code.

---

## 8. New Model Classes

### 8.1 Add to Models File

**File:** `app/models.py`  
**Location:** After Setting model (around line 400)

Add complete MachineSettingsPreset and Operator models as specified in TECHNICAL_SPECIFICATION.md Section 2.

---

## 9. New Routes Blueprint

### 9.1 Create Settings Routes

**File:** `app/routes/settings.py` (NEW FILE - to be created in next phase)

Will contain all preset and operator management routes.

---

### 9.2 Register Settings Blueprint

**File:** `app/__init__.py`  
**Line:** 45

**Current Code:**
```python
from app.routes import main, clients, projects, products, files, queue, inventory, reports, quotes, invoices, comms
```

**New Code:**
```python
from app.routes import main, clients, projects, products, files, queue, inventory, reports, quotes, invoices, comms, settings
```

**Line:** 56

**Current Code:**
```python
app.register_blueprint(comms.bp)  # Phase 9: Communications module
```

**New Code:**
```python
app.register_blueprint(comms.bp)  # Phase 9: Communications module
app.register_blueprint(settings.bp)  # Phase 10: Settings and presets
```

---

## Summary of Changes

### Files to Modify (8)
1. ✅ `app/templates/projects/form.html` - 3 changes
2. ✅ `app/templates/projects/detail.html` - 4 changes
3. ✅ `app/templates/queue/run_form.html` - 3 changes
4. ✅ `app/routes/projects.py` - 2 changes
5. ✅ `app/routes/queue.py` - 1 change
6. ✅ `app/routes/files.py` - 1 change
7. ✅ `app/models.py` - 3 changes
8. ✅ `config.py` - 1 change
9. ✅ `app/__init__.py` - 2 changes

### Files to Create (6)
1. ⏳ `migrations/schema_v10_enhancements.sql`
2. ⏳ `apply_phase10_migration.py`
3. ⏳ `app/routes/settings.py`
4. ⏳ `app/templates/settings/presets_list.html`
5. ⏳ `app/templates/settings/preset_form.html`
6. ⏳ `app/templates/settings/operators_list.html`

### Total Lines Changed: ~150 lines
### Total New Lines: ~800 lines

---

**End of Code Changes Summary**

