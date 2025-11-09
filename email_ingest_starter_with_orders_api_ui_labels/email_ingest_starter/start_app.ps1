# Email Ingest Application Startup Script (PowerShell)
# This script starts both the backend and frontend servers

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "       Email Ingest Application Starter                    " -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

if (-not (Test-Path $BackendDir)) {
    Write-Host "ERROR: Backend directory not found: $BackendDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $FrontendDir)) {
    Write-Host "ERROR: Frontend directory not found: $FrontendDir" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Prerequisites checked" -ForegroundColor Green
Write-Host ""

# Start backend
Write-Host "Starting backend server..." -ForegroundColor Cyan
$BackendJob = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload" -WorkingDirectory $BackendDir -PassThru -WindowStyle Normal

if ($BackendJob) {
    Write-Host "✓ Backend server started (PID: $($BackendJob.Id))" -ForegroundColor Green
    Write-Host "  Backend URL: http://localhost:8000" -ForegroundColor Cyan
} else {
    Write-Host "ERROR: Failed to start backend" -ForegroundColor Red
    exit 1
}

# Wait for backend to initialize
Write-Host ""
Write-Host "Waiting for backend to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend server..." -ForegroundColor Cyan
$FrontendJob = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $FrontendDir -PassThru -WindowStyle Normal

if ($FrontendJob) {
    Write-Host "✓ Frontend server started (PID: $($FrontendJob.Id))" -ForegroundColor Green
    Write-Host "  Frontend URL: http://localhost:5173" -ForegroundColor Cyan
} else {
    Write-Host "ERROR: Failed to start frontend" -ForegroundColor Red
    Write-Host "Stopping backend..." -ForegroundColor Yellow
    Stop-Process -Id $BackendJob.Id -Force
    exit 1
}

# Wait for frontend to be ready
Write-Host ""
Write-Host "Waiting for frontend to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Open browser
Write-Host "Opening browser..." -ForegroundColor Cyan
try {
    Start-Process "http://localhost:5173"
    Write-Host "✓ Browser opened" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not open browser automatically" -ForegroundColor Yellow
    Write-Host "  Please open http://localhost:5173 manually" -ForegroundColor Cyan
}

# Print status
Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "              Application Running                          " -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "✓ Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "✓ Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor Cyan
Write-Host "Close those windows or press Ctrl+C in them to stop the servers." -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop both servers and exit..." -ForegroundColor Yellow
Write-Host ""

# Wait for user input
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host ""
Write-Host "Shutting down servers..." -ForegroundColor Cyan

if ($BackendJob -and -not $BackendJob.HasExited) {
    Write-Host "Stopping backend server..." -ForegroundColor Cyan
    Stop-Process -Id $BackendJob.Id -Force
    Write-Host "✓ Backend server stopped" -ForegroundColor Green
}

if ($FrontendJob -and -not $FrontendJob.HasExited) {
    Write-Host "Stopping frontend server..." -ForegroundColor Cyan
    Stop-Process -Id $FrontendJob.Id -Force
    Write-Host "✓ Frontend server stopped" -ForegroundColor Green
}

Write-Host ""
Write-Host "✓ Application stopped" -ForegroundColor Green
Write-Host ""

