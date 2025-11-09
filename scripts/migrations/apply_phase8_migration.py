"""
Apply Phase 8 Migration - Quotes & Invoices
Creates quotes, quote_items, invoices, and invoice_items tables
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path('data/laser_os.db')

def apply_migration():
    """Apply Phase 8 migration"""
    print("="*80)
    print("APPLYING PHASE 8 MIGRATION: QUOTES & INVOICES")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read migration SQL
        with open('migrations/schema_v8_quotes_invoices.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("\n📝 Executing migration SQL...")
        cursor.executescript(migration_sql)
        
        # Reconnect to get fresh cursor after executescript
        cursor = conn.cursor()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('quotes', 'quote_items', 'invoices', 'invoice_items')")
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables created: {[t[0] for t in tables]}")
        
        # Verify schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        version = result[0] if result else 'Unknown'
        print(f"✅ Schema version updated to: {version}")
        
        # Show quotes table structure
        cursor.execute("PRAGMA table_info(quotes)")
        columns = cursor.fetchall()
        print(f"\n📊 Quotes table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show invoices table structure
        cursor.execute("PRAGMA table_info(invoices)")
        columns = cursor.fetchall()
        print(f"\n📊 Invoices table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND (tbl_name='quotes' OR tbl_name='quote_items' OR tbl_name='invoices' OR tbl_name='invoice_items')")
        indexes = cursor.fetchall()
        print(f"\n🔍 Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[0]}")
        
        conn.commit()
        print("\n" + "="*80)
        print("✅ PHASE 8 MIGRATION COMPLETED SUCCESSFULLY!")
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

