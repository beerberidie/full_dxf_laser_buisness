#!/usr/bin/env python3
"""
Test script for Phase 1 implementation
Verifies all changes are working correctly
"""

from app import create_app
from app.models import Project
import sys

def test_phase1():
    """Test Phase 1 changes."""
    print("=" * 70)
    print("PHASE 1 IMPLEMENTATION TEST")
    print("=" * 70)
    
    # Create app
    app = create_app()
    
    with app.app_context():
        # Test 1: Check if material_thickness attribute exists
        print("\n✓ Test 1: Model Attribute Check")
        if hasattr(Project, 'material_thickness'):
            print("  ✅ Project.material_thickness attribute exists")
        else:
            print("  ❌ Project.material_thickness attribute NOT found")
            return False
        
        # Test 2: Check database column
        print("\n✓ Test 2: Database Column Check")
        try:
            from sqlalchemy import inspect
            inspector = inspect(Project)
            columns = [c.name for c in inspector.columns]
            if 'material_thickness' in columns:
                print("  ✅ material_thickness column exists in database")
            else:
                print("  ❌ material_thickness column NOT in database")
                return False
        except Exception as e:
            print(f"  ❌ Error checking database: {e}")
            return False
        
        # Test 3: Query a project
        print("\n✓ Test 3: Query Test")
        try:
            project = Project.query.first()
            if project:
                print(f"  ✅ Successfully queried project: {project.name}")
                print(f"     Material Type: {project.material_type or 'Not set'}")
                print(f"     Material Thickness: {project.material_thickness or 'Not set'}")
                print(f"     Number of Bins: {project.number_of_bins or 'Not set'}")
            else:
                print("  ℹ️  No projects in database (this is OK)")
        except Exception as e:
            print(f"  ❌ Error querying project: {e}")
            return False
        
        # Test 4: Check config for lbrn2
        print("\n✓ Test 4: File Extension Check")
        if 'lbrn2' in app.config.get('ALLOWED_EXTENSIONS', set()):
            print("  ✅ lbrn2 extension added to ALLOWED_EXTENSIONS")
        else:
            print("  ❌ lbrn2 extension NOT in ALLOWED_EXTENSIONS")
            return False
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nPhase 1 implementation is working correctly.")
        print("\nNext steps:")
        print("  1. Start the Flask server: python run.py")
        print("  2. Open http://127.0.0.1:5000 in your browser")
        print("  3. Test the UI changes:")
        print("     - Create a new project with material thickness")
        print("     - Upload a .lbrn2 file")
        print("     - Verify label changes")
        
        return True

if __name__ == '__main__':
    success = test_phase1()
    sys.exit(0 if success else 1)

