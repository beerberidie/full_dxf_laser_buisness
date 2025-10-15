"""
Apply Phase 2 Migration - Projects Table
"""

import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / 'data' / 'laser_os.db'

# Migration file
migration_file = Path(__file__).parent / 'migrations' / 'schema_v2_projects.sql'

print("="*80)
print("PHASE 2 MIGRATION: Adding Projects Table")
print("="*80)

try:
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Read migration SQL
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    # Execute migration
    cursor.executescript(migration_sql)
    conn.commit()
    
    print("\n✅ Migration applied successfully!")
    
    # Verify table was created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if cursor.fetchone():
        print("✅ Projects table created")
    
    # Check schema version
    cursor.execute("SELECT value FROM settings WHERE key='schema_version'")
    version = cursor.fetchone()
    if version:
        print(f"✅ Schema version updated to: {version[0]}")
    
    # Show table structure
    cursor.execute("PRAGMA table_info(projects)")
    columns = cursor.fetchall()
    print(f"\n✅ Projects table has {len(columns)} columns:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n" + "="*80)
    print("✅ MIGRATION COMPLETE!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()

