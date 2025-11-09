"""
Module N - Validation Tests
Tests for file validation utilities
"""

import pytest
from pathlib import Path
from ..utils.validation import detect_file_type, sanitize_filename


def test_detect_file_type_dxf():
    """Test DXF file type detection"""
    assert detect_file_type("test.dxf", "AUTO") == "dxf"
    assert detect_file_type("test.DXF", "AUTO") == "dxf"


def test_detect_file_type_lbrn2():
    """Test LBRN2 file type detection"""
    assert detect_file_type("test.lbrn2", "AUTO") == "lbrn2"
    assert detect_file_type("test.LBRN2", "AUTO") == "lbrn2"


def test_detect_file_type_pdf():
    """Test PDF file type detection"""
    assert detect_file_type("test.pdf", "AUTO") == "pdf"
    assert detect_file_type("test.PDF", "AUTO") == "pdf"


def test_detect_file_type_excel():
    """Test Excel file type detection"""
    assert detect_file_type("test.xlsx", "AUTO") == "excel"
    assert detect_file_type("test.xls", "AUTO") == "excel"


def test_detect_file_type_image():
    """Test image file type detection"""
    assert detect_file_type("test.jpg", "AUTO") == "image"
    assert detect_file_type("test.png", "AUTO") == "image"


def test_detect_file_type_manual_mode():
    """Test manual mode overrides auto-detection"""
    assert detect_file_type("test.dxf", "pdf") == "pdf"
    assert detect_file_type("test.pdf", "dxf") == "dxf"


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("test file.dxf") == "test_file.dxf"
    assert sanitize_filename("../../../etc/passwd") == "etc_passwd"
    assert sanitize_filename("test@#$%.dxf") == "test.dxf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

