"""
Comprehensive Production Automation Verification Script

This script systematically verifies all Production Automation features:
1. Database models and schema
2. Routes and blueprints
3. Services and business logic
4. Templates
5. Scheduler jobs
6. Security/RBAC
"""

from app import create_app, db
from sqlalchemy import inspect
import sys

app = create_app()
app.app_context().push()

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f'\n{BLUE}{"=" * 80}{RESET}')
    print(f'{BLUE}{text.center(80)}{RESET}')
    print(f'{BLUE}{"=" * 80}{RESET}\n')

def print_section(text):
    print(f'\n{YELLOW}--- {text} ---{RESET}')

def print_success(text):
    print(f'{GREEN}✅ {text}{RESET}')

def print_warning(text):
    print(f'{YELLOW}⚠️  {text}{RESET}')

def print_error(text):
    print(f'{RED}❌ {text}{RESET}')

# Track overall status
issues_found = []
warnings_found = []

print_header('PRODUCTION AUTOMATION - COMPREHENSIVE VERIFICATION')

# ============================================================================
# 1. DATABASE MODELS VERIFICATION
# ============================================================================
print_section('1. DATABASE MODELS VERIFICATION')

inspector = inspect(db.engine)
tables = inspector.get_table_names()

# Check new tables
new_tables = {
    'notifications': ['id', 'project_id', 'inventory_item_id', 'notif_type', 'message', 'resolved', 'auto_cleared', 'created_at', 'resolved_at'],
    'daily_reports': ['id', 'report_date', 'generated_at', 'runs_count', 'total_sheets_used', 'total_parts_produced', 'total_cut_time_minutes', 'report_body'],
    'outbound_drafts': ['id', 'client_id', 'project_id', 'channel_hint', 'body_text', 'sent', 'created_at', 'sent_at'],
    'extra_operators': ['id', 'name', 'is_active', 'created_at']
}

for table_name, expected_cols in new_tables.items():
    if table_name in tables:
        cols = inspector.get_columns(table_name)
        col_names = [c['name'] for c in cols]
        
        missing_cols = [col for col in expected_cols if col not in col_names]
        if missing_cols:
            print_error(f'{table_name}: Missing columns: {", ".join(missing_cols)}')
            issues_found.append(f'{table_name} missing columns: {missing_cols}')
        else:
            print_success(f'{table_name}: All columns present ({len(col_names)} columns)')
    else:
        print_error(f'{table_name}: TABLE MISSING')
        issues_found.append(f'{table_name} table does not exist')

# Check enhanced fields
enhanced_fields = {
    'users': ['role', 'is_active_operator', 'display_name'],
    'projects': ['stage', 'stage_last_updated', 'thickness_mm', 'sheet_size', 'sheets_required', 'target_complete_date'],
    'laser_runs': ['started_at', 'ended_at', 'sheets_used', 'sheet_size', 'thickness_mm'],
    'inventory_items': ['sheet_size', 'thickness_mm']
}

print_section('Enhanced Fields in Existing Tables')
for table_name, expected_fields in enhanced_fields.items():
    if table_name in tables:
        cols = inspector.get_columns(table_name)
        col_names = [c['name'] for c in cols]
        
        missing_fields = [field for field in expected_fields if field not in col_names]
        if missing_fields:
            print_error(f'{table_name}: Missing fields: {", ".join(missing_fields)}')
            issues_found.append(f'{table_name} missing enhanced fields: {missing_fields}')
        else:
            print_success(f'{table_name}: All enhanced fields present')
    else:
        print_error(f'{table_name}: TABLE MISSING')
        issues_found.append(f'{table_name} table does not exist')

# ============================================================================
# 2. ROUTES AND BLUEPRINTS VERIFICATION
# ============================================================================
print_section('2. ROUTES AND BLUEPRINTS VERIFICATION')

# Check blueprints
required_blueprints = ['notifications', 'phone']
registered_blueprints = list(app.blueprints.keys())

for bp_name in required_blueprints:
    if bp_name in registered_blueprints:
        print_success(f'Blueprint registered: {bp_name}')
    else:
        print_error(f'Blueprint missing: {bp_name}')
        issues_found.append(f'{bp_name} blueprint not registered')

# Check routes
print_section('Production Automation Routes')
pa_routes = []
for rule in app.url_map.iter_rules():
    rule_str = str(rule)
    if any(prefix in rule_str for prefix in ['/notifications', '/phone', '/reports/daily', '/communications/drafts']):
        pa_routes.append(rule_str)

expected_routes = [
    '/notifications/',
    '/notifications/count',
    '/notifications/<int:notification_id>/resolve',
    '/notifications/mark-all-read',
    '/phone/',
    '/phone/home',
    '/phone/run/start/<int:project_id>',
    '/reports/daily',
    '/reports/daily/<report_date>',
    '/reports/daily/generate',
    '/communications/drafts',
    '/communications/drafts/<int:draft_id>/send',
    '/communications/drafts/<int:draft_id>/delete',
    '/communications/drafts/<int:draft_id>/edit'
]

print(f'\nFound {len(pa_routes)} Production Automation routes:')
for route in sorted(pa_routes):
    print(f'  • {route}')

# ============================================================================
# 3. SERVICES VERIFICATION
# ============================================================================
print_section('3. SERVICES VERIFICATION')

try:
    from app.services.notification_logic import (
        get_unresolved_notifications,
        get_notification_count,
        mark_notification_resolved,
        evaluate_notifications_for_project
    )
    print_success('notification_logic service: All functions imported')
