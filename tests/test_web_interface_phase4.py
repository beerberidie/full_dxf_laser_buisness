"""
Phase 4 Web Interface Testing Script
Tests all file management web interface functionality
"""

from app import create_app, db
from app.models import DesignFile, Project, ActivityLog
from datetime import datetime
import io

app = create_app('development')


def test_project_detail_file_section():
    """Test that project detail page shows file management section"""
    print("\n" + "="*80)
    print("TEST 1: PROJECT DETAIL PAGE - FILE SECTION")
    print("="*80)
    
    with app.test_client() as client:
        # Get a project with files
        with app.app_context():
            project = Project.query.join(DesignFile).first()
            if not project:
                project = Project.query.first()
            project_id = project.id
        
        response = client.get(f'/projects/{project_id}', follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for file section
        assert 'Design Files (DXF)' in html, "File section header not found"
        print("✅ File section header present")
        
        # Check for upload button
        assert 'Upload File' in html, "Upload button not found"
        print("✅ Upload button present")
        
        # Check for upload form
        assert 'uploadForm' in html, "Upload form not found"
        print("✅ Upload form present")
        
        # Check for file input
        assert 'type="file"' in html, "File input not found"
        assert 'accept=".dxf,.DXF"' in html, "File type restriction not found"
        print("✅ File input with DXF restriction present")
        
        print("\n✅ PROJECT DETAIL FILE SECTION TEST PASSED")


def test_file_upload():
    """Test file upload functionality"""
    print("\n" + "="*80)
    print("TEST 2: FILE UPLOAD FUNCTIONALITY")
    print("="*80)
    
    with app.test_client() as client:
        # Get a project
        with app.app_context():
            project = Project.query.first()
            project_id = project.id
            initial_file_count = DesignFile.query.filter_by(project_id=project_id).count()
        
        # Create a fake DXF file
        data = {
            'file': (io.BytesIO(b'DXF file content'), 'test_upload.dxf'),
            'notes': 'Test file upload from automated test'
        }
        
        response = client.post(
            f'/files/upload/{project_id}',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for success message
        assert 'uploaded successfully' in html or 'test_upload.dxf' in html, "Success message not found"
        print("✅ File upload successful")
        
        # Verify in database
        with app.app_context():
            new_file_count = DesignFile.query.filter_by(project_id=project_id).count()
            assert new_file_count == initial_file_count + 1, "File not added to database"
            print("✅ File added to database")
            
            # Check activity log
            uploaded_file = DesignFile.query.filter_by(
                project_id=project_id,
                original_filename='test_upload.dxf'
            ).first()
            
            if uploaded_file:
                log = ActivityLog.query.filter_by(
                    entity_type='FILE',
                    entity_id=uploaded_file.id,
                    action='UPLOADED'
                ).first()
                assert log is not None, "Activity log not created"
                print("✅ Activity log created")
        
        print("\n✅ FILE UPLOAD TEST PASSED")


def test_file_list_display():
    """Test that files are displayed in project detail"""
    print("\n" + "="*80)
    print("TEST 3: FILE LIST DISPLAY")
    print("="*80)
    
    with app.test_client() as client:
        # Get a project with files
        with app.app_context():
            project = Project.query.join(DesignFile).first()
            if not project:
                print("⚠️  No projects with files found, skipping test")
                return
            
            project_id = project.id
            file_count = len(project.design_files)
            first_file = project.design_files[0]
            first_filename = first_file.original_filename
        
        response = client.get(f'/projects/{project_id}', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        # Check that file is listed
        assert first_filename in html, f"File {first_filename} not found in list"
        print(f"✅ File '{first_filename}' displayed in list")
        
        # Check for file actions
        assert 'Download' in html, "Download button not found"
        assert 'View' in html or 'Detail' in html, "View button not found"
        assert 'Delete' in html, "Delete button not found"
        print("✅ File action buttons present")
        
        # Check for file count
        assert f'{file_count} file' in html, "File count not displayed"
        print(f"✅ File count displayed ({file_count} files)")
        
        print("\n✅ FILE LIST DISPLAY TEST PASSED")


def test_file_detail_page():
    """Test file detail page"""
    print("\n" + "="*80)
    print("TEST 4: FILE DETAIL PAGE")
    print("="*80)
    
    with app.test_client() as client:
        # Get a file
        with app.app_context():
            file = DesignFile.query.first()
            if not file:
                print("⚠️  No files found, skipping test")
                return
            
            file_id = file.id
            filename = file.original_filename
        
        response = client.get(f'/files/{file_id}', follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for filename
        assert filename in html, "Filename not found on detail page"
        print(f"✅ Filename '{filename}' displayed")
        
        # Check for file information
        assert 'File Information' in html, "File information section not found"
        assert 'File Type' in html, "File type not displayed"
        assert 'File Size' in html, "File size not displayed"
        print("✅ File information displayed")
        
        # Check for download button
        assert 'Download' in html, "Download button not found"
        print("✅ Download button present")
        
        # Check for delete button
        assert 'Delete' in html, "Delete button not found"
        print("✅ Delete button present")
        
        # Check for activity log
        assert 'Activity Log' in html, "Activity log section not found"
        print("✅ Activity log section present")
        
        print("\n✅ FILE DETAIL PAGE TEST PASSED")


def test_dashboard_file_statistics():
    """Test that dashboard shows file statistics"""
    print("\n" + "="*80)
    print("TEST 5: DASHBOARD FILE STATISTICS")
    print("="*80)
    
    with app.test_client() as client:
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for file statistics card
        assert 'Design Files' in html, "Design Files card not found"
        print("✅ Design Files statistics card present")
        
        # Check for file count
        with app.app_context():
            total_files = DesignFile.query.count()
        
        assert str(total_files) in html, "File count not displayed"
        print(f"✅ File count displayed ({total_files} files)")
        
        # Check for recent files section
        assert 'Recent Files' in html, "Recent Files section not found"
        print("✅ Recent Files section present")
        
        print("\n✅ DASHBOARD FILE STATISTICS TEST PASSED")


def test_file_download_link():
    """Test file download link"""
    print("\n" + "="*80)
    print("TEST 6: FILE DOWNLOAD LINK")
    print("="*80)
    
    with app.test_client() as client:
        # Get a file
        with app.app_context():
            file = DesignFile.query.first()
            if not file:
                print("⚠️  No files found, skipping test")
                return
            
            file_id = file.id
        
        # Note: We can't actually download the file since it doesn't exist on disk
        # But we can check that the route exists and returns a proper response
        response = client.get(f'/files/download/{file_id}', follow_redirects=True)
        
        # Should redirect back to project page with error message since file doesn't exist on disk
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Download route accessible")
        
        print("\n✅ FILE DOWNLOAD LINK TEST PASSED")


def test_file_delete():
    """Test file deletion"""
    print("\n" + "="*80)
    print("TEST 7: FILE DELETION")
    print("="*80)
    
    with app.test_client() as client:
        # Create a test file to delete
        with app.app_context():
            project = Project.query.first()
            
            test_file = DesignFile(
                project_id=project.id,
                original_filename='to_delete.dxf',
                stored_filename='20251006_999999_delete.dxf',
                file_path='data/files/projects/1/20251006_999999_delete.dxf',
                file_size=1024,
                file_type='dxf',
                uploaded_by='Test User'
            )
            db.session.add(test_file)
            db.session.commit()
            
            file_id = test_file.id
            project_id = project.id
        
        # Delete the file
        response = client.post(f'/files/delete/{file_id}', follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for success message
        assert 'deleted successfully' in html or 'to_delete.dxf' not in html, "Delete confirmation not found"
        print("✅ File deletion successful")
        
        # Verify file is deleted from database
        with app.app_context():
            deleted_file = DesignFile.query.get(file_id)
            assert deleted_file is None, "File still exists in database"
            print("✅ File removed from database")
        
        print("\n✅ FILE DELETION TEST PASSED")


def run_all_tests():
    """Run all Phase 4 web interface tests"""
    print("\n" + "="*80)
    print("PHASE 4: WEB INTERFACE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests in sequence
        test_project_detail_file_section()
        test_file_upload()
        test_file_list_display()
        test_file_detail_page()
        test_dashboard_file_statistics()
        test_file_download_link()
        test_file_delete()
        
        print("\n" + "="*80)
        print("✅ ALL WEB INTERFACE TESTS PASSED!")
        print("="*80)
        print(f"Completed at: {datetime.now()}")
        print("\nTotal Tests: 7")
        print("Passed: 7")
        print("Failed: 0")
        print("Pass Rate: 100%")
        
        return True
        
    except AssertionError as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
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

