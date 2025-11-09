"""
Test ProfilesParser with real data from profiles_import/CL-0003.

This script validates the parser against actual production data.
"""

import os
from pathlib import Path
from app.services.profiles_parser import ProfilesParser
from app import create_app, db
from app.models import Client


def check_client_exists():
    """Verify client CL-0003 exists in database."""
    print("\n" + "="*70)
    print("STEP 1: VERIFY CLIENT IN DATABASE")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        client = Client.query.filter_by(client_code='CL-0003').first()
        
        if client:
            print(f"\n✅ Client Found: {client.name}")
            print(f"   Client Code: {client.client_code}")
            print(f"   Client ID: {client.id}")
            return True
        else:
            print("\n❌ Client NOT FOUND")
            print("   Client code 'CL-0003' does not exist in the database.")
            return False


def scan_directory_structure():
    """Scan the profiles_import/CL-0003 directory structure."""
    print("\n" + "="*70)
    print("STEP 2: SCAN DIRECTORY STRUCTURE")
    print("="*70)
    
    base_path = Path("profiles_import/CL-0003/1.Projects")
    
    if not base_path.exists():
        print(f"\n❌ Directory not found: {base_path}")
        return []
    
    print(f"\n📁 Scanning: {base_path}")
    
    projects = []
    
    # Get all project folders
    for project_folder in sorted(base_path.iterdir()):
        if project_folder.is_dir():
            project_data = {
                'folder_name': project_folder.name,
                'folder_path': project_folder,
                'files': []
            }
            
            # Get all files in the project folder
            for file_path in sorted(project_folder.iterdir()):
                if file_path.is_file():
                    project_data['files'].append({
                        'file_name': file_path.name,
                        'file_path': file_path,
                        'extension': file_path.suffix.lower()
                    })
            
            projects.append(project_data)
    
    print(f"\n✅ Found {len(projects)} project folder(s)")
    for project in projects:
        print(f"   - {project['folder_name']} ({len(project['files'])} files)")
    
    return projects


def test_folder_parsing(projects):
    """Test parsing project folder names."""
    print("\n" + "="*70)
    print("STEP 3: TEST PROJECT FOLDER PARSING")
    print("="*70)
    
    results = []
    
    for project in projects:
        folder_name = project['folder_name']
        print(f"\n📁 Testing: {folder_name}")
        print("-" * 70)
        
        parsed = ProfilesParser.parse_project_folder(folder_name)
        
        if parsed:
            print(f"   ✅ Successfully parsed")
            print(f"      Project Number: {parsed['project_number']}")
            print(f"      Description: {parsed['description']}")
            print(f"      Date String: {parsed['date_str']}")
            print(f"      Date Created: {parsed['date_created'].strftime('%Y-%m-%d')}")
            
            results.append({
                'folder_name': folder_name,
                'success': True,
                'parsed': parsed
            })
        else:
            print(f"   ❌ FAILED to parse")
            results.append({
                'folder_name': folder_name,
                'success': False,
                'parsed': None
            })
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'='*70}")
    print(f"Folder Parsing Summary: {success_count}/{len(results)} successful")
    print(f"{'='*70}")
    
    return results


def test_file_parsing(projects):
    """Test parsing file names."""
    print("\n" + "="*70)
    print("STEP 4: TEST FILE NAME PARSING")
    print("="*70)
    
    all_results = []
    
    for project in projects:
        print(f"\n📁 Project: {project['folder_name']}")
        print("-" * 70)
        
        for file_info in project['files']:
            file_name = file_info['file_name']
            extension = file_info['extension']
            
            print(f"\n   📄 File: {file_name}")
            
            parsed = ProfilesParser.parse_file_name(file_name)
            
            if parsed:
                print(f"      ✅ Successfully parsed")
                print(f"         Project Number: {parsed['project_number']}")
                print(f"         Part Description: {parsed['part_description']}")
                print(f"         Material Code: {parsed['material_code']}")
                print(f"         Material Type: {parsed['material_type']}")
                print(f"         Thickness: {parsed['thickness']} mm")
                print(f"         Quantity: {parsed['quantity']}")
                print(f"         File Type: {'Design File' if extension in ['.dxf', '.lbrn2'] else 'Document'}")
                
                all_results.append({
                    'file_name': file_name,
                    'success': True,
                    'parsed': parsed,
                    'extension': extension
                })
            else:
                print(f"      ℹ️  Not a design file (no metadata pattern)")
                print(f"         File Type: Document")
                
                all_results.append({
                    'file_name': file_name,
                    'success': False,
                    'parsed': None,
                    'extension': extension
                })
    
    # Summary
    success_count = sum(1 for r in all_results if r['success'])
    design_files = [r for r in all_results if r['extension'] in ['.dxf', '.lbrn2']]
    design_parsed = sum(1 for r in design_files if r['success'])
    
    print(f"\n{'='*70}")
    print(f"File Parsing Summary:")
    print(f"  Total Files: {len(all_results)}")
    print(f"  Design Files (DXF/LBRN2): {len(design_files)}")
    print(f"  Design Files Parsed: {design_parsed}/{len(design_files)}")
    print(f"  Documents: {len(all_results) - len(design_files)}")
    print(f"{'='*70}")
    
    return all_results


