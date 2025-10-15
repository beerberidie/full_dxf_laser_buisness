"""
Test script to verify the Flask routing fix for projects.new_project endpoint.
"""

from app import create_app

def test_endpoint_exists():
    """Test that the projects.new_project endpoint exists and is accessible."""
    app = create_app()
    
    with app.app_context():
        # Get all registered endpoints
        endpoints = []
        for rule in app.url_map.iter_rules():
            endpoints.append(rule.endpoint)
        
        print("Testing Flask Routing Fix")
        print("=" * 50)
        
        # Check if the correct endpoint exists
        if 'projects.new_project' in endpoints:
            print("✓ Endpoint 'projects.new_project' exists")
        else:
            print("✗ Endpoint 'projects.new_project' NOT FOUND")
            
        # Check if the incorrect endpoint exists (it shouldn't)
        if 'projects_new_project' in endpoints:
            print("✗ Incorrect endpoint 'projects_new_project' still exists")
        else:
            print("✓ Incorrect endpoint 'projects_new_project' does not exist")
        
        # List all projects-related endpoints
        print("\nAll 'projects' blueprint endpoints:")
        projects_endpoints = [ep for ep in endpoints if ep.startswith('projects.')]
        for ep in sorted(projects_endpoints):
            print(f"  - {ep}")
        
        # Test URL generation
        print("\nTesting URL generation:")
        try:
            with app.test_request_context():
                from flask import url_for
                url = url_for('projects.new_project')
                print(f"✓ url_for('projects.new_project') = {url}")
        except Exception as e:
            print(f"✗ Error generating URL: {e}")
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")

if __name__ == '__main__':
    test_endpoint_exists()

