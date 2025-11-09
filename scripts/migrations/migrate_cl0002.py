"""
Migration script for client CL-0002.

This script migrates all projects from profiles_import/CL-0002 into the database.
"""

from app import create_app, db
from app.services.profiles_migrator import ProfilesMigrator
from app.models import Client, Project


def main():
    """Main migration function."""
    print("\n" + "="*70)
    print("PROFILES MIGRATION - CLIENT CL-0002")
    print("="*70)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Initialize migrator
        migrator = ProfilesMigrator()
        
        client_code = 'CL-0002'
        
        # Step 1: Verify client exists
        print("\n" + "="*70)
        print("STEP 1: VERIFY CLIENT")
        print("="*70)
        
        client = migrator.verify_client(client_code)
        
        if not client:
            print(f"\n❌ Client {client_code} not found in database!")
            print("Please ensure the client exists before running migration.")
            return
        
        print(f"\n✅ Client Found:")
        print(f"   Code: {client.client_code}")
        print(f"   Name: {client.name}")
        print(f"   ID: {client.id}")
        
        # Step 2: Scan and preview
        print("\n" + "="*70)
        print("STEP 2: SCAN AND PREVIEW")
        print("="*70)
        
        preview = migrator.get_migration_preview(client_code)
        print(f"\n{preview}")
        
        # Step 3: Ask for confirmation
        print("\n" + "="*70)
        print("STEP 3: CONFIRMATION")
        print("="*70)
        
        print("\n⚠️  WARNING: This will create database records and copy files.")
        print("This operation cannot be easily undone.")
        
        response = input("\nDo you want to proceed with the migration? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Migration cancelled by user.")
            return
        
        # Step 4: Execute migration
        print("\n" + "="*70)
        print("STEP 4: EXECUTE MIGRATION")
        print("="*70)
        
        print("\n🚀 Starting migration...")
        
        result = migrator.migrate_client(client_code, dry_run=False)
        
        # Step 5: Display results
        print("\n" + "="*70)
        print("STEP 5: MIGRATION RESULTS")
        print("="*70)
        
        if result['success']:
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ {result['message']}")
        
        stats = result['stats']
        
        print("\n📊 Statistics:")
        print(f"   Projects Scanned: {stats['projects_scanned']}")
        print(f"   Projects Created: {stats['projects_created']}")
        print(f"   Design Files Uploaded: {stats['design_files_uploaded']}")
        print(f"   Documents Uploaded: {stats['documents_uploaded']}")
        
        if stats['warnings']:
            print(f"\n⚠️  Warnings: {len(stats['warnings'])}")
            for warning in stats['warnings']:
                print(f"   - {warning}")
        
        if stats['errors']:
            print(f"\n❌ Errors: {len(stats['errors'])}")
            for error in stats['errors']:
                print(f"   - {error}")
        
        # Step 6: Verify migration
        if result['success']:
            print("\n" + "="*70)
            print("STEP 6: VERIFY MIGRATION")
            print("="*70)
            
            # Query created projects
            projects = Project.query.filter_by(client_id=client.id).all()
            
            print(f"\n✅ Found {len(projects)} projects for {client.name}:")
            
            for project in projects:
                print(f"\n   Project: {project.project_code}")
                print(f"      Name: {project.name}")
                print(f"      Status: {project.status}")
                print(f"      Material: {project.material_type or 'N/A'}")
                print(f"      Thickness: {project.material_thickness or 'N/A'} mm")
                print(f"      Parts: {project.parts_quantity or 'N/A'}")
                print(f"      Design Files: {len(project.design_files)}")
                print(f"      Documents: {len(project.documents)}")
        
        print("\n" + "="*70)
        print("MIGRATION COMPLETE")
        print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

