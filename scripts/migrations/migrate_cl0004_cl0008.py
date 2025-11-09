#!/usr/bin/env python3
"""
Migration script for clients CL-0004 through CL-0008.
Imports all projects from profiles_import directory into the database.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Client
from app.services.profiles_migrator import ProfilesMigrator


def print_config():
    """Print application configuration."""
    from flask import current_app

    print("\n" + "="*70)
    print("LASER OS - CONFIGURATION STATUS")
    print("="*70)
    print(f"📋 Environment: {os.getenv('FLASK_ENV', 'unknown')}")
    print(f"🐛 Debug Mode: {current_app.config.get('DEBUG', False)}")
    print(f"💾 Database: {current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')}")
    print(f"📁 Upload Folder: {current_app.config.get('UPLOAD_FOLDER', 'N/A')}")
    print(f"📄 Documents Folder: {current_app.config.get('DOCUMENTS_FOLDER', 'N/A')}")
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 0)
    print(f"📦 Max Upload Size: {max_size / (1024 * 1024):.1f} MB" if max_size else "📦 Max Upload Size: N/A")
    print(f"📧 Email Configured: {'✓ Yes' if current_app.config.get('MAIL_SERVER') else '✗ No (using defaults)'}")
    print(f"\n⚙️  Business Rules:")
    print(f"   POP Deadline: {current_app.config.get('POP_DEADLINE_DAYS', 'N/A')} days")
    print(f"   Max Hours/Day: {current_app.config.get('MAX_HOURS_PER_DAY', 'N/A')} hours")
    print(f"   Default SLA: {current_app.config.get('DEFAULT_SLA_DAYS', 'N/A')} days")
    material_types = current_app.config.get('MATERIAL_TYPES', [])
    print(f"\n🔧 Material Types: {len(material_types)} configured")
    print("="*70)


def verify_clients(client_codes):
    """Verify that all clients exist in the database."""
    print("\n" + "="*70)
    print("STEP 1: VERIFY CLIENTS")
    print("="*70)
    
    clients = {}
    missing = []
    
    for code in client_codes:
        client = Client.query.filter_by(client_code=code).first()
        if client:
            clients[code] = client
            print(f"\n✅ {code}: {client.name}")
            print(f"   Contact: {client.contact_person or 'N/A'}")
            print(f"   Phone: {client.phone or 'N/A'}")
        else:
            missing.append(code)
            print(f"\n❌ {code}: NOT FOUND")
    
    if missing:
        print(f"\n⚠️  Missing clients: {', '.join(missing)}")
        print("Please create these clients before running migration.")
        return None
    
    return clients


def scan_projects(client_codes, base_path):
    """Scan all project directories for the clients."""
    print("\n" + "="*70)
    print("STEP 2: SCAN PROJECT DIRECTORIES")
    print("="*70)
    
    all_scans = {}
    
    for client_code in client_codes:
        print(f"\n{'='*70}")
        print(f"SCANNING: {client_code}")
        print(f"{'='*70}")
        
        projects_path = Path(base_path) / client_code / '1.Projects'
        
        if not projects_path.exists():
            print(f"⚠️  Directory not found: {projects_path}")
            all_scans[client_code] = []
            continue
        
        # Get all project folders
        project_folders = [d for d in projects_path.iterdir() if d.is_dir()]
        
        if not project_folders:
            print(f"⚠️  No project folders found")
            all_scans[client_code] = []
            continue
        
        print(f"\n📁 Found {len(project_folders)} project folder(s):")
        
        scan_results = []
        for folder in sorted(project_folders):
            # Count files
            design_files = list(folder.glob('*.dxf')) + list(folder.glob('*.lbrn2'))
            documents = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() not in ['.dxf', '.lbrn2']]
            
            print(f"\n   📂 {folder.name}")
            print(f"      Design Files: {len(design_files)}")
            print(f"      Documents: {len(documents)}")
            
            scan_results.append({
                'folder': folder.name,
                'design_files': len(design_files),
                'documents': len(documents)
            })
        
        all_scans[client_code] = scan_results
    
    return all_scans


def print_preview(all_scans):
    """Print migration preview summary."""
    print("\n" + "="*70)
    print("MIGRATION PREVIEW SUMMARY")
    print("="*70)
    
    total_projects = 0
    total_design_files = 0
    total_documents = 0
    
    for client_code, scans in all_scans.items():
        projects = len(scans)
        design_files = sum(s['design_files'] for s in scans)
        documents = sum(s['documents'] for s in scans)
        
        print(f"\n{client_code}:")
        print(f"   Projects: {projects}")
        print(f"   Design Files: {design_files}")
        print(f"   Documents: {documents}")
        
        total_projects += projects
        total_design_files += design_files
        total_documents += documents
    
    print(f"\n{'='*70}")
    print("TOTAL:")
    print(f"   Projects: {total_projects}")
    print(f"   Design Files: {total_design_files}")
    print(f"   Documents: {total_documents}")
    print("="*70)
    
    return total_projects, total_design_files, total_documents


def migrate_client(client_code, client, base_path, default_status='Completed'):
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
    print("PROFILES MIGRATION: CL-0004 through CL-0008")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Configuration
        client_codes = ['CL-0004', 'CL-0005', 'CL-0006', 'CL-0007', 'CL-0008']
        base_path = 'profiles_import'
        default_status = 'Completed'  # Must match Project.STATUS_COMPLETED
        
        # Print configuration
        print_config()
        
        # Step 1: Verify clients exist
        clients = verify_clients(client_codes)
        if not clients:
            print("\n❌ Migration aborted - missing clients")
            return
        
        # Step 2: Scan project directories
        all_scans = scan_projects(client_codes, base_path)
        
        # Step 3: Print preview
        total_projects, total_design_files, total_documents = print_preview(all_scans)
        
        if total_projects == 0:
            print("\n⚠️  No projects found to migrate")
            return
        
        # Step 4: Confirm migration
        print("\n" + "="*70)
        print("CONFIRMATION REQUIRED")
        print("="*70)
        print("\nThis will:")
        print("   1. Create project records in the database")
        print("   2. Upload all design files and documents")
        print(f"   3. Set project status to: '{default_status}'")
        print("   4. Link all files to their respective projects")
        
        response = input("\n⚠️  Proceed with migration? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Migration cancelled by user")
            return
        
        # Step 5: Execute migration
        print("\n" + "="*70)
        print("STEP 3: EXECUTE MIGRATION")
        print("="*70)
        
        results = {}
        for client_code in client_codes:
            if all_scans[client_code]:  # Only migrate if there are projects
                results[client_code] = migrate_client(
                    client_code,
                    clients[client_code],
                    base_path,
                    default_status
                )
            else:
                print(f"\n⚠️  Skipping {client_code} - no projects found")
                results[client_code] = {
                    'projects_created': 0,
                    'design_files_uploaded': 0,
                    'documents_uploaded': 0,
                    'warnings': [],
                    'errors': []
                }
        
        # Step 6: Final summary
        print("\n" + "="*70)
        print("MIGRATION COMPLETE - FINAL SUMMARY")
        print("="*70)
        
        total_projects_created = 0
        total_files_uploaded = 0
        total_docs_uploaded = 0
        total_warnings = 0
        total_errors = 0
        
        for client_code, stats in results.items():
            client_name = clients[client_code].name
            print(f"\n{client_code} ({client_name}):")
            print(f"   ✅ Projects: {stats['projects_created']}")
            print(f"   ✅ Design Files: {stats['design_files_uploaded']}")
            print(f"   ✅ Documents: {stats['documents_uploaded']}")
            if stats['errors']:
                print(f"   ❌ Errors: {len(stats['errors'])}")
            
            total_projects_created += stats['projects_created']
            total_files_uploaded += stats['design_files_uploaded']
            total_docs_uploaded += stats['documents_uploaded']
            total_warnings += len(stats['warnings'])
            total_errors += len(stats['errors'])
        
        print(f"\n{'='*70}")
        print("GRAND TOTAL:")
        print(f"   Projects Created: {total_projects_created}")
        print(f"   Design Files Uploaded: {total_files_uploaded}")
        print(f"   Documents Uploaded: {total_docs_uploaded}")
        print(f"   Warnings: {total_warnings}")
        print(f"   Errors: {total_errors}")
        print("="*70)
        
        if total_errors > 0:
            print(f"\n⚠️  Migration completed with {total_errors} error(s)")
        else:
            print("\n🎉 Migration completed successfully!")
        
        print("\nNext steps:")
        print("   1. Verify the migrated projects in the web application")
        print("   2. Check that all files are accessible")
        print(f"   3. Confirm project statuses are set to '{default_status}'")


if __name__ == '__main__':
    main()

