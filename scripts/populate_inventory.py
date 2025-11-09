"""
Populate Inventory System with Materials and Supplies

This script populates the inventory system with:
1. Sheet metal materials (1mm to 16mm for MS, SS, AL, CS)
2. Consumable supplies (wrapping, tape, gas, etc.)

All items are created as permanent inventory entries that remain visible even at zero stock.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import InventoryItem, ActivityLog
from datetime import datetime


# Material types for sheet metal
MATERIAL_TYPES = [
    'Mild Steel',
    'Stainless Steel',
    'Aluminum',
    'Carbon Steel'
]

# Thickness range for sheet metal (in mm)
THICKNESSES = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]

# Consumable supplies
CONSUMABLES = [
    {
        'name': 'Wrapping Material',
        'unit': 'rolls',
        'description': 'Protective wrapping for finished products',
        'reorder_level': 5,
        'reorder_quantity': 10
    },
    {
        'name': 'Masking Tape',
        'unit': 'rolls',
        'description': 'Masking tape for surface protection',
        'reorder_level': 10,
        'reorder_quantity': 20
    },
    {
        'name': 'Plastic Sheeting',
        'unit': 'rolls',
        'description': 'Plastic covering for product protection',
        'reorder_level': 3,
        'reorder_quantity': 10
    },
    {
        'name': 'Cleaning Brushes',
        'unit': 'pieces',
        'description': 'Brushes for cleaning laser bed and parts',
        'reorder_level': 5,
        'reorder_quantity': 10
    },
    {
        'name': 'Stone Tablets (Laser Bed)',
        'unit': 'pieces',
        'description': 'Stone tablets for laser bed protection and support',
        'reorder_level': 10,
        'reorder_quantity': 20
    }
]

# Gas supplies
GAS_SUPPLIES = [
    {
        'name': 'Oxygen Gas',
        'unit': 'liters',
        'description': 'Oxygen gas for laser cutting (thick materials)',
        'reorder_level': 500,
        'reorder_quantity': 2000
    },
    {
        'name': 'Nitrogen Gas',
        'unit': 'liters',
        'description': 'Nitrogen gas for laser cutting (stainless steel, aluminum)',
        'reorder_level': 500,
        'reorder_quantity': 2000
    },
    {
        'name': 'Compressed Air',
        'unit': 'liters',
        'description': 'Compressed air for laser cutting (thin materials)',
        'reorder_level': 1000,
        'reorder_quantity': 5000
    }
]


def generate_item_code(category, material_type=None, thickness=None, index=None):
    """
    Generate a unique item code.
    
    Format:
    - Sheet Metal: SM-{MATERIAL_ABBREV}-{THICKNESS}MM
    - Gas: GAS-{NAME_ABBREV}
    - Consumables: CONS-{INDEX:03d}
    
    Examples:
    - SM-MS-3MM (3mm Mild Steel)
    - GAS-O2 (Oxygen)
    - CONS-001 (First consumable)
    """
    if category == InventoryItem.CATEGORY_SHEET_METAL:
        # Material abbreviations
        abbrev_map = {
            'Mild Steel': 'MS',
            'Stainless Steel': 'SS',
            'Aluminum': 'AL',
            'Carbon Steel': 'CS'
        }
        abbrev = abbrev_map.get(material_type, 'UNK')
        return f"SM-{abbrev}-{int(thickness)}MM"
    
    elif category == InventoryItem.CATEGORY_GAS:
        # Gas abbreviations
        gas_abbrev_map = {
            'Oxygen Gas': 'O2',
            'Nitrogen Gas': 'N2',
            'Compressed Air': 'AIR'
        }
        # Extract gas name from full name
        for gas_name, abbrev in gas_abbrev_map.items():
            if gas_name in material_type:
                return f"GAS-{abbrev}"
        return f"GAS-{index:03d}"
    
    elif category == InventoryItem.CATEGORY_CONSUMABLES:
        return f"CONS-{index:03d}"
    
    else:
        return f"INV-{index:03d}"


def create_sheet_metal_items(dry_run=False):
    """Create inventory items for sheet metal materials."""
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*80)
    print("CREATING SHEET METAL INVENTORY ITEMS")
    print("="*80 + "\n")
    
    for material_type in MATERIAL_TYPES:
        for thickness in THICKNESSES:
            item_code = generate_item_code(
                InventoryItem.CATEGORY_SHEET_METAL,
                material_type=material_type,
                thickness=thickness
            )
            
            item_name = f"{thickness}mm {material_type}"
            
            # Check if item already exists
            existing = InventoryItem.query.filter_by(item_code=item_code).first()
            if existing:
                print(f"⏭️  EXISTS: {item_code} - {item_name}")
                skipped_count += 1
                continue
            
            if not dry_run:
                # Create inventory item
                item = InventoryItem(
                    item_code=item_code,
                    name=item_name,
                    category=InventoryItem.CATEGORY_SHEET_METAL,
                    material_type=material_type,
                    thickness=thickness,
                    unit='sheets',
                    quantity_on_hand=0,  # Start at zero
                    reorder_level=10,  # Alert when below 10 sheets
                    reorder_quantity=50,  # Order 50 sheets when restocking
                    unit_cost=None,  # To be set later
                    supplier_name=None,
                    supplier_contact=None,
                    location='Warehouse',
                    notes=f'Sheet metal material - {material_type} {thickness}mm thickness'
                )
                
                db.session.add(item)
                db.session.commit()
                
                print(f"✅ CREATED: {item_code} - {item_name}")
                created_count += 1
            else:
                print(f"✅ WOULD CREATE: {item_code} - {item_name}")
                created_count += 1
    
    return created_count, skipped_count


def create_gas_items(dry_run=False):
    """Create inventory items for gas supplies."""
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*80)
    print("CREATING GAS SUPPLY INVENTORY ITEMS")
    print("="*80 + "\n")
    
    for idx, gas_data in enumerate(GAS_SUPPLIES, start=1):
        item_code = generate_item_code(
            InventoryItem.CATEGORY_GAS,
            material_type=gas_data['name'],
            index=idx
        )
        
        # Check if item already exists
        existing = InventoryItem.query.filter_by(item_code=item_code).first()
        if existing:
            print(f"⏭️  EXISTS: {item_code} - {gas_data['name']}")
            skipped_count += 1
            continue
        
        if not dry_run:
            # Create inventory item
            item = InventoryItem(
                item_code=item_code,
                name=gas_data['name'],
                category=InventoryItem.CATEGORY_GAS,
                material_type=None,
                thickness=None,
                unit=gas_data['unit'],
                quantity_on_hand=0,  # Start at zero
                reorder_level=gas_data['reorder_level'],
                reorder_quantity=gas_data['reorder_quantity'],
                unit_cost=None,  # To be set later
                supplier_name=None,
                supplier_contact=None,
                location='Gas Storage',
                notes=gas_data['description']
            )
            
            db.session.add(item)
            db.session.commit()
            
            print(f"✅ CREATED: {item_code} - {gas_data['name']}")
            print(f"   Unit: {gas_data['unit']}, Reorder Level: {gas_data['reorder_level']}")
            created_count += 1
        else:
            print(f"✅ WOULD CREATE: {item_code} - {gas_data['name']}")
            print(f"   Unit: {gas_data['unit']}, Reorder Level: {gas_data['reorder_level']}")
            created_count += 1
    
    return created_count, skipped_count


def create_consumable_items(dry_run=False):
    """Create inventory items for consumable supplies."""
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*80)
    print("CREATING CONSUMABLE SUPPLY INVENTORY ITEMS")
    print("="*80 + "\n")
    
    for idx, consumable_data in enumerate(CONSUMABLES, start=1):
        item_code = generate_item_code(
            InventoryItem.CATEGORY_CONSUMABLES,
            index=idx
        )
        
        # Check if item already exists
        existing = InventoryItem.query.filter_by(item_code=item_code).first()
        if existing:
            print(f"⏭️  EXISTS: {item_code} - {consumable_data['name']}")
            skipped_count += 1
            continue
        
        if not dry_run:
            # Create inventory item
            item = InventoryItem(
                item_code=item_code,
                name=consumable_data['name'],
                category=InventoryItem.CATEGORY_CONSUMABLES,
                material_type=None,
                thickness=None,
                unit=consumable_data['unit'],
                quantity_on_hand=0,  # Start at zero
                reorder_level=consumable_data['reorder_level'],
                reorder_quantity=consumable_data['reorder_quantity'],
                unit_cost=None,  # To be set later
                supplier_name=None,
                supplier_contact=None,
                location='Supply Room',
                notes=consumable_data['description']
            )
            
            db.session.add(item)
            db.session.commit()
            
            print(f"✅ CREATED: {item_code} - {consumable_data['name']}")
            print(f"   Unit: {consumable_data['unit']}, Reorder Level: {consumable_data['reorder_level']}")
            created_count += 1
        else:
            print(f"✅ WOULD CREATE: {item_code} - {consumable_data['name']}")
            print(f"   Unit: {consumable_data['unit']}, Reorder Level: {consumable_data['reorder_level']}")
            created_count += 1
    
    return created_count, skipped_count


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate Inventory System with Materials and Supplies')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be created without saving to database')
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("INVENTORY POPULATION SCRIPT")
        print("="*80)
        
        if args.dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be saved to database\n")
        
        # Create sheet metal items
        sm_created, sm_skipped = create_sheet_metal_items(dry_run=args.dry_run)
        
        # Create gas items
        gas_created, gas_skipped = create_gas_items(dry_run=args.dry_run)
        
        # Create consumable items
        cons_created, cons_skipped = create_consumable_items(dry_run=args.dry_run)
        
        # Print summary
        total_created = sm_created + gas_created + cons_created
        total_skipped = sm_skipped + gas_skipped + cons_skipped
        
        print("\n" + "="*80)
        print("POPULATION SUMMARY")
        print("="*80)
        print(f"\n📦 SHEET METAL:")
        print(f"   ✅ Created: {sm_created}")
        print(f"   ⏭️  Skipped: {sm_skipped}")
        print(f"\n⚗️  GAS SUPPLIES:")
        print(f"   ✅ Created: {gas_created}")
        print(f"   ⏭️  Skipped: {gas_skipped}")
        print(f"\n🧰 CONSUMABLES:")
        print(f"   ✅ Created: {cons_created}")
        print(f"   ⏭️  Skipped: {cons_skipped}")
        print(f"\n📊 TOTAL:")
        print(f"   ✅ Created: {total_created}")
        print(f"   ⏭️  Skipped: {total_skipped}")
        print(f"   📈 Grand Total: {total_created + total_skipped}")
        print("="*80 + "\n")
        
        if args.dry_run:
            print("🔍 This was a DRY RUN - no changes were saved to the database")
            print("   Run without --dry-run to actually create the inventory items\n")
        else:
            print("✅ Inventory population complete!")
            print("   View items at: http://127.0.0.1:5000/inventory/\n")


if __name__ == '__main__':
    main()

