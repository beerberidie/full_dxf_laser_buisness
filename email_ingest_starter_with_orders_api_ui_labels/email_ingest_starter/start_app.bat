@echo off
REM Email Ingest Application Startup Script (Batch)
REM This script starts both the backend and frontend servers

echo.
echo ============================================================
echo        Email Ingest Application Starter
echo ============================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

REM Check prerequisites
echo Checking prerequisites...

if not exist "%BACKEND_DIR%" (
    echo ERROR: Backend directory not found: %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory not found: %FRONTEND_DIR%
    pause
    exit /b 1
)

echo [OK] Prerequisites checked
echo.

REM Start backend in a new window
echo Starting backend server...
start "Email Ingest - Backend" /D "%BACKEND_DIR%" cmd /k "python -m uvicorn app.main:app --reload"
echo [OK] Backend server started
echo      Backend URL: http://localhost:8000
echo.

REM Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo Starting frontend server...
start "Email Ingest - Frontend" /D "%FRONTEND_DIR%" cmd /k "npm run dev"
echo [OK] Frontend server started
echo      Frontend URL: http://localhost:5173
echo.

REM Wait for frontend to be ready
echo Waiting for frontend to be ready...
timeout /t 5 /nobreak >nul

REM Open browser
echo Opening browser...
start http://localhost:5173
echo [OK] Browser opened
echo.

REM Print status
echo ============================================================
echo               Application Running
echo ============================================================
echo.
echo [OK] Backend:  http://localhost:8000
echo [OK] Frontend: http://localhost:5173
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul

