"""
Gas Type Service for Laser OS.

This service provides automatic gas type selection based on material type
and thickness according to business rules.

Phase 10 Implementation.
"""

from typing import Optional


def get_recommended_gas_type(material_type: str, thickness: float) -> str:
    """
    Get recommended gas type based on material and thickness.
    
    Business Rules:
    - Thickness >= 6mm and <= 16mm: Always Oxygen (OXY)
    - Thickness < 6mm:
        - Aluminum or Zinc: Nitrogen
        - All other materials: Air
    
    Args:
        material_type: Type of material (e.g., 'Mild Steel', 'Aluminum', 'Zinc')
        thickness: Material thickness in millimeters
    
    Returns:
        str: Recommended gas type ('Oxygen', 'Nitrogen', or 'Air')
    
    Examples:
        >>> get_recommended_gas_type('Mild Steel', 8.0)
        'Oxygen'
        
        >>> get_recommended_gas_type('Aluminum', 3.0)
        'Nitrogen'
        
        >>> get_recommended_gas_type('Mild Steel', 2.0)
        'Air'
    """
    # Rule 1: 6mm to 16mm always uses Oxygen
    if 6.0 <= thickness <= 16.0:
        return 'Oxygen'
    
    # Rule 2: < 6mm - check material type
    if thickness < 6.0:
        # Aluminum and Zinc require Nitrogen
        if material_type in ['Aluminum', 'Zinc']:
            return 'Nitrogen'
        
        # All other materials use Air
        return 'Air'
    
    # Default fallback for thickness > 16mm (edge case)
    return 'Oxygen'


def validate_thickness(thickness: float) -> bool:
    """
    Validate if thickness is within allowed range and increments.
    
    Allowed values:
    - 0.47mm (thin Carbon Steel)
    - 0.53mm (thin Carbon Steel)
    - 1.0mm to 16.0mm in 0.5mm increments
    
    Args:
        thickness: Material thickness in millimeters
    
    Returns:
        bool: True if thickness is valid, False otherwise
    
    Examples:
        >>> validate_thickness(0.47)
        True
        
        >>> validate_thickness(1.5)
        True
        
        >>> validate_thickness(1.3)
        False
    """
    # Special thin values for Carbon Steel
    if thickness in [0.47, 0.53]:
        return True
    
    # Check if within range 1.0 to 16.0
    if not (1.0 <= thickness <= 16.0):
        return False
    
    # Check if it's a valid 0.5mm increment
    # Convert to avoid floating point precision issues
    thickness_times_10 = round(thickness * 10)
    
    # Valid if it's a multiple of 5 (0.5mm increments)
    return thickness_times_10 % 5 == 0


def get_allowed_thicknesses() -> list:
    """
    Get list of all allowed thickness values.
    
    Returns:
        list: Sorted list of allowed thickness values in mm
    
    Example:
        >>> thicknesses = get_allowed_thicknesses()
        >>> len(thicknesses)
        33
        >>> thicknesses[0]
        0.47
        >>> thicknesses[-1]
        16.0
    """
    thicknesses = [0.47, 0.53]  # Special thin values
    
    # Add 1.0 to 16.0 in 0.5mm increments
    current = 1.0
    while current <= 16.0:
        thicknesses.append(current)
        current += 0.5
    
    return sorted(thicknesses)


def format_thickness_options() -> list:
    """
    Get formatted thickness options for dropdown display.
    
    Returns:
        list: List of tuples (value, display_text) for dropdown options
    
    Example:
        >>> options = format_thickness_options()
        >>> options[0]
        (0.47, '0.47mm (Thin Carbon Steel)')
        >>> options[2]
        (1.0, '1.0mm')
    """
    options = []
    
    # Special thin values with labels
    options.append((0.47, '0.47mm (Thin Carbon Steel)'))
    options.append((0.53, '0.53mm (Thin Carbon Steel)'))
    
    # Standard increments
    current = 1.0
    while current <= 16.0:
        options.append((current, f'{current}mm'))
        current += 0.5
    
    return options


def get_gas_type_description(gas_type: str) -> str:
    """
    Get description of gas type and its typical uses.
    
    Args:
        gas_type: Gas type ('Oxygen', 'Nitrogen', or 'Air')
    
    Returns:
        str: Description of the gas type
    """
    descriptions = {
        'Oxygen': 'High-speed cutting for thick materials (6mm-16mm). Produces oxide layer on cut edge.',
        'Nitrogen': 'Clean cutting for non-ferrous metals (Aluminum, Zinc). Prevents oxidation.',
        'Air': 'Cost-effective cutting for thin ferrous metals (<6mm). General purpose.'
    }
    
    return descriptions.get(gas_type, 'Unknown gas type')


def suggest_gas_pressure(material_type: str, thickness: float, gas_type: str) -> Optional[float]:
    """
    Suggest gas pressure based on material, thickness, and gas type.
    
    This is a basic suggestion - actual pressure should be fine-tuned
    based on machine specifications and cutting tests.
    
    Args:
        material_type: Type of material
        thickness: Material thickness in mm
        gas_type: Gas type being used
    
    Returns:
        float: Suggested pressure in bar, or None if no suggestion available
    
    Note:
        These are general guidelines. Always refer to machine manual
        and conduct test cuts for optimal settings.
    """
    # This is a placeholder for future enhancement
    # Actual pressure values should be determined through testing
    # and stored in machine settings presets
    
    if gas_type == 'Oxygen':
        # Oxygen pressure typically increases with thickness
        if thickness < 3.0:
            return 0.5
        elif thickness < 6.0:
            return 1.0
        elif thickness < 10.0:
            return 1.5
        else:
            return 2.0
    
    elif gas_type == 'Nitrogen':
        # Nitrogen typically requires higher pressure
        if thickness < 3.0:
            return 8.0
        elif thickness < 6.0:
            return 12.0
        else:
            return 15.0
    
    elif gas_type == 'Air':
        # Air pressure is moderate
        if thickness < 3.0:
            return 4.0
        else:
            return 6.0
    
    return None

