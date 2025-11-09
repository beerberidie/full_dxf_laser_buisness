# Fuzzy Thickness Matching for Inventory

**Feature:** Intelligent material thickness matching with tolerance  
**Version:** 1.0  
**Date:** 2025-10-28  
**Status:** ✅ Implemented & Tested

---

## Overview

The fuzzy thickness matching feature allows the inventory system to intelligently match project material requirements with available inventory, even when there are slight differences between nominal and actual material thickness values.

This is particularly important for sheet metal materials where:
- **Nominal thickness** is what customers specify (e.g., "1mm steel")
- **Actual thickness** may vary slightly (e.g., 1.2mm actual thickness)

### Problem Solved

Previously, the system used **exact matching** for material thickness, which caused issues when:
- Inventory items were recorded with actual thickness (1.2mm)
- Projects specified nominal thickness (1mm)
- Auto-queue would fail due to "no matching inventory"

### Solution

The new fuzzy matching algorithm:
1. **First attempts exact match** (preferred)
2. **Falls back to fuzzy match** within a configurable tolerance (default: ±0.3mm)
3. **Prioritizes closest match** when multiple items are within tolerance
4. **Indicates match type** in results for transparency

---

## Technical Implementation

### Function Signature

```python
def check_inventory_availability(
    material_type: str, 
    thickness: float, 
    required_quantity: float,
    fuzzy_tolerance: float = 0.3
) -> Dict
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `material_type` | str | Required | Material type (e.g., 'Mild Steel', 'Galvanized Steel') |
| `thickness` | float | Required | Nominal thickness in mm |
| `required_quantity` | float | Required | Required quantity in sheets |
| `fuzzy_tolerance` | float | 0.3 | Tolerance for fuzzy matching in mm (±) |

### Return Dictionary

```python
{
    'available': bool,              # Whether enough inventory is available
    'inventory_item': InventoryItem, # Matching inventory item (or None)
    'quantity_on_hand': float,      # Current quantity in inventory
    'required_quantity': float,     # Required quantity
    'shortage': float,              # Shortage amount (0 if available)
    'match_type': str,              # 'exact', 'fuzzy', or 'none'
    'message': str                  # Human-readable status message
}
```

### Match Types

| Match Type | Description | Example |
|------------|-------------|---------|
| `exact` | Exact thickness match found | Looking for 1.0mm, found 1.0mm |
| `fuzzy` | Match within tolerance | Looking for 1.0mm, found 1.2mm (within ±0.3mm) |
| `none` | No match found | Looking for 5.0mm, no inventory within tolerance |

---

## Algorithm Details

### Step 1: Exact Match (Preferred)

```python
inventory_item = InventoryItem.query.filter_by(
    category=InventoryItem.CATEGORY_SHEET_METAL,
    material_type=material_type,
    thickness=thickness
).first()
```

If an exact match is found, it is used immediately.

### Step 2: Fuzzy Match (Fallback)

If no exact match exists:

```python
min_thickness = thickness - fuzzy_tolerance
max_thickness = thickness + fuzzy_tolerance

fuzzy_matches = InventoryItem.query.filter(
    InventoryItem.category == InventoryItem.CATEGORY_SHEET_METAL,
    InventoryItem.material_type == material_type,
    InventoryItem.thickness.isnot(None),
    InventoryItem.thickness >= min_thickness,
    InventoryItem.thickness <= max_thickness
).all()
```

### Step 3: Prioritization

When multiple fuzzy matches are found, they are sorted by:

1. **Closest thickness match** (primary)
2. **Highest quantity on hand** (secondary)

```python
fuzzy_matches.sort(
    key=lambda item: (
        abs(float(item.thickness) - thickness),  # Closest first
        -float(item.quantity_on_hand)            # Highest quantity second
    )
)
inventory_item = fuzzy_matches[0]
```

---

## Usage Examples

### Example 1: Exact Match

```python
result = check_inventory_availability(
    material_type='Galvanized Steel',
    thickness=1.0,
    required_quantity=5
)

# Result:
# {
#     'available': True,
#     'match_type': 'exact',
#     'inventory_item': <InventoryItem: 1.2 / 1mm Galv>,
#     'quantity_on_hand': 10.0,
#     'message': 'Sufficient inventory available'
# }
```

### Example 2: Fuzzy Match

```python
result = check_inventory_availability(
    material_type='Mild Steel',
    thickness=3.2,  # Looking for 3.2mm
    required_quantity=2
)

# Result:
# {
#     'available': True,
#     'match_type': 'fuzzy',
#     'inventory_item': <InventoryItem: 3mm Mild Steel>,  # Found 3.0mm
#     'quantity_on_hand': 6.0,
#     'message': 'Sufficient inventory available (using 3.0mm material - fuzzy match)'
# }
```

### Example 3: Custom Tolerance

```python
result = check_inventory_availability(
    material_type='Mild Steel',
    thickness=3.5,
    required_quantity=1,
    fuzzy_tolerance=0.5  # ±0.5mm instead of default ±0.3mm
)

