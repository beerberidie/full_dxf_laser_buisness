#!/usr/bin/env python3
"""
Test script for Phase 5 services.

This script tests the Communication Service, Scheduling Validator,
Document Service, and enhanced Activity Logger.

Usage:
    python test_phase5_services.py
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
from io import BytesIO

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_communication_service():
    """Test the Communication Service."""
    print("\n" + "="*70)
    print("TEST 1: COMMUNICATION SERVICE")
    print("="*70)

    try:
        from app import create_app, db
        from app.models import Client, Project, Communication
        from app.services.communication_service import send_email, send_whatsapp, send_notification

        app = create_app('testing')

        with app.app_context():
            # Create all tables for testing
            db.create_all()

            # Create test client
            client = Client.query.first()
            if not client:
                print("  ⚠ No clients found, testing without client link")
                client_id = None
            else:
                client_id = client.id
                print(f"  ✓ Using test client: {client.name}")
            
            # Test 1: Send email (testing mode)
            print("\n  Testing email sending...")
            result = send_email(
                to='test@example.com',
                subject='Test Email',
                body='This is a test email from LaserOS',
                client_id=client_id,
                save_to_db=True
            )
            
            if result['success']:
                print(f"  ✓ Email sent successfully (testing mode)")
                print(f"    Communication ID: {result['communication_id']}")
                
                # Verify communication was saved
                comm = Communication.query.get(result['communication_id'])
                if comm and comm.comm_type == 'Email' and comm.status == 'Sent':
                    print(f"  ✓ Communication saved to database")
                else:
                    print(f"  ✗ Communication not saved correctly")
                    return False
            else:
                print(f"  ✗ Email failed: {result['message']}")
                return False
            
            # Test 2: Send WhatsApp (placeholder)
            print("\n  Testing WhatsApp sending...")
            result = send_whatsapp(
                to='+27821234567',
                message='Your order is ready for collection',
                client_id=client_id,
                save_to_db=True
            )
            
            if result['success']:
                print(f"  ✓ WhatsApp queued successfully")
                print(f"    Communication ID: {result['communication_id']}")
            else:
                print(f"  ✗ WhatsApp failed: {result['message']}")
                return False
            
            # Test 3: Send notification
            print("\n  Testing notification sending...")
            result = send_notification(
                title='Order Ready',
                message='Project JB-2024-01-CL0001-001 is ready',
                client_id=client_id,
                save_to_db=True
            )
            
            if result['success']:
                print(f"  ✓ Notification created successfully")
                print(f"    Communication ID: {result['communication_id']}")
            else:
                print(f"  ✗ Notification failed: {result['message']}")
                return False
            
            # Test 4: Validation
            print("\n  Testing validation...")
            result = send_email(to='', subject='Test', body='Test')
            if not result['success'] and 'required' in result['message'].lower():
                print(f"  ✓ Email validation working")
            else:
                print(f"  ✗ Email validation not working")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Communication service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduling_validator():
    """Test the Scheduling Validator Service."""
    print("\n" + "="*70)
    print("TEST 2: SCHEDULING VALIDATOR SERVICE")
    print("="*70)
    
    try:
        from app import create_app, db
        from app.models import Project
        from app.services.scheduling_validator import (
            validate_pop_deadline,
            check_overdue_projects,
            check_upcoming_deadlines,
            validate_queue_capacity,
            validate_scheduling
        )
        
        app = create_app('testing')

        with app.app_context():
            # Create all tables for testing
            db.create_all()

            # Create test project with POP
            project = Project.query.first()
            if not project:
                print("  ⚠ No projects found, creating test project")
                from app.models import Client
                client = Client.query.first()
                if not client:
                    client = Client(client_code='TEST-CL001', name='Test Client')
                    db.session.add(client)
                    db.session.commit()
                project = Project(
                    project_code='TEST-001',
                    name='Test Project',
                    client_id=client.id,
                    status='Approved'
                )
                db.session.add(project)
                db.session.commit()
            
            # Set POP received
            project.pop_received = True
            project.pop_received_date = date.today() - timedelta(days=1)
            project.calculate_pop_deadline()
            db.session.commit()
            
            print(f"  ✓ Using test project: {project.project_code}")
            print(f"    POP deadline: {project.pop_deadline}")
            
            # Test 1: Validate POP deadline (valid)
            print("\n  Testing POP deadline validation (valid)...")
            result = validate_pop_deadline(project, date.today())
            if result['valid']:
                print(f"  ✓ Validation passed: {result['message']}")
                print(f"    Days remaining: {result['days_remaining']}")
            else:
                print(f"  ✗ Validation failed unexpectedly: {result['message']}")
                return False
            
            # Test 2: Validate POP deadline (past deadline)
            print("\n  Testing POP deadline validation (past deadline)...")
            future_date = project.pop_deadline + timedelta(days=5)
            result = validate_pop_deadline(project, future_date)
            if not result['valid'] and 'past' in result['message'].lower():
                print(f"  ✓ Correctly rejected past deadline")
            else:
                print(f"  ✗ Should have rejected past deadline")
                return False
            
            # Test 3: Check overdue projects
            print("\n  Testing overdue projects check...")
            overdue = check_overdue_projects()
            print(f"  ✓ Found {len(overdue)} overdue projects")
            
            # Test 4: Check upcoming deadlines
            print("\n  Testing upcoming deadlines check...")
            upcoming = check_upcoming_deadlines(days_ahead=3)
            print(f"  ✓ Found {len(upcoming)} projects with upcoming deadlines")
            
            # Test 5: Validate queue capacity
            print("\n  Testing queue capacity validation...")
            result = validate_queue_capacity(date.today(), 120)
            if result['valid']:
                print(f"  ✓ Capacity validation passed")
                print(f"    Available: {result['capacity_available']} minutes")
            else:
                print(f"  ⚠ Capacity validation: {result['message']}")
            
            # Test 6: Comprehensive scheduling validation
            print("\n  Testing comprehensive scheduling validation...")
            result = validate_scheduling(project, date.today(), 120)
            print(f"  ✓ Scheduling validation complete")
            print(f"    Valid: {result['valid']}")
            print(f"    Errors: {len(result['errors'])}")
            print(f"    Warnings: {len(result['warnings'])}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Scheduling validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_service():
    """Test the Document Service."""
    print("\n" + "="*70)
    print("TEST 3: DOCUMENT SERVICE")
    print("="*70)
    
    try:
        from app import create_app, db
        from app.models import Project, ProjectDocument
        from app.services.document_service import (
            allowed_file,
            get_file_size_mb,
            generate_unique_filename,
            get_document_folder,
            validate_document_upload
        )
        from werkzeug.datastructures import FileStorage
        
        app = create_app('testing')
        
        with app.app_context():
            # Test 1: File extension validation
            print("\n  Testing file extension validation...")
            if allowed_file('quote.pdf'):
                print(f"  ✓ PDF files allowed")
            else:
                print(f"  ✗ PDF files should be allowed")
                return False
            
            if not allowed_file('malware.exe'):
                print(f"  ✓ EXE files rejected")
            else:
                print(f"  ✗ EXE files should be rejected")
                return False
            
            # Test 2: Unique filename generation
            print("\n  Testing unique filename generation...")
            filename = generate_unique_filename('quote.pdf', 1, 'Quote')
            if 'project_1' in filename and 'quote' in filename and '.pdf' in filename:
                print(f"  ✓ Unique filename generated: {filename}")
            else:
                print(f"  ✗ Filename generation failed: {filename}")
                return False
            
            # Test 3: Document folder mapping
            print("\n  Testing document folder mapping...")
            folder = get_document_folder('Quote')
            if 'quotes' in str(folder):
                print(f"  ✓ Quote folder: {folder}")
            else:
                print(f"  ✗ Quote folder incorrect: {folder}")
                return False
            
            # Test 4: File upload validation
            print("\n  Testing file upload validation...")
            
            # Create a mock file
            file_content = b'This is a test PDF file'
            file = FileStorage(
                stream=BytesIO(file_content),
                filename='test.pdf',
                content_type='application/pdf'
            )
            
            valid, error = validate_document_upload(file, 'Quote')
            if valid:
                print(f"  ✓ Valid file passed validation")
            else:
                print(f"  ✗ Valid file failed validation: {error}")
                return False
            
            # Test invalid file type
            bad_file = FileStorage(
                stream=BytesIO(b'test'),
                filename='test.exe',
                content_type='application/octet-stream'
            )
            
            valid, error = validate_document_upload(bad_file, 'Quote')
            if not valid and 'not allowed' in error.lower():
                print(f"  ✓ Invalid file type rejected")
            else:
                print(f"  ✗ Invalid file type should be rejected")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Document service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_activity_logger_enhancements():
    """Test the enhanced Activity Logger functions."""
    print("\n" + "="*70)
    print("TEST 4: ENHANCED ACTIVITY LOGGER")
    print("="*70)
    
    try:
        from app import create_app, db
        from app.models import Project, ActivityLog
        from app.services.activity_logger import (
            log_pop_status_change,
            log_notification_status_change,
            log_delivery_status_change,
            log_communication_link,
            log_communication_unlink,
            log_material_update,
            log_scheduling_update
        )
        
        app = create_app('testing')

        with app.app_context():
            # Create all tables for testing
            db.create_all()

            # Get or create test project
            project = Project.query.first()
            if not project:
                print("  ⚠ No projects found, creating test project")
                from app.models import Client
                client = Client.query.first()
                if not client:
                    client = Client(client_code='TEST-CL001', name='Test Client')
                    db.session.add(client)
                    db.session.commit()
                project = Project(
                    project_code='TEST-001',
                    name='Test Project',
                    client_id=client.id,
                    status='Approved'
                )
                db.session.add(project)
                db.session.commit()
            
            print(f"  ✓ Using test project: {project.project_code}")
            
            # Test 1: Log POP status change
            print("\n  Testing POP status logging...")
            log = log_pop_status_change(project.id, True, date.today())
            if log and log.action == 'POP_RECEIVED':
                print(f"  ✓ POP status logged: {log.action}")
            else:
                print(f"  ✗ POP status logging failed")
                return False
            
            # Test 2: Log notification status change
            print("\n  Testing notification status logging...")
            log = log_notification_status_change(project.id, True, date.today())
            if log and log.action == 'CLIENT_NOTIFIED':
                print(f"  ✓ Notification status logged: {log.action}")
            else:
                print(f"  ✗ Notification status logging failed")
                return False
            
            # Test 3: Log delivery status change
            print("\n  Testing delivery status logging...")
            log = log_delivery_status_change(project.id, True, date.today())
            if log and log.action == 'DELIVERY_CONFIRMED':
                print(f"  ✓ Delivery status logged: {log.action}")
            else:
                print(f"  ✗ Delivery status logging failed")
                return False
            
            # Test 4: Log communication link
            print("\n  Testing communication link logging...")
            log = log_communication_link(1, client_id=1, project_id=project.id)
            if log and log.action == 'LINKED':
                print(f"  ✓ Communication link logged: {log.action}")
            else:
                print(f"  ✗ Communication link logging failed")
                return False
            
            # Test 5: Log material update
            print("\n  Testing material update logging...")
            log = log_material_update(project.id, 'Mild Steel', 5)
            if log and log.action == 'MATERIAL_UPDATED':
                print(f"  ✓ Material update logged: {log.action}")
            else:
                print(f"  ✗ Material update logging failed")
                return False
            
            # Test 6: Log scheduling update
            print("\n  Testing scheduling update logging...")
            log = log_scheduling_update(project.id, date.today(), 120)
            if log and log.action == 'SCHEDULING_UPDATED':
                print(f"  ✓ Scheduling update logged: {log.action}")
            else:
                print(f"  ✗ Scheduling update logging failed")
                return False
            
            # Verify all logs were created
            logs = ActivityLog.query.filter_by(entity_type='PROJECT', entity_id=project.id).all()
            print(f"\n  ✓ Total activity logs for project: {len(logs)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Activity logger test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Phase 5 Services Test Suite")
    print("=" * 70)
    
    tests = [
        test_communication_service,
        test_scheduling_validator,
        test_document_service,
        test_activity_logger_enhancements
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nPhase 5 implementation is complete.")
        print("All services are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

