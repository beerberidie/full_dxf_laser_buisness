"""
Import 6000 Laser Presets from .fsm files

This script parses the filenames of .fsm preset files and imports them into the database.
The filenames contain valuable information about material type, thickness, and gas type.

Filename Pattern Examples:
- "0.5mm C Air CS Used 1.5sn.fsm" -> 0.5mm, Copper/Carbon Steel, Air
- "1.2mm MS air cut 1.5sn.fsm" -> 1.2mm, Mild Steel, Air
- "10mm O2 MS Cut 1.2D.fsm" -> 10mm, Mild Steel, Oxygen
- "3mm Al air cut 1.5sn.fsm" -> 3mm, Aluminum, Air
- "1mm ss nitro cut 1.5sn.fsm" -> 1mm, Stainless Steel, Nitrogen
"""

import os
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import MachineSettingsPreset
from datetime import datetime


# Material type mappings
MATERIAL_MAPPINGS = {
    'MS': 'Mild Steel',
    'SS': 'Stainless Steel',
    'AL': 'Aluminum',
    'C': 'Carbon Steel',
    'CS': 'Carbon Steel',
    'VASTRAP': 'Vastrap',
}

# Gas type mappings
GAS_MAPPINGS = {
    'AIR': 'Air',
    'O2': 'Oxygen',
    'N2': 'Nitrogen',
    'NITRO': 'Nitrogen',
    'OXY': 'Oxygen',
}

# Nozzle type mappings (from filename patterns like "1.5sn", "1.2D", etc.)
NOZZLE_MAPPINGS = {
    '1.5SN': '1.5mm Single',
    '1.2D': '1.2mm Double',
    '1.4D': '1.4mm Double',
    '1.4E': '1.4mm Enhanced',
    '2SN': '2.0mm Single',
}


