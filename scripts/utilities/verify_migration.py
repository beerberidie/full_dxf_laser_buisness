#!/usr/bin/env python3
"""
Verify Phase 9 migration is complete.
"""

import sqlite3
import os

DB_PATH = 'data/laser_os.db'

def verify_migration():
    """Verify migration is complete."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("Phase 9 Migration Verification")
    print("=" * 70)
    
    all_good = True
    
    # Check schema version table structure
    print("\n📋 Checking schema_version table...")
    cursor.execute("PRAGMA table_info(schema_version)")
    schema_cols = [col[1] for col in cursor.fetchall()]
    print(f"   Columns: {', '.join(schema_cols)}")
    
    # Get current version
    try:
        cursor.execute("SELECT * FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            print(f"   Latest entry: {result}")
    except Exception as e:
        print(f"   Error reading version: {e}")
    
    # Verify all Phase 9 columns exist
    print("\n📋 Verifying projects table columns...")
    cursor.execute("PRAGMA table_info(projects)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    required_columns = {
        'material_type': 'VARCHAR(100)',
        'material_quantity_sheets': 'INTEGER',
        'parts_quantity': 'INTEGER',
        'estimated_cut_time': 'INTEGER',
        'drawing_creation_time': 'INTEGER',
        'number_of_bins': 'INTEGER',
        'pop_received': 'BOOLEAN',
        'pop_received_date': 'DATE',
        'pop_deadline': 'DATE',
        'client_notified': 'BOOLEAN',
        'client_notified_date': 'DATE',
        'delivery_confirmed': 'BOOLEAN',
        'delivery_confirmed_date': 'DATE',
        'scheduled_cut_date': 'DATE'
    }
    
    for col, expected_type in required_columns.items():
        if col in columns:
            print(f"   ✓ {col} ({columns[col]})")
        else:
            print(f"   ✗ MISSING: {col}")
            all_good = False
    
    # Verify new tables exist
    print("\n📋 Verifying new tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['project_documents', 'communications', 'communication_attachments']
    for table in required_tables:
        if table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            col_count = len(cursor.fetchall())
            print(f"   ✓ {table} ({col_count} columns)")
        else:
            print(f"   ✗ MISSING: {table}")
            all_good = False
    
    # Verify indexes
    print("\n📋 Verifying indexes...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_projects_%'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    expected_indexes = [
        'idx_projects_material_type',
        'idx_projects_pop_received',
        'idx_projects_scheduled_cut_date',
        'idx_projects_pop_deadline'
    ]
    
    for idx in expected_indexes:
        if idx in indexes:
            print(f"   ✓ {idx}")
        else:
            print(f"   ⚠ Missing index: {idx} (optional)")
    
    conn.close()
    
    print("\n" + "=" * 70)
    if all_good:
        print("✅ Phase 9 migration is COMPLETE and verified!")
        print("\nAll required columns and tables are in place.")
        print("Ready to proceed with Phase 3 (Routes implementation).")
    else:
        print("⚠️  Some components are missing. Review above.")
    
    print("=" * 70)
    return all_good

if __name__ == '__main__':
    verify_migration()

