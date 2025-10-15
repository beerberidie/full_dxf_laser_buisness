#!/usr/bin/env python3
"""
Check current database schema to see what's already applied.
"""

import sqlite3
import os

DB_PATH = 'data/laser_os.db'

def check_schema():
    """Check current database schema."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("Current Database Schema Check")
    print("=" * 70)
    
    # Check schema version
    print("\n📋 Schema Version:")
    try:
        cursor.execute("SELECT version, description FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            print(f"   Version: {result[0]}")
            print(f"   Description: {result[1]}")
        else:
            print("   No schema version found")
    except sqlite3.OperationalError as e:
        print(f"   Error: {e}")
    
    # Check projects table columns
    print("\n📋 Projects Table Columns:")
    cursor.execute("PRAGMA table_info(projects)")
    columns = cursor.fetchall()
    phase9_columns = [
        'material_type', 'material_quantity_sheets', 'parts_quantity',
        'estimated_cut_time', 'drawing_creation_time', 'number_of_bins',
        'pop_received', 'pop_received_date', 'pop_deadline',
        'client_notified', 'client_notified_date',
        'delivery_confirmed', 'delivery_confirmed_date',
        'scheduled_cut_date'
    ]
    
    existing_columns = [col[1] for col in columns]
    for col in phase9_columns:
        status = "✓" if col in existing_columns else "✗"
        print(f"   {status} {col}")
    
    # Check for new tables
    print("\n📋 Phase 9 Tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    phase9_tables = ['project_documents', 'communications', 'communication_attachments']
    for table in phase9_tables:
        status = "✓" if table in tables else "✗"
        print(f"   {status} {table}")
    
    # Check all tables
    print("\n📋 All Tables in Database:")
    for table in sorted(tables):
        print(f"   - {table}")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == '__main__':
    check_schema()

