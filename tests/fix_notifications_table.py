"""
Fix Notifications Table Schema

This script drops and recreates the notifications table with the correct schema
to match the Notification model.

Usage: python fix_notifications_table.py
"""

import sqlite3
import os
from datetime import datetime

def fix_notifications_table():
    """Drop and recreate notifications table with correct schema."""
    print("=" * 80)
    print("FIX NOTIFICATIONS TABLE SCHEMA")
    print("=" * 80)
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'laser_os.db')
    
    if not os.path.exists(db_path):
        print(f"\n❌ ERROR: Database not found at {db_path}")
        return False
    
    print(f"\nDatabase: {db_path}")
    
    # Create backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n📦 Creating backup: {backup_path}")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print("✅ Backup created successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to create backup: {str(e)}")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 80)
        print("STEP 1: Drop existing notifications table")
        print("=" * 80)
        
        cursor.execute("DROP TABLE IF EXISTS notifications")
        print("  ✓ Dropped notifications table")
        
        print("\n" + "=" * 80)
        print("STEP 2: Create notifications table with correct schema")
        print("=" * 80)
        
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
        print("  ✓ Created notifications table")
        
        print("\n" + "=" * 80)
        print("STEP 3: Create indexes")
        print("=" * 80)
        
        cursor.execute("CREATE INDEX ix_notifications_project_id ON notifications(project_id)")
        print("  ✓ Created index: ix_notifications_project_id")
        
        cursor.execute("CREATE INDEX ix_notifications_inventory_item_id ON notifications(inventory_item_id)")
        print("  ✓ Created index: ix_notifications_inventory_item_id")
        
        cursor.execute("CREATE INDEX ix_notifications_notif_type ON notifications(notif_type)")
        print("  ✓ Created index: ix_notifications_notif_type")
        
        cursor.execute("CREATE INDEX ix_notifications_resolved ON notifications(resolved)")
        print("  ✓ Created index: ix_notifications_resolved")
        
        cursor.execute("CREATE INDEX ix_notifications_created_at ON notifications(created_at)")
        print("  ✓ Created index: ix_notifications_created_at")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 80)
        print("✅ NOTIFICATIONS TABLE FIXED SUCCESSFULLY")
        print("=" * 80)
        print(f"\n📦 Backup saved at: {backup_path}")
        print("\nNext steps:")
        print("1. Restart the application")
        print("2. Test the notification system")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        print(f"\nTo rollback, restore from backup:")
        print(f"  copy {backup_path} {db_path}")
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    success = fix_notifications_table()
    exit(0 if success else 1)

