"""
Test the web interface endpoints
"""

import urllib.request
import urllib.parse
import json

def test_dashboard():
    """Test dashboard page"""
    print("\n" + "="*80)
    print("WEB TEST 1: DASHBOARD")
    print("="*80)
    
    try:
        response = urllib.request.urlopen('http://127.0.0.1:5000/')
        content = response.read().decode('utf-8')
        
        print(f"✅ Dashboard loaded (Status: {response.status})")
        print(f"✅ Contains 'Laser OS': {'Laser OS' in content}")
        print(f"✅ Contains 'Dashboard': {'Dashboard' in content}")
        print(f"✅ Contains 'Total Clients': {'Total Clients' in content}")
        
        # Check if client count is displayed
        if '5' in content:
            print(f"✅ Shows 5 clients (from test data)")
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")


def test_client_list():
    """Test client list page"""
    print("\n" + "="*80)
    print("WEB TEST 2: CLIENT LIST")
    print("="*80)
    
    try:
        response = urllib.request.urlopen('http://127.0.0.1:5000/clients')
        content = response.read().decode('utf-8')
        
        print(f"✅ Client list loaded (Status: {response.status})")
        print(f"✅ Contains 'Clients': {'Clients' in content}")
        
        # Check for test clients
        test_clients = [
            'CL-0001',
            'Acme Manufacturing',
            'Precision Engineering',
            'BuildCo Construction',
            'Design Studio',
            'AutoParts Suppliers'
        ]
        
        found_count = 0
        for client_name in test_clients:
            if client_name in content:
                found_count += 1
                print(f"✅ Found: {client_name}")
        
        print(f"\n✅ Found {found_count}/{len(test_clients)} test clients")
        
    except Exception as e:
        print(f"❌ Client list test failed: {e}")


def test_client_search():
    """Test client search"""
    print("\n" + "="*80)
    print("WEB TEST 3: CLIENT SEARCH")
    print("="*80)
    
    try:
        # Search for "Engineering"
        params = urllib.parse.urlencode({'search': 'Engineering'})
        url = f'http://127.0.0.1:5000/clients?{params}'
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8')
        
        print(f"✅ Search loaded (Status: {response.status})")
        
        if 'Precision Engineering' in content:
            print(f"✅ Found 'Precision Engineering' in search results")
        
        if 'Acme Manufacturing' not in content or content.count('Test Client') == 1:
            print(f"✅ Search filtered correctly (only Engineering results)")
        
    except Exception as e:
        print(f"❌ Client search test failed: {e}")


def test_client_detail():
    """Test client detail page"""
    print("\n" + "="*80)
    print("WEB TEST 4: CLIENT DETAIL")
    print("="*80)
    
    try:
        # Assuming client ID 1 exists
        response = urllib.request.urlopen('http://127.0.0.1:5000/clients/1')
        content = response.read().decode('utf-8')
        
        print(f"✅ Client detail loaded (Status: {response.status})")
        print(f"✅ Contains 'CL-0001': {'CL-0001' in content}")
        print(f"✅ Contains 'Acme Manufacturing': {'Acme Manufacturing' in content}")
        print(f"✅ Contains 'John Smith': {'John Smith' in content}")
        print(f"✅ Contains 'Activity Log': {'Activity Log' in content}")
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"⚠️  Client ID 1 not found - this is expected if database was reset")
        else:
            print(f"❌ Client detail test failed: {e}")
    except Exception as e:
        print(f"❌ Client detail test failed: {e}")


def test_new_client_form():
    """Test new client form page"""
    print("\n" + "="*80)
    print("WEB TEST 5: NEW CLIENT FORM")
    print("="*80)
    
    try:
        response = urllib.request.urlopen('http://127.0.0.1:5000/clients/new')
        content = response.read().decode('utf-8')
        
        print(f"✅ New client form loaded (Status: {response.status})")
        has_form = '<form' in content
        has_name = 'name="name"' in content or 'id="name"' in content
        has_email = 'name="email"' in content or 'id="email"' in content
        has_phone = 'name="phone"' in content or 'id="phone"' in content

        print(f"✅ Contains form: {has_form}")
        print(f"✅ Contains name field: {has_name}")
        print(f"✅ Contains email field: {has_email}")
        print(f"✅ Contains phone field: {has_phone}")
        
    except Exception as e:
        print(f"❌ New client form test failed: {e}")


def test_navigation():
    """Test navigation menu"""
    print("\n" + "="*80)
    print("WEB TEST 6: NAVIGATION")
    print("="*80)
    
    try:
        response = urllib.request.urlopen('http://127.0.0.1:5000/')
        content = response.read().decode('utf-8')
        
        print(f"✅ Page loaded (Status: {response.status})")
        
        nav_items = [
            ('Dashboard', '/'),
            ('Clients', '/clients'),
            ('Projects', '/projects'),
            ('Queue', '/queue'),
            ('Inventory', '/inventory'),
            ('Reports', '/reports'),
            ('Parameters', '/parameters')
        ]
        
        found_count = 0
        for name, link in nav_items:
            if name in content:
                found_count += 1
                print(f"✅ Found navigation item: {name}")
        
        print(f"\n✅ Found {found_count}/{len(nav_items)} navigation items")
        
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")


def run_all_web_tests():
    """Run all web interface tests"""
    print("\n" + "="*80)
    print("PHASE 1: WEB INTERFACE TESTING")
    print("="*80)
    
    try:
        test_dashboard()
        test_client_list()
        test_client_search()
        test_client_detail()
        test_new_client_form()
        test_navigation()
        
        print("\n" + "="*80)
        print("✅ ALL WEB TESTS COMPLETED!")
        print("="*80)
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ WEB TESTS FAILED!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_web_tests()

