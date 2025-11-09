"""
Simple standalone script to apply the project status CHECK constraint fix.

This script applies the schema_v9_1_fix_project_status_constraint.sql migration
without requiring Flask or any app dependencies.

Usage:
    python scripts/fix_project_status_constraint_simple.py
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import shutil

# Paths
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'data' / 'laser_os.db'
MIGRATION_FILE = BASE_DIR / 'migrations' / 'schema_v9_1_fix_project_status_constraint.sql'

def main():
    print("=" * 80)
    print("PROJECT STATUS CHECK CONSTRAINT FIX")
    print("=" * 80)
    
    # Check if database exists
    if not DB_PATH.exists():
        print(f"\n❌ ERROR: Database not found at {DB_PATH}")
        return 1
    
    # Check if migration file exists
    if not MIGRATION_FILE.exists():
        print(f"\n❌ ERROR: Migration file not found at {MIGRATION_FILE}")
        return 1
    
    print(f"\n📊 Database: {DB_PATH}")
    print(f"📝 Migration: {MIGRATION_FILE}")
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check current schema version
        cursor.execute("SELECT value FROM settings WHERE key='schema_version'")
        result = cursor.fetchone()
        current_version = result[0] if result else "Unknown"
        print(f"\n✅ Current schema version: {current_version}")
        
        # Check if migration already applied
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
        result = cursor.fetchone()
        
        if result and "'Request'" in result[0]:
            print("\n✅ Migration already applied - CHECK constraint already includes new status values")
            print("\n📋 Valid status values:")
            print("   - Request")
            print("   - Quote & Approval")
            print("   - Approved (POP Received)")
            print("   - Queued (Scheduled for Cutting)")
            print("   - In Progress")
            print("   - Completed")
            print("   - Cancelled")
            print("   - Quote (legacy)")
            print("   - Approved (legacy)")
            conn.close()
            return 0
        
        # Count existing projects
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        print(f"✅ Found {project_count} existing projects")
        
        # Show current constraint
        print("\n📋 Current CHECK constraint:")
        if result:
            schema = result[0]
            # Extract CHECK constraint
            if "CHECK" in schema:
                check_start = schema.find("CHECK")
                check_end = schema.find(")", check_start) + 1
                check_constraint = schema[check_start:check_end]
                print(f"   {check_constraint[:100]}...")
        
        # Create backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{DB_PATH}.backup_{timestamp}"
        print(f"\n💾 Creating backup: {backup_path}")
        shutil.copy2(DB_PATH, backup_path)
        print("✅ Backup created successfully")
        
        # Confirm execution
        print("\n" + "=" * 80)
        print("⚠️  This migration will:")
        print("   1. Create a new projects table with updated CHECK constraint")
        print("   2. Copy all existing data to the new table")
        print("   3. Drop the old table and rename the new one")
        print("   4. Recreate all indexes")
        print("   5. Update schema version to 9.1")
        print("=" * 80)
        
        response = input("\n❓ Apply migration? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Migration cancelled by user")
            conn.close()
            return 0
        
        # Read migration file
        print("\n📝 Reading migration file...")
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("\n🔧 Applying migration...")
        print("   ⏳ This may take a moment...")
        
        cursor.executescript(migration_sql)
        conn.commit()
        
        print("\n✅ Migration applied successfully!")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        
        # Check schema version
        cursor.execute("SELECT value FROM settings WHERE key='schema_version'")
        result = cursor.fetchone()
        new_version = result[0] if result else "Unknown"
        print(f"✅ Schema version: {new_version}")
        
        # Verify data integrity
        cursor.execute("SELECT COUNT(*) FROM projects")
        new_project_count = cursor.fetchone()[0]
        print(f"✅ Projects preserved: {new_project_count}/{project_count}")
        
        if new_project_count != project_count:
            print(f"⚠️  WARNING: Project count mismatch!")
        
        # Verify indexes
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name='projects'")
        index_count = cursor.fetchone()[0]
        print(f"✅ Indexes created: {index_count}")
        
        # Verify new constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
        result = cursor.fetchone()
        
        if result and "'Request'" in result[0]:
            print("✅ CHECK constraint updated successfully")
        else:
            print("⚠️  WARNING: CHECK constraint may not be updated correctly")
        
        # Check activity log
        cursor.execute("""
            SELECT details, created_at 
            FROM activity_log 
            WHERE action = 'MIGRATION' 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        log_entry = cursor.fetchone()
        if log_entry:
            print(f"✅ Migration logged: {log_entry[0][:60]}...")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📋 Summary:")
        print(f"   - Schema version: {new_version}")
        print(f"   - Projects preserved: {new_project_count}")
        print(f"   - Indexes created: {index_count}")
        print(f"   - Backup saved: {backup_path}")
        print("\n✅ You can now create projects with these status values:")
        print("   - Request")
        print("   - Quote & Approval")
        print("   - Approved (POP Received)")
        print("   - Queued (Scheduled for Cutting)")
        print("   - In Progress")
        print("   - Completed")
        print("   - Cancelled")
        print("   - Quote (legacy)")
        print("   - Approved (legacy)")
        
        return 0
        
    except sqlite3.Error as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        conn.rollback()
        conn.close()
        print(f"\n💾 Database backup available at: {backup_path}")
        return 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        conn.close()
        return 1

if __name__ == '__main__':
    exit(main())

