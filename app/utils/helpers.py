"""
Laser OS Tier 1 - Helper Utilities

This module provides general helper functions.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path


def ensure_dir(directory):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory (str or Path): Directory path
    
    Returns:
        Path: Path object for the directory
    
    Example:
        >>> ensure_dir('data/files/clients')
        PosixPath('data/files/clients')
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(filepath):
    """
    Get file size in bytes.
    
    Args:
        filepath (str or Path): File path
    
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    
    Example:
        >>> get_file_size('test.txt')
        1024
    """
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0


def format_file_size(bytes):
    """
    Format bytes as human-readable file size.
    
    Args:
        bytes (int): File size in bytes
    
    Returns:
        str: Formatted file size
    
    Example:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
    """
    if bytes is None or bytes == 0:
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f'{bytes:.1f} {unit}'
        bytes /= 1024.0
    
    return f'{bytes:.1f} PB'


def calculate_due_date(start_date=None, sla_days=3):
    """
    Calculate due date based on SLA days.
    
    Args:
        start_date (datetime, optional): Start date (default: now)
        sla_days (int): Number of SLA days (default: 3)
    
    Returns:
        datetime: Due date
    
    Example:
        >>> calculate_due_date(sla_days=5)
        datetime.datetime(2025, 10, 11, ...)
    """
    if start_date is None:
        start_date = datetime.utcnow()
    
    return start_date + timedelta(days=sla_days)


def truncate_string(text, max_length=50, suffix='...'):
    """
    Truncate a string to a maximum length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length (default: 50)
        suffix (str): Suffix to add if truncated (default: '...')
    
    Returns:
        str: Truncated text
    
    Example:
        >>> truncate_string('This is a very long text', max_length=10)
        'This is...'
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_dxf_filename(filename):
    """
    Parse DXF filename into components.
    
    Expected format: [USERCODE]-[part]-[material]-[thickness]-[qty].dxf
    
    Args:
        filename (str): DXF filename
    
    Returns:
        dict: Parsed components or None if invalid
    
    Example:
        >>> parse_dxf_filename('ABC-bracket-MS-3mm-10.dxf')
        {
            'usercode': 'ABC',
            'part_name': 'bracket',
            'material': 'MS',
            'thickness': '3mm',
            'quantity': '10',
            'extension': 'dxf'
        }
    """
    if not filename:
        return None
    
    # Remove extension
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    extension = filename.rsplit('.', 1)[1] if '.' in filename else ''
    
    # Split by hyphen
    parts = name_without_ext.split('-')
    
    if len(parts) < 5:
        return None
    
    return {
        'usercode': parts[0],
        'part_name': '-'.join(parts[1:-3]),  # Handle multi-part names
        'material': parts[-3],
        'thickness': parts[-2],
        'quantity': parts[-1],
        'extension': extension
    }


def get_client_directory(upload_folder, client_code):
    """
    Get the directory path for a client.
    
    Args:
        upload_folder (str or Path): Base upload folder
        client_code (str): Client code (e.g., 'CL-0001')
    
    Returns:
        Path: Client directory path
    
    Example:
        >>> get_client_directory('data/files', 'CL-0001')
        PosixPath('data/files/clients/CL-0001')
    """
    return Path(upload_folder) / 'clients' / client_code


def get_project_directory(upload_folder, client_code, project_code):
    """
    Get the directory path for a project.
    
    Args:
        upload_folder (str or Path): Base upload folder
        client_code (str): Client code (e.g., 'CL-0001')
        project_code (str): Project code (e.g., 'JB-2025-10-CL0001-001')
    
    Returns:
        Path: Project directory path
    
    Example:
        >>> get_project_directory('data/files', 'CL-0001', 'JB-2025-10-CL0001-001')
        PosixPath('data/files/clients/CL-0001/projects/JB-2025-10-CL0001-001')
    """
    return get_client_directory(upload_folder, client_code) / 'projects' / project_code


def get_dxf_directory(upload_folder, client_code, project_code):
    """
    Get the DXF directory path for a project.
    
    Args:
        upload_folder (str or Path): Base upload folder
        client_code (str): Client code
        project_code (str): Project code
    
    Returns:
        Path: DXF directory path
    
    Example:
        >>> get_dxf_directory('data/files', 'CL-0001', 'JB-2025-10-CL0001-001')
        PosixPath('data/files/clients/CL-0001/projects/JB-2025-10-CL0001-001/dxf')
    """
    return get_project_directory(upload_folder, client_code, project_code) / 'dxf'


def format_currency(amount):
    """
    Format amount as ZAR currency.
    
    Args:
        amount (float): Amount to format
    
    Returns:
        str: Formatted currency string
    
    Example:
        >>> format_currency(1234.56)
        'R 1,234.56'
    """
    if amount is None:
        return 'R 0.00'
    
    return f'R {amount:,.2f}'


def parse_thickness(thickness_str):
    """
    Parse thickness string to float (in mm).
    
    Args:
        thickness_str (str): Thickness string (e.g., '3mm', '3.0', '3')
    
    Returns:
        float: Thickness in mm, or None if invalid
    
    Example:
        >>> parse_thickness('3mm')
        3.0
        >>> parse_thickness('3.5')
        3.5
    """
    if not thickness_str:
        return None
    
    # Remove 'mm' suffix if present
    cleaned = thickness_str.lower().replace('mm', '').strip()
    
    try:
        return float(cleaned)
    except ValueError:
        return None

