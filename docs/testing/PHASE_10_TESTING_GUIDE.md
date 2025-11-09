# Phase 10: Testing Guide

**Version:** Phase 10 - Automation & Workflow Enhancements  
**Date:** 2025-10-21  
**Status:** Ready for Testing

---

## 🧪 Quick Start Testing

### Prerequisites
- ✅ Migration completed (`python run_phase10_migration.py`)
- ✅ Application running (`python run.py`)
- ✅ Test data available (clients, projects, inventory)

---

## 📋 Test Scenarios

### **Test 1: Gas Type Auto-Selection**

**Objective:** Verify gas type is automatically selected based on material and thickness

**Steps:**
1. Navigate to **Machine Settings Presets** → **New Preset**
2. Select **Material Type:** `Mild Steel`
3. Enter **Thickness:** `10` (mm)
4. **Expected:** Gas Type should auto-select to `Oxygen`
5. Change **Thickness:** to `3` (mm)
6. **Expected:** Gas Type should auto-select to `Air`
7. Change **Material Type:** to `Aluminum`
8. **Expected:** Gas Type should auto-select to `Nitrogen`
9. Change **Material Type:** to `Zinc`
10. **Expected:** Gas Type should remain `Nitrogen`

**Pass Criteria:**
- ✅ Gas type auto-selects correctly for all combinations
- ✅ User can manually override the selection
- ✅ Preset saves with selected gas type

---

### **Test 2: New Material Types**

**Objective:** Verify Carbon Steel and Zinc are available in all dropdowns

**Steps:**
1. Navigate to **Projects** → **New Project**
2. Check **Material Type** dropdown
3. **Expected:** `Carbon Steel` and `Zinc` are in the list
4. Navigate to **Inventory** → **New Item**
5. Check **Material Type** dropdown
6. **Expected:** `Carbon Steel` and `Zinc` are in the list
7. Navigate to **Machine Settings Presets** → **New Preset**
8. Check **Material Type** dropdown
9. **Expected:** `Carbon Steel` and `Zinc` are in the list

**Pass Criteria:**
- ✅ Both new materials appear in all dropdowns
- ✅ Materials can be selected and saved

---

### **Test 3: Thickness Validation**

**Objective:** Verify thickness dropdown includes special values and increments

**Steps:**
1. Navigate to **Projects** → **New Project**
2. Click **Material Thickness** dropdown
3. **Expected:** See options:
   - `0.47mm (Thin Carbon Steel)`
   - `0.53mm (Thin Carbon Steel)`
   - `1.0mm`, `1.5mm`, `2.0mm`, ... up to `16.0mm`
   - `Custom thickness...`
4. Select `Custom thickness...`
5. **Expected:** Input field appears for manual entry
6. Enter `18.5` and save
7. **Expected:** Custom thickness is saved

**Pass Criteria:**
- ✅ All thickness options are available
- ✅ Custom thickness option works
- ✅ Thickness saves correctly

---

### **Test 4: Operator Management**

**Objective:** Verify operator CRUD operations and user linking

**Steps:**
1. Navigate to **Operators** (new menu item)
2. **Expected:** Operators list page loads
3. Click **+ New Operator**
4. Fill in:
   - Name: `Test Operator`
   - Email: `test@example.com`
   - Phone: `0123456789`
   - Link to User: Select a user from dropdown (optional)
5. Click **Create Operator**
6. **Expected:** Operator created, redirected to detail page
7. Click **Edit**
8. Change name to `Test Operator Updated`
9. Click **Update**
10. **Expected:** Operator updated successfully
11. Click **Toggle Active Status**
12. **Expected:** Operator marked as inactive
13. Go back to operators list
14. **Expected:** Inactive operator shown with badge

**Pass Criteria:**
- ✅ All CRUD operations work
- ✅ User linking works (optional)
- ✅ Active/Inactive toggle works
- ✅ Operator detail page shows recent runs

---

### **Test 5: Auto-Scheduling (Success Case)**

**Objective:** Verify project auto-schedules when POP received with sufficient inventory

**Prerequisites:**
- Create inventory item: `Mild Steel 3.0mm` with quantity `10 sheets`
- Create project with:
  - Material Type: `Mild Steel`
  - Material Thickness: `3.0mm`
  - Material Quantity (Sheets): `5`
  - Parts Quantity: `50`
  - Estimated Cut Time: `45` minutes
  - POP: **NOT** received yet

