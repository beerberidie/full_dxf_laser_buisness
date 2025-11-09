"""
Phase 4 Database Testing Script
Tests all DXF file management database functionality
"""

from app import create_app, db
from app.models import DesignFile, Project, Client, ActivityLog
from datetime import datetime
import os
import tempfile

app = create_app('development')


def test_file_upload():
    """Test uploading design files to projects"""
    print("\n" + "="*80)
    print("TEST 1: FILE UPLOAD AND STORAGE")
    print("="*80)
    
    with app.app_context():
        # Get a test project
        project = Project.query.first()
        if not project:
            print("❌ No projects found. Please run Phase 2 tests first.")
            return False
        
        print(f"\n📁 Testing file upload for project: {project.project_code}")
        
        # Create test files
        test_files = [
            {
                'original_filename': 'bracket_design_v1.dxf',
                'stored_filename': '20251006_123456_abc123.dxf',
                'file_size': 1024 * 512,  # 512 KB
                'notes': 'Initial bracket design'
            },
            {
                'original_filename': 'panel_cutout.dxf',
                'stored_filename': '20251006_123457_def456.dxf',
                'file_size': 1024 * 1024 * 2,  # 2 MB
                'notes': 'Panel with cutouts for mounting'
            },
            {
                'original_filename': 'nameplate_final.dxf',
                'stored_filename': '20251006_123458_ghi789.dxf',
                'file_size': 1024 * 256,  # 256 KB
                'notes': None
            }
        ]
        
        created_files = []
        
        for i, file_data in enumerate(test_files, 1):
            # Create file path
            file_path = f"data/files/projects/{project.id}/{file_data['stored_filename']}"
            
            # Create design file record
            design_file = DesignFile(
                project_id=project.id,
                original_filename=file_data['original_filename'],
                stored_filename=file_data['stored_filename'],
                file_path=file_path,
                file_size=file_data['file_size'],
                file_type='dxf',
                uploaded_by='Test User',
                notes=file_data['notes']
            )
            
            db.session.add(design_file)
            db.session.commit()
            
            created_files.append(design_file)
            
            print(f"✅ Created File #{i}: {design_file.original_filename}")
            print(f"   - Size: {design_file.file_size_mb} MB")
            print(f"   - Stored as: {design_file.stored_filename}")
            print(f"   - Path: {design_file.file_path}")
        
        print(f"\n✅ Successfully created {len(created_files)} test files")
        return True


def test_file_retrieval():
    """Test retrieving files from database"""
    print("\n" + "="*80)
    print("TEST 2: FILE RETRIEVAL")
    print("="*80)
    
    with app.app_context():
        # Get all files
        files = DesignFile.query.all()
        
        print(f"\n📊 Total files in database: {len(files)}")
        
        if files:
            print("\n📄 File List:")
            for file in files:
                print(f"\n   File ID: {file.id}")
                print(f"   Filename: {file.original_filename}")
                print(f"   Project: {file.project.project_code}")
                print(f"   Size: {file.file_size_mb} MB ({file.file_size:,} bytes)")
                print(f"   Type: {file.file_type}")
                print(f"   Uploaded: {file.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Uploaded by: {file.uploaded_by}")
                if file.notes:
                    print(f"   Notes: {file.notes}")
        
        print("\n✅ File retrieval test passed")
        return True


def test_project_file_relationship():
    """Test project-file relationship"""
    print("\n" + "="*80)
    print("TEST 3: PROJECT-FILE RELATIONSHIP")
    print("="*80)
    
    with app.app_context():
        # Get a project with files
        project = Project.query.join(DesignFile).first()
        
        if not project:
            print("❌ No projects with files found")
            return False
        
        print(f"\n📁 Project: {project.project_code} - {project.name}")
        print(f"   Total files: {len(project.design_files)}")
        
        if project.design_files:
            print("\n   Files in this project:")
            for file in project.design_files:
                print(f"   - {file.original_filename} ({file.file_size_mb} MB)")
        
        print("\n✅ Project-file relationship test passed")
        return True


def test_file_metadata():
    """Test file metadata and properties"""
    print("\n" + "="*80)
    print("TEST 4: FILE METADATA AND PROPERTIES")
    print("="*80)
    
    with app.app_context():
        file = DesignFile.query.first()
        
        if not file:
            print("❌ No files found")
            return False
        
        print(f"\n📄 Testing metadata for: {file.original_filename}")
        
        # Test properties
        print(f"\n   Properties:")
        print(f"   - ID: {file.id}")
        print(f"   - Original filename: {file.original_filename}")
        print(f"   - Stored filename: {file.stored_filename}")
        print(f"   - File path: {file.file_path}")
        print(f"   - File size (bytes): {file.file_size:,}")
        print(f"   - File size (MB): {file.file_size_mb}")
        print(f"   - File type: {file.file_type}")
        print(f"   - File extension: {file.file_extension}")
        print(f"   - Upload date: {file.upload_date}")
        print(f"   - Uploaded by: {file.uploaded_by}")
        print(f"   - Created at: {file.created_at}")
        print(f"   - Updated at: {file.updated_at}")
        
        # Test to_dict method
        file_dict = file.to_dict()
        print(f"\n   to_dict() keys: {list(file_dict.keys())}")
        
        print("\n✅ File metadata test passed")
        return True


def test_activity_logging():
    """Test activity logging for file operations"""
    print("\n" + "="*80)
    print("TEST 5: ACTIVITY LOGGING")
    print("="*80)
    
    with app.app_context():
        # Get a file
        file = DesignFile.query.first()
        
        if not file:
            print("❌ No files found")
            return False
        
        print(f"\n📝 Creating activity logs for file: {file.original_filename}")
        
        # Create upload log
        upload_log = ActivityLog(
            entity_type='FILE',
            entity_id=file.id,
            action='UPLOADED',
            details=f'Uploaded file: {file.original_filename} ({file.file_size_mb} MB)',
            user='Test User'
        )
        db.session.add(upload_log)

        # Create download log
        download_log = ActivityLog(
            entity_type='FILE',
            entity_id=file.id,
            action='DOWNLOADED',
            details=f'Downloaded file: {file.original_filename}',
            user='Test User'
        )
        db.session.add(download_log)
        
        db.session.commit()
        
        # Retrieve logs
        logs = ActivityLog.query.filter_by(
            entity_type='FILE',
            entity_id=file.id
        ).order_by(ActivityLog.created_at.desc()).all()
        
        print(f"\n   Activity logs for file ID {file.id}:")
        for log in logs:
            print(f"   - {log.action}: {log.details} (by {log.user})")
        
        print(f"\n✅ Created {len(logs)} activity log entries")
        print("✅ Activity logging test passed")
        return True


def run_all_tests():
    """Run all Phase 4 database tests"""
    print("\n" + "="*80)
    print("PHASE 4: DXF FILE MANAGEMENT - DATABASE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests in sequence
        results = []
        results.append(("File Upload", test_file_upload()))
        results.append(("File Retrieval", test_file_retrieval()))
        results.append(("Project-File Relationship", test_project_file_relationship()))
        results.append(("File Metadata", test_file_metadata()))
        results.append(("Activity Logging", test_activity_logging()))
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print("\n" + "="*80)
        if passed == total:
            print("✅ ALL DATABASE TESTS PASSED!")
        else:
            print(f"⚠️  {passed}/{total} TESTS PASSED")
        print("="*80)
        print(f"Completed at: {datetime.now()}")
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Pass Rate: {(passed/total)*100:.0f}%")
        
        return passed == total
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST ERROR!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)

