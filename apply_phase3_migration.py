"""
Apply Phase 3 Migration - SKU/Product Management
Creates products and project_products tables
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path('data/laser_os.db')

def apply_migration():
    """Apply Phase 3 migration"""
    print("="*80)
    print("APPLYING PHASE 3 MIGRATION: SKU/PRODUCT MANAGEMENT")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read migration SQL
        with open('migrations/schema_v3_products.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("\n📝 Executing migration SQL...")
        cursor.executescript(migration_sql)

        # Reconnect to get fresh cursor after executescript
        cursor = conn.cursor()

        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('products', 'project_products')")
        tables = cursor.fetchall()

        print(f"\n✅ Tables created: {[t[0] for t in tables]}")

        # Verify schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        version = result[0] if result else 'Unknown'
        print(f"✅ Schema version updated to: {version}")
        
        # Show products table structure
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        print(f"\n📊 Products table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show project_products table structure
        cursor.execute("PRAGMA table_info(project_products)")
        columns = cursor.fetchall()
        print(f"\n📊 Project_Products table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND (tbl_name='products' OR tbl_name='project_products')")
        indexes = cursor.fetchall()
        print(f"\n🔍 Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[0]}")
        
        conn.commit()
        print("\n" + "="*80)
        print("✅ PHASE 3 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*80)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()


if __name__ == '__main__':
    apply_migration()

