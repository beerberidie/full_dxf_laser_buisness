#!/usr/bin/env python3
"""
Test script for Phase 9 models.

This script tests the new models and enhancements without requiring
the full application context. Run this after applying the migration
to verify everything works correctly.

Usage:
    python test_phase9_models.py
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all models can be imported."""
    print("Testing model imports...")
    try:
        from app.models import (
            Project, ProjectDocument, Communication, 
            CommunicationAttachment, Client
        )
        print("✓ All models imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_project_constants():
    """Test that Project model has new status constants."""
    print("\nTesting Project status constants...")
    try:
        from app.models import Project
        
        # Check new status constants exist
        assert hasattr(Project, 'STATUS_REQUEST')
        assert hasattr(Project, 'STATUS_QUOTE_APPROVAL')
        assert hasattr(Project, 'STATUS_APPROVED_POP')
        assert hasattr(Project, 'STATUS_QUEUED')
        
        # Check they're in VALID_STATUSES
        assert Project.STATUS_REQUEST in Project.VALID_STATUSES
        assert Project.STATUS_QUOTE_APPROVAL in Project.VALID_STATUSES
        assert Project.STATUS_APPROVED_POP in Project.VALID_STATUSES
        assert Project.STATUS_QUEUED in Project.VALID_STATUSES
        
        print(f"✓ Project has {len(Project.VALID_STATUSES)} valid statuses")
        print(f"  New statuses: {Project.STATUS_REQUEST}, {Project.STATUS_QUOTE_APPROVAL}, "
              f"{Project.STATUS_APPROVED_POP}, {Project.STATUS_QUEUED}")
        return True
    except (AssertionError, AttributeError) as e:
        print(f"✗ Status constants test failed: {e}")
        return False


def test_project_properties():
    """Test that Project model has new properties."""
    print("\nTesting Project properties...")
    try:
        from app.models import Project
        
        # Check new properties exist
        properties = [
            'is_ready_for_quote',
            'is_within_pop_deadline',
            'days_until_pop_deadline',
            'estimated_cut_time_hours',
            'drawing_creation_time_hours'
        ]
        
        for prop in properties:
            assert hasattr(Project, prop), f"Missing property: {prop}"
        
        print(f"✓ All {len(properties)} new properties exist")
        return True
    except AssertionError as e:
        print(f"✗ Properties test failed: {e}")
        return False


def test_project_methods():
    """Test that Project model has new methods."""
    print("\nTesting Project methods...")
    try:
        from app.models import Project
        
        # Check new methods exist
        assert hasattr(Project, 'calculate_pop_deadline')
        
        print("✓ calculate_pop_deadline method exists")
        return True
    except AssertionError as e:
        print(f"✗ Methods test failed: {e}")
        return False


def test_project_document_model():
    """Test ProjectDocument model."""
    print("\nTesting ProjectDocument model...")
    try:
        from app.models import ProjectDocument
        
        # Check constants
        assert hasattr(ProjectDocument, 'TYPE_QUOTE')
        assert hasattr(ProjectDocument, 'TYPE_INVOICE')
        assert hasattr(ProjectDocument, 'TYPE_POP')
        assert hasattr(ProjectDocument, 'TYPE_DELIVERY_NOTE')
        
        # Check methods
        assert hasattr(ProjectDocument, 'to_dict')
        assert hasattr(ProjectDocument, 'file_size_formatted')
        
        print("✓ ProjectDocument model structure valid")
        print(f"  Document types: {ProjectDocument.VALID_TYPES}")
        return True
    except (AssertionError, AttributeError) as e:
        print(f"✗ ProjectDocument test failed: {e}")
        return False


def test_communication_model():
    """Test Communication model."""
    print("\nTesting Communication model...")
    try:
        from app.models import Communication
        
        # Check type constants
        assert hasattr(Communication, 'TYPE_EMAIL')
        assert hasattr(Communication, 'TYPE_WHATSAPP')
        assert hasattr(Communication, 'TYPE_NOTIFICATION')
        
        # Check direction constants
        assert hasattr(Communication, 'DIRECTION_INBOUND')
        assert hasattr(Communication, 'DIRECTION_OUTBOUND')
        
        # Check status constants
        assert hasattr(Communication, 'STATUS_PENDING')
        assert hasattr(Communication, 'STATUS_SENT')
        assert hasattr(Communication, 'STATUS_DELIVERED')
        assert hasattr(Communication, 'STATUS_FAILED')
        assert hasattr(Communication, 'STATUS_READ')
        
        # Check methods
        assert hasattr(Communication, 'to_dict')
        assert hasattr(Communication, 'preview_text')
        
        print("✓ Communication model structure valid")
        print(f"  Types: {Communication.VALID_TYPES}")
        print(f"  Directions: {Communication.VALID_DIRECTIONS}")
        print(f"  Statuses: {Communication.VALID_STATUSES}")
        return True
    except (AssertionError, AttributeError) as e:
        print(f"✗ Communication test failed: {e}")
        return False


def test_communication_attachment_model():
    """Test CommunicationAttachment model."""
    print("\nTesting CommunicationAttachment model...")
    try:
        from app.models import CommunicationAttachment
        
        # Check methods
        assert hasattr(CommunicationAttachment, 'to_dict')
        assert hasattr(CommunicationAttachment, 'file_size_formatted')
        
        print("✓ CommunicationAttachment model structure valid")
        return True
    except (AssertionError, AttributeError) as e:
        print(f"✗ CommunicationAttachment test failed: {e}")
        return False


def test_pop_deadline_calculation():
    """Test POP deadline calculation logic."""
    print("\nTesting POP deadline calculation...")
    try:
        from app.models import Project
        from datetime import date, timedelta
        
        # Create a mock project (not saved to DB)
        project = Project()
        
        # Test 1: No POP date set
        project.pop_received_date = None
        project.calculate_pop_deadline()
        assert project.pop_deadline is None, "Deadline should be None when no POP date"
        
        # Test 2: POP date set
        test_date = date(2025, 10, 14)
        project.pop_received_date = test_date
        project.calculate_pop_deadline()
        expected_deadline = test_date + timedelta(days=3)
        assert project.pop_deadline == expected_deadline, \
            f"Expected {expected_deadline}, got {project.pop_deadline}"
        
        print("✓ POP deadline calculation works correctly")
        print(f"  POP date: {test_date} → Deadline: {project.pop_deadline}")
        return True
    except (AssertionError, Exception) as e:
        print(f"✗ POP deadline calculation failed: {e}")
        return False


def test_time_formatting():
    """Test time formatting properties."""
    print("\nTesting time formatting...")
    try:
        from app.models import Project
        
        project = Project()
        
        # Test 1: Minutes only
        project.estimated_cut_time = 45
        assert project.estimated_cut_time_hours == "45m"
        
        # Test 2: Hours and minutes
        project.estimated_cut_time = 125  # 2h 5m
        assert project.estimated_cut_time_hours == "2h 5m"
        
        # Test 3: Exact hours
        project.estimated_cut_time = 120  # 2h 0m
        assert project.estimated_cut_time_hours == "2h 0m"
        
        # Test 4: None
        project.estimated_cut_time = None
        assert project.estimated_cut_time_hours is None
        
        print("✓ Time formatting works correctly")
        print("  45 min → 45m")
        print("  125 min → 2h 5m")
        print("  120 min → 2h 0m")
        return True
    except (AssertionError, Exception) as e:
        print(f"✗ Time formatting failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Phase 9 Models Test Suite")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_project_constants,
        test_project_properties,
        test_project_methods,
        test_project_document_model,
        test_communication_model,
        test_communication_attachment_model,
        test_pop_deadline_calculation,
        test_time_formatting,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
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
        print("\nPhase 1 & 2 implementation is working correctly.")
        print("You can now proceed to apply the migration and test with the database.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above before proceeding.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

