"""
Module N - Filename Generator
Generates standardized filenames with collision handling
"""

import re
from pathlib import Path
from typing import Optional
from ..models.schemas import NormalizedMetadata, MATERIAL_CODE_MAP
import logging

logger = logging.getLogger(__name__)


def generate_filename(metadata: NormalizedMetadata) -> str:
    """
    Generate standardized filename from metadata.
    
    Format: {ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}
    Example: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.dxf
    
    Args:
        metadata: NormalizedMetadata object
    
    Returns:
        Standardized filename string
    """
    parts = []
    
    # Client code (required)
    if metadata.client_code:
        # Remove hyphens and clean
        client_code = metadata.client_code.replace('-', '').replace(' ', '')
        parts.append(client_code)
    else:
        parts.append('UNKNOWN')
        logger.warning("No client code provided, using 'UNKNOWN'")
    
    # Project code (required)
    if metadata.project_code:
        parts.append(metadata.project_code)
    else:
        parts.append('NOPROJECT')
        logger.warning("No project code provided, using 'NOPROJECT'")
    
    # Part name (required)
    if metadata.part_name:
        # Sanitize part name - remove special characters
        part_name = re.sub(r'[^a-zA-Z0-9_-]', '', metadata.part_name)
        if part_name:
            parts.append(part_name)
        else:
            parts.append('Part')
            logger.warning(f"Part name '{metadata.part_name}' sanitized to empty, using 'Part'")
    else:
        parts.append('Part')
        logger.warning("No part name provided, using 'Part'")
    
    # Material (required)
    if metadata.material:
        material_code = MATERIAL_CODE_MAP.get(metadata.material, 'UNK')
        parts.append(material_code)
    else:
        parts.append('UNK')
        logger.warning("No material provided, using 'UNK'")
    
    # Thickness (optional)
    if metadata.thickness_mm:
        # Format thickness to remove unnecessary decimals
        thickness = metadata.thickness_mm
        if thickness == int(thickness):
            parts.append(f'{int(thickness)}mm')
        else:
            parts.append(f'{thickness}mm')
    
    # Quantity (optional)
    if metadata.quantity and metadata.quantity > 1:
        parts.append(f'x{metadata.quantity}')
    
    # Version (optional)
    if metadata.version and metadata.version > 1:
        parts.append(f'v{metadata.version}')
    
    # Extension
    ext = Path(metadata.source_file).suffix if '.' in metadata.source_file else '.bin'
    
    filename = '-'.join(parts) + ext
    
    logger.info(f"Generated filename: {filename}")
    return filename


def handle_filename_collision(
    filename: str,
    client_code: str,
    project_code: str,
    base_path: Path
) -> str:
    """
    Handle filename collisions by appending -v2, -v3, etc.
    
    Args:
        filename: Original filename
        client_code: Client code (e.g., 'CL0001')
        project_code: Project code (e.g., 'JB-2025-10-CL0001-001')
        base_path: Base path for file storage
    
    Returns:
        Unique filename with version suffix if needed
    """
    # Construct full path
    target_path = base_path / 'clients' / client_code / 'projects' / project_code / 'inputs' / filename
    
    if not target_path.exists():
        logger.info(f"No collision for {filename}")
        return filename
    
    # File exists, increment version
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    version = 2
    
    # Remove existing version suffix if present
    version_pattern = r'-v\d+$'
    name = re.sub(version_pattern, '', name)
    
    while True:
        new_filename = f'{name}-v{version}.{ext}' if ext else f'{name}-v{version}'
        new_path = base_path / 'clients' / client_code / 'projects' / project_code / 'inputs' / new_filename
        
        if not new_path.exists():
            logger.info(f"Collision resolved: {filename} -> {new_filename}")
            return new_filename
        
        version += 1
        
        if version > 100:  # Safety limit
            logger.error(f"Too many versions of file: {filename}")
            raise ValueError(f"Too many versions of file: {filename} (limit: 100)")


def parse_filename_metadata(filename: str) -> dict:
    """
    Parse metadata from standardized filename.

    Format: {ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}

    Args:
        filename: Filename to parse

    Returns:
        Dictionary with extracted metadata
    """
    # Remove extension
    name = Path(filename).stem

    # Pattern for standardized filename
    # Example: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1
    # Client code: CL0001 (letters + numbers)
    # Project code: JB-2025-10-CL0001-001 (specific format with hyphens)
    # Part name: BracketLeft (alphanumeric, underscores, hyphens)
    # Material code: MS (uppercase letters)
    # Thickness: 5mm (optional)
    # Quantity: x14 (optional)
    # Version: v1 (optional)

    # More specific pattern that handles project codes with hyphens
    # Match client code, then project code (letters-year-month-client-number), then rest
    pattern = r'^([A-Z0-9]+)-([A-Z]+-\d{4}-\d{2}-[A-Z0-9]+-\d{3})-([A-Za-z0-9_]+)-([A-Z]+)(?:-(\d+\.?\d*)mm)?(?:-x(\d+))?(?:-v(\d+))?$'

    match = re.match(pattern, name)

    if match:
        client_code, project_code, part_name, material_code, thickness, quantity, version = match.groups()

        # Reverse material code lookup
        material = None
        for mat_name, code in MATERIAL_CODE_MAP.items():
            if code == material_code:
                material = mat_name
                break

        return {
            'client_code': client_code,
            'project_code': project_code,
            'part_name': part_name,
            'material': material or material_code,
            'thickness_mm': float(thickness) if thickness else None,
            'quantity': int(quantity) if quantity else 1,
            'version': int(version) if version else 1
        }

    logger.warning(f"Could not parse filename: {filename}")
    return {}


def extract_client_project_from_filename(filename: str) -> tuple:
    """
    Extract client code and project code from filename.
    
    Args:
        filename: Filename to parse
    
    Returns:
        Tuple of (client_code, project_code) or (None, None)
    """
    metadata = parse_filename_metadata(filename)
    return metadata.get('client_code'), metadata.get('project_code')

