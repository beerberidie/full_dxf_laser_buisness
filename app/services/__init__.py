"""
Laser OS Tier 1 - Services Package

This package contains business logic services that are used across the application.
"""

from app.services.id_generator import generate_client_code, generate_project_code
from app.services.activity_logger import log_activity

__all__ = [
    'generate_client_code',
    'generate_project_code',
    'log_activity'
]

