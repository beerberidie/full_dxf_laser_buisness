"""
Manual test script for ProfilesParser.

This script tests the parser without requiring pytest.
"""

from app.services.profiles_parser import ProfilesParser
from decimal import Decimal


def test_project_folder_parsing():
    """Test project folder parsing."""
    print("\n" + "="*70)
    print("TESTING PROJECT FOLDER PARSING")
    print("="*70)
    
    test_cases = [
        "0001-Gas Cover box-10.15.2025",
        "0042-Gas Cover box 1 to 1 ratio-12.25.2025",
        "0001-Project Name-15-10-2025",
        "0001-Box & Cover (v2)-10.15.2025",
    ]
    
    for folder_name in test_cases:
        print(f"\nTesting: {folder_name}")
        result = ProfilesParser.parse_project_folder(folder_name)
        if result:
            print(f"  ✓ Project Number: {result['project_number']}")
            print(f"  ✓ Description: {result['description']}")
            print(f"  ✓ Date: {result['date_created']}")
        else:
            print(f"  ✗ FAILED to parse")
    
    # Test invalid cases
    print("\n--- Testing Invalid Cases ---")
    invalid_cases = [
        "0001-Gas Cover box",  # Missing date
        "Gas Cover box-10.15.2025",  # Missing number
        "",  # Empty
    ]
    
    for folder_name in invalid_cases:
        print(f"\nTesting: '{folder_name}'")
        result = ProfilesParser.parse_project_folder(folder_name)
        if result is None:
            print(f"  ✓ Correctly rejected")
        else:
            print(f"  ✗ Should have been rejected")


def test_file_name_parsing():
    """Test file name parsing."""
    print("\n" + "="*70)
    print("TESTING FILE NAME PARSING")
    print("="*70)
    
    test_cases = [
        "0001-Full Gas Box Version1-Galv-1mm-x1.dxf",
        "0042-Bracket-SS-2mm-x10.dxf",
        "0001-Part-MS-3mm-x5.lbrn2",
        "0001-Part-Galv-1.5mm-x2.dxf",
        "0001-Part-Al-2mm-x1.dxf",
    ]
    
    for file_name in test_cases:
        print(f"\nTesting: {file_name}")
        result = ProfilesParser.parse_file_name(file_name)
        if result:
            print(f"  ✓ Project Number: {result['project_number']}")
            print(f"  ✓ Part Description: {result['part_description']}")
            print(f"  ✓ Material Code: {result['material_code']}")
            print(f"  ✓ Material Type: {result['material_type']}")
            print(f"  ✓ Thickness: {result['thickness']} mm")
            print(f"  ✓ Quantity: {result['quantity']}")
        else:
            print(f"  ✗ FAILED to parse")
    
    # Test invalid cases
    print("\n--- Testing Invalid Cases ---")
    invalid_cases = [
        "0001-Part-Galv-1mm.dxf",  # Missing quantity
        "random_file.dxf",  # Wrong format
        "",  # Empty
    ]
    
    for file_name in invalid_cases:
        print(f"\nTesting: '{file_name}'")
        result = ProfilesParser.parse_file_name(file_name)
        if result is None:
            print(f"  ✓ Correctly rejected")
        else:
            print(f"  ✗ Should have been rejected")


def test_material_mapping():
    """Test material code mapping."""
    print("\n" + "="*70)
    print("TESTING MATERIAL MAPPING")
    print("="*70)
    
    test_cases = [
        ("Galv", "Galvanized Steel"),
        ("SS", "Stainless Steel"),
        ("MS", "Mild Steel"),
        ("Al", "Aluminum"),
        ("Brass", "Brass"),
        ("Copper", "Copper"),
        ("Unknown", "Other"),
    ]
    
    for code, expected in test_cases:
        result = ProfilesParser.map_material(code)
        status = "✓" if result == expected else "✗"
        print(f"{status} {code:15} -> {result:20} (expected: {expected})")


def test_thickness_parsing():
    """Test thickness parsing."""
    print("\n" + "="*70)
    print("TESTING THICKNESS PARSING")
    print("="*70)
    
    test_cases = [
        ("1mm", Decimal('1.0')),
        ("2mm", Decimal('2.0')),
        ("1.5mm", Decimal('1.5')),
        ("0.5mm", Decimal('0.5')),
        ("1m", Decimal('1.0')),
        ("2.5", Decimal('2.5')),
    ]
    
    for thickness_str, expected in test_cases:
        result = ProfilesParser.parse_thickness(thickness_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} {thickness_str:10} -> {result} (expected: {expected})")
    
    # Test invalid cases
    print("\n--- Testing Invalid Cases ---")
    invalid_cases = ["", "abc", "-1mm", "0mm"]
    
    for thickness_str in invalid_cases:
        result = ProfilesParser.parse_thickness(thickness_str)
        status = "✓" if result is None else "✗"
        print(f"{status} '{thickness_str}' -> {result} (expected: None)")


def test_quantity_parsing():
    """Test quantity parsing."""
    print("\n" + "="*70)
    print("TESTING QUANTITY PARSING")
    print("="*70)
    
    test_cases = [
        ("1", 1),
        ("10", 10),
        ("100", 100),
    ]
    
    for quantity_str, expected in test_cases:
        result = ProfilesParser.parse_quantity(quantity_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} {quantity_str:10} -> {result} (expected: {expected})")
    
    # Test invalid cases
    print("\n--- Testing Invalid Cases ---")
    invalid_cases = ["", "abc", "-1", "0", "1.5"]
    
    for quantity_str in invalid_cases:
        result = ProfilesParser.parse_quantity(quantity_str)
        status = "✓" if result is None else "✗"
        print(f"{status} '{quantity_str}' -> {result} (expected: None)")


def test_date_parsing():
    """Test date parsing."""
    print("\n" + "="*70)
    print("TESTING DATE PARSING")
    print("="*70)
    
    test_cases = [
        "10.15.2025",
        "15-10-2025",
        "2025-10-15",
        "10/15/2025",
    ]
    
    for date_str in test_cases:
        result = ProfilesParser.parse_date(date_str)
        status = "✓" if result is not None else "✗"
        print(f"{status} {date_str:15} -> {result}")
    
    # Test invalid cases
    print("\n--- Testing Invalid Cases ---")
    invalid_cases = ["", "invalid", "13/32/2025"]
    
    for date_str in invalid_cases:
        result = ProfilesParser.parse_date(date_str)
        status = "✓" if result is None else "✗"
        print(f"{status} '{date_str}' -> {result} (expected: None)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROFILES PARSER - MANUAL TEST SUITE")
    print("="*70)
    
    try:
        test_project_folder_parsing()
        test_file_name_parsing()
        test_material_mapping()
        test_thickness_parsing()
        test_quantity_parsing()
        test_date_parsing()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)
        print("\nReview the output above to verify all tests passed (✓)")
        print("Any failures will be marked with (✗)")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

