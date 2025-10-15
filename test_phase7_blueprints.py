"""
Phase 7 Blueprint Registration Verification Test Suite

Tests all blueprints are properly registered, routes are accessible, and no conflicts exist.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app


def test_blueprint_registration():
    """Test that all blueprints are properly registered."""
    print("\n" + "="*70)
    print("TEST 1: BLUEPRINT REGISTRATION")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Expected blueprints
            expected_blueprints = [
                'main',
                'clients',
                'projects',
                'products',
                'files',
                'queue',
                'inventory',
                'reports',
                'quotes',
                'invoices',
                'comms'  # Phase 9
            ]
            
            # Get registered blueprints
            registered_blueprints = list(app.blueprints.keys())
            
            print(f"\n  Expected Blueprints: {len(expected_blueprints)}")
            print(f"  Registered Blueprints: {len(registered_blueprints)}")
            
            # Check each expected blueprint
            missing = []
            for bp_name in expected_blueprints:
                if bp_name in registered_blueprints:
                    print(f"  ✓ {bp_name}")
                else:
                    print(f"  ✗ {bp_name} - MISSING")
                    missing.append(bp_name)
            
            # Check for unexpected blueprints
            unexpected = [bp for bp in registered_blueprints if bp not in expected_blueprints]
            if unexpected:
                print(f"\n  Unexpected blueprints found:")
                for bp in unexpected:
                    print(f"  ⚠ {bp}")
            
            if missing:
                print(f"\n  ✗ {len(missing)} blueprint(s) missing")
                return False
            
            print(f"\n  ✓ All {len(expected_blueprints)} blueprints registered correctly")
            return True
            
    except Exception as e:
        print(f"  ✗ Blueprint registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_route_listing():
    """Test and list all routes for each blueprint."""
    print("\n" + "="*70)
    print("TEST 2: ROUTE LISTING")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Group routes by blueprint
            blueprint_routes = defaultdict(list)
            
            for rule in app.url_map.iter_rules():
                # Get blueprint name from endpoint
                if '.' in rule.endpoint:
                    bp_name = rule.endpoint.split('.')[0]
                else:
                    bp_name = 'app'  # Application-level routes
                
                blueprint_routes[bp_name].append({
                    'endpoint': rule.endpoint,
                    'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
                    'path': str(rule)
                })
            
            # Display routes by blueprint
            total_routes = 0
            for bp_name in sorted(blueprint_routes.keys()):
                routes = blueprint_routes[bp_name]
                print(f"\n  {bp_name.upper()} Blueprint ({len(routes)} routes):")
                
                for route in sorted(routes, key=lambda x: x['path']):
                    methods_str = ', '.join(route['methods'])
                    print(f"    {route['path']:<40} [{methods_str}]")
                    total_routes += 1
            
            print(f"\n  ✓ Total routes: {total_routes}")
            return True
            
    except Exception as e:
        print(f"  ✗ Route listing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_routing_conflicts():
    """Test for routing conflicts (duplicate paths)."""
    print("\n" + "="*70)
    print("TEST 3: ROUTING CONFLICTS")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Group routes by path
            path_endpoints = defaultdict(list)
            
            for rule in app.url_map.iter_rules():
                path_endpoints[str(rule)].append({
                    'endpoint': rule.endpoint,
                    'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'})
                })
            
            # Check for conflicts
            conflicts = []
            for path, endpoints in path_endpoints.items():
                if len(endpoints) > 1:
                    # Check if methods overlap
                    all_methods = set()
                    for ep in endpoints:
                        ep_methods = set(ep['methods'])
                        if all_methods & ep_methods:
                            conflicts.append({
                                'path': path,
                                'endpoints': endpoints
                            })
                        all_methods.update(ep_methods)
            
            if conflicts:
                print(f"\n  ✗ Found {len(conflicts)} routing conflict(s):")
                for conflict in conflicts:
                    print(f"\n    Path: {conflict['path']}")
                    for ep in conflict['endpoints']:
                        print(f"      - {ep['endpoint']} [{', '.join(ep['methods'])}]")
                return False
            else:
                print("  ✓ No routing conflicts detected")
                return True
            
    except Exception as e:
        print(f"  ✗ Routing conflict test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase9_routes():
    """Test that all Phase 9 routes are registered."""
    print("\n" + "="*70)
    print("TEST 4: PHASE 9 ROUTES")
    print("="*70)

    try:
        app = create_app('development')

        with app.app_context():
            # Expected Phase 9 routes (actual implementation)
            expected_routes = {
                # Communications routes (URL prefix: /communications)
                'comms.index': '/communications/',
                'comms.detail': '/communications/<int:id>',
                'comms.new_communication': '/communications/new',
                'comms.link_communication': '/communications/<int:id>/link',
                'comms.unlink_communication': '/communications/<int:id>/unlink',

                # Project enhancement routes
                'projects.toggle_pop': '/projects/<int:id>/toggle-pop',
                'projects.toggle_notified': '/projects/<int:id>/toggle-notified',
                'projects.toggle_delivery': '/projects/<int:id>/toggle-delivery',
                'projects.upload_document': '/projects/<int:id>/upload-document',
                'projects.delete_document': '/projects/document/<int:doc_id>/delete',
            }
            
            # Get all registered endpoints
            registered_endpoints = {rule.endpoint: str(rule) for rule in app.url_map.iter_rules()}
            
            # Check each expected route
            missing = []
            for endpoint, expected_path in expected_routes.items():
                if endpoint in registered_endpoints:
                    actual_path = registered_endpoints[endpoint]
                    print(f"  ✓ {endpoint:<40} {actual_path}")
                else:
                    print(f"  ✗ {endpoint:<40} MISSING")
                    missing.append(endpoint)
            
            if missing:
                print(f"\n  ✗ {len(missing)} Phase 9 route(s) missing")
                return False
            
            print(f"\n  ✓ All {len(expected_routes)} Phase 9 routes registered")
            return True
            
    except Exception as e:
        print(f"  ✗ Phase 9 routes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_accessibility():
    """Test that endpoints are accessible (don't raise import errors)."""
    print("\n" + "="*70)
    print("TEST 5: ENDPOINT ACCESSIBILITY")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Test that we can get view functions for all endpoints
            inaccessible = []
            
            for rule in app.url_map.iter_rules():
                try:
                    view_func = app.view_functions.get(rule.endpoint)
                    if view_func is None:
                        inaccessible.append(rule.endpoint)
                except Exception as e:
                    inaccessible.append(f"{rule.endpoint} ({str(e)})")
            
            if inaccessible:
                print(f"\n  ✗ Found {len(inaccessible)} inaccessible endpoint(s):")
                for ep in inaccessible:
                    print(f"    - {ep}")
                return False
            else:
                total_endpoints = len(list(app.url_map.iter_rules()))
                print(f"  ✓ All {total_endpoints} endpoints are accessible")
                return True
            
    except Exception as e:
        print(f"  ✗ Endpoint accessibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_url_prefixes():
    """Test that blueprints have correct URL prefixes."""
    print("\n" + "="*70)
    print("TEST 6: URL PREFIXES")
    print("="*70)

    try:
        app = create_app('development')

        with app.app_context():
            # Expected URL prefixes (actual implementation)
            expected_prefixes = {
                'main': None,  # No prefix
                'clients': '/clients',
                'projects': '/projects',
                'products': '/products',
                'files': '/files',
                'queue': '/queue',
                'inventory': '/inventory',
                'reports': '/reports',
                'quotes': '/quotes',
                'invoices': '/invoices',
                'comms': '/communications',  # Phase 9: Full word for clarity
            }
            
            # Check each blueprint's prefix
            all_correct = True
            for bp_name, expected_prefix in expected_prefixes.items():
                if bp_name in app.blueprints:
                    bp = app.blueprints[bp_name]
                    actual_prefix = bp.url_prefix
                    
                    if actual_prefix == expected_prefix:
                        prefix_display = actual_prefix if actual_prefix else '(none)'
                        print(f"  ✓ {bp_name:<15} {prefix_display}")
                    else:
                        print(f"  ✗ {bp_name:<15} Expected: {expected_prefix}, Got: {actual_prefix}")
                        all_correct = False
                else:
                    print(f"  ✗ {bp_name:<15} Blueprint not registered")
                    all_correct = False
            
            if all_correct:
                print(f"\n  ✓ All URL prefixes correct")
            else:
                print(f"\n  ✗ Some URL prefixes incorrect")
            
            return all_correct
            
    except Exception as e:
        print(f"  ✗ URL prefix test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 7 blueprint verification tests."""
    print("\n" + "="*70)
    print("PHASE 7 BLUEPRINT REGISTRATION VERIFICATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Blueprint Registration", test_blueprint_registration),
        ("Route Listing", test_route_listing),
        ("Routing Conflicts", test_routing_conflicts),
        ("Phase 9 Routes", test_phase9_routes),
        ("Endpoint Accessibility", test_endpoint_accessibility),
        ("URL Prefixes", test_url_prefixes),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nPhase 7 blueprint registration is complete and working correctly.")
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

