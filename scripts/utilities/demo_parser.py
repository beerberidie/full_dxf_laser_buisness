"""
Demo script for ProfilesParser.

This script demonstrates how to use the ProfilesParser with real-world examples
from the profiles_import directory structure.
"""

from app.services.profiles_parser import ProfilesParser
import json


def demo_parse_project():
    """Demonstrate parsing a complete project folder and its files."""
    print("\n" + "="*70)
    print("DEMO: Parsing a Complete Project")
    print("="*70)
    
    # Example project folder
    folder_name = "0001-Gas Cover box 1 to 1 ratio-10.15.2025"
    
    print(f"\nProject Folder: {folder_name}")
    print("-" * 70)
    
    # Parse folder
    folder_data = ProfilesParser.parse_project_folder(folder_name)
    
    if folder_data:
        print("\n📁 Folder Metadata:")
        print(f"   Project Number: {folder_data['project_number']}")
        print(f"   Description: {folder_data['description']}")
        print(f"   Date Created: {folder_data['date_created'].strftime('%Y-%m-%d')}")
    
    # Example files in this project
    files = [
        "0001-Full Gas Box Version1-Galv-1mm-x1.dxf",
        "0001-Full Gas Box Version1-Galv-1mm-x1.lbrn2",
        "0001-Cover Plate-Galv-1mm-x1.dxf",
        "quote.pdf",
    ]
    
    print("\n📄 Files in Project:")
    print("-" * 70)
    
    design_files = []
    documents = []
    
    for file_name in files:
        print(f"\n   File: {file_name}")
        
        # Check if it's a design file (has the pattern)
        file_data = ProfilesParser.parse_file_name(file_name)
        
        if file_data:
            # It's a design file with metadata
            print(f"      Type: Design File")
            print(f"      Part: {file_data['part_description']}")
            print(f"      Material: {file_data['material_type']}")
            print(f"      Thickness: {file_data['thickness']} mm")
            print(f"      Quantity: {file_data['quantity']}")
            design_files.append(file_data)
        else:
            # It's a document
            print(f"      Type: Document")
            documents.append(file_name)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nProject: {folder_data['description']}")
    print(f"Created: {folder_data['date_created'].strftime('%Y-%m-%d')}")
    print(f"Design Files: {len(design_files)}")
    print(f"Documents: {len(documents)}")
    
    if design_files:
        # Get material info from first design file
        first_file = design_files[0]
        print(f"\nMaterial: {first_file['material_type']}")
        print(f"Thickness: {first_file['thickness']} mm")
        print(f"Total Parts: {sum(f['quantity'] for f in design_files)}")


def demo_multiple_projects():
    """Demonstrate parsing multiple projects."""
    print("\n" + "="*70)
    print("DEMO: Parsing Multiple Projects")
    print("="*70)
    
    projects = [
        {
            'folder': "0001-Gas Cover box-10.15.2025",
            'files': [
                "0001-Full Gas Box-Galv-1mm-x1.dxf",
                "0001-Cover-Galv-1mm-x2.dxf",
            ]
        },
        {
            'folder': "0002-Brackets Set-10.16.2025",
            'files': [
                "0002-Bracket A-SS-2mm-x10.dxf",
                "0002-Bracket B-SS-2mm-x10.dxf",
            ]
        },
        {
            'folder': "0003-Signage Letters-10.17.2025",
            'files': [
                "0003-Letter A-Al-3mm-x1.dxf",
                "0003-Letter B-Al-3mm-x1.dxf",
                "0003-Letter C-Al-3mm-x1.dxf",
            ]
        },
    ]
    
    print("\n{:<10} {:<30} {:<15} {:<10} {:<10}".format(
        "Proj #", "Description", "Material", "Thickness", "Parts"
    ))
    print("-" * 70)
    
    for project in projects:
        folder_data = ProfilesParser.parse_project_folder(project['folder'])
        
        if folder_data:
            # Parse first file to get material info
            first_file = ProfilesParser.parse_file_name(project['files'][0])
            
            if first_file:
                total_parts = 0
                for file_name in project['files']:
                    file_data = ProfilesParser.parse_file_name(file_name)
                    if file_data:
                        total_parts += file_data['quantity']
                
                print("{:<10} {:<30} {:<15} {:<10} {:<10}".format(
                    folder_data['project_number'],
                    folder_data['description'][:28],
                    first_file['material_type'][:13],
                    f"{first_file['thickness']} mm",
                    total_parts
                ))


