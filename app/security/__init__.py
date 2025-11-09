"""
Security package for Laser OS.

This package contains security-related utilities including:
- Role-based access control decorators
- Permission checking functions
"""

from .decorators import require_role, require_any_role

__all__ = ['require_role', 'require_any_role']

