"""
Module N - PDF Parser Tests
Comprehensive tests for PDF parsing functionality
"""

import pytest
import tempfile
from pathlib import Path
from module_n.parsers import PDFParser
from module_n.models.schemas import FileType, NormalizedMetadata


# Sample PDF files (if available in the codebase)
SAMPLE_PDF_1 = "data/documents/quotes/20251016_204054_c75e1176.pdf"
SAMPLE_PDF_2 = "data/documents/other/20251016_203416_b2ad49be.pdf"


class TestPDFParser:
    """Test suite for PDF parser"""
    
    def test_parser_initialization(self):
        """Test that parser can be initialized"""
        parser = PDFParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'MATERIAL_PATTERNS')
        assert hasattr(parser, 'THICKNESS_PATTERN')
    
    def test_parse_sample_pdf_quote(self):
        """Test parsing a sample quote PDF file"""
        if not Path(SAMPLE_PDF_1).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_1}")
        
        parser = PDFParser()
        metadata = parser.parse(SAMPLE_PDF_1, "quote.pdf")
        
        assert metadata.detected_type == FileType.PDF
        assert metadata.extracted is not None
        assert 'page_count' in metadata.extracted
        assert metadata.extracted['page_count'] > 0
        assert 'text_content' in metadata.extracted
        assert metadata.confidence_score >= 0.2
    
    def test_parse_sample_pdf_pop(self):
        """Test parsing a sample proof of payment PDF"""
        if not Path(SAMPLE_PDF_2).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_2}")
        
        parser = PDFParser()
        metadata = parser.parse(SAMPLE_PDF_2, "pop.pdf")
        
        assert metadata.detected_type == FileType.PDF
        assert metadata.extracted is not None
        assert metadata.confidence_score >= 0.2
    
    def test_parse_filename_old_format(self):
        """Test parsing old filename format"""
        parser = PDFParser()
        filename_meta = parser._parse_filename("0001-Full Gas Box-Galv-1mm-x1.pdf")
        
        assert filename_meta.part_name == "Full Gas Box"
        assert filename_meta.material == "Galvanized Steel"
        assert filename_meta.thickness_mm == 1.0
        assert filename_meta.quantity == 1
    
    def test_parse_filename_new_format(self):
        """Test parsing new filename format"""
        parser = PDFParser()
        filename_meta = parser._parse_filename("CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.pdf")
        
        assert filename_meta.client_code == "CL0001"
        assert filename_meta.project_code == "JB-2025-10-CL0001-001"
        assert filename_meta.part_name == "BracketLeft"
        assert filename_meta.material == "Mild Steel"
        assert filename_meta.thickness_mm == 5.0
        assert filename_meta.quantity == 14
        assert filename_meta.version == 1
    
    def test_material_detection_from_text(self):
        """Test material detection from text content"""
        parser = PDFParser()
        
        # Test various material patterns
        assert parser._detect_material_from_text("Galvanized steel plate") == "Galvanized Steel"
        assert parser._detect_material_from_text("SS 304") == "Stainless Steel"
        assert parser._detect_material_from_text("Mild steel") == "Mild Steel"
        assert parser._detect_material_from_text("Aluminum plate") == "Aluminum"
        assert parser._detect_material_from_text("Brass fitting") == "Brass"
        assert parser._detect_material_from_text("Copper sheet") == "Copper"
    
    def test_thickness_detection_from_text(self):
        """Test thickness detection from text content"""
        parser = PDFParser()
        
        # Test various thickness patterns
        assert parser._detect_thickness_from_text("Material: 3mm steel") == 3.0
        assert parser._detect_thickness_from_text("t=5mm") == 5.0
        assert parser._detect_thickness_from_text("thickness: 10") == 10.0
        assert parser._detect_thickness_from_text("6.5mm thick") == 6.5
        assert parser._detect_thickness_from_text("no thickness here") is None
    
    def test_quantity_detection_from_text(self):
        """Test quantity detection from text content"""
        parser = PDFParser()
        
        # Test various quantity patterns
        assert parser._detect_quantity_from_text("Qty: 10") == 10
        assert parser._detect_quantity_from_text("Quantity: 25") == 25
        assert parser._detect_quantity_from_text("x 5 pieces") == 5
        assert parser._detect_quantity_from_text("100 pcs") == 100
        assert parser._detect_quantity_from_text("no quantity") is None
    
    def test_client_code_detection(self):
        """Test client code detection from text"""
        parser = PDFParser()
        
        # Test various client code patterns
        assert parser._detect_client_code("Client: CL-0001") == "CL0001"
        assert parser._detect_client_code("CL 0002 Project") == "CL0002"
        assert parser._detect_client_code("CL0003") == "CL0003"
        assert parser._detect_client_code("no client code") is None
    
    def test_project_code_detection(self):
        """Test project code detection from text"""
        parser = PDFParser()
        
        # Test various project code patterns
        result = parser._detect_project_code("Project: JB-2025-10-CL0001-001")
        assert result is not None
        assert "JB" in result
        
        result = parser._detect_project_code("PO 2024 12 CL0002 005")
        assert result is not None
        assert "PO" in result
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = PDFParser()
        
        # Minimal metadata
        meta1 = NormalizedMetadata(
            source_file="test.pdf",
            detected_type=FileType.PDF,
            extracted={'page_count': 1}
        )
        score1 = parser._calculate_confidence(meta1)
        assert 0.2 <= score1 <= 0.3
        
        # Complete metadata
        meta2 = NormalizedMetadata(
            source_file="test.pdf",
            detected_type=FileType.PDF,
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            part_name="Bracket",
            material="Mild Steel",
            thickness_mm=5.0,
            quantity=10,
            extracted={'page_count': 2, 'tables': [{'table_number': 1}]}
        )
        score2 = parser._calculate_confidence(meta2)
        assert score2 >= 0.9
    
    def test_invalid_pdf_file(self):
        """Test handling of invalid PDF file"""
        parser = PDFParser()
        
        # Create a temporary invalid PDF file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("This is not a valid PDF file")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Failed to parse PDF"):
                parser.parse(temp_path, "invalid.pdf")
        finally:
            Path(temp_path).unlink()
    
    def test_text_extraction(self):
        """Test text extraction from PDF"""
        if not Path(SAMPLE_PDF_1).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_1}")
        
        parser = PDFParser()
        metadata = parser.parse(SAMPLE_PDF_1, "test.pdf")
        
        assert 'text_content' in metadata.extracted
        text = metadata.extracted['text_content']
        assert isinstance(text, str)
        # Text should not be empty for a real PDF
        assert len(text) > 0
    
    def test_metadata_extraction(self):
        """Test PDF metadata extraction"""
        if not Path(SAMPLE_PDF_1).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_1}")
        
        parser = PDFParser()
        metadata = parser.parse(SAMPLE_PDF_1, "test.pdf")
        
        assert 'pdf_metadata' in metadata.extracted
        pdf_meta = metadata.extracted['pdf_metadata']
        assert isinstance(pdf_meta, dict)
        # Should have standard PDF metadata fields
        assert 'title' in pdf_meta or 'creator' in pdf_meta or 'producer' in pdf_meta
    
    def test_page_count(self):
        """Test page count extraction"""
        if not Path(SAMPLE_PDF_1).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_1}")
        
        parser = PDFParser()
        metadata = parser.parse(SAMPLE_PDF_1, "test.pdf")
        
        assert 'page_count' in metadata.extracted
        assert metadata.extracted['page_count'] > 0
        assert isinstance(metadata.extracted['page_count'], int)
    
    def test_file_size_and_mime_type(self):
        """Test file size and MIME type are set"""
        if not Path(SAMPLE_PDF_1).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_1}")
        
        parser = PDFParser()
        metadata = parser.parse(SAMPLE_PDF_1, "test.pdf")
        
        assert metadata.file_size is not None
        assert metadata.file_size > 0
        assert metadata.mime_type == 'application/pdf'
    
    def test_part_name_detection(self):
        """Test part name detection from PDF"""
        parser = PDFParser()
        
        # Test with PDF metadata
        pdf_meta = {
            'metadata': {
                'title': 'Bracket Assembly Drawing'
            }
        }
        part_name = parser._detect_part_name(pdf_meta, "")
        assert part_name == "Bracket Assembly Drawing"
        
        # Test with text content
        text = "Part Name: Gas Box Cover\nMaterial: Mild Steel\nThickness: 3mm"
        part_name = parser._detect_part_name({}, text)
        assert part_name is not None
        assert len(part_name) > 0
    
    def test_client_and_project_override(self):
        """Test that provided client/project codes override detection"""
        if not Path(SAMPLE_PDF_1).exists():
            pytest.skip(f"Sample PDF file not found: {SAMPLE_PDF_1}")
        
        parser = PDFParser()
        metadata = parser.parse(
            SAMPLE_PDF_1,
            "test.pdf",
            client_code="CL9999",
            project_code="TEST-2025-01-CL9999-999"
        )
        
        assert metadata.client_code == "CL9999"
        assert metadata.project_code == "TEST-2025-01-CL9999-999"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

