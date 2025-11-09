#!/usr/bin/env python3
"""
Database Cleanup Script for Laser OS
Removes all data while preserving the schema structure
"""

import os
import sys
import sqlite3
from pathlib import Path
import shutil


def get_database_path():
    """Get the database file path."""
    return 'data/laser_os.db'


def backup_database():
    """Create a backup of the database before cleanup."""
    from datetime import datetime
    
    db_path = get_database_path()
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return None
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'data/laser_os_backup_{timestamp}.db'
    
    try:
        shutil.copy2(db_path, backup_path)
        file_size = os.path.getsize(backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        print(f"   Backup size: {file_size:,} bytes")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {str(e)}")
        return None


def get_table_counts(conn):
    """Get record counts for all tables."""
    cursor = conn.cursor()

    tables = {
        'clients': 'SELECT COUNT(*) FROM clients',
        'projects': 'SELECT COUNT(*) FROM projects',
        'design_files': 'SELECT COUNT(*) FROM design_files',
        'project_documents': 'SELECT COUNT(*) FROM project_documents',
        'queue_items': 'SELECT COUNT(*) FROM queue_items',
        'laser_runs': 'SELECT COUNT(*) FROM laser_runs',
        'project_products': 'SELECT COUNT(*) FROM project_products',
        'communications': 'SELECT COUNT(*) FROM communications',
        'communication_attachments': 'SELECT COUNT(*) FROM communication_attachments'
    }

    counts = {}
    for table, query in tables.items():
        try:
            cursor.execute(query)
            counts[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            counts[table] = 0

    return counts


def clean_file_storage():
    """Clean up file storage directories."""
    print("\n" + "="*80)
    print("CLEANING FILE STORAGE")
    print("="*80)
    
    directories_to_clean = [
        'data/files/projects',
        'data/documents/quotes',
        'data/documents/invoices',
        'data/documents/pops',
        'data/documents/delivery_notes'
    ]
    
    files_removed = 0
    dirs_removed = 0
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            try:
                # Remove all files and subdirectories
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        files_removed += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        dirs_removed += 1
                print(f"✅ Cleaned: {directory}")
            except Exception as e:
                print(f"⚠️  Error cleaning {directory}: {str(e)}")
        else:
            print(f"⚠️  Directory not found: {directory}")
    
    print(f"\n📊 Files removed: {files_removed}")
    print(f"📊 Directories removed: {dirs_removed}")
    
    return files_removed, dirs_removed


def clean_database_data(conn):
    """Remove all data from database tables while preserving schema."""
    print("\n" + "="*80)
    print("CLEANING DATABASE DATA")
    print("="*80)
    
    cursor = conn.cursor()
    
    # Get counts before cleanup
    print("\n📊 Current record counts:")
    before_counts = get_table_counts(conn)
    for table, count in before_counts.items():
        print(f"   {table}: {count}")
    
    # Delete data in correct order (respecting foreign keys)
    tables_to_clean = [
        'communication_attachments',
        'communications',
        'laser_runs',
        'queue_items',
        'project_products',
        'project_documents',
        'design_files',
        'projects',
        'clients'
    ]
    
    print("\n🗑️  Deleting data...")
    
    try:
        # Disable foreign key constraints temporarily
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        for table in tables_to_clean:
            try:
                cursor.execute(f'DELETE FROM {table}')
                deleted = cursor.rowcount
                print(f"   ✅ Deleted {deleted} records from {table}")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  Table {table} not found or error: {str(e)}")
        
        # Re-enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Reset auto-increment counters
        cursor.execute('DELETE FROM sqlite_sequence')
        print(f"   ✅ Reset auto-increment counters")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during cleanup: {str(e)}")
        return False
    
    # Get counts after cleanup
    print("\n📊 Record counts after cleanup:")
    after_counts = get_table_counts(conn)
    for table, count in after_counts.items():
        print(f"   {table}: {count}")
    
    # Verify all tables are empty
    if all(count == 0 for count in after_counts.values()):
        print("\n✅ All tables successfully cleaned!")
        return True
    else:
        print("\n⚠️  Some tables still contain data")
        return False


def verify_schema(conn):
    """Verify that the database schema is still intact."""
    print("\n" + "="*80)
    print("VERIFYING DATABASE SCHEMA")
    print("="*80)
    
    cursor = conn.cursor()
    
    # Check for required tables
    required_tables = [
        'clients',
        'projects',
        'design_files',
        'project_documents',
        'communications',
        'communication_attachments'
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    print("\n📋 Checking required tables:")
    all_present = True
    for table in required_tables:
        if table in existing_tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} - MISSING!")
            all_present = False
    
    if all_present:
        print("\n✅ Database schema is intact!")
        return True
    else:
        print("\n❌ Database schema is incomplete!")
        return False


def main():
    """Main cleanup function."""
    print("="*80)
    print("LASER OS - DATABASE CLEANUP SCRIPT")
    print("="*80)
    print("\n⚠️  WARNING: This will delete ALL data from the database!")
    print("   - All clients will be removed")
    print("   - All projects will be removed")
    print("   - All design files will be removed")
    print("   - All project documents will be removed")
    print("   - All communications will be removed")
    print("   - All files in storage directories will be removed")
    print("\n   The database schema will be preserved.")
    
    # Check if running in non-interactive mode
    if '--yes' in sys.argv or '-y' in sys.argv:
        confirm = 'yes'
    else:
        print("\n" + "="*80)
        confirm = input("\nType 'yes' to continue with cleanup: ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Cleanup cancelled by user")
        return 1
    
    # Step 1: Backup database
    print("\n" + "="*80)
    print("STEP 1: BACKING UP DATABASE")
    print("="*80)
    
    backup_path = backup_database()
    if not backup_path:
        print("\n❌ Backup failed. Cleanup aborted for safety.")
        return 1
    
    # Step 2: Connect to database
    db_path = get_database_path()
    try:
        conn = sqlite3.connect(db_path)
        print(f"\n✅ Connected to database: {db_path}")
    except Exception as e:
        print(f"\n❌ Error connecting to database: {str(e)}")
        return 1
    
    try:
        # Step 3: Clean database data
        print("\n" + "="*80)
        print("STEP 2: CLEANING DATABASE DATA")
        print("="*80)
        
        if not clean_database_data(conn):
            print("\n❌ Database cleanup failed")
            return 1
        
        # Step 4: Verify schema
        if not verify_schema(conn):
            print("\n❌ Schema verification failed")
            return 1
        
        # Step 5: Clean file storage
        print("\n" + "="*80)
        print("STEP 3: CLEANING FILE STORAGE")
        print("="*80)
        
        clean_file_storage()
        
        # Final summary
        print("\n" + "="*80)
        print("✅ CLEANUP COMPLETE!")
        print("="*80)
        print(f"\n📁 Backup saved to: {backup_path}")
        print("\n✅ Database is now empty and ready for fresh data import")
        print("✅ Database schema is intact")
        print("✅ File storage directories are cleaned")
        print("\n🚀 You can now import your real business data using:")
        print("   python bulk_import.py --all --clients clients_import_template_full.csv --projects projects_import_template_full.csv")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

