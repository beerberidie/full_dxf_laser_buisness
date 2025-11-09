"""
Runtime Testing Script for Production Automation

This script tests actual runtime behavior to identify issues that static analysis misses.
"""

from app import create_app, db
from app.models.auth import User
from app.models.business import DailyReport, LaserRun, Project, Notification
from app.services.daily_report import generate_daily_report
from datetime import datetime, timedelta, date
import traceback

app = create_app()
app.app_context().push()

# Color codes
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

def print_error(text):
    print(f'{RED}❌ {text}{RESET}')

def print_warning(text):
    print(f'{YELLOW}⚠️  {text}{RESET}')

issues = []
warnings = []

print_header('PRODUCTION AUTOMATION - RUNTIME TESTING')

# ============================================================================
# TEST 1: User Roles and Operator Status
# ============================================================================
print_section('TEST 1: User Roles and Operator Status')

try:
    all_users = User.query.all()
    print(f'Total users in database: {len(all_users)}')
    
    print('\nUser Details:')
    print(f'{"Username":<15} {"Role":<10} {"Active Op":<10} {"Display Name":<20}')
    print('-' * 60)
    
    for user in all_users:
        print(f'{user.username:<15} {user.role:<10} {str(user.is_active_operator):<10} {user.display_name or "N/A":<20}')
    
    # Check for users with is_active_operator=True
    active_operators = User.query.filter_by(is_active_operator=True).all()
    print(f'\n✓ Users with is_active_operator=True: {len(active_operators)}')
    for op in active_operators:
        print(f'  - {op.username} ({op.display_name})')
    
    if len(active_operators) == 0:
        print_error('NO ACTIVE OPERATORS FOUND!')
        issues.append('No users have is_active_operator=True')
    else:
        print_success(f'Found {len(active_operators)} active operators')
    
    # Check for admin/manager users
    admins = User.query.filter_by(role='admin').all()
    managers = User.query.filter_by(role='manager').all()
    operators = User.query.filter_by(role='operator').all()
    
    print(f'\nRole Distribution:')
    print(f'  Admins: {len(admins)}')
    print(f'  Managers: {len(managers)}')
    print(f'  Operators: {len(operators)}')
    
    if len(admins) == 0:
        print_warning('No admin users found')
        warnings.append('No admin users configured')
    
except Exception as e:
    print_error(f'User role test failed: {str(e)}')
    traceback.print_exc()
    issues.append(f'User role test failed: {str(e)}')

# ============================================================================
# TEST 2: Daily Report Generation
# ============================================================================
print_section('TEST 2: Daily Report Generation')

try:
    # Check existing reports
    existing_reports = DailyReport.query.all()
    print(f'Existing daily reports: {len(existing_reports)}')
    
    if len(existing_reports) > 0:
        print('\nExisting Reports:')
        for report in existing_reports[:5]:  # Show first 5
            print(f'  - {report.report_date}: {report.runs_count} runs, {report.total_sheets_used} sheets')
    
    # Try to generate a report for yesterday
    print('\nAttempting to generate daily report for yesterday...')
    yesterday = date.today() - timedelta(days=1)
    
    # Check if report already exists
    existing = DailyReport.query.filter_by(report_date=yesterday).first()
    if existing:
        print(f'✓ Report already exists for {yesterday}')
        print(f'  Runs: {existing.runs_count}')
        print(f'  Sheets: {existing.total_sheets_used}')
        print(f'  Parts: {existing.total_parts_produced}')
        print(f'  Cut Time: {existing.total_cut_time_minutes} minutes')
        print_success('Daily report exists and has correct fields')
    else:
        # Generate new report
        report = generate_daily_report(yesterday)
        print(f'✓ Generated report for {yesterday}')
        print(f'  Runs: {report.runs_count}')
        print(f'  Sheets: {report.total_sheets_used}')
        print(f'  Parts: {report.total_parts_produced}')
        print(f'  Cut Time: {report.total_cut_time_minutes} minutes')
        print_success('Daily report generated successfully')
    
except Exception as e:
    print_error(f'Daily report generation failed: {str(e)}')
    traceback.print_exc()
    issues.append(f'Daily report generation failed: {str(e)}')

# ============================================================================
# TEST 3: Laser Runs and Operator Assignment
# ============================================================================
print_section('TEST 3: Laser Runs and Operator Assignment')

try:
    # Check laser runs
    all_runs = LaserRun.query.all()
    print(f'Total laser runs: {len(all_runs)}')
    
    if len(all_runs) > 0:
        print('\nRecent Runs:')
        recent_runs = LaserRun.query.order_by(LaserRun.id.desc()).limit(5).all()
        for run in recent_runs:
            operator_name = 'Unknown'
            if run.operator_id:
                operator = User.query.get(run.operator_id)
                if operator:
                    operator_name = operator.display_name or operator.username
            elif run.operator:
                operator_name = run.operator
            
            print(f'  - Run #{run.id}: {operator_name}, Status: {run.status}')
        
        print_success(f'Found {len(all_runs)} laser runs')
    else:
        print_warning('No laser runs found in database')
        warnings.append('No laser runs exist for testing')
    
    # Check for runs with operator_id
    runs_with_operator_id = LaserRun.query.filter(LaserRun.operator_id.isnot(None)).count()
    print(f'\nRuns with operator_id: {runs_with_operator_id}')
    
