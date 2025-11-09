# Inventory Dropdown Conversion - Testing Guide

## 🧪 Manual Testing Checklist

Use this guide to manually test the inventory dropdown functionality.

---

## ✅ Test 1: View New Inventory Form

**Steps:**
1. Open browser to: `http://127.0.0.1:5000/inventory/new`
2. Locate the **Material Type** field
3. Locate the **Thickness** field

**Expected Results:**
- ✅ Material Type is a **dropdown** (not a text input)
- ✅ Thickness is a **dropdown** (not a number input)
- ✅ Both dropdowns have a blank "Select..." option
- ✅ Material Type shows 7 options (Mild Steel, Stainless Steel, etc.)
- ✅ Thickness shows 12 options (0.5mm, 0.8mm, 1.0mm, etc.)

---

## ✅ Test 2: Create Inventory Item with Dropdown Values

**Steps:**
1. Fill in the form:
   - **Item Code:** TEST-001
   - **Name:** Test Sheet Metal
   - **Category:** Sheet Metal
   - **Unit:** sheets
   - **Material Type:** Select "Mild Steel" from dropdown
   - **Thickness:** Select "3.0" from dropdown
   - **Initial Quantity:** 10
   - **Reorder Level:** 5
   - **Unit Cost:** 150.00
2. Click **Save Item**

**Expected Results:**
- ✅ Item created successfully
- ✅ Redirected to item detail page
- ✅ Material Type shows: "Mild Steel"
- ✅ Thickness shows: "3.000mm" or "3.0mm"
- ✅ Success message displayed

---

## ✅ Test 3: Edit Inventory Item

**Steps:**
1. From the item detail page (from Test 2), click **Edit**
2. Verify the form loads correctly
3. Check Material Type dropdown
4. Check Thickness dropdown

**Expected Results:**
- ✅ Material Type dropdown shows "Mild Steel" selected
- ✅ Thickness dropdown shows "3.0" selected
- ✅ All other fields populated correctly

---

## ✅ Test 4: Change Dropdown Values

**Steps:**
1. On the edit form (from Test 3):
   - Change **Material Type** to "Stainless Steel"
   - Change **Thickness** to "2.0"
2. Click **Save Item**

**Expected Results:**
- ✅ Item updated successfully
- ✅ Material Type now shows: "Stainless Steel"
- ✅ Thickness now shows: "2.000mm" or "2.0mm"
- ✅ Success message displayed

---

## ✅ Test 5: Custom Material Type

**Steps:**
1. Click **Edit** on the test item
2. In **Material Type** dropdown, select the blank option (top option)
3. A prompt should appear: "Enter custom material type:"
4. Type: "Titanium"
5. Click OK
6. Click **Save Item**

**Expected Results:**
- ✅ Prompt appears when blank option selected
- ✅ Custom value "Titanium" is added to dropdown
- ✅ "Titanium" is selected in dropdown
- ✅ Item saves successfully
- ✅ Material Type shows: "Titanium"

---

## ✅ Test 6: Custom Thickness

**Steps:**
1. Click **Edit** on the test item
2. In **Thickness** dropdown, select the blank option (top option)
3. A prompt should appear: "Enter custom thickness (mm):"
4. Type: "7.5"
5. Click OK
6. Click **Save Item**

**Expected Results:**
- ✅ Prompt appears when blank option selected
- ✅ Custom value "7.5mm" is added to dropdown
- ✅ "7.5mm" is selected in dropdown
- ✅ Item saves successfully
- ✅ Thickness shows: "7.500mm" or "7.5mm"

---

## ✅ Test 7: Optional Fields (Leave Blank)

**Steps:**
1. Navigate to: `http://127.0.0.1:5000/inventory/new`
2. Fill in required fields only:
   - **Item Code:** TEST-002
   - **Name:** Test Gas Cylinder
   - **Category:** Gas
   - **Unit:** liters
3. Leave **Material Type** and **Thickness** blank (select blank option)
4. Click **Save Item**

**Expected Results:**
- ✅ Item created successfully
- ✅ Material Type is blank/NULL
- ✅ Thickness is blank/NULL
- ✅ No errors or validation issues

---

## ✅ Test 8: Edit Item with Blank Fields

**Steps:**
1. From Test 7, click **Edit** on TEST-002
2. Verify dropdowns

**Expected Results:**
- ✅ Material Type dropdown shows blank option selected
- ✅ Thickness dropdown shows blank option selected
- ✅ Form loads without errors

---

## ✅ Test 9: Existing Items (Backward Compatibility)

**If you have existing inventory items:**

**Steps:**
1. Navigate to: `http://127.0.0.1:5000/inventory/`
2. Click on an existing inventory item
3. Click **Edit**
4. Check Material Type and Thickness dropdowns

