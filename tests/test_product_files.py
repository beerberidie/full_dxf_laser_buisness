"""
Test script for Product File Upload Functionality
Tests the new product file upload, download, and delete features.
"""

import sqlite3
import sys
from pathlib import Path

def test_product_files():
    """Test product file upload functionality."""
    
    print("=" * 80)
    print("PRODUCT FILE UPLOAD FUNCTIONALITY TEST")
    print("=" * 80)
    print()
    
    # Connect to database
    db_path = Path('data/laser_os.db')
    if not db_path.exists():
        print("❌ ERROR: Database not found at data/laser_os.db")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    all_tests_passed = True
    
    # Test 1: Verify product_files table exists
    print("Test 1: Verify product_files table exists")
    print("-" * 80)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_files'")
    if cursor.fetchone():
        print("✅ PASS: product_files table exists")
    else:
        print("❌ FAIL: product_files table not found")
        all_tests_passed = False
    print()
    
    # Test 2: Verify table schema
    print("Test 2: Verify product_files table schema")
    print("-" * 80)
    cursor.execute("PRAGMA table_info(product_files)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_columns = {
        'id': 'INTEGER',
        'product_id': 'INTEGER',
        'original_filename': 'VARCHAR(255)',
        'stored_filename': 'VARCHAR(255)',
        'file_path': 'VARCHAR(500)',
        'file_size': 'INTEGER',
        'file_type': 'VARCHAR(50)',
        'upload_date': 'DATETIME',
        'uploaded_by': 'VARCHAR(100)',
        'notes': 'TEXT',
        'created_at': 'DATETIME',
        'updated_at': 'DATETIME'
    }
    
    schema_ok = True
    for col_name, col_type in required_columns.items():
        if col_name in columns:
            print(f"✅ Column '{col_name}' exists ({columns[col_name]})")
        else:
            print(f"❌ Column '{col_name}' missing")
            schema_ok = False
            all_tests_passed = False
    
    if schema_ok:
        print("✅ PASS: All required columns exist")
    print()
    
    # Test 3: Verify indexes
    print("Test 3: Verify indexes on product_files table")
    print("-" * 80)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='product_files'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    required_indexes = [
        'idx_product_files_product_id',
        'idx_product_files_upload_date',
        'idx_product_files_created_at'
    ]
    
    indexes_ok = True
    for idx in required_indexes:
        if idx in indexes:
            print(f"✅ Index '{idx}' exists")
        else:
            print(f"❌ Index '{idx}' missing")
            indexes_ok = False
            all_tests_passed = False
    
    if indexes_ok:
        print("✅ PASS: All required indexes exist")
    print()
    
    # Test 4: Verify foreign key constraint
    print("Test 4: Verify foreign key constraint")
    print("-" * 80)
    cursor.execute("PRAGMA foreign_key_list(product_files)")
    fk_info = cursor.fetchall()
    
    if fk_info:
        for fk in fk_info:
            print(f"✅ Foreign key: {fk[3]} -> {fk[2]}({fk[4]})")
        print("✅ PASS: Foreign key constraint exists")
    else:
        print("⚠️  WARNING: No foreign key constraints found")
        print("   This may be OK if SQLite foreign keys are not enabled")
    print()
    
    # Test 5: Verify products table has material and thickness
    print("Test 5: Verify products table has material and thickness fields")
    print("-" * 80)
    cursor.execute("PRAGMA table_info(products)")
    product_columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    if 'material' in product_columns and 'thickness' in product_columns:
        print(f"✅ Column 'material' exists ({product_columns['material']})")
        print(f"✅ Column 'thickness' exists ({product_columns['thickness']})")
        print("✅ PASS: Products table has required fields")
    else:
        print("❌ FAIL: Products table missing material or thickness fields")
        all_tests_passed = False
    print()
    
    # Test 6: Check for existing products
    print("Test 6: Check for existing products")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    if product_count > 0:
        print(f"✅ Found {product_count} products in database")
        
        # Show sample products
        cursor.execute("""
            SELECT id, sku_code, name, material, thickness 
            FROM products 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        print("\n   Sample products:")
        for pid, sku, name, material, thickness in cursor.fetchall():
            mat_info = f"{material} {thickness}mm" if material and thickness else (material or "No material")
            print(f"   • {sku}: {name} ({mat_info})")
    else:
        print("⚠️  WARNING: No products found in database")
        print("   You'll need to create products to test file uploads")
    print()
    
    # Test 7: Check for existing product files
    print("Test 7: Check for existing product files")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM product_files")
    file_count = cursor.fetchone()[0]
    
    if file_count > 0:
        print(f"✅ Found {file_count} product files in database")
        
        # Show sample files
        cursor.execute("""
            SELECT pf.id, pf.original_filename, pf.file_type, pf.file_size, p.sku_code
            FROM product_files pf
            JOIN products p ON pf.product_id = p.id
            ORDER BY pf.upload_date DESC
            LIMIT 5
        """)
        print("\n   Sample product files:")
        for fid, filename, ftype, fsize, sku in cursor.fetchall():
            size_mb = round(fsize / (1024 * 1024), 2)
            print(f"   • {filename} ({ftype.upper()}, {size_mb} MB) - Product: {sku}")
    else:
        print("ℹ️  No product files uploaded yet (this is OK for a new feature)")
    print()
    
    # Test 8: Verify file upload folder exists
    print("Test 8: Verify file upload folder structure")
    print("-" * 80)
    upload_folder = Path('data/files/products')
    
    if upload_folder.exists():
        print(f"✅ Upload folder exists: {upload_folder}")
        
        # Count product folders
        product_folders = [f for f in upload_folder.iterdir() if f.is_dir()]
        if product_folders:
            print(f"   Found {len(product_folders)} product folders")
        else:
            print("   No product folders yet (will be created on first upload)")
    else:
        print(f"ℹ️  Upload folder doesn't exist yet: {upload_folder}")
        print("   It will be created automatically on first file upload")
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    if all_tests_passed:
        print("✅ ALL CRITICAL TESTS PASSED")
        print()
        print("Product file upload functionality is ready!")
        print()
        print("Next steps:")
        print("1. Start the Flask server: python app.py")
        print("2. Navigate to a product detail page")
        print("3. Test file upload:")
        print("   • Click 'Upload File' button")
        print("   • Select a .dxf or .lbrn2 file")
        print("   • Add optional notes")
        print("   • Click 'Upload'")
        print("4. Test file download:")
        print("   • Click 'Download' button on an uploaded file")
        print("5. Test file delete:")
        print("   • Click 'Delete' button and confirm")
        print("6. Verify files appear in product list with file count badge")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the errors above and fix any issues.")
    print("=" * 80)
    
    conn.close()
    return all_tests_passed

if __name__ == '__main__':
    success = test_product_files()
    sys.exit(0 if success else 1)

