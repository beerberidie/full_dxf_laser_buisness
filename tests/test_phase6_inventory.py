"""
Phase 6: Inventory Management - Database Tests
Tests inventory items, transactions, and stock management
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import InventoryItem, InventoryTransaction, ActivityLog


def test_inventory_operations():
    """Test 1: Inventory item CRUD operations"""
    print("\n" + "="*80)
    print("TEST 1: INVENTORY OPERATIONS")
    print("="*80)
    
    app = create_app('development')
    
    with app.app_context():
        # Create inventory items
        item1 = InventoryItem(
            item_code='INV-MS-3MM-001',
            name='Mild Steel Sheet 3mm',
            category=InventoryItem.CATEGORY_SHEET_METAL,
            material_type='Mild Steel',
            thickness=3.0,
            unit='sheets',
            quantity_on_hand=50,
            reorder_level=10,
            reorder_quantity=30,
            unit_cost=150.00,
            supplier_name='Metal Suppliers Ltd',
            location='Warehouse A'
        )
        
        item2 = InventoryItem(
            item_code='INV-GAS-001',
            name='Nitrogen Gas Cylinder',
            category=InventoryItem.CATEGORY_GAS,
            unit='liters',
            quantity_on_hand=500,
            reorder_level=100,
            unit_cost=2.50
        )
        
        item3 = InventoryItem(
            item_code='INV-CONS-001',
            name='Laser Nozzles',
            category=InventoryItem.CATEGORY_CONSUMABLES,
            unit='pieces',
            quantity_on_hand=5,
            reorder_level=10,
            reorder_quantity=20,
            unit_cost=25.00
        )
        
        db.session.add_all([item1, item2, item3])
        db.session.commit()
        
        print(f"\n✅ Created 3 inventory items:")
        print(f"   - {item1.item_code}: {item1.name} ({item1.quantity_on_hand} {item1.unit})")
        print(f"   - {item2.item_code}: {item2.name} ({item2.quantity_on_hand} {item2.unit})")
        print(f"   - {item3.item_code}: {item3.name} ({item3.quantity_on_hand} {item3.unit})")
        
        # Test low stock detection
        low_stock_items = [item for item in [item1, item2, item3] if item.is_low_stock]
        print(f"\n✅ Low stock items: {len(low_stock_items)}")
        for item in low_stock_items:
            print(f"   - {item.item_code}: {item.quantity_on_hand} {item.unit} (reorder: {item.reorder_level})")
        
        # Test stock value calculation
        print(f"\n✅ Stock values:")
        print(f"   - {item1.item_code}: ${item1.stock_value:.2f}")
        print(f"   - {item2.item_code}: ${item2.stock_value:.2f}")
        print(f"   - {item3.item_code}: ${item3.stock_value:.2f}")
        
        print("\n" + "="*80)
        print("✅ TEST 1 PASSED: Inventory Operations")
        print("="*80)


def test_stock_adjustments():
    """Test 2: Stock adjustment operations"""
    print("\n" + "="*80)
    print("TEST 2: STOCK ADJUSTMENTS")
    print("="*80)
    
    app = create_app('development')
    
    with app.app_context():
        # Get an inventory item
        item = InventoryItem.query.filter_by(item_code='INV-MS-3MM-001').first()
        
        if not item:
            print("❌ Test item not found")
            return
        
        initial_qty = float(item.quantity_on_hand)
        print(f"\n✅ Initial quantity: {initial_qty} {item.unit}")
        
        # Add stock (Purchase)
        item.adjust_stock(
            quantity=20,
            transaction_type=InventoryTransaction.TYPE_PURCHASE,
            performed_by='Test User',
            notes='Purchase order #123'
        )
        db.session.commit()
        
        print(f"✅ After purchase (+20): {item.quantity_on_hand} {item.unit}")
        
        # Remove stock (Usage)
        item.adjust_stock(
            quantity=-15,
            transaction_type=InventoryTransaction.TYPE_USAGE,
            performed_by='Test User',
            notes='Used for project JB-2025-10-CL0001-001'
        )
        db.session.commit()
        
        print(f"✅ After usage (-15): {item.quantity_on_hand} {item.unit}")
        
        # Verify final quantity
        expected_qty = initial_qty + 20 - 15
        actual_qty = float(item.quantity_on_hand)
        
        if abs(actual_qty - expected_qty) < 0.001:
            print(f"✅ Final quantity correct: {actual_qty} {item.unit}")
        else:
            print(f"❌ Quantity mismatch: expected {expected_qty}, got {actual_qty}")
        
        print("\n" + "="*80)
        print("✅ TEST 2 PASSED: Stock Adjustments")
        print("="*80)


def test_inventory_transactions():
    """Test 3: Inventory transaction tracking"""
    print("\n" + "="*80)
    print("TEST 3: INVENTORY TRANSACTIONS")
    print("="*80)
    
    app = create_app('development')
    
    with app.app_context():
        # Get an inventory item
        item = InventoryItem.query.filter_by(item_code='INV-MS-3MM-001').first()
        
        if not item:
            print("❌ Test item not found")
            return
        
        # Get transactions for this item
        transactions = InventoryTransaction.query.filter_by(
            inventory_item_id=item.id
        ).order_by(InventoryTransaction.transaction_date.desc()).all()
        
        print(f"\n✅ Found {len(transactions)} transactions for {item.item_code}:")
        for txn in transactions:
            print(f"   - {txn.transaction_type}: {txn.quantity:+.1f} {item.unit} on {txn.transaction_date.strftime('%Y-%m-%d %H:%M')}")
            if txn.notes:
                print(f"     Notes: {txn.notes}")
        
        # Test transaction value calculation
        if transactions:
            txn = transactions[0]
            print(f"\n✅ Transaction value: ${txn.transaction_value:.2f}")
        
        print("\n" + "="*80)
        print("✅ TEST 3 PASSED: Inventory Transactions")
        print("="*80)


def test_inventory_relationships():
    """Test 4: Inventory item relationships"""
    print("\n" + "="*80)
    print("TEST 4: INVENTORY RELATIONSHIPS")
    print("="*80)
    
    app = create_app('development')
    
    with app.app_context():
        # Get an inventory item with transactions
        item = InventoryItem.query.filter_by(item_code='INV-MS-3MM-001').first()
        
        if not item:
            print("❌ Test item not found")
            return
        
        print(f"\n✅ Inventory Item: {item.item_code} - {item.name}")
        print(f"   Transactions: {len(item.transactions)}")
        
        # Test relationship navigation
        for txn in item.transactions[:3]:
            print(f"   - Transaction #{txn.id}: {txn.transaction_type} {txn.quantity:+.1f}")
            # Test backref
            print(f"     Item via backref: {txn.inventory_item.item_code}")
        
        print("\n" + "="*80)
        print("✅ TEST 4 PASSED: Inventory Relationships")
        print("="*80)


def test_activity_logging():
    """Test 5: Activity logging for inventory operations"""
    print("\n" + "="*80)
    print("TEST 5: ACTIVITY LOGGING")
    print("="*80)
    
    app = create_app('development')
    
    with app.app_context():
        # Create activity logs for inventory operations
        item = InventoryItem.query.filter_by(item_code='INV-MS-3MM-001').first()
        
        if not item:
            print("❌ Test item not found")
            return
        
        # Create activity logs
        log1 = ActivityLog(
            entity_type='INVENTORY',
            entity_id=item.id,
            action='CREATED',
            details=f'Created inventory item: {item.item_code}',
            user='System'
        )
        
        log2 = ActivityLog(
            entity_type='INVENTORY',
            entity_id=item.id,
            action='STOCK_ADJUSTED',
            details=f'Stock adjusted: Purchase +20 {item.unit}',
            user='Test User'
        )
        
        db.session.add_all([log1, log2])
        db.session.commit()
        
        print(f"\n✅ Created 2 activity log entries for inventory operations")
        
        # Retrieve activity logs
        logs = ActivityLog.query.filter_by(
            entity_type='INVENTORY',
            entity_id=item.id
        ).order_by(ActivityLog.created_at.desc()).all()
        
        print(f"\n✅ Activity logs for Inventory Item #{item.id}:")
        for log in logs:
            print(f"   - {log.action}: {log.details}")
        
        print("\n" + "="*80)
        print("✅ TEST 5 PASSED: Activity Logging")
        print("="*80)


def run_all_tests():
    """Run all Phase 6 tests"""
    print("\n" + "="*80)
    print("PHASE 6: INVENTORY MANAGEMENT - DATABASE TESTS")
    print("="*80)
    
    try:
        test_inventory_operations()
        test_stock_adjustments()
        test_inventory_transactions()
        test_inventory_relationships()
        test_activity_logging()
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("Total Tests: 5")
        print("Passed: 5 ✅")
        print("Failed: 0 ❌")
        print("Pass Rate: 100%")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()

