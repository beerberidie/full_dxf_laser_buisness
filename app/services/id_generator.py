"""
Laser OS Tier 1 - ID Generator Service

This module provides functions to generate unique IDs for clients and projects.
"""

from datetime import datetime
from app import db
from app.models import Client


def generate_client_code():
    """
    Generate a unique client code in format CL-xxxx.
    
    Finds the highest existing client code and increments by 1.
    
    Returns:
        str: Client code in format CL-0001, CL-0002, etc.
    
    Example:
        >>> code = generate_client_code()
        >>> print(code)
        'CL-0001'
    """
    # Query the highest client code
    last_client = Client.query.order_by(Client.client_code.desc()).first()
    
    if last_client and last_client.client_code:
        # Extract number from CL-xxxx format
        try:
            last_number = int(last_client.client_code.split('-')[1])
            new_number = last_number + 1
        except (IndexError, ValueError):
            # If parsing fails, start from 1
            new_number = 1
    else:
        # No clients yet, start from 1
        new_number = 1
    
    # Format as CL-xxxx with zero padding
    return f'CL-{new_number:04d}'


def generate_project_code(client_code):
    """
    Generate a unique project code in format JB-yyyy-mm-client-###.

    Args:
        client_code (str): Client code (e.g., 'CL-0001')

    Returns:
        str: Project code in format JB-2025-10-CL0001-001

    Example:
        >>> code = generate_project_code('CL-0001')
        >>> print(code)
        'JB-2025-10-CL0001-001'
    """
    from app.models import Project

    # Get current year and month
    now = datetime.utcnow()
    year = now.year
    month = f'{now.month:02d}'

    # Clean client code (remove hyphen for compact format)
    client_part = client_code.replace('-', '')

    # Build prefix
    prefix = f'JB-{year}-{month}-{client_part}'

    # Count existing projects with this prefix
    project_count = Project.query.filter(
        Project.project_code.like(f'{prefix}-%')
    ).count()

    # Generate new code
    return f'{prefix}-{project_count + 1:03d}'


def validate_client_code(code):
    """
    Validate client code format.
    
    Args:
        code (str): Client code to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_client_code('CL-0001')
        True
        >>> validate_client_code('INVALID')
        False
    """
    if not code:
        return False
    
    parts = code.split('-')
    if len(parts) != 2:
        return False
    
    if parts[0] != 'CL':
        return False
    
    try:
        number = int(parts[1])
        return 1 <= number <= 9999
    except ValueError:
        return False


def validate_project_code(code):
    """
    Validate project code format.
    
    Args:
        code (str): Project code to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_project_code('JB-2025-10-CL0001-001')
        True
        >>> validate_project_code('INVALID')
        False
    
    Note:
        This function will be fully implemented in Phase 2.
    """
    if not code:
        return False
    
    parts = code.split('-')
    if len(parts) != 5:
        return False
    
    # Check prefix
    if parts[0] != 'JB':
        return False
    
    # Check year (4 digits)
    try:
        year = int(parts[1])
        if not (2020 <= year <= 2099):
            return False
    except ValueError:
        return False
    
    # Check month (2 digits, 01-12)
    try:
        month = int(parts[2])
        if not (1 <= month <= 12):
            return False
    except ValueError:
        return False
    
    # Check client code part (CLxxxx format)
    if not parts[3].startswith('CL'):
        return False
    
    # Check sequence number (3 digits)
    try:
        seq = int(parts[4])
        if not (1 <= seq <= 999):
            return False
    except ValueError:
        return False
    
    return True

