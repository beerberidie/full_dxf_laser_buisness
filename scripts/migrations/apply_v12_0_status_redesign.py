#!/usr/bin/env python3
"""
Laser OS - Migration v12.0: Status System Redesign
Apply migration with backup and verification
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Database paths
DB_PATH = 'data/laser_os.db'
BACKUP_DIR = 'data/backups'
MIGRATION_FILE = 'migrations/schema_v12_0_status_system_redesign.sql'

def create_backup():
    """Create timestamped backup of database."""
    print("📦 Creating database backup...")
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{BACKUP_DIR}/laser_os_pre_v12_0_{timestamp}.db'
    
    # Copy database file
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def verify_database():
    """Verify database exists and is accessible."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database verified: {count} projects found")
        return True
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def get_pre_migration_stats(conn):
    """Get statistics before migration."""
    cursor = conn.cursor()
    
    stats = {}
    
    # Total projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    stats['total_projects'] = cursor.fetchone()[0]
    
    # Projects by status
    cursor.execute("SELECT status, COUNT(*) FROM projects GROUP BY status")
    stats['by_status'] = dict(cursor.fetchall())
    
    # Legacy status count
    cursor.execute("""
        SELECT COUNT(*) FROM projects 
        WHERE status IN ('Quote', 'Approved')
    """)
    stats['legacy_status_count'] = cursor.fetchone()[0]
    
    # Cancelled projects
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'Cancelled'")
    stats['cancelled_count'] = cursor.fetchone()[0]
    
    # Projects in Quote & Approval with quote_date
    cursor.execute("""
        SELECT COUNT(*) FROM projects 
        WHERE status IN ('Quote', 'Quote & Approval') 
        AND quote_date IS NOT NULL
    """)
    stats['quote_with_date_count'] = cursor.fetchone()[0]
    
    return stats

def get_post_migration_stats(conn):
    """Get statistics after migration."""
    cursor = conn.cursor()
    
    stats = {}
    
    # Total projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    stats['total_projects'] = cursor.fetchone()[0]
    
    # Projects by status
    cursor.execute("SELECT status, COUNT(*) FROM projects GROUP BY status")
    stats['by_status'] = dict(cursor.fetchall())
    
    # Legacy status count (should be 0)
    cursor.execute("""
        SELECT COUNT(*) FROM projects 
        WHERE status IN ('Quote', 'Approved')
    """)
    stats['legacy_status_count'] = cursor.fetchone()[0]
    
    # Projects with quote_expiry_date
    cursor.execute("SELECT COUNT(*) FROM projects WHERE quote_expiry_date IS NOT NULL")
    stats['with_expiry_date'] = cursor.fetchone()[0]
    
    # Projects that can be reinstated
    cursor.execute("SELECT COUNT(*) FROM projects WHERE can_reinstate = 1")
    stats['can_reinstate_count'] = cursor.fetchone()[0]
    
    # Projects on hold
    cursor.execute("SELECT COUNT(*) FROM projects WHERE on_hold = 1")
    stats['on_hold_count'] = cursor.fetchone()[0]
    
    # Verify new columns exist
    cursor.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cursor.fetchall()]
    stats['has_new_columns'] = all([
        'on_hold' in columns,
        'on_hold_reason' in columns,
        'on_hold_date' in columns,
        'quote_expiry_date' in columns,
        'quote_reminder_sent' in columns,
        'cancellation_reason' in columns,
        'can_reinstate' in columns
    ])
    
    return stats

def apply_migration():
    """Apply the migration SQL file."""
    print("\n🔄 Applying migration v12.0...")
    
    # Read migration file
    with open(MIGRATION_FILE, 'r') as f:
        migration_sql = f.read()
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get pre-migration stats
        print("\n📊 Pre-migration statistics:")
        pre_stats = get_pre_migration_stats(conn)
        print(f"   Total projects: {pre_stats['total_projects']}")
        print(f"   Projects by status:")
        for status, count in pre_stats['by_status'].items():
            print(f"      {status}: {count}")
        print(f"   Legacy statuses to migrate: {pre_stats['legacy_status_count']}")
        print(f"   Cancelled projects: {pre_stats['cancelled_count']}")
        print(f"   Quotes with dates: {pre_stats['quote_with_date_count']}")
        
        # Execute migration
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Get post-migration stats
        print("\n📊 Post-migration statistics:")
        post_stats = get_post_migration_stats(conn)
        print(f"   Total projects: {post_stats['total_projects']}")
        print(f"   Projects by status:")
        for status, count in post_stats['by_status'].items():
            print(f"      {status}: {count}")
        print(f"   Legacy statuses remaining: {post_stats['legacy_status_count']}")
        print(f"   Projects with expiry dates: {post_stats['with_expiry_date']}")
        print(f"   Projects can reinstate: {post_stats['can_reinstate_count']}")
        print(f"   Projects on hold: {post_stats['on_hold_count']}")
        print(f"   New columns added: {'✅ YES' if post_stats['has_new_columns'] else '❌ NO'}")
        
        # Verification
        print("\n✅ Verification:")
        
        # Check project count unchanged
        if pre_stats['total_projects'] == post_stats['total_projects']:
            print("   ✅ Project count unchanged")
        else:
            print(f"   ❌ Project count changed: {pre_stats['total_projects']} → {post_stats['total_projects']}")
            raise Exception("Project count mismatch!")
        
        # Check legacy statuses migrated
        if post_stats['legacy_status_count'] == 0:
            print("   ✅ All legacy statuses migrated")
        else:
            print(f"   ❌ {post_stats['legacy_status_count']} legacy statuses remain")
            raise Exception("Legacy status migration failed!")
        
        # Check new columns added
        if post_stats['has_new_columns']:
            print("   ✅ All new columns added")
        else:
            print("   ❌ Some new columns missing")
            raise Exception("Column creation failed!")
        
        # Check can_reinstate set for cancelled projects
        if post_stats['can_reinstate_count'] == pre_stats['cancelled_count']:
            print("   ✅ Cancelled projects marked as can_reinstate")
        else:
            print(f"   ⚠️  can_reinstate count ({post_stats['can_reinstate_count']}) != cancelled count ({pre_stats['cancelled_count']})")
        
        print("\n✅ Migration v12.0 applied successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main migration process."""
    print("=" * 80)
    print("Laser OS - Migration v12.0: Status System Redesign")
    print("=" * 80)
    
    # Step 1: Verify database
    if not verify_database():
        print("\n❌ Migration aborted: Database verification failed")
        return 1
    
    # Step 2: Create backup
    backup_path = create_backup()
    
    # Step 3: Apply migration
    success = apply_migration()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETE")
        print("=" * 80)
        print(f"\n📦 Backup saved: {backup_path}")
        print("\n📋 Next steps:")
        print("   1. Update Project model in app/models/business.py")
        print("   2. Create app/services/status_automation.py")
        print("   3. Create app/services/scheduler.py")
        print("   4. Update routes in app/routes/projects.py")
        print("   5. Update templates")
        print("   6. Run tests")
        print("\n🔄 To rollback: python scripts/migrations/rollback_v12_0.py")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ MIGRATION FAILED")
        print("=" * 80)
        print(f"\n📦 Restore from backup: {backup_path}")
        print("   cp {backup_path} {DB_PATH}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

