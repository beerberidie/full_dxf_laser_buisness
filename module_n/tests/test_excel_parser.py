"""
Module N - Excel Parser Tests
Comprehensive tests for Excel parsing functionality
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from module_n.parsers import ExcelParser
from module_n.models.schemas import FileType, NormalizedMetadata


# Sample Excel files (test fixtures)
SAMPLE_EXCEL_1 = "module_n/tests/fixtures/test_quote.xlsx"
SAMPLE_EXCEL_2 = "module_n/tests/fixtures/test_cutting_list.xlsx"


class TestExcelParser:
    """Test suite for Excel parser"""
    
    def test_parser_initialization(self):
        """Test that parser can be initialized"""
        parser = ExcelParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'MATERIAL_PATTERNS')
        assert hasattr(parser, 'COLUMN_PATTERNS')
        assert parser.MAX_DATA_ROWS == 100
    
    def test_parse_sample_excel_quote(self):
        """Test parsing a sample quote Excel file"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_1, "test_quote.xlsx")
        
        assert metadata.detected_type == FileType.EXCEL
        assert metadata.extracted is not None
        assert 'sheet_names' in metadata.extracted
        assert 'row_count' in metadata.extracted
        assert metadata.extracted['row_count'] > 0
        assert metadata.confidence_score >= 0.2
    
    def test_parse_sample_excel_cutting_list(self):
        """Test parsing a sample cutting list Excel file"""
        if not Path(SAMPLE_EXCEL_2).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_2}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_2, "test_cutting_list.xlsx")
        
        assert metadata.detected_type == FileType.EXCEL
        assert metadata.extracted is not None
        assert metadata.confidence_score >= 0.2
    
    def test_parse_filename_old_format(self):
        """Test parsing old filename format"""
        parser = ExcelParser()
        filename_meta = parser._parse_filename("0001-Full Gas Box-Galv-1mm-x1.xlsx")
        
        assert filename_meta.part_name == "Full Gas Box"
        assert filename_meta.material == "Galvanized Steel"
        assert filename_meta.thickness_mm == 1.0
        assert filename_meta.quantity == 1
    
    def test_parse_filename_new_format(self):
        """Test parsing new filename format"""
        parser = ExcelParser()
        filename_meta = parser._parse_filename("CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.xlsx")
        
        assert filename_meta.client_code == "CL0001"
        assert filename_meta.project_code == "JB-2025-10-CL0001-001"
        assert filename_meta.part_name == "BracketLeft"
        assert filename_meta.material == "Mild Steel"
        assert filename_meta.thickness_mm == 5.0
        assert filename_meta.quantity == 14
        assert filename_meta.version == 1
    
    def test_material_detection_from_text(self):
        """Test material detection from text content"""
        parser = ExcelParser()
        
        # Test various material patterns
        assert parser._detect_material_from_text("Galvanized steel plate") == "Galvanized Steel"
        assert parser._detect_material_from_text("SS 304") == "Stainless Steel"
        assert parser._detect_material_from_text("Mild steel") == "Mild Steel"
        assert parser._detect_material_from_text("Aluminum plate") == "Aluminum"
        assert parser._detect_material_from_text("Brass fitting") == "Brass"
        assert parser._detect_material_from_text("Copper sheet") == "Copper"
    
    def test_thickness_detection_from_text(self):
        """Test thickness detection from text content"""
        parser = ExcelParser()
        
        # Test various thickness patterns
        assert parser._detect_thickness_from_text("Material: 3mm steel") == 3.0
        assert parser._detect_thickness_from_text("t=5mm") == 5.0
        assert parser._detect_thickness_from_text("thickness: 10") == 10.0
        assert parser._detect_thickness_from_text("6.5mm thick") == 6.5
        assert parser._detect_thickness_from_text("no thickness here") is None
    
    def test_quantity_detection_from_text(self):
        """Test quantity detection from text content"""
        parser = ExcelParser()
        
        # Test various quantity patterns
        assert parser._detect_quantity_from_text("Qty: 10") == 10
        assert parser._detect_quantity_from_text("Quantity: 25") == 25
        assert parser._detect_quantity_from_text("x 5 pieces") == 5
        assert parser._detect_quantity_from_text("100 pcs") == 100
        assert parser._detect_quantity_from_text("no quantity") is None
    
    def test_client_code_detection(self):
        """Test client code detection from text"""
        parser = ExcelParser()
        
        # Test various client code patterns
        assert parser._detect_client_code("Client: CL-0001") == "CL0001"
        assert parser._detect_client_code("CL 0002 Project") == "CL0002"
        assert parser._detect_client_code("CL0003") == "CL0003"
        assert parser._detect_client_code("no client code") is None
    
    def test_project_code_detection(self):
        """Test project code detection from text"""
        parser = ExcelParser()
        
        # Test various project code patterns
        result = parser._detect_project_code("Project: JB-2025-10-CL0001-001")
        assert result is not None
        assert "JB" in result
        
        result = parser._detect_project_code("PO 2024 12 CL0002 005")
        assert result is not None
        assert "PO" in result
    
    def test_schema_detection_quote(self):
        """Test schema detection for quote structure"""
        parser = ExcelParser()
        
        headers = ['Part Name', 'Material', 'Thickness', 'Quantity', 'Price', 'Total']
        data_rows = []
        
        schema_info = parser._detect_schema(headers, data_rows)
        assert schema_info['schema_type'] == 'quote'
        assert 'part_name' in schema_info['column_mapping']
        assert 'material' in schema_info['column_mapping']
        assert 'price' in schema_info['column_mapping']
    
    def test_schema_detection_cutting_list(self):
        """Test schema detection for cutting list structure"""
        parser = ExcelParser()
        
        headers = ['Part', 'Material', 'Thickness', 'Qty']
        data_rows = []
        
        schema_info = parser._detect_schema(headers, data_rows)
        assert schema_info['schema_type'] == 'cutting_list'
        assert 'part_name' in schema_info['column_mapping']
        assert 'material' in schema_info['column_mapping']
    
    def test_schema_detection_parts_list(self):
        """Test schema detection for parts list structure"""
        parser = ExcelParser()
        
        headers = ['Part Name', 'Description', 'Quantity']
        data_rows = []
        
        schema_info = parser._detect_schema(headers, data_rows)
        assert schema_info['schema_type'] == 'parts_list'
        assert 'part_name' in schema_info['column_mapping']
        assert 'quantity' in schema_info['column_mapping']
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = ExcelParser()
        
        # Minimal metadata
        meta1 = NormalizedMetadata(
            source_file="test.xlsx",
            detected_type=FileType.EXCEL,
            extracted={'sheet_count': 1}
        )
        score1 = parser._calculate_confidence(meta1)
        assert 0.2 <= score1 <= 0.3
        
        # Complete metadata
        meta2 = NormalizedMetadata(
            source_file="test.xlsx",
            detected_type=FileType.EXCEL,
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            part_name="Bracket",
            material="Mild Steel",
            thickness_mm=5.0,
            quantity=10,
            extracted={'sheet_count': 1, 'detected_schema': 'quote'}
        )
        score2 = parser._calculate_confidence(meta2)
        assert score2 >= 0.9
    
    def test_invalid_excel_file(self):
        """Test handling of invalid Excel file"""
        parser = ExcelParser()
        
        # Create a temporary invalid Excel file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            f.write("This is not a valid Excel file")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Failed to parse Excel"):
                parser.parse(temp_path, "invalid.xlsx")
        finally:
            Path(temp_path).unlink()
    
    def test_sheet_name_extraction(self):
        """Test sheet name extraction"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_1, "test.xlsx")
        
        assert 'sheet_names' in metadata.extracted
        sheet_names = metadata.extracted['sheet_names']
        assert isinstance(sheet_names, list)
        assert len(sheet_names) > 0
    
    def test_data_extraction(self):
        """Test data extraction from cells"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_1, "test.xlsx")
        
        assert 'data_rows' in metadata.extracted
        data_rows = metadata.extracted['data_rows']
        assert isinstance(data_rows, list)
        assert len(data_rows) > 0
    
    def test_header_detection(self):
        """Test header row detection"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_1, "test.xlsx")
        
        assert 'headers' in metadata.extracted
        headers = metadata.extracted['headers']
        assert isinstance(headers, list)
        assert len(headers) > 0
    
    def test_row_and_column_counts(self):
        """Test row and column counting"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_1, "test.xlsx")
        
        assert 'row_count' in metadata.extracted
        assert 'column_count' in metadata.extracted
        assert metadata.extracted['row_count'] > 0
        assert metadata.extracted['column_count'] > 0
    
    def test_file_size_and_mime_type(self):
        """Test file size and MIME type are set"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(SAMPLE_EXCEL_1, "test.xlsx")
        
        assert metadata.file_size is not None
        assert metadata.file_size > 0
        assert metadata.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    def test_mime_type_xls(self):
        """Test MIME type for .xls files"""
        parser = ExcelParser()
        mime_type = parser._get_mime_type("test.xls")
        assert mime_type == 'application/vnd.ms-excel'
    
    def test_normalize_material(self):
        """Test material normalization"""
        parser = ExcelParser()
        
        # Test material code normalization
        assert parser._normalize_material("MS") == "Mild Steel"
        assert parser._normalize_material("SS") == "Stainless Steel"
        assert parser._normalize_material("GALV") == "Galvanized Steel"
        
        # Test material name normalization
        assert parser._normalize_material("Mild Steel") == "Mild Steel"
        assert parser._normalize_material("stainless") == "Stainless Steel"
    
    def test_extract_number(self):
        """Test number extraction from strings"""
        parser = ExcelParser()
        
        assert parser._extract_number("3mm") == 3.0
        assert parser._extract_number("5.5") == 5.5
        assert parser._extract_number("10 pcs") == 10.0
        assert parser._extract_number("abc") is None
    
    def test_client_and_project_override(self):
        """Test that provided client/project codes override detection"""
        if not Path(SAMPLE_EXCEL_1).exists():
            pytest.skip(f"Sample Excel file not found: {SAMPLE_EXCEL_1}")
        
        parser = ExcelParser()
        metadata = parser.parse(
            SAMPLE_EXCEL_1,
            "test.xlsx",
            client_code="CL9999",
            project_code="TEST-2025-01-CL9999-999"
        )
        
        assert metadata.client_code == "CL9999"
        assert metadata.project_code == "TEST-2025-01-CL9999-999"
    
    def test_empty_sheet_handling(self):
        """Test handling of empty sheets"""
        # Create a temporary Excel file with empty sheet
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            df = pd.DataFrame()
            df.to_excel(temp_path, index=False)
            
            parser = ExcelParser()
            metadata = parser.parse(temp_path, "empty.xlsx")
            
            assert metadata.detected_type == FileType.EXCEL
            assert metadata.extracted['row_count'] == 0
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

