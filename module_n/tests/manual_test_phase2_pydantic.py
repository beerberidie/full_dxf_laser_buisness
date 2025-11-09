"""
Manual Test - Phase 2: Pydantic Models & Validation
Tests all Pydantic models with valid/invalid data, validation rules, edge cases
"""

import sys
from pathlib import Path
from pydantic import ValidationError

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from module_n.models.schemas import (
    NormalizedMetadata, DXFMetadata, PDFMetadata, ExcelMetadata,
    LBRNMetadata, ImageMetadata, FileIngestRequest,
    FileIngestResponse, IngestStatusResponse, FileType, ProcessingMode, ProcessingStatus
)


def test_normalized_metadata_valid():
    """Test NormalizedMetadata with valid data"""
    print("\n1. Testing NormalizedMetadata with valid data...")

    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            part_name="Bracket",
            material="Mild Steel",
            thickness_mm=5.0,
            quantity=10,
            version=1,
            confidence_score=0.95
        )
        print(f"   ✅ Valid NormalizedMetadata created: {metadata.part_name}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_normalized_metadata_invalid():
    """Test NormalizedMetadata with invalid data"""
    print("\n2. Testing NormalizedMetadata with invalid data...")

    tests_passed = 0
    tests_total = 0

    # Test invalid confidence score (> 1.0)
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            confidence_score=1.5
        )
        print(f"   ❌ Should have rejected confidence_score=1.5")
    except ValidationError:
        print(f"   ✅ Correctly rejected confidence_score=1.5")
        tests_passed += 1

    # Test invalid confidence score (< 0.0)
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            confidence_score=-0.5
        )
        print(f"   ❌ Should have rejected confidence_score=-0.5")
    except ValidationError:
        print(f"   ✅ Correctly rejected confidence_score=-0.5")
        tests_passed += 1

    # Test invalid thickness (negative)
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            thickness_mm=-5.0
        )
        print(f"   ❌ Should have rejected thickness_mm=-5.0")
    except ValidationError:
        print(f"   ✅ Correctly rejected thickness_mm=-5.0")
        tests_passed += 1

    # Test invalid quantity (zero)
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            quantity=0
        )
        print(f"   ❌ Should have rejected quantity=0")
    except ValidationError:
        print(f"   ✅ Correctly rejected quantity=0")
        tests_passed += 1

    print(f"   Validation tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def test_dxf_metadata():
    """Test DXFMetadata"""
    print("\n3. Testing DXFMetadata...")

    try:
        metadata = DXFMetadata(
            layers=["Layer1", "Layer2", "Layer3"],
            entity_counts={"LINE": 100, "CIRCLE": 50},
            dxf_version="AC1027",
            bounding_box={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100}
        )
        print(f"   ✅ Valid DXFMetadata created: {metadata.dxf_version}, {len(metadata.layers)} layers")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_pdf_metadata():
    """Test PDFMetadata"""
    print("\n4. Testing PDFMetadata...")

    try:
        metadata = PDFMetadata(
            page_count=5,
            text_content="Sample text from PDF",
            pdf_version="1.7"
        )
        print(f"   ✅ Valid PDFMetadata created: {metadata.page_count} pages, PDF {metadata.pdf_version}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_excel_metadata():
    """Test ExcelMetadata"""
    print("\n5. Testing ExcelMetadata...")

    try:
        metadata = ExcelMetadata(
            sheet_names=["Sheet1", "Sheet2", "Sheet3"],
            row_count=100,
            column_count=10
        )
        print(f"   ✅ Valid ExcelMetadata created: {len(metadata.sheet_names)} sheets, {metadata.row_count} rows")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_lbrn_metadata():
    """Test LBRNMetadata"""
    print("\n6. Testing LBRNMetadata...")

    try:
        metadata = LBRNMetadata(
            app_version="1.4.0",
            layer_count=2,
            has_variable_text=False
        )
        print(f"   ✅ Valid LBRNMetadata created: {metadata.layer_count} layers")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_image_metadata():
    """Test ImageMetadata"""
    print("\n7. Testing ImageMetadata...")

    try:
        metadata = ImageMetadata(
            width=1920,
            height=1080,
            format="PNG",
            mode="RGB",
            ocr_text="Sample OCR text"
        )
        print(f"   ✅ Valid ImageMetadata created: {metadata.width}x{metadata.height} {metadata.format}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_file_ingest_request():
    """Test FileIngestRequest"""
    print("\n8. Testing FileIngestRequest...")

    try:
        request = FileIngestRequest(
            client_code="CL0001",
            project_code="JB-2025-10-CL0001-001",
            mode=ProcessingMode.AUTO
        )
        print(f"   ✅ Valid FileIngestRequest created: mode={request.mode}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_file_ingest_response():
    """Test FileIngestResponse"""
    print("\n9. Testing FileIngestResponse...")

    try:
        response = FileIngestResponse(
            success=True,
            ingest_id=1,
            filename="test.dxf",
            normalized_filename="CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
            status=ProcessingStatus.COMPLETED
        )
        print(f"   ✅ Valid FileIngestResponse created: id={response.ingest_id}, status={response.status}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_ingest_status_response():
    """Test IngestStatusResponse"""
    print("\n10. Testing IngestStatusResponse...")

    try:
        from datetime import datetime
        response = IngestStatusResponse(
            ingest_id=1,
            status=ProcessingStatus.COMPLETED,
            filename="test.dxf",
            normalized_filename="CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
            confidence_score=0.95,
            created_at=datetime.utcnow()
        )
        print(f"   ✅ Valid IngestStatusResponse created: id={response.ingest_id}, status={response.status}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n11. Testing edge cases...")

    tests_passed = 0
    tests_total = 0

    # Test empty strings
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            client_code="",
            part_name="Test"
        )
        print(f"   ✅ Accepts empty client_code")
        tests_passed += 1
    except ValidationError:
        print(f"   ❌ Rejected empty client_code (should accept)")

    # Test very long strings
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            part_name="A" * 500
        )
        print(f"   ✅ Accepts very long part_name")
        tests_passed += 1
    except ValidationError:
        print(f"   ⚠️  Rejected very long part_name (may have max length)")
        tests_passed += 1  # This is acceptable behavior

    # Test None values for optional fields
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            client_code=None,
            part_name=None
        )
        print(f"   ✅ Accepts None for optional fields")
        tests_passed += 1
    except ValidationError:
        print(f"   ❌ Rejected None for optional fields")

    # Test boundary values for thickness
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            thickness_mm=0.001
        )
        print(f"   ✅ Accepts very small thickness (0.001mm)")
        tests_passed += 1
    except ValidationError:
        print(f"   ❌ Rejected very small thickness")

    # Test boundary values for quantity
    tests_total += 1
    try:
        metadata = NormalizedMetadata(
            source_file="test.dxf",
            detected_type=FileType.DXF,
            quantity=1
        )
        print(f"   ✅ Accepts quantity=1")
        tests_passed += 1
    except ValidationError:
        print(f"   ❌ Rejected quantity=1")

    print(f"   Edge case tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def main():
    """Run all Phase 2 tests"""
    print("\n" + "🔬 STARTING PHASE 2 COMPREHENSIVE TESTS".center(80, "="))
    
    results = []
    
    # Test all models
    results.append(("NormalizedMetadata - Valid Data", test_normalized_metadata_valid()))
    results.append(("NormalizedMetadata - Invalid Data", test_normalized_metadata_invalid()))
    results.append(("DXFMetadata", test_dxf_metadata()))
    results.append(("PDFMetadata", test_pdf_metadata()))
    results.append(("ExcelMetadata", test_excel_metadata()))
    results.append(("LBRNMetadata", test_lbrn_metadata()))
    results.append(("ImageMetadata", test_image_metadata()))
    results.append(("FileIngestRequest", test_file_ingest_request()))
    results.append(("FileIngestResponse", test_file_ingest_response()))
    results.append(("IngestStatusResponse", test_ingest_status_response()))
    results.append(("Edge Cases", test_edge_cases()))
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 2 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

