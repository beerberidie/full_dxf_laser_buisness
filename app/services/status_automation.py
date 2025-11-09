"""
Laser OS - Status Automation Service (V12.0)

This service handles automated status transitions and validations for the
status system redesign.

Features:
- Auto-advance from Request to Quote & Approval
- 30-day quote expiry checking and auto-cancellation
- 25-day quote reminder sending
- Status transition validation
- Quote expiry date calculation

Author: Laser OS Development Team
Version: 12.0
Date: 2025-10-23
"""

from datetime import date, timedelta
from typing import Dict, List, Optional
from app.models.business import Project, db
from app.services.activity_logger import log_activity


def auto_advance_to_quote_approval(project: Project, performed_by: str = 'System (Auto)') -> Dict:
    """
    Auto-advance project from Request to Quote & Approval if all required fields are valid.
    
    This function checks if a project in "Request" status has all required fields filled
    and automatically advances it to "Quote & Approval" status with a 30-day expiry timer.
    
    Args:
        project (Project): The project to check and potentially advance
        performed_by (str): User/system performing the action (default: 'System (Auto)')
    
    Returns:
        dict: {
            'advanced': bool - Whether the project was advanced
            'message': str - Success or failure message
            'reasons': list - List of missing fields (if not advanced)
        }
    
    Example:
        >>> result = auto_advance_to_quote_approval(project)
        >>> if result['advanced']:
        >>>     print(f"Project advanced: {result['message']}")
    """
    # Only auto-advance projects in Request status
    if project.status != Project.STATUS_REQUEST:
        return {
            'advanced': False,
            'message': f'Project is in {project.status} status, not Request',
            'reasons': []
        }
    
    # Check if ready for quote approval
    if not project.is_ready_for_quote_approval:
        missing_fields = get_missing_fields_for_quote_approval(project)
        return {
            'advanced': False,
            'message': 'Project not ready for quote approval',
            'reasons': missing_fields
        }
    
    # Advance to Quote & Approval
    old_status = project.status
    project.status = Project.STATUS_QUOTE_APPROVAL
    project.quote_date = date.today()
    project.calculate_quote_expiry_date(days=30)
    project.updated_at = db.func.now()
    
    # Commit changes
    db.session.commit()
    
    # Log activity
    log_activity('PROJECT', project.id, 'STATUS_AUTO_ADVANCED', {
        'old_status': old_status,
        'new_status': project.status,
        'quote_date': project.quote_date.isoformat(),
        'quote_expiry_date': project.quote_expiry_date.isoformat(),
        'reason': 'All required fields completed'
    }, performed_by)
    
    return {
        'advanced': True,
        'message': f'Project advanced to Quote & Approval (expires {project.quote_expiry_date})',
        'reasons': []
    }


def get_missing_fields_for_quote_approval(project: Project) -> List[str]:
    """
    Get list of missing required fields for Quote & Approval status.
    
    Args:
        project (Project): The project to check
    
    Returns:
        list: List of missing field names
    """
    missing = []
    
    if not project.name:
        missing.append('Project name')
    if not project.client_id:
        missing.append('Client')
    if not project.material_type:
        missing.append('Material type')
    if not project.material_thickness:
        missing.append('Material thickness')
    if len(project.design_files) == 0:
        missing.append('DXF files (at least one required)')
    
    return missing


def check_quote_expiry() -> Dict:
    """
    Background job to check for expired quotes and auto-cancel them.
    
    This function should be run daily by the background scheduler.
    It finds all projects in "Quote & Approval" status with expired quotes
    (quote_expiry_date < today AND pop_received = False) and automatically
    cancels them with can_reinstate = True.
    
    Returns:
        dict: {
            'checked': int - Number of projects checked
            'expired': int - Number of projects auto-cancelled
            'cancelled_ids': list - List of cancelled project IDs
            'errors': list - List of error messages (if any)
        }
    
    Example:
        >>> result = check_quote_expiry()
        >>> print(f"Checked {result['checked']} projects, cancelled {result['expired']}")
    """
    from app.services.notification_service import send_quote_expired_notice
    
    # Find projects in Quote & Approval with expired quotes
    expired_projects = Project.query.filter(
        Project.status == Project.STATUS_QUOTE_APPROVAL,
        Project.pop_received == False,
        Project.quote_expiry_date < date.today()
    ).all()
    
    cancelled_ids = []
    errors = []
    
    for project in expired_projects:
        try:
            # Cancel project
            project.cancel_with_reason(
                reason=f'Quote expired - No POP received within 30 days (expired {project.quote_expiry_date})',
                performed_by='System (Auto-Expiry)'
            )
            
            # Send notification
            try:
                send_quote_expired_notice(project)
            except Exception as e:
                errors.append(f'Failed to send notification for project {project.project_code}: {str(e)}')
            
            cancelled_ids.append(project.id)
            
        except Exception as e:
            errors.append(f'Failed to cancel project {project.project_code}: {str(e)}')
    
    # Commit all changes
    if cancelled_ids:
        db.session.commit()
    
    # Get total count of projects in Quote & Approval
    total_in_quote_approval = Project.query.filter_by(
        status=Project.STATUS_QUOTE_APPROVAL
    ).count()
    
    return {
        'checked': total_in_quote_approval,
        'expired': len(cancelled_ids),
        'cancelled_ids': cancelled_ids,
        'errors': errors
    }


