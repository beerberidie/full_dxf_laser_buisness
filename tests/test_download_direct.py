#!/usr/bin/env python3
"""
Test download function directly
"""

from app import create_app, db
from app.models import DesignFile
from flask import send_file
import os
from pathlib import Path

app = create_app()

with app.app_context():
    # Get first file
    design_file = DesignFile.query.first()
    
    if not design_file:
        print("No files in database")
        exit(1)
    
    print("=" * 70)
    print("DOWNLOAD FUNCTION TEST")
    print("=" * 70)
    
    print(f"\nFile ID: {design_file.id}")
    print(f"Original Filename: {design_file.original_filename}")
    print(f"Stored Path (DB): {design_file.file_path}")
    
    # Simulate what the download function does
    base_folder = app.config.get('UPLOAD_FOLDER')
    print(f"\nBase Folder: {base_folder}")
    
    # Method 1: os.path.join + os.path.abspath
    full_file_path = os.path.abspath(os.path.join(base_folder, design_file.file_path))
    print(f"\nMethod 1 (os.path.abspath + os.path.join):")
    print(f"  Full Path: {full_file_path}")
    print(f"  Is Absolute: {os.path.isabs(full_file_path)}")
    print(f"  Exists: {os.path.exists(full_file_path)}")
    
    # Method 2: Path object
    file_path_obj = Path(full_file_path)
    print(f"\nMethod 2 (Path object):")
    print(f"  Path: {file_path_obj}")
    print(f"  Is Absolute: {file_path_obj.is_absolute()}")
    print(f"  Exists: {file_path_obj.exists()}")
    
    # Test send_file
    print(f"\nTesting send_file():")
    try:
        with app.test_request_context():
            # Try with Path object
            response = send_file(
                file_path_obj,
                as_attachment=True,
                download_name=design_file.original_filename
            )
            print(f"  ✅ send_file() succeeded with Path object")
            print(f"  Response status: {response.status}")
            print(f"  Content-Disposition: {response.headers.get('Content-Disposition')}")
    except Exception as e:
        print(f"  ❌ send_file() failed: {e}")
        
        # Try with string path
        print(f"\n  Trying with string path...")
        try:
            with app.test_request_context():
                response = send_file(
                    str(file_path_obj),
                    as_attachment=True,
                    download_name=design_file.original_filename
                )
                print(f"  ✅ send_file() succeeded with string path")
                print(f"  Response status: {response.status}")
        except Exception as e2:
            print(f"  ❌ send_file() also failed with string: {e2}")
    
    print("\n" + "=" * 70)

