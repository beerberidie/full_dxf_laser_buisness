# Phase 5 Testing Guide

## Manual Testing Checklist

Follow these steps to manually test the Phase 5 dropdown conversions:

---

## 1. Start the Flask Server

```bash
python app.py
```

Navigate to: `http://localhost:5000`

---

## 2. Test Operator Dropdown

1. Navigate to any project
2. Click "Log Laser Run" button
3. **Verify:**
   - ✅ Operator field is a dropdown (not text input)
   - ✅ Dropdown shows "Select operator..." placeholder
   - ✅ Dropdown contains 3 operators:
     - System
     - Operator 1
     - Operator 2
   - ✅ Operators are sorted alphabetically

---

## 3. Test Material Type Dropdown

1. On the same form, locate the Material Type field
2. **Verify:**
   - ✅ Material Type field is a dropdown (not text input)
   - ✅ Dropdown shows "Select material type..." placeholder
   - ✅ Dropdown contains material types from config:
     - Aluminum
     - Brass
     - Copper
     - Galvanized Steel
     - Mild Steel
     - Stainless Steel
     - Vastrap
     - Other

---

## 4. Test Preset Dropdown

1. On the same form, locate the Machine Settings Preset field
2. **Verify:**
   - ✅ Preset field is a dropdown
   - ✅ Dropdown shows "Select preset (optional)..." placeholder
   - ✅ Dropdown contains 7 presets:
     - Mild Steel 1mm - Standard
     - Mild Steel 2mm - Standard
     - Mild Steel 3mm - Standard
     - Stainless Steel 1mm - Standard
     - Stainless Steel 2mm - Standard
     - Aluminum 1mm - Standard
     - Aluminum 2mm - Standard
   - ✅ Help text shows: "Selecting a preset will auto-populate machine settings below"

---

## 5. Test Preset Filtering by Material Type

1. **Select Material Type:** "Mild Steel"
2. **Verify:**
   - ✅ Preset dropdown now shows only Mild Steel presets (3 presets)
   - ✅ Placeholder updates to "Select preset (3 available)..."
   - ✅ Other material presets are hidden

3. **Change Material Type:** "Aluminum"
4. **Verify:**
   - ✅ Preset dropdown now shows only Aluminum presets (2 presets)
   - ✅ Placeholder updates to "Select preset (2 available)..."

5. **Clear Material Type:** Select "Select material type..."
6. **Verify:**
   - ✅ All presets are visible again (7 presets)

---

## 6. Test Preset Filtering by Thickness

1. **Enter Material Thickness:** 1.0
2. **Verify:**
   - ✅ Preset dropdown shows only 1mm presets (4 presets)
   - ✅ Placeholder updates to "Select preset (4 available)..."

3. **Change Thickness:** 2.0
4. **Verify:**
   - ✅ Preset dropdown shows only 2mm presets (3 presets)

5. **Enter non-matching thickness:** 5.0
6. **Verify:**
   - ✅ Preset dropdown shows no presets
   - ✅ Placeholder shows "No matching presets found"

---

## 7. Test Preset Filtering by Both Material and Thickness

1. **Select Material Type:** "Mild Steel"
2. **Enter Thickness:** 2.0
3. **Verify:**
   - ✅ Preset dropdown shows only "Mild Steel 2mm - Standard" (1 preset)
   - ✅ Placeholder shows "Select preset (1 available)..."

---

## 8. Test Preset Auto-Population

1. **Clear the form** (refresh page if needed)
2. **Select Material Type:** "Mild Steel"
3. **Enter Thickness:** 1.0
4. **Select Preset:** "Mild Steel 1mm - Standard"
5. **Verify all machine settings fields are populated:**
   - ✅ Nozzle: "1.5mm Single"
   - ✅ Cut Speed: "3000"
   - ✅ Nozzle Height: "1.0"
   - ✅ Gas Type: "Oxygen"
   - ✅ Gas Pressure: "0.8"
   - ✅ Peak Power: "2000"
   - ✅ Actual Power: "1800"
   - ✅ Duty Cycle: "90"
   - ✅ Pulse Frequency: "5000"
   - ✅ (Other fields may be empty depending on preset data)

---

## 9. Test Manual Override

1. **With preset still selected**, manually change a field:
   - Change "Cut Speed" from "3000" to "3500"
2. **Verify:**
   - ✅ Field value changes to 3500
   - ✅ No error or warning
   - ✅ Preset remains selected

---

## 10. Test Material/Thickness Change Warning

