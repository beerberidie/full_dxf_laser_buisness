"""
Comprehensive endpoint verification script.
This script checks all registered Flask endpoints and verifies naming consistency.
"""

from app import create_app

def verify_endpoints():
    """Verify all Flask endpoints are correctly named."""
    app = create_app()
    
    with app.app_context():
        print("Flask Endpoint Verification Report")
        print("=" * 70)
        
        # Group endpoints by blueprint
        blueprint_endpoints = {}
        
        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            
            # Skip static endpoint
            if endpoint == 'static':
                continue
            
            # Extract blueprint name
            if '.' in endpoint:
                blueprint_name = endpoint.split('.')[0]
            else:
                blueprint_name = 'main'
            
            if blueprint_name not in blueprint_endpoints:
                blueprint_endpoints[blueprint_name] = []
            
            blueprint_endpoints[blueprint_name].append({
                'endpoint': endpoint,
                'url': str(rule),
                'methods': ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            })
        
        # Display endpoints by blueprint
        for blueprint_name in sorted(blueprint_endpoints.keys()):
            print(f"\n{blueprint_name.upper()} Blueprint:")
            print("-" * 70)
            
            for ep_info in sorted(blueprint_endpoints[blueprint_name], key=lambda x: x['endpoint']):
                print(f"  Endpoint: {ep_info['endpoint']:<35} URL: {ep_info['url']:<30} Methods: {ep_info['methods']}")
        
        # Check for any endpoints with underscores (potential issues)
        print("\n" + "=" * 70)
        print("Checking for potential naming issues...")
        print("-" * 70)
        
        issues_found = False
        for blueprint_name, endpoints in blueprint_endpoints.items():
            for ep_info in endpoints:
                endpoint = ep_info['endpoint']
                # Check if endpoint has underscore in the function name part (after the dot)
                if '.' in endpoint:
                    parts = endpoint.split('.')
                    if len(parts) == 2 and '_' in parts[0]:
                        print(f"⚠ Warning: Blueprint name has underscore: {endpoint}")
                        issues_found = True
        
        if not issues_found:
            print("✓ No naming issues found. All endpoints follow correct naming convention.")
        
        print("\n" + "=" * 70)
        print("Verification complete!")

if __name__ == '__main__':
    verify_endpoints()

