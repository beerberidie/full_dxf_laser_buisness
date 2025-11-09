# Presets Management System - Testing Guide

## Quick Start

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

---

## Test Scenarios

### ✅ Test 1: View Presets Page

**Steps:**
1. Click the **"Presets"** tab in the top navigation bar
2. You should see the Presets management page

**Expected Results:**
- ✅ Page loads successfully
- ✅ Table shows 7 sample presets
- ✅ Each preset shows: name, material, thickness, key settings, status, usage count
- ✅ "Add New Preset" button is visible
- ✅ Filter form is visible at the top

**Sample Presets You Should See:**
- Mild Steel 1mm - Standard
- Mild Steel 2mm - Standard
- Mild Steel 3mm - Standard
- Stainless Steel 1mm - Standard
- Stainless Steel 2mm - Standard
- Aluminum 1mm - Standard
- Aluminum 2mm - Standard

---

### ✅ Test 2: Filter Presets

**Steps:**
1. On the Presets page, use the filter form:
   - **Search:** Enter "Mild Steel"
   - Click "Apply Filters"

**Expected Results:**
- ✅ Only Mild Steel presets are shown (3 presets)
- ✅ Other presets are hidden

**Steps:**
2. Clear search and filter by material:
   - Clear the search box
   - Select "Stainless Steel" from Material Type dropdown
   - Click "Apply Filters"

**Expected Results:**
- ✅ Only Stainless Steel presets are shown (2 presets)

**Steps:**
3. Filter by status:
   - Select "Active" from Status dropdown
   - Click "Apply Filters"

**Expected Results:**
- ✅ Only active presets are shown (all 7 should be active)

---

### ✅ Test 3: Add New Preset

**Steps:**
1. Click **"Add New Preset"** button
2. Fill in the form:
   - **Preset Name:** "Mild Steel 5mm - Standard"
   - **Material Type:** Select "Mild Steel"
   - **Thickness:** 5.0
   - **Nozzle:** "2.0mm Single"
   - **Cut Speed:** 1500
   - **Nozzle Height:** 1.2
   - **Gas Type:** "Oxygen"
   - **Gas Pressure:** 1.0
   - **Peak Power:** 3000
   - **Actual Power:** 2800
   - **Duty Cycle:** 95
   - **Pulse Frequency:** 4000
   - **Notes:** "Standard settings for 5mm mild steel"
3. Click **"Save Preset"**

**Expected Results:**
- ✅ Redirected to Presets list page
- ✅ Success message: "Preset created successfully"
- ✅ New preset appears in the table
- ✅ Preset shows as "Active"
- ✅ Usage count is 0

---

### ✅ Test 4: Edit Preset

**Steps:**
1. Find the preset you just created ("Mild Steel 5mm - Standard")
2. Click the **"Edit"** button
3. Modify some fields:
   - **Cut Speed:** Change to 1600
   - **Notes:** Add "Updated cut speed for better quality"
4. Click **"Save Preset"**

**Expected Results:**
- ✅ Redirected to Presets list page
- ✅ Success message: "Preset updated successfully"
- ✅ Changes are reflected in the table

---

### ✅ Test 5: Deactivate Preset

**Steps:**
1. Find the preset you created
2. Click the **"Deactivate"** button

**Expected Results:**
- ✅ Page refreshes
- ✅ Success message: "Preset deactivated successfully"
- ✅ Status changes to "Inactive" (red badge)
- ✅ Button changes to "Activate"

**Steps:**
2. Click the **"Activate"** button

**Expected Results:**
- ✅ Page refreshes
- ✅ Success message: "Preset activated successfully"
- ✅ Status changes to "Active" (green badge)
- ✅ Button changes to "Deactivate"

---

### ✅ Test 6: Delete Preset (Unused)

**Steps:**
1. Find the preset you created (should have 0 usage count)
2. Click the **"Delete"** button
3. Confirm the deletion in the popup

**Expected Results:**
- ✅ Page refreshes
- ✅ Success message: "Preset deleted successfully"
- ✅ Preset is removed from the table

---

### ✅ Test 7: Try to Delete Preset (In Use)

**First, create a laser run using a preset:**

**Steps:**
1. Navigate to a project (or create a new one)
2. Click **"Log Laser Run"** button
3. Fill in the form:
   - **Operator:** Select "Operator 1"
   - **Material Type:** Select "Mild Steel"
   - **Material Thickness:** 1.0
   - **Preset:** Select "Mild Steel 1mm - Standard" (should auto-filter)
   - **Cut Time:** 30
   - **Parts Produced:** 50
4. Click **"Log Run"**

**Now try to delete the preset:**

**Steps:**
1. Navigate back to Presets page
2. Find "Mild Steel 1mm - Standard" preset
3. Note that Usage Count is now 1 (or more)
4. Click the **"Delete"** button
5. Confirm the deletion

**Expected Results:**
- ✅ Error message: "Cannot delete preset: it is currently used by 1 laser run(s)"
- ✅ Preset is NOT deleted
- ✅ Preset remains in the table

---

### ✅ Test 8: Simplified Laser Run Form