def demo_material_variations():
    """Demonstrate parsing different material codes."""
    print("\n" + "="*70)
    print("DEMO: Material Code Variations")
    print("="*70)
    
    files = [
        "0001-Part-Galv-1mm-x1.dxf",
        "0002-Part-SS-2mm-x1.dxf",
        "0003-Part-MS-3mm-x1.dxf",
        "0004-Part-Al-1.5mm-x1.dxf",
        "0005-Part-Brass-2mm-x1.dxf",
        "0006-Part-Copper-1mm-x1.dxf",
        "0007-Part-Stainless-2mm-x1.dxf",
        "0008-Part-Mild-3mm-x1.dxf",
    ]
    
    print("\n{:<15} {:<20}".format("Code", "Full Material Name"))
    print("-" * 40)
    
    for file_name in files:
        file_data = ProfilesParser.parse_file_name(file_name)
        if file_data:
            print("{:<15} {:<20}".format(
                file_data['material_code'],
                file_data['material_type']
            ))


def demo_thickness_variations():
    """Demonstrate parsing different thickness formats."""
    print("\n" + "="*70)
    print("DEMO: Thickness Format Variations")
    print("="*70)
    
    files = [
        "0001-Part-Galv-1mm-x1.dxf",
        "0001-Part-Galv-1.5mm-x1.dxf",
        "0001-Part-Galv-2mm-x1.dxf",
        "0001-Part-Galv-0.5mm-x1.dxf",
        "0001-Part-Galv-3m-x1.dxf",
    ]
    
    print("\n{:<20} {:<15}".format("Thickness String", "Parsed Value"))
    print("-" * 40)
    
    for file_name in files:
        file_data = ProfilesParser.parse_file_name(file_name)
        if file_data:
            print("{:<20} {:<15}".format(
                file_data['thickness_str'],
                f"{file_data['thickness']} mm"
            ))


def demo_date_variations():
    """Demonstrate parsing different date formats."""
    print("\n" + "="*70)
    print("DEMO: Date Format Variations")
    print("="*70)
    
    folders = [
        "0001-Project-10.15.2025",
        "0001-Project-15-10-2025",
        "0001-Project-2025-10-15",
        "0001-Project-10/15/2025",
    ]
    
    print("\n{:<20} {:<15}".format("Date String", "Parsed Date"))
    print("-" * 40)
    
    for folder_name in folders:
        folder_data = ProfilesParser.parse_project_folder(folder_name)
        if folder_data:
            print("{:<20} {:<15}".format(
                folder_data['date_str'],
                folder_data['date_created'].strftime('%Y-%m-%d')
            ))


def demo_json_output():
    """Demonstrate JSON output for API integration."""
    print("\n" + "="*70)
    print("DEMO: JSON Output for API Integration")
    print("="*70)
    
    folder_name = "0001-Gas Cover box-10.15.2025"
    file_name = "0001-Full Gas Box-Galv-1mm-x1.dxf"
    
    folder_data = ProfilesParser.parse_project_folder(folder_name)
    file_data = ProfilesParser.parse_file_name(file_name)
    
    # Prepare data for JSON serialization
    output = {
        'project': {
            'project_number': folder_data['project_number'],
            'description': folder_data['description'],
            'date_created': folder_data['date_created'].isoformat(),
        },
        'design_file': {
            'part_description': file_data['part_description'],
            'material_type': file_data['material_type'],
            'thickness': float(file_data['thickness']),
            'quantity': file_data['quantity'],
        }
    }
    
    print("\nJSON Output:")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROFILES PARSER - DEMONSTRATION")
    print("="*70)
    
    try:
        demo_parse_project()
        demo_multiple_projects()
        demo_material_variations()
        demo_thickness_variations()
        demo_date_variations()
        demo_json_output()
        
        print("\n" + "="*70)
        print("DEMONSTRATION COMPLETE")
        print("="*70)
        print("\nThe ProfilesParser is ready to use!")
        print("Next step: Create test data in profiles_import directory")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

