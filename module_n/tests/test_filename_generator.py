"""
Module N - Filename Generator Tests
Tests for filename generation and parsing
"""

import pytest
from ..models.schemas import NormalizedMetadata, FileType
from ..utils.filename_generator import (
    generate_filename,
    parse_filename_metadata,
    extract_client_project_from_filename
)


def test_generate_filename_complete():
    """Test filename generation with all fields"""
    metadata = NormalizedMetadata(
        source_file="bracket.dxf",
        detected_type=FileType.DXF,
        client_code="CL0001",
        project_code="JB-2025-10-CL0001-001",
        part_name="BracketLeft",
        material="Mild Steel",
        thickness_mm=5.0,
        quantity=10,
        version=1
    )
    
    filename = generate_filename(metadata)
    assert filename == "CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x10.dxf"


def test_generate_filename_minimal():
    """Test filename generation with minimal fields"""
    metadata = NormalizedMetadata(
        source_file="test.dxf",
        detected_type=FileType.DXF
    )
    
    filename = generate_filename(metadata)
    assert filename == "UNKNOWN-NOPROJECT-Part-UNK.dxf"


def test_generate_filename_with_version():
    """Test filename generation with version"""
    metadata = NormalizedMetadata(
        source_file="bracket.dxf",
        detected_type=FileType.DXF,
        client_code="CL0001",
        project_code="JB-2025-10-CL0001-001",
        part_name="Bracket",
        material="Mild Steel",
        thickness_mm=5.0,
        quantity=1,
        version=2
    )
    
    filename = generate_filename(metadata)
    assert filename == "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-v2.dxf"


def test_parse_filename_metadata():
    """Test parsing metadata from filename"""
    filename = "CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x10-v1.dxf"
    
    metadata = parse_filename_metadata(filename)
    
    assert metadata['client_code'] == "CL0001"
    assert metadata['project_code'] == "JB-2025-10-CL0001-001"
    assert metadata['part_name'] == "BracketLeft"
    assert metadata['material'] == "Mild Steel"
    assert metadata['thickness_mm'] == 5.0
    assert metadata['quantity'] == 10
    assert metadata['version'] == 1


def test_extract_client_project_from_filename():
    """Test extracting client and project codes"""
    filename = "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10.dxf"
    
    client_code, project_code = extract_client_project_from_filename(filename)
    
    assert client_code == "CL0001"
    assert project_code == "JB-2025-10-CL0001-001"


def test_material_code_mapping():
    """Test material code mapping"""
    metadata = NormalizedMetadata(
        source_file="test.dxf",
        detected_type=FileType.DXF,
        client_code="CL0001",
        project_code="TEST-001",
        part_name="Test",
        material="Stainless Steel",
        thickness_mm=3.0
    )
    
    filename = generate_filename(metadata)
    assert "SS" in filename  # Stainless Steel -> SS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

