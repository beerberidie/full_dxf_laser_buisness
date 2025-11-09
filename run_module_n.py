"""
Module N - Quick Start Script
Runs the Module N FastAPI service
"""

import sys
import os
from pathlib import Path

# Add module_n to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    from module_n.config import settings
    
    print("=" * 60)
    print("Module N - File Ingest & Extract System")
    print("=" * 60)
    print(f"Starting service on {settings.MODULE_N_HOST}:{settings.MODULE_N_PORT}")
    print(f"Upload folder: {settings.UPLOAD_FOLDER}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Webhook URL: {settings.LASER_OS_WEBHOOK_URL}")
    print("=" * 60)
    print(f"API Documentation: http://localhost:{settings.MODULE_N_PORT}/docs")
    print(f"Health Check: http://localhost:{settings.MODULE_N_PORT}/health")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        "module_n.main:app",
        host=settings.MODULE_N_HOST,
        port=settings.MODULE_N_PORT,
        reload=settings.MODULE_N_RELOAD,
        workers=1 if settings.MODULE_N_RELOAD else settings.MODULE_N_WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )

