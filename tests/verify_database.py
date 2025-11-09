"""
Verify Production Automation Database Schema
"""
from app import create_app, db
from sqlalchemy import inspect

app = create_app()
app.app_context().push()

print('=' * 70)
print('PRODUCTION AUTOMATION - DATABASE SCHEMA VERIFICATION')
print('=' * 70)

inspector = inspect(db.engine)
tables = inspector.get_table_names()

print(f'\n📊 Total tables: {len(tables)}')
print(f'Tables: {", ".join(sorted(tables))}')

# Check new tables
new_tables = ['notifications', 'daily_reports', 'outbound_drafts', 'extra_operators']
print('\n' + '=' * 70)
print('NEW TABLES VERIFICATION')
print('=' * 70)

for table_name in new_tables:
    if table_name in tables:
        print(f'\n✅ {table_name.upper()} TABLE EXISTS')
        cols = inspector.get_columns(table_name)
        print(f'   Columns ({len(cols)}):')
        for c in cols:
            nullable = 'NULL' if c.get('nullable', True) else 'NOT NULL'
            print(f'      - {c["name"]}: {c["type"]} ({nullable})')
    else:
        print(f'\n❌ {table_name.upper()} TABLE MISSING')

# Check enhanced fields in existing tables
print('\n' + '=' * 70)
print('ENHANCED FIELDS VERIFICATION')
print('=' * 70)

enhanced_fields = {
    'users': ['role', 'is_active_operator', 'display_name'],
    'projects': ['stage', 'stage_last_updated', 'thickness_mm', 'sheet_size', 'sheets_required', 'target_complete_date'],
    'laser_runs': ['started_at', 'ended_at', 'sheets_used', 'sheet_size', 'thickness_mm'],
    'inventory_items': ['sheet_size', 'thickness_mm']
}

for table_name, expected_fields in enhanced_fields.items():
    print(f'\n📋 {table_name.upper()} TABLE')
    if table_name in tables:
        cols = inspector.get_columns(table_name)
        col_names = [c['name'] for c in cols]
        
        for field in expected_fields:
            if field in col_names:
                col_info = next(c for c in cols if c['name'] == field)
                nullable = 'NULL' if col_info.get('nullable', True) else 'NOT NULL'
                print(f'   ✅ {field}: {col_info["type"]} ({nullable})')
            else:
                print(f'   ❌ {field}: MISSING')
    else:
        print(f'   ❌ Table does not exist')

print('\n' + '=' * 70)
print('VERIFICATION COMPLETE')
print('=' * 70)

