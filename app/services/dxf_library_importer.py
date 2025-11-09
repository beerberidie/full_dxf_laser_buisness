"""
DXF Library Importer Service

This service imports DXF files from the starter library into the products database.
"""

import csv
import os
import shutil
from pathlib import Path
from decimal import Decimal
from app import db
from app.models import Product, ProductFile
from app.services.activity_logger import log_activity
from datetime import datetime


class DXFLibraryImporter:
    """Import DXF files from the starter library into products."""
    
    def __init__(self, library_path, upload_folder):
        """
        Initialize the importer.
        
        Args:
            library_path: Path to the dxf_library directory
            upload_folder: Path to the products upload folder
        """
        self.library_path = Path(library_path)
        self.upload_folder = Path(upload_folder)
        self.index_file = self.library_path / 'index.csv'
        
    def parse_thickness(self, thickness_str):
        """
        Parse thickness string to extract numeric value.
        
        Args:
            thickness_str: String like "10 mm", "2 mm", "—", etc.
            
        Returns:
            Decimal or None
        """
        if not thickness_str or thickness_str.strip() in ['—', '-', '']:
            return None
            
        # Extract numeric part
        thickness_str = thickness_str.strip().lower()
        thickness_str = thickness_str.replace('mm', '').strip()
        
        try:
            return Decimal(thickness_str)
        except:
            return None
    
    def parse_size(self, size_str):
        """
        Parse size string to extract dimensions for description.
        
        Args:
            size_str: String like "200x200", "Ø800", etc.
            
        Returns:
            str: Formatted size description
        """
        if not size_str:
            return None
        return size_str.strip()
    
    def extract_material_from_industry(self, industry):
        """
        Map industry to likely material type.
        
        Args:
            industry: Industry category string
            
        Returns:
            str: Material type
        """
        industry_lower = industry.lower()
        
        # Map industries to common materials
        if 'structural' in industry_lower or 'petrochem' in industry_lower or 'marine' in industry_lower:
            return 'Mild Steel'
        elif 'food' in industry_lower or 'beverage' in industry_lower or 'pharma' in industry_lower:
            return 'Stainless Steel'
        elif 'architecture' in industry_lower or 'furniture' in industry_lower or 'arts' in industry_lower:
            return 'Mild Steel'
        elif 'automotive' in industry_lower:
            return 'Mild Steel'
        elif 'sugar' in industry_lower:
            return 'Mild Steel'
        elif 'electronics' in industry_lower:
            return 'Aluminum'
        else:
            return 'Mild Steel'  # Default
    
    def find_dxf_file(self, filename):
        """
        Find the DXF file in the library directory structure.
        
        Args:
            filename: DXF filename to find
            
        Returns:
            Path or None
        """
        # Search in all subdirectories
        for dxf_file in self.library_path.rglob(filename):
            if dxf_file.is_file():
                return dxf_file
        return None
    
    def import_products(self, copy_files=True, skip_existing=True):
        """
        Import products from the DXF library.
        
        Args:
            copy_files: If True, copy DXF files to product upload folder
            skip_existing: If True, skip products that already exist (by name)
            
        Returns:
            dict: Statistics about the import
        """
        stats = {
            'total': 0,
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'files_copied': 0
        }
        
        # Check if index file exists
        if not self.index_file.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_file}")
        
        # Read CSV file
        with open(self.index_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                stats['total'] += 1
                
                try:
                    # Extract data from CSV
                    industry = row.get('industry', '').strip()
                    item_name = row.get('item', '').strip()
                    filename = row.get('file', '').strip()
                    size = row.get('size', '').strip()
                    thickness_str = row.get('thickness', '').strip()
                    notes = row.get('notes', '').strip()
                    
                    # Skip if essential data is missing
                    if not item_name or not filename:
                        print(f"⚠ Skipping row with missing data: {row}")
                        stats['skipped'] += 1
                        continue
                    
                    # Check if product already exists
                    if skip_existing:
                        existing = Product.query.filter_by(name=item_name).first()
                        if existing:
                            print(f"⚠ Product already exists: {item_name} (SKU: {existing.sku_code})")
                            stats['skipped'] += 1
                            continue
                    
                    # Parse thickness
                    thickness = self.parse_thickness(thickness_str)
                    
                    # Determine material
                    material = self.extract_material_from_industry(industry)
                    
                    # Build description
                    description_parts = []
                    if industry:
                        description_parts.append(f"Industry: {industry}")
                    if size:
                        description_parts.append(f"Size: {size}")
                    if notes:
                        description_parts.append(f"Notes: {notes}")
                    
                    description = " | ".join(description_parts) if description_parts else None
                    
                    # Create product
                    product = Product(
                        name=item_name,
                        description=description,
                        material=material,
                        thickness=thickness,
                        unit_price=None,  # Will be set later
                        notes=f"Imported from DXF Starter Library\nOriginal file: {filename}"
                    )
                    
                    db.session.add(product)
                    db.session.flush()  # Get the product ID
                    
                    print(f"✓ Created product: {item_name} (SKU: {product.sku_code})")
                    stats['created'] += 1
                    
                    # Copy DXF file if requested
                    if copy_files:
                        dxf_path = self.find_dxf_file(filename)
                        
                        if dxf_path and dxf_path.exists():
                            # Create product upload folder
                            product_folder = self.upload_folder / str(product.id)
                            product_folder.mkdir(parents=True, exist_ok=True)
                            
                            # Copy file with original name
                            dest_path = product_folder / filename
                            shutil.copy2(dxf_path, dest_path)
                            
                            # Get file size
                            file_size = dest_path.stat().st_size
                            
                            # Create ProductFile record
                            relative_path = f"{product.id}/{filename}"
                            product_file = ProductFile(
                                product_id=product.id,
                                original_filename=filename,
                                stored_filename=filename,
                                file_path=relative_path,
                                file_size=file_size,
                                file_type='dxf',
                                uploaded_by='System',
                                notes='Imported from DXF Starter Library'
                            )
                            
                            db.session.add(product_file)
                            stats['files_copied'] += 1
                            print(f"  ✓ Copied DXF file: {filename}")
                        else:
                            print(f"  ⚠ DXF file not found: {filename}")
                    
                    # Log activity
                    log_activity(
                        entity_type='PRODUCT',
                        entity_id=product.id,
                        action='CREATED',
                        details=f'Imported from DXF Starter Library: {item_name}'
                    )
                    
                except Exception as e:
                    print(f"✗ Error importing {item_name if 'item_name' in locals() else 'unknown'}: {str(e)}")
                    stats['errors'] += 1
                    db.session.rollback()
                    continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✓ Import completed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error committing changes: {str(e)}")
            raise
        
        return stats

