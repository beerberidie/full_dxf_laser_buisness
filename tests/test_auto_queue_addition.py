"""
Test script for automatic queue addition when POP is received.

This script tests the new functionality that automatically adds projects
to the production queue when POP (Proof of Payment) is marked as received.
"""

import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.models import Project, Client, QueueItem
from datetime import date, timedelta


def test_auto_queue_addition():
    """Test automatic queue addition when POP is received."""
    print("\n" + "="*80)
    print("TESTING AUTOMATIC QUEUE ADDITION")
    print("="*80 + "\n")
    
    app = create_app('development')
    
    with app.app_context():
        # Get or create a test client
        client = Client.query.first()
        
        if not client:
            print("❌ No clients found. Please create a client first.")
            return
        
        print(f"Using client: {client.name} ({client.client_code})")
        
        # Create a test project
        from app.services.id_generator import generate_project_code
        
        project = Project(
            client_id=client.id,
            name="Test Auto Queue Project",
            description="Testing automatic queue addition when POP is received",
            status=Project.STATUS_APPROVED,
            material_type="Mild Steel",
            material_thickness=10.0,
            material_quantity_sheets=5,
            parts_quantity=100,
            estimated_cut_time=120,  # 2 hours
            quoted_price=5000.00,
            pop_received=False
        )
        
        # Generate project code
        project.project_code = generate_project_code(client.client_code)
        
        db.session.add(project)
        db.session.commit()
        
        print(f"\n✓ Created test project: {project.project_code}")
        print(f"  Name: {project.name}")
        print(f"  Estimated cut time: {project.estimated_cut_time} minutes")
        print(f"  POP received: {project.pop_received}")
        
        # Check queue before
        queue_count_before = QueueItem.query.filter_by(project_id=project.id).count()
        print(f"\n  Queue items before: {queue_count_before}")
        
        # Simulate marking POP as received (like the toggle_pop route does)
        print("\n" + "-"*80)
        print("SIMULATING POP RECEIVED...")
        print("-"*80)
        
        project.pop_received = True
        project.pop_received_date = date.today()
        project.calculate_pop_deadline()
        
        print(f"\n✓ POP marked as received")
        print(f"  POP received date: {project.pop_received_date}")
        print(f"  POP deadline: {project.pop_deadline}")
        
        # Now test the auto_add_to_queue function
        from app.routes.projects import auto_add_to_queue
        
        success, message = auto_add_to_queue(project)
        
        if success:
            db.session.commit()
            print(f"\n✓ AUTO QUEUE ADDITION SUCCESSFUL")
            print(f"  Message: {message}")
        else:
            print(f"\n✗ AUTO QUEUE ADDITION FAILED")
            print(f"  Message: {message}")
            return
        
        # Check queue after
        queue_items = QueueItem.query.filter_by(project_id=project.id).all()
        print(f"\n  Queue items after: {len(queue_items)}")
        
        if queue_items:
            for qi in queue_items:
                print(f"\n  Queue Item Details:")
                print(f"    ID: {qi.id}")
                print(f"    Position: {qi.queue_position}")
                print(f"    Status: {qi.status}")
                print(f"    Priority: {qi.priority}")
                print(f"    Scheduled date: {qi.scheduled_date}")
                print(f"    Estimated cut time: {qi.estimated_cut_time} minutes")
                print(f"    Added by: {qi.added_by}")
                print(f"    Notes: {qi.notes}")
        
        # Test duplicate prevention
        print("\n" + "-"*80)
        print("TESTING DUPLICATE PREVENTION...")
        print("-"*80)
        
        success2, message2 = auto_add_to_queue(project)
        
        if not success2:
            print(f"\n✓ DUPLICATE PREVENTION WORKING")
            print(f"  Message: {message2}")
        else:
            print(f"\n✗ DUPLICATE PREVENTION FAILED - Should not allow duplicate")
        
        # Test with a project already in progress
        print("\n" + "-"*80)
        print("TESTING IN-PROGRESS PREVENTION...")
        print("-"*80)
        
        # Change status to in progress
        queue_items[0].status = QueueItem.STATUS_IN_PROGRESS
        db.session.commit()
        
        # Create another test project
        project2 = Project(
            client_id=client.id,
            name="Test Auto Queue Project 2",
            description="Testing in-progress prevention",
            status=Project.STATUS_APPROVED,
            material_type="Stainless Steel",
            material_thickness=5.0,
            estimated_cut_time=60,
            pop_received=True,
            pop_received_date=date.today()
        )
        project2.project_code = generate_project_code(client.client_code)
        project2.calculate_pop_deadline()
        
        db.session.add(project2)
        db.session.commit()
        
        print(f"\n✓ Created second test project: {project2.project_code}")
        
        # Add to queue
        success3, message3 = auto_add_to_queue(project2)
        
        if success3:
            db.session.commit()
            print(f"\n✓ Second project added to queue successfully")
            print(f"  Message: {message3}")
            
            # Check position
            qi2 = QueueItem.query.filter_by(project_id=project2.id).first()
            if qi2:
                print(f"  Queue position: {qi2.queue_position}")
                print(f"  Priority: {qi2.priority}")
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        all_queue_items = QueueItem.query.order_by(QueueItem.queue_position).all()
        print(f"\nTotal queue items: {len(all_queue_items)}")
        
        for qi in all_queue_items:
            print(f"\n  Position {qi.queue_position}: {qi.project.project_code}")
            print(f"    Status: {qi.status}")
            print(f"    Priority: {qi.priority}")
            print(f"    Added by: {qi.added_by}")
        
        print("\n" + "="*80)
        print("✓ ALL TESTS COMPLETED")
        print("="*80 + "\n")
        
        # Cleanup option
        cleanup = input("\nDo you want to clean up test data? (y/n): ").strip().lower()
        
        if cleanup == 'y':
            # Delete queue items
            for qi in all_queue_items:
                if qi.project.name.startswith("Test Auto Queue"):
                    db.session.delete(qi)
            
            # Delete test projects
            test_projects = Project.query.filter(
                Project.name.like("Test Auto Queue%")
            ).all()
            
            for p in test_projects:
                db.session.delete(p)
            
            db.session.commit()
            print("\n✓ Test data cleaned up")
        else:
            print("\n✓ Test data preserved for manual inspection")
            print(f"   View at: http://127.0.0.1:5000/queue/")


if __name__ == '__main__':
    test_auto_queue_addition()

