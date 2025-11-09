#!/bin/bash
# ============================================================================
# Laser OS Tier 1 - Daily Backup Script for Linux/Mac Cron
# ============================================================================
# This script is designed to be run by cron
# It activates the virtual environment and runs the backup script
# ============================================================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Change to project root directory
cd "$PROJECT_ROOT"

# Activate virtual environment
source venv/bin/activate

# Run the backup script (keeps last 30 backups by default)
python scripts/backup_database.py --keep 30

# Log the completion
echo "[$(date)] Backup completed" >> logs/backup_scheduler.log

# Deactivate virtual environment
deactivate

