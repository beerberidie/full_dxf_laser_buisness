#!/usr/bin/env python3
"""
Apply Phase 10 Part 4 Migration: Add operator_id to laser_runs

This script:
1. Creates a backup of the database
2. Applies the Phase 4 schema migration (adds operator_id column)
3. Verifies the migration was successful
4. Provides rollback instructions if needed
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Configuration
DB_PATH = 'data/laser_os.db'
BACKUP_DIR = 'data/backups'
MIGRATION_FILE = 'migrations/schema_v10_phase4_operator_id.sql'
ROLLBACK_FILE = 'migrations/rollback_v10_phase4.sql'

def create_backup():
    """Create a backup of the database."""
    print("=" * 70)
    print("STEP 1: Creating Database Backup")
    print("=" * 70)
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'laser_os_backup_v10_phase4_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Copy database file
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup created: {backup_path}")
        file_size = os.path.getsize(backup_path)
        print(f"   Size: {file_size:,} bytes")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def verify_database():
    """Verify database exists and is accessible."""
    print("\n" + "=" * 70)
    print("STEP 2: Verifying Database")
    print("=" * 70)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if database is valid
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        print(f"✅ Database is valid")
        print(f"   Path: {DB_PATH}")
        print(f"   Tables: {table_count}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def apply_migration():
    """Apply the Phase 4 migration."""
    print("\n" + "=" * 70)
    print("STEP 3: Applying Migration")
    print("=" * 70)
    
    if not os.path.exists(MIGRATION_FILE):
        print(f"❌ Migration file not found: {MIGRATION_FILE}")
        return False
    
    try:
        # Read migration SQL
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute migration
        print("📝 Executing migration SQL...")
        cursor.executescript(migration_sql)
        
        conn.commit()
        conn.close()
        
        print("✅ Migration applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        print(f"\n⚠️  To rollback, run:")
        print(f"   sqlite3 {DB_PATH} < {ROLLBACK_FILE}")
        return False

def verify_migration():
    """Verify the migration was successful."""
    print("\n" + "=" * 70)
    print("STEP 4: Verifying Migration")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if operator_id column was added to laser_runs
        cursor.execute("PRAGMA table_info(laser_runs)")
        columns = cursor.fetchall()
        operator_id_exists = any(col[1] == 'operator_id' for col in columns)
        
        # Check if index was created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='laser_runs' AND name='idx_laser_runs_operator_id'
        """)
        index_exists = cursor.fetchone() is not None
        
        conn.close()
        
        # Display results
        print("\n📊 Migration Verification Results:")
        print(f"\n  ✅ laser_runs.operator_id column: {'EXISTS' if operator_id_exists else 'MISSING'}")
        print(f"  ✅ idx_laser_runs_operator_id index: {'EXISTS' if index_exists else 'MISSING'}")
        
        # Overall status
        success = operator_id_exists and index_exists
        
        if success:
            print("\n" + "=" * 70)
            print("✅ MIGRATION SUCCESSFUL!")
            print("=" * 70)
            print(f"\nTables modified:")
            print(f"  • laser_runs (added operator_id column)")
            print(f"\nIndexes created:")
            print(f"  • idx_laser_runs_operator_id")
        else:
            print("\n" + "=" * 70)
            print("❌ MIGRATION VERIFICATION FAILED")
            print("=" * 70)
        
        return success
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def display_rollback_instructions(backup_path):
    """Display rollback instructions."""
    print("\n" + "=" * 70)
    print("ROLLBACK INSTRUCTIONS")
    print("=" * 70)
    print("\nIf you need to rollback this migration:")
    print("\nOption 1: Restore from backup")
    print(f"  Copy-Item {backup_path} {DB_PATH} -Force")
    print("\nOption 2: Run rollback script")
    print(f"  Get-Content {ROLLBACK_FILE} | sqlite3 {DB_PATH}")

def main():
    """Main migration function."""
    print("\n" + "=" * 70)
    print("LASER OS - PHASE 10 PART 4 MIGRATION")
    print("Add operator_id to laser_runs Table")
    print("=" * 70)
    
    # Step 1: Create backup
    backup_path = create_backup()
    if not backup_path:
        print("\n❌ Migration aborted: Could not create backup")
        return False
    
    # Step 2: Verify database
    if not verify_database():
        print("\n❌ Migration aborted: Database verification failed")
        return False
    
    # Step 3: Apply migration
    if not apply_migration():
        print("\n❌ Migration failed")
        display_rollback_instructions(backup_path)
        return False
    
    # Step 4: Verify migration
    if not verify_migration():
        print("\n❌ Migration verification failed")
        display_rollback_instructions(backup_path)
        return False
    
    # Success!
    print("\n" + "=" * 70)
    print("🎉 PHASE 10 PART 4 MIGRATION COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Test the new models in the Flask app")
    print("  2. Verify model relationships work correctly")
    print("  3. Proceed to Phase 5: Dropdown Conversions")
    print(f"\nBackup saved at: {backup_path}")
    
    display_rollback_instructions(backup_path)
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

