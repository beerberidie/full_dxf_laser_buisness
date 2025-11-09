"""
Migration script for clients CL-0001 and CL-0003.

This script:
1. Verifies both clients exist in the database
2. Scans their project directories
3. Shows a preview of what will be imported
4. Asks for confirmation
5. Migrates all projects with status set to "Complete"
"""

import os
from app import create_app
from app.models import Client, Project
from app.services.profiles_migrator import ProfilesMigrator


def verify_clients(client_codes):
    """Verify that clients exist in the database."""
    print("\n" + "="*70)
    print("STEP 1: VERIFY CLIENTS")
    print("="*70)
    
    clients = {}
    for code in client_codes:
        client = Client.query.filter_by(client_code=code).first()
        if not client:
            print(f"\n❌ ERROR: Client {code} not found in database!")
            return None
        
        clients[code] = client
        print(f"\n✅ {client.client_code}: {client.name}")
        if client.contact_person:
            print(f"   Contact: {client.contact_person}")
        if client.email:
            print(f"   Email: {client.email}")
        if client.phone:
            print(f"   Phone: {client.phone}")
    
    return clients


def scan_and_preview(client_code, base_path):
    """Scan a client's projects directory and show preview."""
    print("\n" + "="*70)
    print(f"SCANNING: {client_code}")
    print("="*70)
    
    projects_path = os.path.join(base_path, client_code, '1.Projects')
    
    if not os.path.exists(projects_path):
        print(f"\n❌ ERROR: Projects directory not found: {projects_path}")
        return None
    
    # Get all project folders
    project_folders = [f for f in os.listdir(projects_path) 
                      if os.path.isdir(os.path.join(projects_path, f))]
    
    if not project_folders:
        print(f"\n⚠️  WARNING: No project folders found in {projects_path}")
        return []
    
    print(f"\n📁 Found {len(project_folders)} project folder(s):\n")
    
    preview_data = []
    
    for folder in sorted(project_folders):
        folder_path = os.path.join(projects_path, folder)
        
        # Count files
        all_files = [f for f in os.listdir(folder_path) 
                    if os.path.isfile(os.path.join(folder_path, f))]
        
        design_files = [f for f in all_files if f.lower().endswith(('.dxf', '.lbrn2'))]
        doc_files = [f for f in all_files 
                    if not f.lower().endswith(('.dxf', '.lbrn2')) and 
                    not f.startswith('.')]
        
        print(f"   📂 {folder}")
        print(f"      Design Files: {len(design_files)}")
        print(f"      Documents: {len(doc_files)}")
        
        preview_data.append({
            'folder': folder,
            'folder_path': folder_path,
            'design_files': len(design_files),
            'documents': len(doc_files),
            'total_files': len(all_files)
        })
    
    return preview_data


def show_summary(previews):
    """Show summary of what will be imported."""
    print("\n" + "="*70)
    print("MIGRATION PREVIEW SUMMARY")
    print("="*70)
    
    total_projects = 0
    total_design_files = 0
    total_documents = 0
    
    for client_code, preview in previews.items():
        if preview:
            projects = len(preview)
            design_files = sum(p['design_files'] for p in preview)
            documents = sum(p['documents'] for p in preview)
            
            total_projects += projects
            total_design_files += design_files
            total_documents += documents
            
            print(f"\n{client_code}:")
            print(f"   Projects: {projects}")
            print(f"   Design Files: {design_files}")
            print(f"   Documents: {documents}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL:")
    print(f"   Projects: {total_projects}")
    print(f"   Design Files: {total_design_files}")
    print(f"   Documents: {total_documents}")
    print(f"{'='*70}")
    
    return total_projects > 0


