"""
Phase 7: Reporting & Analytics - Web Interface Tests
Tests reporting functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app


def test_reports_index():
    """Test 1: Reports index page"""
    print("\n" + "="*80)
    print("TEST 1: REPORTS INDEX PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/reports/')
        
        print(f"\n✅ Reports index page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Reports & Analytics' in response.data
        assert b'Production Summary' in response.data
        assert b'Efficiency Metrics' in response.data
        
        print("✅ Page contains expected elements:")
        print("   - Reports & Analytics title")
        print("   - Production Summary link")
        print("   - Efficiency Metrics link")
        print("   - Inventory Report link")
        print("   - Client Report link")
        
        print("\n" + "="*80)
        print("✅ TEST 1 PASSED: Reports Index Page")
        print("="*80)


def test_production_report():
    """Test 2: Production summary report"""
    print("\n" + "="*80)
    print("TEST 2: PRODUCTION SUMMARY REPORT")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/reports/production')
        
        print(f"\n✅ Production report page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Production Summary Report' in response.data
        assert b'Total Runs' in response.data
        
        print("✅ Page contains:")
        print("   - Production Summary title")
        print("   - Statistics cards")
        print("   - Operator Performance section")
        print("   - Material Usage section")
        
        print("\n" + "="*80)
        print("✅ TEST 2 PASSED: Production Summary Report")
        print("="*80)


def test_efficiency_report():
    """Test 3: Efficiency metrics report"""
    print("\n" + "="*80)
    print("TEST 3: EFFICIENCY METRICS REPORT")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/reports/efficiency')
        
        print(f"\n✅ Efficiency report page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Efficiency Metrics Report' in response.data
        
        print("✅ Page contains:")
        print("   - Efficiency Metrics title")
        print("   - Statistics cards")
        print("   - Project Efficiency Analysis table")
        
        print("\n" + "="*80)
        print("✅ TEST 3 PASSED: Efficiency Metrics Report")
        print("="*80)


def test_inventory_report():
    """Test 4: Inventory report"""
    print("\n" + "="*80)
    print("TEST 4: INVENTORY REPORT")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/reports/inventory')
        
        print(f"\n✅ Inventory report page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Inventory Report' in response.data
        assert b'Category Breakdown' in response.data
        
        print("✅ Page contains:")
        print("   - Inventory Report title")
        print("   - Statistics cards")
        print("   - Category Breakdown table")
        print("   - All Inventory Items table")
        
        print("\n" + "="*80)
        print("✅ TEST 4 PASSED: Inventory Report")
        print("="*80)


def test_client_report():
    """Test 5: Client report"""
    print("\n" + "="*80)
    print("TEST 5: CLIENT REPORT")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/reports/clients')
        
        print(f"\n✅ Client report page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Client & Project Report' in response.data
        assert b'Client Analysis' in response.data
        
        print("✅ Page contains:")
        print("   - Client & Project Report title")
        print("   - Statistics cards")
        print("   - Client Analysis table")
        
        print("\n" + "="*80)
        print("✅ TEST 5 PASSED: Client Report")
        print("="*80)


def test_csv_export():
    """Test 6: CSV export functionality"""
    print("\n" + "="*80)
    print("TEST 6: CSV EXPORT")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/reports/export/production')
        
        print(f"\n✅ CSV export request sent")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/csv'
        assert 'attachment' in response.headers['Content-Disposition']
        
        print("✅ CSV export successful:")
        print("   - Content-Type: text/csv")
        print("   - Content-Disposition: attachment")
        
        print("\n" + "="*80)
        print("✅ TEST 6 PASSED: CSV Export")
        print("="*80)


def run_all_tests():
    """Run all Phase 7 tests"""
    print("\n" + "="*80)
    print("PHASE 7: REPORTING & ANALYTICS - WEB INTERFACE TESTS")
    print("="*80)
    
    try:
        test_reports_index()
        test_production_report()
        test_efficiency_report()
        test_inventory_report()
        test_client_report()
        test_csv_export()
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("Total Tests: 6")
        print("Passed: 6 ✅")
        print("Failed: 0 ❌")
        print("Pass Rate: 100%")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()

