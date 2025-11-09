"""
View imported products from the database.
Run this with: python view_imported_products.py
"""

import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.models import Product, ProductFile

def main():
    """Display imported products."""
    app = create_app('development')
    
    with app.app_context():
        # Get all products
        products = Product.query.order_by(Product.created_at.desc()).all()
        
        print(f"\n{'='*80}")
        print(f"IMPORTED PRODUCTS ({len(products)} total)")
        print(f"{'='*80}\n")
        
        # Group by material
        materials = {}
        for product in products:
            material = product.material or 'Unknown'
            if material not in materials:
                materials[material] = []
            materials[material].append(product)
        
        # Display by material
        for material, prods in sorted(materials.items()):
            print(f"\n{material} ({len(prods)} products)")
            print("-" * 80)
            
            for product in prods:
                # Get file count
                file_count = len(product.product_files)
                
                # Format thickness
                thickness_str = f"{product.thickness}mm" if product.thickness else "N/A"
                
                # Format price
                price_str = f"R{product.unit_price:.2f}" if product.unit_price else "Not set"
                
                print(f"  {product.sku_code:20} | {product.name:40} | {thickness_str:8} | {price_str:12} | {file_count} file(s)")
        
        print(f"\n{'='*80}")
        
        # Show some statistics
        print("\nSTATISTICS:")
        print("-" * 80)
        
        # Products with files
        products_with_files = sum(1 for p in products if len(p.product_files) > 0)
        print(f"Products with DXF files:  {products_with_files}/{len(products)}")
        
        # Products with pricing
        products_with_price = sum(1 for p in products if p.unit_price is not None)
        print(f"Products with pricing:    {products_with_price}/{len(products)}")
        
        # Thickness distribution
        thickness_counts = {}
        for product in products:
            thickness = f"{product.thickness}mm" if product.thickness else "N/A"
            thickness_counts[thickness] = thickness_counts.get(thickness, 0) + 1
        
        print(f"\nThickness distribution:")
        for thickness, count in sorted(thickness_counts.items()):
            print(f"  {thickness:8} : {count:2} products")
        
        print(f"\n{'='*80}\n")
        
        # Show a few sample products with details
        print("SAMPLE PRODUCTS (first 5):")
        print("-" * 80)
        
        for product in products[:5]:
            print(f"\nSKU: {product.sku_code}")
            print(f"Name: {product.name}")
            print(f"Material: {product.material or 'N/A'}")
            print(f"Thickness: {product.thickness}mm" if product.thickness else "Thickness: N/A")
            print(f"Description: {product.description[:100]}..." if product.description and len(product.description) > 100 else f"Description: {product.description or 'N/A'}")
            
            if product.product_files:
                print(f"Files:")
                for pf in product.product_files:
                    size_mb = pf.file_size / (1024 * 1024)
                    print(f"  - {pf.original_filename} ({size_mb:.2f} MB)")
            
            print("-" * 80)

if __name__ == '__main__':
    main()

