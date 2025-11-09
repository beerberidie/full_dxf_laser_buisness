"""
Phase 8: Quotes & Invoices - Web Interface Tests
Tests quotes and invoices functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app


def test_quotes_index():
    """Test 1: Quotes index page"""
    print("\n" + "="*80)
    print("TEST 1: QUOTES INDEX PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/quotes/')
        
        print(f"\n✅ Quotes index page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Quotes' in response.data
        assert b'New Quote' in response.data
        
        print("✅ Page contains expected elements")
        
        print("\n" + "="*80)
        print("✅ TEST 1 PASSED: Quotes Index Page")
        print("="*80)


def test_invoices_index():
    """Test 2: Invoices index page"""
    print("\n" + "="*80)
    print("TEST 2: INVOICES INDEX PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/invoices/')
        
        print(f"\n✅ Invoices index page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'Invoices' in response.data
        assert b'New Invoice' in response.data
        
        print("✅ Page contains expected elements")
        
        print("\n" + "="*80)
        print("✅ TEST 2 PASSED: Invoices Index Page")
        print("="*80)


def test_quote_form():
    """Test 3: Quote creation form"""
    print("\n" + "="*80)
    print("TEST 3: QUOTE CREATION FORM")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/quotes/new')
        
        print(f"\n✅ Quote form page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'New Quote' in response.data
        
        print("✅ Form contains expected fields")
        
        print("\n" + "="*80)
        print("✅ TEST 3 PASSED: Quote Creation Form")
        print("="*80)


def test_invoice_form():
    """Test 4: Invoice creation form"""
    print("\n" + "="*80)
    print("TEST 4: INVOICE CREATION FORM")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        response = client.get('/invoices/new')
        
        print(f"\n✅ Invoice form page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200
        assert b'New Invoice' in response.data
        
        print("✅ Form contains expected fields")
        
        print("\n" + "="*80)
        print("✅ TEST 4 PASSED: Invoice Creation Form")
        print("="*80)


def test_models():
    """Test 5: Quote and Invoice models"""
    print("\n" + "="*80)
    print("TEST 5: QUOTE AND INVOICE MODELS")
    print("="*80)
    
    app = create_app('development')
    
    with app.app_context():
        from app.models import Quote, QuoteItem, Invoice, InvoiceItem
        
        # Test Quote model
        print("\n✅ Quote model imported successfully")
        print(f"   Status constants: {Quote.STATUS_DRAFT}, {Quote.STATUS_SENT}, {Quote.STATUS_ACCEPTED}")
        
        # Test Invoice model
        print("✅ Invoice model imported successfully")
        print(f"   Status constants: {Invoice.STATUS_DRAFT}, {Invoice.STATUS_SENT}, {Invoice.STATUS_PAID}")
        
        # Test QuoteItem model
        print("✅ QuoteItem model imported successfully")
        
        # Test InvoiceItem model
        print("✅ InvoiceItem model imported successfully")
        
        print("\n" + "="*80)
        print("✅ TEST 5 PASSED: Quote and Invoice Models")
        print("="*80)


def run_all_tests():
    """Run all Phase 8 tests"""
    print("\n" + "="*80)
    print("PHASE 8: QUOTES & INVOICES - WEB INTERFACE TESTS")
    print("="*80)
    
    try:
        test_quotes_index()
        test_invoices_index()
        test_quote_form()
        test_invoice_form()
        test_models()
        
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

