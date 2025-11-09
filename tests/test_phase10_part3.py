#!/usr/bin/env python3
"""
Test Phase 10 Part 3: Machine Settings Presets and Operators Tables

This script verifies:
1. Operators table structure and data
2. Machine Settings Presets table structure and data
3. Laser Runs preset_id column
4. Indexes and constraints
5. Sample data integrity
"""

import sqlite3
import os

DB_PATH = 'data/laser_os.db'

def test_operators_table():
    """Test operators table."""
    print("=" * 70)
    print("TEST 1: Operators Table")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' AND name='operators'
    """)
    exists = cursor.fetchone()[0] > 0
    print(f"\n✅ Table exists: {exists}")
    
    if not exists:
        conn.close()
        return False
    
    # Check schema
    cursor.execute("PRAGMA table_info(operators)")
    columns = cursor.fetchall()
    
    expected_columns = ['id', 'name', 'email', 'phone', 'is_active', 'created_at', 'updated_at']
    actual_columns = [col[1] for col in columns]
    
    print(f"\n📊 Table Structure:")
    for col in columns:
        print(f"   • {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    
    missing = set(expected_columns) - set(actual_columns)
    if missing:
        print(f"\n❌ Missing columns: {missing}")
        conn.close()
        return False
    
    print(f"\n✅ All expected columns present")
    
    # Check indexes
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='operators'
    """)
    indexes = cursor.fetchall()
    print(f"\n🔍 Indexes ({len(indexes)}):")
    for idx in indexes:
        print(f"   • {idx[0]}")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM operators")
    count = cursor.fetchone()[0]
    print(f"\n📈 Total operators: {count}")
    
    cursor.execute("SELECT id, name, email, is_active FROM operators")
    operators = cursor.fetchall()
    print(f"\n📋 Operators:")
    for op in operators:
        status = "✅ Active" if op[3] else "❌ Inactive"
        email = op[2] if op[2] else "No email"
        print(f"   • ID {op[0]}: {op[1]} ({email}) - {status}")
    
    # Check constraints
    try:
        # Try to insert duplicate name (should fail)
        cursor.execute("INSERT INTO operators (name) VALUES ('System')")
        print(f"\n❌ UNIQUE constraint not working (duplicate allowed)")
        conn.rollback()
        conn.close()
        return False
    except sqlite3.IntegrityError:
        print(f"\n✅ UNIQUE constraint working (duplicate rejected)")
        conn.rollback()
    
    conn.close()
    return True

def test_presets_table():
    """Test machine_settings_presets table."""
    print("\n" + "=" * 70)
    print("TEST 2: Machine Settings Presets Table")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' AND name='machine_settings_presets'
    """)
    exists = cursor.fetchone()[0] > 0
    print(f"\n✅ Table exists: {exists}")
    
    if not exists:
        conn.close()
        return False
    
    # Check schema
    cursor.execute("PRAGMA table_info(machine_settings_presets)")
    columns = cursor.fetchall()
    
    print(f"\n📊 Table Structure ({len(columns)} columns):")
    for col in columns:
        nullable = "NULL" if not col[3] else "NOT NULL"
        print(f"   • {col[1]} ({col[2]}) {nullable}")
    
    # Check key columns
    expected_columns = [
        'id', 'preset_name', 'material_type', 'thickness',
        'nozzle', 'cut_speed', 'gas_type', 'gas_pressure',
        'peak_power', 'actual_power', 'duty_cycle', 'pulse_frequency',
        'is_active', 'created_at', 'updated_at'
    ]
    actual_columns = [col[1] for col in columns]
    
    missing = set(expected_columns) - set(actual_columns)
    if missing:
        print(f"\n❌ Missing columns: {missing}")
        conn.close()
        return False
    
    print(f"\n✅ All key columns present")
    
    # Check indexes
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='machine_settings_presets'
    """)
    indexes = cursor.fetchall()
    print(f"\n🔍 Indexes ({len(indexes)}):")
    for idx in indexes:
        print(f"   • {idx[0]}")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM machine_settings_presets")
    count = cursor.fetchone()[0]
    print(f"\n📈 Total presets: {count}")
    
    cursor.execute("""
        SELECT id, preset_name, material_type, thickness, 
               cut_speed, gas_type, peak_power, is_active
        FROM machine_settings_presets
        ORDER BY material_type, thickness
    """)
    presets = cursor.fetchall()
    print(f"\n📋 Presets:")
    for preset in presets:
        status = "✅" if preset[7] else "❌"
        print(f"   {status} ID {preset[0]}: {preset[1]}")
        print(f"      Material: {preset[2]} {preset[3]}mm")
        print(f"      Speed: {preset[4]} mm/min, Gas: {preset[5]}, Power: {preset[6]}W")
    
    # Check material type distribution
    cursor.execute("""
        SELECT material_type, COUNT(*) 
        FROM machine_settings_presets 
        GROUP BY material_type
    """)
    distribution = cursor.fetchall()
    print(f"\n📊 Presets by Material Type:")
    for mat, cnt in distribution:
        print(f"   • {mat}: {cnt} presets")
    
    conn.close()
    return True

