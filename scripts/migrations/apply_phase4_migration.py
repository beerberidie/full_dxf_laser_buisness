"""
Apply Phase 4 Migration - DXF File Management
Creates design_files table
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path('data/laser_os.db')

def apply_migration():
    """Apply Phase 4 migration"""
    print("="*80)
    print("APPLYING PHASE 4 MIGRATION: DXF FILE MANAGEMENT")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read migration SQL
        with open('migrations/schema_v4_design_files.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("\n📝 Executing migration SQL...")
        cursor.executescript(migration_sql)
        
        # Reconnect to get fresh cursor after executescript
        cursor = conn.cursor()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='design_files'")
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables created: {[t[0] for t in tables]}")
        
        # Verify schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        version = result[0] if result else 'Unknown'
        print(f"✅ Schema version updated to: {version}")
        
        # Show design_files table structure
        cursor.execute("PRAGMA table_info(design_files)")
        columns = cursor.fetchall()
        print(f"\n📊 Design_Files table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='design_files'")
        indexes = cursor.fetchall()
        print(f"\n🔍 Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[0]}")
        
        # Show file management settings
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%file%'")
        settings = cursor.fetchall()
        print(f"\n⚙️  File management settings:")
        for setting in settings:
            print(f"   - {setting[0]}: {setting[1]}")
        
        conn.commit()
        print("\n" + "="*80)
        print("✅ PHASE 4 MIGRATION COMPLETED SUCCESSFULLY!")
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