def validate_metadata(projects, folder_results, file_results):
    """Validate that extracted metadata is correct."""
    print("\n" + "="*70)
    print("STEP 5: VALIDATE EXTRACTED METADATA")
    print("="*70)
    
    issues = []
    
    for i, project in enumerate(projects):
        folder_result = folder_results[i]
        
        if not folder_result['success']:
            issues.append(f"❌ Folder '{project['folder_name']}' failed to parse")
            continue
        
        parsed_folder = folder_result['parsed']
        
        # Check project number consistency
        project_number = parsed_folder['project_number']
        
        # Get files for this project
        project_files = [f for f in file_results 
                        if any(file_info['file_name'] == f['file_name'] 
                              for file_info in project['files'])]
        
        for file_result in project_files:
            if file_result['success']:
                parsed_file = file_result['parsed']
                
                # Validate project number matches
                if parsed_file['project_number'] != project_number:
                    issues.append(
                        f"❌ Project number mismatch: "
                        f"Folder={project_number}, File={parsed_file['project_number']} "
                        f"in {file_result['file_name']}"
                    )
                
                # Validate material type is valid
                valid_materials = [
                    'Mild Steel', 'Stainless Steel', 'Aluminum', 
                    'Brass', 'Copper', 'Galvanized Steel', 'Other'
                ]
                if parsed_file['material_type'] not in valid_materials:
                    issues.append(
                        f"⚠️  Unknown material type: {parsed_file['material_type']} "
                        f"in {file_result['file_name']}"
                    )
                
                # Validate thickness is positive
                if parsed_file['thickness'] <= 0:
                    issues.append(
                        f"❌ Invalid thickness: {parsed_file['thickness']} "
                        f"in {file_result['file_name']}"
                    )
                
                # Validate quantity is positive
                if parsed_file['quantity'] <= 0:
                    issues.append(
                        f"❌ Invalid quantity: {parsed_file['quantity']} "
                        f"in {file_result['file_name']}"
                    )
    
    if issues:
        print("\n⚠️  Validation Issues Found:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ All metadata validated successfully!")
        print("   - Project numbers consistent")
        print("   - Material types valid")
        print("   - Thickness values positive")
        print("   - Quantity values positive")
    
    return len(issues) == 0


def generate_summary_report(projects, folder_results, file_results):
    """Generate a summary report of the test."""
    print("\n" + "="*70)
    print("FINAL SUMMARY REPORT")
    print("="*70)
    
    print(f"\n📊 Statistics:")
    print(f"   Client Code: CL-0003")
    print(f"   Client Name: Magnium Machines")
    print(f"   Total Projects: {len(projects)}")
    print(f"   Total Files: {len(file_results)}")
    
    design_files = [f for f in file_results if f['extension'] in ['.dxf', '.lbrn2']]
    documents = [f for f in file_results if f['extension'] not in ['.dxf', '.lbrn2']]
    
    print(f"   Design Files: {len(design_files)}")
    print(f"   Documents: {len(documents)}")
    
    print(f"\n✅ Parsing Success Rates:")
    folder_success = sum(1 for r in folder_results if r['success'])
    print(f"   Folders: {folder_success}/{len(folder_results)} ({folder_success/len(folder_results)*100:.1f}%)")

    file_success = sum(1 for r in file_results if r['success'])
    design_success = sum(1 for r in design_files if r['success'])
    design_pct = (design_success/len(design_files)*100) if len(design_files) > 0 else 0
    print(f"   Design Files: {design_success}/{len(design_files)} ({design_pct:.1f}%)")
    
    print(f"\n📋 Project Details:")
    for i, project in enumerate(projects):
        folder_result = folder_results[i]
        if folder_result['success']:
            parsed = folder_result['parsed']
            project_files = [f for f in file_results 
                           if any(file_info['file_name'] == f['file_name'] 
                                 for file_info in project['files'])]
            design_count = sum(1 for f in project_files if f['extension'] in ['.dxf', '.lbrn2'])
            
            print(f"\n   Project {parsed['project_number']}: {parsed['description']}")
            print(f"      Date: {parsed['date_created'].strftime('%Y-%m-%d')}")
            print(f"      Files: {len(project_files)} ({design_count} design files)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROFILES PARSER - REAL DATA TEST")
    print("Testing with: profiles_import/CL-0003")
    print("="*70)
    
    try:
        # Step 1: Check client exists
        if not check_client_exists():
            print("\n❌ Cannot proceed without client in database")
            exit(1)
        
        # Step 2: Scan directory
        projects = scan_directory_structure()
        if not projects:
            print("\n❌ No projects found to test")
            exit(1)
        
        # Step 3: Test folder parsing
        folder_results = test_folder_parsing(projects)
        
        # Step 4: Test file parsing
        file_results = test_file_parsing(projects)
        
        # Step 5: Validate metadata
        validation_passed = validate_metadata(projects, folder_results, file_results)
        
        # Step 6: Generate summary
        generate_summary_report(projects, folder_results, file_results)
        
        # Final result
        print("\n" + "="*70)
        if validation_passed:
            print("✅ ALL TESTS PASSED - Parser is ready for production!")
        else:
            print("⚠️  TESTS COMPLETED WITH WARNINGS - Review issues above")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

