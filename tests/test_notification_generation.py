"""
Test Notification Generation

This script manually triggers the notification evaluation job to test if notifications
are being generated correctly.
"""

from app import create_app, db
from app.models.business import Project, Notification
from app.scheduler.daily_job import evaluate_project_notifications_job
from datetime import datetime

app = create_app()
app.app_context().push()

# Color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

print(f'\n{BLUE}{"=" * 80}{RESET}')
print(f'{BLUE}{"TEST NOTIFICATION GENERATION".center(80)}{RESET}')
print(f'{BLUE}{"=" * 80}{RESET}\n')

# Check current notifications
print(f'{YELLOW}--- Before Evaluation ---{RESET}')
before_count = Notification.query.count()
print(f'Existing notifications: {before_count}')

# Check projects by stage
print(f'\n{YELLOW}--- Projects by Stage ---{RESET}')
projects = Project.query.all()
stage_counts = {}
for project in projects:
    stage = project.stage or 'None'
    stage_counts[stage] = stage_counts.get(stage, 0) + 1

for stage, count in sorted(stage_counts.items()):
    print(f'  {stage:25} {count:3} projects')

# Check for projects in QuotesAndApproval stage
quotes_projects = Project.query.filter_by(stage='QuotesAndApproval').all()
print(f'\n{YELLOW}--- Projects in QuotesAndApproval Stage ---{RESET}')
for project in quotes_projects:
    days_in_stage = (datetime.utcnow() - project.stage_last_updated).days
    print(f'  {project.project_code}: {days_in_stage} days in stage (threshold: 4 days)')

# Run the notification evaluation job
print(f'\n{YELLOW}--- Running Notification Evaluation Job ---{RESET}')
try:
    evaluate_project_notifications_job()
    print(f'{GREEN}✅ Notification evaluation completed successfully{RESET}')
except Exception as e:
    print(f'{RED}❌ Error: {str(e)}{RESET}')
    import traceback
    traceback.print_exc()

# Check notifications after
print(f'\n{YELLOW}--- After Evaluation ---{RESET}')
after_count = Notification.query.count()
print(f'Total notifications: {after_count}')
print(f'New notifications created: {after_count - before_count}')

if after_count > 0:
    print(f'\n{YELLOW}--- All Notifications ---{RESET}')
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    for notif in notifications:
        status = 'Resolved' if notif.resolved else 'Active'
        auto = ' (auto-clear)' if notif.auto_cleared else ''
        print(f'  [{status}] {notif.notif_type}: {notif.message[:60]}...{auto}')

print(f'\n{BLUE}{"=" * 80}{RESET}')
print(f'{GREEN}TEST COMPLETE!{RESET}')
print(f'{BLUE}{"=" * 80}{RESET}\n')

