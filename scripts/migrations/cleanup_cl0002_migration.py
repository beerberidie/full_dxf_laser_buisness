"""
Cleanup script to remove partial migration for CL-0002.

This script removes any projects created during the failed migration attempt.
"""

from app import create_app, db
from app.models import Client, Project
import shutil
from pathlib import Path


def main():
    """Main cleanup function."""
    print("\n" + "="*70)
    print("CLEANUP PARTIAL MIGRATION - CLIENT CL-0002")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        client_code = 'CL-0002'
        
        # Find client
        client = Client.query.filter_by(client_code=client_code).first()
        
        if not client:
            print(f"\n❌ Client {client_code} not found!")
            return
        
        print(f"\n✅ Client Found: {client.name} ({client.client_code})")
        
        # Find all projects for this client
        projects = Project.query.filter_by(client_id=client.id).all()
        
        if not projects:
            print(f"\n✅ No projects found for {client.name}. Nothing to clean up.")
            return
        
        print(f"\n⚠️  Found {len(projects)} project(s) for {client.name}:")
        for project in projects:
            print(f"   - {project.project_code}: {project.name}")
            print(f"     Design Files: {len(project.design_files)}")
            print(f"     Documents: {len(project.documents)}")
        
        response = input("\nDo you want to DELETE these projects? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Cleanup cancelled.")
            return
        
        print("\n🗑️  Deleting projects...")
        
        # Delete each project (cascade will delete files and documents)
        for project in projects:
            print(f"\n   Deleting: {project.project_code}")
            
            # Delete physical files
            project_folder = Path("data/files") / str(project.id)
            if project_folder.exists():
                shutil.rmtree(project_folder)
                print(f"      ✓ Deleted folder: {project_folder}")
            
            # Delete from database (cascade will handle design_files and documents)
            db.session.delete(project)
        
        db.session.commit()
        
        print("\n✅ Cleanup complete!")
        print(f"   Deleted {len(projects)} project(s)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

