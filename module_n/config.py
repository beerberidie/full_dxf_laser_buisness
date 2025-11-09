"""
Module N - Configuration
Loads configuration from environment variables
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Module N Settings"""
    
    # Service Configuration
    MODULE_N_PORT: int = 8081
    MODULE_N_HOST: str = "0.0.0.0"
    MODULE_N_WORKERS: int = 4
    MODULE_N_RELOAD: bool = False
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///data/laser_os.db"
    
    # File Storage Configuration
    UPLOAD_FOLDER: str = "data/files"
    MAX_UPLOAD_SIZE: int = 52428800  # 50 MB
    AUTO_VERSION: bool = True  # Automatically increment version on filename collision

    # Allowed File Extensions
    ALLOWED_DXF_EXTENSIONS: list = ['.dxf']
    ALLOWED_PDF_EXTENSIONS: list = ['.pdf']
    ALLOWED_EXCEL_EXTENSIONS: list = ['.xlsx', '.xls']
    ALLOWED_LBRN_EXTENSIONS: list = ['.lbrn2', '.lbrn']
    ALLOWED_IMAGE_EXTENSIONS: list = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif']
    
    # Laser OS Integration
    LASER_OS_WEBHOOK_URL: str = "http://localhost:8080/webhooks/module-n/event"
    LASER_OS_TIMEOUT: int = 30
    WEBHOOK_ENABLED: bool = True  # Enable/disable webhook notifications
    WEBHOOK_RETRY_ATTEMPTS: int = 3  # Number of retry attempts for failed webhooks
    WEBHOOK_RETRY_DELAY: int = 5  # Delay in seconds between retry attempts (exponential backoff)
    WEBHOOK_SECRET: str = ""  # Secret key for webhook signature (HMAC-SHA256)
    WEBHOOK_ENABLED_EVENTS: list = []  # List of enabled event types (empty = all events)
    
    # OCR Settings
    TESSERACT_LANGUAGES: str = "eng+afr"
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"
    
    # Processing Settings
    CONFIDENCE_THRESHOLD: float = 0.70
    AUTO_PROCESS: bool = True
    
    # Google APIs (Phase 2)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/module_n.log"
    
    class Config:
        env_file = ".env.module_n"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_upload_folder() -> Path:
    """Get upload folder as Path object"""
    return Path(settings.UPLOAD_FOLDER)


def get_database_url() -> str:
    """Get database URL"""
    return settings.DATABASE_URL


def get_laser_os_webhook_url() -> str:
    """Get Laser OS webhook URL"""
    return settings.LASER_OS_WEBHOOK_URL