def send_quote_reminders() -> Dict:
    """
    Background job to send 25-day quote expiry reminders.
    
    This function should be run daily by the background scheduler.
    It finds all projects in "Quote & Approval" status that will expire in 5 days
    (quote_expiry_date - 5 days = today) and sends reminder emails.
    
    Returns:
        dict: {
            'checked': int - Number of projects checked
            'reminders_sent': int - Number of reminders sent
            'project_ids': list - List of project IDs that received reminders
            'errors': list - List of error messages (if any)
        }
    
    Example:
        >>> result = send_quote_reminders()
        >>> print(f"Sent {result['reminders_sent']} reminders")
    """
    from app.services.notification_service import send_quote_expiry_reminder
    
    # Calculate reminder date (5 days before expiry)
    reminder_date = date.today() + timedelta(days=5)
    
    # Find projects that expire in 5 days and haven't been reminded yet
    projects_to_remind = Project.query.filter(
        Project.status == Project.STATUS_QUOTE_APPROVAL,
        Project.pop_received == False,
        Project.quote_expiry_date == reminder_date,
        Project.quote_reminder_sent == False
    ).all()
    
    reminded_ids = []
    errors = []
    
    for project in projects_to_remind:
        try:
            # Send reminder
            result = send_quote_expiry_reminder(project)
            
            if result.get('sent'):
                # Mark reminder as sent
                project.quote_reminder_sent = True
                reminded_ids.append(project.id)
                
                # Log activity
                log_activity('PROJECT', project.id, 'QUOTE_REMINDER_SENT', {
                    'quote_expiry_date': project.quote_expiry_date.isoformat(),
                    'days_remaining': 5
                }, 'System (Auto-Reminder)')
            else:
                errors.append(f'Failed to send reminder for project {project.project_code}: {result.get("message")}')
                
        except Exception as e:
            errors.append(f'Error sending reminder for project {project.project_code}: {str(e)}')
    
    # Commit all changes
    if reminded_ids:
        db.session.commit()
    
    # Get total count of projects in Quote & Approval
    total_in_quote_approval = Project.query.filter_by(
        status=Project.STATUS_QUOTE_APPROVAL
    ).count()
    
    return {
        'checked': total_in_quote_approval,
        'reminders_sent': len(reminded_ids),
        'project_ids': reminded_ids,
        'errors': errors
    }


def validate_status_transition(project: Project, new_status: str) -> Dict:
    """
    Validate if a status transition is allowed and check required fields.
    
    Args:
        project (Project): The project to validate
        new_status (str): The desired new status
    
    Returns:
        dict: {
            'valid': bool - Whether the transition is valid
            'message': str - Success or error message
            'missing_fields': list - List of missing required fields
            'warnings': list - List of warnings (non-blocking)
        }
    
    Example:
        >>> result = validate_status_transition(project, 'Quote & Approval')
        >>> if not result['valid']:
        >>>     print(f"Cannot transition: {result['message']}")
    """
    missing_fields = []
    warnings = []
    
    # Validate based on target status
    if new_status == Project.STATUS_QUOTE_APPROVAL:
        # Require: name, client, material type, material thickness, DXF files
        if not project.name:
            missing_fields.append('Project name')
        if not project.client_id:
            missing_fields.append('Client')
        if not project.material_type:
            missing_fields.append('Material type')
        if not project.material_thickness:
            missing_fields.append('Material thickness')
        if len(project.design_files) == 0:
            missing_fields.append('DXF files (at least one required)')
    
    elif new_status == Project.STATUS_APPROVED_POP:
        # Require: POP document, POP date
        if not project.pop_received:
            missing_fields.append('POP (Proof of Payment) must be marked as received')
        if not project.pop_received_date:
            missing_fields.append('POP received date')
    
    elif new_status == Project.STATUS_QUEUED:
        # Require: POP received, material details
        if not project.pop_received:
            missing_fields.append('POP must be received before queuing')
        if not project.estimated_cut_time:
            warnings.append('Estimated cut time not set - queue scheduling may be affected')
    
    elif new_status == Project.STATUS_IN_PROGRESS:
        # Require: Must be queued first
        if project.status not in [Project.STATUS_QUEUED, Project.STATUS_IN_PROGRESS]:
            missing_fields.append('Project must be queued before starting')
    
    # Check if transition is valid
    valid = len(missing_fields) == 0
    
    if valid:
        message = f'Status transition to {new_status} is valid'
    else:
        message = f'Cannot transition to {new_status}: missing required fields'
    
    return {
        'valid': valid,
        'message': message,
        'missing_fields': missing_fields,
        'warnings': warnings
    }


def get_projects_expiring_soon(days: int = 7) -> List[Project]:
    """
    Get list of projects with quotes expiring within specified days.
    
    Args:
        days (int): Number of days to look ahead (default: 7)
    
    Returns:
        list: List of Project objects with quotes expiring soon
    """
    expiry_threshold = date.today() + timedelta(days=days)
    
    return Project.query.filter(
        Project.status == Project.STATUS_QUOTE_APPROVAL,
        Project.pop_received == False,
        Project.quote_expiry_date.isnot(None),
        Project.quote_expiry_date >= date.today(),
        Project.quote_expiry_date <= expiry_threshold
    ).order_by(Project.quote_expiry_date).all()


def get_expired_quotes() -> List[Project]:
    """
    Get list of projects with expired quotes that haven't been auto-cancelled yet.
    
    Returns:
        list: List of Project objects with expired quotes
    """
    return Project.query.filter(
        Project.status == Project.STATUS_QUOTE_APPROVAL,
        Project.pop_received == False,
        Project.quote_expiry_date < date.today()
    ).order_by(Project.quote_expiry_date).all()