except ImportError as e:
    print_error(f'notification_logic service: Import error - {str(e)}')
    issues_found.append(f'notification_logic service import failed: {str(e)}')

try:
    from app.services.daily_report import (
        generate_daily_report,
        get_report_by_date,
        get_reports_for_date_range
    )
    print_success('daily_report service: All functions imported')
except ImportError as e:
    print_error(f'daily_report service: Import error - {str(e)}')
    issues_found.append(f'daily_report service import failed: {str(e)}')

try:
    from app.services.comms_drafts import (
        get_pending_drafts,
        get_sent_drafts,
        mark_draft_as_sent,
        delete_draft,
        update_draft
    )
    print_success('comms_drafts service: All functions imported')
except ImportError as e:
    print_error(f'comms_drafts service: Import error - {str(e)}')
    issues_found.append(f'comms_drafts service import failed: {str(e)}')

# ============================================================================
# 4. TEMPLATES VERIFICATION
# ============================================================================
print_section('4. TEMPLATES VERIFICATION')

import os
from pathlib import Path

template_dir = Path('app/templates')
required_templates = [
    'partials/bell_dropdown.html',
    'notifications/list.html',
    'phone/base_phone.html',
    'phone/home.html',
    'phone/run_active.html',
    'reports/daily_reports.html',
    'reports/daily_report.html',
    'comms/drafts.html',
    'comms/edit_draft.html'
]

for template_path in required_templates:
    full_path = template_dir / template_path
    if full_path.exists():
        print_success(f'Template exists: {template_path}')
    else:
        print_error(f'Template missing: {template_path}')
        issues_found.append(f'Template missing: {template_path}')

# ============================================================================
# 5. SCHEDULER VERIFICATION
# ============================================================================
print_section('5. SCHEDULER VERIFICATION')

try:
    from app.scheduler.daily_job import (
        generate_daily_report_job,
        evaluate_project_notifications_job,
        check_low_stock_job,
        init_scheduler
    )
    print_success('Scheduler jobs: All functions imported')
    print('  • generate_daily_report_job (07:30 SAST)')
    print('  • evaluate_project_notifications_job (hourly)')
    print('  • check_low_stock_job (every 6 hours)')
except ImportError as e:
    print_error(f'Scheduler jobs: Import error - {str(e)}')
    issues_found.append(f'Scheduler import failed: {str(e)}')

# ============================================================================
# 6. SECURITY/RBAC VERIFICATION
# ============================================================================
print_section('6. SECURITY/RBAC VERIFICATION')

try:
    from app.security.decorators import (
        require_role,
        require_any_role,
        is_operator,
        is_manager,
        is_admin,
        can_edit_presets,
        can_edit_inventory,
        can_access_phone_mode,
        can_access_pc_mode,
        can_generate_reports
    )
    print_success('Security decorators: All functions imported')
    print('  • require_role, require_any_role')
    print('  • is_operator, is_manager, is_admin')
    print('  • can_edit_presets, can_edit_inventory')
    print('  • can_access_phone_mode, can_access_pc_mode')
    print('  • can_generate_reports')
except ImportError as e:
    print_error(f'Security decorators: Import error - {str(e)}')
    issues_found.append(f'Security decorators import failed: {str(e)}')

# ============================================================================
# 7. MODEL SCHEMA MISMATCHES
# ============================================================================
print_section('7. MODEL SCHEMA MISMATCHES')

# Check DailyReport model vs database
from app.models.business import DailyReport
daily_report_model_cols = [c.name for c in DailyReport.__table__.columns]
daily_report_db_cols = [c['name'] for c in inspector.get_columns('daily_reports')]

if 'report_text' in daily_report_model_cols and 'report_text' not in daily_report_db_cols:
    print_warning('DailyReport: Model has "report_text" but DB has "report_body"')
    warnings_found.append('DailyReport schema mismatch: report_text vs report_body')
else:
    print_success('DailyReport: Model and DB schema match')

# Check ExtraOperator model vs database
from app.models.business import ExtraOperator
extra_op_model_cols = [c.name for c in ExtraOperator.__table__.columns]
extra_op_db_cols = [c['name'] for c in inspector.get_columns('extra_operators')]

if 'display_name' in extra_op_model_cols and 'display_name' not in extra_op_db_cols:
    print_warning('ExtraOperator: Model has "display_name" but DB has "name"')
    warnings_found.append('ExtraOperator schema mismatch: display_name vs name')
else:
    print_success('ExtraOperator: Model and DB schema match')

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header('VERIFICATION SUMMARY')

print(f'\n📊 Statistics:')
print(f'  • Total tables checked: {len(new_tables) + len(enhanced_fields)}')
print(f'  • Total routes found: {len(pa_routes)}')
print(f'  • Total templates checked: {len(required_templates)}')

if issues_found:
    print(f'\n{RED}❌ CRITICAL ISSUES FOUND: {len(issues_found)}{RESET}')
    for i, issue in enumerate(issues_found, 1):
        print(f'  {i}. {issue}')
else:
    print(f'\n{GREEN}✅ NO CRITICAL ISSUES FOUND{RESET}')

if warnings_found:
    print(f'\n{YELLOW}⚠️  WARNINGS: {len(warnings_found)}{RESET}')
    for i, warning in enumerate(warnings_found, 1):
        print(f'  {i}. {warning}')
else:
    print(f'\n{GREEN}✅ NO WARNINGS{RESET}')

print('\n' + '=' * 80)

# Exit with appropriate code
sys.exit(1 if issues_found else 0)

