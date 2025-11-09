# 🐛 Bug Fix: ProjectDocument `uploaded_at` Attribute Error

**Date:** October 16, 2025  
**Issue:** Jinja2 template error when viewing migrated projects  
**Status:** ✅ FIXED

---

## Problem Description

After successfully migrating client CL-0002 (Dura Edge) projects to the database, attempting to view a project with documents attached resulted in a Jinja2 template error:

```
UndefinedError
jinja2.exceptions.UndefinedError: 'app.models.ProjectDocument object' has no attribute 'uploaded_at'
```

---

## Root Cause Analysis

### Issue
The `ProjectDocument` model uses `upload_date` as the column name for the upload timestamp, but several parts of the codebase were incorrectly trying to access `uploaded_at`.

### Affected Locations

1. **Template:** `app/templates/projects/detail.html`
   - Line 471: Sorting documents by `uploaded_at` (incorrect)
   - Line 480: Displaying `uploaded_at` (incorrect)

2. **Service:** `app/services/document_service.py`
   - Line 331: Ordering query by `uploaded_at` (incorrect)

### Correct Attribute Name

According to the `ProjectDocument` model definition in `app/models.py`:

```python
class ProjectDocument(db.Model):
    # ...
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    uploaded_by = db.Column(db.String(100))
```

The correct attribute is **`upload_date`**, not `uploaded_at`.

---

## Solution

### Files Modified

#### 1. `app/templates/projects/detail.html`

**Before (Line 471):**
```jinja2
{% for doc in project.documents|sort(attribute='uploaded_at', reverse=True) %}
```

**After:**
```jinja2
{% for doc in project.documents|sort(attribute='upload_date', reverse=True) %}
```

**Before (Line 480):**
```jinja2
<td>{{ doc.uploaded_at|datetime }}</td>
```

**After:**
```jinja2
<td>{{ doc.upload_date|datetime }}</td>
```

#### 2. `app/services/document_service.py`

**Before (Line 331):**
```python
return query.order_by(ProjectDocument.uploaded_at.desc()).all()
```

**After:**
```python
return query.order_by(ProjectDocument.upload_date.desc()).all()
```

---

## Verification

### 1. Code Search
Performed a comprehensive search for any remaining instances of `uploaded_at`:

```powershell
Get-ChildItem -Path "app" -Recurse -Include "*.py","*.html" | Select-String -Pattern "uploaded_at" -CaseSensitive
```

**Result:** ✅ No instances found (all fixed)

### 2. Model Consistency Check

Verified that the `ProjectDocument` model consistently uses `upload_date`:

- ✅ Column definition: `upload_date`
- ✅ `to_dict()` method: Uses `upload_date`
- ✅ Documentation: References `upload_date`

### 3. Similar Models Check

Checked other models for consistency:

**DesignFile Model:**
- Uses `upload_date` ✅ (consistent)

**Communication Model:**
- Uses `sent_at` ✅ (different purpose, correct)

---

## Impact Assessment

### Before Fix
- ❌ Viewing projects with documents caused template errors
- ❌ Document service queries would fail
- ❌ Migration appeared successful but data was inaccessible

### After Fix
- ✅ Projects with documents display correctly
- ✅ Document sorting works properly
- ✅ Document service queries execute successfully
- ✅ All migrated data is now accessible

---

## Testing Recommendations

### Manual Testing
1. ✅ Navigate to a project with documents (e.g., JB-2025-10-CL0002-004)
2. ✅ Verify the documents table displays correctly
3. ✅ Verify documents are sorted by upload date (newest first)
4. ✅ Verify upload date displays in the correct format

### Automated Testing
Consider adding tests to prevent similar issues:

```python
def test_project_document_attributes():
    """Test that ProjectDocument has correct attribute names."""
    doc = ProjectDocument(
        project_id=1,
        document_type='Quote',
        original_filename='test.pdf',
        stored_filename='test_stored.pdf',
        file_path='/path/to/file',
        file_size=1024
    )
    
    # Should have upload_date, not uploaded_at
    assert hasattr(doc, 'upload_date')
    assert not hasattr(doc, 'uploaded_at')
```

---

## Lessons Learned

### 1. Naming Consistency
The codebase has inconsistent naming conventions:
- `DesignFile` uses `upload_date`
- `ProjectDocument` uses `upload_date`
- Some code incorrectly assumed `uploaded_at`

**Recommendation:** Establish and document naming conventions for timestamp fields.

### 2. Template Testing
Templates should be tested with real data to catch attribute errors.

**Recommendation:** Add integration tests that render templates with actual model instances.

### 3. Migration Validation
The migration completed successfully, but the bug wasn't discovered until viewing the data.

**Recommendation:** Add post-migration validation that tests viewing migrated data.

---

## Related Issues

### Historical Context
From `PHASE_9_IMPLEMENTATION_SUMMARY.md`:

> **Issue:** Test expected `file_name` and `uploaded_at`, actual columns are `original_filename` and `upload_date`
> **Fix:** Updated test to match actual schema

This indicates the `uploaded_at` vs `upload_date` confusion existed before and was partially addressed in tests but not in all templates/services.

---

## Prevention Strategies

### 1. Code Review Checklist
- [ ] Verify attribute names match model definitions
- [ ] Check for similar patterns in other files
- [ ] Test templates with real data

### 2. Linting/Static Analysis
Consider adding tools to detect:
- Undefined template variables
- Incorrect model attribute access

### 3. Documentation
- Document all model attributes in a central location
- Include examples of correct usage
- Maintain a glossary of naming conventions

---

## Summary

**Root Cause:** Attribute name mismatch (`uploaded_at` vs `upload_date`)

**Files Fixed:**
- `app/templates/projects/detail.html` (2 changes)
- `app/services/document_service.py` (1 change)

**Verification:** ✅ All instances corrected, no remaining issues found

**Impact:** Migration data is now fully accessible and displayable

**Status:** ✅ **RESOLVED**

---

**Fix completed on October 16, 2025**

