#!/usr/bin/env python3
"""
Apply Phase 10 Part 3 Migration: Machine Settings Presets and Operators Tables

This script:
1. Creates a backup of the database
2. Applies the Phase 3 schema migration
3. Verifies the migration was successful
4. Provides rollback instructions if needed
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
DB_PATH = 'data/laser_os.db'
BACKUP_DIR = 'data/backups'
MIGRATION_FILE = 'migrations/schema_v10_phase3_presets.sql'
ROLLBACK_FILE = 'migrations/rollback_v10_phase3.sql'

def create_backup():
    """Create a backup of the database."""
    print("=" * 70)
    print("STEP 1: Creating Database Backup")
    print("=" * 70)
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'laser_os_backup_v10_phase3_{timestamp}.db'
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
    """Apply the Phase 3 migration."""
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
        
        # Execute migration (SQLite executescript handles multiple statements)
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
        
        # Check if operators table exists
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='operators'
        """)
        operators_exists = cursor.fetchone()[0] > 0
        
        # Check if machine_settings_presets table exists
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='machine_settings_presets'
        """)
        presets_exists = cursor.fetchone()[0] > 0
        
        # Check if preset_id column was added to laser_runs
        cursor.execute("PRAGMA table_info(laser_runs)")
        columns = cursor.fetchall()
        preset_id_exists = any(col[1] == 'preset_id' for col in columns)
        
        # Count operators
        cursor.execute("SELECT COUNT(*) FROM operators")
        operator_count = cursor.fetchone()[0]
        
        # Count presets
        cursor.execute("SELECT COUNT(*) FROM machine_settings_presets")
        preset_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute("SELECT id, name, is_active FROM operators LIMIT 5")
        operators = cursor.fetchall()
        
        cursor.execute("""
            SELECT id, preset_name, material_type, thickness 
            FROM machine_settings_presets 
            LIMIT 5
        """)
        presets = cursor.fetchall()
        
        conn.close()
        
        # Display results
        print("\n📊 Migration Verification Results:")
        print(f"\n  ✅ operators table: {'EXISTS' if operators_exists else 'MISSING'}")
        if operators_exists:
            print(f"     - Records: {operator_count}")
            print(f"     - Sample data:")
            for op in operators:
                status = "Active" if op[2] else "Inactive"
                print(f"       • ID {op[0]}: {op[1]} ({status})")
        
        print(f"\n  ✅ machine_settings_presets table: {'EXISTS' if presets_exists else 'MISSING'}")
        if presets_exists:
            print(f"     - Records: {preset_count}")
            print(f"     - Sample data:")
            for preset in presets:
                print(f"       • ID {preset[0]}: {preset[1]} ({preset[2]} {preset[3]}mm)")
        
        print(f"\n  ✅ laser_runs.preset_id column: {'EXISTS' if preset_id_exists else 'MISSING'}")
        
        # Overall status
        success = operators_exists and presets_exists and preset_id_exists
        
        if success:
            print("\n" + "=" * 70)
            print("✅ MIGRATION SUCCESSFUL!")
            print("=" * 70)
            print(f"\nNew tables created:")
            print(f"  • operators ({operator_count} records)")
            print(f"  • machine_settings_presets ({preset_count} records)")
            print(f"\nTables modified:")
            print(f"  • laser_runs (added preset_id column)")
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
    print("\nOption 3: Use Python script")
    print(f"  python -c \"import sqlite3; conn = sqlite3.connect('{DB_PATH}'); ")
    print(f"  conn.executescript(open('{ROLLBACK_FILE}').read()); conn.close()\"")

def main():
    """Main migration function."""
    print("\n" + "=" * 70)
    print("LASER OS - PHASE 10 PART 3 MIGRATION")
    print("Machine Settings Presets and Operators Tables")
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
    print("🎉 PHASE 10 PART 3 MIGRATION COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review the new tables in the database")
    print("  2. Test the application to ensure everything works")
    print("  3. Proceed to Phase 4: Model Updates")
    print(f"\nBackup saved at: {backup_path}")
    
    display_rollback_instructions(backup_path)
    
    return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

