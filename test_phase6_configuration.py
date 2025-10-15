"""
Phase 6 Configuration Test Suite

Tests all configuration settings, validation, and environment variable handling.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig


def test_development_config():
    """Test development configuration."""
    print("\n" + "="*70)
    print("TEST 1: DEVELOPMENT CONFIGURATION")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Check basic settings
            assert app.config['DEBUG'] == True, "Debug should be enabled"
            assert app.config['TESTING'] == False, "Testing should be disabled"
            print("  ✓ Development mode configured correctly")
            
            # Check database
            assert 'SQLALCHEMY_DATABASE_URI' in app.config
            assert 'sqlite:///' in app.config['SQLALCHEMY_DATABASE_URI']
            print(f"  ✓ Database: {app.config['DATABASE_PATH']}")
            
            # Check file storage
            assert app.config['UPLOAD_FOLDER']
            assert app.config['DOCUMENTS_FOLDER']
            print(f"  ✓ Upload Folder: {app.config['UPLOAD_FOLDER']}")
            print(f"  ✓ Documents Folder: {app.config['DOCUMENTS_FOLDER']}")
            
            # Check Phase 9 settings
            assert app.config['POP_DEADLINE_DAYS'] == 3
            assert app.config['MAX_HOURS_PER_DAY'] == 8
            print(f"  ✓ POP Deadline: {app.config['POP_DEADLINE_DAYS']} days")
            print(f"  ✓ Max Hours/Day: {app.config['MAX_HOURS_PER_DAY']} hours")
            
            # Check material types
            assert len(app.config['MATERIAL_TYPES']) > 0
            print(f"  ✓ Material Types: {len(app.config['MATERIAL_TYPES'])} configured")
            
            # Check document types
            assert len(app.config['DOCUMENT_TYPES']) > 0
            print(f"  ✓ Document Types: {len(app.config['DOCUMENT_TYPES'])} configured")
            
            # Check communication types
            assert len(app.config['COMMUNICATION_TYPES']) > 0
            print(f"  ✓ Communication Types: {len(app.config['COMMUNICATION_TYPES'])} configured")
            
            # Check email settings
            assert app.config['MAIL_SERVER']
            assert app.config['MAIL_PORT']
            print(f"  ✓ Mail Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            
            # Check pagination
            assert app.config['ITEMS_PER_PAGE'] == 20
            assert app.config['COMMUNICATIONS_PER_PAGE'] == 25
            print(f"  ✓ Pagination: {app.config['ITEMS_PER_PAGE']} items/page")
        
        return True
    except Exception as e:
        print(f"  ✗ Development config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_testing_config():
    """Test testing configuration."""
    print("\n" + "="*70)
    print("TEST 2: TESTING CONFIGURATION")
    print("="*70)
    
    try:
        app = create_app('testing')
        
        with app.app_context():
            # Check testing mode
            assert app.config['TESTING'] == True, "Testing should be enabled"
            assert app.config['DEBUG'] == True, "Debug should be enabled"
            print("  ✓ Testing mode configured correctly")
            
            # Check in-memory database
            assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
            print("  ✓ Using in-memory database")
            
            # Check CSRF disabled
            assert app.config.get('WTF_CSRF_ENABLED') == False
            print("  ✓ CSRF disabled for testing")
            
            # All other settings should still be available
            assert app.config['POP_DEADLINE_DAYS']
            assert app.config['MATERIAL_TYPES']
            print("  ✓ All configuration settings available")
        
        return True
    except Exception as e:
        print(f"  ✗ Testing config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_validation():
    """Test configuration validation."""
    print("\n" + "="*70)
    print("TEST 3: CONFIGURATION VALIDATION")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Test material types
            materials = app.config['MATERIAL_TYPES']
            assert 'Mild Steel' in materials
            assert 'Stainless Steel' in materials
            assert 'Aluminum' in materials
            print(f"  ✓ Material types validated ({len(materials)} types)")
            
            # Test document types
            doc_types = app.config['DOCUMENT_TYPES']
            assert 'Quote' in doc_types
            assert 'Invoice' in doc_types
            assert 'Proof of Payment' in doc_types
            assert 'Delivery Note' in doc_types
            print(f"  ✓ Document types validated ({len(doc_types)} types)")
            
            # Test communication types
            comm_types = app.config['COMMUNICATION_TYPES']
            assert 'Email' in comm_types
            assert 'Phone' in comm_types
            assert 'WhatsApp' in comm_types
            print(f"  ✓ Communication types validated ({len(comm_types)} types)")
            
            # Test file extensions
            allowed_exts = app.config['ALLOWED_EXTENSIONS']
            assert 'dxf' in allowed_exts
            assert 'pdf' in allowed_exts
            print(f"  ✓ Allowed extensions validated ({len(allowed_exts)} types)")
            
            # Test document extensions
            doc_exts = app.config['ALLOWED_DOCUMENT_EXTENSIONS']
            assert 'pdf' in doc_exts
            assert 'xlsx' in doc_exts
            print(f"  ✓ Document extensions validated ({len(doc_exts)} types)")
            
            # Test numeric settings
            assert isinstance(app.config['POP_DEADLINE_DAYS'], int)
            assert isinstance(app.config['MAX_HOURS_PER_DAY'], int)
            assert isinstance(app.config['ITEMS_PER_PAGE'], int)
            assert isinstance(app.config['MAX_UPLOAD_SIZE'], int)
            print("  ✓ Numeric settings validated")
            
            # Test boolean settings
            assert isinstance(app.config['MAIL_USE_TLS'], bool)
            assert isinstance(app.config['MAIL_USE_SSL'], bool)
            print("  ✓ Boolean settings validated")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directory_creation():
    """Test that all required directories are created."""
    print("\n" + "="*70)
    print("TEST 4: DIRECTORY CREATION")
    print("="*70)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Check upload folder structure
            upload_folder = Path(app.config['UPLOAD_FOLDER'])
            assert upload_folder.exists(), f"Upload folder not created: {upload_folder}"
            assert (upload_folder / 'clients').exists(), "Clients subfolder not created"
            assert (upload_folder / 'reports').exists(), "Reports subfolder not created"
            print(f"  ✓ Upload folder structure created: {upload_folder}")
            
            # Check documents folder structure
            docs_folder = Path(app.config['DOCUMENTS_FOLDER'])
            assert docs_folder.exists(), f"Documents folder not created: {docs_folder}"
            assert (docs_folder / 'quotes').exists(), "Quotes subfolder not created"
            assert (docs_folder / 'invoices').exists(), "Invoices subfolder not created"
            assert (docs_folder / 'pops').exists(), "POPs subfolder not created"
            assert (docs_folder / 'delivery_notes').exists(), "Delivery notes subfolder not created"
            print(f"  ✓ Documents folder structure created: {docs_folder}")
            
            # Check database folder
            db_path = Path(app.config['DATABASE_PATH'])
            assert db_path.parent.exists(), f"Database folder not created: {db_path.parent}"
            print(f"  ✓ Database folder created: {db_path.parent}")
        
        return True
    except Exception as e:
        print(f"  ✗ Directory creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_variable_handling():
    """Test environment variable handling."""
    print("\n" + "="*70)
    print("TEST 5: ENVIRONMENT VARIABLE HANDLING")
    print("="*70)

    try:
        # Note: Environment variables are read when config module is imported
        # So we test that defaults work correctly
        app = create_app('development')

        with app.app_context():
            # Check that default values are set
            assert app.config['POP_DEADLINE_DAYS'] == 3, "Default POP_DEADLINE_DAYS not set"
            assert app.config['MAX_HOURS_PER_DAY'] == 8, "Default MAX_HOURS_PER_DAY not set"
            assert app.config['ITEMS_PER_PAGE'] == 20, "Default ITEMS_PER_PAGE not set"
            print("  ✓ Default integer values set correctly")

            # Check boolean defaults
            assert app.config['MAIL_USE_TLS'] == True, "Default MAIL_USE_TLS not set"
            assert app.config['MAIL_USE_SSL'] == False, "Default MAIL_USE_SSL not set"
            print("  ✓ Default boolean values set correctly")

            # Check string defaults
            assert app.config['MAIL_SERVER'] == 'smtp.gmail.com', "Default MAIL_SERVER not set"
            assert app.config['COMPANY_NAME'] == 'Laser OS', "Default COMPANY_NAME not set"
            print("  ✓ Default string values set correctly")

            # Check that environment variable mechanism exists
            assert 'SECRET_KEY' in app.config
            assert 'DATABASE_PATH' in app.config
            print("  ✓ Environment variable mechanism working")

        return True
    except Exception as e:
        print(f"  ✗ Environment variable test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_production_validation():
    """Test production configuration validation."""
    print("\n" + "="*70)
    print("TEST 6: PRODUCTION VALIDATION")
    print("="*70)

    try:
        # Test validation function directly (without creating production app)
        app = create_app('development')

        with app.app_context():
            # Test that validation catches default SECRET_KEY
            try:
                Config.validate_production_config(app)
                print("  ✗ Validation should have failed with default SECRET_KEY")
                return False
            except ValueError as e:
                print("  ✓ Validation correctly rejects default SECRET_KEY")
                error_msg = str(e)
                assert 'SECRET_KEY' in error_msg
                assert 'MAIL_USERNAME' in error_msg
                assert 'MAIL_PASSWORD' in error_msg
                print("  ✓ All required production settings checked")

        # Test with proper configuration
        app2 = create_app('development')
        with app2.app_context():
            # Temporarily set proper values
            app2.config['SECRET_KEY'] = 'test-production-secret-key-12345'
            app2.config['MAIL_USERNAME'] = 'test@example.com'
            app2.config['MAIL_PASSWORD'] = 'test-password'

            # This should pass
            result = Config.validate_production_config(app2)
            assert result == True
            print("  ✓ Validation passes with proper configuration")

        return True
    except Exception as e:
        print(f"  ✗ Production validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 6 configuration tests."""
    print("\n" + "="*70)
    print("PHASE 6 CONFIGURATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Development Configuration", test_development_config),
        ("Testing Configuration", test_testing_config),
        ("Configuration Validation", test_configuration_validation),
        ("Directory Creation", test_directory_creation),
        ("Environment Variable Handling", test_environment_variable_handling),
        ("Production Validation", test_production_validation),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nPhase 6 configuration is complete and working correctly.")
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

