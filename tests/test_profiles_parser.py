"""
Profiles Parser Tests for Laser OS.

This module tests the ProfilesParser service for parsing folder and file names
from the profiles_import directory structure.

Phase 2 of Profiles Migration System.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from app.services.profiles_parser import ProfilesParser


class TestParseProjectFolder:
    """Test project folder name parsing."""
    
    def test_parse_valid_folder_basic(self):
        """Test parsing a basic valid folder name."""
        result = ProfilesParser.parse_project_folder("0001-Gas Cover box-10.15.2025")
        
        assert result is not None
        assert result['project_number'] == '0001'
        assert result['description'] == 'Gas Cover box'
        assert result['date_str'] == '10.15.2025'
        assert result['date_created'] is not None
        assert result['date_created'].year == 2025
        assert result['date_created'].month == 10
        assert result['date_created'].day == 15
    
    def test_parse_valid_folder_complex_description(self):
        """Test parsing folder with complex description."""
        result = ProfilesParser.parse_project_folder("0042-Gas Cover box 1 to 1 ratio-12.25.2025")
        
        assert result is not None
        assert result['project_number'] == '0042'
        assert result['description'] == 'Gas Cover box 1 to 1 ratio'
        assert result['date_created'].month == 12
        assert result['date_created'].day == 25
    
    def test_parse_valid_folder_different_date_format(self):
        """Test parsing folder with different date formats."""
        # Test DD-MM-YYYY format
        result = ProfilesParser.parse_project_folder("0001-Project Name-15-10-2025")
        assert result is not None
        assert result['date_created'] is not None
        
        # Test YYYY-MM-DD format
        result = ProfilesParser.parse_project_folder("0001-Project Name-2025-10-15")
        assert result is not None
        assert result['date_created'] is not None
    
    def test_parse_invalid_folder_missing_parts(self):
        """Test parsing invalid folder names."""
        # Missing date
        result = ProfilesParser.parse_project_folder("0001-Gas Cover box")
        assert result is None
        
        # Missing description
        result = ProfilesParser.parse_project_folder("0001-10.15.2025")
        assert result is None
        
        # Missing project number
        result = ProfilesParser.parse_project_folder("Gas Cover box-10.15.2025")
        assert result is None
    
    def test_parse_empty_folder_name(self):
        """Test parsing empty or None folder name."""
        result = ProfilesParser.parse_project_folder("")
        assert result is None
        
        result = ProfilesParser.parse_project_folder(None)
        assert result is None
    
    def test_parse_folder_with_special_characters(self):
        """Test parsing folder with special characters in description."""
        result = ProfilesParser.parse_project_folder("0001-Box & Cover (v2)-10.15.2025")
        assert result is not None
        assert result['description'] == 'Box & Cover (v2)'


class TestParseFileName:
    """Test file name parsing."""
    
    def test_parse_valid_file_basic(self):
        """Test parsing a basic valid file name."""
        result = ProfilesParser.parse_file_name("0001-Full Gas Box Version1-Galv-1mm-x1.dxf")
        
        assert result is not None
        assert result['project_number'] == '0001'
        assert result['part_description'] == 'Full Gas Box Version1'
        assert result['material_code'] == 'Galv'
        assert result['material_type'] == 'Galvanized Steel'
        assert result['thickness'] == Decimal('1.0')
        assert result['thickness_str'] == '1mm'
        assert result['quantity'] == 1
    
    def test_parse_valid_file_stainless_steel(self):
        """Test parsing file with stainless steel material."""
        result = ProfilesParser.parse_file_name("0042-Bracket-SS-2mm-x10.dxf")
        
        assert result is not None
        assert result['material_code'] == 'SS'
        assert result['material_type'] == 'Stainless Steel'
        assert result['thickness'] == Decimal('2.0')
        assert result['quantity'] == 10
    
    def test_parse_valid_file_mild_steel(self):
        """Test parsing file with mild steel material."""
        result = ProfilesParser.parse_file_name("0001-Part-MS-3mm-x5.lbrn2")
        
        assert result is not None
        assert result['material_code'] == 'MS'
        assert result['material_type'] == 'Mild Steel'
        assert result['thickness'] == Decimal('3.0')
        assert result['quantity'] == 5
    
    def test_parse_valid_file_decimal_thickness(self):
        """Test parsing file with decimal thickness."""
        result = ProfilesParser.parse_file_name("0001-Part-Galv-1.5mm-x2.dxf")
        
        assert result is not None
        assert result['thickness'] == Decimal('1.5')
    
    def test_parse_valid_file_aluminum(self):
        """Test parsing file with aluminum material."""
        result = ProfilesParser.parse_file_name("0001-Part-Al-2mm-x1.dxf")
        
        assert result is not None
        assert result['material_code'] == 'Al'
        assert result['material_type'] == 'Aluminum'
    
    def test_parse_invalid_file_missing_parts(self):
        """Test parsing invalid file names."""
        # Missing quantity
        result = ProfilesParser.parse_file_name("0001-Part-Galv-1mm.dxf")
        assert result is None
        
        # Missing thickness
        result = ProfilesParser.parse_file_name("0001-Part-Galv-x1.dxf")
        assert result is None
        
        # Wrong format
        result = ProfilesParser.parse_file_name("random_file.dxf")
        assert result is None
    
    def test_parse_empty_file_name(self):
        """Test parsing empty or None file name."""
        result = ProfilesParser.parse_file_name("")
        assert result is None
        
        result = ProfilesParser.parse_file_name(None)
        assert result is None


class TestMapMaterial:
    """Test material code mapping."""
    
    def test_map_galvanized(self):
        """Test mapping galvanized steel codes."""
        assert ProfilesParser.map_material("Galv") == "Galvanized Steel"
        assert ProfilesParser.map_material("galv") == "Galvanized Steel"
        assert ProfilesParser.map_material("GALV") == "Galvanized Steel"
        assert ProfilesParser.map_material("Galvanized") == "Galvanized Steel"
    
    def test_map_stainless_steel(self):
        """Test mapping stainless steel codes."""
        assert ProfilesParser.map_material("SS") == "Stainless Steel"
        assert ProfilesParser.map_material("ss") == "Stainless Steel"
        assert ProfilesParser.map_material("Stainless") == "Stainless Steel"
    
    def test_map_mild_steel(self):
        """Test mapping mild steel codes."""
        assert ProfilesParser.map_material("MS") == "Mild Steel"
        assert ProfilesParser.map_material("Mild") == "Mild Steel"
        assert ProfilesParser.map_material("Steel") == "Mild Steel"
    
    def test_map_aluminum(self):
        """Test mapping aluminum codes."""
        assert ProfilesParser.map_material("Al") == "Aluminum"
        assert ProfilesParser.map_material("Aluminum") == "Aluminum"
        assert ProfilesParser.map_material("Aluminium") == "Aluminum"
    
    def test_map_brass_copper(self):
        """Test mapping brass and copper."""
        assert ProfilesParser.map_material("Brass") == "Brass"
        assert ProfilesParser.map_material("Copper") == "Copper"
    
    def test_map_unknown(self):
        """Test mapping unknown material codes."""
        assert ProfilesParser.map_material("Unknown") == "Other"
        assert ProfilesParser.map_material("XYZ") == "Other"
        assert ProfilesParser.map_material("") == "Other"
        assert ProfilesParser.map_material(None) == "Other"


class TestParseThickness:
    """Test thickness parsing."""
    
    def test_parse_thickness_with_mm(self):
        """Test parsing thickness with 'mm' suffix."""
        assert ProfilesParser.parse_thickness("1mm") == Decimal('1.0')
        assert ProfilesParser.parse_thickness("2mm") == Decimal('2.0')
        assert ProfilesParser.parse_thickness("1.5mm") == Decimal('1.5')
        assert ProfilesParser.parse_thickness("0.5mm") == Decimal('0.5')
    
    def test_parse_thickness_with_m(self):
        """Test parsing thickness with 'm' suffix."""
        assert ProfilesParser.parse_thickness("1m") == Decimal('1.0')
        assert ProfilesParser.parse_thickness("2m") == Decimal('2.0')
    
    def test_parse_thickness_without_suffix(self):
        """Test parsing thickness without suffix."""
        assert ProfilesParser.parse_thickness("1") == Decimal('1.0')
        assert ProfilesParser.parse_thickness("2.5") == Decimal('2.5')
        assert ProfilesParser.parse_thickness("3") == Decimal('3.0')
    
    def test_parse_thickness_invalid(self):
        """Test parsing invalid thickness values."""
        assert ProfilesParser.parse_thickness("") is None
        assert ProfilesParser.parse_thickness(None) is None
        assert ProfilesParser.parse_thickness("abc") is None
        assert ProfilesParser.parse_thickness("-1mm") is None
        assert ProfilesParser.parse_thickness("0mm") is None


class TestParseQuantity:
    """Test quantity parsing."""
    
    def test_parse_quantity_valid(self):
        """Test parsing valid quantities."""
        assert ProfilesParser.parse_quantity("1") == 1
        assert ProfilesParser.parse_quantity("10") == 10
        assert ProfilesParser.parse_quantity("100") == 100
    
    def test_parse_quantity_invalid(self):
        """Test parsing invalid quantities."""
        assert ProfilesParser.parse_quantity("") is None
        assert ProfilesParser.parse_quantity(None) is None
        assert ProfilesParser.parse_quantity("abc") is None
        assert ProfilesParser.parse_quantity("-1") is None
        assert ProfilesParser.parse_quantity("0") is None
        assert ProfilesParser.parse_quantity("1.5") is None  # Should be integer


class TestParseDate:
    """Test date parsing."""
    
    def test_parse_date_mm_dd_yyyy_dot(self):
        """Test parsing MM.DD.YYYY format."""
        result = ProfilesParser.parse_date("10.15.2025")
        assert result is not None
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 15
    
    def test_parse_date_dd_mm_yyyy_dash(self):
        """Test parsing DD-MM-YYYY format."""
        result = ProfilesParser.parse_date("15-10-2025")
        assert result is not None
        assert result.year == 2025
        # Could be month 15 or day 15 - parser tries both
    
    def test_parse_date_yyyy_mm_dd(self):
        """Test parsing YYYY-MM-DD format."""
        result = ProfilesParser.parse_date("2025-10-15")
        assert result is not None
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 15
    
    def test_parse_date_mm_dd_yyyy_slash(self):
        """Test parsing MM/DD/YYYY format."""
        result = ProfilesParser.parse_date("10/15/2025")
        assert result is not None
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 15
    
    def test_parse_date_invalid(self):
        """Test parsing invalid dates."""
        assert ProfilesParser.parse_date("") is None
        assert ProfilesParser.parse_date(None) is None
        assert ProfilesParser.parse_date("invalid") is None
        assert ProfilesParser.parse_date("13/32/2025") is None  # Invalid date

