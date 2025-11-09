"""
Module N - Image Parser Tests
Comprehensive tests for Image parsing functionality
"""

import pytest
import tempfile
from pathlib import Path
from PIL import Image
from module_n.parsers import ImageParser
from module_n.models.schemas import FileType, NormalizedMetadata


# Sample image file (test fixture)
SAMPLE_IMAGE = "module_n/tests/fixtures/test_image.png"


class TestImageParser:
    """Test suite for Image parser"""
    
    def test_parser_initialization(self):
        """Test that parser can be initialized"""
        parser = ImageParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'MATERIAL_PATTERNS')
        assert hasattr(parser, 'THICKNESS_PATTERN')
    
    def test_parse_sample_image(self):
        """Test parsing a sample image file"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(SAMPLE_IMAGE, "test_image.png")
        
        assert metadata.detected_type == FileType.IMAGE
        assert metadata.extracted is not None
        assert 'width' in metadata.extracted
        assert 'height' in metadata.extracted
        assert metadata.extracted['width'] > 0
        assert metadata.extracted['height'] > 0
        assert metadata.confidence_score >= 0.0
    
    def test_parse_filename_old_format(self):
        """Test parsing old filename format"""
        parser = ImageParser()
        filename_meta = parser._parse_filename("0001-Full Gas Box-Galv-1mm-x1.png")
        
        assert filename_meta.part_name == "Full Gas Box"
        assert filename_meta.material == "Galvanized Steel"
        assert filename_meta.thickness_mm == 1.0
        assert filename_meta.quantity == 1
    
    def test_parse_filename_new_format(self):
        """Test parsing new filename format"""
        parser = ImageParser()
        filename_meta = parser._parse_filename("CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.png")
        
        assert filename_meta.client_code == "CL0001"
        assert filename_meta.project_code == "JB-2025-10-CL0001-001"
        assert filename_meta.part_name == "BracketLeft"
        assert filename_meta.material == "Mild Steel"
        assert filename_meta.thickness_mm == 5.0
        assert filename_meta.quantity == 14
        assert filename_meta.version == 1
    
    def test_material_detection_from_text(self):
        """Test material detection from text content"""
        parser = ImageParser()
        
        # Test various material patterns
        assert parser._detect_material_from_text("Galvanized steel plate") == "Galvanized Steel"
        assert parser._detect_material_from_text("SS 304") == "Stainless Steel"
        assert parser._detect_material_from_text("Mild steel") == "Mild Steel"
        assert parser._detect_material_from_text("Aluminum plate") == "Aluminum"
    
    def test_thickness_detection_from_text(self):
        """Test thickness detection from text content"""
        parser = ImageParser()
        
        # Test various thickness patterns
        assert parser._detect_thickness_from_text("Material: 3mm steel") == 3.0
        assert parser._detect_thickness_from_text("t=5mm") == 5.0
        assert parser._detect_thickness_from_text("thickness: 10") == 10.0
        assert parser._detect_thickness_from_text("no thickness here") is None
    
    def test_quantity_detection_from_text(self):
        """Test quantity detection from text content"""
        parser = ImageParser()
        
        # Test various quantity patterns
        assert parser._detect_quantity_from_text("Qty: 10") == 10
        assert parser._detect_quantity_from_text("Quantity: 25") == 25
        assert parser._detect_quantity_from_text("x 5 pieces") == 5
    
    def test_client_code_detection(self):
        """Test client code detection from text"""
        parser = ImageParser()
        
        # Test various client code patterns
        assert parser._detect_client_code("Client: CL-0001") == "CL0001"
        assert parser._detect_client_code("CL 0002 Project") == "CL0002"
        assert parser._detect_client_code("no client code") is None
    
    def test_project_code_detection(self):
        """Test project code detection from text"""
        parser = ImageParser()
        
        # Test various project code patterns
        result = parser._detect_project_code("Project: JB-2025-10-CL0001-001")
        assert result is not None
        assert "JB" in result
    
    def test_image_dimensions(self):
        """Test image dimensions extraction"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(SAMPLE_IMAGE, "test.png")
        
        assert 'width' in metadata.extracted
        assert 'height' in metadata.extracted
        assert metadata.extracted['width'] == 400
        assert metadata.extracted['height'] == 200
    
    def test_image_format(self):
        """Test image format extraction"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(SAMPLE_IMAGE, "test.png")
        
        assert 'format' in metadata.extracted
        assert metadata.extracted['format'] == 'PNG'
    
    def test_image_mode(self):
        """Test image mode extraction"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(SAMPLE_IMAGE, "test.png")
        
        assert 'mode' in metadata.extracted
        assert metadata.extracted['mode'] in ['RGB', 'RGBA', 'L']
    
    def test_mime_type_png(self):
        """Test MIME type for PNG files"""
        parser = ImageParser()
        mime_type = parser._get_mime_type("test.png", "PNG")
        assert mime_type == 'image/png'
    
    def test_mime_type_jpg(self):
        """Test MIME type for JPG files"""
        parser = ImageParser()
        mime_type = parser._get_mime_type("test.jpg", "JPEG")
        assert mime_type == 'image/jpeg'
    
    def test_mime_type_bmp(self):
        """Test MIME type for BMP files"""
        parser = ImageParser()
        mime_type = parser._get_mime_type("test.bmp", "BMP")
        assert mime_type == 'image/bmp'
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = ImageParser()
        
        # Minimal metadata (no OCR)
        meta1 = NormalizedMetadata(
            source_file="test.png",
            detected_type=FileType.IMAGE,
            extracted={'width': 100, 'height': 100, 'ocr_available': False}
        )
        score1 = parser._calculate_confidence(meta1)
        assert 0.0 <= score1 <= 0.3
        
        # Complete metadata with OCR
        meta2 = NormalizedMetadata(
            source_file="test.png",
            detected_type=FileType.IMAGE,
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            part_name="Bracket",
            material="Mild Steel",
            thickness_mm=5.0,
            quantity=10,
            extracted={'width': 100, 'height': 100, 'ocr_available': True, 'ocr_text': 'Some text'}
        )
        score2 = parser._calculate_confidence(meta2)
        assert score2 >= 0.8
    
    def test_invalid_image_file(self):
        """Test handling of invalid image file"""
        parser = ImageParser()
        
        # Create a temporary invalid image file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.png', delete=False) as f:
            f.write("This is not a valid image")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Failed to parse image"):
                parser.parse(temp_path, "invalid.png")
        finally:
            Path(temp_path).unlink()
    
    def test_file_size_and_mime_type(self):
        """Test file size and MIME type are set"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(SAMPLE_IMAGE, "test.png")
        
        assert metadata.file_size is not None
        assert metadata.file_size > 0
        assert metadata.mime_type == 'image/png'
    
    def test_client_and_project_override(self):
        """Test that provided client/project codes override detection"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(
            SAMPLE_IMAGE,
            "test.png",
            client_code="CL9999",
            project_code="TEST-2025-01-CL9999-999"
        )
        
        assert metadata.client_code == "CL9999"
        assert metadata.project_code == "TEST-2025-01-CL9999-999"
    
    def test_ocr_availability_flag(self):
        """Test OCR availability flag is set correctly"""
        if not Path(SAMPLE_IMAGE).exists():
            pytest.skip(f"Sample image file not found: {SAMPLE_IMAGE}")
        
        parser = ImageParser()
        metadata = parser.parse(SAMPLE_IMAGE, "test.png")
        
        assert 'ocr_available' in metadata.extracted
        # OCR availability depends on whether pytesseract is installed
        assert isinstance(metadata.extracted['ocr_available'], bool)
    
    def test_create_simple_image(self):
        """Test parsing a simple created image"""
        # Create a simple test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(temp_path)
            
            parser = ImageParser()
            metadata = parser.parse(temp_path, "simple.png")
            
            assert metadata.detected_type == FileType.IMAGE
            assert metadata.extracted['width'] == 100
            assert metadata.extracted['height'] == 100
        finally:
            Path(temp_path).unlink()
    
    def test_grayscale_image(self):
        """Test parsing a grayscale image"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            img = Image.new('L', (50, 50), color=128)
            img.save(temp_path)
            
            parser = ImageParser()
            metadata = parser.parse(temp_path, "gray.png")
            
            assert metadata.detected_type == FileType.IMAGE
            assert metadata.extracted['mode'] == 'L'
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