1. **With preset selected and settings populated:**
2. **Change Material Type** to "Stainless Steel"
3. **Verify:**
   - ✅ Alert appears: "Changing material type may invalidate the selected preset. Do you want to clear the preset selection?"
   - ✅ If you click "OK": Preset is cleared, settings remain
   - ✅ If you click "Cancel": Material type reverts, preset remains

4. **Change Thickness** to 3.0
5. **Verify:**
   - ✅ Similar alert appears for thickness change

---

## 11. Test Form Submission

1. **Fill out the complete form:**
   - Operator: "Operator 1"
   - Cut Time: 45
   - Material Type: "Mild Steel"
   - Material Thickness: 2.0
   - Preset: "Mild Steel 2mm - Standard"
   - Raw Material Count: 1
   - Parts Produced: 50
   - (Machine settings should be auto-populated from preset)

2. **Click "Log Run"**

3. **Verify:**
   - ✅ Success message appears
   - ✅ Redirected to project detail page
   - ✅ New laser run appears in the list
   - ✅ Operator shows "Operator 1"
   - ✅ Preset name shows below operator

---

## 12. Test Display Templates

### **Queue Runs Page** (`/queue/runs`)
1. Navigate to Queue → Laser Runs
2. **Verify:**
   - ✅ Operator column shows operator name
   - ✅ If preset was used, shows preset name below operator

### **Queue Detail Page** (`/queue/detail/<id>`)
1. Navigate to a queue item with laser runs
2. **Verify:**
   - ✅ Operator column shows operator name
   - ✅ If preset was used, shows preset name below operator

### **Production Report** (`/reports/production`)
1. Navigate to Reports → Production Report
2. **Verify:**
   - ✅ Operator column shows operator name

### **Project Detail Page** (`/projects/detail/<id>`)
1. Navigate to a project with laser runs
2. Scroll to "Laser Run History" section
3. **Verify:**
   - ✅ Operator column shows operator name

---

## 13. Test Backward Compatibility

1. **Check existing laser runs** (if any exist from before Phase 5)
2. **Verify:**
   - ✅ Old runs still display correctly
   - ✅ Operator name shows from legacy text field
   - ✅ No errors or missing data

---

## 14. Test Edge Cases

### **Empty Operator:**
1. Try to submit form without selecting operator
2. **Verify:**
   - ✅ Form submits successfully (operator is optional)
   - ✅ Operator shows "N/A" in display

### **Empty Preset:**
1. Submit form without selecting preset
2. **Verify:**
   - ✅ Form submits successfully
   - ✅ Machine settings can be entered manually
   - ✅ No preset name shown in display

### **Invalid Operator ID:**
1. (Developer test) Manually submit form with invalid operator_id
2. **Verify:**
   - ✅ Error message: "Selected operator not found"
   - ✅ Form is not submitted

### **Inactive Operator:**
1. (Developer test) Deactivate an operator in database
2. **Verify:**
   - ✅ Operator no longer appears in dropdown
   - ✅ Cannot select inactive operator

---

## 15. Test JavaScript Console

1. Open browser developer tools (F12)
2. Go to Console tab
3. Navigate to Log Laser Run form
4. **Verify:**
   - ✅ No JavaScript errors
   - ✅ No warnings

---

## Expected Results Summary

✅ **All dropdowns populate correctly**
✅ **Preset filtering works by material and thickness**
✅ **Auto-population works when preset selected**
✅ **Manual override works**
✅ **Warnings appear when material/thickness changed**
✅ **Form submission saves data correctly**
✅ **Display templates show operator and preset names**
✅ **Backward compatibility maintained**
✅ **No JavaScript errors**

---

## Troubleshooting

### **Dropdowns are empty:**
- Check that operators and presets exist in database
- Run `python test_phase10_part5.py` to verify data

### **Preset filtering not working:**
- Check browser console for JavaScript errors
- Verify JavaScript is enabled
- Try hard refresh (Ctrl+F5)

### **Auto-population not working:**
- Check that preset has data in all fields
- Verify data attributes are present in HTML
- Check browser console for errors

### **Form submission fails:**
- Check Flask server logs for errors
- Verify database connection
- Check that operator_id and preset_id are valid

---

## Success Criteria

Phase 5 is considered successful if:

1. ✅ All 3 dropdowns (Operator, Material Type, Preset) work correctly
2. ✅ Preset filtering works by material type and thickness
3. ✅ Auto-population works when preset is selected
4. ✅ Manual override is allowed
5. ✅ Form submission saves data correctly with relationships
6. ✅ Display templates show operator and preset names
7. ✅ Backward compatibility is maintained
8. ✅ No JavaScript errors in console
9. ✅ All automated tests pass

---

**Ready to test!** 🚀