**Steps:**
1. Navigate to project detail page
2. Click **Toggle POP Received**
3. **Expected:** Flash message appears:
   - `✅ Project auto-scheduled for cutting - Inventory reserved`
4. Navigate to **Queue**
5. **Expected:** Project appears in queue with:
   - Priority: `Normal`
   - Scheduled Date: Today or next business day
   - Status: `Pending`
   - Badge: `✅ POP Received - Auto-scheduled`
6. Navigate to **Inventory**
7. **Expected:** Mild Steel 3.0mm quantity reduced by 5 sheets (10 → 5)
8. Check **Inventory Transactions**
9. **Expected:** Transaction logged:
   - Type: `Deduction`
   - Quantity: `-5.0`
   - Reference: `Queue Item #X`

**Pass Criteria:**
- ✅ Project auto-schedules when POP received
- ✅ Inventory is reserved/deducted
- ✅ Queue item created with correct details
- ✅ Activity logged
- ✅ Flash message shows success

---

### **Test 6: Auto-Scheduling (Insufficient Inventory)**

**Objective:** Verify warning shown when inventory insufficient

**Prerequisites:**
- Create inventory item: `Stainless Steel 5.0mm` with quantity `2 sheets`
- Create project with:
  - Material Type: `Stainless Steel`
  - Material Thickness: `5.0mm`
  - Material Quantity (Sheets): `10`
  - POP: **NOT** received yet

**Steps:**
1. Navigate to project detail page
2. Click **Toggle POP Received**
3. **Expected:** Flash messages appear:
   - `⚠️ Not auto-scheduled: Insufficient inventory (need 10.0 sheets, have 2.0)`
   - `💡 Suggestion: Order 8 sheets of Stainless Steel 5.0mm`
4. Navigate to **Queue**
5. **Expected:** Project **NOT** in queue
6. Navigate to **Inventory**
7. **Expected:** Stainless Steel 5.0mm quantity unchanged (still 2 sheets)

**Pass Criteria:**
- ✅ Project does NOT auto-schedule
- ✅ Warning message shows shortage
- ✅ Ordering suggestion provided
- ✅ Inventory not deducted
- ✅ Project can be manually added to queue later

---

### **Test 7: Auto-Scheduling (Missing Production Details)**

**Objective:** Verify warning shown when material details missing

**Prerequisites:**
- Create project with:
  - Material Type: **NOT SET**
  - Material Thickness: **NOT SET**
  - POP: **NOT** received yet

**Steps:**
1. Navigate to project detail page
2. Click **Toggle POP Received**
3. **Expected:** Flash message appears:
   - `⚠️ Not auto-scheduled: Missing material information`
4. Navigate to **Queue**
5. **Expected:** Project **NOT** in queue
6. Go back to project, click **Edit**
7. Fill in:
   - Material Type: `Aluminum`
   - Material Thickness: `2.0mm`
   - Material Quantity: `3`
8. Save project
9. **Expected:** POP still received (checkbox remains checked)
10. Refresh page
11. **Expected:** If inventory available, project should now be in queue

**Pass Criteria:**
- ✅ Project does NOT auto-schedule without material details
- ✅ Warning message clear
- ✅ After adding details, can manually trigger or auto-schedules

---

### **Test 8: Laser Run Form Pre-filling**

**Objective:** Verify laser run form pre-fills from project data

**Prerequisites:**
- Create project with complete data:
  - Material Type: `Mild Steel`
  - Material Thickness: `3.0mm`
  - Material Quantity: `5 sheets`
  - Parts Quantity: `50`
  - Estimated Cut Time: `45 minutes`
- Create matching preset: `Mild Steel 3.0mm`

**Steps:**
1. Navigate to project detail page
2. Click **Log Laser Run**
3. **Expected:** Form pre-filled with:
   - Cut Time: `45` (with note "Pre-filled from project estimate")
   - Material Type: `Mild Steel` (with note "Pre-filled from project")
   - Material Thickness: `3.0` (with note "Pre-filled from project")
   - Raw Material Count: `5` (with note "Pre-filled from project (5 sheets)")
   - Parts Produced: `50` (with note "Pre-filled from project estimate (50 parts)")
   - Machine Settings Preset: `Mild Steel 3.0mm` **auto-selected**
