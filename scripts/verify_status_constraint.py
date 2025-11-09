"""
Verify that the project status CHECK constraint has been fixed.
"""

import sqlite3
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'data' / 'laser_os.db'

def main():
    print("=" * 80)
    print("VERIFYING PROJECT STATUS CHECK CONSTRAINT")
    print("=" * 80)
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Get the projects table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
        result = cursor.fetchone()
        
        if not result:
            print("\n❌ ERROR: projects table not found")
            return 1
        
        schema = result[0]
        
        print("\n📋 Projects Table Schema:")
        print("-" * 80)
        print(schema)
        print("-" * 80)
        
        # Check for new status values in the CHECK constraint
        new_statuses = [
            'Request',
            'Quote & Approval',
            'Approved (POP Received)',
            'Queued (Scheduled for Cutting)'
        ]
        
        legacy_statuses = [
            'Quote',
            'Approved',
            'In Progress',
            'Completed',
            'Cancelled'
        ]
        
        print("\n🔍 Checking for status values in CHECK constraint:")
        print("\nNew Phase 9 Statuses:")
        for status in new_statuses:
            if f"'{status}'" in schema:
                print(f"   ✅ {status}")
            else:
                print(f"   ❌ {status} - MISSING!")
        
        print("\nLegacy Statuses:")
        for status in legacy_statuses:
            if f"'{status}'" in schema:
                print(f"   ✅ {status}")
            else:
                print(f"   ❌ {status} - MISSING!")
        
        # Check if all statuses are present
        all_statuses = new_statuses + legacy_statuses
        all_present = all(f"'{status}'" in schema for status in all_statuses)
        
        if all_present:
            print("\n✅ SUCCESS: All status values are present in the CHECK constraint!")
        else:
            print("\n❌ ERROR: Some status values are missing from the CHECK constraint!")
            return 1
        
        # Count projects by status
        print("\n📊 Current Projects by Status:")
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM projects
            GROUP BY status
            ORDER BY count DESC
        """)
        
        status_counts = cursor.fetchall()
        
        if status_counts:
            for status, count in status_counts:
                print(f"   - {status}: {count} projects")
        else:
            print("   No projects found")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM projects")
        total = cursor.fetchone()[0]
        print(f"\n   Total: {total} projects")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 80)
        
        return 0
        
    except sqlite3.Error as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        conn.close()
        return 1

if __name__ == '__main__':
    exit(main())