**Expected Results:**
- ✅ If item has material type matching dropdown: Value is selected
- ✅ If item has custom material type: Value displays correctly
- ✅ If item has thickness matching dropdown: Value is selected
- ✅ If item has custom thickness: Value displays correctly
- ✅ If fields are NULL: Blank option is selected
- ✅ No errors loading the form

---

## ✅ Test 10: All Material Types

**Steps:**
1. Create or edit an inventory item
2. Test each material type in the dropdown:
   - Mild Steel
   - Stainless Steel
   - Aluminum
   - Brass
   - Copper
   - Galvanized Steel
   - Other

**Expected Results:**
- ✅ All 7 material types appear in dropdown
- ✅ Each can be selected
- ✅ Each saves correctly

---

## ✅ Test 11: All Thickness Options

**Steps:**
1. Create or edit an inventory item
2. Test several thickness options:
   - 0.5mm
   - 1.0mm
   - 2.0mm
   - 3.0mm
   - 5.0mm
   - 10.0mm

**Expected Results:**
- ✅ All 12 thickness options appear in dropdown
- ✅ Each can be selected
- ✅ Each saves correctly
- ✅ Values display with correct precision

---

## ✅ Test 12: Invalid Custom Thickness

**Steps:**
1. Edit an inventory item
2. Select blank option in Thickness dropdown
3. When prompted, enter: "abc" (non-numeric)
4. Click OK

**Expected Results:**
- ✅ Prompt validates input
- ✅ Invalid value is rejected
- ✅ Dropdown returns to previous value or blank
- ✅ No error on page

---

## 🎯 Quick Smoke Test

**Fastest way to verify everything works:**

1. ✅ Open: `http://127.0.0.1:5000/inventory/new`
2. ✅ Verify Material Type is a dropdown with 7 options
3. ✅ Verify Thickness is a dropdown with 12 options
4. ✅ Create a test item with dropdown values
5. ✅ Edit the item and verify values are selected
6. ✅ Test custom value entry for both fields
7. ✅ Delete test item

**Time:** ~3 minutes

---

## 📊 Visual Verification

### Material Type Dropdown Should Show:
```
Select Material Type
Mild Steel
Stainless Steel
Aluminum
Brass
Copper
Galvanized Steel
Other
```

### Thickness Dropdown Should Show:
```
Select Thickness
0.5mm
0.8mm
1.0mm
1.2mm
1.5mm
2.0mm
3.0mm
4.0mm
5.0mm
6.0mm
8.0mm
10.0mm
```

---

## 🐛 Troubleshooting

### Material Type dropdown is empty
**Solution:** Check that `config.py` has `MATERIAL_TYPES` defined

### Thickness dropdown is empty
**Solution:** Check that database has `default_thicknesses` setting:
```sql
SELECT * FROM settings WHERE key = 'default_thicknesses';
```

### Custom value prompt doesn't appear
**Solution:** 
- Check browser console for JavaScript errors
- Verify JavaScript is enabled
- Try refreshing the page

### Values don't save
**Solution:**
- Check browser console for errors
- Check Flask server logs
- Verify database connection

---

## ✅ Success Criteria

All tests should pass with these results:

- ✅ Material Type is a dropdown (not text input)
- ✅ Thickness is a dropdown (not number input)
- ✅ Dropdowns populate with correct values
- ✅ Items can be created with dropdown values
- ✅ Items can be edited and values are selected
- ✅ Custom values can be entered
- ✅ Blank/NULL values work correctly
- ✅ Existing items display correctly
- ✅ No JavaScript errors
- ✅ No server errors

---

## 📝 Test Results Template

Use this template to record your test results:

```
Date: _______________
Tester: _______________

Test 1: View New Inventory Form          [ ] Pass  [ ] Fail
Test 2: Create Item with Dropdowns        [ ] Pass  [ ] Fail
Test 3: Edit Inventory Item               [ ] Pass  [ ] Fail
Test 4: Change Dropdown Values            [ ] Pass  [ ] Fail
Test 5: Custom Material Type              [ ] Pass  [ ] Fail
Test 6: Custom Thickness                  [ ] Pass  [ ] Fail
Test 7: Optional Fields (Leave Blank)     [ ] Pass  [ ] Fail
Test 8: Edit Item with Blank Fields       [ ] Pass  [ ] Fail
Test 9: Existing Items (Compatibility)    [ ] Pass  [ ] Fail
Test 10: All Material Types               [ ] Pass  [ ] Fail
Test 11: All Thickness Options            [ ] Pass  [ ] Fail
Test 12: Invalid Custom Thickness         [ ] Pass  [ ] Fail

Overall Result: [ ] All Pass  [ ] Some Fail

Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🎉 Completion

When all tests pass, the Inventory dropdown conversion is **complete and verified**!

**Next Steps:**
- Use the new dropdowns in production
- Monitor for any issues
- Gather user feedback
- Consider adding more material types or thicknesses if needed

---

**Happy Testing!** 🧪✨

