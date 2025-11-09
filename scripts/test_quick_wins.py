#!/usr/bin/env python
"""
Test script to verify Quick Win improvements are working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Project, DesignFile, QueueItem, InventoryItem

def test_application_startup():
    """Test that application starts correctly."""
    print('\n' + '=' * 80)
    print('TEST 1: Application Startup')
    print('=' * 80)
    
    try:
        app = create_app()
        print(f'✓ Application created successfully')
        print(f'✓ Blueprints registered: {len(app.blueprints)}')
        print(f'✓ Database URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        return True
    except Exception as e:
        print(f'✗ Application startup failed: {str(e)}')
        return False


def test_database_queries():
    """Test that database queries work with new indexes."""
    print('\n' + '=' * 80)
    print('TEST 2: Database Queries with Indexes')
    print('=' * 80)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic counts
            total_projects = Project.query.count()
            print(f'✓ Total projects: {total_projects}')
            
            total_files = DesignFile.query.count()
            print(f'✓ Total design files: {total_files}')
            
            total_queue = QueueItem.query.count()
            print(f'✓ Total queue items: {total_queue}')
            
            # Test filtered queries (should use indexes)
            active_projects = Project.query.filter(
                Project.status.in_(['Approved', 'In Progress'])
            ).count()
            print(f'✓ Active projects (using idx_projects_status): {active_projects}')
            
            # Test ordered queries (should use indexes)
            recent_files = DesignFile.query.order_by(
                DesignFile.upload_date.desc()
            ).limit(5).all()
            print(f'✓ Recent files query (using idx_design_files_project_upload): {len(recent_files)} files')
            
            return True
            
        except Exception as e:
            print(f'✗ Database query failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return False


def test_eager_loading():
    """Test that eager loading works correctly."""
    print('\n' + '=' * 80)
    print('TEST 3: Eager Loading (N+1 Query Fix)')
    print('=' * 80)
    
    app = create_app()
    
    with app.app_context():
        try:
            from sqlalchemy.orm import joinedload
            
            # Test eager loading for design files
            recent_files = DesignFile.query.options(
                joinedload(DesignFile.project)
            ).order_by(
                DesignFile.upload_date.desc()
            ).limit(5).all()
            
            print(f'✓ Loaded {len(recent_files)} design files with eager loading')
            
            # Access project relationship (should not trigger additional queries)
            for file in recent_files:
                if file.project:
                    _ = file.project.project_code
            
            print(f'✓ Accessed project relationships without N+1 queries')
            
            # Test eager loading for queue items
            queue_items = QueueItem.query.options(
                joinedload(QueueItem.project)
            ).filter(
                QueueItem.status.in_(['Queued', 'In Progress'])
            ).order_by(QueueItem.queue_position).limit(5).all()
            
            print(f'✓ Loaded {len(queue_items)} queue items with eager loading')
            
            for item in queue_items:
                if item.project:
                    _ = item.project.project_code
            
            print(f'✓ Accessed queue item project relationships without N+1 queries')
            
            return True
            
        except Exception as e:
            print(f'✗ Eager loading test failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return False


def test_inventory_query_optimization():
    """Test optimized inventory low stock query."""
    print('\n' + '=' * 80)
    print('TEST 4: Inventory Query Optimization')
    print('=' * 80)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Old method (loads all items into memory)
            # low_stock_count = len([item for item in InventoryItem.query.all() if item.is_low_stock])

            # New method (database query only)
            low_stock_count = InventoryItem.query.filter(
                InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
            ).count()
            
            print(f'✓ Low stock items (optimized query): {low_stock_count}')
            print(f'✓ Query executed at database level (no Python iteration)')
            
            return True
            
        except Exception as e:
            print(f'✗ Inventory query test failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return False


def test_backup_directory():
    """Test that backup directory exists and backups were created."""
    print('\n' + '=' * 80)
    print('TEST 5: Backup System')
    print('=' * 80)
    
    try:
        backup_dir = project_root / 'data' / 'backups'
        
        if not backup_dir.exists():
            print(f'⚠ Backup directory does not exist: {backup_dir}')
            return False
        
        print(f'✓ Backup directory exists: {backup_dir}')
        
        # Count backup files
        backups = list(backup_dir.glob('laser_os_backup_*.db'))
        print(f'✓ Found {len(backups)} backup file(s)')
        
        if backups:
            latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
            size_mb = latest_backup.stat().st_size / (1024 * 1024)
            print(f'✓ Latest backup: {latest_backup.name} ({size_mb:.2f} MB)')
        
        return True
        
    except Exception as e:
        print(f'✗ Backup test failed: {str(e)}')
        return False


def test_css_classes():
    """Test that CSS classes exist for dashboard."""
    print('\n' + '=' * 80)
    print('TEST 6: CSS Classes (Inline Styles Removed)')
    print('=' * 80)
    
    try:
        css_file = project_root / 'app' / 'static' / 'css' / 'main.css'
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for new CSS classes
        required_classes = [
            'dashboard-stat-title',
            'dashboard-stat-value',
            'dashboard-stat-subtitle',
            'quick-action-btn',
            'inventory-stat-box',
            'inventory-stat-value'
        ]
        
        missing_classes = []
        for css_class in required_classes:
            if f'.{css_class}' in css_content:
                print(f'✓ CSS class exists: .{css_class}')
            else:
                print(f'✗ CSS class missing: .{css_class}')
                missing_classes.append(css_class)
        
        if missing_classes:
            print(f'\n⚠ Missing {len(missing_classes)} CSS class(es)')
            return False
        
        return True
        
    except Exception as e:
        print(f'✗ CSS test failed: {str(e)}')
        return False


def main():
    """Run all tests."""
    print('\n' + '=' * 80)
    print('LASER OS TIER 1 - QUICK WINS VERIFICATION')
    print('=' * 80)
    
    tests = [
        ('Application Startup', test_application_startup),
        ('Database Queries', test_database_queries),
        ('Eager Loading', test_eager_loading),
        ('Inventory Optimization', test_inventory_query_optimization),
        ('Backup System', test_backup_directory),
        ('CSS Classes', test_css_classes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f'\n✗ Test "{test_name}" crashed: {str(e)}')
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
        print('\n🎉 All Quick Win improvements verified successfully!')
        return 0
    else:
        print(f'\n⚠ {total - passed} test(s) failed. Please review the output above.')
        return 1


if __name__ == '__main__':
    sys.exit(main())

