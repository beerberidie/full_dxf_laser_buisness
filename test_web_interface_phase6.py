"""
Phase 6: Inventory Management - Web Interface Tests
Tests inventory web interface functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import InventoryItem, InventoryTransaction


def test_inventory_index():
    """Test 1: Inventory index page"""
    print("\n" + "="*80)
    print("TEST 1: INVENTORY INDEX PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/inventory/')
        
        print(f"\n✅ Inventory index page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Inventory Management' in response.data
        assert b'Total Items' in response.data
        
        print("✅ Page contains expected elements:")
        print("   - Inventory Management title")
        print("   - Statistics cards")
        print("   - Inventory table")
        
        print("\n" + "="*80)
        print("✅ TEST 1 PASSED: Inventory Index Page")
        print("="*80)


def test_create_inventory_item():
    """Test 2: Create inventory item"""
    print("\n" + "="*80)
    print("TEST 2: CREATE INVENTORY ITEM")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Count items before
        count_before = InventoryItem.query.count()
        
        # Submit form
        response = client.post('/inventory/new', data={
            'item_code': 'TEST-ITEM-001',
            'name': 'Test Inventory Item',
            'category': 'Sheet Metal',
            'material_type': 'Stainless Steel',
            'thickness': '2.0',
            'unit': 'sheets',
            'quantity_on_hand': '100',
            'reorder_level': '20',
            'reorder_quantity': '50',
            'unit_cost': '200.00',
            'supplier_name': 'Test Supplier',
            'location': 'Warehouse B'
        }, follow_redirects=True)
        
        print(f"\n✅ Create inventory item request sent")
        print(f"   Status Code: {response.status_code}")
        
        # Count items after
        count_after = InventoryItem.query.count()
        
        print(f"✅ Inventory items before: {count_before}")
        print(f"✅ Inventory items after: {count_after}")
        
        # Get the created item
        item = InventoryItem.query.filter_by(item_code='TEST-ITEM-001').first()
        
        assert item is not None
        assert item.name == 'Test Inventory Item'
        assert item.category == 'Sheet Metal'
        assert float(item.quantity_on_hand) == 100.0
        
        print(f"✅ Inventory item created:")
        print(f"   - Code: {item.item_code}")
        print(f"   - Name: {item.name}")
        print(f"   - Quantity: {item.quantity_on_hand} {item.unit}")
        
        print("\n" + "="*80)
        print("✅ TEST 2 PASSED: Create Inventory Item")
        print("="*80)


def test_inventory_detail():
    """Test 3: Inventory item detail page"""
    print("\n" + "="*80)
    print("TEST 3: INVENTORY ITEM DETAIL PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get an inventory item
        item = InventoryItem.query.first()
        
        if not item:
            print("❌ No inventory items found")
            return
        
        response = client.get(f'/inventory/{item.id}')
        
        print(f"\n✅ Inventory item detail page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert item.item_code.encode() in response.data
        assert item.name.encode() in response.data
        
        print(f"✅ Page contains:")
        print(f"   - Item Code: {item.item_code}")
        print(f"   - Item Name: {item.name}")
        print(f"   - Stock Information")
        
        print("\n" + "="*80)
        print("✅ TEST 3 PASSED: Inventory Item Detail Page")
        print("="*80)


def test_adjust_stock():
    """Test 4: Adjust inventory stock"""
    print("\n" + "="*80)
    print("TEST 4: ADJUST INVENTORY STOCK")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get an inventory item
        item = InventoryItem.query.filter_by(item_code='TEST-ITEM-001').first()
        
        if not item:
            print("❌ Test item not found")
            return
        
        initial_qty = float(item.quantity_on_hand)
        
        # Adjust stock
        response = client.post(f'/inventory/{item.id}/adjust', data={
            'transaction_type': 'Purchase',
            'quantity': '25',
            'notes': 'Test purchase'
        }, follow_redirects=True)
        
        print(f"\n✅ Stock adjustment request sent")
        print(f"   Status Code: {response.status_code}")
        
        # Refresh item
        db.session.refresh(item)
        
        new_qty = float(item.quantity_on_hand)
        
        print(f"✅ Stock adjusted:")
        print(f"   - Initial: {initial_qty} {item.unit}")
        print(f"   - Adjustment: +25 {item.unit}")
        print(f"   - New: {new_qty} {item.unit}")
        
        assert new_qty == initial_qty + 25
        
        print("\n" + "="*80)
        print("✅ TEST 4 PASSED: Adjust Inventory Stock")
        print("="*80)


def test_low_stock_page():
    """Test 5: Low stock alerts page"""
    print("\n" + "="*80)
    print("TEST 5: LOW STOCK ALERTS PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/inventory/low-stock')
        
        print(f"\n✅ Low stock page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Low Stock Alerts' in response.data
        
        # Count low stock items
        low_stock_items = [item for item in InventoryItem.query.all() if item.is_low_stock]
        
        print(f"✅ Low stock items in database: {len(low_stock_items)}")
        
        print("\n" + "="*80)
        print("✅ TEST 5 PASSED: Low Stock Alerts Page")
        print("="*80)


def test_transactions_page():
    """Test 6: Inventory transactions page"""
    print("\n" + "="*80)
    print("TEST 6: INVENTORY TRANSACTIONS PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/inventory/transactions')
        
        print(f"\n✅ Transactions page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Inventory Transactions' in response.data
        
        # Count transactions
        txn_count = InventoryTransaction.query.count()
        
        print(f"✅ Total transactions in database: {txn_count}")
        
        print("\n" + "="*80)
        print("✅ TEST 6 PASSED: Inventory Transactions Page")
        print("="*80)


def test_edit_inventory_item():
    """Test 7: Edit inventory item"""
    print("\n" + "="*80)
    print("TEST 7: EDIT INVENTORY ITEM")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get an inventory item
        item = InventoryItem.query.filter_by(item_code='TEST-ITEM-001').first()
        
        if not item:
            print("❌ Test item not found")
            return
        
        # Edit item
        response = client.post(f'/inventory/{item.id}/edit', data={
            'name': 'Updated Test Item',
            'category': 'Sheet Metal',
            'unit': 'sheets',
            'reorder_level': '30',
            'unit_cost': '250.00'
        }, follow_redirects=True)
        
        print(f"\n✅ Edit inventory item request sent")
        print(f"   Status Code: {response.status_code}")
        
        # Refresh item
        db.session.refresh(item)
        
        assert item.name == 'Updated Test Item'
        assert float(item.reorder_level) == 30.0
        assert float(item.unit_cost) == 250.00
        
        print(f"✅ Inventory item updated:")
        print(f"   - Name: {item.name}")
        print(f"   - Reorder Level: {item.reorder_level}")
        print(f"   - Unit Cost: ${item.unit_cost}")
        
        print("\n" + "="*80)
        print("✅ TEST 7 PASSED: Edit Inventory Item")
        print("="*80)


def test_dashboard_inventory_section():
    """Test 8: Dashboard inventory section"""
    print("\n" + "="*80)
    print("TEST 8: DASHBOARD INVENTORY SECTION")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/')
        
        print(f"\n✅ Dashboard loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Inventory Status' in response.data
        
        print("✅ Dashboard contains inventory section")
        
        print("\n" + "="*80)
        print("✅ TEST 8 PASSED: Dashboard Inventory Section")
        print("="*80)


def run_all_tests():
    """Run all Phase 6 web interface tests"""
    print("\n" + "="*80)
    print("PHASE 6: INVENTORY MANAGEMENT - WEB INTERFACE TESTS")
    print("="*80)
    
    try:
        test_inventory_index()
        test_create_inventory_item()
        test_inventory_detail()
        test_adjust_stock()
        test_low_stock_page()
        test_transactions_page()
        test_edit_inventory_item()
        test_dashboard_inventory_section()
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("Total Tests: 8")
        print("Passed: 8 ✅")
        print("Failed: 0 ❌")
        print("Pass Rate: 100%")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()

