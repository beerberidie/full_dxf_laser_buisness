"""
Production Automation Database Migration Script

This script adds the new models and fields required for the Production Automation system.

Run this script with: python migrations/production_automation_migration.py
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'laser_os.db')

def run_migration():
    """Run the production automation migration."""
    print("=" * 80)
    print("PRODUCTION AUTOMATION DATABASE MIGRATION")
    print("=" * 80)
    print(f"\nDatabase: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ ERROR: Database not found at {DB_PATH}")
        return False
    
    # Backup database first
    backup_path = DB_PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n📦 Creating backup: {backup_path}")
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print("✅ Backup created successfully")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 80)
        print("STEP 1: Modify User table")
        print("=" * 80)
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' not in columns:
            print("  Adding column: role")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'operator' NOT NULL")
        else:
            print("  ✓ Column 'role' already exists")
        
        if 'is_active_operator' not in columns:
            print("  Adding column: is_active_operator")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active_operator BOOLEAN DEFAULT 1 NOT NULL")
        else:
            print("  ✓ Column 'is_active_operator' already exists")
        
        if 'display_name' not in columns:
            print("  Adding column: display_name")
            cursor.execute("ALTER TABLE users ADD COLUMN display_name VARCHAR(120)")
        else:
            print("  ✓ Column 'display_name' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 2: Modify Project table")
        print("=" * 80)
        
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'stage' not in columns:
            print("  Adding column: stage")
            cursor.execute("ALTER TABLE projects ADD COLUMN stage VARCHAR(50)")
        else:
            print("  ✓ Column 'stage' already exists")
        
        if 'stage_last_updated' not in columns:
            print("  Adding column: stage_last_updated")
            cursor.execute("ALTER TABLE projects ADD COLUMN stage_last_updated DATETIME")
        else:
            print("  ✓ Column 'stage_last_updated' already exists")

        if 'thickness_mm' not in columns:
            print("  Adding column: thickness_mm")
            cursor.execute("ALTER TABLE projects ADD COLUMN thickness_mm VARCHAR(10)")
        else:
            print("  ✓ Column 'thickness_mm' already exists")

        if 'sheet_size' not in columns:
            print("  Adding column: sheet_size")
            cursor.execute("ALTER TABLE projects ADD COLUMN sheet_size VARCHAR(32)")
        else:
            print("  ✓ Column 'sheet_size' already exists")

        if 'sheets_required' not in columns:
            print("  Adding column: sheets_required")
            cursor.execute("ALTER TABLE projects ADD COLUMN sheets_required INTEGER DEFAULT 0")
        else:
            print("  ✓ Column 'sheets_required' already exists")

        if 'target_complete_date' not in columns:
            print("  Adding column: target_complete_date")
            cursor.execute("ALTER TABLE projects ADD COLUMN target_complete_date DATETIME")
        else:
            print("  ✓ Column 'target_complete_date' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 3: Modify LaserRun table")
        print("=" * 80)
        
        cursor.execute("PRAGMA table_info(laser_runs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'started_at' not in columns:
            print("  Adding column: started_at")
            cursor.execute("ALTER TABLE laser_runs ADD COLUMN started_at DATETIME")
        else:
            print("  ✓ Column 'started_at' already exists")
        
        if 'ended_at' not in columns:
            print("  Adding column: ended_at")
            cursor.execute("ALTER TABLE laser_runs ADD COLUMN ended_at DATETIME")
        else:
            print("  ✓ Column 'ended_at' already exists")
        
        if 'sheets_used' not in columns:
            print("  Adding column: sheets_used")
            cursor.execute("ALTER TABLE laser_runs ADD COLUMN sheets_used INTEGER")
        else:
            print("  ✓ Column 'sheets_used' already exists")
        
        if 'sheet_size' not in columns:
            print("  Adding column: sheet_size")
            cursor.execute("ALTER TABLE laser_runs ADD COLUMN sheet_size VARCHAR(20)")
        else:
            print("  ✓ Column 'sheet_size' already exists")
        
        if 'thickness_mm' not in columns:
            print("  Adding column: thickness_mm")
            cursor.execute("ALTER TABLE laser_runs ADD COLUMN thickness_mm VARCHAR(10)")
        else:
            print("  ✓ Column 'thickness_mm' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 4: Modify InventoryItem table")
        print("=" * 80)
        
        cursor.execute("PRAGMA table_info(inventory_items)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'sheet_size' not in columns:
            print("  Adding column: sheet_size")
            cursor.execute("ALTER TABLE inventory_items ADD COLUMN sheet_size VARCHAR(20)")
        else:
            print("  ✓ Column 'sheet_size' already exists")
        
        if 'thickness_mm' not in columns:
            print("  Adding column: thickness_mm")
            cursor.execute("ALTER TABLE inventory_items ADD COLUMN thickness_mm VARCHAR(10)")
        else:
            print("  ✓ Column 'thickness_mm' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 5: Create Notification table")
        print("=" * 80)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        if not cursor.fetchone():
            print("  Creating table: notifications")
            cursor.execute("""
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    inventory_item_id INTEGER,
                    notif_type VARCHAR(50) NOT NULL,
                    message VARCHAR(500) NOT NULL,
                    resolved BOOLEAN DEFAULT 0 NOT NULL,
                    auto_cleared BOOLEAN DEFAULT 0 NOT NULL,
                    created_at DATETIME NOT NULL,
                    resolved_at DATETIME,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX ix_notifications_project_id ON notifications(project_id)")
            cursor.execute("CREATE INDEX ix_notifications_inventory_item_id ON notifications(inventory_item_id)")
            cursor.execute("CREATE INDEX ix_notifications_notif_type ON notifications(notif_type)")
            cursor.execute("CREATE INDEX ix_notifications_resolved ON notifications(resolved)")
            cursor.execute("CREATE INDEX ix_notifications_created_at ON notifications(created_at)")
        else:
            print("  ✓ Table 'notifications' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 6: Create DailyReport table")
        print("=" * 80)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_reports'")
        if not cursor.fetchone():
            print("  Creating table: daily_reports")
            cursor.execute("""
                CREATE TABLE daily_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date DATE NOT NULL UNIQUE,
                    generated_at DATETIME NOT NULL,
                    runs_count INTEGER DEFAULT 0 NOT NULL,
                    total_sheets_used INTEGER DEFAULT 0 NOT NULL,
                    total_parts_produced INTEGER DEFAULT 0 NOT NULL,
                    total_cut_time_minutes FLOAT DEFAULT 0.0 NOT NULL,
                    report_body TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX ix_daily_reports_report_date ON daily_reports(report_date)")
        else:
            print("  ✓ Table 'daily_reports' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 7: Create OutboundDraft table")
        print("=" * 80)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='outbound_drafts'")
        if not cursor.fetchone():
            print("  Creating table: outbound_drafts")
            cursor.execute("""
                CREATE TABLE outbound_drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    project_id INTEGER,
                    channel_hint VARCHAR(20),
                    body_text TEXT NOT NULL,
                    sent BOOLEAN DEFAULT 0 NOT NULL,
                    created_at DATETIME NOT NULL,
                    sent_at DATETIME,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """)
            cursor.execute("CREATE INDEX ix_outbound_drafts_sent ON outbound_drafts(sent)")
        else:
            print("  ✓ Table 'outbound_drafts' already exists")
        
        print("\n" + "=" * 80)
        print("STEP 8: Create ExtraOperator table")
        print("=" * 80)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extra_operators'")
        if not cursor.fetchone():
            print("  Creating table: extra_operators")
            cursor.execute("""
                CREATE TABLE extra_operators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(120) NOT NULL,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at DATETIME NOT NULL
                )
            """)
        else:
            print("  ✓ Table 'extra_operators' already exists")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\n📦 Backup saved at: {backup_path}")
        print("\nNext steps:")
        print("1. Re-enable the scheduler in app/__init__.py")
        print("2. Restart the application")
        print("3. Test the new features")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {str(e)}")
        conn.rollback()
        print(f"\n📦 Restore from backup if needed: {backup_path}")
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)

