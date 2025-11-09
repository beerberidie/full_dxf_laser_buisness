#!/usr/bin/env python3
"""
Verification script for CL-0004 through CL-0008 migration.
Displays all migrated projects and their details.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Project, Client, DesignFile, ProjectDocument


def verify_migration():
    """Verify the migration results."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("VERIFICATION: CL-0004 through CL-0008 Migration")
        print("="*70)
        
        # Get clients
        clients = Client.query.filter(
            Client.client_code.in_(['CL-0004', 'CL-0005', 'CL-0006', 'CL-0007', 'CL-0008'])
        ).order_by(Client.client_code).all()
        
        if not clients:
            print("\n❌ No clients found!")
            return
        
        total_projects = 0
        total_files = 0
        total_docs = 0
        
        for client in clients:
            print(f"\n{'='*70}")
            print(f"CLIENT: {client.client_code} - {client.name}")
            print(f"{'='*70}")
            
            projects = Project.query.filter_by(client_id=client.id).order_by(Project.project_code).all()
            
            if not projects:
                print("  ⚠️  No projects found for this client")
                continue
            
            print(f"\n  Total Projects: {len(projects)}")
            
            for i, project in enumerate(projects, 1):
                print(f"\n  [{i}] {project.project_code} - {project.name}")
                print(f"      Status: {project.status}")
                print(f"      Material: {project.material_type or 'N/A'} ({project.material_thickness or 'N/A'}mm)")
                print(f"      Quantity: {project.parts_quantity or 0}")
                print(f"      Created: {project.created_at}")
                print(f"      Files: {len(project.design_files)} design files, {len(project.documents)} documents")
                
                total_projects += 1
                total_files += len(project.design_files)
                total_docs += len(project.documents)
        
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"  Total Clients: {len(clients)}")
        print(f"  Total Projects: {total_projects}")
        print(f"  Total Design Files: {total_files}")
        print(f"  Total Documents: {total_docs}")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    verify_migration()

