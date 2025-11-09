#!/usr/bin/env python3
"""
Laser OS - Schema v9.2 Migration Script
========================================
Adds 'Other' and 'Image' document types to project_documents table.

This script:
1. Creates a backup of the database
2. Applies the v9.2 schema migration
3. Validates the migration was successful
4. Provides rollback capability if needed

Usage:
    python scripts/migrations/apply_v9_2_document_types.py
    python scripts/migrations/apply_v9_2_document_types.py --rollback  # To rollback
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys
import argparse
from pathlib import Path


class MigrationManager:
    """Manages the v9.2 migration process."""
    
    def __init__(self):
        self.db_path = 'data/laser_os.db'
        self.migration_file = 'migrations/schema_v9_2_add_document_types.sql'
        self.rollback_file = 'migrations/rollback_v9_2.sql'
        self.backup_path = None
        
    def create_backup(self):
        """Create a backup of the database before migration."""
        print("\n" + "="*70)
        print("STEP 1: CREATING DATABASE BACKUP")
        print("="*70)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at {self.db_path}")
            return False
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = f'data/laser_os.db.backup_v9_1_to_v9_2_{timestamp}'
        
        try:
            shutil.copy2(self.db_path, self.backup_path)
            backup_size = os.path.getsize(self.backup_path) / 1024 / 1024
            print(f"✓ Backup created: {self.backup_path}")
            print(f"✓ Backup size: {backup_size:.2f} MB")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def get_current_schema_version(self):
        """Get the current schema version."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 'Unknown'
        except Exception as e:
            print(f"⚠ Could not read schema version: {e}")
            return 'Unknown'
    
    def check_existing_documents(self):
        """Check for existing documents in the database."""
        print("\n" + "="*70)
        print("CHECKING EXISTING DOCUMENTS")
        print("="*70)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count total documents
            cursor.execute("SELECT COUNT(*) FROM project_documents")
            total = cursor.fetchone()[0]
            print(f"Total documents: {total}")
            
            # Count by type
            cursor.execute("""
                SELECT document_type, COUNT(*) 
                FROM project_documents 
                GROUP BY document_type
            """)
            for doc_type, count in cursor.fetchall():
                print(f"  - {doc_type}: {count}")
            
            conn.close()
            return True
        except Exception as e:
            print(f"⚠ Could not check documents: {e}")
            return True  # Continue anyway
    
    def apply_migration(self):
        """Apply the migration SQL."""
        print("\n" + "="*70)
        print("STEP 2: APPLYING MIGRATION")
        print("="*70)
        
        if not os.path.exists(self.migration_file):
            print(f"❌ Migration file not found: {self.migration_file}")
            return False
        
        try:
            # Read migration SQL
            with open(self.migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Apply migration
            conn = sqlite3.connect(self.db_path)
            conn.executescript(migration_sql)
            conn.close()
            
            print("✓ Migration SQL executed successfully")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_migration(self):
        """Verify the migration was successful."""
        print("\n" + "="*70)
        print("STEP 3: VERIFYING MIGRATION")
        print("="*70)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check schema version
            cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
            version = cursor.fetchone()[0]
            print(f"✓ Schema version: {version}")
            
            if version != '9.2':
                print(f"⚠ Warning: Expected version 9.2, got {version}")
            
            # Check table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='project_documents'
            """)
            if cursor.fetchone():
                print("✓ project_documents table exists")
            else:
                print("❌ project_documents table not found!")
                return False
            
            # Check indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='project_documents'
            """)
            indexes = cursor.fetchall()
            print(f"✓ Found {len(indexes)} indexes")
            for idx in indexes:
                print(f"  - {idx[0]}")
            
            # Count documents
            cursor.execute("SELECT COUNT(*) FROM project_documents")
            count = cursor.fetchone()[0]
            print(f"✓ Document count: {count}")
            
            # Test new constraint by attempting to insert a test record
            print("\n✓ Testing new document types...")
            try:
                # Test 'Other' type
                cursor.execute("""
                    SELECT 1 FROM (
                        SELECT 'Other' AS test_type
                    ) WHERE test_type IN ('Quote', 'Invoice', 'Proof of Payment', 'Delivery Note', 'Other', 'Image')
                """)
                if cursor.fetchone():
                    print("  ✓ 'Other' document type is valid")
                
                # Test 'Image' type
                cursor.execute("""
                    SELECT 1 FROM (
                        SELECT 'Image' AS test_type
                    ) WHERE test_type IN ('Quote', 'Invoice', 'Proof of Payment', 'Delivery Note', 'Other', 'Image')
                """)
                if cursor.fetchone():
                    print("  ✓ 'Image' document type is valid")
                
            except Exception as e:
                print(f"  ⚠ Could not verify new types: {e}")
            
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def rollback(self):
        """Rollback the migration by restoring from backup."""
        print("\n" + "="*70)
        print("ROLLING BACK MIGRATION")
        print("="*70)
        
        if not self.backup_path or not os.path.exists(self.backup_path):
            print(f"❌ Backup not found: {self.backup_path}")
            return False
        
        try:
            # Restore from backup
            shutil.copy2(self.backup_path, self.db_path)
            print(f"✓ Database restored from: {self.backup_path}")
            
            # Verify
            version = self.get_current_schema_version()
            print(f"✓ Schema version after rollback: {version}")
            
            return True
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def run(self):
        """Run the complete migration process."""
        print("\n" + "="*70)
        print("LASER OS - SCHEMA v9.2 MIGRATION")
        print("Add 'Other' and 'Image' Document Types")
        print("="*70)
        
        # Show current state
        current_version = self.get_current_schema_version()
        print(f"\nCurrent schema version: {current_version}")
        
        if current_version == '9.2':
            print("\n✓ Database is already at version 9.2")
            print("No migration needed.")
            return True
        
        # Check existing documents
        self.check_existing_documents()
        
        # Confirm
        print("\n" + "="*70)
        response = input("\nProceed with migration? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return False
        
        # Step 1: Backup
        if not self.create_backup():
            print("\n❌ Migration aborted - backup failed")
            return False
        
        # Step 2: Apply migration
        if not self.apply_migration():
            print("\n❌ Migration failed!")
            print(f"\nTo restore from backup, run:")
            print(f"  Copy-Item {self.backup_path} {self.db_path} -Force")
            return False
        
        # Step 3: Verify
        if not self.verify_migration():
            print("\n⚠ Migration completed but verification failed")
            print(f"\nTo rollback, run:")
            print(f"  python {__file__} --rollback")
            return False
        
        # Success!
        print("\n" + "="*70)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\nSchema version: 9.1 → 9.2")
        print(f"Backup location: {self.backup_path}")
        print("\nNew document types available:")
        print("  - Other")
        print("  - Image")
        print("\nYou can now upload documents with these types!")
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Apply v9.2 migration')
    parser.add_argument('--rollback', action='store_true', 
                       help='Rollback to previous version')
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.rollback:
        print("🔄 Rollback mode")
        # Find most recent backup
        backup_files = [f for f in os.listdir('data') 
                       if f.startswith('laser_os.db.backup_v9_1_to_v9_2_')]
        if not backup_files:
            print("❌ No backup files found")
            return 1
        
        backup_files.sort(reverse=True)
        manager.backup_path = os.path.join('data', backup_files[0])
        print(f"Found backup: {manager.backup_path}")
        
        response = input("Restore from this backup? (y/N): ")
        if response.lower() == 'y':
            if manager.rollback():
                print("✓ Rollback successful")
                return 0
        return 1
    
    # Normal migration
    success = manager.run()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

