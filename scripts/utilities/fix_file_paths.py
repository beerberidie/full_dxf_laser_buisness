#!/usr/bin/env python3
"""
Fix file paths in design_files table
Converts absolute/incorrect paths to relative paths (relative to UPLOAD_FOLDER)
"""

from app import create_app, db
from app.models import DesignFile
import os
from pathlib import Path

def fix_file_paths():
    """Fix file paths in the database."""
    print("=" * 70)
    print("FIX FILE PATHS MIGRATION")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        upload_folder = app.config['UPLOAD_FOLDER']
        print(f"\n📁 Upload Folder: {upload_folder}")
        
        # Get all design files
        files = DesignFile.query.all()
        print(f"\n📊 Found {len(files)} file(s) to check")
        
        if len(files) == 0:
            print("\n✅ No files to fix")
            return
        
        fixed_count = 0
        error_count = 0
        
        for design_file in files:
            old_path = design_file.file_path
            print(f"\n{'='*70}")
            print(f"File ID: {design_file.id}")
            print(f"Original Filename: {design_file.original_filename}")
            print(f"Current Path: {old_path}")
            
            # Try to determine the correct relative path
            # Expected format: {project_id}/{stored_filename}
            
            # Case 1: Path starts with upload_folder (absolute path)
            if old_path.startswith(upload_folder):
                # Remove upload_folder prefix
                relative_path = old_path[len(upload_folder):].lstrip(os.sep).lstrip('/')
                print(f"  → Detected absolute path, converting to relative")
            
            # Case 2: Path starts with 'data/files' or 'data\\files'
            elif old_path.startswith('data/files') or old_path.startswith('data\\files'):
                # Remove 'data/files' prefix
                relative_path = old_path.replace('data/files\\', '').replace('data/files/', '')
                print(f"  → Detected 'data/files' prefix, removing")
            
            # Case 3: Path already looks correct (just project_id/filename)
            elif old_path.startswith(str(design_file.project_id) + os.sep) or \
                 old_path.startswith(str(design_file.project_id) + '/'):
                relative_path = old_path
                print(f"  → Path already in correct format")
            
            # Case 4: Unknown format - try to construct from stored_filename
            else:
                relative_path = os.path.join(str(design_file.project_id), design_file.stored_filename)
                print(f"  → Unknown format, reconstructing from project_id and stored_filename")
            
            # Normalize path separators to forward slashes for consistency
            relative_path = relative_path.replace('\\', '/')
            
            print(f"New Path: {relative_path}")
            
            # Verify the file exists at the new path
            full_path = os.path.join(upload_folder, relative_path)
            if os.path.exists(full_path):
                print(f"  ✅ File exists at: {full_path}")
                
                # Update the database
                design_file.file_path = relative_path
                fixed_count += 1
            else:
                print(f"  ❌ WARNING: File not found at: {full_path}")
                print(f"  → Skipping this file (keeping old path)")
                error_count += 1
        
        # Commit changes
        if fixed_count > 0:
            try:
                db.session.commit()
                print(f"\n{'='*70}")
                print(f"✅ Successfully updated {fixed_count} file path(s)")
                if error_count > 0:
                    print(f"⚠️  {error_count} file(s) could not be updated (file not found)")
                print(f"{'='*70}")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error committing changes: {e}")
                print(f"{'='*70}")
        else:
            print(f"\n{'='*70}")
            print(f"ℹ️  No files needed updating")
            print(f"{'='*70}")

if __name__ == '__main__':
    fix_file_paths()

