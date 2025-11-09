#!/usr/bin/env python3
"""
CSV Export Script for Laser OS Projects
Exports all projects from the database to a CSV file with comprehensive data.
"""

import os
import sys
import csv
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Project, Client


def format_value(value):
    """Format a value for CSV export, handling None and special types."""
    if value is None:
        return ''
    elif isinstance(value, bool):
        return 'Yes' if value else 'No'
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif hasattr(value, 'strftime'):  # Date object
        return value.strftime('%Y-%m-%d')
    else:
        return str(value)


def export_projects_to_csv(output_dir='data/exports', filename=None):
    """
    Export all projects to a CSV file.
    
    Args:
        output_dir (str): Directory to save the CSV file
        filename (str): Optional custom filename (default: projects_export_YYYY-MM-DD.csv)
    
    Returns:
        str: Path to the exported CSV file
    """
    app = create_app()
    
    with app.app_context():
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            filename = f'projects_export_{timestamp}.csv'
        
        csv_file_path = output_path / filename
        
        # Query all projects with client relationship
        projects = Project.query.join(Client).order_by(Project.created_at.desc()).all()
        
        if not projects:
            print("\n⚠️  No projects found in the database.")
            return None
        
        print(f"\n{'='*70}")
        print(f"EXPORTING {len(projects)} PROJECTS TO CSV")
        print(f"{'='*70}")
        
        # Define CSV columns
        columns = [
            # Basic Information
            'project_code',
            'project_name',
            'client_code',
            'client_name',
            'status',
            'description',
            
            # Timeline
            'quote_date',
            'approval_date',
            'due_date',
            'completion_date',
            'scheduled_cut_date',
            'created_at',
            'updated_at',
            
            # Pricing
            'quoted_price',
            'final_price',
            
            # Material & Production
            'material_type',
            'material_thickness_mm',
            'material_quantity_sheets',
            'parts_quantity',
            'estimated_cut_time_minutes',
            'number_of_bins',
            'drawing_creation_time_minutes',
            
            # POP (Proof of Payment) Tracking
            'pop_received',
            'pop_received_date',
            'pop_deadline',
            
            # Client Notification
            'client_notified',
            'client_notified_date',
            
            # Delivery Confirmation
            'delivery_confirmed',
            'delivery_confirmed_date',
            
            # File Counts
            'design_files_count',
            'documents_count',
            
            # Notes
            'notes',
        ]
        
        # Write to CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for project in projects:
                row = {
                    # Basic Information
                    'project_code': format_value(project.project_code),
                    'project_name': format_value(project.name),
                    'client_code': format_value(project.client.client_code),
                    'client_name': format_value(project.client.name),
                    'status': format_value(project.status),
                    'description': format_value(project.description),
                    
                    # Timeline
                    'quote_date': format_value(project.quote_date),
                    'approval_date': format_value(project.approval_date),
                    'due_date': format_value(project.due_date),
                    'completion_date': format_value(project.completion_date),
                    'scheduled_cut_date': format_value(project.scheduled_cut_date),
                    'created_at': format_value(project.created_at),
                    'updated_at': format_value(project.updated_at),
                    
                    # Pricing
                    'quoted_price': format_value(project.quoted_price),
                    'final_price': format_value(project.final_price),
                    
                    # Material & Production
                    'material_type': format_value(project.material_type),
                    'material_thickness_mm': format_value(project.material_thickness),
                    'material_quantity_sheets': format_value(project.material_quantity_sheets),
                    'parts_quantity': format_value(project.parts_quantity),
                    'estimated_cut_time_minutes': format_value(project.estimated_cut_time),
                    'number_of_bins': format_value(project.number_of_bins),
                    'drawing_creation_time_minutes': format_value(project.drawing_creation_time),
                    
                    # POP (Proof of Payment) Tracking
                    'pop_received': format_value(project.pop_received),
                    'pop_received_date': format_value(project.pop_received_date),
                    'pop_deadline': format_value(project.pop_deadline),
                    
                    # Client Notification
                    'client_notified': format_value(project.client_notified),
                    'client_notified_date': format_value(project.client_notified_date),
                    
                    # Delivery Confirmation
                    'delivery_confirmed': format_value(project.delivery_confirmed),
                    'delivery_confirmed_date': format_value(project.delivery_confirmed_date),
                    
                    # File Counts
                    'design_files_count': len(project.design_files),
                    'documents_count': len(project.documents),
                    
                    # Notes
                    'notes': format_value(project.notes),
                }
                
                writer.writerow(row)
        
        # Print summary
        print(f"\n✅ Export completed successfully!")
        print(f"\n📁 File saved to: {csv_file_path}")
        print(f"📊 Total projects exported: {len(projects)}")
        
        # Print statistics
        print(f"\n{'='*70}")
        print("EXPORT STATISTICS")
        print(f"{'='*70}")
        
        # Status breakdown
        status_counts = {}
        for project in projects:
            status = project.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\nProjects by Status:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        
        # Client breakdown
        client_counts = {}
        for project in projects:
            client_name = project.client.name
            client_counts[client_name] = client_counts.get(client_name, 0) + 1
        
        print("\nProjects by Client:")
        for client_name, count in sorted(client_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {client_name}: {count}")
        
        # Material breakdown
        material_counts = {}
        for project in projects:
            material = project.material_type or 'Not Specified'
            material_counts[material] = material_counts.get(material, 0) + 1
        
        print("\nProjects by Material Type:")
        for material, count in sorted(material_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {material}: {count}")
        
        # File statistics
        total_design_files = sum(len(p.design_files) for p in projects)
        total_documents = sum(len(p.documents) for p in projects)
        
        print(f"\nFile Statistics:")
        print(f"  Total Design Files: {total_design_files}")
        print(f"  Total Documents: {total_documents}")
        print(f"  Average Design Files per Project: {total_design_files / len(projects):.1f}")
        print(f"  Average Documents per Project: {total_documents / len(projects):.1f}")
        
        # Pricing statistics
        projects_with_quoted_price = [p for p in projects if p.quoted_price]
        if projects_with_quoted_price:
            total_quoted = sum(float(p.quoted_price) for p in projects_with_quoted_price)
            avg_quoted = total_quoted / len(projects_with_quoted_price)
            print(f"\nPricing Statistics:")
            print(f"  Projects with Quoted Price: {len(projects_with_quoted_price)}")
            print(f"  Total Quoted Value: R{total_quoted:,.2f}")
            print(f"  Average Quoted Price: R{avg_quoted:,.2f}")
        
        print(f"\n{'='*70}\n")
        
        return str(csv_file_path)


def main():
    """Main function."""
    print("\n" + "="*70)
    print("LASER OS - PROJECT CSV EXPORT")
    print("="*70)
    
    # Export projects
    csv_file = export_projects_to_csv()
    
    if csv_file:
        print(f"✅ Export completed successfully!")
        print(f"\n📄 CSV file: {csv_file}")
        print(f"\nYou can now:")
        print(f"  1. Open the CSV file in Excel or Google Sheets")
        print(f"  2. Use it for reporting and analysis")
        print(f"  3. Import it into other systems")
        print(f"  4. Create backups of your project data")
    else:
        print(f"❌ Export failed - no projects found")


if __name__ == '__main__':
    main()

