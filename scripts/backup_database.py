#!/usr/bin/env python
"""
Laser OS Tier 1 - Automated Database Backup Script

This script creates timestamped backups of the SQLite database and automatically
cleans up old backups to prevent disk space issues.

Features:
- Creates timestamped backup files (YYYYMMDD_HHMMSS format)
- Stores backups in data/backups/ directory
- Automatically removes old backups (keeps last 30 by default)
- Verifies backup integrity
- Logs all operations
- Can be scheduled with Windows Task Scheduler or cron

Usage:
    python scripts/backup_database.py [--keep N]

Arguments:
    --keep N    Number of backups to keep (default: 30)

Examples:
    python scripts/backup_database.py              # Keep last 30 backups
    python scripts/backup_database.py --keep 60    # Keep last 60 backups

Schedule with Windows Task Scheduler:
    1. Open Task Scheduler
    2. Create Basic Task
    3. Name: "Laser OS Database Backup"
    4. Trigger: Daily at 2:00 AM
    5. Action: Start a program
    6. Program: C:\path\to\python.exe
    7. Arguments: C:\path\to\scripts\backup_database.py
    8. Start in: C:\path\to\project\root

Schedule with cron (Linux/Mac):
    # Add to crontab (crontab -e)
    0 2 * * * cd /path/to/project && python scripts/backup_database.py

Author: Augment Agent
Date: October 18, 2025
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path


def get_project_root():
    """
    Get the project root directory.
    
    Returns:
        Path: Project root directory
    """
    # Script is in scripts/ directory, so parent is project root
    script_dir = Path(__file__).parent
    return script_dir.parent


def setup_logging():
    """
    Set up basic logging to console and file.
    
    Returns:
        Logger instance
    """
    import logging
    
    project_root = get_project_root()
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'backup.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def verify_database_exists(db_path):
    """
    Verify that the database file exists and is readable.
    
    Args:
        db_path (Path): Path to database file
        
    Returns:
        bool: True if database exists and is readable
    """
    if not db_path.exists():
        return False
    
    if not db_path.is_file():
        return False
    
    # Try to read the file to verify permissions
    try:
        with open(db_path, 'rb') as f:
            # Read first 16 bytes to verify it's a SQLite database
            header = f.read(16)
            if not header.startswith(b'SQLite format 3'):
                return False
        return True
    except (IOError, PermissionError):
        return False


def get_database_size(db_path):
    """
    Get the size of the database file in MB.
    
    Args:
        db_path (Path): Path to database file
        
    Returns:
        float: Size in MB
    """
    size_bytes = db_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)


def create_backup(db_path, backup_dir, logger):
    """
    Create a timestamped backup of the database.
    
    Args:
        db_path (Path): Path to database file
        backup_dir (Path): Directory to store backups
        logger: Logger instance
        
    Returns:
        Path: Path to created backup file, or None if failed
    """
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp-based filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'laser_os_backup_{timestamp}.db'
    backup_path = backup_dir / backup_filename
    
    try:
        logger.info(f'Creating backup: {backup_filename}')
        logger.info(f'Source: {db_path}')
        logger.info(f'Destination: {backup_path}')
        
        # Get source database size
        source_size = get_database_size(db_path)
        logger.info(f'Database size: {source_size} MB')
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Verify backup was created successfully
        if not backup_path.exists():
            logger.error('Backup file was not created')
            return None
        
        # Verify backup size matches source
        backup_size = get_database_size(backup_path)
        if backup_size != source_size:
            logger.warning(f'Backup size ({backup_size} MB) differs from source ({source_size} MB)')
        
        # Verify backup is a valid SQLite database
        if not verify_database_exists(backup_path):
            logger.error('Backup file is not a valid SQLite database')
            backup_path.unlink()  # Delete invalid backup
            return None
        
        logger.info(f'✓ Backup created successfully: {backup_filename} ({backup_size} MB)')
        return backup_path
        
    except Exception as e:
        logger.error(f'Failed to create backup: {str(e)}')
        # Clean up partial backup if it exists
        if backup_path.exists():
            try:
                backup_path.unlink()
            except:
                pass
        return None


def cleanup_old_backups(backup_dir, keep_count, logger):
    """
    Remove old backups, keeping only the most recent N backups.
    
    Args:
        backup_dir (Path): Directory containing backups
        keep_count (int): Number of backups to keep
        logger: Logger instance
        
    Returns:
        int: Number of backups deleted
    """
    try:
        # Get all backup files sorted by modification time (newest first)
        backups = sorted(
            backup_dir.glob('laser_os_backup_*.db'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        total_backups = len(backups)
        logger.info(f'Found {total_backups} backup(s) in {backup_dir}')
        
        if total_backups <= keep_count:
            logger.info(f'No cleanup needed (keeping {keep_count} backups)')
            return 0
        
        # Delete old backups
        backups_to_delete = backups[keep_count:]
        deleted_count = 0
        freed_space = 0
        
        for backup in backups_to_delete:
            try:
                size = get_database_size(backup)
                backup.unlink()
                deleted_count += 1
                freed_space += size
                logger.info(f'Deleted old backup: {backup.name} ({size} MB)')
            except Exception as e:
                logger.error(f'Failed to delete {backup.name}: {str(e)}')
        
        logger.info(f'✓ Cleanup complete: Deleted {deleted_count} old backup(s), freed {round(freed_space, 2)} MB')
        return deleted_count
        
    except Exception as e:
        logger.error(f'Failed to cleanup old backups: {str(e)}')
        return 0


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Automated database backup script for Laser OS Tier 1'
    )
    parser.add_argument(
        '--keep',
        type=int,
        default=30,
        help='Number of backups to keep (default: 30)'
    )
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging()
    
    logger.info('=' * 80)
    logger.info('Laser OS Tier 1 - Database Backup Script')
    logger.info('=' * 80)
    
    # Get paths
    project_root = get_project_root()
    db_path = project_root / 'data' / 'laser_os.db'
    backup_dir = project_root / 'data' / 'backups'
    
    logger.info(f'Project root: {project_root}')
    logger.info(f'Database path: {db_path}')
    logger.info(f'Backup directory: {backup_dir}')
    logger.info(f'Keeping last {args.keep} backups')
    
    # Verify database exists
    if not verify_database_exists(db_path):
        logger.error(f'Database not found or not readable: {db_path}')
        logger.error('Please ensure the database exists and you have read permissions')
        sys.exit(1)
    
    # Create backup
    backup_path = create_backup(db_path, backup_dir, logger)
    if not backup_path:
        logger.error('Backup failed!')
        sys.exit(1)
    
    # Cleanup old backups
    cleanup_old_backups(backup_dir, args.keep, logger)
    
    logger.info('=' * 80)
    logger.info('Backup completed successfully!')
    logger.info('=' * 80)
    
    sys.exit(0)


if __name__ == '__main__':
    main()

