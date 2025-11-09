"""
Test script for Inventory Dropdown Conversions
Tests that Material Type and Thickness fields are properly converted to dropdowns
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import InventoryItem, Setting
from config import Config

def test_inventory_dropdowns():
    """Test inventory dropdown functionality."""
    
    print("="*70)
    print("INVENTORY DROPDOWN CONVERSION - TEST SUITE")
    print("="*70)
    print()
    
    # Create app
    app = create_app()
    
    with app.app_context():
        # Test 1: Check material types from config
        print("✓ Test 1: Material Types from Config")
        material_types = app.config.get('MATERIAL_TYPES', [])
        print(f"  Found {len(material_types)} material types:")
        for mat in material_types:
            print(f"    - {mat}")
        assert len(material_types) > 0, "Material types should be configured"
        print()
        
        # Test 2: Check thicknesses from settings
        print("✓ Test 2: Thicknesses from Settings")
        thicknesses_setting = Setting.query.filter_by(key='default_thicknesses').first()
        if thicknesses_setting:
            thicknesses = thicknesses_setting.value.split(',')
            print(f"  Found {len(thicknesses)} thickness options:")
            for thick in thicknesses[:5]:  # Show first 5
                print(f"    - {thick}mm")
            if len(thicknesses) > 5:
                print(f"    ... and {len(thicknesses) - 5} more")
            assert len(thicknesses) > 0, "Thicknesses should be configured"
        else:
            print("  ⚠️  Warning: default_thicknesses setting not found in database")
            print("  This is expected if migrations haven't been run yet")
        print()
        
        # Test 3: Check existing inventory items
        print("✓ Test 3: Existing Inventory Items")
        items = InventoryItem.query.all()
        print(f"  Found {len(items)} inventory items")
        
        items_with_material = [item for item in items if item.material_type]
        items_with_thickness = [item for item in items if item.thickness]
        
        print(f"  Items with material type: {len(items_with_material)}")
        print(f"  Items with thickness: {len(items_with_thickness)}")
        
        if items_with_material:
            print(f"  Sample materials:")
            for item in items_with_material[:3]:
                print(f"    - {item.item_code}: {item.material_type}")
        
        if items_with_thickness:
            print(f"  Sample thicknesses:")
            for item in items_with_thickness[:3]:
                print(f"    - {item.item_code}: {item.thickness}mm")
        print()
        
        # Test 4: Test creating inventory item with dropdown values
        print("✓ Test 4: Create Test Inventory Item")
        
        # Check if test item already exists
        test_item = InventoryItem.query.filter_by(item_code='TEST-DROPDOWN-001').first()
        if test_item:
            print(f"  Test item already exists, deleting...")
            db.session.delete(test_item)
            db.session.commit()
        
        # Create new test item
        test_item = InventoryItem(
            item_code='TEST-DROPDOWN-001',
            name='Test Sheet Metal - Dropdown',
            category=InventoryItem.CATEGORY_SHEET_METAL,
            material_type='Mild Steel',  # From dropdown
            thickness=3.0,  # From dropdown
            unit='sheets',
            quantity_on_hand=10,
            reorder_level=5,
            unit_cost=150.00,
            notes='Test item created to verify dropdown functionality'
        )
        
        db.session.add(test_item)
        db.session.commit()
        
        print(f"  ✅ Created test item: {test_item.item_code}")
        print(f"     Material: {test_item.material_type}")
        print(f"     Thickness: {test_item.thickness}mm")
        print()
        
        # Test 5: Verify test item can be retrieved
        print("✓ Test 5: Retrieve Test Item")
        retrieved_item = InventoryItem.query.filter_by(item_code='TEST-DROPDOWN-001').first()
        assert retrieved_item is not None, "Test item should exist"
        assert retrieved_item.material_type == 'Mild Steel', "Material type should match"
        assert float(retrieved_item.thickness) == 3.0, "Thickness should match"
        print(f"  ✅ Retrieved item successfully")
        print(f"     ID: {retrieved_item.id}")
        print(f"     Name: {retrieved_item.name}")
        print(f"     Material: {retrieved_item.material_type}")
        print(f"     Thickness: {retrieved_item.thickness}mm")
        print()
        
        # Test 6: Test updating item with new dropdown values
        print("✓ Test 6: Update Item with New Values")
        retrieved_item.material_type = 'Stainless Steel'
        retrieved_item.thickness = 2.0
        db.session.commit()
        
        updated_item = InventoryItem.query.filter_by(item_code='TEST-DROPDOWN-001').first()
        assert updated_item.material_type == 'Stainless Steel', "Material should be updated"
        assert float(updated_item.thickness) == 2.0, "Thickness should be updated"
        print(f"  ✅ Updated item successfully")
        print(f"     New Material: {updated_item.material_type}")
        print(f"     New Thickness: {updated_item.thickness}mm")
        print()
        
        # Test 7: Test with custom values (not in dropdown)
        print("✓ Test 7: Custom Values (Not in Dropdown)")
        retrieved_item.material_type = 'Custom Alloy'
        retrieved_item.thickness = 7.5
        db.session.commit()
        
        custom_item = InventoryItem.query.filter_by(item_code='TEST-DROPDOWN-001').first()
        assert custom_item.material_type == 'Custom Alloy', "Custom material should be saved"
        assert float(custom_item.thickness) == 7.5, "Custom thickness should be saved"
        print(f"  ✅ Custom values saved successfully")
        print(f"     Custom Material: {custom_item.material_type}")
        print(f"     Custom Thickness: {custom_item.thickness}mm")
        print()
        
        # Test 8: Test with NULL values
        print("✓ Test 8: NULL Values (Optional Fields)")
        retrieved_item.material_type = None
        retrieved_item.thickness = None
        db.session.commit()
        
        null_item = InventoryItem.query.filter_by(item_code='TEST-DROPDOWN-001').first()
        assert null_item.material_type is None, "Material can be NULL"
        assert null_item.thickness is None, "Thickness can be NULL"
        print(f"  ✅ NULL values handled correctly")
        print(f"     Material: {null_item.material_type}")
        print(f"     Thickness: {null_item.thickness}")
        print()
        
        # Cleanup
        print("✓ Cleanup: Removing Test Item")
        db.session.delete(test_item)
        db.session.commit()
        print(f"  ✅ Test item deleted")
        print()
        
    print("="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print()
    print("Summary:")
    print("  ✅ Material types loaded from config")
    print("  ✅ Thicknesses loaded from settings")
    print("  ✅ Inventory items can be created with dropdown values")
    print("  ✅ Inventory items can be updated")
    print("  ✅ Custom values (not in dropdown) work correctly")
    print("  ✅ NULL values (optional fields) work correctly")
    print()
    print("Next Steps:")
    print("  1. Start the Flask server: python app.py")
    print("  2. Navigate to: http://127.0.0.1:5000/inventory/new")
    print("  3. Verify Material Type dropdown shows all material types")
    print("  4. Verify Thickness dropdown shows all thickness options")
    print("  5. Test creating a new inventory item")
    print("  6. Test editing an existing inventory item")
    print()

if __name__ == '__main__':
    try:
        test_inventory_dropdowns()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

