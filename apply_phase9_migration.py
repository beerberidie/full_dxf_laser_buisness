#!/usr/bin/env python3
"""
Laser OS - Phase 9 Migration Script
====================================
Applies database schema updates for project enhancements and communications module.

This script:
1. Backs up the existing database
2. Applies the v9.0 schema migration
3. Validates the migration was successful
4. Provides rollback capability if needed

Usage:
    python apply_phase9_migration.py
    python apply_phase9_migration.py --rollback  # To restore from backup
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys
import argparse


class MigrationManager:
    """Manages database migration for Phase 9."""
    
    def __init__(self, db_path='data/laser_os.db'):
        self.db_path = db_path
        self.backup_path = None
        self.migration_file = 'migrations/schema_v9_project_enhancements.sql'
        
    def create_backup(self):
        """Create a backup of the database before migration."""
        if not os.path.exists(self.db_path):
            print(f"❌ Error: Database not found at {self.db_path}")
            return False
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = f"{self.db_path}.backup_v8_to_v9_{timestamp}"
        
        try:
            shutil.copy2(self.db_path, self.backup_path)
            print(f"✓ Database backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def get_current_schema_version(self):
        """Get the current schema version from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 'Unknown'
        except Exception as e:
            print(f"⚠️  Warning: Could not read schema version: {e}")
            return 'Unknown'
    
    def validate_prerequisites(self):
        """Validate that all prerequisites are met before migration."""
        print("\n📋 Validating prerequisites...")
        
        # Check database exists
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at {self.db_path}")
            return False
        
        # Check migration file exists
        if not os.path.exists(self.migration_file):
            print(f"❌ Migration file not found at {self.migration_file}")
            return False
        
        # Check current schema version
        current_version = self.get_current_schema_version()
        print(f"   Current schema version: {current_version}")
        
        if current_version != 'Unknown' and current_version >= '9.0':
            print(f"⚠️  Warning: Schema version {current_version} is already at or above v9.0")
            response = input("   Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # Check required tables exist
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
            if not cursor.fetchone():
                print("❌ Required table 'projects' not found")
                conn.close()
                return False
            conn.close()
        except Exception as e:
            print(f"❌ Error validating database: {e}")
            return False
        
        print("✓ All prerequisites validated")
        return True
    
    def apply_migration(self):
        """Apply the migration SQL script."""
        print("\n🔄 Applying migration...")
        
        try:
            # Read migration SQL
            with open(self.migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Connect and execute
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute the migration script
            cursor.executescript(migration_sql)
            
            conn.commit()
            conn.close()
            
            print("✓ Migration SQL executed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    def validate_migration(self):
        """Validate that the migration was applied correctly."""
        print("\n🔍 Validating migration...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check schema version updated
            cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
            version = cursor.fetchone()[0]
            if version != '9.0':
                print(f"❌ Schema version not updated correctly (found: {version})")
                conn.close()
                return False
            print(f"   ✓ Schema version: {version}")
            
            # Check new tables exist
            new_tables = ['project_documents', 'communications', 'communication_attachments']
            for table in new_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    print(f"❌ New table '{table}' not found")
                    conn.close()
                    return False
                print(f"   ✓ Table '{table}' created")
            
            # Check new columns in projects table
            cursor.execute("PRAGMA table_info(projects)")
            columns = [row[1] for row in cursor.fetchall()]
            
            new_columns = [
                'material_type', 'material_quantity_sheets', 'parts_quantity',
                'estimated_cut_time', 'number_of_bins', 'drawing_creation_time',
                'pop_received', 'pop_received_date', 'pop_deadline',
                'client_notified', 'client_notified_date',
                'delivery_confirmed', 'delivery_confirmed_date',
                'scheduled_cut_date'
            ]
            
            missing_columns = [col for col in new_columns if col not in columns]
            if missing_columns:
                print(f"❌ Missing columns in projects table: {missing_columns}")
                conn.close()
                return False
            
            print(f"   ✓ All {len(new_columns)} new columns added to projects table")
            
            # Check indexes created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_projects_material_type'")
            if cursor.fetchone():
                print(f"   ✓ Indexes created successfully")
            
            conn.close()
            print("✓ Migration validation successful")
            return True
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
    
    def rollback(self):
        """Restore database from backup."""
        if not self.backup_path or not os.path.exists(self.backup_path):
            print("❌ No backup file found for rollback")
            return False
        
        try:
            shutil.copy2(self.backup_path, self.db_path)
            print(f"✓ Database restored from backup: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def run(self):
        """Execute the complete migration process."""
        print("=" * 70)
        print("Laser OS - Phase 9 Migration")
        print("Project Enhancements & Communications Module")
        print("=" * 70)
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            print("\n❌ Migration aborted: Prerequisites not met")
            return False
        
        # Step 2: Create backup
        if not self.create_backup():
            print("\n❌ Migration aborted: Could not create backup")
            return False
        
        # Step 3: Apply migration
        if not self.apply_migration():
            print("\n❌ Migration failed!")
            print(f"   Your original database is safe at: {self.backup_path}")
            response = input("\n   Attempt rollback? (y/N): ")
            if response.lower() == 'y':
                self.rollback()
            return False
        
        # Step 4: Validate migration
        if not self.validate_migration():
            print("\n⚠️  Migration applied but validation failed!")
            print(f"   Your original database backup: {self.backup_path}")
            response = input("\n   Attempt rollback? (y/N): ")
            if response.lower() == 'y':
                self.rollback()
            return False
        
        # Success!
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Database upgraded to schema v9.0")
        print(f"Backup saved at: {self.backup_path}")
        print("\nNew features available:")
        print("  • Enhanced project tracking (material type, quantities, cut times)")
        print("  • POP (Proof of Payment) management with 3-day deadline tracking")
        print("  • Client notification and delivery confirmation toggles")
        print("  • Project documents (Quote, Invoice, POP, Delivery Note)")
        print("  • Communications module (Email, WhatsApp, Notifications)")
        print("\nNext steps:")
        print("  1. Restart your application")
        print("  2. Test the new features")
        print("  3. Keep the backup file until you're confident everything works")
        print("=" * 70)
        
        return True


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description='Apply Phase 9 database migration')
    parser.add_argument('--rollback', help='Rollback to most recent backup', action='store_true')
    parser.add_argument('--db', help='Database path (default: data/laser_os.db)', default='data/laser_os.db')
    args = parser.parse_args()
    
    manager = MigrationManager(db_path=args.db)
    
    if args.rollback:
        print("🔄 Rollback mode")
        # Find most recent backup
        backup_files = [f for f in os.listdir('data') if f.startswith('laser_os.db.backup_v8_to_v9_')]
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

