#!/usr/bin/env python3
"""
Email Ingest Application Startup Script

This script starts both the backend (FastAPI) and frontend (Vite) servers
for the email ingestion application.

Usage:
    python start_app.py

The script will:
1. Start the backend server on http://localhost:8000
2. Start the frontend server on http://localhost:5173
3. Open the frontend in your default browser
4. Monitor both processes and handle graceful shutdown

Press Ctrl+C to stop both servers.
"""

import subprocess
import sys
import time
import os
import signal
import webbrowser
from pathlib import Path

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def get_script_dir():
    """Get the directory where this script is located"""
    return Path(__file__).parent.absolute()

def check_prerequisites():
    """Check if required files and directories exist"""
    script_dir = get_script_dir()
    backend_dir = script_dir / "backend"
    frontend_dir = script_dir / "frontend"
    
    print_info("Checking prerequisites...")
    
    if not backend_dir.exists():
        print_error(f"Backend directory not found: {backend_dir}")
        return False
    
    if not frontend_dir.exists():
        print_error(f"Frontend directory not found: {frontend_dir}")
        return False
    
    if not (backend_dir / "app" / "main.py").exists():
        print_error("Backend main.py not found")
        return False
    
    if not (frontend_dir / "package.json").exists():
        print_error("Frontend package.json not found")
        return False
    
    print_success("All prerequisites checked")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    script_dir = get_script_dir()
    backend_dir = script_dir / "backend"
    
    print_info("Starting backend server...")
    
    # Use python -m uvicorn to ensure correct Python version
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        print_success(f"Backend server started (PID: {process.pid})")
        print_info("Backend URL: http://localhost:8000")
        return process
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Vite frontend server"""
    script_dir = get_script_dir()
    frontend_dir = script_dir / "frontend"
    
    print_info("Starting frontend server...")
    
    # Use npm run dev
    cmd = ["npm", "run", "dev"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        print_success(f"Frontend server started (PID: {process.pid})")
        print_info("Frontend URL: http://localhost:5173")
        return process
    except Exception as e:
        print_error(f"Failed to start frontend: {e}")
        return None

def wait_for_server(url, timeout=30):
    """Wait for a server to be ready"""
    import urllib.request
    import urllib.error
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            time.sleep(0.5)
    return False

def monitor_process(process, name):
    """Monitor a process and print its output"""
    try:
        for line in process.stdout:
            print(f"{Colors.OKCYAN}[{name}]{Colors.ENDC} {line.rstrip()}")
    except Exception:
        pass

def cleanup_processes(backend_process, frontend_process):
    """Gracefully terminate both processes"""
    print_info("\nShutting down servers...")
    
    processes = []
    if backend_process:
        processes.append(("Backend", backend_process))
    if frontend_process:
        processes.append(("Frontend", frontend_process))
    
    for name, process in processes:
        if process and process.poll() is None:
            print_info(f"Stopping {name} server...")
            try:
                if sys.platform == "win32":
                    # On Windows, send CTRL_BREAK_EVENT
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    process.terminate()
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    process.wait(timeout=5)
                    print_success(f"{name} server stopped")
                except subprocess.TimeoutExpired:
                    print_warning(f"{name} server didn't stop gracefully, forcing...")
                    process.kill()
                    process.wait()
                    print_success(f"{name} server killed")
            except Exception as e:
                print_error(f"Error stopping {name}: {e}")

def main():
    """Main function to start the application"""
    print_header("Email Ingest Application Starter")
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Exiting.")
        sys.exit(1)
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print_error("Failed to start backend. Exiting.")
            sys.exit(1)
        
        # Wait a bit for backend to initialize
        print_info("Waiting for backend to initialize...")
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print_error("Failed to start frontend. Cleaning up...")
            cleanup_processes(backend_process, None)
            sys.exit(1)
        
        # Wait for frontend to be ready
        print_info("Waiting for frontend to be ready...")
        time.sleep(3)
        
        if wait_for_server("http://localhost:5173", timeout=15):
            print_success("Frontend is ready!")
            
            # Open browser
            print_info("Opening browser...")
            try:
                webbrowser.open("http://localhost:5173")
                print_success("Browser opened")
            except Exception as e:
                print_warning(f"Could not open browser automatically: {e}")
                print_info("Please open http://localhost:5173 manually")
        else:
            print_warning("Frontend may not be ready yet, but continuing...")
        
        # Print status
        print_header("Application Running")
        print_success("Backend:  http://localhost:8000")
        print_success("Frontend: http://localhost:5173")
        print_info("\nPress Ctrl+C to stop both servers\n")
        
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print_error("Backend process has stopped unexpectedly!")
                break
            
            if frontend_process.poll() is not None:
                print_error("Frontend process has stopped unexpectedly!")
                break
    
    except KeyboardInterrupt:
        print_info("\nReceived shutdown signal (Ctrl+C)")
    
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    finally:
        cleanup_processes(backend_process, frontend_process)
        print_success("\nApplication stopped")

if __name__ == "__main__":
    main()

