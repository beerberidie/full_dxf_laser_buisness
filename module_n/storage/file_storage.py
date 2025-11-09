"""
Module N - File Storage
Handles file storage to local filesystem with organized directory structure
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple
import re

from ..config import get_upload_folder

# Configure logging
logger = logging.getLogger(__name__)


def ensure_directory(directory: Path) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
    
    Returns:
        True on success, False on error
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False


def get_storage_path(client_code: Optional[str] = None, project_code: Optional[str] = None) -> Path:
    """
    Get storage path for a file based on client and project codes
    
    Args:
        client_code: Client code (e.g., 'CL0001')
        project_code: Project code (e.g., 'JB-2025-10-CL0001-001')
    
    Returns:
        Path object for storage directory
    """
    base_path = get_upload_folder()
    
    if client_code and project_code:
        # Organized structure: data/files/{client_code}/{project_code}/
        return base_path / client_code / project_code
    elif client_code:
        # Client-only structure: data/files/{client_code}/
        return base_path / client_code
    else:
        # Default structure: data/files/uncategorized/
        return base_path / "uncategorized"


def get_next_version(directory: Path, base_filename: str) -> int:
    """
    Get the next version number for a file
    
    Args:
        directory: Directory to check for existing files
        base_filename: Base filename without version (e.g., 'CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10')
    
    Returns:
        Next version number
    """
    if not directory.exists():
        return 1
    
    # Pattern to match versioned files
    # Example: CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf
    pattern = re.compile(rf"{re.escape(base_filename)}-v(\d+)\.")
    
    max_version = 0
    for file_path in directory.iterdir():
        if file_path.is_file():
            match = pattern.search(file_path.name)
            if match:
                version = int(match.group(1))
                max_version = max(max_version, version)
    
    return max_version + 1


def save_file(
    source_path: str,
    normalized_filename: str,
    client_code: Optional[str] = None,
    project_code: Optional[str] = None,
    auto_version: bool = True
) -> Optional[Tuple[str, str]]:
    """
    Save file to storage with normalized filename
    
    Args:
        source_path: Path to source file (temporary upload)
        normalized_filename: Normalized filename from filename generator
        client_code: Client code for directory organization
        project_code: Project code for directory organization
        auto_version: Automatically increment version if file exists
    
    Returns:
        Tuple of (stored_filename, file_path) or None on error
    """
    try:
        # Get storage directory
        storage_dir = get_storage_path(client_code, project_code)
        
        # Ensure directory exists
        if not ensure_directory(storage_dir):
            return None
        
        # Handle versioning if auto_version is enabled
        if auto_version:
            # Extract base filename and extension
            file_path_obj = Path(normalized_filename)
            extension = file_path_obj.suffix
            base_name = file_path_obj.stem
            
            # Check if filename already has version
            version_match = re.search(r'-v(\d+)$', base_name)
            if version_match:
                # Remove existing version
                base_name_no_version = base_name[:version_match.start()]
            else:
                base_name_no_version = base_name
            
            # Get next version
            next_version = get_next_version(storage_dir, base_name_no_version)
            
            # Create versioned filename
            stored_filename = f"{base_name_no_version}-v{next_version}{extension}"
        else:
            stored_filename = normalized_filename
        
        # Full destination path
        dest_path = storage_dir / stored_filename
        
        # Copy file to destination
        shutil.copy2(source_path, dest_path)
        
        # Get relative path from upload folder
        relative_path = dest_path.relative_to(get_upload_folder())
        file_path = str(relative_path).replace('\\', '/')
        
        logger.info(f"Saved file: {stored_filename} to {file_path}")
        return (stored_filename, file_path)
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


def get_file_path(file_path: str) -> Optional[Path]:
    """
    Get full file path from relative path
    
    Args:
        file_path: Relative file path from database
    
    Returns:
        Full Path object or None if file doesn't exist
    """
    try:
        full_path = get_upload_folder() / file_path
        
        if full_path.exists():
            return full_path
        else:
            logger.warning(f"File not found: {full_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting file path: {e}")
        return None


def delete_file(file_path: str) -> bool:
    """
    Delete file from storage
    
    Args:
        file_path: Relative file path from database
    
    Returns:
        True on success, False on error
    """
    try:
        full_path = get_upload_folder() / file_path
        
        if full_path.exists():
            full_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False


def file_exists(file_path: str) -> bool:
    """
    Check if file exists in storage
    
    Args:
        file_path: Relative file path from database
    
    Returns:
        True if file exists, False otherwise
    """
    try:
        full_path = get_upload_folder() / file_path
        return full_path.exists()
    except Exception as e:
        logger.error(f"Error checking file existence: {e}")
        return False


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes
    
    Args:
        file_path: Relative file path from database
    
    Returns:
        File size in bytes or None on error
    """
    try:
        full_path = get_upload_folder() / file_path
        
        if full_path.exists():
            return full_path.stat().st_size
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting file size: {e}")
        return None


def cleanup_empty_directories(client_code: Optional[str] = None) -> int:
    """
    Clean up empty directories in storage
    
    Args:
        client_code: Optional client code to limit cleanup scope
    
    Returns:
        Number of directories removed
    """
    count = 0
    try:
        if client_code:
            base_path = get_upload_folder() / client_code
        else:
            base_path = get_upload_folder()
        
        if not base_path.exists():
            return 0
        
        # Walk directory tree bottom-up
        for dirpath, dirnames, filenames in os.walk(base_path, topdown=False):
            dir_path = Path(dirpath)
            
            # Skip base path
            if dir_path == base_path:
                continue
            
            # Check if directory is empty
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
                count += 1
                logger.info(f"Removed empty directory: {dir_path}")
        
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up directories: {e}")
        return count

