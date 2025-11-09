"""
Module N - DXF Parser Tests
Tests for DXF file parsing and metadata extraction
"""

import pytest
from pathlib import Path
from ..parsers.dxf_parser import DXFParser
from ..models.schemas import FileType


# Test fixtures - paths to sample DXF files
SAMPLE_DXF_1 = "dxf_starter_library_v1/dxf_library/02_Petrochemical_OilGas_Mining/baffle_rect_800x1200_t6_4cornerHoles.dxf"
SAMPLE_DXF_2 = "dxf_starter_library_v1/dxf_library/01_Structural_Steel_and_Construction/base_plate_200x200_t10_4x18_on160.dxf"
SAMPLE_DXF_3 = "profiles_import/CL-0001/1.Projects/0001-Gas Cover box 1 to 1 ratio-10.15.2025/0001-Full Gas Box Version1-Galv-1mm-x1.dxf"


class TestDXFParser:
    """Test suite for DXF parser"""
    
    def test_parser_initialization(self):
        """Test DXF parser can be initialized"""
        parser = DXFParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
    
    def test_parse_sample_dxf_baffle(self):
        """Test parsing baffle plate DXF file"""
        if not Path(SAMPLE_DXF_1).exists():
            pytest.skip(f"Sample DXF file not found: {SAMPLE_DXF_1}")
        
        parser = DXFParser()
        metadata = parser.parse(SAMPLE_DXF_1, "baffle_rect_800x1200_t6_4cornerHoles.dxf")
        
        # Check basic metadata
        assert metadata is not None
        assert metadata.detected_type == FileType.DXF
        assert metadata.source_file == "baffle_rect_800x1200_t6_4cornerHoles.dxf"
        
        # Check DXF-specific data
        assert 'layers' in metadata.extracted
        assert 'entity_counts' in metadata.extracted
        assert 'bounding_box' in metadata.extracted
        
        # Check layers
        layers = metadata.extracted['layers']
        assert isinstance(layers, list)
        assert len(layers) > 0
        assert 'OUTLINE' in layers or 'HOLES' in layers
        
        # Check bounding box
        bbox = metadata.extracted['bounding_box']
        if bbox:
            assert 'width' in bbox
            assert 'height' in bbox
            # Baffle should be approximately 800x1200mm
            assert bbox['width'] > 700
            assert bbox['height'] > 1100
        
        # Check holes
        holes = metadata.extracted.get('holes', [])
        assert isinstance(holes, list)
        # Should have 4 corner holes
        assert len(holes) >= 4
        
        # Check confidence score
        assert metadata.confidence_score > 0.0
        assert metadata.confidence_score <= 1.0
    
    def test_parse_sample_dxf_base_plate(self):
        """Test parsing base plate DXF file"""
        if not Path(SAMPLE_DXF_2).exists():
            pytest.skip(f"Sample DXF file not found: {SAMPLE_DXF_2}")
        
        parser = DXFParser()
        metadata = parser.parse(SAMPLE_DXF_2, "base_plate_200x200_t10_4x18_on160.dxf")
        
        # Check basic metadata
        assert metadata is not None
        assert metadata.detected_type == FileType.DXF
        
        # Check bounding box dimensions
        bbox = metadata.extracted.get('bounding_box')
        if bbox:
            # Base plate should be approximately 200x200mm
            assert bbox['width'] > 150
            assert bbox['width'] < 250
            assert bbox['height'] > 150
            assert bbox['height'] < 250
    
    def test_parse_filename_old_format(self):
        """Test parsing old filename format"""
        if not Path(SAMPLE_DXF_3).exists():
            pytest.skip(f"Sample DXF file not found: {SAMPLE_DXF_3}")
        
        parser = DXFParser()
        metadata = parser.parse(
            SAMPLE_DXF_3,
            "0001-Full Gas Box Version1-Galv-1mm-x1.dxf"
        )
        
        # Check filename parsing
        assert metadata.part_name == "Full Gas Box Version1"
        assert metadata.material == "Galvanized Steel"
        assert metadata.thickness_mm == 1.0
        assert metadata.quantity == 1
    
    def test_parse_filename_new_format(self):
        """Test parsing new filename format"""
        parser = DXFParser()
        
        # Create a minimal test - just test filename parsing without actual file
        filename_meta = parser._parse_filename("CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.dxf")
        
        assert filename_meta.client_code == "CL0001"
        assert filename_meta.project_code == "JB-2025-10-CL0001-001"
        assert filename_meta.part_name == "BracketLeft"
        assert filename_meta.material == "Mild Steel"
        assert filename_meta.thickness_mm == 5.0
        assert filename_meta.quantity == 14
        assert filename_meta.version == 1
    
    def test_material_detection_from_text(self):
        """Test material detection from text notes"""
        parser = DXFParser()
        
        # Test various material patterns
        assert parser._detect_material_from_text(["Galvanized steel plate"]) == "Galvanized Steel"
        assert parser._detect_material_from_text(["SS 304"]) == "Stainless Steel"
        assert parser._detect_material_from_text(["Mild steel"]) == "Mild Steel"
        assert parser._detect_material_from_text(["Aluminum plate"]) == "Aluminum"
        assert parser._detect_material_from_text(["Brass fitting"]) == "Brass"
    
    def test_thickness_detection_from_text(self):
        """Test thickness detection from text notes"""
        parser = DXFParser()
        
        # Test various thickness patterns
        assert parser._detect_thickness_from_text(["3mm plate"]) == 3.0
        assert parser._detect_thickness_from_text(["t=5mm"]) == 5.0
        assert parser._detect_thickness_from_text(["thickness: 10mm"]) == 10.0
        assert parser._detect_thickness_from_text(["1.5mm"]) == 1.5
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = DXFParser()
        
        # Create mock metadata with varying completeness
        from ..models.schemas import NormalizedMetadata, DXFMetadata
        
        # Minimal metadata (low confidence)
        minimal_meta = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            extracted={}
        )
        minimal_dxf = DXFMetadata()
        score_minimal = parser._calculate_confidence(minimal_meta, minimal_dxf)
        assert score_minimal >= 0.2  # Base score
        assert score_minimal < 0.5
        
        # Complete metadata (high confidence)
        complete_meta = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            client_code="CL0001",
            project_code="TEST-001",
            part_name="Test Part",
            material="Mild Steel",
            thickness_mm=5.0,
            extracted={}
        )
        complete_dxf = DXFMetadata(
            layers=["OUTLINE", "HOLES"],
            entity_counts={"LINE": 10, "CIRCLE": 4},
            bounding_box={"width": 100, "height": 100, "min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100}
        )
        score_complete = parser._calculate_confidence(complete_meta, complete_dxf)
        assert score_complete > 0.8
        assert score_complete <= 1.0
    
    def test_invalid_dxf_file(self):
        """Test handling of invalid DXF file"""
        parser = DXFParser()
        
        # Create a temporary invalid file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            f.write("This is not a valid DXF file")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid DXF file structure|Failed to parse DXF"):
                parser.parse(temp_path, "invalid.dxf")
        finally:
            Path(temp_path).unlink()
    
    def test_perimeter_calculation(self):
        """Test perimeter calculation from outline entities"""
        if not Path(SAMPLE_DXF_1).exists():
            pytest.skip(f"Sample DXF file not found: {SAMPLE_DXF_1}")
        
        parser = DXFParser()
        metadata = parser.parse(SAMPLE_DXF_1, "baffle_rect_800x1200_t6_4cornerHoles.dxf")
        
        # Check if perimeter was calculated
        perimeter = metadata.extracted.get('perimeter_mm')
        if perimeter:
            # Baffle 800x1200 should have perimeter around 4000mm (2*(800+1200))
            assert perimeter > 3500
            assert perimeter < 4500
    
    def test_entity_counting(self):
        """Test entity type counting"""
        if not Path(SAMPLE_DXF_1).exists():
            pytest.skip(f"Sample DXF file not found: {SAMPLE_DXF_1}")
        
        parser = DXFParser()
        metadata = parser.parse(SAMPLE_DXF_1, "baffle_rect_800x1200_t6_4cornerHoles.dxf")
        
        # Check entity counts
        entity_counts = metadata.extracted.get('entity_counts', {})
        assert isinstance(entity_counts, dict)
        assert len(entity_counts) > 0
        
        # Should have some common entities
        common_entities = ['LINE', 'CIRCLE', 'TEXT', 'POLYLINE', 'LWPOLYLINE']
        has_common = any(entity in entity_counts for entity in common_entities)
        assert has_common
    
    def test_text_extraction(self):
        """Test text note extraction"""
        if not Path(SAMPLE_DXF_1).exists():
            pytest.skip(f"Sample DXF file not found: {SAMPLE_DXF_1}")
        
        parser = DXFParser()
        metadata = parser.parse(SAMPLE_DXF_1, "baffle_rect_800x1200_t6_4cornerHoles.dxf")
        
        # Check text notes
        text_notes = metadata.extracted.get('text_notes', [])
        assert isinstance(text_notes, list)
        # Baffle file should have a title text
        if text_notes:
            assert any('baffle' in note.lower() for note in text_notes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