4. Change **Cut Time** to `50`
5. Change **Parts Produced** to `48`
6. Fill in **Operator** and **Run Date**
7. Click **Log Run**
8. **Expected:** Laser run saved with **actual** values (50 min, 48 parts)

**Pass Criteria:**
- ✅ All fields pre-fill correctly
- ✅ Matching preset auto-selects
- ✅ Fields are editable
- ✅ Actual values save (not estimates)
- ✅ Visual indicators show pre-filled fields

---

### **Test 9: POP Status Messages**

**Objective:** Verify new POP status messages appear correctly

**Steps:**
1. Create project **without** POP received
2. Navigate to project detail page
3. **Expected:** See `❌ Awaiting POP` badge
4. Mark POP as received (with sufficient inventory)
5. **Expected:** See:
   - `✅ POP Received` badge
   - `Auto-scheduled for cutting` message
6. Navigate to **Queue**
7. **Expected:** Project shows `✅ POP Received - Auto-scheduled` badge
8. Create another project with POP but missing material details
9. **Expected:** See:
   - `✅ POP Received` badge
   - `⚠️ Missing production details` message

**Pass Criteria:**
- ✅ No countdown messages ("X days remaining")
- ✅ New status messages clear and accurate
- ✅ Info box explains auto-scheduling
- ✅ Queue page shows correct badges

---

### **Test 10: Preset Filtering**

**Objective:** Verify preset dropdown filters by material/thickness

**Prerequisites:**
- Create presets:
  - `Mild Steel 3.0mm`
  - `Mild Steel 5.0mm`
  - `Aluminum 2.0mm`

**Steps:**
1. Navigate to **Log Laser Run** for any project
2. Select **Material Type:** `Mild Steel`
3. Enter **Material Thickness:** `3.0`
4. Click **Machine Settings Preset** dropdown
5. **Expected:** Only `Mild Steel 3.0mm` visible (others hidden)
6. **Expected:** Placeholder shows `Select preset (1 available)...`
7. Change **Material Type:** to `Aluminum`
8. **Expected:** Only `Aluminum 2.0mm` visible
9. Clear material type and thickness
10. **Expected:** All presets visible

**Pass Criteria:**
- ✅ Presets filter correctly
- ✅ Count updates in placeholder
- ✅ Matching preset auto-selects on page load
- ✅ User can still manually select any preset

---

## 🔍 Edge Cases to Test

### Edge Case 1: Toggle POP Off Then On
1. Mark POP as received → Auto-schedules
2. Uncheck POP → Queue item should remain (manual removal required)
3. Check POP again → Should show "Already in queue" message

### Edge Case 2: Delete Queue Item After Auto-Schedule
1. Auto-schedule project (inventory reserved)
2. Delete queue item
3. **Expected:** Inventory should be released back

### Edge Case 3: Multiple Projects Same Material
1. Create 3 projects requiring same material
2. Inventory has enough for 2 projects only
3. Mark all 3 POP as received
4. **Expected:** First 2 auto-schedule, 3rd shows insufficient inventory

### Edge Case 4: Custom Thickness Preset Matching
1. Create preset with custom thickness `4.7mm`
2. Create project with thickness `4.7mm`
3. Open laser run form
4. **Expected:** Preset auto-selects (tolerance ±0.1mm)

---

## ✅ Final Verification Checklist

After completing all tests:

- [ ] All gas type rules work correctly
- [ ] New materials (Carbon Steel, Zinc) available everywhere
- [ ] Thickness validation works (special values + increments)
- [ ] Operator CRUD operations functional
- [ ] Auto-scheduling works with sufficient inventory
- [ ] Auto-scheduling shows warnings when conditions not met
- [ ] Inventory reservation/release works correctly
- [ ] Laser run form pre-fills accurately
- [ ] Preset auto-selection works
- [ ] POP status messages updated (no countdowns)
- [ ] All edge cases handled gracefully
- [ ] No errors in browser console
- [ ] No errors in application logs
- [ ] Activity log records all actions

---

## 🐛 Known Issues / Limitations

None identified during implementation.

---

## 📞 Support

If you encounter any issues during testing:
1. Check browser console for JavaScript errors
2. Check application logs for Python errors
3. Verify migration ran successfully
4. Ensure test data is set up correctly

---

**Happy Testing!** 🚀

