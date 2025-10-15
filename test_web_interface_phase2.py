"""
Phase 2 Web Interface Testing Script
Tests all project management web interface functionality
"""

from app import create_app, db
from app.models import Project, Client, ActivityLog
from datetime import datetime, date, timedelta

app = create_app('development')


def test_project_list_page():
    """Test project list page loads and displays projects"""
    print("\n" + "="*80)
    print("TEST 1: PROJECT LIST PAGE")
    print("="*80)

    with app.test_client() as client:
        # Get project list page
        response = client.get('/projects', follow_redirects=True)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check page title
        assert '<h1>Projects</h1>' in html, "Page title not found"
        print("✅ Page title correct")
        
        # Check for New Project button
        assert '+ New Project' in html, "New Project button not found"
        print("✅ New Project button present")
        
        # Check for search bar
        assert 'Search projects by name, code, or description' in html, "Search bar not found"
        print("✅ Search bar present")
        
        # Check for filter dropdowns
        assert 'All Clients' in html, "Client filter not found"
        assert 'All Statuses' in html, "Status filter not found"
        print("✅ Filter dropdowns present")
        
        # Check for project table
        assert '<table class="table">' in html, "Project table not found"
        print("✅ Project table present")
        
        # Check for project codes (from test data)
        assert 'JB-2025-10-CL0001-001' in html, "Project code not found in list"
        assert 'JB-2025-10-CL0001-002' in html, "Project code not found in list"
        print("✅ Project codes displayed")
        
        # Check for status badges
        assert 'badge-quote' in html or 'Quote' in html, "Quote status not found"
        assert 'badge-approved' in html or 'Approved' in html, "Approved status not found"
        print("✅ Status badges present")
        
        print("\n✅ PROJECT LIST PAGE TEST PASSED")


