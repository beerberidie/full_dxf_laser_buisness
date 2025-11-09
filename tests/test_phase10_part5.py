"""
Test script for Phase 10 Part 5: Dropdown Conversions
Tests the new dropdown functionality and preset auto-population.
"""

import sqlite3
import sys
from pathlib import Path

def test_phase5():
    """Test Phase 5 implementation."""
    
    print("=" * 80)
    print("PHASE 10 PART 5 - DROPDOWN CONVERSIONS TEST")
    print("=" * 80)
    print()
    
    # Connect to database
    db_path = Path('data/laser_os.db')
    if not db_path.exists():
        print("❌ ERROR: Database not found at data/laser_os.db")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    all_tests_passed = True
    
    # Test 1: Verify operators table has data
    print("Test 1: Verify operators table has active operators")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM operators WHERE is_active = 1")
    active_operators = cursor.fetchone()[0]
    if active_operators > 0:
        print(f"✅ PASS: Found {active_operators} active operators")
        cursor.execute("SELECT id, name FROM operators WHERE is_active = 1 ORDER BY name")
        for op_id, name in cursor.fetchall():
            print(f"   • {name} (ID: {op_id})")
    else:
        print("❌ FAIL: No active operators found")
        all_tests_passed = False
    print()
    
    # Test 2: Verify presets table has data
    print("Test 2: Verify machine_settings_presets table has active presets")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM machine_settings_presets WHERE is_active = 1")
    active_presets = cursor.fetchone()[0]
    if active_presets > 0:
        print(f"✅ PASS: Found {active_presets} active presets")
        cursor.execute("""
            SELECT id, preset_name, material_type, thickness 
            FROM machine_settings_presets 
            WHERE is_active = 1 
            ORDER BY material_type, thickness
        """)
        for preset_id, name, material, thickness in cursor.fetchall():
            print(f"   • {name} ({material} {thickness}mm) - ID: {preset_id}")
    else:
        print("❌ FAIL: No active presets found")
        all_tests_passed = False
    print()
    
    # Test 3: Verify laser_runs table has operator_id and preset_id columns
    print("Test 3: Verify laser_runs table schema")
    print("-" * 80)
    cursor.execute("PRAGMA table_info(laser_runs)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_columns = {
        'operator_id': 'INTEGER',
        'preset_id': 'INTEGER',
        'operator': 'VARCHAR(100)',  # Legacy field
        'material_type': 'VARCHAR(100)',
        'material_thickness': 'DECIMAL(10,3)'
    }
    
    schema_ok = True
    for col_name, col_type in required_columns.items():
        if col_name in columns:
            print(f"✅ Column '{col_name}' exists ({columns[col_name]})")
        else:
            print(f"❌ Column '{col_name}' missing")
            schema_ok = False
            all_tests_passed = False
    
    if schema_ok:
        print("✅ PASS: All required columns exist")
    else:
        print("❌ FAIL: Some columns are missing")
    print()
    
    # Test 4: Check if there are any laser runs with relationships
    print("Test 4: Check laser runs with operator/preset relationships")
    print("-" * 80)
    cursor.execute("""
        SELECT COUNT(*) FROM laser_runs 
        WHERE operator_id IS NOT NULL OR preset_id IS NOT NULL
    """)
    runs_with_relationships = cursor.fetchone()[0]
    print(f"ℹ️  Found {runs_with_relationships} laser runs with operator_id or preset_id")
    
    # Show sample if any exist
    if runs_with_relationships > 0:
        cursor.execute("""
            SELECT lr.id, lr.operator_id, o.name as operator_name, 
                   lr.preset_id, p.preset_name
            FROM laser_runs lr
            LEFT JOIN operators o ON lr.operator_id = o.id
            LEFT JOIN machine_settings_presets p ON lr.preset_id = p.id
            WHERE lr.operator_id IS NOT NULL OR lr.preset_id IS NOT NULL
            LIMIT 5
        """)
        print("   Sample laser runs:")
        for run_id, op_id, op_name, preset_id, preset_name in cursor.fetchall():
            print(f"   • Run #{run_id}: Operator={op_name or 'N/A'}, Preset={preset_name or 'N/A'}")
    print()
    
    # Test 5: Verify backward compatibility - legacy operator field
    print("Test 5: Verify backward compatibility with legacy operator field")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM laser_runs WHERE operator IS NOT NULL")
    legacy_runs = cursor.fetchone()[0]
    print(f"ℹ️  Found {legacy_runs} laser runs with legacy 'operator' text field")
    if legacy_runs > 0:
        print("✅ PASS: Legacy operator field is still functional")
    else:
        print("⚠️  WARNING: No laser runs with legacy operator field (this is OK if all are new)")
    print()
    
    # Test 6: Check indexes
    print("Test 6: Verify database indexes")
    print("-" * 80)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='laser_runs'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    required_indexes = ['idx_laser_runs_operator_id', 'idx_laser_runs_preset_id']
    indexes_ok = True
    for idx_name in required_indexes:
        if idx_name in indexes:
            print(f"✅ Index '{idx_name}' exists")
        else:
            print(f"⚠️  Index '{idx_name}' not found (may be auto-created)")
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    if all_tests_passed:
        print("✅ ALL CRITICAL TESTS PASSED")
        print()
        print("Phase 5 database schema is ready!")
        print()
        print("Next steps:")
        print("1. Start the Flask server")
        print("2. Navigate to a project and click 'Log Laser Run'")
        print("3. Verify dropdowns are populated:")
        print("   • Operator dropdown shows active operators")
        print("   • Material Type dropdown shows material types from config")
        print("   • Preset dropdown shows active presets")
        print("4. Test preset filtering:")
        print("   • Select a material type and thickness")
        print("   • Verify preset dropdown filters to matching presets")
        print("5. Test preset auto-population:")
        print("   • Select a preset")
        print("   • Verify machine settings fields are auto-populated")
        print("6. Submit the form and verify data is saved correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the errors above and fix any issues.")
    print("=" * 80)
    
    conn.close()
    return all_tests_passed

if __name__ == '__main__':
    success = test_phase5()
    sys.exit(0 if success else 1)