except Exception as e:
    print_error(f'Laser run test failed: {str(e)}')
    traceback.print_exc()
    issues.append(f'Laser run test failed: {str(e)}')

# ============================================================================
# TEST 4: Notifications
# ============================================================================
print_section('TEST 4: Notifications')

try:
    all_notifications = Notification.query.all()
    print(f'Total notifications: {len(all_notifications)}')
    
    if len(all_notifications) > 0:
        unresolved = Notification.query.filter_by(resolved=False).count()
        resolved = Notification.query.filter_by(resolved=True).count()
        
        print(f'  Unresolved: {unresolved}')
        print(f'  Resolved: {resolved}')
        
        # Show recent notifications
        recent = Notification.query.order_by(Notification.created_at.desc()).limit(5).all()
        print('\nRecent Notifications:')
        for notif in recent:
            status = 'Resolved' if notif.resolved else 'Active'
            print(f'  - {notif.notif_type}: {notif.message[:50]}... ({status})')
        
        print_success(f'Found {len(all_notifications)} notifications')
    else:
        print_warning('No notifications found')
        warnings.append('No notifications exist - system may not be generating them')
    
except Exception as e:
    print_error(f'Notification test failed: {str(e)}')
    traceback.print_exc()
    issues.append(f'Notification test failed: {str(e)}')

# ============================================================================
# TEST 5: Projects with Stage Information
# ============================================================================
print_section('TEST 5: Projects with Stage Information')

try:
    all_projects = Project.query.all()
    print(f'Total projects: {len(all_projects)}')
    
    if len(all_projects) > 0:
        # Count projects by stage
        stages = {}
        for project in all_projects:
            stage = project.stage or 'None'
            stages[stage] = stages.get(stage, 0) + 1
        
        print('\nProjects by Stage:')
        for stage, count in stages.items():
            print(f'  {stage}: {count}')
        
        # Check for projects with enhanced fields
        with_thickness = Project.query.filter(Project.thickness_mm.isnot(None)).count()
        with_sheet_size = Project.query.filter(Project.sheet_size.isnot(None)).count()
        with_stage = Project.query.filter(Project.stage.isnot(None)).count()
        
        print(f'\nProjects with enhanced fields:')
        print(f'  With thickness_mm: {with_thickness}')
        print(f'  With sheet_size: {with_sheet_size}')
        print(f'  With stage: {with_stage}')
        
        if with_stage == 0:
            print_warning('No projects have stage set')
            warnings.append('No projects have stage field populated')
        else:
            print_success(f'{with_stage} projects have stage information')
    else:
        print_warning('No projects found')
        warnings.append('No projects exist for testing')
    
except Exception as e:
    print_error(f'Project test failed: {str(e)}')
    traceback.print_exc()
    issues.append(f'Project test failed: {str(e)}')

# ============================================================================
# TEST 6: Role-Based Decorator Compatibility
# ============================================================================
print_section('TEST 6: Role-Based Decorator Compatibility')

try:
    # Test if users have has_role() method
    test_user = User.query.first()
    if test_user:
        # Try calling has_role() - this uses the old Role relationship
        try:
            has_admin_role = test_user.has_role('admin')
            print(f'✓ User.has_role() method exists (returns: {has_admin_role})')
            
            # But check the actual role field
            print(f'✓ User.role field value: {test_user.role}')
            
            # These might not match!
            if test_user.role == 'admin' and not has_admin_role:
                print_warning('MISMATCH: user.role="admin" but has_role("admin")=False')
                print_warning('This means decorators using has_role() will fail!')
                issues.append('Role field and has_role() method are inconsistent')
            else:
                print_success('Role field and has_role() method are consistent')
        except Exception as e:
            print_error(f'has_role() method failed: {str(e)}')
            issues.append(f'has_role() method error: {str(e)}')
    
except Exception as e:
    print_error(f'Role decorator test failed: {str(e)}')
    traceback.print_exc()
    issues.append(f'Role decorator test failed: {str(e)}')

# ============================================================================
# SUMMARY
# ============================================================================
print_header('RUNTIME TESTING SUMMARY')

print(f'\n📊 Test Results:')
print(f'  Critical Issues: {len(issues)}')
print(f'  Warnings: {len(warnings)}')

if issues:
    print(f'\n{RED}❌ CRITICAL ISSUES:{RESET}')
    for i, issue in enumerate(issues, 1):
        print(f'  {i}. {issue}')

if warnings:
    print(f'\n{YELLOW}⚠️  WARNINGS:{RESET}')
    for i, warning in enumerate(warnings, 1):
        print(f'  {i}. {warning}')

if not issues and not warnings:
    print(f'\n{GREEN}✅ ALL TESTS PASSED!{RESET}')

print('\n' + '=' * 80)

