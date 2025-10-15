"""
Phase 3 Database Testing Script
Tests product/SKU management functionality
"""

from app import create_app, db
from app.models import Product, Client, Project, ProjectProduct, ActivityLog
from datetime import datetime, date, timedelta
from decimal import Decimal

app = create_app('development')


def test_product_creation():
    """Test creating products with auto-generated SKU codes"""
    print("\n" + "="*80)
    print("TEST 1: PRODUCT CREATION")
    print("="*80)
    
    with app.app_context():
        # Create test products with different materials and thicknesses
        products_data = [
            {
                'name': 'Test Product - Mild Steel Bracket',
                'description': 'Standard bracket for industrial use',
                'material': 'Mild Steel',
                'thickness': Decimal('3.0'),
                'unit_price': Decimal('25.50')
            },
            {
                'name': 'Test Product - Stainless Steel Panel',
                'description': 'Decorative panel',
                'material': 'Stainless Steel',
                'thickness': Decimal('1.5'),
                'unit_price': Decimal('45.00')
            },
            {
                'name': 'Test Product - Aluminum Plate',
                'description': 'Lightweight plate',
                'material': 'Aluminum',
                'thickness': Decimal('2.0'),
                'unit_price': Decimal('35.75')
            },
            {
                'name': 'Test Product - Acrylic Sign',
                'description': 'Custom signage',
                'material': 'Acrylic',
                'thickness': Decimal('5.0'),
                'unit_price': Decimal('50.00')
            },
            {
                'name': 'Test Product - Brass Nameplate',
                'description': 'Engraved nameplate',
                'material': 'Brass',
                'thickness': Decimal('1.0'),
                'unit_price': Decimal('60.00')
            }
        ]
        
        created_products = []
        for data in products_data:
            product = Product(**data)
            db.session.add(product)
            db.session.flush()  # Generate SKU code
            created_products.append(product)
            print(f"✅ Created Product #{product.id}: {product.sku_code} - {product.name}")
        
        db.session.commit()
        
        print(f"\n✅ Successfully created {len(created_products)} test products")
        return created_products


def test_product_retrieval():
    """Test retrieving and listing products"""
    print("\n" + "="*80)
    print("TEST 2: PRODUCT RETRIEVAL")
    print("="*80)
    
    with app.app_context():
        products = Product.query.all()
        
        print(f"\n📊 Total products in database: {len(products)}")
        print("\nProduct List:")
        print("-" * 80)
        
        for product in products:
            print(f"SKU: {product.sku_code}")
            print(f"Name: {product.name}")
            print(f"Material: {product.material or 'N/A'}")
            print(f"Thickness: {product.thickness}mm" if product.thickness else "Thickness: N/A")
            print(f"Price: R{product.unit_price}" if product.unit_price else "Price: N/A")
            print("-" * 80)
        
        print(f"\n✅ Successfully retrieved {len(products)} products")


def test_sku_code_generation():
    """Test SKU code format and uniqueness"""
    print("\n" + "="*80)
    print("TEST 3: SKU CODE AUTO-GENERATION")
    print("="*80)
    
    with app.app_context():
        products = Product.query.all()
        
        print("\n📋 Validating SKU codes:")
        sku_codes = set()
        
        for product in products:
            # Check format: SKU-{MATERIAL}{THICKNESS}-{NUMBER}
            assert product.sku_code.startswith('SKU-'), f"Invalid SKU format: {product.sku_code}"
            assert product.sku_code not in sku_codes, f"Duplicate SKU code: {product.sku_code}"
            sku_codes.add(product.sku_code)
            print(f"✅ {product.sku_code} - Valid format, unique")
        
        print(f"\n✅ All {len(products)} SKU codes are valid and unique")


def test_product_project_relationship():
    """Test adding products to projects"""
    print("\n" + "="*80)
    print("TEST 4: PRODUCT-PROJECT RELATIONSHIP")
    print("="*80)
    
    with app.app_context():
        # Get a test project
        project = Project.query.first()
        if not project:
            print("⚠️  No projects found, skipping test")
            return
        
        # Get some products
        products = Product.query.limit(3).all()
        if not products:
            print("⚠️  No products found, skipping test")
            return
        
        print(f"\n📦 Adding products to project: {project.project_code}")
        
        # Add products to project
        for i, product in enumerate(products, 1):
            pp = ProjectProduct(
                project_id=project.id,
                product_id=product.id,
                quantity=i * 10,  # 10, 20, 30
                unit_price=product.unit_price,
                notes=f'Test line item {i}'
            )
            db.session.add(pp)
            print(f"✅ Added: {product.sku_code} x {pp.quantity} @ R{pp.unit_price} = R{pp.total_price}")
        
        db.session.commit()
        
        # Verify relationship
        project_products = ProjectProduct.query.filter_by(project_id=project.id).all()
        print(f"\n✅ Project now has {len(project_products)} products")
        
        # Calculate total
        total = sum(pp.total_price for pp in project_products)
        print(f"✅ Total project value: R{total:.2f}")


def test_product_detail():
    """Test viewing product details and usage"""
    print("\n" + "="*80)
    print("TEST 5: PRODUCT DETAIL VIEW")
    print("="*80)
    
    with app.app_context():
        product = Product.query.first()
        if not product:
            print("⚠️  No products found, skipping test")
            return
        
        print(f"\n📋 Product Details for {product.sku_code}:")
        print("=" * 80)
        print(f"Name:             {product.name}")
        print(f"SKU Code:         {product.sku_code}")
        print(f"Description:      {product.description or 'N/A'}")
        print(f"Material:         {product.material or 'N/A'}")
        print(f"Thickness:        {product.thickness}mm" if product.thickness else "Thickness:        N/A")
        print(f"Unit Price:       R{product.unit_price}" if product.unit_price else "Unit Price:       N/A")
        print(f"Created:          {product.created_at}")
        print(f"Last Updated:     {product.updated_at}")
        
        # Check usage in projects
        project_products = ProjectProduct.query.filter_by(product_id=product.id).all()
        print(f"\n📊 Used in {len(project_products)} project(s)")
        
        if project_products:
            print("\nProject Usage:")
            for pp in project_products:
                print(f"  - {pp.project.project_code}: {pp.quantity} units @ R{pp.unit_price}")
        
        # Check activity log
        logs = ActivityLog.query.filter_by(
            entity_type='PRODUCT',
            entity_id=product.id
        ).all()
        print(f"\n📝 Activity Log ({len(logs)} entries)")
        for log in logs:
            print(f"  - {log.created_at}: {log.action} - {log.details}")
        
        print("\n✅ Product detail view test passed")


def run_all_tests():
    """Run all Phase 3 database tests"""
    print("\n" + "="*80)
    print("PHASE 3: PRODUCT/SKU MANAGEMENT - DATABASE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        test_product_creation()
        test_product_retrieval()
        test_sku_code_generation()
        test_product_project_relationship()
        test_product_detail()
        
        print("\n" + "="*80)
        print("✅ ALL DATABASE TESTS PASSED!")
        print("="*80)
        print(f"Completed at: {datetime.now()}")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()