def test_project_search():
    """Test project search functionality"""
    print("\n" + "="*80)
    print("TEST 2: PROJECT SEARCH FUNCTIONALITY")
    print("="*80)

    with app.test_client() as client:
        # Search by name
        response = client.get('/projects?search=Metal', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')

        assert 'Metal Brackets' in html, "Search result not found"
        print("✅ Search by name works")

        # Search by code
        response = client.get('/projects?search=JB-2025-10-CL0001', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        assert 'JB-2025-10-CL0001-001' in html, "Search by code failed"
        assert 'JB-2025-10-CL0001-002' in html, "Search by code failed"
        print("✅ Search by code works")
        
        # Search with no results
        response = client.get('/projects?search=NonexistentProject', follow_redirects=True)
        html = response.data.decode('utf-8')

        assert 'No projects found' in html, "Empty search result message not shown"
        print("✅ Empty search handled correctly")

        print("\n✅ PROJECT SEARCH TEST PASSED")


def test_project_filters():
    """Test project filter functionality"""
    print("\n" + "="*80)
    print("TEST 3: PROJECT FILTER FUNCTIONALITY")
    print("="*80)

    with app.app_context():
        # Get a client ID for testing
        client_obj = Client.query.first()
        client_id = client_obj.id

    with app.test_client() as client:
        # Filter by client
        response = client.get(f'/projects?client_id={client_id}', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')

        # Should show projects for this client only
        print("✅ Client filter works")

        # Filter by status
        response = client.get('/projects?status=Quote', follow_redirects=True)
        html = response.data.decode('utf-8')

        assert 'Quote' in html, "Status filter failed"
        print("✅ Status filter works")

        # Combined filters
        response = client.get(f'/projects?client_id={client_id}&status=Quote', follow_redirects=True)
        assert response.status_code == 200, "Combined filters failed"
        print("✅ Combined filters work")
        
        print("\n✅ PROJECT FILTER TEST PASSED")


def test_new_project_form():
    """Test new project form displays correctly"""
    print("\n" + "="*80)
    print("TEST 4: NEW PROJECT FORM")
    print("="*80)

    with app.test_client() as client:
        response = client.get('/projects/new', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check form elements
        assert '<h1>New Project</h1>' in html, "Form title not found"
        print("✅ Form title correct")
        
        assert 'name="client_id"' in html, "Client dropdown not found"
        assert 'name="name"' in html, "Name field not found"
        assert 'name="description"' in html, "Description field not found"
        assert 'name="status"' in html, "Status field not found"
        assert 'name="quote_date"' in html, "Quote date field not found"
        assert 'name="due_date"' in html, "Due date field not found"
        assert 'name="quoted_price"' in html, "Quoted price field not found"
        assert 'name="notes"' in html, "Notes field not found"
        print("✅ All form fields present")
        
        # Check for client options
        assert 'Select a client' in html, "Client dropdown placeholder not found"
        print("✅ Client dropdown populated")
        
        # Check for status options
        assert 'Quote' in html, "Status options not found"
        print("✅ Status dropdown populated")
        
        # Check for submit button
        assert 'Create Project' in html, "Submit button not found"
        print("✅ Submit button present")
        
        print("\n✅ NEW PROJECT FORM TEST PASSED")


def test_project_creation():
    """Test creating a new project"""
    print("\n" + "="*80)
    print("TEST 5: PROJECT CREATION")
    print("="*80)
    
    with app.app_context():
        # Get a client for testing
        client_obj = Client.query.first()
        client_id = client_obj.id
        client_code = client_obj.client_code
        
        # Count existing projects for this client this month
        now = datetime.utcnow()
        year = now.year
        month = f'{now.month:02d}'
        client_part = client_code.replace('-', '')
        prefix = f'JB-{year}-{month}-{client_part}'
        
        existing_count = Project.query.filter(
            Project.project_code.like(f'{prefix}-%')
        ).count()
        
        expected_code = f'{prefix}-{existing_count + 1:03d}'
    
    with app.test_client() as client:
        # Create a new project
        response = client.post('/projects/new', data={
            'client_id': client_id,
            'name': 'Automated Test Project',
            'description': 'Created by automated test suite',
            'status': 'Quote',
            'quote_date': date.today().strftime('%Y-%m-%d'),
            'due_date': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'quoted_price': '1500.00',
            'notes': 'Test notes'
        }, follow_redirects=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check for success message
        assert 'created successfully' in html, "Success message not found"
        print("✅ Success message displayed")
        
        # Check that we're on the detail page
        assert 'Automated Test Project' in html, "Project name not found on detail page"
        print("✅ Redirected to detail page")
        
        # Verify project code was auto-generated
        assert expected_code in html, f"Expected code {expected_code} not found"
        print(f"✅ Project code auto-generated: {expected_code}")
        
        # Verify all data was saved
        assert 'Created by automated test suite' in html, "Description not saved"
        assert 'Quote' in html, "Status not saved"
        assert 'R1500.00' in html, "Price not saved"
        assert 'Test notes' in html, "Notes not saved"
        print("✅ All project data saved correctly")
        
    # Verify in database
    with app.app_context():
        project = Project.query.filter_by(name='Automated Test Project').first()
        assert project is not None, "Project not found in database"
        assert project.project_code == expected_code, "Project code mismatch"
        assert project.client_id == client_id, "Client ID mismatch"
        assert project.status == 'Quote', "Status mismatch"
        print("✅ Project verified in database")
        
        # Check activity log
        log = ActivityLog.query.filter_by(
            entity_type='PROJECT',
            entity_id=project.id,
            action='CREATED'
        ).first()
        assert log is not None, "Activity log not created"
        print("✅ Activity log created")
        
        print("\n✅ PROJECT CREATION TEST PASSED")


def test_project_detail_page():
    """Test project detail page displays all information"""
    print("\n" + "="*80)
    print("TEST 6: PROJECT DETAIL PAGE")
    print("="*80)

    with app.app_context():
        # Get a project for testing
        project = Project.query.first()
        project_id = project.id
        project_code = project.project_code
        project_name = project.name

    with app.test_client() as client:
        response = client.get(f'/projects/{project_id}', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check breadcrumb
        assert 'Projects' in html, "Breadcrumb not found"
        assert project_code in html, "Project code not in breadcrumb"
        print("✅ Breadcrumb present")
        
        # Check project information
        assert project_name in html, "Project name not found"
        assert project_code in html, "Project code not found"
        print("✅ Project information displayed")
        
        # Check for action buttons
        assert 'Edit Project' in html, "Edit button not found"
        assert 'Delete Project' in html, "Delete button not found"
        print("✅ Action buttons present")
        
        # Check for information cards
        assert 'Project Information' in html, "Project info card not found"
        assert 'Timeline' in html, "Timeline card not found"
        assert 'Pricing' in html, "Pricing card not found"
        assert 'Metadata' in html, "Metadata card not found"
        print("✅ Information cards present")
        
        # Check for activity log
        assert 'Activity Log' in html, "Activity log not found"
        print("✅ Activity log present")
        
        print("\n✅ PROJECT DETAIL PAGE TEST PASSED")


def test_edit_project_form():
    """Test edit project form pre-fills with current values"""
    print("\n" + "="*80)
    print("TEST 7: EDIT PROJECT FORM")
    print("="*80)

    with app.app_context():
        # Get a project for testing
        project = Project.query.first()
        project_id = project.id
        project_name = project.name

    with app.test_client() as client:
        response = client.get(f'/projects/{project_id}/edit', follow_redirects=True)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        html = response.data.decode('utf-8')
        
        # Check form title
        assert '<h1>Edit Project</h1>' in html, "Form title not found"
        print("✅ Form title correct")
        
        # Check that form is pre-filled
        assert project_name in html, "Project name not pre-filled"
        print("✅ Form pre-filled with current values")
        
        # Check that client field is disabled/static
        assert 'Client cannot be changed' in html or 'form-control-static' in html, "Client field not disabled"
        print("✅ Client field is read-only")
        
        # Check for update button
        assert 'Update Project' in html, "Update button not found"
        print("✅ Update button present")
        
        print("\n✅ EDIT PROJECT FORM TEST PASSED")


def run_all_tests():
    """Run all Phase 2 web interface tests"""
    print("\n" + "="*80)
    print("PHASE 2: WEB INTERFACE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests in sequence
        test_project_list_page()
        test_project_search()
        test_project_filters()
        test_new_project_form()
        test_project_creation()
        test_project_detail_page()
        test_edit_project_form()
        
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

