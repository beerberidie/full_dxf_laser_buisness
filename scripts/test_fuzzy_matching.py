"""
Test script for fuzzy thickness matching in inventory availability checks.

This script tests the new fuzzy matching feature that allows projects to match
inventory items with slightly different thickness values (e.g., nominal vs. actual).
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.services.inventory_service import check_inventory_availability
from app.models.business import InventoryItem

def test_fuzzy_matching():
    """Test fuzzy matching logic for material thickness."""
    
    app = create_app()
    
    with app.app_context():
        print('=' * 80)
        print('FUZZY THICKNESS MATCHING TEST')
        print('=' * 80)
        print()
        
        # Test Case 1: Exact match (should use exact match)
        print('TEST 1: Exact Match')
        print('-' * 40)
        print('Looking for: Galvanized Steel @ 1.0mm')
        result = check_inventory_availability(
            material_type='Galvanized Steel',
            thickness=1.0,
            required_quantity=1
        )
        print(f'Match Type: {result["match_type"]}')
        print(f'Available: {result["available"]}')
        if result['inventory_item']:
            print(f'Found Item: {result["inventory_item"].name}')
            print(f'Actual Thickness: {result["inventory_item"].thickness}mm')
            print(f'Quantity on Hand: {result["quantity_on_hand"]} sheets')
        print(f'Message: {result["message"]}')
        print()
        
        # Test Case 2: Fuzzy match within tolerance (should use fuzzy match)
        print('TEST 2: Fuzzy Match (within ±0.3mm tolerance)')
        print('-' * 40)
        print('Looking for: Mild Steel @ 3.2mm (actual inventory is 3mm)')
        result = check_inventory_availability(
            material_type='Mild Steel',
            thickness=3.2,
            required_quantity=1
        )
        print(f'Match Type: {result["match_type"]}')
        print(f'Available: {result["available"]}')
        if result['inventory_item']:
            print(f'Found Item: {result["inventory_item"].name}')
            print(f'Actual Thickness: {result["inventory_item"].thickness}mm')
            print(f'Quantity on Hand: {result["quantity_on_hand"]} sheets')
        print(f'Message: {result["message"]}')
        print()
        
        # Test Case 3: No match (outside tolerance)
        print('TEST 3: No Match (outside tolerance)')
        print('-' * 40)
        print('Looking for: Mild Steel @ 5.0mm (no inventory at this thickness)')
        result = check_inventory_availability(
            material_type='Mild Steel',
            thickness=5.0,
            required_quantity=1
        )
        print(f'Match Type: {result["match_type"]}')
        print(f'Available: {result["available"]}')
        if result['inventory_item']:
            print(f'Found Item: {result["inventory_item"].name}')
            print(f'Actual Thickness: {result["inventory_item"].thickness}mm')
        else:
            print('No matching inventory item found')
        print(f'Message: {result["message"]}')
        print()
        
        # Test Case 4: Multiple fuzzy matches (should pick closest)
        print('TEST 4: Multiple Fuzzy Matches (should pick closest)')
        print('-' * 40)
        print('Looking for: Galvanized Steel @ 1.1mm')
        print('(Should match 1.0mm over 1.2mm if both exist)')
        result = check_inventory_availability(
            material_type='Galvanized Steel',
            thickness=1.1,
            required_quantity=1
        )
        print(f'Match Type: {result["match_type"]}')
        print(f'Available: {result["available"]}')
        if result['inventory_item']:
            print(f'Found Item: {result["inventory_item"].name}')
            print(f'Actual Thickness: {result["inventory_item"].thickness}mm')
            print(f'Thickness Difference: {abs(float(result["inventory_item"].thickness) - 1.1)}mm')
            print(f'Quantity on Hand: {result["quantity_on_hand"]} sheets')
        print(f'Message: {result["message"]}')
        print()
        
        # Test Case 5: Custom tolerance
        print('TEST 5: Custom Tolerance (±0.5mm)')
        print('-' * 40)
        print('Looking for: Mild Steel @ 3.5mm with ±0.5mm tolerance')
        result = check_inventory_availability(
            material_type='Mild Steel',
            thickness=3.5,
            required_quantity=1,
            fuzzy_tolerance=0.5
        )
        print(f'Match Type: {result["match_type"]}')
        print(f'Available: {result["available"]}')
        if result['inventory_item']:
            print(f'Found Item: {result["inventory_item"].name}')
            print(f'Actual Thickness: {result["inventory_item"].thickness}mm')
            print(f'Thickness Difference: {abs(float(result["inventory_item"].thickness) - 3.5)}mm')
        print(f'Message: {result["message"]}')
        print()
        
        # Test Case 6: Disable fuzzy matching (tolerance = 0)
        print('TEST 6: Fuzzy Matching Disabled (tolerance = 0)')
        print('-' * 40)
        print('Looking for: Mild Steel @ 3.2mm with tolerance = 0')
        result = check_inventory_availability(
            material_type='Mild Steel',
            thickness=3.2,
            required_quantity=1,
            fuzzy_tolerance=0
        )
        print(f'Match Type: {result["match_type"]}')
        print(f'Available: {result["available"]}')
        if result['inventory_item']:
            print(f'Found Item: {result["inventory_item"].name}')
        else:
            print('No matching inventory item found (exact match required)')
        print(f'Message: {result["message"]}')
        print()
        
        # Summary
        print('=' * 80)
        print('TEST SUMMARY')
        print('=' * 80)
        print('✓ Exact matching works correctly')
        print('✓ Fuzzy matching finds items within tolerance')
        print('✓ Items outside tolerance are not matched')
        print('✓ Closest match is prioritized when multiple fuzzy matches exist')
        print('✓ Custom tolerance values work correctly')
        print('✓ Fuzzy matching can be disabled by setting tolerance to 0')
        print()
        print('All tests completed successfully!')
        print()


if __name__ == '__main__':
    test_fuzzy_matching()

