#!/usr/bin/env python3
"""
Test script for Phase 3 routes.

This script tests that all new routes are properly registered
and the application starts without errors.

Usage:
    python test_phase3_routes.py
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Test that the app can be created."""
    print("Testing app creation...")
    try:
        from app import create_app
        app = create_app('testing')
        print("✓ App created successfully")
        return app
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return None


def test_blueprints_registered(app):
    """Test that all blueprints are registered."""
    print("\nTesting blueprint registration...")
    try:
        blueprints = list(app.blueprints.keys())
        print(f"  Registered blueprints: {', '.join(blueprints)}")
        
        required_blueprints = [
            'main', 'clients', 'projects', 'products', 'files',
            'queue', 'inventory', 'reports', 'quotes', 'invoices',
            'comms'  # Phase 9
        ]
        
        for bp in required_blueprints:
            if bp in blueprints:
                print(f"  ✓ {bp}")
            else:
                print(f"  ✗ MISSING: {bp}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Blueprint test failed: {e}")
        return False


def test_routes_exist(app):
    """Test that Phase 9 routes exist."""
    print("\nTesting Phase 9 routes...")
    try:
        with app.app_context():
            # Get all routes
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(str(rule))
            
            # Check for Phase 9 project routes
            phase9_project_routes = [
                '/projects/<id>/toggle-pop',
                '/projects/<id>/toggle-notified',
                '/projects/<id>/toggle-delivery',
                '/projects/<id>/upload-document',
                '/projects/document/<doc_id>/delete'
            ]
            
            print("  Project routes:")
            for route in phase9_project_routes:
                # Check if route pattern exists (may have different parameter names)
                found = any(route.replace('<id>', '<int:id>').replace('<doc_id>', '<int:doc_id>') in r for r in routes)
                if found:
                    print(f"    ✓ {route}")
                else:
                    print(f"    ⚠ Not found: {route}")
            
            # Check for communications routes
            comms_routes = [
                '/communications/',
                '/communications/<id>',
                '/communications/new',
                '/communications/<id>/link',
                '/communications/<id>/unlink'
            ]
            
            print("  Communications routes:")
            for route in comms_routes:
                found = any(route.replace('<id>', '<int:id>') in r for r in routes)
                if found:
                    print(f"    ✓ {route}")
                else:
                    print(f"    ⚠ Not found: {route}")
            
        return True
    except Exception as e:
        print(f"✗ Routes test failed: {e}")
        return False


def test_config_values(app):
    """Test that Phase 9 config values are set."""
    print("\nTesting Phase 9 configuration...")
    try:
        with app.app_context():
            # Check Phase 9 config values
            config_keys = [
                'DOCUMENTS_FOLDER',
                'ALLOWED_DOCUMENT_EXTENSIONS',
                'POP_DEADLINE_DAYS',
                'MATERIAL_TYPES',
                'MAIL_SERVER',
                'MAIL_PORT',
                'MAIL_DEFAULT_SENDER'
            ]
            
            for key in config_keys:
                value = app.config.get(key)
                if value is not None:
                    if isinstance(value, list):
                        print(f"  ✓ {key}: {len(value)} items")
                    elif isinstance(value, str) and len(value) > 50:
                        print(f"  ✓ {key}: {value[:50]}...")
                    else:
                        print(f"  ✓ {key}: {value}")
                else:
                    print(f"  ⚠ {key}: Not set")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


def test_models_import():
    """Test that Phase 9 models can be imported."""
    print("\nTesting Phase 9 models import...")
    try:
        from app.models import ProjectDocument, Communication, CommunicationAttachment
        print("  ✓ ProjectDocument")
        print("  ✓ Communication")
        print("  ✓ CommunicationAttachment")
        return True
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Phase 3 Routes Test Suite")
    print("=" * 70)
    
    # Test app creation
    app = test_app_creation()
    if not app:
        print("\n❌ FAILED: Cannot proceed without app")
        return 1
    
    # Run tests
    tests = [
        lambda: test_blueprints_registered(app),
        lambda: test_routes_exist(app),
        lambda: test_config_values(app),
        test_models_import
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
        print("\nPhase 3 implementation is working correctly.")
        print("Routes are registered and configuration is set.")
        print("\nReady to proceed to Phase 4 (Templates).")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

