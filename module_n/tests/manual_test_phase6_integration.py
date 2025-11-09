"""
Manual Test - Phase 6: Database Integration Workflow
Tests complete file ingestion workflow (upload → parse → save to DB → store file)
"""

import sys
from pathlib import Path
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from module_n.db import init_db, get_session
from module_n.db.models import FileIngest, FileExtraction, FileMetadata
from module_n.parsers.dxf_parser import DXFParser
from module_n.models.schemas import FileType, ProcessingStatus, ProcessingMode


def test_database_initialization():
    """Test database initialization"""
    print("\n" + "="*80)
    print("TESTING DATABASE INITIALIZATION")
    print("="*80)
    
    try:
        # Initialize database
        init_db()
        print("   ✅ Database initialized successfully")
        
        # Get a session
        session = get_session()
        print("   ✅ Database session created successfully")
        
        # Check tables exist
        from sqlalchemy import inspect
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
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_file_ingestion_workflow():
    """Test complete file ingestion workflow"""
    print("\n" + "="*80)
    print("TESTING FILE INGESTION WORKFLOW")
    print("="*80)
    
    # Use a real DXF file
    test_file = Path("data/files/1/base_plate_200x200_t10_4x18_on160.dxf")
    
    if not test_file.exists():
        print(f"   ⚠️  Test file not found: {test_file}")
        return True  # Skip test
    
    print(f"\n📄 Testing with: {test_file.name}")
    print(f"   Size: {test_file.stat().st_size:,} bytes")
    
    try:
        # Step 1: Parse the file
        print("\n   Step 1: Parsing file...")
        parser = DXFParser()
        metadata = parser.parse(str(test_file), test_file.name)
        print(f"      ✅ File parsed (confidence: {metadata.confidence_score:.2f})")
        
        # Step 2: Create database record
        print("\n   Step 2: Creating database record...")
        session = get_session()
        
        file_ingest = FileIngest(
            original_filename=test_file.name,
            stored_filename=f"test_{test_file.name}",
            file_path=str(test_file),
            file_size=test_file.stat().st_size,
            file_type=metadata.detected_type.value,
            detected_type=metadata.detected_type.value,
            confidence_score=metadata.confidence_score,
            status=ProcessingStatus.PENDING.value,
            processing_mode=ProcessingMode.AUTO.value,
            client_code=metadata.client_code,
            project_code=metadata.project_code,
            part_name=metadata.part_name,
            material=metadata.material,
            thickness_mm=metadata.thickness_mm,
            quantity=metadata.quantity,
            version=metadata.version
        )
        
        session.add(file_ingest)
        session.commit()
        print(f"      ✅ Database record created (ID: {file_ingest.id})")
        
        # Step 3: Create extraction record
        print("\n   Step 3: Creating extraction record...")
        file_extraction = FileExtraction(
            file_ingest_id=file_ingest.id,
            extraction_type="automatic",
            extracted_data=str(metadata.extracted),
            confidence_score=metadata.confidence_score
        )
        
        session.add(file_extraction)
        session.commit()
        print(f"      ✅ Extraction record created (ID: {file_extraction.id})")
        
        # Step 4: Create metadata record
        print("\n   Step 4: Creating metadata record...")
        file_metadata_record = FileMetadata(
            file_ingest_id=file_ingest.id,
            key="test_key",
            value="test_value",
            source="manual_test"
        )
        
        session.add(file_metadata_record)
        session.commit()
        print(f"      ✅ Metadata record created (ID: {file_metadata_record.id})")
        
        # Step 5: Store file
        print("\n   Step 5: Storing file...")
        storage_dir = Path("data/module_n_storage/test")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        stored_file = storage_dir / f"{file_ingest.id}_{test_file.name}"
        shutil.copy(test_file, stored_file)
        
        # Update database with storage path
        file_ingest.file_path = str(stored_file)
        file_ingest.status = ProcessingStatus.COMPLETED.value
        session.commit()
        print(f"      ✅ File stored at: {stored_file}")
        
        # Step 6: Query the record
        print("\n   Step 6: Querying database...")
        queried_file = session.query(FileIngest).filter_by(id=file_ingest.id).first()
        
        if queried_file:
            print(f"      ✅ Record found:")
            print(f"         ID: {queried_file.id}")
            print(f"         Filename: {queried_file.original_filename}")
            print(f"         Status: {queried_file.status}")
            print(f"         Extractions: {len(queried_file.extractions)}")
            print(f"         Metadata: {len(queried_file.file_metadata)}")
        else:
            print(f"      ❌ Record not found")
            return False
        
        # Step 7: Test relationships
        print("\n   Step 7: Testing relationships...")
        if len(queried_file.extractions) == 1:
            print(f"      ✅ Extraction relationship works")
        else:
            print(f"      ❌ Extraction relationship failed")
            return False
        
        if len(queried_file.file_metadata) == 1:
            print(f"      ✅ Metadata relationship works")
        else:
            print(f"      ❌ Metadata relationship failed")
            return False
        
        # Step 8: Test cascade delete
        print("\n   Step 8: Testing cascade delete...")
        session.delete(queried_file)
        session.commit()
        
        # Check if related records were deleted
        extraction_count = session.query(FileExtraction).filter_by(file_ingest_id=file_ingest.id).count()
        metadata_count = session.query(FileMetadata).filter_by(file_ingest_id=file_ingest.id).count()
        
        if extraction_count == 0 and metadata_count == 0:
            print(f"      ✅ Cascade delete works (related records deleted)")
        else:
            print(f"      ❌ Cascade delete failed (extraction: {extraction_count}, metadata: {metadata_count})")
            return False
        
        # Cleanup
        if stored_file.exists():
            stored_file.unlink()
        
        session.close()
        print("\n   ✅ Complete workflow test passed!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_operations():
    """Test various database query operations"""
    print("\n" + "="*80)
    print("TESTING QUERY OPERATIONS")
    print("="*80)
    
    try:
        session = get_session()
        
        # Create test records
        print("\n   Creating test records...")
        test_records = []
        for i in range(3):
            file_ingest = FileIngest(
                original_filename=f"test_file_{i}.dxf",
                stored_filename=f"stored_test_file_{i}.dxf",
                file_path=f"/test/path/test_file_{i}.dxf",
                file_size=1000 + i,
                file_type=FileType.DXF.value,
                detected_type=FileType.DXF.value,
                confidence_score=0.8 + (i * 0.05),
                status=ProcessingStatus.COMPLETED.value if i % 2 == 0 else ProcessingStatus.PENDING.value,
                processing_mode=ProcessingMode.AUTO.value,
                client_code=f"CL000{i}",
                project_code=f"PRJ{i}",
                part_name=f"Part {i}",
                material="Mild Steel",
                thickness_mm=5.0 + i,
                quantity=10 + i
            )
            session.add(file_ingest)
            test_records.append(file_ingest)
        
        session.commit()
        print(f"      ✅ Created {len(test_records)} test records")
        
        # Test 1: Query all
        print("\n   Test 1: Query all records...")
        all_records = session.query(FileIngest).all()
        print(f"      ✅ Found {len(all_records)} total records")
        
        # Test 2: Filter by status
        print("\n   Test 2: Filter by status...")
        complete_records = session.query(FileIngest).filter_by(status=ProcessingStatus.COMPLETED.value).all()
        print(f"      ✅ Found {len(complete_records)} COMPLETED records")
        
        # Test 3: Filter by client code
        print("\n   Test 3: Filter by client code...")
        client_records = session.query(FileIngest).filter_by(client_code="CL0001").all()
        print(f"      ✅ Found {len(client_records)} records for CL0001")
        
        # Test 4: Order by confidence score
        print("\n   Test 4: Order by confidence score...")
        ordered_records = session.query(FileIngest).order_by(FileIngest.confidence_score.desc()).all()
        if len(ordered_records) >= 2:
            if ordered_records[0].confidence_score >= ordered_records[1].confidence_score:
                print(f"      ✅ Ordering works correctly")
            else:
                print(f"      ❌ Ordering failed")
                return False
        
        # Test 5: Count records
        print("\n   Test 5: Count records...")
        count = session.query(FileIngest).count()
        print(f"      ✅ Total count: {count}")
        
        # Cleanup
        for record in test_records:
            session.delete(record)
        session.commit()
        session.close()
        
        print("\n   ✅ All query operations passed!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Query operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 6 tests"""
    print("\n" + "🔬 STARTING PHASE 6 COMPREHENSIVE TESTS".center(80, "="))
    
    results = []
    
    # Test database operations
    results.append(("Database Initialization", test_database_initialization()))
    results.append(("File Ingestion Workflow", test_file_ingestion_workflow()))
    results.append(("Query Operations", test_query_operations()))
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 6 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PHASE 6 TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

