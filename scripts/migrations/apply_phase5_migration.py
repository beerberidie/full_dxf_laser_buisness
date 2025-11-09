"""
Apply Phase 5 Migration - Schedule Queue & Laser Runs Management
Creates queue_items and laser_runs tables
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path('data/laser_os.db')

def apply_migration():
    """Apply Phase 5 migration"""
    print("="*80)
    print("APPLYING PHASE 5 MIGRATION: SCHEDULE QUEUE & LASER RUNS")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read migration SQL
        with open('migrations/schema_v5_queue.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("\n📝 Executing migration SQL...")
        cursor.executescript(migration_sql)
        
        # Reconnect to get fresh cursor after executescript
        cursor = conn.cursor()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('queue_items', 'laser_runs')")
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables created: {[t[0] for t in tables]}")
        
        # Verify schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        version = result[0] if result else 'Unknown'
        print(f"✅ Schema version updated to: {version}")
        
        # Show queue_items table structure
        cursor.execute("PRAGMA table_info(queue_items)")
        columns = cursor.fetchall()
        print(f"\n📊 Queue_Items table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show laser_runs table structure
        cursor.execute("PRAGMA table_info(laser_runs)")
        columns = cursor.fetchall()
        print(f"\n📊 Laser_Runs table structure ({len(columns)} columns):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Show indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND (tbl_name='queue_items' OR tbl_name='laser_runs')")
        indexes = cursor.fetchall()
        print(f"\n🔍 Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[0]}")
        
        # Show queue management settings
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%queue%' OR key LIKE '%priority%'")
        settings = cursor.fetchall()
        print(f"\n⚙️  Queue management settings:")
        for setting in settings:
            print(f"   - {setting[0]}: {setting[1]}")
        
        conn.commit()
        print("\n" + "="*80)
        print("✅ PHASE 5 MIGRATION COMPLETED SUCCESSFULLY!")
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

