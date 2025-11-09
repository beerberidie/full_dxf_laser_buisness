@echo off
REM ============================================================================
REM Laser OS Tier 1 - Daily Backup Script for Windows Task Scheduler
REM ============================================================================
REM This script is designed to be run by Windows Task Scheduler
REM It activates the virtual environment and runs the backup script
REM ============================================================================

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the backup script (keeps last 30 backups by default)
python scripts\backup_database.py --keep 30

REM Log the completion
echo [%date% %time%] Backup completed >> logs\backup_scheduler.log

REM Deactivate virtual environment
deactivate

