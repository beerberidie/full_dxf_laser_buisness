#!/usr/bin/env python3
"""
Fix Sage metadata column name.

This script renames the 'metadata' column to 'business_metadata' in the sage_businesses table
to avoid conflict with SQLAlchemy's reserved 'metadata' attribute.
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def fix_metadata_column():
    """Rename metadata column to business_metadata."""
    db_path = 'data/laser_os.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sage_businesses'")
        if not cursor.fetchone():
            print("❌ Table 'sage_businesses' does not exist")
            conn.close()
            return False
        
        # Check if metadata column exists
        cursor.execute("PRAGMA table_info(sage_businesses)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'business_metadata' in column_names:
            print("✅ Column 'business_metadata' already exists. No changes needed.")
            conn.close()
            return True
        
        if 'metadata' not in column_names:
            print("❌ Column 'metadata' does not exist")
            conn.close()
            return False
        
        print("🔄 Renaming 'metadata' column to 'business_metadata'...")
        
        # SQLite doesn't support RENAME COLUMN directly in older versions
        # We need to use the ALTER TABLE ... RENAME COLUMN syntax (SQLite 3.25.0+)
        try:
            cursor.execute("ALTER TABLE sage_businesses RENAME COLUMN metadata TO business_metadata")
            conn.commit()
            print("✅ Column renamed successfully!")
        except sqlite3.OperationalError as e:
            if "no such column" in str(e).lower():
                print("✅ Column already renamed or doesn't exist")
            else:
                raise
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("FIX SAGE METADATA COLUMN")
    print("=" * 70)
    
    success = fix_metadata_column()
    
    if success:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

