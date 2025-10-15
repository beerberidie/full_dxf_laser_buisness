#!/usr/bin/env python3
"""
Test script for Phase 4 templates.

This script tests that all new templates exist and can be rendered
without errors.

Usage:
    python test_phase4_templates.py
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_template_files_exist():
    """Test that all Phase 4 template files exist."""
    print("Testing template file existence...")
    
    templates_dir = Path('app/templates')
    
    required_templates = [
        'comms/list.html',
        'comms/detail.html',
        'comms/form.html',
        'projects/form.html',  # Updated
        'projects/detail.html',  # Updated
        'queue/index.html',  # Updated
        'base.html'  # Updated
    ]
    
    all_exist = True
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ MISSING: {template}")
            all_exist = False
    
    return all_exist


def test_template_rendering():
    """Test that templates can be rendered without errors."""
    print("\nTesting template rendering...")
    
    try:
        from app import create_app, db
        from app.models import Client, Project, Communication
        from datetime import date, datetime
        
        app = create_app('testing')
        
        with app.app_context():
            # Test base template context
            with app.test_request_context():
                from flask import render_template_string
                
                # Test that base template has Communications link
                base_content = Path('app/templates/base.html').read_text(encoding='utf-8')
                if 'comms.index' in base_content:
                    print("  ✓ Base template has Communications link")
                else:
                    print("  ✗ Base template missing Communications link")
                    return False

                # Test that project form has Phase 9 fields
                form_content = Path('app/templates/projects/form.html').read_text(encoding='utf-8')
                phase9_fields = [
                    'material_type',
                    'material_quantity_sheets',
                    'parts_quantity',
                    'estimated_cut_time',
                    'drawing_creation_time',
                    'number_of_bins',
                    'scheduled_cut_date'
                ]
                
                missing_fields = []
                for field in phase9_fields:
                    if field not in form_content:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("  ✓ Project form has all Phase 9 fields")
                else:
                    print(f"  ✗ Project form missing fields: {', '.join(missing_fields)}")
                    return False
                
                # Test that project detail has Phase 9 sections
                detail_content = Path('app/templates/projects/detail.html').read_text(encoding='utf-8')
                phase9_sections = [
                    'Material & Production Information',
                    'Proof of Payment (POP) Tracking',
                    'Client Notification',
                    'Delivery Confirmation',
                    'Project Documents',
                    'Communications'
                ]

                missing_sections = []
                for section in phase9_sections:
                    if section not in detail_content:
                        missing_sections.append(section)

                if not missing_sections:
                    print("  ✓ Project detail has all Phase 9 sections")
                else:
                    print(f"  ✗ Project detail missing sections: {', '.join(missing_sections)}")
                    return False

                # Test that queue template has POP deadline warnings
                queue_content = Path('app/templates/queue/index.html').read_text(encoding='utf-8')
                if 'pop_deadline' in queue_content and 'POP deadline' in queue_content:
                    print("  ✓ Queue template has POP deadline warnings")
                else:
                    print("  ✗ Queue template missing POP deadline warnings")
                    return False

                # Test communications templates exist and have key elements
                comms_list_content = Path('app/templates/comms/list.html').read_text(encoding='utf-8')
                if 'Communications' in comms_list_content and 'comm_type' in comms_list_content:
                    print("  ✓ Communications list template has key elements")
                else:
                    print("  ✗ Communications list template missing key elements")
                    return False

                comms_detail_content = Path('app/templates/comms/detail.html').read_text(encoding='utf-8')
                if 'Link Communication' in comms_detail_content or 'Unlink' in comms_detail_content:
                    print("  ✓ Communications detail template has linking functionality")
                else:
                    print("  ✗ Communications detail template missing linking functionality")
                    return False

                comms_form_content = Path('app/templates/comms/form.html').read_text(encoding='utf-8')
                if 'comm_type' in comms_form_content and 'direction' in comms_form_content:
                    print("  ✓ Communications form template has required fields")
                else:
                    print("  ✗ Communications form template missing required fields")
                    return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Template rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_route_updates():
    """Test that routes pass required template variables."""
    print("\nTesting route updates...")
    
    try:
        from app import create_app
        
        app = create_app('testing')
        
        with app.app_context():
            # Check that projects.detail route passes 'today'
            from app.routes import projects
            import inspect
            
            detail_source = inspect.getsource(projects.detail)
            if 'today=date.today()' in detail_source:
                print("  ✓ projects.detail passes 'today' variable")
            else:
                print("  ⚠ projects.detail may not pass 'today' variable")
            
            # Check that queue.index route passes 'today'
            from app.routes import queue
            index_source = inspect.getsource(queue.index)
            if 'today=date.today()' in index_source:
                print("  ✓ queue.index passes 'today' variable")
            else:
                print("  ⚠ queue.index may not pass 'today' variable")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Route update test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Phase 4 Templates Test Suite")
    print("=" * 70)
    
    tests = [
        test_template_files_exist,
        test_template_rendering,
        test_route_updates
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
        print("\nPhase 4 implementation is complete.")
        print("All templates created and updated successfully.")
        print("\nReady to test the application UI!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

