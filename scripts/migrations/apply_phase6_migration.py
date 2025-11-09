"""
Apply Phase 6 Migration - Inventory Management
Creates inventory_items and inventory_transactions tables
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path('data/laser_os.db')

def apply_migration():
    """Apply Phase 6 migration"""
    print("="*80)
    print("APPLYING PHASE 6 MIGRATION: INVENTORY MANAGEMENT")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read migration SQL
        with open('migrations/schema_v6_inventory.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("\n📝 Executing migration SQL...")
        cursor.executescript(migration_sql)
        
        # Reconnect to get fresh cursor after executescript
        cursor = conn.cursor()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('inventory_items', 'inventory_transactions')")
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables created: {[t[0] for t in tables]}")
        
        # Verify schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        version = result[0] if result else 'Unknown'
        print(f"✅ Schema version updated to: {version}")
        
        # Show inventory_items table structure
        cursor.execute("PRAGMA table_info(inventory_items)")
        columns = cursor.fetchall()
        print(f"\n📊 Inventory_Items table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show inventory_transactions table structure
        cursor.execute("PRAGMA table_info(inventory_transactions)")
        columns = cursor.fetchall()
        print(f"\n📊 Inventory_Transactions table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND (tbl_name='inventory_items' OR tbl_name='inventory_transactions')")
        indexes = cursor.fetchall()
        print(f"\n🔍 Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[0]}")
        
        # Show inventory management settings
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%inventory%'")
        settings = cursor.fetchall()
        print(f"\n⚙️  Inventory management settings:")
        for setting in settings:
            print(f"   - {setting[0]}: {setting[1]}")
        
        conn.commit()
        print("\n" + "="*80)
        print("✅ PHASE 6 MIGRATION COMPLETED SUCCESSFULLY!")
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

