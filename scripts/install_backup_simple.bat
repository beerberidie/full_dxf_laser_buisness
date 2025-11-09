@echo off
REM ============================================================================
REM Laser OS Tier 1 - Install Backup Schedule (Simple Version)
REM ============================================================================
REM This batch script creates a Windows Task Scheduler task using schtasks
REM ============================================================================

echo ============================================================================
echo Laser OS Tier 1 - Backup Schedule Installation
echo ============================================================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set BATCH_SCRIPT=%SCRIPT_DIR%schedule_backup_windows.bat

echo Project Root: %PROJECT_ROOT%
echo Batch Script: %BATCH_SCRIPT%
echo Task Name: LaserOS_DailyBackup
echo Schedule: Daily at 2:00 AM
echo.

REM Check if task already exists
schtasks /Query /TN "LaserOS_DailyBackup" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Task 'LaserOS_DailyBackup' already exists.
    set /p REPLACE="Do you want to replace it? (Y/N): "
    if /i not "%REPLACE%"=="Y" (
        echo Installation cancelled.
        exit /b 0
    )
    
    REM Delete existing task
    schtasks /Delete /TN "LaserOS_DailyBackup" /F >nul 2>&1
    echo Existing task removed.
    echo.
)

REM Create the scheduled task
echo Creating scheduled task...
schtasks /Create /TN "LaserOS_DailyBackup" /TR "\"%BATCH_SCRIPT%\"" /SC DAILY /ST 02:00 /RU "%USERNAME%" /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================================
    echo SUCCESS! Scheduled task created successfully!
    echo ============================================================================
    echo.
    echo Task Details:
    echo   Name: LaserOS_DailyBackup
    echo   Schedule: Daily at 2:00 AM
    echo   Script: %BATCH_SCRIPT%
    echo   User: %USERNAME%
    echo.
    echo You can view/modify this task in Task Scheduler:
    echo   1. Press Win+R
    echo   2. Type 'taskschd.msc' and press Enter
    echo   3. Look for 'LaserOS_DailyBackup' in the Task Scheduler Library
    echo.
    echo To test the backup now, run:
    echo   schtasks /Run /TN "LaserOS_DailyBackup"
    echo.
    echo ============================================================================
) else (
    echo.
    echo ERROR: Failed to create scheduled task!
    echo Please make sure you are running this script as Administrator.
    echo.
    exit /b 1
)

pause