**Steps:**
1. Navigate to a project
2. Click **"Log Laser Run"** button

**Expected Results:**
- ✅ Form loads successfully
- ✅ **Operator dropdown** is visible
- ✅ **Material Type dropdown** is visible
- ✅ **Material Thickness input** is visible
- ✅ **Machine Settings Preset dropdown** is visible
- ✅ **Additional Settings/Notes textarea** is visible
- ✅ **NO individual machine settings fields** (nozzle, cut speed, etc.)
- ✅ Help text says: "Preset defines all machine settings. Manage presets in the Presets page."

---

### ✅ Test 9: Preset Filtering in Laser Run Form

**Steps:**
1. On the Log Laser Run form:
   - **Material Type:** Select "Stainless Steel"
   - **Material Thickness:** Leave blank
2. Click on the **Preset dropdown**

**Expected Results:**
- ✅ Only Stainless Steel presets are shown
- ✅ Mild Steel and Aluminum presets are hidden
- ✅ Placeholder shows: "Select preset (2 available)..."

**Steps:**
2. Enter thickness:
   - **Material Thickness:** 1.0
3. Click on the **Preset dropdown** again

**Expected Results:**
- ✅ Only "Stainless Steel 1mm - Standard" is shown
- ✅ "Stainless Steel 2mm - Standard" is hidden (thickness doesn't match)
- ✅ Placeholder shows: "Select preset (1 available)..."

**Steps:**
3. Change thickness:
   - **Material Thickness:** 5.0
4. Click on the **Preset dropdown** again

**Expected Results:**
- ✅ No presets are shown
- ✅ Placeholder shows: "No matching presets found"

---

### ✅ Test 10: Submit Laser Run with Preset

**Steps:**
1. On the Log Laser Run form:
   - **Operator:** Select "Operator 1"
   - **Material Type:** Select "Mild Steel"
   - **Material Thickness:** 2.0
   - **Preset:** Select "Mild Steel 2mm - Standard"
   - **Additional Settings/Notes:** "Test run with preset"
   - **Cut Time:** 45
   - **Parts Produced:** 75
2. Click **"Log Run"**

**Expected Results:**
- ✅ Redirected to project detail page
- ✅ Success message: "Laser run logged successfully"
- ✅ New laser run appears in the table
- ✅ Operator shows: "Operator 1"
- ✅ Preset shows: "Mild Steel 2mm - Standard"
- ✅ Material shows: "Mild Steel 2.0mm"

---

### ✅ Test 11: Verify Data in Database

**Steps:**
1. Navigate to the laser run detail page (click on the run you just created)

**Expected Results:**
- ✅ Operator displays correctly
- ✅ Preset displays correctly
- ✅ Machine Settings shows only: "Test run with preset" (not individual settings)
- ✅ All other fields display correctly

---

### ✅ Test 12: Preset Auto-Fill Material/Thickness

**Steps:**
1. On the Log Laser Run form:
   - **Leave Material Type and Thickness blank**
   - **Preset:** Select "Aluminum 1mm - Standard"

**Expected Results:**
- ✅ Material Type auto-fills to "Aluminum"
- ✅ Material Thickness auto-fills to "1.0"

---

## Common Issues and Solutions

### Issue: Presets page shows "No presets found"

**Solution:**
- Run the migration script to seed sample presets:
  ```bash
  python apply_phase10_part4_migration.py
  ```

### Issue: Preset dropdown is empty in laser run form

**Solution:**
- Check that presets are active (not deactivated)
- Check that material type and thickness match existing presets
- Navigate to Presets page and verify presets exist

### Issue: Cannot delete preset

**Solution:**
- This is expected if the preset is used by laser runs
- Deactivate the preset instead of deleting it
- Or delete the laser runs using the preset first (not recommended)

### Issue: Form validation errors

**Solution:**
- Ensure all required fields are filled (marked with *)
- Check that numeric fields have valid numbers
- Check that preset name is unique

---

## Success Criteria

All tests should pass with the expected results. The system should:

- ✅ Display presets correctly
- ✅ Filter presets by search, material, and status
- ✅ Allow adding new presets
- ✅ Allow editing existing presets
- ✅ Allow activating/deactivating presets
- ✅ Prevent deletion of presets in use
- ✅ Allow deletion of unused presets
- ✅ Show simplified laser run form (no individual fields)
- ✅ Filter presets by material/thickness in laser run form
- ✅ Auto-fill material/thickness from preset selection
- ✅ Save laser runs with preset_id relationship
- ✅ Display preset name in laser run details
- ✅ Log all preset changes to activity log

---

## Next Steps After Testing

If all tests pass:

1. **Start using the system:**
   - Create presets for your common material/thickness combinations
   - Train operators to use preset dropdown when logging runs
   - Manage presets in the dedicated Presets page

2. **Monitor usage:**
   - Check preset usage counts
   - Identify which presets are most used
   - Deactivate unused presets

3. **Maintain presets:**
   - Update presets as machine settings change
   - Add new presets for new materials
   - Keep preset names descriptive and consistent

---

**Happy Testing!** 🎉

