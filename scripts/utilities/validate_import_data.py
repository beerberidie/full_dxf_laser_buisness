#!/usr/bin/env python3
"""
Quick validation script for import data
Checks CSV files and file references before running the actual import
"""

import csv
import os
import sys
from pathlib import Path
from datetime import datetime


def validate_csv_file(filepath):
    """Check if CSV file exists and is readable."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                print(f"⚠️  File is empty: {filepath}")
                return False
            print(f"✅ Found {len(rows)} rows in {filepath}")
            return True
    except Exception as e:
        print(f"❌ Error reading {filepath}: {str(e)}")
        return False


def validate_clients_csv(filepath):
    """Validate clients CSV structure and data."""
    print("\n" + "="*80)
    print("VALIDATING CLIENTS CSV")
    print("="*80)
    
    if not validate_csv_file(filepath):
        return False
    
    errors = []
    warnings = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Check required headers
        required_headers = ['name']
        optional_headers = ['client_code', 'contact_person', 'email', 'phone', 'address', 'notes']
        
        headers = reader.fieldnames
        missing_required = [h for h in required_headers if h not in headers]
        
        if missing_required:
            print(f"❌ Missing required columns: {', '.join(missing_required)}")
            return False
        
        print(f"✅ All required columns present")
        print(f"📋 Columns found: {', '.join(headers)}")
        
        # Validate each row
        for idx, row in enumerate(reader, start=2):
            # Check required fields
            if not row.get('name', '').strip():
                errors.append(f"Row {idx}: Missing client name")
            
            # Check email format
            email = row.get('email', '').strip()
            if email and '@' not in email:
                warnings.append(f"Row {idx}: Email may be invalid: {email}")
            
            # Check client code format if provided
            client_code = row.get('client_code', '').strip()
            if client_code and not client_code.startswith('CL-'):
                warnings.append(f"Row {idx}: Client code should start with 'CL-': {client_code}")
    
    # Print results
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        for error in errors[:10]:
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
        return False
    
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warnings:")
        for warning in warnings[:10]:
            print(f"   {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more warnings")
    
    print(f"\n✅ Clients CSV validation passed!")
    return True


def validate_projects_csv(filepath, files_dir=None):
    """Validate projects CSV structure and data."""
    print("\n" + "="*80)
    print("VALIDATING PROJECTS CSV")
    print("="*80)
    
    if not validate_csv_file(filepath):
        return False
    
    errors = []
    warnings = []
    missing_files = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Check required headers
        required_headers = ['client_code', 'name']
        headers = reader.fieldnames
        
        missing_required = [h for h in required_headers if h not in headers]
        
        if missing_required:
            print(f"❌ Missing required columns: {', '.join(missing_required)}")
            return False
        
        print(f"✅ All required columns present")
        print(f"📋 Columns found: {', '.join(headers)}")
        
        # Validate each row
        for idx, row in enumerate(reader, start=2):
            # Check required fields
            if not row.get('client_code', '').strip():
                errors.append(f"Row {idx}: Missing client_code")
            if not row.get('name', '').strip():
                errors.append(f"Row {idx}: Missing project name")
            
            # Check status if provided
            status = row.get('status', '').strip()
            valid_statuses = ['Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled',
                            'Request', 'Quote & Approval', 'Approved (POP Received)',
                            'Queued (Scheduled for Cutting)']
            if status and status not in valid_statuses:
                errors.append(f"Row {idx}: Invalid status '{status}'")
            
            # Check date formats
            date_fields = ['quote_date', 'approval_date', 'due_date', 'completion_date',
                          'scheduled_cut_date', 'pop_received_date', 'pop_deadline']
            for field in date_fields:
                date_str = row.get(field, '').strip()
                if date_str:
                    if not validate_date_format(date_str):
                        warnings.append(f"Row {idx}: Invalid date format in {field}: {date_str}")
            
            # Check file references if files_dir provided
            if files_dir:
                file_fields = ['dxf_files', 'quote_files', 'invoice_files', 'pop_files',
                              'delivery_note_files', 'image_files']
                for field in file_fields:
                    files_str = row.get(field, '').strip()
                    if files_str:
                        file_paths = [f.strip() for f in files_str.replace(';', ',').split(',') if f.strip()]
                        for file_path in file_paths:
                            full_path = Path(files_dir) / file_path
                            if not full_path.exists():
                                missing_files.append(f"Row {idx}: File not found: {file_path}")
    
    # Print results
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        for error in errors[:10]:
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
        return False
    
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warnings:")
        for warning in warnings[:10]:
            print(f"   {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more warnings")
    
    if missing_files:
        print(f"\n⚠️  Found {len(missing_files)} missing files:")
        for missing in missing_files[:10]:
            print(f"   {missing}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more missing files")
        print("\n   Note: Files will be skipped during import if not found")
    
    print(f"\n✅ Projects CSV validation passed!")
    return True


def validate_date_format(date_str):
    """Check if date string is in a valid format."""
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
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    return False


def main():
    """Main validation function."""
    print("="*80)
    print("LASER OS - IMPORT DATA VALIDATOR")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python validate_import_data.py clients.csv")
        print("  python validate_import_data.py projects.csv [files_directory]")
        print("  python validate_import_data.py clients.csv projects.csv [files_directory]")
        print("\nExamples:")
        print("  python validate_import_data.py clients_import_template.csv")
        print("  python validate_import_data.py projects_import_template.csv ./my_import_files")
        print("  python validate_import_data.py clients.csv projects.csv ./my_import_files")
        return 1
    
    # Parse arguments
    files_to_check = []
    files_dir = None
    
    for arg in sys.argv[1:]:
        if arg.endswith('.csv'):
            files_to_check.append(arg)
        elif os.path.isdir(arg):
            files_dir = arg
        else:
            # Assume it's a files directory even if it doesn't exist yet
            files_dir = arg
    
    if not files_to_check:
        print("❌ No CSV files specified")
        return 1
    
    # Validate each file
    all_valid = True
    
    for csv_file in files_to_check:
        if 'client' in csv_file.lower():
            if not validate_clients_csv(csv_file):
                all_valid = False
        elif 'project' in csv_file.lower():
            if not validate_projects_csv(csv_file, files_dir):
                all_valid = False
        else:
            print(f"\n⚠️  Unknown CSV type: {csv_file}")
            print("   Filename should contain 'client' or 'project'")
    
    # Final summary
    print("\n" + "="*80)
    if all_valid:
        print("✅ ALL VALIDATIONS PASSED!")
        print("="*80)
        print("\nYou can now run the import:")
        if len(files_to_check) == 1:
            if 'client' in files_to_check[0].lower():
                print(f"  python bulk_import.py --clients {files_to_check[0]}")
            else:
                cmd = f"  python bulk_import.py --projects {files_to_check[0]}"
                if files_dir:
                    cmd += f" --files-dir {files_dir}"
                print(cmd)
        else:
            cmd = "  python bulk_import.py --all"
            for f in files_to_check:
                if 'client' in f.lower():
                    cmd += f" --clients {f}"
                else:
                    cmd += f" --projects {f}"
            if files_dir:
                cmd += f" --files-dir {files_dir}"
            print(cmd)
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print("="*80)
        print("\nPlease fix the errors above before importing.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

