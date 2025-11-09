"""
Module N - Integration Tests
Comprehensive tests for the complete flow: upload → parse → save to DB → retrieve
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from module_n.db.models import Base, FileIngest, FileExtraction, FileMetadata
from module_n.db.operations import (
    init_db,
    save_file_ingest,
    save_file_extraction,
    save_file_metadata,
    get_file_ingest,
    get_file_ingests,
    update_file_ingest,
    delete_file_ingest,
    re_extract_file
)
from module_n.storage.file_storage import (
    save_file,
    get_file_path,
    delete_file,
    file_exists,
    get_next_version
)
from module_n.parsers import DXFParser, PDFParser, ExcelParser, LBRNParser, ImageParser
from module_n.models.schemas import NormalizedMetadata, FileType

# Import filename generator directly to avoid libmagic dependency
from module_n.utils.filename_generator import generate_filename


# Test database URL (in-memory SQLite)
TEST_DB_URL = "sqlite:///:memory:"

# Test fixtures directory
FIXTURES_DIR = Path("module_n/tests/fixtures")


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
    # Initialize test database
    init_db(TEST_DB_URL)
    yield
    # Cleanup is automatic with in-memory database


@pytest.fixture(scope="function")
def test_storage(tmp_path):
    """Create a temporary storage directory for each test"""
    storage_dir = tmp_path / "test_storage"
    storage_dir.mkdir()
    yield storage_dir
    # Cleanup
    if storage_dir.exists():
        shutil.rmtree(storage_dir)


class TestDatabaseOperations:
    """Test database CRUD operations"""
    
    def test_save_and_get_file_ingest(self, test_db):
        """Test saving and retrieving file ingest"""
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            part_name="Bracket",
            material="Mild Steel",
            thickness_mm=5.0,
            quantity=10,
            confidence_score=0.95
        )
        
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
            file_path="CL0001/JB-2025-10-CL0001-001/CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
            status='completed'
        )
        
        assert file_ingest is not None
        assert file_ingest.id is not None
        assert file_ingest.client_code == "CL0001"
        assert file_ingest.material == "Mild Steel"
        
        # Retrieve
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is not None
        assert retrieved.id == file_ingest.id
        assert retrieved.part_name == "Bracket"
    
    def test_save_file_extraction(self, test_db):
        """Test saving extraction data"""
        # First create a file ingest
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            confidence_score=0.90
        )
        
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf"
        )
        
        # Save extraction
        extraction = save_file_extraction(
            file_ingest_id=file_ingest.id,
            extraction_type="dxf_metadata",
            extracted_data={"layers": 3, "entities": 150},
            confidence_score=0.90,
            parser_name="dxf_parser",
            parser_version="1.0.0"
        )
        
        assert extraction is not None
        assert extraction.file_ingest_id == file_ingest.id
        assert extraction.extraction_type == "dxf_metadata"
    
    def test_save_file_metadata(self, test_db):
        """Test saving metadata key-value pairs"""
        # First create a file ingest
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF
        )
        
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf"
        )
        
        # Save metadata
        success = save_file_metadata(
            file_ingest_id=file_ingest.id,
            metadata_dict={
                'material': 'Mild Steel',
                'thickness_mm': 5.0,
                'quantity': 10
            },
            source='dxf_parser'
        )
        
        assert success is True
        
        # Retrieve and check
        retrieved = get_file_ingest(file_ingest.id)
        assert len(retrieved.file_metadata) == 3
    
    def test_get_file_ingests_with_filters(self, test_db):
        """Test querying files with filters"""
        # Create multiple file ingests
        for i in range(5):
            metadata = NormalizedMetadata(
                source_file=f"test{i}.dxf",
                detected_type=FileType.DXF,
                client_code="CL0001" if i < 3 else "CL0002",
                material="Mild Steel" if i % 2 == 0 else "Stainless Steel",
                thickness_mm=5.0
            )
            
            save_file_ingest(
            normalized_metadata=metadata,
                original_filename=f"test{i}.dxf",
                stored_filename=f"test{i}-v1.dxf",
                file_path=f"test/test{i}-v1.dxf"
            )
        
        # Query all
        all_files = get_file_ingests()
        assert len(all_files) == 5
        
        # Query by client code
        cl0001_files = get_file_ingests(client_code="CL0001")
        assert len(cl0001_files) == 3
        
        # Query by material
        ms_files = get_file_ingests(material="Mild Steel")
        assert len(ms_files) == 3
        
        # Query by thickness
        thick_files = get_file_ingests(thickness_mm=5.0)
        assert len(thick_files) == 5
    
    def test_update_file_ingest(self, test_db):
        """Test updating file ingest"""
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            status='pending'
        )
        
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf",
            status='pending'
        )
        
        # Update
        updated = update_file_ingest(
            file_ingest.id,
            status='completed',
            confidence_score=0.95
        )
        
        assert updated is not None
        assert updated.status == 'completed'
        assert updated.confidence_score == 0.95
    
    def test_soft_delete_file_ingest(self, test_db):
        """Test soft deleting file ingest"""
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF
        )
        
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf"
        )
        
        # Soft delete
        success = delete_file_ingest(file_ingest.id, hard_delete=False)
        assert success is True
        
        # Should not be found in normal query
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is None
        
        # Should be found when including deleted
        retrieved_deleted = get_file_ingest(file_ingest.id, include_deleted=True)
        assert retrieved_deleted is not None
        assert retrieved_deleted.is_deleted is True
    
    def test_hard_delete_file_ingest(self, test_db):
        """Test hard deleting file ingest"""
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF
        )
        
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf"
        )
        
        # Hard delete
        success = delete_file_ingest(file_ingest.id, hard_delete=True)
        assert success is True
        
        # Should not be found even when including deleted
        retrieved = get_file_ingest(file_ingest.id, include_deleted=True)
        assert retrieved is None


class TestFileStorage:
    """Test file storage operations"""
    
    def test_save_file_basic(self, test_storage, tmp_path):
        """Test basic file saving"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        # Mock get_upload_folder to return test_storage
        import module_n.storage.file_storage as storage_module
        original_get_upload_folder = storage_module.get_upload_folder
        storage_module.get_upload_folder = lambda: test_storage
        
        try:
            result = save_file(
                source_path=str(test_file),
                normalized_filename="test-v1.txt",
                client_code="CL0001",
                project_code="JB-2025-10-CL0001-001",
                auto_version=False
            )
            
            assert result is not None
            stored_filename, file_path = result
            assert stored_filename == "test-v1.txt"
            assert "CL0001" in file_path
            
        finally:
            storage_module.get_upload_folder = original_get_upload_folder
    
    def test_auto_versioning(self, test_storage, tmp_path):
        """Test automatic version incrementing"""
        # Create test files
        test_file1 = tmp_path / "test1.txt"
        test_file1.write_text("Test content 1")
        test_file2 = tmp_path / "test2.txt"
        test_file2.write_text("Test content 2")
        
        # Mock get_upload_folder
        import module_n.storage.file_storage as storage_module
        original_get_upload_folder = storage_module.get_upload_folder
        storage_module.get_upload_folder = lambda: test_storage
        
        try:
            # Save first file
            result1 = save_file(
                source_path=str(test_file1),
                normalized_filename="test.txt",
                client_code="CL0001",
                auto_version=True
            )
            
            assert result1 is not None
            stored_filename1, _ = result1
            assert "v1" in stored_filename1
            
            # Save second file with same name
            result2 = save_file(
                source_path=str(test_file2),
                normalized_filename="test.txt",
                client_code="CL0001",
                auto_version=True
            )
            
            assert result2 is not None
            stored_filename2, _ = result2
            assert "v2" in stored_filename2
            
        finally:
            storage_module.get_upload_folder = original_get_upload_folder


