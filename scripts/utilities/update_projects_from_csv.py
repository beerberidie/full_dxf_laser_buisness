#!/usr/bin/env python3
"""
Laser OS - Project Update Script
=================================
Update existing projects from CSV file (exported or manually created).

This script:
1. Reads project data from CSV (supports both export and import formats)
2. Updates existing projects based on project_code
3. Optionally creates new projects if they don't exist
4. Validates data before updating
5. Provides detailed progress reporting

Usage:
    # Update only (skip non-existent projects)
    python update_projects_from_csv.py projects_export_2025-10-17.csv
    
    # Update existing and create new projects
    python update_projects_from_csv.py projects_export_2025-10-17.csv --create-new
    
    # Validate only (dry run)
    python update_projects_from_csv.py projects_export_2025-10-17.csv --validate-only
    
    # Show preview before updating
    python update_projects_from_csv.py projects_export_2025-10-17.csv --preview

Requirements:
    - CSV file with project_code column (required for matching)
    - Database must be initialized and accessible
"""

import os
import sys
import csv
import argparse
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Project, Client


class ProjectUpdater:
    """Handles updating projects from CSV data."""
    
    def __init__(self, app):
        self.app = app
        self.stats = {
            'projects_updated': 0,
            'projects_created': 0,
            'projects_skipped': 0,
            'projects_not_found': 0,
            'errors': []
        }
        
    def log(self, message: str, level: str = 'INFO'):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '📋',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'PROGRESS': '⏳',
            'PREVIEW': '👁️'
        }.get(level, 'ℹ️')
        print(f"[{timestamp}] {prefix} {message}")
        
    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string in various formats."""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        
        # Try different date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',  # Export format with timestamp
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.date() if isinstance(parsed, datetime) else parsed
            except ValueError:
                continue
                
        self.log(f"Could not parse date: {date_str}", 'WARNING')
        return None
        
    def parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse datetime string."""
        if not datetime_str or datetime_str.strip() == '':
            return None
            
        datetime_str = datetime_str.strip()
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
                
        return None
        
    def parse_decimal(self, value: str) -> Optional[Decimal]:
        """Parse decimal value."""
        if not value or value.strip() == '':
            return None
        try:
            return Decimal(str(value).strip().replace(',', ''))
        except:
            return None
            
    def parse_int(self, value: str) -> Optional[int]:
        """Parse integer value."""
        if not value or value.strip() == '':
            return None
        try:
            return int(str(value).strip())
        except ValueError:
            return None
            
    def parse_bool(self, value: str) -> bool:
        """Parse boolean value - supports multiple formats."""
        if not value:
            return False
        value_str = str(value).strip().lower()
        return value_str in ['true', 'yes', '1', 'y', 't']
        
    def normalize_column_name(self, col: str) -> str:
        """Normalize column names to handle different formats."""
        # Map export format columns to import format
        column_mapping = {
            'project_name': 'name',
            'estimated_cut_time_minutes': 'estimated_cut_time',
            'drawing_creation_time_minutes': 'drawing_creation_time',
        }
        return column_mapping.get(col, col)
        
    def get_updatable_fields(self) -> List[str]:
        """Get list of fields that can be updated."""
        return [
            'name',
            'description',
            'status',
            'quote_date',
            'approval_date',
            'due_date',
            'completion_date',
            'quoted_price',
            'final_price',
            'notes',
            'material_type',
            'material_thickness',
            'material_quantity_sheets',
            'parts_quantity',
            'estimated_cut_time',
            'drawing_creation_time',
            'number_of_bins',
            'scheduled_cut_date',
            'pop_received',
            'pop_received_date',
            'pop_deadline',
            'client_notified',
            'client_notified_date',
            'delivery_confirmed',
            'delivery_confirmed_date'
        ]
        
    def extract_project_data(self, row: Dict) -> Dict:
        """Extract and normalize project data from CSV row."""
        data = {}
        
        # Normalize column names
        normalized_row = {self.normalize_column_name(k): v for k, v in row.items()}
        
        # Map CSV columns to database fields
        field_mappings = {
            'name': ('name', str),
            'description': ('description', str),
            'status': ('status', str),
            'quote_date': ('quote_date', self.parse_date),
            'approval_date': ('approval_date', self.parse_date),
            'due_date': ('due_date', self.parse_date),
            'completion_date': ('completion_date', self.parse_date),
            'quoted_price': ('quoted_price', self.parse_decimal),
            'final_price': ('final_price', self.parse_decimal),
            'notes': ('notes', str),
            'material_type': ('material_type', str),
            'material_thickness': ('material_thickness_mm', self.parse_decimal),
            'material_quantity_sheets': ('material_quantity_sheets', self.parse_int),
            'parts_quantity': ('parts_quantity', self.parse_int),
            'estimated_cut_time': ('estimated_cut_time', self.parse_int),
            'drawing_creation_time': ('drawing_creation_time', self.parse_int),
            'number_of_bins': ('number_of_bins', self.parse_int),
            'scheduled_cut_date': ('scheduled_cut_date', self.parse_date),
            'pop_received': ('pop_received', self.parse_bool),
            'pop_received_date': ('pop_received_date', self.parse_date),
            'pop_deadline': ('pop_deadline', self.parse_date),
            'client_notified': ('client_notified', self.parse_bool),
            'client_notified_date': ('client_notified_date', self.parse_datetime),
            'delivery_confirmed': ('delivery_confirmed', self.parse_bool),
            'delivery_confirmed_date': ('delivery_confirmed_date', self.parse_date)
        }
        
        for db_field, (csv_field, parser) in field_mappings.items():
            if csv_field in normalized_row:
                value = normalized_row[csv_field]
                if value and str(value).strip():
                    if parser == str:
                        data[db_field] = str(value).strip()
                    else:
                        parsed = parser(value)
                        if parsed is not None:
                            data[db_field] = parsed
        
        return data

    def preview_changes(self, project: Project, updates: Dict) -> None:
        """Preview changes that will be made to a project."""
        self.log(f"\nProject: {project.project_code} - {project.name}", 'PREVIEW')

        if not updates:
            self.log("  No changes detected", 'PREVIEW')
            return

        for field, new_value in updates.items():
            old_value = getattr(project, field, None)
            if old_value != new_value:
                self.log(f"  {field}: {old_value} → {new_value}", 'PREVIEW')

    def update_project(self, project: Project, data: Dict, preview_only: bool = False) -> bool:
        """Update a project with new data."""
        try:
            # Track what changed
            changes = {}

            for field, new_value in data.items():
                old_value = getattr(project, field, None)

                # Compare values (handle None and type differences)
                if old_value != new_value:
                    # Special handling for Decimal comparison
                    if isinstance(old_value, Decimal) and isinstance(new_value, Decimal):
                        if old_value == new_value:
                            continue
                    changes[field] = new_value

            if not changes:
                return False  # No changes needed

            if preview_only:
                self.preview_changes(project, changes)
                return True

            # Apply changes
            for field, value in changes.items():
                setattr(project, field, value)

            return True

        except Exception as e:
            self.log(f"Error updating project {project.project_code}: {str(e)}", 'ERROR')
            return False

    def create_project(self, row: Dict, data: Dict, preview_only: bool = False) -> Optional[Project]:
        """Create a new project from CSV data."""
        try:
            # Get client
            client_code = row.get('client_code', '').strip()
            if not client_code:
                self.log("Cannot create project: client_code is required", 'ERROR')
                return None

            client = Client.query.filter_by(client_code=client_code).first()
            if not client:
                self.log(f"Cannot create project: Client {client_code} not found", 'ERROR')
                return None

            # Get or generate project code
            project_code = row.get('project_code', '').strip()
            if not project_code:
                # Generate new project code
                project_date = data.get('created_at', date.today())
                if isinstance(project_date, datetime):
                    project_date = project_date.date()
                project_code = self.generate_project_code(client_code, project_date)

            if preview_only:
                self.log(f"\nWould create new project: {project_code}", 'PREVIEW')
                for field, value in data.items():
                    self.log(f"  {field}: {value}", 'PREVIEW')
                return None

            # Create project
            project = Project(
                project_code=project_code,
                client_id=client.id,
                **data
            )

            return project

        except Exception as e:
            self.log(f"Error creating project: {str(e)}", 'ERROR')
            return None

    def generate_project_code(self, client_code: str, project_date: date) -> str:
        """Generate project code in format JB-yyyy-mm-CLxxxx-###."""
        # Format: JB-yyyy-mm-CLxxxx-###
        year_month = project_date.strftime('%Y-%m')
        prefix = f"JB-{year_month}-{client_code}-"

        # Find highest sequence number for this client/month
        result = db.session.execute(
            db.text(
                "SELECT project_code FROM projects "
                "WHERE project_code LIKE :prefix "
                "ORDER BY project_code DESC LIMIT 1"
            ),
            {'prefix': f"{prefix}%"}
        ).fetchone()

        if result and result[0]:
            try:
                last_seq = int(result[0].split('-')[-1])
                next_seq = last_seq + 1
            except (IndexError, ValueError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:03d}"

    def update_from_csv(self, csv_file: str, create_new: bool = False,
                       validate_only: bool = False, preview: bool = False) -> bool:
        """Update projects from CSV file."""
        self.log(f"Reading CSV file: {csv_file}")

        if not os.path.exists(csv_file):
            self.log(f"File not found: {csv_file}", 'ERROR')
            return False

        try:
            # Read CSV
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self.log(f"Found {len(rows)} project records to process")

            if validate_only or preview:
                mode = "VALIDATION" if validate_only else "PREVIEW"
                self.log(f"\n{'='*70}")
                self.log(f"{mode} MODE - No changes will be made")
                self.log(f"{'='*70}\n")

            # Process each row
            with self.app.app_context():
                for idx, row in enumerate(rows, start=2):
                    try:
                        # Get project code
                        project_code = row.get('project_code', '').strip()
                        if not project_code:
                            self.log(f"Row {idx}: Skipping - no project_code", 'WARNING')
                            self.stats['projects_skipped'] += 1
                            continue

                        # Extract data
                        data = self.extract_project_data(row)

                        # Find existing project
                        project = Project.query.filter_by(project_code=project_code).first()

                        if project:
                            # Update existing project
                            has_changes = self.update_project(project, data, preview_only=(validate_only or preview))

                            if has_changes:
                                if not validate_only and not preview:
                                    db.session.commit()
                                    self.log(f"Updated project: {project_code} - {project.name}", 'SUCCESS')
                                self.stats['projects_updated'] += 1
                            else:
                                self.log(f"Row {idx}: No changes for {project_code}", 'INFO')
                                self.stats['projects_skipped'] += 1

                        else:
                            # Project not found
                            if create_new:
                                # Create new project
                                new_project = self.create_project(row, data, preview_only=(validate_only or preview))

                                if new_project and not validate_only and not preview:
                                    db.session.add(new_project)
                                    db.session.commit()
                                    self.log(f"Created new project: {new_project.project_code} - {new_project.name}", 'SUCCESS')

                                if new_project or validate_only or preview:
                                    self.stats['projects_created'] += 1
                            else:
                                self.log(f"Row {idx}: Project {project_code} not found (use --create-new to create)", 'WARNING')
                                self.stats['projects_not_found'] += 1

                    except Exception as e:
                        db.session.rollback()
                        error_msg = f"Row {idx}: Error processing project: {str(e)}"
                        self.log(error_msg, 'ERROR')
                        self.stats['errors'].append(error_msg)

            return True

        except Exception as e:
            self.log(f"Error reading CSV file: {str(e)}", 'ERROR')
            return False

    def print_summary(self):
        """Print summary of update operation."""
        self.log("\n" + "="*70)
        self.log("UPDATE SUMMARY")
        self.log("="*70)

        self.log(f"\n✅ Projects Updated: {self.stats['projects_updated']}")
        self.log(f"➕ Projects Created: {self.stats['projects_created']}")
        self.log(f"⏭️  Projects Skipped (no changes): {self.stats['projects_skipped']}")
        self.log(f"❓ Projects Not Found: {self.stats['projects_not_found']}")

        if self.stats['errors']:
            self.log(f"\n❌ Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                self.log(f"  - {error}", 'ERROR')
            if len(self.stats['errors']) > 10:
                self.log(f"  ... and {len(self.stats['errors']) - 10} more errors", 'ERROR')

        self.log("\n" + "="*70 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Update Laser OS projects from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update existing projects only
  python update_projects_from_csv.py data/exports/projects_export_2025-10-17.csv

  # Update existing and create new projects
  python update_projects_from_csv.py projects.csv --create-new

  # Preview changes without updating
  python update_projects_from_csv.py projects.csv --preview

  # Validate data only (dry run)
  python update_projects_from_csv.py projects.csv --validate-only

Supported CSV Formats:
  - Export format (from export_projects_to_csv.py)
  - Import template format (projects_import_template.csv)
  - Custom CSV with project_code column (required)

Column Name Mapping:
  - project_name → name
  - estimated_cut_time_minutes → estimated_cut_time
  - drawing_creation_time_minutes → drawing_creation_time

Boolean Values:
  - Accepts: Yes/No, true/false, 1/0, Y/N, T/F (case-insensitive)
        """
    )

    parser.add_argument('csv_file', help='CSV file containing project data')
    parser.add_argument('--create-new', action='store_true',
                       help='Create new projects if they don\'t exist')
    parser.add_argument('--validate-only', action='store_true',
                       help='Validate data without making changes (dry run)')
    parser.add_argument('--preview', action='store_true',
                       help='Preview changes without updating database')

    args = parser.parse_args()

    # Print header
    print("\n" + "="*70)
    print("LASER OS - PROJECT UPDATE FROM CSV")
    print("="*70)

    # Create Flask app
    app = create_app()

    # Create updater
    updater = ProjectUpdater(app)

    # Run update
    success = updater.update_from_csv(
        args.csv_file,
        create_new=args.create_new,
        validate_only=args.validate_only,
        preview=args.preview
    )

    # Print summary
    updater.print_summary()

    if args.validate_only:
        print("✅ Validation complete - no changes were made")
    elif args.preview:
        print("👁️  Preview complete - no changes were made")
    elif success:
        print("✅ Update complete!")
    else:
        print("❌ Update failed - check errors above")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

