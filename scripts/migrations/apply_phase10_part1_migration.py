#!/usr/bin/env python3
"""
Phase 10 Part 1 Migration Script
Applies simple changes: material_thickness column addition

Usage:
    python apply_phase10_part1_migration.py

This script will:
1. Create a backup of the database
2. Apply the schema changes from migrations/schema_v10_phase1_simple_changes.sql
3. Verify the changes
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
DB_PATH = Path('data/laser_os.db')
BACKUP_DIR = Path('data/backups')
MIGRATION_FILE = Path('migrations/schema_v10_phase1_simple_changes.sql')

def create_backup():
    """Create a timestamped backup of the database."""
    if not DB_PATH.exists():
        print(f"❌ Error: Database not found at {DB_PATH}")
        sys.exit(1)
    
    # Create backup directory if it doesn't exist
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'laser_os_backup_v10_phase1_{timestamp}.db'
    
    print(f"📦 Creating backup: {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup created successfully")
    
    return backup_path

def verify_migration(conn):
    """Verify that the migration was applied correctly."""
    cursor = conn.cursor()
    
    print("\n🔍 Verifying migration...")
    
    # Check if material_thickness column exists
    cursor.execute("PRAGMA table_info(projects)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'material_thickness' in column_names:
        print("✅ material_thickness column added successfully")
    else:
        print("❌ material_thickness column not found!")
        return False
    
    # Check column type
    for col in columns:
        if col[1] == 'material_thickness':
            print(f"   Type: {col[2]}")
            print(f"   Nullable: {'Yes' if col[3] == 0 else 'No'}")
    
    return True

def apply_migration():
    """Apply the migration SQL file."""
    if not MIGRATION_FILE.exists():
        print(f"❌ Error: Migration file not found at {MIGRATION_FILE}")
        sys.exit(1)
    
    # Create backup first
    backup_path = create_backup()
    
    # Read migration SQL
    print(f"\n📄 Reading migration file: {MIGRATION_FILE}")
    with open(MIGRATION_FILE, 'r') as f:
        migration_sql = f.read()
    
    # Connect to database
    print(f"🔌 Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Execute migration
        print("⚙️  Applying migration...")

        # Remove comments and split by semicolons
        lines = migration_sql.split('\n')
        clean_lines = []
        for line in lines:
            # Remove comments
            if '--' in line:
                line = line[:line.index('--')]
            line = line.strip()
            if line:
                clean_lines.append(line)

        clean_sql = ' '.join(clean_lines)
        statements = [s.strip() for s in clean_sql.split(';') if s.strip()]

        print(f"   Found {len(statements)} SQL statement(s)")
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"   Executing statement {i}...")
                cursor.execute(statement)

        conn.commit()
        print("✅ Migration applied successfully")
        
        # Verify migration
        if verify_migration(conn):
            print("\n✅ Migration verification passed")
            print(f"\n🎉 Phase 10 Part 1 migration completed successfully!")
            print(f"📦 Backup saved at: {backup_path}")
        else:
            print("\n❌ Migration verification failed!")
            print(f"💡 To rollback, restore from backup:")
            print(f"   cp {backup_path} {DB_PATH}")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error applying migration: {e}")
        print(f"💡 Rolling back changes...")
        conn.rollback()
        print(f"💡 To restore from backup:")
        print(f"   cp {backup_path} {DB_PATH}")
        sys.exit(1)
    
    finally:
        conn.close()

def main():
    """Main entry point."""
    print("=" * 70)
    print("Phase 10 Part 1 Migration: Simple Changes")
    print("=" * 70)
    print("\nThis migration will:")
    print("  • Add material_thickness column to projects table")
    print("  • Create a backup before making changes")
    print("\nChanges:")
    print("  ✓ Add material_thickness NUMERIC(10,3) column")
    print("\n" + "=" * 70)
    
    # Confirm before proceeding
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Migration cancelled")
        sys.exit(0)
    
    apply_migration()

if __name__ == '__main__':
    main()