class TestCompleteFlow:
    """Test complete flow: parse → save → retrieve"""

    def test_dxf_complete_flow(self, test_db, test_storage):
        """Test complete flow with DXF file"""
        dxf_file = FIXTURES_DIR / "test_baffle.dxf"
        if not dxf_file.exists():
            pytest.skip(f"DXF fixture not found: {dxf_file}")

        # Parse DXF
        parser = DXFParser()
        metadata = parser.parse(str(dxf_file), "test_baffle.dxf", "CL0001", "JB-2025-10-CL0001-001")

        assert metadata is not None
        assert metadata.detected_type == FileType.DXF

        # Generate filename
        normalized_filename = generate_filename(metadata)
        assert normalized_filename is not None

        # Save to database
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test_baffle.dxf",
            stored_filename=normalized_filename,
            file_path=f"CL0001/JB-2025-10-CL0001-001/{normalized_filename}",
            status='completed'
        )

        assert file_ingest is not None
        assert file_ingest.id is not None

        # Save extraction data
        extraction = save_file_extraction(
            file_ingest_id=file_ingest.id,
            extraction_type="dxf_metadata",
            extracted_data=metadata.extracted,
            confidence_score=metadata.confidence_score,
            parser_name="dxf_parser",
            parser_version="1.0.0"
        )

        assert extraction is not None

        # Retrieve and verify
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is not None
        assert retrieved.client_code == "CL0001"
        assert retrieved.file_type == "dxf"

    def test_pdf_complete_flow(self, test_db):
        """Test complete flow with PDF file"""
        pdf_file = FIXTURES_DIR / "test_quote.pdf"
        if not pdf_file.exists():
            pytest.skip(f"PDF fixture not found: {pdf_file}")

        # Parse PDF
        parser = PDFParser()
        metadata = parser.parse(str(pdf_file), "test_quote.pdf", "CL0001", "JB-2025-10-CL0001-001")

        assert metadata is not None
        assert metadata.detected_type == FileType.PDF

        # Generate filename
        normalized_filename = generate_filename(metadata)

        # Save to database
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test_quote.pdf",
            stored_filename=normalized_filename,
            file_path=f"CL0001/JB-2025-10-CL0001-001/{normalized_filename}",
            status='completed'
        )

        assert file_ingest is not None

        # Retrieve
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is not None
        assert retrieved.file_type == "pdf"

    def test_excel_complete_flow(self, test_db):
        """Test complete flow with Excel file"""
        excel_file = FIXTURES_DIR / "test_quote.xlsx"
        if not excel_file.exists():
            pytest.skip(f"Excel fixture not found: {excel_file}")

        # Parse Excel
        parser = ExcelParser()
        metadata = parser.parse(str(excel_file), "test_quote.xlsx", "CL0001", "JB-2025-10-CL0001-001")

        assert metadata is not None
        assert metadata.detected_type == FileType.EXCEL

        # Save to database
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test_quote.xlsx",
            stored_filename="test_quote-v1.xlsx",
            file_path="CL0001/test_quote-v1.xlsx",
            status='completed'
        )

        assert file_ingest is not None

        # Retrieve
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is not None
        assert retrieved.file_type == "excel"

    def test_lbrn_complete_flow(self, test_db):
        """Test complete flow with LightBurn file"""
        lbrn_file = FIXTURES_DIR / "test_lightburn.lbrn2"
        if not lbrn_file.exists():
            pytest.skip(f"LightBurn fixture not found: {lbrn_file}")

        # Parse LightBurn
        parser = LBRNParser()
        metadata = parser.parse(str(lbrn_file), "test_lightburn.lbrn2", "CL0001", "JB-2025-10-CL0001-001")

        assert metadata is not None
        assert metadata.detected_type == FileType.LBRN2

        # Save to database
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test_lightburn.lbrn2",
            stored_filename="test_lightburn-v1.lbrn2",
            file_path="CL0001/test_lightburn-v1.lbrn2",
            status='completed'
        )

        assert file_ingest is not None

        # Retrieve
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is not None
        assert retrieved.file_type == "lbrn2"

    def test_image_complete_flow(self, test_db):
        """Test complete flow with Image file"""
        image_file = FIXTURES_DIR / "test_image.png"
        if not image_file.exists():
            pytest.skip(f"Image fixture not found: {image_file}")

        # Parse Image
        parser = ImageParser()
        metadata = parser.parse(str(image_file), "test_image.png", "CL0001", "JB-2025-10-CL0001-001")

        assert metadata is not None
        assert metadata.detected_type == FileType.IMAGE

        # Save to database
        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test_image.png",
            stored_filename="test_image-v1.png",
            file_path="CL0001/test_image-v1.png",
            status='completed'
        )

        assert file_ingest is not None

        # Retrieve
        retrieved = get_file_ingest(file_ingest.id)
        assert retrieved is not None
        assert retrieved.file_type == "image"


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_invalid_file_id(self, test_db):
        """Test querying non-existent file"""
        result = get_file_ingest(99999)
        assert result is None

    def test_duplicate_metadata_keys(self, test_db):
        """Test saving duplicate metadata keys"""
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF
        )

        file_ingest = save_file_ingest(
            normalized_metadata=metadata,
            original_filename="test.dxf",
            stored_filename="test-v1.dxf",
            file_path="test/test-v1.dxf"
        )

        # Save metadata twice
        save_file_metadata(file_ingest.id, {'material': 'MS'}, 'parser')
        save_file_metadata(file_ingest.id, {'material': 'SS'}, 'user_override')

        # Should have both entries
        retrieved = get_file_ingest(file_ingest.id)
        assert len(retrieved.file_metadata) == 2

    def test_update_non_existent_file(self, test_db):
        """Test updating non-existent file"""
        result = update_file_ingest(99999, status='completed')
        assert result is None

    def test_delete_non_existent_file(self, test_db):
        """Test deleting non-existent file"""
        result = delete_file_ingest(99999)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

