"""
Module N - LightBurn Parser Tests
Comprehensive tests for LightBurn parsing functionality
"""

import pytest
import tempfile
from pathlib import Path
from module_n.parsers import LBRNParser
from module_n.models.schemas import FileType, NormalizedMetadata


# Sample LightBurn file (test fixture)
SAMPLE_LBRN = "module_n/tests/fixtures/test_lightburn.lbrn2"


class TestLBRNParser:
    """Test suite for LightBurn parser"""
    
    def test_parser_initialization(self):
        """Test that parser can be initialized"""
        parser = LBRNParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'MATERIAL_PATTERNS')
        assert hasattr(parser, 'THICKNESS_PATTERN')
    
    def test_parse_sample_lbrn(self):
        """Test parsing a sample LightBurn file"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test_lightburn.lbrn2")
        
        assert metadata.detected_type == FileType.LBRN2
        assert metadata.extracted is not None
        assert 'app_version' in metadata.extracted
        assert 'device_name' in metadata.extracted
        assert metadata.extracted['device_name'] == 'Test Laser'
        assert metadata.confidence_score >= 0.2
    
    def test_parse_filename_old_format(self):
        """Test parsing old filename format"""
        parser = LBRNParser()
        filename_meta = parser._parse_filename("0001-Full Gas Box-Galv-1mm-x1.lbrn2")
        
        assert filename_meta.part_name == "Full Gas Box"
        assert filename_meta.material == "Galvanized Steel"
        assert filename_meta.thickness_mm == 1.0
        assert filename_meta.quantity == 1
    
    def test_parse_filename_new_format(self):
        """Test parsing new filename format"""
        parser = LBRNParser()
        filename_meta = parser._parse_filename("CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.lbrn2")
        
        assert filename_meta.client_code == "CL0001"
        assert filename_meta.project_code == "JB-2025-10-CL0001-001"
        assert filename_meta.part_name == "BracketLeft"
        assert filename_meta.material == "Mild Steel"
        assert filename_meta.thickness_mm == 5.0
        assert filename_meta.quantity == 14
        assert filename_meta.version == 1
    
    def test_material_detection_from_text(self):
        """Test material detection from text content"""
        parser = LBRNParser()
        
        # Test various material patterns
        assert parser._detect_material_from_text("Galvanized steel plate") == "Galvanized Steel"
        assert parser._detect_material_from_text("SS 304") == "Stainless Steel"
        assert parser._detect_material_from_text("Mild steel") == "Mild Steel"
        assert parser._detect_material_from_text("Aluminum plate") == "Aluminum"
    
    def test_thickness_detection_from_text(self):
        """Test thickness detection from text content"""
        parser = LBRNParser()
        
        # Test various thickness patterns
        assert parser._detect_thickness_from_text("Material: 3mm steel") == 3.0
        assert parser._detect_thickness_from_text("t=5mm") == 5.0
        assert parser._detect_thickness_from_text("thickness: 10") == 10.0
        assert parser._detect_thickness_from_text("no thickness here") is None
    
    def test_quantity_detection_from_text(self):
        """Test quantity detection from text content"""
        parser = LBRNParser()
        
        # Test various quantity patterns
        assert parser._detect_quantity_from_text("Qty: 10") == 10
        assert parser._detect_quantity_from_text("Quantity: 25") == 25
        assert parser._detect_quantity_from_text("x 5 pieces") == 5
    
    def test_client_code_detection(self):
        """Test client code detection from text"""
        parser = LBRNParser()
        
        # Test various client code patterns
        assert parser._detect_client_code("Client: CL-0001") == "CL0001"
        assert parser._detect_client_code("CL 0002 Project") == "CL0002"
        assert parser._detect_client_code("no client code") is None
    
    def test_project_code_detection(self):
        """Test project code detection from text"""
        parser = LBRNParser()
        
        # Test various project code patterns
        result = parser._detect_project_code("Project: JB-2025-10-CL0001-001")
        assert result is not None
        assert "JB" in result
    
    def test_cut_settings_extraction(self):
        """Test cut settings extraction"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'cut_settings' in metadata.extracted
        cut_settings = metadata.extracted['cut_settings']
        assert isinstance(cut_settings, list)
        assert len(cut_settings) == 2  # Cut and Engrave
        assert cut_settings[0]['type'] == 'Cut'
        assert cut_settings[1]['type'] == 'Engrave'
    
    def test_layer_count(self):
        """Test layer count extraction"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'layer_count' in metadata.extracted
        assert metadata.extracted['layer_count'] == 2
    
    def test_shape_count(self):
        """Test shape count extraction"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'shape_count' in metadata.extracted
        assert metadata.extracted['shape_count'] == 3  # Path, Circle, Text
    
    def test_shape_types(self):
        """Test shape types extraction"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'shape_types' in metadata.extracted
        shape_types = metadata.extracted['shape_types']
        assert 'Path' in shape_types
        assert 'Circle' in shape_types
        assert 'Text' in shape_types
    
    def test_text_extraction(self):
        """Test text element extraction"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'text_elements' in metadata.extracted
        text_elements = metadata.extracted['text_elements']
        assert isinstance(text_elements, list)
        assert len(text_elements) > 0
        assert 'Test Part' in text_elements[0]
    
    def test_material_height_extraction(self):
        """Test material height extraction"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'material_height' in metadata.extracted
        assert metadata.extracted['material_height'] == 3.0
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = LBRNParser()
        
        # Minimal metadata
        meta1 = NormalizedMetadata(
            source_file="test.lbrn2",
            detected_type=FileType.LBRN2,
            extracted={'layer_count': 1, 'shape_count': 5}
        )
        score1 = parser._calculate_confidence(meta1)
        assert 0.2 <= score1 <= 0.4
        
        # Complete metadata
        meta2 = NormalizedMetadata(
            source_file="test.lbrn2",
            detected_type=FileType.LBRN2,
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            part_name="Bracket",
            material="Mild Steel",
            thickness_mm=5.0,
            quantity=10,
            extracted={'layer_count': 2, 'shape_count': 10}
        )
        score2 = parser._calculate_confidence(meta2)
        assert score2 >= 0.9
    
    def test_invalid_lbrn_file(self):
        """Test handling of invalid LightBurn file"""
        parser = LBRNParser()
        
        # Create a temporary invalid LightBurn file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lbrn2', delete=False) as f:
            f.write("This is not valid XML")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Failed to parse LightBurn"):
                parser.parse(temp_path, "invalid.lbrn2")
        finally:
            Path(temp_path).unlink()
    
    def test_bounding_box_calculation(self):
        """Test bounding box calculation"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert 'bounding_box' in metadata.extracted
        bbox = metadata.extracted['bounding_box']
        assert 'width' in bbox
        assert 'height' in bbox
    
    def test_file_size_and_mime_type(self):
        """Test file size and MIME type are set"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(SAMPLE_LBRN, "test.lbrn2")
        
        assert metadata.file_size is not None
        assert metadata.file_size > 0
        assert metadata.mime_type == 'application/xml'
    
    def test_client_and_project_override(self):
        """Test that provided client/project codes override detection"""
        if not Path(SAMPLE_LBRN).exists():
            pytest.skip(f"Sample LightBurn file not found: {SAMPLE_LBRN}")
        
        parser = LBRNParser()
        metadata = parser.parse(
            SAMPLE_LBRN,
            "test.lbrn2",
            client_code="CL9999",
            project_code="TEST-2025-01-CL9999-999"
        )
        
        assert metadata.client_code == "CL9999"
        assert metadata.project_code == "TEST-2025-01-CL9999-999"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

