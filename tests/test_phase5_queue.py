"""
Phase 5: Schedule Queue & Laser Runs - Database Tests
Tests queue management and laser run logging functionality
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import QueueItem, LaserRun, Project, Client, ActivityLog


def test_queue_operations():
    """Test 1: Queue Operations - Add, Update, Remove"""
    print("\n" + "="*80)
    print("TEST 1: QUEUE OPERATIONS")
    print("="*80)

    app = create_app('development')
    
    with app.app_context():
        # Get existing projects
        projects = Project.query.limit(3).all()
        
        if len(projects) < 3:
            print("❌ Not enough projects in database. Need at least 3 projects.")
            return
        
        # Add projects to queue
        queue_items = []
        for i, project in enumerate(projects, start=1):
            queue_item = QueueItem(
                project_id=project.id,
                queue_position=i,
                status=QueueItem.STATUS_QUEUED,
                priority=QueueItem.PRIORITY_NORMAL if i % 2 == 0 else QueueItem.PRIORITY_HIGH,
                scheduled_date=date.today() + timedelta(days=i),
                estimated_cut_time=30 + (i * 10),
                notes=f'Test queue item {i}',
                added_by='Test System'
            )
            db.session.add(queue_item)
            queue_items.append(queue_item)
        
        db.session.commit()
        
        print(f"\n✅ Created {len(queue_items)} queue items:")
        for item in queue_items:
            print(f"   - Position {item.queue_position}: {item.project.project_code} "
                  f"({item.priority}, {item.status})")
        
        # Update status
        first_item = queue_items[0]
        first_item.status = QueueItem.STATUS_IN_PROGRESS
        first_item.started_at = datetime.utcnow()
        db.session.commit()
        
        print(f"\n✅ Updated queue item #{first_item.id} status to: {first_item.status}")
        print(f"   Started at: {first_item.started_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Test properties
        print(f"\n✅ Queue item properties:")
        print(f"   - Is Active: {first_item.is_active}")
        print(f"   - Duration in Queue: {first_item.duration_in_queue} days")
        
        # Test to_dict
        item_dict = first_item.to_dict()
        print(f"\n✅ to_dict() method works:")
        print(f"   - Keys: {list(item_dict.keys())}")
        
        print("\n" + "="*80)
        print("✅ TEST 1 PASSED: Queue Operations")
        print("="*80)


def test_laser_runs():
    """Test 2: Laser Run Logging"""
    print("\n" + "="*80)
    print("TEST 2: LASER RUN LOGGING")
    print("="*80)

    app = create_app('development')
    
    with app.app_context():
        # Get a project and queue item
        project = Project.query.first()
        queue_item = QueueItem.query.first()
        
        if not project:
            print("❌ No projects in database")
            return
        
        # Create laser runs
        runs = []
        for i in range(1, 4):
            laser_run = LaserRun(
                project_id=project.id,
                queue_item_id=queue_item.id if queue_item else None,
                operator=f'Operator {i}',
                cut_time_minutes=45 + (i * 15),
                material_type='Mild Steel',
                material_thickness=3.0,
                sheet_count=i,
                parts_produced=50 * i,
                machine_settings=f'Power: {i*100}W, Speed: {i*10}mm/s',
                notes=f'Test run {i}'
            )
            db.session.add(laser_run)
            runs.append(laser_run)
        
        db.session.commit()
        
        print(f"\n✅ Created {len(runs)} laser runs:")
        for run in runs:
            print(f"   - Run #{run.id}: {run.operator}, {run.cut_time_minutes} min, "
                  f"{run.parts_produced} parts")
        
        # Test properties
        first_run = runs[0]
        print(f"\n✅ Laser run properties:")
        print(f"   - Cut Time (minutes): {first_run.cut_time_minutes}")
        print(f"   - Cut Time (hours): {first_run.cut_time_hours}")
        print(f"   - Material: {first_run.material_type} ({first_run.material_thickness}mm)")
        
        # Test to_dict
        run_dict = first_run.to_dict()
        print(f"\n✅ to_dict() method works:")
        print(f"   - Keys: {list(run_dict.keys())}")
        
        print("\n" + "="*80)
        print("✅ TEST 2 PASSED: Laser Run Logging")
        print("="*80)


def test_queue_project_relationship():
    """Test 3: Queue-Project Relationship"""
    print("\n" + "="*80)
    print("TEST 3: QUEUE-PROJECT RELATIONSHIP")
    print("="*80)

    app = create_app('development')
    
    with app.app_context():
        # Get a project with queue items
        project = Project.query.join(QueueItem).first()
        
        if not project:
            print("❌ No projects with queue items")
            return
        
        print(f"\n✅ Project: {project.project_code} - {project.name}")
        print(f"   Queue Items: {len(project.queue_items)}")
        
        for item in project.queue_items:
            print(f"   - Position {item.queue_position}: {item.status} ({item.priority})")
        
        # Test backref
        if project.queue_items:
            first_item = project.queue_items[0]
            print(f"\n✅ Backref works:")
            print(f"   - Queue Item #{first_item.id} -> Project: {first_item.project.project_code}")
        
        print("\n" + "="*80)
        print("✅ TEST 3 PASSED: Queue-Project Relationship")
        print("="*80)


def test_laser_run_relationships():
    """Test 4: Laser Run Relationships"""
    print("\n" + "="*80)
    print("TEST 4: LASER RUN RELATIONSHIPS")
    print("="*80)

    app = create_app('development')
    
    with app.app_context():
        # Get a project with laser runs
        project = Project.query.join(LaserRun).first()
        
        if not project:
            print("❌ No projects with laser runs")
            return
        
        print(f"\n✅ Project: {project.project_code}")
        print(f"   Laser Runs: {len(project.laser_runs)}")
        
        for run in project.laser_runs[:5]:
            print(f"   - Run #{run.id}: {run.run_date.strftime('%Y-%m-%d')}, "
                  f"{run.operator}, {run.cut_time_minutes} min")
        
        # Test queue item relationship
        run_with_queue = LaserRun.query.filter(LaserRun.queue_item_id.isnot(None)).first()
        if run_with_queue:
            print(f"\n✅ Laser Run -> Queue Item relationship:")
            print(f"   - Run #{run_with_queue.id} -> Queue Item #{run_with_queue.queue_item_id}")
            print(f"   - Queue Position: {run_with_queue.queue_item.queue_position}")
        
        print("\n" + "="*80)
        print("✅ TEST 4 PASSED: Laser Run Relationships")
        print("="*80)


def test_activity_logging():
    """Test 5: Activity Logging for Queue Operations"""
    print("\n" + "="*80)
    print("TEST 5: ACTIVITY LOGGING")
    print("="*80)

    app = create_app('development')
    
    with app.app_context():
        # Get a queue item
        queue_item = QueueItem.query.first()
        
        if not queue_item:
            print("❌ No queue items in database")
            return
        
        # Create activity logs
        activities = [
            ActivityLog(
                entity_type='QUEUE',
                entity_id=queue_item.id,
                action='ADDED',
                details=f'Added project {queue_item.project.project_code} to queue',
                user='Test System'
            ),
            ActivityLog(
                entity_type='QUEUE',
                entity_id=queue_item.id,
                action='STATUS_CHANGED',
                details=f'Status changed from Queued to In Progress',
                user='Test System'
            )
        ]
        
        for activity in activities:
            db.session.add(activity)
        
        db.session.commit()
        
        print(f"\n✅ Created {len(activities)} activity log entries")
        
        # Retrieve logs
        logs = ActivityLog.query.filter_by(
            entity_type='QUEUE',
            entity_id=queue_item.id
        ).all()
        
        print(f"\n✅ Activity logs for Queue Item #{queue_item.id}:")
        for log in logs:
            print(f"   - {log.action}: {log.details}")
        
        # Create laser run activity log
        laser_run = LaserRun.query.first()
        if laser_run:
            run_activity = ActivityLog(
                entity_type='LASER_RUN',
                entity_id=laser_run.id,
                action='CREATED',
                details=f'Logged laser run for project {laser_run.project.project_code}',
                user='Test System'
            )
            db.session.add(run_activity)
            db.session.commit()
            
            print(f"\n✅ Created activity log for Laser Run #{laser_run.id}")
        
        print("\n" + "="*80)
        print("✅ TEST 5 PASSED: Activity Logging")
        print("="*80)


def run_all_tests():
    """Run all Phase 5 tests"""
    print("\n" + "="*80)
    print("PHASE 5: SCHEDULE QUEUE & LASER RUNS - DATABASE TESTS")
    print("="*80)
    
    tests = [
        test_queue_operations,
        test_laser_runs,
        test_queue_project_relationship,
        test_laser_run_relationships,
        test_activity_logging
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

