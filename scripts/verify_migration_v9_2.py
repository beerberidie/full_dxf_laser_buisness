#!/usr/bin/env python3
"""Verify the v9.2 migration was successful."""

import sqlite3

def verify():
    conn = sqlite3.connect('data/laser_os.db')
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("VERIFYING v9.2 MIGRATION")
    print("="*70)
    
    # Get table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='project_documents'")
    result = cursor.fetchone()
    
    if result:
        schema = result[0]
        print("\n✓ project_documents table exists")
        print("\nTable schema:")
        print(schema)
        
        # Check if new types are in the constraint
        if "'Other'" in schema and "'Image'" in schema:
            print("\n✓ CHECK constraint includes 'Other' and 'Image'")
            print("\n✅ MIGRATION SUCCESSFUL!")
        else:
            print("\n❌ CHECK constraint does NOT include new types")
            print("Migration may have failed.")
    else:
        print("\n❌ project_documents table not found!")
    
    # Count documents
    cursor.execute("SELECT COUNT(*) FROM project_documents")
    count = cursor.fetchone()[0]
    print(f"\nTotal documents in table: {count}")
    
    # Test inserting a document with 'Image' type (will rollback)
    print("\n" + "="*70)
    print("TESTING NEW DOCUMENT TYPES")
    print("="*70)
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            INSERT INTO project_documents 
            (project_id, document_type, original_filename, stored_filename, file_path, file_size, uploaded_by)
            VALUES (1, 'Image', 'test.png', 'test.png', '/test/test.png', 1000, 'test')
        """)
        print("✓ Successfully inserted test document with type 'Image'")
        cursor.execute("ROLLBACK")
        print("✓ Test transaction rolled back (no data was saved)")
        print("\n✅ NEW DOCUMENT TYPES ARE WORKING!")
    except sqlite3.IntegrityError as e:
        cursor.execute("ROLLBACK")
        print(f"❌ Failed to insert test document: {e}")
        print("Migration may have failed.")
    
    conn.close()

if __name__ == '__main__':
    verify()

