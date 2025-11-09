#!/usr/bin/env python3
"""
Apply the project status CHECK constraint fix migration.

This script applies the schema_v9_1_fix_project_status_constraint.sql migration
to fix the IntegrityError caused by the mismatch between the model's VALID_STATUSES
and the database CHECK constraint.

Usage:
    python scripts/apply_status_constraint_fix.py
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Project


def get_db_path():
    """Get the database path from the app config."""
    app = create_app()
    with app.app_context():
        # Get database URI and extract path
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            return db_path
        else:
            raise ValueError(f"Unsupported database URI: {db_uri}")


def backup_database(db_path):
    """Create a backup of the database before migration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    
    print(f"Creating backup: {backup_path}")
    
    # Copy database file
    import shutil
    shutil.copy2(db_path, backup_path)
    
    print(f"✓ Backup created successfully")
    return backup_path


def check_current_schema_version(db_path):
    """Check the current schema version."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        if result:
            version = result[0]
            print(f"Current schema version: {version}")
            return version
        else:
            print("Warning: No schema version found in settings table")
            return None
    except sqlite3.Error as e:
        print(f"Error checking schema version: {e}")
        return None
    finally:
        conn.close()


def verify_constraint_issue(db_path):
    """Verify that the constraint issue exists."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nVerifying constraint issue...")
    
    try:
        # Get the table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
        result = cursor.fetchone()
        
        if result:
            schema = result[0]
            print("\nCurrent projects table schema:")
            print("-" * 80)
            print(schema)
            print("-" * 80)
            
            # Check if new statuses are in the constraint
            if "'Request'" in schema:
                print("\n✓ New status values already in CHECK constraint")
                return False
            else:
                print("\n✗ New status values NOT in CHECK constraint - migration needed")
                return True
        else:
            print("Error: projects table not found")
            return False
            
    except sqlite3.Error as e:
        print(f"Error verifying constraint: {e}")
        return False
    finally:
        conn.close()


def apply_migration(db_path, migration_file):
    """Apply the migration SQL file."""
    print(f"\nApplying migration: {migration_file}")
    
    # Read migration file
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Execute migration (SQLite executescript handles multiple statements)
        cursor.executescript(migration_sql)
        conn.commit()
        print("✓ Migration applied successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Error applying migration: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_migration_success(db_path):
    """Verify that the migration was successful."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nVerifying migration success...")
    
    try:
        # Check schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        if result:
            version = result[0]
            print(f"✓ Schema version updated to: {version}")
        
        # Check table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
        result = cursor.fetchone()
        
        if result:
            schema = result[0]
            
            # Verify new statuses are in constraint
            new_statuses = ['Request', 'Quote & Approval', 'Approved (POP Received)', 'Queued (Scheduled for Cutting)']
            all_present = all(f"'{status}'" in schema for status in new_statuses)
            
            if all_present:
                print("✓ All new status values present in CHECK constraint")
                print("\nNew valid statuses:")
                for status in new_statuses:
                    print(f"  - {status}")
                return True
            else:
                print("✗ Some new status values missing from CHECK constraint")
                return False
        else:
            print("✗ projects table not found")
            return False
            
    except sqlite3.Error as e:
        print(f"✗ Error verifying migration: {e}")
        return False
    finally:
        conn.close()


def test_new_status():
    """Test that we can now use the new 'Request' status."""
    print("\nTesting new status values...")
    
    app = create_app()
    with app.app_context():
        try:
            # Try to create a test project with 'Request' status
            from app.models import Client
            
            # Get first client for testing
            client = Client.query.first()
            if not client:
                print("⚠ No clients found - skipping status test")
                return True
            
            # Create a test project
            test_project = Project(
                project_code=f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                client_id=client.id,
                name="Test Project - Status Constraint Fix",
                status=Project.STATUS_REQUEST  # This should now work
            )
            
            db.session.add(test_project)
            db.session.commit()
            
            print(f"✓ Successfully created project with status: {test_project.status}")
            
            # Clean up test project
            db.session.delete(test_project)
            db.session.commit()
            print("✓ Test project cleaned up")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error testing new status: {e}")
            return False


def main():
    """Main execution function."""
    print("=" * 80)
    print("Project Status CHECK Constraint Fix Migration")
    print("=" * 80)
    
    # Get database path
    try:
        db_path = get_db_path()
        print(f"\nDatabase path: {db_path}")
    except Exception as e:
        print(f"Error getting database path: {e}")
        return 1
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return 1
    
    # Check current schema version
    check_current_schema_version(db_path)
    
    # Verify the constraint issue exists
    needs_migration = verify_constraint_issue(db_path)
    
    if not needs_migration:
        print("\n✓ Migration not needed - constraint already updated")
        return 0
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    response = input("Do you want to proceed with the migration? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled")
        return 0
    
    # Create backup
    try:
        backup_path = backup_database(db_path)
    except Exception as e:
        print(f"Error creating backup: {e}")
        return 1
    
    # Apply migration
    migration_file = os.path.join('migrations', 'schema_v9_1_fix_project_status_constraint.sql')
    
    if not os.path.exists(migration_file):
        print(f"Error: Migration file not found at {migration_file}")
        return 1
    
    success = apply_migration(db_path, migration_file)
    
    if not success:
        print(f"\n✗ Migration failed - database backup available at: {backup_path}")
        return 1
    
    # Verify migration
    if not verify_migration_success(db_path):
        print(f"\n✗ Migration verification failed - database backup available at: {backup_path}")
        return 1
    
    # Test new status
    if not test_new_status():
        print("\n⚠ Status test failed, but migration was applied")
    
    print("\n" + "=" * 80)
    print("✓ Migration completed successfully!")
    print(f"✓ Database backup saved at: {backup_path}")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

