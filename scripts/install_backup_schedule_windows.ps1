# ============================================================================
# Laser OS Tier 1 - Install Backup Schedule on Windows
# ============================================================================
# This PowerShell script creates a Windows Task Scheduler task to run
# the backup script daily at 2:00 AM
# ============================================================================
# Usage: Run as Administrator
#   powershell -ExecutionPolicy Bypass -File scripts\install_backup_schedule_windows.ps1
# ============================================================================

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires Administrator privileges!"
    Write-Host "Please run PowerShell as Administrator and try again."
    exit 1
}

# Get the project root directory (parent of scripts directory)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Path to the batch script
$batchScriptPath = Join-Path $projectRoot "scripts\schedule_backup_windows.bat"

# Verify the batch script exists
if (-not (Test-Path $batchScriptPath)) {
    Write-Error "Batch script not found: $batchScriptPath"
    exit 1
}

# Task Scheduler configuration
$taskName = "LaserOS_DailyBackup"
$taskDescription = "Daily backup of Laser OS Tier 1 database at 2:00 AM"
$taskTime = "02:00"  # 2:00 AM

Write-Host "============================================================================"
Write-Host "Laser OS Tier 1 - Backup Schedule Installation"
Write-Host "============================================================================"
Write-Host ""
Write-Host "Project Root: $projectRoot"
Write-Host "Batch Script: $batchScriptPath"
Write-Host "Task Name: $taskName"
Write-Host "Schedule: Daily at $taskTime"
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$taskName' already exists."
    $response = Read-Host "Do you want to replace it? (Y/N)"
    if ($response -ne 'Y' -and $response -ne 'y') {
        Write-Host "Installation cancelled."
        exit 0
    }
    
    # Unregister existing task
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Existing task removed."
}

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute $batchScriptPath -WorkingDirectory $projectRoot

# Create the scheduled task trigger (daily at 2:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At $taskTime

# Create the scheduled task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -DontStopOnIdleEnd

# Create the scheduled task principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U

# Register the scheduled task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null
    
    Write-Host ""
    Write-Host "✓ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:"
    Write-Host "  Name: $taskName"
    Write-Host "  Schedule: Daily at $taskTime"
    Write-Host "  Script: $batchScriptPath"
    Write-Host "  User: $env:USERNAME"
    Write-Host ""
    Write-Host "You can view/modify this task in Task Scheduler:"
    Write-Host "  1. Press Win+R"
    Write-Host "  2. Type 'taskschd.msc' and press Enter"
    Write-Host "  3. Look for '$taskName' in the Task Scheduler Library"
    Write-Host ""
    Write-Host "To test the backup now, run:"
    Write-Host "  schtasks /Run /TN `"$taskName`""
    Write-Host ""
    
} catch {
    Write-Error "Failed to create scheduled task: $_"
    exit 1
}

# Verify the task was created
$verifyTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($verifyTask) {
    Write-Host "✓ Verification successful - Task is registered" -ForegroundColor Green
    
    # Show next run time
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "  Next Run Time: $($taskInfo.NextRunTime)"
} else {
    Write-Warning "Task was created but verification failed"
}

Write-Host ""
Write-Host "============================================================================"
Write-Host "Installation Complete!"
Write-Host "============================================================================"
Write-Host ""
