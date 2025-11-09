#!/usr/bin/env python3
"""
Laser OS - Bulk Data Import Script
===================================
Import clients, projects, and associated files from CSV/Excel templates.

This script:
1. Validates import data before processing
2. Imports clients with all contact information
3. Imports projects linked to clients
4. Uploads and links all project files (DXF, documents, images)
5. Maintains data integrity with transaction rollback on errors
6. Provides detailed progress reporting and error logging

Usage:
    python bulk_import.py --clients clients_import.csv
    python bulk_import.py --projects projects_import.csv --files-dir ./import_files
    python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./files
    python bulk_import.py --validate-only --clients clients.csv --projects projects.csv

Requirements:
    - CSV/Excel file with proper headers (see template files)
    - Files organized in the specified directory structure
    - Database must be initialized and accessible
"""

import os
import sys
import csv
import argparse
import shutil
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import sqlite3
import json

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Client, Project, DesignFile, ProjectDocument
from werkzeug.utils import secure_filename
import uuid


class BulkImporter:
    """Handles bulk import of clients, projects, and files."""
    
    def __init__(self, app, files_base_dir: Optional[str] = None):
        self.app = app
        self.files_base_dir = Path(files_base_dir) if files_base_dir else None
        self.stats = {
            'clients_imported': 0,
            'clients_skipped': 0,
            'projects_imported': 0,
            'projects_skipped': 0,
            'files_uploaded': 0,
            'files_failed': 0,
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
            'PROGRESS': '⏳'
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
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        self.log(f"Could not parse date: {date_str}", 'WARNING')
        return None
        
    def parse_decimal(self, value: str) -> Optional[float]:
        """Parse decimal value."""
        if not value or value.strip() == '':
            return None
        try:
            return float(str(value).strip().replace(',', ''))
        except ValueError:
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
        """Parse boolean value."""
        if not value:
            return False
        value_str = str(value).strip().lower()
        return value_str in ['true', 'yes', '1', 'y', 't']
        
    def generate_client_code(self) -> str:
        """Generate next available client code."""
        with self.app.app_context():
            # Get the highest client code
            result = db.session.execute(
                db.text("SELECT client_code FROM clients ORDER BY client_code DESC LIMIT 1")
            ).fetchone()
            
            if result and result[0]:
                # Extract number from CL-XXXX format
                last_code = result[0]
                try:
                    last_num = int(last_code.split('-')[1])
                    next_num = last_num + 1
                except (IndexError, ValueError):
                    next_num = 1
            else:
                next_num = 1
                
            return f"CL-{next_num:04d}"
            
    def generate_project_code(self, client_code: str, project_date: date) -> str:
        """Generate project code in format JB-yyyy-mm-CLxxxx-###."""
        with self.app.app_context():
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
            
    def validate_client_row(self, row: Dict, row_num: int) -> Tuple[bool, List[str]]:
        """Validate a client data row."""
        errors = []
        
        # Required fields
        if not row.get('name', '').strip():
            errors.append(f"Row {row_num}: Client name is required")
            
        # Email format (basic check)
        email = row.get('email', '').strip()
        if email and '@' not in email:
            errors.append(f"Row {row_num}: Invalid email format: {email}")
            
        return len(errors) == 0, errors
        
    def validate_project_row(self, row: Dict, row_num: int) -> Tuple[bool, List[str]]:
        """Validate a project data row."""
        errors = []
        
        # Required fields
        if not row.get('client_code', '').strip():
            errors.append(f"Row {row_num}: Client code is required")
        if not row.get('name', '').strip():
            errors.append(f"Row {row_num}: Project name is required")
            
        # Valid status
        status = row.get('status', '').strip()
        valid_statuses = ['Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled',
                         'Request', 'Quote & Approval', 'Approved (POP Received)',
                         'Queued (Scheduled for Cutting)']
        if status and status not in valid_statuses:
            errors.append(f"Row {row_num}: Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")
            
        return len(errors) == 0, errors

    def import_clients(self, csv_file: str, validate_only: bool = False) -> bool:
        """Import clients from CSV file."""
        self.log(f"{'Validating' if validate_only else 'Importing'} clients from: {csv_file}")

        if not os.path.exists(csv_file):
            self.log(f"File not found: {csv_file}", 'ERROR')
            return False

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self.log(f"Found {len(rows)} client records to process")

            # Validate all rows first
            all_valid = True
            for idx, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
                valid, errors = self.validate_client_row(row, idx)
                if not valid:
                    all_valid = False
                    for error in errors:
                        self.log(error, 'ERROR')
                        self.stats['errors'].append(error)

            if not all_valid:
                self.log("Validation failed. Please fix errors and try again.", 'ERROR')
                return False

            if validate_only:
                self.log("Validation successful! All client records are valid.", 'SUCCESS')
                return True

            # Import clients
            with self.app.app_context():
                for idx, row in enumerate(rows, start=2):
                    try:
                        # Check if client already exists
                        client_code = row.get('client_code', '').strip()
                        if client_code:
                            existing = Client.query.filter_by(client_code=client_code).first()
                            if existing:
                                self.log(f"Row {idx}: Client {client_code} already exists, skipping", 'WARNING')
                                self.stats['clients_skipped'] += 1
                                continue
                        else:
                            # Generate new client code
                            client_code = self.generate_client_code()

                        # Create client
                        client = Client(
                            client_code=client_code,
                            name=row.get('name', '').strip(),
                            contact_person=row.get('contact_person', '').strip() or None,
                            email=row.get('email', '').strip() or None,
                            phone=row.get('phone', '').strip() or None,
                            address=row.get('address', '').strip() or None,
                            notes=row.get('notes', '').strip() or None
                        )

                        db.session.add(client)
                        db.session.commit()

                        self.log(f"Imported client: {client_code} - {client.name}", 'SUCCESS')
                        self.stats['clients_imported'] += 1

                    except Exception as e:
                        db.session.rollback()
                        error_msg = f"Row {idx}: Error importing client: {str(e)}"
                        self.log(error_msg, 'ERROR')
                        self.stats['errors'].append(error_msg)
                        self.stats['clients_skipped'] += 1

            return True

        except Exception as e:
            self.log(f"Error reading CSV file: {str(e)}", 'ERROR')
            return False

    def import_projects(self, csv_file: str, validate_only: bool = False) -> bool:
        """Import projects from CSV file."""
        self.log(f"{'Validating' if validate_only else 'Importing'} projects from: {csv_file}")

        if not os.path.exists(csv_file):
            self.log(f"File not found: {csv_file}", 'ERROR')
            return False

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self.log(f"Found {len(rows)} project records to process")

            # Validate all rows first
            all_valid = True
            with self.app.app_context():
                for idx, row in enumerate(rows, start=2):
                    valid, errors = self.validate_project_row(row, idx)
                    if not valid:
                        all_valid = False
                        for error in errors:
                            self.log(error, 'ERROR')
                            self.stats['errors'].append(error)

                    # Check if client exists
                    client_code = row.get('client_code', '').strip()
                    if client_code:
                        client = Client.query.filter_by(client_code=client_code).first()
                        if not client:
                            all_valid = False
                            error = f"Row {idx}: Client {client_code} not found in database"
                            self.log(error, 'ERROR')
                            self.stats['errors'].append(error)

            if not all_valid:
                self.log("Validation failed. Please fix errors and try again.", 'ERROR')
                return False

            if validate_only:
                self.log("Validation successful! All project records are valid.", 'SUCCESS')
                return True

            # Import projects
            with self.app.app_context():
                for idx, row in enumerate(rows, start=2):
                    try:
                        # Get client
                        client_code = row.get('client_code', '').strip()
                        client = Client.query.filter_by(client_code=client_code).first()

                        # Check if project already exists
                        project_code = row.get('project_code', '').strip()
                        if project_code:
                            existing = Project.query.filter_by(project_code=project_code).first()
                            if existing:
                                self.log(f"Row {idx}: Project {project_code} already exists, skipping", 'WARNING')
                                self.stats['projects_skipped'] += 1
                                continue
                        else:
                            # Generate new project code
                            project_date = self.parse_date(row.get('created_date', '')) or date.today()
                            project_code = self.generate_project_code(client_code, project_date)

                        # Create project
                        project = Project(
                            project_code=project_code,
                            client_id=client.id,
                            name=row.get('name', '').strip(),
                            description=row.get('description', '').strip() or None,
                            status=row.get('status', 'Quote').strip(),
                            quote_date=self.parse_date(row.get('quote_date', '')),
                            approval_date=self.parse_date(row.get('approval_date', '')),
                            due_date=self.parse_date(row.get('due_date', '')),
                            completion_date=self.parse_date(row.get('completion_date', '')),
                            quoted_price=self.parse_decimal(row.get('quoted_price', '')),
                            final_price=self.parse_decimal(row.get('final_price', '')),
                            notes=row.get('notes', '').strip() or None,
                            # Phase 9 fields
                            material_type=row.get('material_type', '').strip() or None,
                            material_quantity_sheets=self.parse_int(row.get('material_quantity_sheets', '')),
                            parts_quantity=self.parse_int(row.get('parts_quantity', '')),
                            estimated_cut_time=self.parse_int(row.get('estimated_cut_time', '')),
                            drawing_creation_time=self.parse_int(row.get('drawing_creation_time', '')),
                            number_of_bins=self.parse_int(row.get('number_of_bins', '')),
                            scheduled_cut_date=self.parse_date(row.get('scheduled_cut_date', '')),
                            pop_received=self.parse_bool(row.get('pop_received', '')),
                            pop_received_date=self.parse_date(row.get('pop_received_date', '')),
                            pop_deadline=self.parse_date(row.get('pop_deadline', '')),
                            client_notified=self.parse_bool(row.get('client_notified', '')),
                            delivery_confirmed=self.parse_bool(row.get('delivery_confirmed', ''))
                        )

                        db.session.add(project)
                        db.session.commit()

                        self.log(f"Imported project: {project_code} - {project.name}", 'SUCCESS')
                        self.stats['projects_imported'] += 1

                        # Import files if specified
                        if self.files_base_dir:
                            self.import_project_files(project, row)

                    except Exception as e:
                        db.session.rollback()
                        error_msg = f"Row {idx}: Error importing project: {str(e)}"
                        self.log(error_msg, 'ERROR')
                        self.stats['errors'].append(error_msg)
                        self.stats['projects_skipped'] += 1

            return True

        except Exception as e:
            self.log(f"Error reading CSV file: {str(e)}", 'ERROR')
            return False

    def import_project_files(self, project: Project, row: Dict):
        """Import files for a project based on CSV row data."""
        # Files can be specified in the CSV as comma-separated paths
        # Format: dxf_files, quote_files, invoice_files, pop_files, delivery_note_files, image_files

        file_mappings = {
            'dxf_files': ('dxf', DesignFile),
            'quote_files': ('Quote', ProjectDocument),
            'invoice_files': ('Invoice', ProjectDocument),
            'pop_files': ('Proof of Payment', ProjectDocument),
            'delivery_note_files': ('Delivery Note', ProjectDocument),
            'image_files': ('Image', ProjectDocument)
        }

        for csv_field, (file_type, model_class) in file_mappings.items():
            files_str = row.get(csv_field, '').strip()
            if not files_str:
                continue

            # Split by comma or semicolon
            file_paths = [f.strip() for f in files_str.replace(';', ',').split(',') if f.strip()]

            for file_path in file_paths:
                try:
                    self.upload_file(project, file_path, file_type, model_class)
                except Exception as e:
                    error_msg = f"Error uploading file {file_path} for project {project.project_code}: {str(e)}"
                    self.log(error_msg, 'ERROR')
                    self.stats['files_failed'] += 1
                    self.stats['errors'].append(error_msg)

    def upload_file(self, project: Project, file_path: str, file_type: str, model_class):
        """Upload a single file for a project."""
        # Resolve file path
        if self.files_base_dir:
            full_path = self.files_base_dir / file_path
        else:
            full_path = Path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        # Get file info
        original_filename = full_path.name
        file_size = full_path.stat().st_size

        # Generate stored filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        ext = full_path.suffix
        stored_filename = f"{timestamp}_{unique_id}{ext}"

        # Determine destination
        if model_class == DesignFile:
            # DXF files go to data/files/projects/{project_id}/
            dest_dir = Path(self.app.config['UPLOAD_FOLDER']) / str(project.id)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / stored_filename

            # Copy file
            shutil.copy2(full_path, dest_path)

            # Create database record
            design_file = DesignFile(
                project_id=project.id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=str(dest_path),
                file_size=file_size,
                file_type='dxf',
                uploaded_by='bulk_import'
            )
            db.session.add(design_file)
            db.session.commit()

        else:  # ProjectDocument
            # Documents go to data/documents/{type}/
            doc_type_map = {
                'Quote': 'quotes',
                'Invoice': 'invoices',
                'Proof of Payment': 'pops',
                'Delivery Note': 'delivery_notes',
                'Image': 'images'
            }

            doc_folder = doc_type_map.get(file_type, 'other')
            dest_dir = Path(self.app.config['DOCUMENTS_FOLDER']) / doc_folder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / stored_filename

            # Copy file
            shutil.copy2(full_path, dest_path)

            # Create database record
            document = ProjectDocument(
                project_id=project.id,
                document_type=file_type,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=str(dest_path),
                file_size=file_size,
                uploaded_by='bulk_import'
            )
            db.session.add(document)
            db.session.commit()

        self.log(f"  Uploaded: {original_filename} ({file_size} bytes)", 'SUCCESS')
        self.stats['files_uploaded'] += 1

    def print_summary(self):
        """Print import summary statistics."""
        self.log("=" * 80)
        self.log("IMPORT SUMMARY", 'INFO')
        self.log("=" * 80)
        self.log(f"Clients imported: {self.stats['clients_imported']}")
        self.log(f"Clients skipped: {self.stats['clients_skipped']}")
        self.log(f"Projects imported: {self.stats['projects_imported']}")
        self.log(f"Projects skipped: {self.stats['projects_skipped']}")
        self.log(f"Files uploaded: {self.stats['files_uploaded']}")
        self.log(f"Files failed: {self.stats['files_failed']}")
        self.log(f"Total errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            self.log("\nErrors encountered:", 'ERROR')
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                self.log(f"  - {error}", 'ERROR')
            if len(self.stats['errors']) > 10:
                self.log(f"  ... and {len(self.stats['errors']) - 10} more errors", 'ERROR')

        self.log("=" * 80)


def main():
    """Main entry point for bulk import script."""
    parser = argparse.ArgumentParser(
        description='Bulk import clients, projects, and files into Laser OS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import only clients
  python bulk_import.py --clients clients.csv

  # Import only projects (clients must already exist)
  python bulk_import.py --projects projects.csv --files-dir ./import_files

  # Import both clients and projects
  python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./files

  # Validate data without importing
  python bulk_import.py --validate-only --clients clients.csv --projects projects.csv

  # Generate template files
  python bulk_import.py --generate-templates
        """
    )

    parser.add_argument('--clients', help='Path to clients CSV file')
    parser.add_argument('--projects', help='Path to projects CSV file')
    parser.add_argument('--files-dir', help='Base directory containing project files')
    parser.add_argument('--all', action='store_true', help='Import both clients and projects')
    parser.add_argument('--validate-only', action='store_true', help='Validate data without importing')
    parser.add_argument('--generate-templates', action='store_true', help='Generate CSV template files')

    args = parser.parse_args()

    # Generate templates if requested
    if args.generate_templates:
        generate_templates()
        return 0

    # Validate arguments
    if not args.clients and not args.projects:
        parser.print_help()
        print("\nError: Must specify --clients, --projects, or --generate-templates")
        return 1

    # Create Flask app
    app = create_app('development')

    # Create importer
    importer = BulkImporter(app, args.files_dir)

    # Run imports
    success = True

    if args.clients:
        if not importer.import_clients(args.clients, args.validate_only):
            success = False

    if args.projects and (success or args.validate_only):
        if not importer.import_projects(args.projects, args.validate_only):
            success = False

    # Print summary
    if not args.validate_only:
        importer.print_summary()

    return 0 if success else 1


def generate_templates():
    """Generate CSV template files for import."""
    print("Generating import template files...")

    # Clients template
    clients_template = """client_code,name,contact_person,email,phone,address,notes
,Acme Corporation,John Smith,john@acme.com,+27 11 123 4567,"123 Main St, Johannesburg, 2000",Preferred customer
,Tech Solutions Ltd,Jane Doe,jane@techsolutions.co.za,+27 21 987 6543,"456 Oak Ave, Cape Town, 8001",Net 30 payment terms
,Manufacturing Co,Bob Johnson,bob@manufacturing.com,+27 31 555 1234,"789 Industrial Rd, Durban, 4001","""

    # Projects template
    projects_template = """client_code,project_code,name,description,status,quote_date,approval_date,due_date,completion_date,quoted_price,final_price,material_type,material_quantity_sheets,parts_quantity,estimated_cut_time,drawing_creation_time,number_of_bins,scheduled_cut_date,pop_received,pop_received_date,pop_deadline,client_notified,delivery_confirmed,notes,dxf_files,quote_files,invoice_files,pop_files,delivery_note_files,image_files
CL-0001,,Custom Brackets,Laser cut brackets for mounting,Quote,2024-01-15,,,1500.00,,Mild Steel 3mm,2,50,120,30,2,,,,,,,High priority,brackets.dxf,quote_001.pdf,,,,,
CL-0001,,Signage Letters,Company logo letters,Approved,2024-01-10,2024-01-12,2024-01-20,,2500.00,2500.00,Stainless Steel 2mm,3,25,180,45,1,2024-01-18,true,2024-01-13,2024-01-16,true,false,Rush order,signage.dxf;letters.dxf,quote_002.pdf,invoice_002.pdf,pop_002.pdf,,,photo1.jpg;photo2.jpg
CL-0002,,Decorative Panels,Architectural panels,In Progress,2024-01-05,2024-01-08,2024-01-25,,5000.00,,Aluminum 5mm,5,100,300,60,3,2024-01-20,true,2024-01-09,2024-01-12,true,false,,panels.dxf,quote_003.pdf,invoice_003.pdf,pop_003.pdf,,,"""

    # Write templates
    with open('clients_import_template.csv', 'w', encoding='utf-8') as f:
        f.write(clients_template)
    print("✅ Created: clients_import_template.csv")

    with open('projects_import_template.csv', 'w', encoding='utf-8') as f:
        f.write(projects_template)
    print("✅ Created: projects_import_template.csv")

    # Create README
    readme = """# Bulk Import Templates

## Overview
These templates allow you to bulk import clients, projects, and associated files into Laser OS.

## Files Generated
- `clients_import_template.csv` - Template for importing clients
- `projects_import_template.csv` - Template for importing projects and files

## Instructions

### 1. Prepare Your Data

#### Clients CSV
**Required Fields:**
- `name` - Client company name (REQUIRED)

**Optional Fields:**
- `client_code` - Leave blank to auto-generate (format: CL-XXXX)
- `contact_person` - Primary contact name
- `email` - Contact email address
- `phone` - Contact phone number
- `address` - Physical/postal address
- `notes` - Additional notes

#### Projects CSV
**Required Fields:**
- `client_code` - Must match an existing client code (REQUIRED)
- `name` - Project name/description (REQUIRED)

**Optional Fields:**
- `project_code` - Leave blank to auto-generate (format: JB-yyyy-mm-CLxxxx-###)
- `description` - Detailed project description
- `status` - Quote | Approved | In Progress | Completed | Cancelled (default: Quote)
- `quote_date` - Date format: YYYY-MM-DD or DD/MM/YYYY
- `approval_date` - Date project was approved
- `due_date` - Project due date
- `completion_date` - Date project was completed
- `quoted_price` - Initial quoted price (numbers only, no currency symbols)
- `final_price` - Final invoiced price
- `material_type` - e.g., "Mild Steel 3mm", "Stainless Steel 2mm"
- `material_quantity_sheets` - Number of sheets required
- `parts_quantity` - Number of parts to cut
- `estimated_cut_time` - Estimated cutting time in minutes
- `drawing_creation_time` - Time spent creating drawings in minutes
- `number_of_bins` - Number of bins for parts
- `scheduled_cut_date` - Scheduled cutting date
- `pop_received` - true/false - Proof of payment received
- `pop_received_date` - Date POP was received
- `pop_deadline` - POP deadline date
- `client_notified` - true/false - Client has been notified
- `delivery_confirmed` - true/false - Delivery confirmed
- `notes` - Additional notes

**File Fields (comma or semicolon separated file paths):**
- `dxf_files` - DXF design files (e.g., "file1.dxf,file2.dxf")
- `quote_files` - Quote documents (PDF, images)
- `invoice_files` - Invoice documents
- `pop_files` - Proof of payment documents
- `delivery_note_files` - Delivery note documents
- `image_files` - Project images

### 2. Organize Your Files

Create a directory structure for your files:
```
import_files/
├── dxf/
│   ├── brackets.dxf
│   ├── signage.dxf
│   └── panels.dxf
├── quotes/
│   ├── quote_001.pdf
│   └── quote_002.pdf
├── invoices/
│   └── invoice_002.pdf
├── pops/
│   └── pop_002.pdf
└── images/
    ├── photo1.jpg
    └── photo2.jpg
```

In your CSV, reference files relative to the base directory:
- `dxf/brackets.dxf`
- `quotes/quote_001.pdf`
- `images/photo1.jpg,images/photo2.jpg`

### 3. Run the Import

**Validate data first (recommended):**
```bash
python bulk_import.py --validate-only --clients clients.csv --projects projects.csv
```

**Import clients only:**
```bash
python bulk_import.py --clients clients.csv
```

**Import projects with files:**
```bash
python bulk_import.py --projects projects.csv --files-dir ./import_files
```

**Import everything:**
```bash
python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./import_files
```

### 4. Verify Import

After import:
1. Check the console output for any errors
2. Log into Laser OS web interface
3. Navigate to Clients and Projects to verify data
4. Check that files are properly linked to projects

## Tips

- **Always validate first** using `--validate-only` flag
- **Start with clients** before importing projects
- **Use absolute paths** or organize files in a single base directory
- **Check client codes** - projects must reference existing clients
- **Date formats** - Use YYYY-MM-DD for consistency
- **File paths** - Use forward slashes (/) even on Windows
- **Multiple files** - Separate with commas or semicolons
- **Leave blank** - Auto-generated fields (client_code, project_code) can be left empty
- **Backup first** - Always backup your database before bulk imports

## Troubleshooting

**"Client not found"**
- Ensure client_code in projects CSV matches an existing client
- Import clients first, then projects

**"File not found"**
- Check file paths are relative to --files-dir
- Verify files exist in the specified location
- Use forward slashes in paths

**"Invalid date format"**
- Use YYYY-MM-DD format (e.g., 2024-01-15)
- Or DD/MM/YYYY format (e.g., 15/01/2024)

**"Invalid status"**
- Use exact status names: Quote, Approved, In Progress, Completed, Cancelled

## Support

For issues or questions, check the main Laser OS documentation or contact support.
"""

    with open('IMPORT_README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    print("✅ Created: IMPORT_README.md")

    print("\n" + "="*80)
    print("Template files generated successfully!")
    print("="*80)
    print("\nNext steps:")
    print("1. Edit the CSV files with your data")
    print("2. Organize your files in a directory")
    print("3. Run: python bulk_import.py --validate-only --clients clients.csv --projects projects.csv")
    print("4. If validation passes, run the actual import")
    print("\nSee IMPORT_README.md for detailed instructions.")


if __name__ == '__main__':
    sys.exit(main())