def migrate_client(client_code, client, base_path, default_status='Complete'):
    """Migrate a single client's projects."""
    print("\n" + "="*70)
    print(f"MIGRATING: {client_code} - {client.name}")
    print("="*70)

    projects_path = os.path.join(base_path, client_code, '1.Projects')

    # Initialize migrator with custom status
    migrator = ProfilesMigrator(base_path, default_status=default_status)

    # Migrate
    result = migrator.migrate_client(
        client_code=client_code,
        dry_run=False
    )
    
    # Display results
    print(f"\n{'='*70}")
    print(f"MIGRATION RESULTS: {client_code}")
    print(f"{'='*70}")

    # Extract stats from result
    stats = result.get('stats', result)  # Handle both nested and flat formats

    print(f"\n✅ Projects Created: {stats['projects_created']}")
    print(f"✅ Design Files Uploaded: {stats['design_files_uploaded']}")
    print(f"✅ Documents Uploaded: {stats['documents_uploaded']}")

    if stats['warnings']:
        print(f"\n⚠️  Warnings: {len(stats['warnings'])}")
        for warning in stats['warnings']:
            print(f"   - {warning}")

    if stats['errors']:
        print(f"\n❌ Errors: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"   - {error}")
    else:
        print(f"\n✅ No errors encountered!")

    return stats


def main():
    """Main migration function."""
    print("\n" + "="*70)
    print("PROFILES MIGRATION: CL-0001 and CL-0003")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Configuration
        client_codes = ['CL-0001', 'CL-0003']
        base_path = 'profiles_import'
        default_status = 'Completed'  # Must match Project.STATUS_COMPLETED
        
        # Step 1: Verify clients exist
        clients = verify_clients(client_codes)
        if not clients:
            print("\n❌ Migration aborted: Not all clients found in database")
            return
        
        # Step 2: Scan and preview
        print("\n" + "="*70)
        print("STEP 2: SCAN PROJECT DIRECTORIES")
        print("="*70)
        
        previews = {}
        for code in client_codes:
            preview = scan_and_preview(code, base_path)
            if preview is None:
                print(f"\n❌ Migration aborted: Could not scan {code}")
                return
            previews[code] = preview
        
        # Step 3: Show summary
        has_data = show_summary(previews)
        
        if not has_data:
            print("\n⚠️  No data to migrate!")
            return
        
        # Step 4: Ask for confirmation
        print(f"\n{'='*70}")
        print("CONFIRMATION REQUIRED")
        print(f"{'='*70}")
        print(f"\nThis will:")
        print(f"   1. Create project records in the database")
        print(f"   2. Upload all design files and documents")
        print(f"   3. Set project status to: '{default_status}'")
        print(f"   4. Link all files to their respective projects")
        
        response = input("\n⚠️  Proceed with migration? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Migration cancelled by user")
            return
        
        # Step 5: Migrate each client
        print("\n" + "="*70)
        print("STEP 3: EXECUTE MIGRATION")
        print("="*70)
        
        results = {}
        for code in client_codes:
            if previews[code]:  # Only migrate if there's data
                result = migrate_client(code, clients[code], base_path, default_status)
                results[code] = result
            else:
                print(f"\n⚠️  Skipping {code} - no projects found")
        
        # Step 6: Final summary
        print("\n" + "="*70)
        print("MIGRATION COMPLETE - FINAL SUMMARY")
        print("="*70)
        
        total_projects = 0
        total_design_files = 0
        total_documents = 0
        total_warnings = 0
        total_errors = 0
        
        for code, result in results.items():
            total_projects += result['projects_created']
            total_design_files += result['design_files_uploaded']
            total_documents += result['documents_uploaded']
            total_warnings += len(result['warnings'])
            total_errors += len(result['errors'])
            
            print(f"\n{code} ({clients[code].name}):")
            print(f"   ✅ Projects: {result['projects_created']}")
            print(f"   ✅ Design Files: {result['design_files_uploaded']}")
            print(f"   ✅ Documents: {result['documents_uploaded']}")
            if result['warnings']:
                print(f"   ⚠️  Warnings: {len(result['warnings'])}")
            if result['errors']:
                print(f"   ❌ Errors: {len(result['errors'])}")
        
        print(f"\n{'='*70}")
        print(f"GRAND TOTAL:")
        print(f"   Projects Created: {total_projects}")
        print(f"   Design Files Uploaded: {total_design_files}")
        print(f"   Documents Uploaded: {total_documents}")
        print(f"   Warnings: {total_warnings}")
        print(f"   Errors: {total_errors}")
        print(f"{'='*70}")
        
        if total_errors == 0:
            print("\n🎉 Migration completed successfully!")
        else:
            print(f"\n⚠️  Migration completed with {total_errors} error(s)")
        
        print("\nNext steps:")
        print("   1. Verify the migrated projects in the web application")
        print("   2. Check that all files are accessible")
        print("   3. Confirm project statuses are set to 'Complete'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

