#!/usr/bin/env python
"""
Laser OS Tier 1 - Database Restore Script

This script restores the database from a backup file.

Features:
- Lists available backups
- Allows selection of backup to restore
- Creates a safety backup before restoring
- Verifies backup integrity before restoring
- Logs all operations

Usage:
    python scripts/restore_database.py [--backup FILENAME]

Arguments:
    --backup FILENAME    Specific backup file to restore (optional)

Examples:
    python scripts/restore_database.py                                    # Interactive mode
    python scripts/restore_database.py --backup laser_os_backup_20251018_020000.db

WARNING: This will replace the current database with the backup!
         A safety backup of the current database will be created first.

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
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def setup_logging():
    """Set up basic logging."""
    import logging
    
    project_root = get_project_root()
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'restore.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def verify_database_file(db_path):
    """Verify that a file is a valid SQLite database."""
    if not db_path.exists() or not db_path.is_file():
        return False
    
    try:
        with open(db_path, 'rb') as f:
            header = f.read(16)
            return header.startswith(b'SQLite format 3')
    except:
        return False


def list_available_backups(backup_dir):
    """List all available backup files."""
    backups = sorted(
        backup_dir.glob('laser_os_backup_*.db'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return backups


def create_safety_backup(db_path, backup_dir, logger):
    """Create a safety backup before restoring."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safety_backup = backup_dir / f'laser_os_safety_backup_{timestamp}.db'
    
    try:
        logger.info(f'Creating safety backup: {safety_backup.name}')
        shutil.copy2(db_path, safety_backup)
        logger.info('✓ Safety backup created')
        return safety_backup
    except Exception as e:
        logger.error(f'Failed to create safety backup: {str(e)}')
        return None


def restore_backup(backup_path, db_path, logger):
    """Restore database from backup."""
    try:
        logger.info(f'Restoring from: {backup_path.name}')
        logger.info(f'Target: {db_path}')
        
        # Verify backup is valid
        if not verify_database_file(backup_path):
            logger.error('Backup file is not a valid SQLite database')
            return False
        
        # Copy backup to database location
        shutil.copy2(backup_path, db_path)
        
        # Verify restored database
        if not verify_database_file(db_path):
            logger.error('Restored database is not valid')
            return False
        
        logger.info('✓ Database restored successfully')
        return True
        
    except Exception as e:
        logger.error(f'Failed to restore database: {str(e)}')
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Restore database from backup for Laser OS Tier 1'
    )
    parser.add_argument(
        '--backup',
        type=str,
        help='Specific backup file to restore'
    )
    args = parser.parse_args()
    
    logger = setup_logging()
    
    logger.info('=' * 80)
    logger.info('Laser OS Tier 1 - Database Restore Script')
    logger.info('=' * 80)
    
    project_root = get_project_root()
    db_path = project_root / 'data' / 'laser_os.db'
    backup_dir = project_root / 'data' / 'backups'
    
    # Check if backup directory exists
    if not backup_dir.exists():
        logger.error(f'Backup directory not found: {backup_dir}')
        sys.exit(1)
    
    # Get available backups
    backups = list_available_backups(backup_dir)
    
    if not backups:
        logger.error('No backups found')
        sys.exit(1)
    
    logger.info(f'Found {len(backups)} backup(s)')
    
    # Select backup to restore
    if args.backup:
        backup_path = backup_dir / args.backup
        if not backup_path.exists():
            logger.error(f'Backup not found: {args.backup}')
            sys.exit(1)
    else:
        # Interactive mode
        print('\nAvailable backups:')
        for i, backup in enumerate(backups, 1):
            size = backup.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f'{i}. {backup.name} ({size:.2f} MB) - {mtime.strftime("%Y-%m-%d %H:%M:%S")}')
        
        try:
            choice = int(input('\nSelect backup to restore (1-{}): '.format(len(backups))))
            if choice < 1 or choice > len(backups):
                logger.error('Invalid selection')
                sys.exit(1)
            backup_path = backups[choice - 1]
        except (ValueError, KeyboardInterrupt):
            logger.error('Restore cancelled')
            sys.exit(1)
    
    # Confirm restore
    print(f'\nWARNING: This will replace the current database with:')
    print(f'  {backup_path.name}')
    print(f'\nA safety backup will be created first.')
    
    try:
        confirm = input('\nContinue? (yes/no): ').strip().lower()
        if confirm not in ['yes', 'y']:
            logger.info('Restore cancelled by user')
            sys.exit(0)
    except KeyboardInterrupt:
        logger.info('Restore cancelled')
        sys.exit(0)
    
    # Create safety backup
    safety_backup = create_safety_backup(db_path, backup_dir, logger)
    if not safety_backup:
        logger.error('Failed to create safety backup. Aborting restore.')
        sys.exit(1)
    
    # Restore database
    if restore_backup(backup_path, db_path, logger):
        logger.info('=' * 80)
        logger.info('Database restored successfully!')
        logger.info(f'Safety backup saved as: {safety_backup.name}')
        logger.info('=' * 80)
        sys.exit(0)
    else:
        logger.error('Restore failed!')
        logger.info(f'Original database preserved in safety backup: {safety_backup.name}')
        sys.exit(1)


if __name__ == '__main__':
    main()

