# Implementation Plan: Web Application Enhancements
**Date:** 2025-10-16  
**Project:** Laser OS - Full DXF Laser Business Application

---

## Executive Summary

This document outlines a comprehensive implementation plan to address all requested changes across three main pages of the web application:
1. New Project Page (`/projects/new`)
2. Project Detail Page (`/projects/<id>`)
3. Log Laser Run Page (`/queue/runs/new/<id>`)

The changes include field label updates, new fields, file upload enhancements, and a complete machine settings preset management system.

---

## Current Application Analysis

### Technology Stack
- **Backend:** Flask (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** Jinja2 templates with custom CSS
- **File Structure:** Modular blueprint-based architecture

### Existing Database Schema
- **Projects Table:** Contains Phase 9 enhancements including `material_type`, `material_quantity_sheets`, `parts_quantity`, `estimated_cut_time`, `number_of_bins`, `drawing_creation_time`
- **LaserRuns Table:** Contains `operator`, `material_type`, `material_thickness`, `sheet_count`, `machine_settings` (TEXT field)
- **Settings Table:** Key-value configuration storage
- **DesignFiles Table:** Handles DXF file uploads

### Configuration System
- Material types defined in `config.py` as `MATERIAL_TYPES` list
- Settings stored in database `settings` table
- File upload restrictions in `app/routes/files.py`

---

## Detailed Change Requirements

### 1. New Project Page (`/projects/new`)

#### Changes Required:
1. **Rename field label:** "Number of Bins" → "Number of Bends"
2. **Add new field:** "Material Thickness" in "Material & Production Information" section

#### Files Affected:
- `app/templates/projects/form.html` (lines 215-226)
- `app/routes/projects.py` (line 113 for form processing)
- `app/models.py` (add new column to Project model)

---

### 2. Project Detail Page (`/projects/<id>`)

#### Changes Required:
1. **Expand file upload support:** Accept both DXF and LightBurn (.lbrn2) files
2. **Rename field label:** "Number of Bins" → "Number of Bends"
3. **Add new field:** "Material Thickness" display

#### Files Affected:
- `app/templates/projects/detail.html` (lines 256-257, 505-520)
- `app/routes/files.py` (line 18 - `allowed_file()` function)
- `config.py` (line 36 - `ALLOWED_EXTENSIONS`)

---

### 3. Log Laser Run Page (`/queue/runs/new/<id>`)

#### Changes Required:

##### A. Field Label Change
- **Rename:** "Sheet Count" → "Raw Material Count"
- **File:** `app/templates/queue/run_form.html` (line 71)

##### B. Convert to Dropdowns
1. **Material Type:** Text input → Dropdown (use `MATERIAL_TYPES` from config)
2. **Operator:** Text input → Dropdown (configurable list)

##### C. Machine Settings Preset System
**Current State:** Single text area for machine settings  
**Required State:** Dropdown-based preset system with admin interface

**Preset Fields:**
- Material
- Thickness
- Nozzle
- Cut Speed
- Nozzle Height
- Gas Type
- Gas Pressure
- Peak Power
- Actual Power
- Duty Cycle
- Pulse Frequency
- Beam Width
- Focus Position
- Laser On Delay
- Laser Off Delay
- Power Curve (On/Off)

##### D. Auto-populate Estimated Cut Time
- Source: `project.estimated_cut_time`
- Target: "Estimated Cut Time (minutes)" field in "Add to Production Queue" section

---

## Implementation Plan

### Phase 1: Database Schema Changes

#### 1.1 Create Machine Settings Presets Table
```sql
CREATE TABLE machine_settings_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preset_name VARCHAR(200) NOT NULL,
    material_type VARCHAR(100) NOT NULL,
    thickness DECIMAL(10, 3) NOT NULL,
    
    -- Machine Settings
    nozzle VARCHAR(50),
    cut_speed DECIMAL(10, 2),
    nozzle_height DECIMAL(10, 3),
    gas_type VARCHAR(50),
    gas_pressure DECIMAL(10, 2),
    peak_power DECIMAL(10, 2),
    actual_power DECIMAL(10, 2),
    duty_cycle DECIMAL(5, 2),
    pulse_frequency DECIMAL(10, 2),
    beam_width DECIMAL(10, 3),
    focus_position DECIMAL(10, 3),
    laser_on_delay DECIMAL(10, 3),
    laser_off_delay DECIMAL(10, 3),
    power_curve VARCHAR(20),
    
    -- Metadata
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(material_type, thickness)
);
```

#### 1.2 Create Operators Configuration Table
```sql
CREATE TABLE operators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### 1.3 Add Material Thickness to Projects Table
```sql
ALTER TABLE projects ADD COLUMN material_thickness DECIMAL(10, 3);
```

#### 1.4 Rename Column in Projects Table
```sql
-- SQLite doesn't support column rename directly
-- Will need to handle via model property or migration
```

#### 1.5 Update LaserRuns Table
```sql
ALTER TABLE laser_runs ADD COLUMN preset_id INTEGER;
ALTER TABLE laser_runs ADD FOREIGN KEY (preset_id) REFERENCES machine_settings_presets(id) ON DELETE SET NULL;
```

---

### Phase 2: Backend Model Updates

#### 2.1 Create New Models (`app/models.py`)
- `MachineSettingsPreset` model
- `Operator` model

#### 2.2 Update Project Model
- Add `material_thickness` column
- Add property for `number_of_bends` (alias for `number_of_bins`)

#### 2.3 Update LaserRun Model
- Add `preset_id` foreign key
- Add relationship to `MachineSettingsPreset`

---

### Phase 3: Configuration Updates

#### 3.1 Update `config.py`
- Add `.lbrn2` to `ALLOWED_EXTENSIONS`
- Add `OPERATOR_NAMES` configuration list (optional, can use database)

#### 3.2 Update File Upload Handler
- Modify `app/routes/files.py` to accept `.lbrn2` files
- Update file type validation

---

### Phase 4: Admin Interface for Presets

#### 4.1 Create Settings Blueprint (if not exists)
- New route: `/settings` or `/admin`

#### 4.2 Create Preset Management Routes
- `GET /settings/presets` - List all presets
- `GET /settings/presets/new` - Create new preset form
- `POST /settings/presets/new` - Save new preset
- `GET /settings/presets/<id>/edit` - Edit preset form
- `POST /settings/presets/<id>/edit` - Update preset
- `POST /settings/presets/<id>/delete` - Delete preset

#### 4.3 Create Operator Management Routes
- `GET /settings/operators` - List operators
- `POST /settings/operators/new` - Add operator
- `POST /settings/operators/<id>/delete` - Remove operator

#### 4.4 Create Templates
- `settings/presets_list.html`
- `settings/preset_form.html`
- `settings/operators_list.html`

---

### Phase 5: Frontend Template Updates

#### 5.1 Update Project Form Template
**File:** `app/templates/projects/form.html`
- Line 215-226: Change label "Number of Bins" → "Number of Bends"
- Add new field after material_type: "Material Thickness (mm)"

#### 5.2 Update Project Detail Template
**File:** `app/templates/projects/detail.html`
- Line 256-257: Change label "Number of Bins" → "Number of Bends"
- Add "Material Thickness" display field
- Line 518: Update file upload accept attribute to include `.lbrn2`
- Update upload form title and help text

#### 5.3 Update Laser Run Form Template
**File:** `app/templates/queue/run_form.html`
- Line 71: Change "Sheet Count" → "Raw Material Count"
- Lines 42-46: Convert Operator to dropdown
- Lines 56-60: Convert Material Type to dropdown
- Lines 84-89: Replace Machine Settings textarea with preset dropdown
- Add JavaScript for dynamic preset loading based on material + thickness

#### 5.4 Update Add to Queue Form
**File:** `app/templates/projects/detail.html` (lines 57-61)
- Auto-populate estimated_cut_time from project data

---

### Phase 6: Route Handler Updates

#### 6.1 Update Projects Routes
**File:** `app/routes/projects.py`
- Add `material_thickness` to form processing (new_project and edit functions)
- Update form data extraction

#### 6.2 Update Queue Routes
**File:** `app/routes/queue.py`
- Update `new_run()` to handle preset selection
- Pass operators list to template
- Pass material types to template
- Pass presets to template (filtered by material/thickness)

#### 6.3 Create Settings Routes
**File:** `app/routes/settings.py` (new file)
- Implement all preset and operator management routes

---

### Phase 7: JavaScript Enhancements

#### 7.1 Preset Selection Logic
Create JavaScript for dynamic preset loading:
- Listen to material_type and material_thickness changes
- Fetch matching presets via AJAX
- Populate preset dropdown
- On preset selection, display all settings (read-only or editable)

#### 7.2 Auto-populate Cut Time
Add JavaScript to auto-fill estimated cut time in queue form

---

### Phase 8: API Endpoints (Optional)

#### 8.1 Preset API
- `GET /api/presets?material=<type>&thickness=<value>` - Get matching presets
- Returns JSON with preset details

---

### Phase 9: Data Migration

#### 9.1 Migration Script
Create `migrations/schema_v10_enhancements.sql`:
- Create new tables
- Add new columns
- Seed initial operators
- Import existing machine settings if available

#### 9.2 Seed Data
- Add sample presets from "Laser cutting parameters.html"
- Add common operators

---

### Phase 10: Testing

#### 10.1 Unit Tests
- Test new models
- Test preset CRUD operations
- Test operator management

#### 10.2 Integration Tests
- Test project creation with new fields
- Test file upload with .lbrn2
- Test laser run logging with presets

#### 10.3 UI Tests
- Test all form submissions
- Test dropdown population
- Test auto-fill functionality

---

## Implementation Sequence

### Priority 1: Simple Changes (1-2 hours)
1. ✅ Rename "Number of Bins" → "Number of Bends" (templates only)
2. ✅ Add "Material Thickness" field to Project form and detail
3. ✅ Rename "Sheet Count" → "Raw Material Count"
4. ✅ Add .lbrn2 file support

### Priority 2: Dropdown Conversions (2-3 hours)
5. ✅ Convert Material Type to dropdown (use existing config)
6. ✅ Create Operator table and management
7. ✅ Convert Operator to dropdown

### Priority 3: Preset System (8-12 hours)
8. ✅ Create database schema for presets
9. ✅ Create Preset model
10. ✅ Create admin interface for preset management
11. ✅ Update Laser Run form with preset dropdown
12. ✅ Add JavaScript for dynamic preset loading
13. ✅ Update LaserRun model to store preset reference

### Priority 4: Auto-population (1 hour)
14. ✅ Auto-populate estimated cut time in queue form

---

## File Change Summary

### New Files (6)
1. `migrations/schema_v10_enhancements.sql` - Database migration
2. `app/routes/settings.py` - Settings/admin routes
3. `app/templates/settings/presets_list.html` - Preset list view
4. `app/templates/settings/preset_form.html` - Preset create/edit form
5. `app/templates/settings/operators_list.html` - Operator management
6. `app/static/js/preset_loader.js` - Dynamic preset loading (optional)

### Modified Files (10)
1. `app/models.py` - Add MachineSettingsPreset, Operator models; update Project, LaserRun
2. `app/templates/projects/form.html` - Label changes, add material_thickness field
3. `app/templates/projects/detail.html` - Label changes, add material_thickness display, update file upload
4. `app/templates/queue/run_form.html` - Label change, convert to dropdowns, add preset selection
5. `app/routes/projects.py` - Handle material_thickness in form processing
6. `app/routes/queue.py` - Pass operators, presets to template; handle preset selection
7. `app/routes/files.py` - Update allowed_file() for .lbrn2
8. `config.py` - Add .lbrn2 to ALLOWED_EXTENSIONS
9. `app/__init__.py` - Register settings blueprint
10. `app/templates/base.html` - Add Settings link to navigation (optional)

---

## Risk Assessment

### Low Risk
- Label changes (cosmetic only)
- Adding material_thickness field (non-breaking)
- File upload extension (backward compatible)

### Medium Risk
- Dropdown conversions (UI change, but data compatible)
- Auto-population (JavaScript, graceful degradation)

### High Risk
- Machine settings preset system (major feature, requires careful testing)
- Database migration (requires backup and rollback plan)

---

## Rollback Plan

1. **Database Backup:** Create backup before migration
2. **Migration Rollback:** Keep reverse migration script
3. **Code Rollback:** Use git tags for each phase
4. **Feature Flags:** Consider feature flags for preset system

---

## Success Criteria

### Functional Requirements
- ✅ All field labels updated correctly
- ✅ Material thickness field functional on projects
- ✅ .lbrn2 files upload successfully
- ✅ Dropdowns populate with correct data
- ✅ Preset system allows CRUD operations
- ✅ Preset selection populates all machine settings
- ✅ Auto-population works for estimated cut time

### Non-Functional Requirements
- ✅ No data loss during migration
- ✅ Backward compatibility with existing data
- ✅ Performance: Page load < 2 seconds
- ✅ Mobile responsive (existing design maintained)

---

## Next Steps

1. **Review and Approval:** Stakeholder review of this plan
2. **Environment Setup:** Create development branch
3. **Database Backup:** Backup production database
4. **Implementation:** Follow priority sequence
5. **Testing:** Comprehensive testing at each phase
6. **Deployment:** Staged rollout (dev → staging → production)

---

**End of Implementation Plan**

