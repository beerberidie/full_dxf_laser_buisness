"""
Test Authentication and Authorization System

This script tests the authentication and authorization system by:
1. Testing login for each user role
2. Verifying route protection
3. Checking permission-based access control

Run this script to verify the authentication system is working correctly.
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from flask import url_for

def test_authentication():
    """Test authentication and authorization system."""
    
    app = create_app()
    
    # Test users with their expected permissions
    test_users = {
        'admin': {
            'username': 'garason',
            'password': 'Admin123!',
            'role': 'Administrator',
            'expected_access': {
                'dashboard': True,
                'clients_list': True,
                'clients_new': True,
                'clients_edit': True,
                'projects_list': True,
                'projects_new': True,
                'projects_edit': True,
                'products_list': True,
                'products_new': True,
                'queue_index': True,
                'queue_remove': True,
                'inventory_index': True,
                'inventory_new': True,
                'reports_production': True,
                'reports_export': True,
                'admin_users': True,
                'presets_index': True,
                'presets_new': True,
            }
        },
        'manager': {
            'username': 'kieran',
            'password': 'Manager123!',
            'role': 'Manager',
            'expected_access': {
                'dashboard': True,
                'clients_list': True,
                'clients_new': True,
                'clients_edit': True,
                'projects_list': True,
                'projects_new': True,
                'projects_edit': True,
                'products_list': True,
                'products_new': True,
                'queue_index': True,
                'queue_remove': True,
                'inventory_index': True,
                'inventory_new': True,
                'reports_production': True,
                'reports_export': True,
                'admin_users': False,  # No admin access
                'presets_index': True,
                'presets_new': True,
            }
        },
        'operator': {
            'username': 'operator1',
            'password': 'Operator123!',
            'role': 'Operator',
            'expected_access': {
                'dashboard': True,
                'clients_list': True,
                'clients_new': False,  # Cannot create clients
                'clients_edit': False,  # Cannot edit clients
                'projects_list': True,
                'projects_new': False,  # Cannot create projects
                'projects_edit': False,  # Cannot edit projects
                'products_list': True,
                'products_new': False,  # Cannot create products
                'queue_index': True,
                'queue_remove': False,  # Cannot remove from queue (admin/manager only)
                'inventory_index': True,
                'inventory_new': False,  # Cannot create inventory
                'reports_production': True,
                'reports_export': False,  # Cannot export (admin/manager only)
                'admin_users': False,  # No admin access
                'presets_index': True,
                'presets_new': False,  # Cannot create presets
            }
        },
        'viewer': {
            'username': 'viewer1',
            'password': 'Viewer123!',
            'role': 'Viewer',
            'expected_access': {
                'dashboard': True,
                'clients_list': True,
                'clients_new': False,  # Read-only
                'clients_edit': False,  # Read-only
                'projects_list': True,
                'projects_new': False,  # Read-only
                'projects_edit': False,  # Read-only
                'products_list': True,
                'products_new': False,  # Read-only
                'queue_index': True,
                'queue_remove': False,  # Read-only
                'inventory_index': True,
                'inventory_new': False,  # Read-only
                'reports_production': True,
                'reports_export': False,  # Read-only
                'admin_users': False,  # No admin access
                'presets_index': True,
                'presets_new': False,  # Read-only
            }
        }
    }
    
    print("=" * 80)
    print("TESTING AUTHENTICATION AND AUTHORIZATION SYSTEM")
    print("=" * 80)
    print()
    
    with app.test_client() as client:
        for user_type, user_data in test_users.items():
            print(f"Testing {user_data['role']} User: {user_data['username']}")
            print("-" * 80)
            
            # Test login
            response = client.post('/auth/login', data={
                'username': user_data['username'],
                'password': user_data['password'],
                'csrf_token': ''  # In test mode, CSRF might be disabled
            }, follow_redirects=False)
            
            if response.status_code == 302:  # Redirect after successful login
                print(f"✅ Login successful")
            else:
                print(f"❌ Login failed (status: {response.status_code})")
                continue
            
            # Test route access
            print(f"\nTesting route access for {user_data['role']}:")
            
            test_routes = {
                'dashboard': '/',
                'clients_list': '/clients/',
                'clients_new': '/clients/new',
                'projects_list': '/projects/',
                'projects_new': '/projects/new',
                'products_list': '/products/',
                'products_new': '/products/new',
                'queue_index': '/queue/',
                'inventory_index': '/inventory/',
                'inventory_new': '/inventory/new',
                'reports_production': '/reports/production',
                'admin_users': '/admin/users',
                'presets_index': '/presets/',
                'presets_new': '/presets/new',
            }
            
            passed = 0
            failed = 0
            
            for route_name, route_path in test_routes.items():
                if route_name not in user_data['expected_access']:
                    continue
                
                response = client.get(route_path, follow_redirects=False)
                expected_access = user_data['expected_access'][route_name]
                
                # 200 = OK, 302 = Redirect (might be to login), 403 = Forbidden
                has_access = response.status_code == 200
                
                if has_access == expected_access:
                    status = "✅ PASS"
                    passed += 1
                else:
                    status = "❌ FAIL"
                    failed += 1
                
                access_str = "ALLOWED" if has_access else "DENIED"
                expected_str = "ALLOWED" if expected_access else "DENIED"
                
                print(f"  {status} {route_name:20} - {access_str:7} (expected: {expected_str:7}) [{response.status_code}]")
            
            # Logout
            client.get('/auth/logout')
            
            print(f"\nResults: {passed} passed, {failed} failed")
            print()
    
    print("=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_authentication()

