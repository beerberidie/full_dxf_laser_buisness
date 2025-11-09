#!/usr/bin/env python3
"""
Quick database status check
Shows current record counts and database state
"""

import sqlite3
import os


def main():
    """Check database status."""
    print("="*80)
    print("LASER OS - DATABASE STATUS CHECK")
    print("="*80)
    
    db_path = 'data/laser_os.db'
    
    if not os.path.exists(db_path):
        print(f"\n❌ Database not found: {db_path}")
        return 1
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get database file size
        db_size = os.path.getsize(db_path)
        print(f"\n📁 Database: {db_path}")
        print(f"📊 Size: {db_size:,} bytes ({db_size / 1024:.2f} KB)")
        
        # Get record counts
        print("\n📊 Current Record Counts:")
        print("-" * 80)
        
        tables = {
            'Clients': 'SELECT COUNT(*) FROM clients',
            'Projects': 'SELECT COUNT(*) FROM projects',
            'Design Files': 'SELECT COUNT(*) FROM design_files',
            'Project Documents': 'SELECT COUNT(*) FROM project_documents',
            'Communications': 'SELECT COUNT(*) FROM communications',
            'Communication Attachments': 'SELECT COUNT(*) FROM communication_attachments'
        }
        
        total_records = 0
        for table_name, query in tables.items():
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                total_records += count
                status = "✅" if count > 0 else "⚪"
                print(f"{status} {table_name:.<30} {count:>6}")
            except sqlite3.OperationalError:
                print(f"⚠️  {table_name:.<30} N/A (table not found)")
        
        print("-" * 80)
        print(f"   {'TOTAL RECORDS':.<30} {total_records:>6}")
        
        # Get some sample data if available
        if total_records > 0:
            print("\n📋 Sample Data:")
            print("-" * 80)
            
            # Sample clients
            cursor.execute('SELECT client_code, name FROM clients LIMIT 3')
            clients = cursor.fetchall()
            if clients:
                print("\nClients:")
                for code, name in clients:
                    print(f"   • {code}: {name}")
            
            # Sample projects
            cursor.execute('SELECT project_code, name, status FROM projects LIMIT 3')
            projects = cursor.fetchall()
            if projects:
                print("\nProjects:")
                for code, name, status in projects:
                    print(f"   • {code}: {name} ({status})")
        
        # Database state
        print("\n" + "="*80)
        if total_records == 0:
            print("✅ DATABASE IS EMPTY - Ready for fresh data import")
        else:
            print(f"📊 DATABASE CONTAINS {total_records} RECORDS")
        print("="*80)
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

