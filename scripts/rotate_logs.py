#!/usr/bin/env python
"""
Log Rotation Script for Laser OS Tier 1

Manually rotate log files when needed.
Automatic rotation is handled by Python's RotatingFileHandler,
but this script can be used for manual rotation or cleanup.
"""

import os
import sys
import gzip
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def rotate_log_file(log_path, max_backups=10, compress=True):
    """
    Rotate a log file.
    
    Args:
        log_path (Path): Path to the log file
        max_backups (int): Maximum number of backup files to keep
        compress (bool): Whether to compress rotated logs
    
    Returns:
        bool: True if rotation successful, False otherwise
    """
    
    if not log_path.exists():
        print(f"✗ Log file not found: {log_path}")
        return False
    
    # Get file size
    file_size = log_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\nRotating: {log_path.name}")
    print(f"  Current size: {file_size_mb:.2f} MB")
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{log_path.stem}_{timestamp}{log_path.suffix}"
    backup_path = log_path.parent / backup_name
    
    # Copy current log to backup
    try:
        shutil.copy2(log_path, backup_path)
        print(f"  ✓ Created backup: {backup_name}")
    except Exception as e:
        print(f"  ✗ Failed to create backup: {e}")
        return False
    
    # Compress backup if requested
    if compress:
        try:
            compressed_path = Path(str(backup_path) + '.gz')
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            backup_path.unlink()
            print(f"  ✓ Compressed backup: {compressed_path.name}")
            backup_path = compressed_path
        except Exception as e:
            print(f"  ⚠ Failed to compress backup: {e}")
    
    # Clear current log file
    try:
        with open(log_path, 'w') as f:
            f.write('')
        print(f"  ✓ Cleared current log file")
    except Exception as e:
        print(f"  ✗ Failed to clear log file: {e}")
        return False
    
    # Clean up old backups
    cleanup_old_backups(log_path, max_backups)
    
    return True


def cleanup_old_backups(log_path, max_backups):
    """
    Remove old backup files, keeping only the most recent N backups.
    
    Args:
        log_path (Path): Path to the log file
        max_backups (int): Maximum number of backups to keep
    """
    
    # Find all backup files for this log
    log_dir = log_path.parent
    log_stem = log_path.stem
    
    # Pattern: logname_YYYYMMDD_HHMMSS.log or logname_YYYYMMDD_HHMMSS.log.gz
    backups = []
    for file in log_dir.glob(f"{log_stem}_*{log_path.suffix}*"):
        if file != log_path:
            backups.append(file)
    
    # Sort by modification time (newest first)
    backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Remove old backups
    backups_to_delete = backups[max_backups:]
    
    if backups_to_delete:
        print(f"  Cleaning up old backups (keeping {max_backups} most recent):")
        for backup in backups_to_delete:
            try:
                backup.unlink()
                print(f"    ✓ Removed: {backup.name}")
            except Exception as e:
                print(f"    ✗ Failed to remove {backup.name}: {e}")
    else:
        print(f"  ✓ No old backups to clean up ({len(backups)} total)")


def get_log_files(logs_dir):
    """Get all log files in the logs directory."""
    
    log_files = []
    
    for log_file in logs_dir.glob('*.log'):
        log_files.append(log_file)
    
    return sorted(log_files)


def main():
    """Main function."""
    
    parser = argparse.ArgumentParser(description='Rotate Laser OS log files')
    parser.add_argument('--log', help='Specific log file to rotate (e.g., laser_os, backup, performance)')
    parser.add_argument('--all', action='store_true', help='Rotate all log files')
    parser.add_argument('--max-backups', type=int, default=10, help='Maximum number of backups to keep (default: 10)')
    parser.add_argument('--no-compress', action='store_true', help='Do not compress rotated logs')
    parser.add_argument('--logs-dir', default='logs', help='Logs directory (default: logs)')
    
    args = parser.parse_args()
    
    logs_dir = project_root / args.logs_dir
    
    print(f"\n{'=' * 80}")
    print(f"Laser OS Tier 1 - Log Rotation")
    print(f"{'=' * 80}")
    print(f"\nLogs Directory: {logs_dir}")
    print(f"Max Backups: {args.max_backups}")
    print(f"Compress: {not args.no_compress}")
    
    # Ensure logs directory exists
    if not logs_dir.exists():
        print(f"\n✗ Logs directory not found: {logs_dir}")
        return 1
    
    # Determine which logs to rotate
    if args.log:
        # Rotate specific log
        log_path = logs_dir / f"{args.log}.log"
        if not log_path.exists():
            print(f"\n✗ Log file not found: {log_path}")
            return 1
        
        log_files = [log_path]
    
    elif args.all:
        # Rotate all logs
        log_files = get_log_files(logs_dir)
        if not log_files:
            print(f"\n✗ No log files found in {logs_dir}")
            return 1
    
    else:
        # Interactive mode - show available logs
        log_files = get_log_files(logs_dir)
        
        if not log_files:
            print(f"\n✗ No log files found in {logs_dir}")
            return 1
        
        print(f"\nAvailable log files:")
        for i, log_file in enumerate(log_files, 1):
            file_size = log_file.stat().st_size / (1024 * 1024)
            print(f"  {i}. {log_file.name} ({file_size:.2f} MB)")
        
        print(f"\nOptions:")
        print(f"  Enter number to rotate specific log")
        print(f"  Enter 'all' to rotate all logs")
        print(f"  Enter 'q' to quit")
        
        choice = input(f"\nYour choice: ").strip().lower()
        
        if choice == 'q':
            print(f"\nCancelled.")
            return 0
        
        if choice == 'all':
            pass  # Rotate all logs
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(log_files):
                    log_files = [log_files[index]]
                else:
                    print(f"\n✗ Invalid choice")
                    return 1
            except ValueError:
                print(f"\n✗ Invalid choice")
                return 1
    
    # Rotate selected logs
    print(f"\n{'=' * 80}")
    print(f"Rotating {len(log_files)} log file(s)")
    print(f"{'=' * 80}")
    
    success_count = 0
    for log_file in log_files:
        if rotate_log_file(log_file, max_backups=args.max_backups, compress=not args.no_compress):
            success_count += 1
    
    print(f"\n{'=' * 80}")
    print(f"Rotation Complete")
    print(f"{'=' * 80}")
    print(f"\nRotated: {success_count}/{len(log_files)} log file(s)")
    
    if success_count == len(log_files):
        print(f"✓ All logs rotated successfully")
        return 0
    else:
        print(f"⚠ Some logs failed to rotate")
        return 1


if __name__ == '__main__':
    sys.exit(main())