# Result:
# {
#     'available': True,
#     'match_type': 'fuzzy',
#     'inventory_item': <InventoryItem: 3mm Mild Steel>,  # 0.5mm difference
#     'message': 'Sufficient inventory available (using 3.0mm material - fuzzy match)'
# }
```

### Example 4: Disable Fuzzy Matching

```python
result = check_inventory_availability(
    material_type='Mild Steel',
    thickness=3.2,
    required_quantity=1,
    fuzzy_tolerance=0  # Exact match only
)

# Result:
# {
#     'available': False,
#     'match_type': 'none',
#     'inventory_item': None,
#     'message': 'No inventory item found for Mild Steel 3.2mm (searched ±0mm)'
# }
```

---

## Integration with Auto-Scheduler

The fuzzy matching feature is automatically used by the auto-scheduler when checking inventory availability for projects with POP received.

**Flow:**
1. Project POP is marked as received
2. Auto-scheduler calls `check_project_inventory_availability(project)`
3. This calls `check_inventory_availability()` with default ±0.3mm tolerance
4. If fuzzy match is found, project is added to queue
5. Flash message indicates if fuzzy match was used

**User Feedback:**
- Exact match: `"✅ Project added to queue - Inventory reserved"`
- Fuzzy match: `"✅ Project added to queue - Inventory reserved (using 3.0mm material - fuzzy match)"`

---

## Configuration

### Default Tolerance

The default tolerance is **±0.3mm**, which is suitable for most sheet metal applications.

To change the default, modify the function signature in `app/services/inventory_service.py`:

```python
def check_inventory_availability(
    material_type: str, 
    thickness: float, 
    required_quantity: float,
    fuzzy_tolerance: float = 0.5  # Change default here
) -> Dict:
```

### Per-Call Tolerance

You can override the tolerance for specific calls:

```python
# Tighter tolerance for precision work
result = check_inventory_availability(
    material_type='Stainless Steel',
    thickness=0.5,
    required_quantity=10,
    fuzzy_tolerance=0.1  # Only ±0.1mm tolerance
)

# Looser tolerance for rough work
result = check_inventory_availability(
    material_type='Mild Steel',
    thickness=6.0,
    required_quantity=5,
    fuzzy_tolerance=0.5  # Allow ±0.5mm tolerance
)
```

---

## Testing

### Test Script

Run the comprehensive test suite:

```bash
python scripts/test_fuzzy_matching.py
```

### Test Coverage

The test script verifies:
- ✅ Exact matching works correctly
- ✅ Fuzzy matching finds items within tolerance
- ✅ Items outside tolerance are not matched
- ✅ Closest match is prioritized when multiple fuzzy matches exist
- ✅ Custom tolerance values work correctly
- ✅ Fuzzy matching can be disabled by setting tolerance to 0

---

## Best Practices

### 1. Inventory Data Entry

**Recommended:** Use **nominal thickness** in inventory items to match what customers specify:
- ✅ Good: "1mm Galvanized Steel" with thickness = 1.0mm
- ❌ Avoid: "1mm Galvanized Steel" with thickness = 1.2mm (actual)

**If using actual thickness:** Name the item clearly:
- ✅ Good: "1.2 / 1mm Galv" with thickness = 1.0mm (nominal)
- ✅ Acceptable: "1.2mm Galv (nominal 1mm)" with thickness = 1.0mm

### 2. Tolerance Selection

| Material Thickness | Recommended Tolerance |
|-------------------|----------------------|
| < 1mm | ±0.1mm |
| 1-3mm | ±0.3mm (default) |
| 3-6mm | ±0.3mm to ±0.5mm |
| > 6mm | ±0.5mm |

### 3. Monitoring Fuzzy Matches

Review the activity log and flash messages to identify when fuzzy matches are being used frequently. This may indicate:
- Inventory thickness values need to be updated
- Projects are specifying non-standard thicknesses
- Tolerance may need adjustment

---

## Related Files

- **Implementation:** `app/services/inventory_service.py`
- **Auto-scheduler:** `app/services/auto_scheduler.py`
- **Test Script:** `scripts/test_fuzzy_matching.py`
- **Models:** `app/models/business.py` (InventoryItem)

---

## Future Enhancements

Potential improvements for future versions:

1. **Material-specific tolerances:** Different tolerances for different material types
2. **Thickness-based tolerances:** Percentage-based tolerance (e.g., ±5% instead of fixed ±0.3mm)
3. **Admin UI:** Configure tolerance through admin settings page
4. **Analytics:** Track fuzzy match usage to identify data quality issues
5. **Warnings:** Alert when fuzzy matches are used frequently for a specific material

---

## Changelog

### Version 1.0 (2025-10-28)
- ✅ Initial implementation of fuzzy thickness matching
- ✅ Default tolerance of ±0.3mm
- ✅ Prioritization by closest match and highest quantity
- ✅ Match type indicator in results
- ✅ Comprehensive test suite
- ✅ Integration with auto-scheduler

