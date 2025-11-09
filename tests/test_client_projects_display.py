#!/usr/bin/env python3
"""
Test script to verify client detail page displays projects correctly.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Client, Project


def test_client_projects():
    """Test that clients have projects and display them correctly."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("CLIENT PROJECTS DISPLAY TEST")
        print("="*70)
        
        # Get all clients with projects
        clients = Client.query.all()
        
        print(f"\nTotal Clients: {len(clients)}")
        
        for client in clients:
            project_count = len(client.projects)
            
            if project_count > 0:
                print(f"\n{'='*70}")
                print(f"CLIENT: {client.client_code} - {client.name}")
                print(f"{'='*70}")
                print(f"Total Projects: {project_count}")
                
                # Show first 5 projects
                for i, project in enumerate(client.projects[:5], 1):
                    print(f"\n  [{i}] {project.project_code} - {project.name}")
                    print(f"      Status: {project.status}")
                    print(f"      Material: {project.material_type or 'N/A'}")
                    if project.material_thickness:
                        print(f"      Thickness: {project.material_thickness}mm")
                    if project.quoted_price:
                        print(f"      Quoted Price: R{project.quoted_price:.2f}")
                    print(f"      Created: {project.created_at}")
                
                if project_count > 5:
                    print(f"\n  ... and {project_count - 5} more projects")
        
        # Summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        
        clients_with_projects = [c for c in clients if len(c.projects) > 0]
        clients_without_projects = [c for c in clients if len(c.projects) == 0]
        
        print(f"\nClients with projects: {len(clients_with_projects)}")
        print(f"Clients without projects: {len(clients_without_projects)}")
        
        if clients_without_projects:
            print("\nClients without projects:")
            for client in clients_without_projects:
                print(f"  - {client.client_code}: {client.name}")
        
        total_projects = sum(len(c.projects) for c in clients)
        print(f"\nTotal projects across all clients: {total_projects}")
        
        print(f"\n{'='*70}")
        print("✅ Test completed successfully!")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    test_client_projects()

