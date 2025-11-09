"""
Apply Product Files Migration
Creates the product_files table for storing DXF and LightBurn files for products.
"""

import sqlite3
import sys
from pathlib import Path

def apply_migration():
    """Apply the product files migration."""
    
    print("=" * 80)
    print("PRODUCT FILES MIGRATION")
    print("=" * 80)
    print()
    
    # Connect to database
    db_path = Path('data/laser_os.db')
    if not db_path.exists():
        print("❌ ERROR: Database not found at data/laser_os.db")
        print("   Please ensure the database exists before running this migration.")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_files'")
        if cursor.fetchone():
            print("⚠️  WARNING: product_files table already exists")
            response = input("   Do you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("   Migration cancelled")
                return False
            print()
        
        # Read and execute migration SQL
        migration_file = Path('migrations/schema_product_files.sql')
        if not migration_file.exists():
            print("❌ ERROR: Migration file not found at migrations/schema_product_files.sql")
            return False
        
        print("📄 Reading migration file...")
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("🔧 Applying migration...")
        cursor.executescript(migration_sql)
        conn.commit()
        
        print("✅ Migration applied successfully!")
        print()
        
        # Verify table creation
        print("🔍 Verifying table structure...")
        cursor.execute("PRAGMA table_info(product_files)")
        columns = cursor.fetchall()
        
        print(f"   Table 'product_files' has {len(columns)} columns:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        print()
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='product_files'")
        indexes = cursor.fetchall()
        print(f"   Created {len(indexes)} indexes:")
        for idx in indexes:
            print(f"   • {idx[0]}")
        print()
        
        print("=" * 80)
        print("✅ MIGRATION COMPLETE")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. The ProductFile model has been added to app/models.py")
        print("2. Update product routes to handle file uploads")
        print("3. Update product templates to show file upload UI")
        print("4. Test file upload/download functionality")
        print()
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: Migration failed: {str(e)}")
        print()
        print("To rollback, run:")
        print("  python -c \"import sqlite3; conn = sqlite3.connect('data/laser_os.db'); conn.executescript(open('migrations/rollback_product_files.sql').read()); conn.commit()\"")
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)

