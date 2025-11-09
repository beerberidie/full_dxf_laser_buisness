#!/usr/bin/env python3
"""
Test script to verify new document types work end-to-end.
This simulates what happens when a user uploads a document.
"""

import sqlite3
from datetime import datetime

def test_document_types():
    """Test inserting documents with new types."""
    
    print("\n" + "="*70)
    print("TESTING NEW DOCUMENT TYPES")
    print("="*70)
    
    conn = sqlite3.connect('data/laser_os.db')
    cursor = conn.cursor()
    
    # Get a valid project_id
    cursor.execute("SELECT id FROM projects LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("❌ No projects found in database")
        conn.close()
        return False
    
    project_id = result[0]
    print(f"\nUsing project_id: {project_id}")
    
    # Test data for new document types
    test_documents = [
        {
            'type': 'Other',
            'filename': 'test_contract.pdf',
            'path': 'data/documents/other/test_contract.pdf',
            'size': 50000
        },
        {
            'type': 'Image',
            'filename': 'test_photo.jpg',
            'path': 'data/documents/images/test_photo.jpg',
            'size': 150000
        }
    ]
    
    success_count = 0
    
    for doc in test_documents:
        print(f"\n{'='*70}")
        print(f"Testing document type: {doc['type']}")
        print(f"{'='*70}")
        
        try:
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert test document
            cursor.execute("""
                INSERT INTO project_documents 
                (project_id, document_type, original_filename, stored_filename, 
                 file_path, file_size, uploaded_by, upload_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                doc['type'],
                doc['filename'],
                doc['filename'],
                doc['path'],
                doc['size'],
                'test_user',
                datetime.now(),
                datetime.now()
            ))
            
            # Get the inserted ID
            doc_id = cursor.lastrowid
            
            print(f"✓ Successfully inserted document with ID: {doc_id}")
            print(f"  - Type: {doc['type']}")
            print(f"  - Filename: {doc['filename']}")
            print(f"  - Size: {doc['size']:,} bytes")
            
            # Verify it was inserted
            cursor.execute("""
                SELECT id, document_type, original_filename 
                FROM project_documents 
                WHERE id = ?
            """, (doc_id,))
            
            result = cursor.fetchone()
            if result:
                print(f"✓ Verified document in database:")
                print(f"  - ID: {result[0]}")
                print(f"  - Type: {result[1]}")
                print(f"  - Filename: {result[2]}")
                success_count += 1
            else:
                print(f"❌ Could not verify document in database")
            
            # Rollback (don't actually save test data)
            cursor.execute("ROLLBACK")
            print(f"✓ Test transaction rolled back (no data saved)")
            
        except sqlite3.IntegrityError as e:
            cursor.execute("ROLLBACK")
            print(f"❌ FAILED: {e}")
            print(f"   Document type '{doc['type']}' is NOT allowed by CHECK constraint")
        except Exception as e:
            cursor.execute("ROLLBACK")
            print(f"❌ ERROR: {e}")
    
    conn.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Tests passed: {success_count}/{len(test_documents)}")
    
    if success_count == len(test_documents):
        print("\n✅ ALL TESTS PASSED!")
        print("New document types 'Other' and 'Image' are working correctly.")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Migration may not have been applied correctly.")
        return False

if __name__ == '__main__':
    success = test_document_types()
    exit(0 if success else 1)