def test_laser_runs_preset_id():
    """Test laser_runs preset_id column."""
    print("\n" + "=" * 70)
    print("TEST 3: Laser Runs preset_id Column")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check column exists
    cursor.execute("PRAGMA table_info(laser_runs)")
    columns = cursor.fetchall()
    preset_id_exists = any(col[1] == 'preset_id' for col in columns)
    
    print(f"\n✅ preset_id column exists: {preset_id_exists}")
    
    if not preset_id_exists:
        conn.close()
        return False
    
    # Get column details
    preset_id_col = [col for col in columns if col[1] == 'preset_id'][0]
    print(f"\n📊 Column Details:")
    print(f"   • Name: {preset_id_col[1]}")
    print(f"   • Type: {preset_id_col[2]}")
    print(f"   • Nullable: {'Yes' if not preset_id_col[3] else 'No'}")
    print(f"   • Default: {preset_id_col[4] if preset_id_col[4] else 'NULL'}")
    
    # Check index
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='laser_runs' AND name LIKE '%preset%'
    """)
    indexes = cursor.fetchall()
    print(f"\n🔍 Preset-related indexes:")
    for idx in indexes:
        print(f"   • {idx[0]}")
    
    # Check if any laser runs have preset_id set
    cursor.execute("SELECT COUNT(*) FROM laser_runs WHERE preset_id IS NOT NULL")
    with_preset = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM laser_runs")
    total = cursor.fetchone()[0]
    
    print(f"\n📈 Laser Runs:")
    print(f"   • Total: {total}")
    print(f"   • With preset_id: {with_preset}")
    print(f"   • Without preset_id: {total - with_preset}")
    
    conn.close()
    return True

def test_data_integrity():
    """Test data integrity and relationships."""
    print("\n" + "=" * 70)
    print("TEST 4: Data Integrity")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test 1: All operators have required fields
    cursor.execute("SELECT COUNT(*) FROM operators WHERE name IS NULL OR name = ''")
    invalid_operators = cursor.fetchone()[0]
    
    if invalid_operators > 0:
        print(f"\n❌ Found {invalid_operators} operators with missing names")
        conn.close()
        return False
    else:
        print(f"\n✅ All operators have valid names")
    
    # Test 2: All presets have required fields
    cursor.execute("""
        SELECT COUNT(*) FROM machine_settings_presets 
        WHERE preset_name IS NULL OR preset_name = ''
           OR material_type IS NULL OR material_type = ''
           OR thickness IS NULL
    """)
    invalid_presets = cursor.fetchone()[0]
    
    if invalid_presets > 0:
        print(f"❌ Found {invalid_presets} presets with missing required fields")
        conn.close()
        return False
    else:
        print(f"✅ All presets have required fields")
    
    # Test 3: Check for duplicate preset names
    cursor.execute("""
        SELECT preset_name, COUNT(*) 
        FROM machine_settings_presets 
        GROUP BY preset_name 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"❌ Found duplicate preset names:")
        for name, count in duplicates:
            print(f"   • {name}: {count} occurrences")
        conn.close()
        return False
    else:
        print(f"✅ No duplicate preset names")
    
    # Test 4: Check active status values
    cursor.execute("SELECT DISTINCT is_active FROM operators")
    operator_statuses = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT is_active FROM machine_settings_presets")
    preset_statuses = [row[0] for row in cursor.fetchall()]
    
    valid_statuses = [0, 1]
    if all(s in valid_statuses for s in operator_statuses + preset_statuses):
        print(f"✅ All is_active values are valid (0 or 1)")
    else:
        print(f"❌ Invalid is_active values found")
        conn.close()
        return False
    
    conn.close()
    return True

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PHASE 10 PART 3 - COMPREHENSIVE TEST SUITE")
    print("Machine Settings Presets and Operators")
    print("=" * 70)
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ Database not found: {DB_PATH}")
        return False
    
    tests = [
        ("Operators Table", test_operators_table),
        ("Machine Settings Presets Table", test_presets_table),
        ("Laser Runs preset_id Column", test_laser_runs_preset_id),
        ("Data Integrity", test_data_integrity),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\nPhase 10 Part 3 migration is complete and verified.")
        print("\nNext steps:")
        print("  1. Proceed to Phase 4: Model Updates")
        print("  2. Add Operator and MachineSettingsPreset models to app/models.py")
        print("  3. Update LaserRun model to include preset relationship")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease review the failures above and fix any issues.")
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

