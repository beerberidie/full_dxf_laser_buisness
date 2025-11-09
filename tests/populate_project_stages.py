"""
Populate Project Stages for Existing Projects

This script initializes the 'stage' field for existing projects based on their current status.
This is needed for Production Automation to work correctly.

Stage Mapping:
- STATUS_QUOTE_PENDING → QuotesAndApproval
- STATUS_QUOTE_SENT → QuotesAndApproval
- STATUS_APPROVED → WaitingOnMaterial (if no POP) or ReadyToCut (if POP received)
- STATUS_QUEUED → ReadyToCut
- STATUS_IN_PROGRESS → Cutting
- STATUS_COMPLETE → Complete
- STATUS_CANCELLED → (skip)
- STATUS_ON_HOLD → (keep current stage or set to WaitingOnMaterial)
"""

from app import create_app, db
from app.models.business import Project
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
print(f'{BLUE}{"POPULATE PROJECT STAGES".center(80)}{RESET}')
print(f'{BLUE}{"=" * 80}{RESET}\n')

# Get all projects without stage
projects_without_stage = Project.query.filter(
    (Project.stage == None) | (Project.stage == '')
).all()

print(f'Found {len(projects_without_stage)} projects without stage field\n')

if len(projects_without_stage) == 0:
    print(f'{GREEN}✅ All projects already have stage field populated!{RESET}')
    exit(0)

# Ask for confirmation
print(f'{YELLOW}This will update {len(projects_without_stage)} projects with appropriate stages.{RESET}')
print(f'{YELLOW}Stage will be determined based on current project status.{RESET}\n')

response = input('Continue? (yes/no): ').strip().lower()

if response not in ['yes', 'y']:
    print(f'{RED}Aborted.{RESET}')
    exit(0)

print()

# Stage mapping logic
updated_count = 0
stage_counts = {}

for project in projects_without_stage:
    old_status = project.status
    new_stage = None

    # Determine stage based on status
    if project.status == Project.STATUS_REQUEST:
        new_stage = 'QuotesAndApproval'

    elif project.status == Project.STATUS_QUOTE_APPROVAL:
        new_stage = 'QuotesAndApproval'

    elif project.status == Project.STATUS_APPROVED_POP:
        # POP received - ready to cut
        new_stage = 'ReadyToCut'

    elif project.status == Project.STATUS_QUEUED:
        new_stage = 'ReadyToCut'

    elif project.status == Project.STATUS_IN_PROGRESS:
        new_stage = 'Cutting'

    elif project.status == Project.STATUS_COMPLETED:
        new_stage = 'Complete'

    elif project.status == Project.STATUS_CANCELLED:
        # Skip cancelled projects
        continue

    # Legacy statuses
    elif project.status == Project.STATUS_QUOTE:
        new_stage = 'QuotesAndApproval'

    elif project.status == Project.STATUS_APPROVED:
        # Check if POP received
        if project.pop_received:
            new_stage = 'ReadyToCut'
        else:
            new_stage = 'WaitingOnMaterial'

    else:
        # Unknown status - default to QuotesAndApproval
        new_stage = 'QuotesAndApproval'
    
    # Update project
    if new_stage:
        project.stage = new_stage
        project.stage_last_updated = datetime.utcnow()
        
        # Track counts
        stage_counts[new_stage] = stage_counts.get(new_stage, 0) + 1
        updated_count += 1
        
        print(f'✓ {project.project_code:20} {old_status:20} → {new_stage}')

# Commit changes
if updated_count > 0:
    try:
        db.session.commit()
        print(f'\n{GREEN}✅ Successfully updated {updated_count} projects!{RESET}\n')
        
        print('Stage Distribution:')
        for stage, count in sorted(stage_counts.items()):
            print(f'  {stage:25} {count:3} projects')
        
        print(f'\n{BLUE}{"=" * 80}{RESET}')
        print(f'{GREEN}STAGE POPULATION COMPLETE!{RESET}')
        print(f'{BLUE}{"=" * 80}{RESET}\n')
        
        print('Next steps:')
        print('1. Restart the application to activate scheduler jobs')
        print('2. Scheduler will now evaluate projects for notifications')
        print('3. Check /notifications/ to see any generated alerts')
        print('4. Navigate to /reports/daily to generate daily reports')
        
    except Exception as e:
        db.session.rollback()
        print(f'\n{RED}❌ Error committing changes: {str(e)}{RESET}')
        exit(1)
else:
    print(f'\n{YELLOW}No projects were updated.{RESET}')

