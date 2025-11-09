"""
Standalone script to import DXF library products.
Run this with: python import_dxf_library.py
"""

import os
import sys

# Set environment to development
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.services.dxf_library_importer import DXFLibraryImporter

def main():
    """Import DXF library products."""
    print('Importing DXF Starter Library...\n')
    
    # Create app
    app = create_app('development')
    
    with app.app_context():
        # Get paths
        library_path = os.path.join(os.getcwd(), 'dxf_starter_library_v1', 'dxf_library')
        upload_folder = app.config.get('UPLOAD_FOLDER', 'data/files/products')
        
        # Check if library exists
        if not os.path.exists(library_path):
            print(f'✗ DXF library not found at: {library_path}')
            return 1
        
        print(f'Library path: {library_path}')
        print(f'Upload folder: {upload_folder}\n')
        
        # Create importer
        importer = DXFLibraryImporter(library_path, upload_folder)
        
        # Run import
        try:
            stats = importer.import_products(copy_files=True, skip_existing=True)
            
            # Print summary
            print('\n' + '='*60)
            print('IMPORT SUMMARY')
            print('='*60)
            print(f'Total rows processed:  {stats["total"]}')
            print(f'Products created:      {stats["created"]}')
            print(f'Products skipped:      {stats["skipped"]}')
            print(f'DXF files copied:      {stats["files_copied"]}')
            print(f'Errors:                {stats["errors"]}')
            print('='*60)
            
            if stats['created'] > 0:
                print(f'\n✓ Successfully imported {stats["created"]} products!')
                return 0
            else:
                print('\n⚠ No new products were imported.')
                return 0
                
        except Exception as e:
            print(f'\n✗ Import failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    sys.exit(main())

