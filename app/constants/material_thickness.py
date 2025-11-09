"""
Material Thickness Constants for Laser OS.

This module defines the authoritative list of material thickness options
used throughout the application for:
- Inventory management (sheet tracking)
- Project material requirements
- Laser run logging
- Preset matching
- Form dropdowns

All thickness values are in millimeters (mm) as strings to preserve precision.
"""

# Authoritative thickness options in millimeters
# These values are used across all modules for consistency
THICKNESS_OPTIONS_MM = [
    "0.47",
    "0.53",
    "1.0",
    "1.2",
    "2.0",
    "2.5",
    "3.0",
    "3.5",
    "4.0",
    "5.0",
    "6.0",
    "8.0",
    "10.0",
    "12.0",
    "16.0"
]

# Common sheet sizes (width x height in mm)
# Used for inventory tracking and project requirements
SHEET_SIZES = [
    "3000x1500",
    "2500x1250",
    "2000x1000",
    "1500x1000",
    "1200x1000",
    "Custom"
]

# Material types commonly used
MATERIAL_TYPES = [
    "Mild Steel",
    "Stainless Steel",
    "Aluminum",
    "Galvanized Steel",
    "Copper",
    "Brass",
    "Other"
]

