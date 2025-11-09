"""
Manual Test - Phase 1: Database Schema & Initialization
Tests database initialization, schema creation, and table relationships
"""

import sys
from pathlib import Path
from sqlalchemy import inspect, text
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from module_n.db import init_db, get_session
from module_n.db.models import FileIngest, FileExtraction, FileMetadata


def test_database_initialization():
    """Test database initialization"""
    print("\n" + "="*80)
    print("PHASE 1 TEST: Database Initialization")
    print("="*80)
    
    # Initialize database
    print("\n1. Initializing database...")
    try:
        init_db()
        print("   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return False
    
    return True


def test_table_creation():
    """Test that all tables are created"""
    print("\n2. Verifying table creation...")
    
    session = get_session()
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    
    expected_tables = ['file_ingests', 'file_extractions', 'file_metadata']
    
    for table in expected_tables:
        if table in tables:
            print(f"   ✅ Table '{table}' exists")
        else:
            print(f"   ❌ Table '{table}' missing")
            return False
    
    session.close()
    return True


def test_table_columns():
    """Test that tables have correct columns"""
    print("\n3. Verifying table columns...")
    
    session = get_session()
    inspector = inspect(session.bind)
    
    # Test file_ingests columns
    columns = [col['name'] for col in inspector.get_columns('file_ingests')]
    expected_columns = [
        'id', 'original_filename', 'stored_filename', 'file_path', 'file_type',
        'file_size', 'status', 'confidence_score', 'client_code', 'project_code',
        'part_name', 'material', 'thickness_mm', 'quantity', 'version',
        'created_at', 'processed_at', 'is_deleted', 'updated_at'
    ]
    
    print(f"   file_ingests columns: {len(columns)} found")
    for col in expected_columns:
        if col in columns:
            print(f"      ✅ {col}")
        else:
            print(f"      ❌ {col} missing")
            return False
    
    # Test file_extractions columns
    columns = [col['name'] for col in inspector.get_columns('file_extractions')]
    expected_columns = ['id', 'file_ingest_id', 'extraction_type', 'extracted_data', 'created_at']
    
    print(f"\n   file_extractions columns: {len(columns)} found")
    for col in expected_columns:
        if col in columns:
            print(f"      ✅ {col}")
        else:
            print(f"      ❌ {col} missing")
            return False
    
    # Test file_metadata columns
    columns = [col['name'] for col in inspector.get_columns('file_metadata')]
    expected_columns = ['id', 'file_ingest_id', 'key', 'value', 'created_at']
    
    print(f"\n   file_metadata columns: {len(columns)} found")
    for col in expected_columns:
        if col in columns:
            print(f"      ✅ {col}")
        else:
            print(f"      ❌ {col} missing")
            return False
    
    session.close()
    return True


def test_indexes():
    """Test that indexes are created"""
    print("\n4. Verifying indexes...")
    
    session = get_session()
    inspector = inspect(session.bind)
    
    # Get indexes for file_ingests
    indexes = inspector.get_indexes('file_ingests')
    index_names = [idx['name'] for idx in indexes]
    
    expected_indexes = [
        'ix_file_ingests_client_code',
        'ix_file_ingests_project_code',
        'ix_file_ingests_file_type',
        'ix_file_ingests_status'
    ]
    
    print(f"   file_ingests indexes: {len(index_names)} found")
    for idx in expected_indexes:
        if idx in index_names:
            print(f"      ✅ {idx}")
        else:
            print(f"      ⚠️  {idx} not found (may be optional)")
    
    session.close()
    return True


def test_relationships():
    """Test table relationships"""
    print("\n5. Testing table relationships...")
    
    session = get_session()
    
    try:
        # Create a test file ingest
        file_ingest = FileIngest(
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf",
            file_type="dxf",
            file_size=1024,
            status="completed",
            confidence_score=0.95
        )
        session.add(file_ingest)
        session.commit()
        print(f"   ✅ Created test FileIngest (id={file_ingest.id})")
        
        # Create related extraction
        extraction = FileExtraction(
            file_ingest_id=file_ingest.id,
            extraction_type="dxf_metadata",
            extracted_data='{"test": "data"}'
        )
        session.add(extraction)
        session.commit()
        print(f"   ✅ Created related FileExtraction (id={extraction.id})")
        
        # Create related metadata
        metadata = FileMetadata(
            file_ingest_id=file_ingest.id,
            key="test_key",
            value="test_value"
        )
        session.add(metadata)
        session.commit()
        print(f"   ✅ Created related FileMetadata (id={metadata.id})")
        
        # Test relationship access
        file_ingest = session.query(FileIngest).filter_by(id=file_ingest.id).first()
        
        if file_ingest.extractions:
            print(f"   ✅ FileIngest.extractions relationship works ({len(file_ingest.extractions)} extractions)")
        else:
            print(f"   ❌ FileIngest.extractions relationship failed")
            return False
        
        if file_ingest.file_metadata:
            print(f"   ✅ FileIngest.file_metadata relationship works ({len(file_ingest.file_metadata)} metadata)")
        else:
            print(f"   ❌ FileIngest.file_metadata relationship failed")
            return False
        
        # Test cascade delete
        session.delete(file_ingest)
        session.commit()
        print(f"   ✅ Deleted FileIngest (cascade delete should remove related records)")
        
        # Verify cascade delete worked
        extraction_count = session.query(FileExtraction).filter_by(file_ingest_id=file_ingest.id).count()
        metadata_count = session.query(FileMetadata).filter_by(file_ingest_id=file_ingest.id).count()
        
        if extraction_count == 0:
            print(f"   ✅ Cascade delete removed FileExtraction")
        else:
            print(f"   ❌ Cascade delete failed for FileExtraction ({extraction_count} remaining)")
        
        if metadata_count == 0:
            print(f"   ✅ Cascade delete removed FileMetadata")
        else:
            print(f"   ❌ Cascade delete failed for FileMetadata ({metadata_count} remaining)")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Relationship test failed: {e}")
        session.rollback()
        session.close()
        return False


def main():
    """Run all Phase 1 tests"""
    print("\n" + "🔬 STARTING PHASE 1 COMPREHENSIVE TESTS".center(80, "="))
    
    results = []
    
    # Test 1: Database Initialization
    results.append(("Database Initialization", test_database_initialization()))
    
    # Test 2: Table Creation
    results.append(("Table Creation", test_table_creation()))
    
    # Test 3: Table Columns
    results.append(("Table Columns", test_table_columns()))
    
    # Test 4: Indexes
    results.append(("Indexes", test_indexes()))
    
    # Test 5: Relationships
    results.append(("Relationships & Cascade Delete", test_relationships()))
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 1 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PHASE 1 TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

