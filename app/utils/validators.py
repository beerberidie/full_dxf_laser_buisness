"""
Laser OS Tier 1 - Validation Utilities

This module provides validation functions for various data types.
"""

import re
from datetime import datetime


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_email('test@example.com')
        True
        >>> validate_email('invalid-email')
        False
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """
    Validate phone number format (basic validation).
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_phone('+27 11 123 4567')
        True
        >>> validate_phone('abc')
        False
    """
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it contains only digits and optional + prefix
    pattern = r'^\+?\d{10,15}$'
    return re.match(pattern, cleaned) is not None


def validate_date(date_str, format='%Y-%m-%d'):
    """
    Validate date string format.
    
    Args:
        date_str (str): Date string to validate
        format (str): Expected date format (default: '%Y-%m-%d')
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_date('2025-10-06')
        True
        >>> validate_date('invalid')
        False
    """
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_required(value):
    """
    Validate that a value is not empty.
    
    Args:
        value: Value to validate
    
    Returns:
        bool: True if not empty, False otherwise
    
    Example:
        >>> validate_required('test')
        True
        >>> validate_required('')
        False
        >>> validate_required(None)
        False
    """
    if value is None:
        return False
    
    if isinstance(value, str):
        return value.strip() != ''
    
    return True


def validate_numeric(value, min_value=None, max_value=None):
    """
    Validate that a value is numeric and optionally within a range.
    
    Args:
        value: Value to validate
        min_value (float, optional): Minimum allowed value
        max_value (float, optional): Maximum allowed value
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_numeric('123')
        True
        >>> validate_numeric('123', min_value=100, max_value=200)
        True
        >>> validate_numeric('abc')
        False
    """
    try:
        num = float(value)
        
        if min_value is not None and num < min_value:
            return False
        
        if max_value is not None and num > max_value:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension.
    
    Args:
        filename (str): Filename to validate
        allowed_extensions (set): Set of allowed extensions (without dots)
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_file_extension('test.dxf', {'dxf', 'pdf'})
        True
        >>> validate_file_extension('test.exe', {'dxf', 'pdf'})
        False
    """
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def validate_dxf_filename(filename):
    """
    Validate DXF filename format according to specification.
    
    Expected format: [USERCODE]-[part]-[material]-[thickness]-[qty].dxf
    Example: ABC-bracket-MS-3mm-10.dxf
    
    Args:
        filename (str): Filename to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_dxf_filename('ABC-bracket-MS-3mm-10.dxf')
        True
        >>> validate_dxf_filename('invalid.dxf')
        False
    """
    if not filename:
        return False
    
    # Pattern: [USERCODE]-[part]-[material]-[thickness]-[qty].dxf
    pattern = r'^[A-Z0-9]{2,8}-[a-zA-Z0-9_-]+-[A-Z]{2,4}-[0-9.]+(?:mm)?-[0-9]+\.dxf$'
    return re.match(pattern, filename, re.IGNORECASE) is not None


def sanitize_filename(filename):
    """
    Sanitize filename by removing or replacing invalid characters.
    
    Args:
        filename (str): Filename to sanitize
    
    Returns:
        str: Sanitized filename
    
    Example:
        >>> sanitize_filename('test file!@#.dxf')
        'test_file___.dxf'
    """
    if not filename:
        return ''
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    return sanitized

