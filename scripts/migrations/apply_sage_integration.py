#!/usr/bin/env python3
"""
Laser OS - Sage Integration Migration Script
Apply Sage Business Cloud Accounting integration schema

This script:
1. Creates a backup of the database
2. Applies the Sage integration schema migration
3. Verifies the migration was successful
4. Provides rollback instructions if needed

Usage:
    python scripts/migrations/apply_sage_integration.py
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration
DB_PATH = Path('data/laser_os.db')
BACKUP_DIR = Path('data/backups')
MIGRATION_FILE = Path('migrations/schema_sage_integration.sql')
ROLLBACK_FILE = Path('migrations/rollback_sage_integration.sql')


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text):
    """Print info message."""
    print(f"ℹ {text}")


def create_backup():
    """Create a backup of the database."""
    print_header("STEP 1: Creating Database Backup")
    
    if not DB_PATH.exists():
        print_error(f"Database not found at {DB_PATH}")
        return None
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'laser_os_backup_sage_integration_{timestamp}.db'
    
    # Copy database
    shutil.copy2(DB_PATH, backup_path)
    print_success(f"Backup created: {backup_path}")
    
    return backup_path


def verify_prerequisites():
    """Verify that prerequisites are met."""
    print_header("STEP 2: Verifying Prerequisites")
    
    # Check if database exists
    if not DB_PATH.exists():
        print_error(f"Database not found at {DB_PATH}")
        return False
    print_success("Database exists")
    
    # Check if migration file exists
    if not MIGRATION_FILE.exists():
        print_error(f"Migration file not found at {MIGRATION_FILE}")
        return False
    print_success("Migration file exists")
    
    # Check if users table exists (required for foreign key)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print_error("Users table not found. Please ensure authentication system is set up.")
        conn.close()
        return False
    print_success("Users table exists")
    conn.close()
    
    return True


def apply_migration():
    """Apply the Sage integration migration."""
    print_header("STEP 3: Applying Migration")
    
    try:
        # Read migration SQL
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute migration
        cursor.executescript(migration_sql)
        conn.commit()
        
        print_success("Migration SQL executed successfully")
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_migration():
    """Verify that the migration was successful."""
    print_header("STEP 4: Verifying Migration")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if all tables were created
        expected_tables = [
            'sage_connections',
            'sage_businesses',
            'sage_sync_cursors',
            'sage_audit_logs'
        ]
        
        for table in expected_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print_success(f"Table '{table}' created")
            else:
                print_error(f"Table '{table}' not found")
                conn.close()
                return False
        
        # Check schema version
        cursor.execute("SELECT version FROM schema_version WHERE version='sage_integration_v1.0'")
        if cursor.fetchone():
            print_success("Schema version recorded")
        else:
            print_error("Schema version not recorded")
            conn.close()
            return False
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_sage_%'")
        indexes = cursor.fetchall()
        print_success(f"Created {len(indexes)} indexes")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Verification failed: {str(e)}")
        return False


def print_rollback_instructions(backup_path):
    """Print rollback instructions."""
    print_header("ROLLBACK INSTRUCTIONS")
    print("\nIf you need to rollback this migration, you have two options:\n")
    print("Option 1: Use the rollback SQL script")
    print(f"  sqlite3 {DB_PATH} < {ROLLBACK_FILE}")
    print("\nOption 2: Restore from backup")
    print(f"  cp {backup_path} {DB_PATH}")
    print()


def print_next_steps():
    """Print next steps."""
    print_header("✓ MIGRATION COMPLETE!")
    print("\nThe Sage integration schema has been successfully applied.\n")
    print("Next steps:")
    print("1. Restart the Flask server to load the new models")
    print("2. Configure Sage OAuth credentials in your environment")
    print("3. Access Sage integration at: http://127.0.0.1:5000/sage/")
    print("4. Connect your Sage Business Cloud Accounting account")
    print()


def main():
    """Main migration function."""
    print_header("LASER OS - SAGE INTEGRATION MIGRATION")
    print("\nThis script will add Sage Business Cloud Accounting integration to Laser OS.")
    print("The following tables will be created:")
    print("  - sage_connections (OAuth tokens)")
    print("  - sage_businesses (Business contexts)")
    print("  - sage_sync_cursors (Sync tracking)")
    print("  - sage_audit_logs (Audit trail)")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed? (y/N): ")
    if response.lower() != 'y':
        print("\nMigration cancelled.")
        return 0
    
    # Create backup
    backup_path = create_backup()
    if not backup_path:
        print_error("Backup failed. Migration aborted.")
        return 1
    
    # Verify prerequisites
    if not verify_prerequisites():
        print_error("Prerequisites not met. Migration aborted.")
        print_rollback_instructions(backup_path)
        return 1
    
    # Apply migration
    if not apply_migration():
        print_error("Migration failed. Please restore from backup.")
        print_rollback_instructions(backup_path)
        return 1
    
    # Verify migration
    if not verify_migration():
        print_error("Migration verification failed. Please check the database.")
        print_rollback_instructions(backup_path)
        return 1
    
    # Success!
    print_next_steps()
    print_rollback_instructions(backup_path)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

