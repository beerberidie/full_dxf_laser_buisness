"""
Test script for Presets Management System
Tests the new presets management functionality and simplified laser run form.
"""

import sqlite3
import sys
from pathlib import Path

def test_presets_management():
    """Test presets management system."""
    
    print("=" * 80)
    print("PRESETS MANAGEMENT SYSTEM TEST")
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
    
    # Test 1: Verify machine_settings_presets table exists
    print("Test 1: Verify machine_settings_presets table exists")
    print("-" * 80)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machine_settings_presets'")
    if cursor.fetchone():
        print("✅ PASS: machine_settings_presets table exists")
    else:
        print("❌ FAIL: machine_settings_presets table not found")
        all_tests_passed = False
    print()
    
    # Test 2: Verify presets table has data
    print("Test 2: Verify presets table has data")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM machine_settings_presets")
    preset_count = cursor.fetchone()[0]
    if preset_count > 0:
        print(f"✅ PASS: Found {preset_count} presets in database")
        
        # Show sample presets
        cursor.execute("""
            SELECT preset_name, material_type, thickness, is_active 
            FROM machine_settings_presets 
            ORDER BY material_type, thickness 
            LIMIT 10
        """)
        print("\n   Sample presets:")
        for name, material, thickness, active in cursor.fetchall():
            status = "Active" if active else "Inactive"
            print(f"   • {name} ({material} {thickness}mm) - {status}")
    else:
        print("⚠️  WARNING: No presets found in database")
        print("   This is OK if you haven't created any presets yet")
    print()
    
    # Test 3: Verify operators table has data
    print("Test 3: Verify operators table has data")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM operators WHERE is_active = 1")
    operator_count = cursor.fetchone()[0]
    if operator_count > 0:
        print(f"✅ PASS: Found {operator_count} active operators")
    else:
        print("❌ FAIL: No active operators found")
        all_tests_passed = False
    print()
    
    # Test 4: Verify laser_runs table schema
    print("Test 4: Verify laser_runs table has required columns")
    print("-" * 80)
    cursor.execute("PRAGMA table_info(laser_runs)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_columns = ['operator_id', 'preset_id', 'machine_settings']
    schema_ok = True
    for col in required_columns:
        if col in columns:
            print(f"✅ Column '{col}' exists")
        else:
            print(f"❌ Column '{col}' missing")
            schema_ok = False
            all_tests_passed = False
    
    if schema_ok:
        print("✅ PASS: All required columns exist")
    print()
    
    # Test 5: Check preset usage
    print("Test 5: Check preset usage in laser runs")
    print("-" * 80)
    cursor.execute("""
        SELECT COUNT(*) FROM laser_runs WHERE preset_id IS NOT NULL
    """)
    runs_with_preset = cursor.fetchone()[0]
    print(f"ℹ️  Found {runs_with_preset} laser runs using presets")
    
    if runs_with_preset > 0:
        cursor.execute("""
            SELECT lr.id, p.preset_name, lr.material_type, lr.material_thickness
            FROM laser_runs lr
            JOIN machine_settings_presets p ON lr.preset_id = p.id
            LIMIT 5
        """)
        print("\n   Sample laser runs with presets:")
        for run_id, preset_name, material, thickness in cursor.fetchall():
            print(f"   • Run #{run_id}: {preset_name} ({material} {thickness}mm)")
    print()
    
    # Test 6: Verify activity log for presets
    print("Test 6: Verify activity logging for presets")
    print("-" * 80)
    cursor.execute("""
        SELECT COUNT(*) FROM activity_log 
        WHERE entity_type = 'PRESET'
    """)
    preset_activities = cursor.fetchone()[0]
    if preset_activities > 0:
        print(f"✅ PASS: Found {preset_activities} preset activity log entries")
        
        cursor.execute("""
            SELECT action, details, created_at 
            FROM activity_log 
            WHERE entity_type = 'PRESET' 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        print("\n   Recent preset activities:")
        for action, details, created_at in cursor.fetchall():
            print(f"   • {action}: {details} ({created_at})")
    else:
        print("ℹ️  No preset activity log entries yet (this is OK if no presets have been created/modified)")
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    if all_tests_passed:
        print("✅ ALL CRITICAL TESTS PASSED")
        print()
        print("Presets management system is ready!")
        print()
        print("Next steps:")
        print("1. Start the Flask server: python app.py")
        print("2. Navigate to the 'Presets' tab in the navigation menu")
        print("3. Test the presets management page:")
        print("   • View existing presets")
        print("   • Add a new preset")
        print("   • Edit an existing preset")
        print("   • Toggle active/inactive status")
        print("   • Delete a preset (if not in use)")
        print("4. Test the simplified 'Log Laser Run' form:")
        print("   • Navigate to a project and click 'Log Laser Run'")
        print("   • Verify the form only shows preset dropdown (no individual fields)")
        print("   • Select a preset and verify filtering works")
        print("   • Submit the form and verify data is saved correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the errors above and fix any issues.")
    print("=" * 80)
    
    conn.close()
    return all_tests_passed

if __name__ == '__main__':
    success = test_presets_management()
    sys.exit(0 if success else 1)

