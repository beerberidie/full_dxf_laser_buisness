"""
Phase 3 Web Interface Testing Script
Tests all product management web interface functionality
"""

from app import create_app, db
from app.models import Product, ActivityLog
from datetime import datetime, date, timedelta
from decimal import Decimal

app = create_app('development')


def test_product_list_page():
    """Test product list page loads and displays products"""
    print("\n" + "="*80)
    print("TEST 1: PRODUCT LIST PAGE")
    print("="*80)
    
    with app.test_client() as client:
        response = client.get('/products', follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check page title
        assert '<h1>Products</h1>' in html, "Page title not found"
        print("✅ Page title correct")
        
        # Check for New Product button
        assert '+ New Product' in html, "New Product button not found"
        print("✅ New Product button present")
        
        # Check for search bar
        assert 'Search products by name, SKU, or description' in html, "Search bar not found"
        print("✅ Search bar present")
        
        # Check for filter dropdown
        assert 'All Materials' in html, "Material filter not found"
        print("✅ Material filter present")
        
        # Check for product table
        assert '<table class="table">' in html, "Product table not found"
        print("✅ Product table present")
        
        # Check for SKU codes (from test data)
        assert 'SKU-MI30-0001' in html, "SKU code not found in list"
        assert 'SKU-ST15-0001' in html, "SKU code not found in list"
        print("✅ SKU codes displayed")
        
        print("\n✅ PRODUCT LIST PAGE TEST PASSED")


def test_product_search():
    """Test product search functionality"""
    print("\n" + "="*80)
    print("TEST 2: PRODUCT SEARCH FUNCTIONALITY")
    print("="*80)
    
    with app.test_client() as client:
        # Search by name
        response = client.get('/products?search=Bracket', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        assert 'Mild Steel Bracket' in html, "Search result not found"
        print("✅ Search by name works")
        
        # Search by SKU
        response = client.get('/products?search=SKU-MI30', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        assert 'SKU-MI30-0001' in html, "Search by SKU failed"
        print("✅ Search by SKU works")
        
        # Search with no results
        response = client.get('/products?search=NonexistentProduct', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        assert 'No products found' in html, "Empty search result message not shown"
        print("✅ Empty search handled correctly")
        
        print("\n✅ PRODUCT SEARCH TEST PASSED")


def test_product_filters():
    """Test product filter functionality"""
    print("\n" + "="*80)
    print("TEST 3: PRODUCT FILTER FUNCTIONALITY")
    print("="*80)
    
    with app.test_client() as client:
        # Filter by material
        response = client.get('/products?material=Mild Steel', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        assert 'Mild Steel' in html, "Material filter failed"
        print("✅ Material filter works")
        
        print("\n✅ PRODUCT FILTER TEST PASSED")


def test_new_product_form():
    """Test new product form displays correctly"""
    print("\n" + "="*80)
    print("TEST 4: NEW PRODUCT FORM")
    print("="*80)
    
    with app.test_client() as client:
        response = client.get('/products/new', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check form elements
        assert '<h1>New Product</h1>' in html, "Form title not found"
        print("✅ Form title correct")
        
        assert 'name="name"' in html, "Name field not found"
        assert 'name="description"' in html, "Description field not found"
        assert 'name="material"' in html, "Material field not found"
        assert 'name="thickness"' in html, "Thickness field not found"
        assert 'name="unit_price"' in html, "Unit price field not found"
        assert 'name="notes"' in html, "Notes field not found"
        print("✅ All form fields present")
        
        # Check for material options
        assert 'Select material' in html, "Material dropdown placeholder not found"
        print("✅ Material dropdown populated")
        
        # Check for thickness options
        assert 'Select thickness' in html, "Thickness dropdown placeholder not found"
        print("✅ Thickness dropdown populated")
        
        # Check for submit button
        assert 'Create Product' in html, "Submit button not found"
        print("✅ Submit button present")
        
        # Check for SKU auto-generation note
        assert 'SKU code will be auto-generated' in html, "SKU auto-generation note not found"
        print("✅ SKU auto-generation note present")
        
        print("\n✅ NEW PRODUCT FORM TEST PASSED")


def test_product_creation():
    """Test creating a new product"""
    print("\n" + "="*80)
    print("TEST 5: PRODUCT CREATION")
    print("="*80)
    
    with app.test_client() as client:
        # Create a new product
        response = client.post('/products/new', data={
            'name': 'Automated Test Product',
            'description': 'Created by automated test suite',
            'material': 'Copper',
            'thickness': '2.5',
            'unit_price': '75.00',
            'notes': 'Test notes'
        }, follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for success message
        assert 'created successfully' in html, "Success message not found"
        print("✅ Success message displayed")
        
        # Check that we're on the detail page
        assert 'Automated Test Product' in html, "Product name not found on detail page"
        print("✅ Redirected to detail page")
        
        # Verify SKU code was auto-generated (should be SKU-CO25-xxxx)
        assert 'SKU-CO25-' in html, "SKU code not auto-generated correctly"
        print("✅ SKU code auto-generated")
        
        # Verify all data was saved
        assert 'Created by automated test suite' in html, "Description not saved"
        assert 'Copper' in html, "Material not saved"
        assert '2.500mm' in html or '2.5mm' in html, "Thickness not saved"
        assert 'R75.00' in html, "Price not saved"
        assert 'Test notes' in html, "Notes not saved"
        print("✅ All product data saved correctly")
        
    # Verify in database
    with app.app_context():
        product = Product.query.filter_by(name='Automated Test Product').first()
        assert product is not None, "Product not found in database"
        assert product.sku_code.startswith('SKU-CO25-'), "SKU code format incorrect"
        assert product.material == 'Copper', "Material mismatch"
        print("✅ Product verified in database")
        
        # Check activity log
        log = ActivityLog.query.filter_by(
            entity_type='PRODUCT',
            entity_id=product.id,
            action='CREATED'
        ).first()
        assert log is not None, "Activity log not created"
        print("✅ Activity log created")
        
        print("\n✅ PRODUCT CREATION TEST PASSED")


def test_product_detail_page():
    """Test product detail page displays all information"""
    print("\n" + "="*80)
    print("TEST 6: PRODUCT DETAIL PAGE")
    print("="*80)
    
    with app.app_context():
        # Get a product for testing
        product = Product.query.first()
        product_id = product.id
        product_sku = product.sku_code
        product_name = product.name
    
    with app.test_client() as client:
        response = client.get(f'/products/{product_id}', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check breadcrumb
        assert 'Products' in html, "Breadcrumb not found"
        assert product_sku in html, "SKU code not in breadcrumb"
        print("✅ Breadcrumb present")
        
        # Check product information
        assert product_name in html, "Product name not found"
        assert product_sku in html, "SKU code not found"
        print("✅ Product information displayed")
        
        # Check for action buttons
        assert 'Edit Product' in html, "Edit button not found"
        assert 'Delete Product' in html, "Delete button not found"
        print("✅ Action buttons present")
        
        # Check for information cards
        assert 'Product Information' in html, "Product info card not found"
        assert 'Metadata' in html, "Metadata card not found"
        print("✅ Information cards present")
        
        # Check for projects using this product section
        assert 'Projects Using This Product' in html, "Projects section not found"
        print("✅ Projects section present")
        
        # Check for activity log
        assert 'Activity Log' in html, "Activity log not found"
        print("✅ Activity log present")
        
        print("\n✅ PRODUCT DETAIL PAGE TEST PASSED")


def test_edit_product_form():
    """Test edit product form pre-fills with current values"""
    print("\n" + "="*80)
    print("TEST 7: EDIT PRODUCT FORM")
    print("="*80)
    
    with app.app_context():
        # Get a product for testing
        product = Product.query.first()
        product_id = product.id
        product_name = product.name
    
    with app.test_client() as client:
        response = client.get(f'/products/{product_id}/edit', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check form title
        assert '<h1>Edit Product</h1>' in html, "Form title not found"
        print("✅ Form title correct")
        
        # Check that form is pre-filled
        assert product_name in html, "Product name not pre-filled"
        print("✅ Form pre-filled with current values")
        
        # Check that SKU field is read-only
        assert 'SKU code cannot be changed' in html or 'form-control-static' in html, "SKU field not read-only"
        print("✅ SKU field is read-only")
        
        # Check for update button
        assert 'Update Product' in html, "Update button not found"
        print("✅ Update button present")
        
        print("\n✅ EDIT PRODUCT FORM TEST PASSED")


def run_all_tests():
    """Run all Phase 3 web interface tests"""
    print("\n" + "="*80)
    print("PHASE 3: WEB INTERFACE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests in sequence
        test_product_list_page()
        test_product_search()
        test_product_filters()
        test_new_product_form()
        test_product_creation()
        test_product_detail_page()
        test_edit_product_form()
        
        print("\n" + "="*80)
        print("✅ ALL WEB INTERFACE TESTS PASSED!")
        print("="*80)
        print(f"Completed at: {datetime.now()}")
        print("\nTotal Tests: 7")
        print("Passed: 7")
        print("Failed: 0")
        print("Pass Rate: 100%")
        
        return True
        
    except AssertionError as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST ERROR!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)

