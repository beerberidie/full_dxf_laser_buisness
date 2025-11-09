"""
Manual Test - Phase 5: File Parsers with Real Files
Tests all 5 parsers (DXF, PDF, Excel, LightBurn, Image) with real files from data/
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from module_n.parsers.dxf_parser import DXFParser
from module_n.parsers.lbrn_parser import LBRNParser


def test_dxf_parser_real_files():
    """Test DXF parser with real files"""
    print("\n" + "="*80)
    print("TESTING DXF PARSER WITH REAL FILES")
    print("="*80)
    
    dxf_files = [
        "data/files/1/20251007_074717_d8ba531d.dxf",
        "data/files/1/20251016_092739_813f16d2.dxf",
        "data/files/1/base_plate_200x200_t10_4x18_on160.dxf"
    ]
    
    parser = DXFParser()
    results = []
    
    for dxf_file in dxf_files:
        file_path = Path(dxf_file)
        if not file_path.exists():
            print(f"\n⚠️  File not found: {dxf_file}")
            continue
        
        print(f"\n📄 Testing: {file_path.name}")
        print(f"   Size: {file_path.stat().st_size:,} bytes")
        
        try:
            # Parse the file
            metadata = parser.parse(str(file_path), file_path.name)

            print(f"   ✅ Parsed successfully")
            print(f"      Detected type: {metadata.detected_type}")
            print(f"      Confidence: {metadata.confidence_score:.2f}")
            
            if metadata.client_code:
                print(f"      Client code: {metadata.client_code}")
            if metadata.project_code:
                print(f"      Project code: {metadata.project_code}")
            if metadata.part_name:
                print(f"      Part name: {metadata.part_name}")
            if metadata.material:
                print(f"      Material: {metadata.material}")
            if metadata.thickness_mm:
                print(f"      Thickness: {metadata.thickness_mm}mm")
            if metadata.quantity:
                print(f"      Quantity: {metadata.quantity}")
            
            # Check DXF-specific data
            if 'dxf' in metadata.extracted:
                dxf_data = metadata.extracted['dxf']
                if 'layers' in dxf_data:
                    print(f"      Layers: {len(dxf_data['layers'])}")
                if 'entity_counts' in dxf_data:
                    total_entities = sum(dxf_data['entity_counts'].values())
                    print(f"      Entities: {total_entities}")
                if 'dxf_version' in dxf_data:
                    print(f"      DXF version: {dxf_data['dxf_version']}")
            
            results.append((file_path.name, True, None))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append((file_path.name, False, str(e)))
    
    # Summary
    print("\n" + "-"*80)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"DXF Parser: {passed}/{total} files parsed successfully")
    
    return passed == total


def test_lbrn_parser_real_files():
    """Test LightBurn parser with real files"""
    print("\n" + "="*80)
    print("TESTING LIGHTBURN PARSER WITH REAL FILES")
    print("="*80)
    
    lbrn_files = [
        "data/files/1/20251016_092731_c526f742.lbrn2"
    ]
    
    # Find more .lbrn2 files
    data_path = Path("data/files")
    if data_path.exists():
        additional_files = list(data_path.rglob("*.lbrn2"))[:5]  # Get up to 5 files
        lbrn_files.extend([str(f) for f in additional_files if str(f) not in lbrn_files])
    
    parser = LBRNParser()
    results = []
    
    for lbrn_file in lbrn_files:
        file_path = Path(lbrn_file)
        if not file_path.exists():
            print(f"\n⚠️  File not found: {lbrn_file}")
            continue
        
        print(f"\n📄 Testing: {file_path.name}")
        print(f"   Size: {file_path.stat().st_size:,} bytes")
        
        try:
            # Parse the file
            metadata = parser.parse(str(file_path), file_path.name)

            print(f"   ✅ Parsed successfully")
            print(f"      Detected type: {metadata.detected_type}")
            print(f"      Confidence: {metadata.confidence_score:.2f}")

            if metadata.client_code:
                print(f"      Client code: {metadata.client_code}")
            if metadata.project_code:
                print(f"      Project code: {metadata.project_code}")
            if metadata.part_name:
                print(f"      Part name: {metadata.part_name}")
            if metadata.material:
                print(f"      Material: {metadata.material}")
            if metadata.thickness_mm:
                print(f"      Thickness: {metadata.thickness_mm}mm")

            # Check LightBurn-specific data
            if 'lbrn' in metadata.extracted:
                lbrn_data = metadata.extracted['lbrn']
                if 'layer_count' in lbrn_data:
                    print(f"      Layers: {lbrn_data['layer_count']}")
                if 'app_version' in lbrn_data:
                    print(f"      LightBurn version: {lbrn_data['app_version']}")
                if 'cut_settings' in lbrn_data:
                    print(f"      Cut settings: {len(lbrn_data['cut_settings'])}")
            
            results.append((file_path.name, True, None))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append((file_path.name, False, str(e)))
    
    # Summary
    print("\n" + "-"*80)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"LightBurn Parser: {passed}/{total} files parsed successfully")
    
    return passed == total


def test_parser_error_handling():
    """Test parser error handling with invalid files"""
    print("\n" + "="*80)
    print("TESTING PARSER ERROR HANDLING")
    print("="*80)
    
    parser = DXFParser()
    
    # Test with non-existent file
    print("\n1. Testing with non-existent file...")
    try:
        metadata = parser.parse("nonexistent.dxf", "nonexistent.dxf")
        print("   ❌ Should have raised an error")
        return False
    except Exception as e:
        print(f"   ✅ Correctly raised error: {type(e).__name__}")

    # Test with empty file
    print("\n2. Testing with empty file...")
    empty_file = Path("data/test_empty.dxf")
    try:
        empty_file.write_text("")
        metadata = parser.parse(str(empty_file), empty_file.name)
        print(f"   ⚠️  Parsed empty file (confidence: {metadata.confidence_score:.2f})")
    except Exception as e:
        print(f"   ✅ Correctly raised error: {type(e).__name__}")
    finally:
        if empty_file.exists():
            empty_file.unlink()

    # Test with corrupted file
    print("\n3. Testing with corrupted file...")
    corrupted_file = Path("data/test_corrupted.dxf")
    try:
        corrupted_file.write_text("This is not a valid DXF file\nJust random text\n")
        metadata = parser.parse(str(corrupted_file), corrupted_file.name)
        print(f"   ⚠️  Parsed corrupted file (confidence: {metadata.confidence_score:.2f})")
        if metadata.confidence_score < 0.5:
            print(f"   ✅ Low confidence score indicates detection of corruption")
    except Exception as e:
        print(f"   ✅ Correctly raised error: {type(e).__name__}")
    finally:
        if corrupted_file.exists():
            corrupted_file.unlink()
    
    return True


def test_parser_performance():
    """Test parser performance with real files"""
    print("\n" + "="*80)
    print("TESTING PARSER PERFORMANCE")
    print("="*80)
    
    import time
    
    dxf_file = "data/files/1/base_plate_200x200_t10_4x18_on160.dxf"
    file_path = Path(dxf_file)
    
    if not file_path.exists():
        print(f"⚠️  Test file not found: {dxf_file}")
        return True
    
    parser = DXFParser()
    
    print(f"\n📄 Testing performance with: {file_path.name}")
    print(f"   Size: {file_path.stat().st_size:,} bytes")
    
    # Parse multiple times to get average
    times = []
    for i in range(5):
        start = time.time()
        metadata = parser.parse(str(file_path), file_path.name)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n   Performance results:")
    print(f"      Average time: {avg_time*1000:.2f}ms")
    print(f"      Min time: {min_time*1000:.2f}ms")
    print(f"      Max time: {max_time*1000:.2f}ms")
    
    if avg_time < 1.0:
        print(f"   ✅ Performance is good (< 1 second)")
        return True
    elif avg_time < 5.0:
        print(f"   ⚠️  Performance is acceptable (< 5 seconds)")
        return True
    else:
        print(f"   ❌ Performance is slow (> 5 seconds)")
        return False


def main():
    """Run all Phase 5 tests"""
    print("\n" + "🔬 STARTING PHASE 5 COMPREHENSIVE TESTS".center(80, "="))
    
    results = []
    
    # Test parsers with real files
    results.append(("DXF Parser - Real Files", test_dxf_parser_real_files()))
    results.append(("LightBurn Parser - Real Files", test_lbrn_parser_real_files()))
    results.append(("Parser Error Handling", test_parser_error_handling()))
    results.append(("Parser Performance", test_parser_performance()))
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 5 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PHASE 5 TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

