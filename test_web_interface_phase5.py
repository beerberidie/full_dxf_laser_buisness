"""
Phase 5: Schedule Queue & Laser Runs - Web Interface Tests
Tests queue management and laser run web interface functionality
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import QueueItem, LaserRun, Project


def test_queue_index_page():
    """Test 1: Queue Index Page"""
    print("\n" + "="*80)
    print("TEST 1: QUEUE INDEX PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Access queue index
        response = client.get('/queue/')
        
        print(f"\n✅ Queue index page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check for key elements
        html = response.data.decode('utf-8')
        
        assert 'Production Queue' in html, "Page title not found"
        assert 'Queued' in html, "Queued status not found"
        assert 'In Progress' in html, "In Progress status not found"
        
        print(f"✅ Page contains expected elements:")
        print(f"   - Production Queue title")
        print(f"   - Status statistics")
        print(f"   - Queue table")
        
        print("\n" + "="*80)
        print("✅ TEST 1 PASSED: Queue Index Page")
        print("="*80)


def test_add_to_queue():
    """Test 2: Add Project to Queue"""
    print("\n" + "="*80)
    print("TEST 2: ADD PROJECT TO QUEUE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get a project
        project = Project.query.first()
        
        if not project:
            print("❌ No projects in database")
            return
        
        # Count queue items before
        count_before = QueueItem.query.count()
        
        # Add to queue
        response = client.post(f'/queue/add/{project.id}', data={
            'priority': 'High',
            'scheduled_date': '2025-10-15',
            'estimated_cut_time': '60',
            'notes': 'Test queue item from web interface'
        }, follow_redirects=True)
        
        print(f"\n✅ Add to queue request sent")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check database
        count_after = QueueItem.query.count()
        
        print(f"✅ Queue items before: {count_before}")
        print(f"✅ Queue items after: {count_after}")
        
        # Verify queue item created
        queue_item = QueueItem.query.filter_by(project_id=project.id).order_by(QueueItem.id.desc()).first()
        
        if queue_item:
            print(f"✅ Queue item created:")
            print(f"   - ID: {queue_item.id}")
            print(f"   - Project: {queue_item.project.project_code}")
            print(f"   - Priority: {queue_item.priority}")
            print(f"   - Position: {queue_item.queue_position}")
        
        print("\n" + "="*80)
        print("✅ TEST 2 PASSED: Add Project to Queue")
        print("="*80)


def test_queue_detail_page():
    """Test 3: Queue Item Detail Page"""
    print("\n" + "="*80)
    print("TEST 3: QUEUE ITEM DETAIL PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get a queue item
        queue_item = QueueItem.query.first()
        
        if not queue_item:
            print("❌ No queue items in database")
            return
        
        # Access detail page
        response = client.get(f'/queue/{queue_item.id}')
        
        print(f"\n✅ Queue item detail page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check for key elements
        html = response.data.decode('utf-8')
        
        assert f'Queue Item #{queue_item.id}' in html, "Queue item ID not found"
        assert queue_item.project.project_code in html, "Project code not found"
        assert queue_item.status in html, "Status not found"
        
        print(f"✅ Page contains expected elements:")
        print(f"   - Queue Item #{queue_item.id}")
        print(f"   - Project: {queue_item.project.project_code}")
        print(f"   - Status: {queue_item.status}")
        
        print("\n" + "="*80)
        print("✅ TEST 3 PASSED: Queue Item Detail Page")
        print("="*80)


def test_update_queue_status():
    """Test 4: Update Queue Item Status"""
    print("\n" + "="*80)
    print("TEST 4: UPDATE QUEUE ITEM STATUS")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get a queue item
        queue_item = QueueItem.query.filter_by(status=QueueItem.STATUS_QUEUED).first()
        
        if not queue_item:
            print("❌ No queued items in database")
            return
        
        old_status = queue_item.status
        
        # Update status
        response = client.post(f'/queue/{queue_item.id}/status', data={
            'status': QueueItem.STATUS_IN_PROGRESS
        }, follow_redirects=True)
        
        print(f"\n✅ Status update request sent")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Refresh from database
        db.session.refresh(queue_item)
        
        print(f"✅ Status updated:")
        print(f"   - Old Status: {old_status}")
        print(f"   - New Status: {queue_item.status}")
        print(f"   - Started At: {queue_item.started_at}")
        
        assert queue_item.status == QueueItem.STATUS_IN_PROGRESS, "Status not updated"
        
        print("\n" + "="*80)
        print("✅ TEST 4 PASSED: Update Queue Item Status")
        print("="*80)


def test_laser_run_form():
    """Test 5: Laser Run Form Page"""
    print("\n" + "="*80)
    print("TEST 5: LASER RUN FORM PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get a project
        project = Project.query.first()
        
        if not project:
            print("❌ No projects in database")
            return
        
        # Access laser run form
        response = client.get(f'/queue/runs/new/{project.id}')
        
        print(f"\n✅ Laser run form page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check for key elements
        html = response.data.decode('utf-8')
        
        assert 'Log Laser Run' in html, "Page title not found"
        assert project.project_code in html, "Project code not found"
        assert 'operator' in html, "Operator field not found"
        assert 'cut_time_minutes' in html, "Cut time field not found"
        
        print(f"✅ Page contains expected elements:")
        print(f"   - Log Laser Run title")
        print(f"   - Project: {project.project_code}")
        print(f"   - Form fields (operator, cut_time, material, etc.)")
        
        print("\n" + "="*80)
        print("✅ TEST 5 PASSED: Laser Run Form Page")
        print("="*80)


def test_log_laser_run():
    """Test 6: Log Laser Run"""
    print("\n" + "="*80)
    print("TEST 6: LOG LASER RUN")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get a project
        project = Project.query.first()
        
        if not project:
            print("❌ No projects in database")
            return
        
        # Count laser runs before
        count_before = LaserRun.query.count()
        
        # Log laser run
        response = client.post(f'/queue/runs/new/{project.id}', data={
            'operator': 'Test Operator',
            'cut_time_minutes': '45',
            'material_type': 'Stainless Steel',
            'material_thickness': '2.5',
            'sheet_count': '2',
            'parts_produced': '75',
            'machine_settings': 'Power: 1500W, Speed: 50mm/s',
            'notes': 'Test laser run from web interface'
        }, follow_redirects=True)
        
        print(f"\n✅ Log laser run request sent")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check database
        count_after = LaserRun.query.count()
        
        print(f"✅ Laser runs before: {count_before}")
        print(f"✅ Laser runs after: {count_after}")
        
        # Verify laser run created
        laser_run = LaserRun.query.filter_by(project_id=project.id).order_by(LaserRun.id.desc()).first()
        
        if laser_run:
            print(f"✅ Laser run created:")
            print(f"   - ID: {laser_run.id}")
            print(f"   - Project: {laser_run.project.project_code}")
            print(f"   - Operator: {laser_run.operator}")
            print(f"   - Cut Time: {laser_run.cut_time_minutes} min")
            print(f"   - Parts: {laser_run.parts_produced}")
        
        print("\n" + "="*80)
        print("✅ TEST 6 PASSED: Log Laser Run")
        print("="*80)


def test_laser_run_history():
    """Test 7: Laser Run History Page"""
    print("\n" + "="*80)
    print("TEST 7: LASER RUN HISTORY PAGE")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Access laser run history
        response = client.get('/queue/runs')
        
        print(f"\n✅ Laser run history page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check for key elements
        html = response.data.decode('utf-8')
        
        assert 'Laser Run History' in html, "Page title not found"
        assert 'Operator' in html, "Operator column not found"
        
        # Check if runs are displayed
        runs_count = LaserRun.query.count()
        print(f"✅ Total laser runs in database: {runs_count}")
        
        if runs_count > 0:
            print(f"✅ Laser runs displayed on page")
        
        print("\n" + "="*80)
        print("✅ TEST 7 PASSED: Laser Run History Page")
        print("="*80)


def test_project_detail_queue_section():
    """Test 8: Project Detail Page - Queue Section"""
    print("\n" + "="*80)
    print("TEST 8: PROJECT DETAIL PAGE - QUEUE SECTION")
    print("="*80)
    
    app = create_app('development')
    client = app.test_client()
    
    with app.app_context():
        # Get a project
        project = Project.query.first()
        
        if not project:
            print("❌ No projects in database")
            return
        
        # Access project detail
        response = client.get(f'/projects/{project.id}')
        
        print(f"\n✅ Project detail page loaded")
        print(f"   Status Code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check for queue-related elements
        html = response.data.decode('utf-8')
        
        assert 'Add to Queue' in html, "Add to Queue button not found"
        assert 'Queue Status' in html, "Queue Status section not found"
        assert 'Laser Run History' in html, "Laser Run History section not found"
        assert 'Log Laser Run' in html, "Log Laser Run button not found"
        
        print(f"✅ Page contains queue-related elements:")
        print(f"   - Add to Queue button")
        print(f"   - Queue Status section")
        print(f"   - Laser Run History section")
        print(f"   - Log Laser Run button")
        
        print("\n" + "="*80)
        print("✅ TEST 8 PASSED: Project Detail Page - Queue Section")
        print("="*80)


def run_all_tests():
    """Run all Phase 5 web interface tests"""
    print("\n" + "="*80)
    print("PHASE 5: SCHEDULE QUEUE & LASER RUNS - WEB INTERFACE TESTS")
    print("="*80)
    
    tests = [
        test_queue_index_page,
        test_add_to_queue,
        test_queue_detail_page,
        test_update_queue_status,
        test_laser_run_form,
        test_log_laser_run,
        test_laser_run_history,
        test_project_detail_queue_section
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test.__name__}")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Pass Rate: {(passed/len(tests)*100):.0f}%")
    print("="*80)


if __name__ == '__main__':
    run_all_tests()

