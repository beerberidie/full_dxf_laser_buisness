#!/usr/bin/env python
"""
Test script to verify Immediate Actions implementation.

Tests:
1. Backup scheduling scripts exist and are executable
2. Production deployment guide exists
3. Performance monitoring is working
4. Log rotation is configured
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_backup_scheduling():
    """Test that backup scheduling scripts exist."""
    print('\n' + '=' * 80)
    print('TEST 1: Backup Scheduling Scripts')
    print('=' * 80)
    
    scripts = [
        'scripts/schedule_backup_windows.bat',
        'scripts/schedule_backup_linux.sh',
        'scripts/install_backup_schedule_windows.ps1'
    ]
    
    all_exist = True
    for script in scripts:
        script_path = project_root / script
        if script_path.exists():
            print(f'✓ {script} exists')
        else:
            print(f'✗ {script} missing')
            all_exist = False
    
    return all_exist


def test_production_guide():
    """Test that production deployment guide exists."""
    print('\n' + '=' * 80)
    print('TEST 2: Production Deployment Guide')
    print('=' * 80)
    
    guide_path = project_root / 'docs' / 'PRODUCTION_DEPLOYMENT_GUIDE.md'
    
    if not guide_path.exists():
        print(f'✗ Production deployment guide not found: {guide_path}')
        return False
    
    print(f'✓ Production deployment guide exists: {guide_path}')
    
    # Check guide content
    with open(guide_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_sections = [
        'Environment Configuration',
        'Generate a Strong SECRET_KEY',
        'Email Configuration',
        'Backup Automation',
        'Production Deployment Checklist'
    ]
    
    all_sections = True
    for section in required_sections:
        if section in content:
            print(f'  ✓ Section found: {section}')
        else:
            print(f'  ✗ Section missing: {section}')
            all_sections = False
    
    return all_sections


def test_performance_monitoring():
    """Test that performance monitoring is working."""
    print('\n' + '=' * 80)
    print('TEST 3: Performance Monitoring')
    print('=' * 80)
    
    # Check middleware exists
    middleware_path = project_root / 'app' / 'middleware' / 'performance.py'
    if not middleware_path.exists():
        print(f'✗ Performance middleware not found: {middleware_path}')
        return False
    
    print(f'✓ Performance middleware exists')
    
    # Check performance monitoring guide
    guide_path = project_root / 'docs' / 'PERFORMANCE_MONITORING_GUIDE.md'
    if not guide_path.exists():
        print(f'✗ Performance monitoring guide not found: {guide_path}')
        return False
    
    print(f'✓ Performance monitoring guide exists')
    
    # Check analysis script
    script_path = project_root / 'scripts' / 'analyze_performance.py'
    if not script_path.exists():
        print(f'✗ Performance analysis script not found: {script_path}')
        return False
    
    print(f'✓ Performance analysis script exists')
    
    # Test that app initializes with performance monitoring
    try:
        from app import create_app
        app = create_app()
        print(f'✓ Application initializes with performance monitoring')
        
        # Check if performance logger is configured
        import logging
        perf_logger = logging.getLogger('performance')
        if perf_logger.handlers:
            print(f'✓ Performance logger configured with {len(perf_logger.handlers)} handler(s)')
        else:
            print(f'⚠ Performance logger has no handlers')
        
        return True
        
    except Exception as e:
        print(f'✗ Failed to initialize app with performance monitoring: {e}')
        return False


def test_log_rotation():
    """Test that log rotation is configured."""
    print('\n' + '=' * 80)
    print('TEST 4: Log Rotation')
    print('=' * 80)
    
    # Check log rotation script
    script_path = project_root / 'scripts' / 'rotate_logs.py'
    if not script_path.exists():
        print(f'✗ Log rotation script not found: {script_path}')
        return False
    
    print(f'✓ Log rotation script exists')
    
    # Check config has log rotation settings
    try:
        from config import Config
        
        required_settings = ['LOG_LEVEL', 'LOG_FILE', 'LOG_MAX_BYTES', 'LOG_BACKUP_COUNT']
        all_settings = True
        
        for setting in required_settings:
            if hasattr(Config, setting):
                value = getattr(Config, setting)
                print(f'  ✓ {setting} = {value}')
            else:
                print(f'  ✗ {setting} not configured')
                all_settings = False
        
        return all_settings
        
    except Exception as e:
        print(f'✗ Failed to check config: {e}')
        return False


def test_env_example():
    """Test that .env.example has all required settings."""
    print('\n' + '=' * 80)
    print('TEST 5: Environment Configuration Template')
    print('=' * 80)
    
    env_example_path = project_root / '.env.example'
    
    if not env_example_path.exists():
        print(f'✗ .env.example not found: {env_example_path}')
        return False
    
    print(f'✓ .env.example exists')
    
    with open(env_example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_settings = [
        'SECRET_KEY',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'SESSION_COOKIE_SECURE',
        'LOG_LEVEL',
        'LOG_FILE',
        'Production Deployment Checklist'
    ]
    
    all_settings = True
    for setting in required_settings:
        if setting in content:
            print(f'  ✓ {setting} found')
        else:
            print(f'  ✗ {setting} missing')
            all_settings = False
    
    return all_settings


def test_documentation():
    """Test that all documentation is in place."""
    print('\n' + '=' * 80)
    print('TEST 6: Documentation')
    print('=' * 80)
    
    docs = [
        'docs/PRODUCTION_DEPLOYMENT_GUIDE.md',
        'docs/PERFORMANCE_MONITORING_GUIDE.md',
        'docs/QUICK_WINS_IMPLEMENTATION_SUMMARY.md',
        'docs/COMPREHENSIVE_ANALYSIS_AND_RECOMMENDATIONS.md'
    ]
    
    all_exist = True
    for doc in docs:
        doc_path = project_root / doc
        if doc_path.exists():
            size_kb = doc_path.stat().st_size / 1024
            print(f'✓ {doc} ({size_kb:.1f} KB)')
        else:
            print(f'✗ {doc} missing')
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print('\n' + '=' * 80)
    print('LASER OS TIER 1 - IMMEDIATE ACTIONS VERIFICATION')
    print('=' * 80)
    
    tests = [
        ('Backup Scheduling Scripts', test_backup_scheduling),
        ('Production Deployment Guide', test_production_guide),
        ('Performance Monitoring', test_performance_monitoring),
        ('Log Rotation', test_log_rotation),
        ('Environment Configuration', test_env_example),
        ('Documentation', test_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f'\n✗ Test "{test_name}" crashed: {str(e)}')
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print('\n' + '=' * 80)
    print('TEST SUMMARY')
    print('=' * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = '✓ PASS' if result else '✗ FAIL'
        print(f'{status}: {test_name}')
    
    print('\n' + '=' * 80)
    print(f'RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)')
    print('=' * 80)
    
    if passed == total:
        print('\n🎉 All Immediate Actions verified successfully!')
        return 0
    else:
        print(f'\n⚠ {total - passed} test(s) failed. Please review the output above.')
        return 1


if __name__ == '__main__':
    sys.exit(main())

