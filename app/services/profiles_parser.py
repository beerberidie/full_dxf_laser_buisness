"""
Profiles Parser Service for Laser OS.

This service handles parsing of folder and file names from the profiles_import
directory structure to extract project metadata for migration.

Phase 2 of Profiles Migration System.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal


class ProfilesParser:
    """
    Parser for extracting metadata from profiles_import folder and file names.
    
    This class provides static methods to parse project folder names and file names
    to extract structured metadata including project numbers, descriptions, dates,
    material types, thicknesses, and quantities.
    
    Example folder structure:
        profiles_import/CL-0001/1.Projects/0001-Gas Cover box-10.15.2025/
            0001-Full Gas Box Version1-Galv-1mm-x1.dxf
    
    Attributes:
        MATERIAL_MAP: Dictionary mapping material codes to full material names
        PROJECT_FOLDER_PATTERN: Regex pattern for project folder names
        FILE_NAME_PATTERN: Regex pattern for project file names
    """
    
    # Material code mapping - maps short codes to full material names
    MATERIAL_MAP = {
        'Galv': 'Galvanized Steel',
        'Galvanized': 'Galvanized Steel',
        'SS': 'Stainless Steel',
        'Stainless': 'Stainless Steel',
        'MS': 'Mild Steel',
        'Mild': 'Mild Steel',
        'Steel': 'Mild Steel',
        'Al': 'Aluminum',
        'Aluminum': 'Aluminum',
        'Aluminium': 'Aluminum',
        'Brass': 'Brass',
        'Copper': 'Copper',
        'Other': 'Other',
    }
    
    # Regex pattern for project folder names
    # Format: {project_number}-{description}-{date}
    # Example: 0001-Gas Cover box 1 to 1 ratio-10.15.2025
    PROJECT_FOLDER_PATTERN = re.compile(
        r'^(\d{4})-(.+?)-(\d{1,2}[\./-]\d{1,2}[\./-]\d{4})$'
    )
    
    # Regex pattern for file names with material info
    # Format: {project_number}-{part_description}-{material}-{thickness}-{quantity}.{ext}
    # Example: 0001-Full Gas Box Version1-Galv-1mm-x1.dxf
    FILE_NAME_PATTERN = re.compile(
        r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*m?m?)-x(\d+)\.'
    )
    
    @staticmethod
    def parse_project_folder(folder_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse a project folder name to extract metadata.
        
        Args:
            folder_name: Name of the project folder
                        Format: {project_number}-{description}-{date}
                        Example: "0001-Gas Cover box-10.15.2025"
        
        Returns:
            Dictionary containing:
                - project_number (str): 4-digit project number
                - description (str): Project description
                - date_created (datetime.date): Parsed creation date
                - date_str (str): Original date string
            Returns None if parsing fails
        
        Example:
            >>> result = ProfilesParser.parse_project_folder("0001-Gas Cover box-10.15.2025")
            >>> result['project_number']
            '0001'
            >>> result['description']
            'Gas Cover box'
        """
        if not folder_name:
            return None
        
        match = ProfilesParser.PROJECT_FOLDER_PATTERN.match(folder_name)
        if not match:
            return None
        
        project_number = match.group(1)
        description = match.group(2).strip()
        date_str = match.group(3)
        
        # Parse the date
        date_created = ProfilesParser.parse_date(date_str)
        
        return {
            'project_number': project_number,
            'description': description,
            'date_created': date_created,
            'date_str': date_str,
        }
    
    @staticmethod
    def parse_file_name(file_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse a file name to extract part metadata.
        
        Args:
            file_name: Name of the file
                      Format: {project_number}-{part_description}-{material}-{thickness}-{quantity}.{ext}
                      Example: "0001-Full Gas Box Version1-Galv-1mm-x1.dxf"
        
        Returns:
            Dictionary containing:
                - project_number (str): 4-digit project number
                - part_description (str): Part description
                - material_code (str): Raw material code from filename
                - material_type (str): Full material name (mapped)
                - thickness (Decimal): Material thickness in mm
                - thickness_str (str): Original thickness string
                - quantity (int): Parts quantity
            Returns None if parsing fails
        
        Example:
            >>> result = ProfilesParser.parse_file_name("0001-Gas Box-Galv-1mm-x1.dxf")
            >>> result['material_type']
            'Galvanized Steel'
            >>> result['thickness']
            Decimal('1.0')
        """
        if not file_name:
            return None
        
        match = ProfilesParser.FILE_NAME_PATTERN.match(file_name)
        if not match:
            return None
        
        project_number = match.group(1)
        part_description = match.group(2).strip()
        material_code = match.group(3)
        thickness_str = match.group(4)
        quantity_str = match.group(5)
        
        # Map material code to full name
        material_type = ProfilesParser.map_material(material_code)
        
        # Parse thickness
        thickness = ProfilesParser.parse_thickness(thickness_str)
        
        # Parse quantity
        quantity = ProfilesParser.parse_quantity(quantity_str)
        
        return {
            'project_number': project_number,
            'part_description': part_description,
            'material_code': material_code,
            'material_type': material_type,
            'thickness': thickness,
            'thickness_str': thickness_str,
            'quantity': quantity,
        }
    
    @staticmethod
    def map_material(material_code: str) -> str:
        """
        Map a material code to its full material name.
        
        Args:
            material_code: Short material code (e.g., "Galv", "SS", "MS")
        
        Returns:
            Full material name (e.g., "Galvanized Steel")
            Returns "Other" if code not found
        
        Example:
            >>> ProfilesParser.map_material("Galv")
            'Galvanized Steel'
            >>> ProfilesParser.map_material("SS")
            'Stainless Steel'
            >>> ProfilesParser.map_material("Unknown")
            'Other'
        """
        if not material_code:
            return 'Other'
        
        # Try exact match first (case-insensitive)
        for code, full_name in ProfilesParser.MATERIAL_MAP.items():
            if material_code.lower() == code.lower():
                return full_name
        
        # Try partial match
        for code, full_name in ProfilesParser.MATERIAL_MAP.items():
            if material_code.lower() in code.lower() or code.lower() in material_code.lower():
                return full_name
        
        # Default to Other if no match found
        return 'Other'
    
    @staticmethod
    def parse_thickness(thickness_str: str) -> Optional[Decimal]:
        """
        Parse thickness string to extract numeric value in mm.

        Args:
            thickness_str: Thickness string (e.g., "1mm", "1.5mm", "2", "0.5m")

        Returns:
            Decimal value representing thickness in mm
            Returns None if parsing fails

        Example:
            >>> ProfilesParser.parse_thickness("1mm")
            Decimal('1.0')
            >>> ProfilesParser.parse_thickness("1.5")
            Decimal('1.5')
            >>> ProfilesParser.parse_thickness("2m")
            Decimal('2.0')
        """
        if not thickness_str:
            return None

        try:
            # Remove 'mm' or 'm' suffix and any whitespace
            cleaned = thickness_str.lower().replace('mm', '').replace('m', '').strip()

            # Check if cleaned string is empty after removing suffixes
            if not cleaned:
                return None

            # Convert to Decimal
            thickness = Decimal(cleaned)

            # Ensure positive value
            if thickness <= 0:
                return None

            return thickness

        except (ValueError, TypeError, Exception):
            return None
    
    @staticmethod
    def parse_quantity(quantity_str: str) -> Optional[int]:
        """
        Parse quantity string to extract numeric value.
        
        Args:
            quantity_str: Quantity string (e.g., "1", "10", "25")
        
        Returns:
            Integer quantity value
            Returns None if parsing fails
        
        Example:
            >>> ProfilesParser.parse_quantity("1")
            1
            >>> ProfilesParser.parse_quantity("10")
            10
        """
        if not quantity_str:
            return None
        
        try:
            quantity = int(quantity_str)
            
            # Ensure positive value
            if quantity <= 0:
                return None
            
            return quantity
        
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse date string in multiple formats to datetime object.
        
        Supported formats:
            - MM.DD.YYYY (e.g., "10.15.2025")
            - DD-MM-YYYY (e.g., "15-10-2025")
            - YYYY-MM-DD (e.g., "2025-10-15")
            - MM/DD/YYYY (e.g., "10/15/2025")
            - DD/MM/YYYY (e.g., "15/10/2025")
        
        Args:
            date_str: Date string in various formats
        
        Returns:
            datetime object if parsing succeeds
            Returns None if all formats fail
        
        Example:
            >>> ProfilesParser.parse_date("10.15.2025")
            datetime.datetime(2025, 10, 15, 0, 0)
            >>> ProfilesParser.parse_date("15-10-2025")
            datetime.datetime(2025, 10, 15, 0, 0)
        """
        if not date_str:
            return None
        
        # List of date formats to try
        date_formats = [
            '%m.%d.%Y',   # MM.DD.YYYY
            '%d.%m.%Y',   # DD.MM.YYYY
            '%m/%d/%Y',   # MM/DD/YYYY
            '%d/%m/%Y',   # DD/MM/YYYY
            '%m-%d-%Y',   # MM-DD-YYYY
            '%d-%m-%Y',   # DD-MM-YYYY
            '%Y-%m-%d',   # YYYY-MM-DD
            '%Y/%m/%d',   # YYYY/MM/DD
            '%Y.%m.%d',   # YYYY.MM.DD
        ]
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date
            except ValueError:
                continue
        
        # If all formats fail, return None
        return None