def parse_thickness(filename):
    """
    Extract thickness from filename.
    
    Examples:
        "0.5mm C Air CS Used 1.5sn.fsm" -> 0.5
        "10mm O2 MS Cut 1.2D.fsm" -> 10.0
        "6-7.7mm VASTRAP Air Cut 1.5sn.fsm" -> 6.0 (takes first value)
    """
    # Match patterns like "0.5mm", "10mm", "6-7.7mm"
    match = re.search(r'(\d+\.?\d*)-?(?:\d+\.?\d*)?mm', filename, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def parse_material_type(filename):
    """
    Extract material type from filename.
    
    Examples:
        "0.5mm C Air CS Used 1.5sn.fsm" -> "Carbon Steel"
        "1.2mm MS air cut 1.5sn.fsm" -> "Mild Steel"
        "3mm Al air cut 1.5sn.fsm" -> "Aluminum"
        "1mm ss nitro cut 1.5sn.fsm" -> "Stainless Steel"
    """
    filename_upper = filename.upper()
    
    # Check for each material type
    for abbrev, full_name in MATERIAL_MAPPINGS.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + abbrev + r'\b'
        if re.search(pattern, filename_upper):
            return full_name
    
    return 'Unknown'


def parse_gas_type(filename):
    """
    Extract gas type from filename.
    
    Examples:
        "0.5mm C Air CS Used 1.5sn.fsm" -> "Air"
        "10mm O2 MS Cut 1.2D.fsm" -> "Oxygen"
        "1mm ss nitro cut 1.5sn.fsm" -> "Nitrogen"
    """
    filename_upper = filename.upper()
    
    # Check for each gas type
    for abbrev, full_name in GAS_MAPPINGS.items():
        pattern = r'\b' + abbrev + r'\b'
        if re.search(pattern, filename_upper):
            return full_name
    
    return 'Air'  # Default to Air if not specified


def parse_nozzle_type(filename):
    """
    Extract nozzle type from filename.
    
    Examples:
        "0.5mm C Air CS Used 1.5sn.fsm" -> "1.5mm Single"
        "10mm O2 MS Cut 1.2D.fsm" -> "1.2mm Double"
    """
    filename_upper = filename.upper()
    
    # Check for each nozzle type
    for abbrev, full_name in NOZZLE_MAPPINGS.items():
        if abbrev in filename_upper:
            return full_name
    
    return None


def parse_description(filename):
    """
    Extract description/notes from filename.
    
    Examples:
        "0.5mm C Air CS Used 1.5sn - coloursmpl.fsm" -> "coloursmpl"
        "3mm MS Air 2sn - Test.fsm" -> "Test"
        "8mm MS O2 1.2DN - MEH.fsm" -> "MEH"
    """
    # Look for text after a dash
    match = re.search(r'-\s*([^.]+?)(?:\.fsm)?$', filename, re.IGNORECASE)
    if match:
        desc = match.group(1).strip()
        # Clean up common suffixes
        desc = re.sub(r'\s*\.fsm$', '', desc, flags=re.IGNORECASE)
        return desc
    return None


def create_preset_name(thickness, material, gas, nozzle, description):
    """
    Create a standardized preset name.
    
    Example:
        create_preset_name(0.5, "Carbon Steel", "Air", "1.5mm Single", None)
        -> "0.5mm Carbon Steel - Air - 1.5mm Single"
    """
    parts = []
    
    if thickness:
        parts.append(f"{thickness}mm")
    
    if material and material != 'Unknown':
        parts.append(material)
    
    if gas:
        parts.append(gas)
    
    if nozzle:
        parts.append(nozzle)
    
    name = " - ".join(parts)
    
    # Add description as suffix if present
    if description:
        name += f" ({description})"
    
    return name


def import_presets_from_directory(directory_path, dry_run=False):
    """
    Import presets from .fsm files in the specified directory.
    
    Args:
        directory_path: Path to directory containing .fsm files
        dry_run: If True, only print what would be imported without saving
    
    Returns:
        Tuple of (imported_count, skipped_count, error_count)
    """
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    # Get all .fsm files
    fsm_files = list(Path(directory_path).glob('*.fsm'))
    
    print(f"\n{'='*80}")
    print(f"Found {len(fsm_files)} .fsm files in {directory_path}")
    print(f"{'='*80}\n")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved to database\n")
    
    for fsm_file in sorted(fsm_files):
        filename = fsm_file.name
        
        try:
            # Parse filename
            thickness = parse_thickness(filename)
            material = parse_material_type(filename)
            gas = parse_gas_type(filename)
            nozzle = parse_nozzle_type(filename)
            description = parse_description(filename)
            
            # Create preset name
            preset_name = create_preset_name(thickness, material, gas, nozzle, description)
            
            # Validate required fields
            if not thickness:
                print(f"⚠️  SKIP: {filename}")
                print(f"   Reason: Could not parse thickness")
                skipped_count += 1
                continue
            
            if material == 'Unknown':
                print(f"⚠️  SKIP: {filename}")
                print(f"   Reason: Could not determine material type")
                skipped_count += 1
                continue
            
            # Check if preset already exists
            existing = MachineSettingsPreset.query.filter_by(preset_name=preset_name).first()
            if existing:
                print(f"⏭️  EXISTS: {preset_name}")
                skipped_count += 1
                continue
            
            # Create preset
            if not dry_run:
                preset = MachineSettingsPreset(
                    preset_name=preset_name,
                    material_type=material,
                    thickness=thickness,
                    gas_type=gas,
                    nozzle=nozzle,
                    description=description,
                    notes=f"Imported from {filename}",
                    created_by="System Import",
                    is_active=True
                )
                
                db.session.add(preset)
                db.session.commit()
                
                print(f"✅ IMPORTED: {preset_name}")
                print(f"   File: {filename}")
                print(f"   Material: {material}, Thickness: {thickness}mm, Gas: {gas}")
                if nozzle:
                    print(f"   Nozzle: {nozzle}")
                if description:
                    print(f"   Description: {description}")
                print()
                
                imported_count += 1
            else:
                print(f"✅ WOULD IMPORT: {preset_name}")
                print(f"   File: {filename}")
                print(f"   Material: {material}, Thickness: {thickness}mm, Gas: {gas}")
                if nozzle:
                    print(f"   Nozzle: {nozzle}")
                if description:
                    print(f"   Description: {description}")
                print()
                
                imported_count += 1
        
        except Exception as e:
            print(f"❌ ERROR: {filename}")
            print(f"   {str(e)}")
            print()
            error_count += 1
    
    return imported_count, skipped_count, error_count


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import 6000 Laser Presets from .fsm files')
    parser.add_argument('--directory', '-d', default='6000_Presets',
                       help='Directory containing .fsm files (default: 6000_Presets)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be imported without saving to database')
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"❌ Error: Directory '{args.directory}' not found")
        sys.exit(1)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("6000 LASER PRESETS IMPORT SCRIPT")
        print("="*80)
        
        # Import presets
        imported, skipped, errors = import_presets_from_directory(
            args.directory,
            dry_run=args.dry_run
        )
        
        # Print summary
        print("\n" + "="*80)
        print("IMPORT SUMMARY")
        print("="*80)
        print(f"✅ Imported: {imported}")
        print(f"⏭️  Skipped:  {skipped}")
        print(f"❌ Errors:   {errors}")
        print(f"📊 Total:    {imported + skipped + errors}")
        print("="*80 + "\n")
        
        if args.dry_run:
            print("🔍 This was a DRY RUN - no changes were saved to the database")
            print("   Run without --dry-run to actually import the presets\n")


if __name__ == '__main__':
    main()

