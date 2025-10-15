"""
Scheduling Validator Service for Laser OS.

This service validates scheduling decisions based on business rules,
particularly the POP (Proof of Payment) deadline requirements.

Phase 9 Implementation.
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from flask import current_app

from app.models import Project, QueueItem


def validate_pop_deadline(project: Project, scheduled_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Validate if a project can be scheduled based on POP deadline rules.
    
    Business Rule: Projects must be scheduled within 3 days of POP receipt.
    
    Args:
        project: Project instance to validate
        scheduled_date: Proposed scheduled date (defaults to today)
    
    Returns:
        dict: Validation result with 'valid', 'message', 'deadline', 'days_remaining'
    
    Example:
        >>> result = validate_pop_deadline(project, date(2024, 1, 15))
        >>> if not result['valid']:
        ...     print(f"Cannot schedule: {result['message']}")
    """
    # Default to today if no date provided
    if scheduled_date is None:
        scheduled_date = date.today()
    
    # Check if project has POP received
    if not project.pop_received:
        return {
            'valid': False,
            'message': 'Cannot schedule: Proof of Payment (POP) not yet received',
            'deadline': None,
            'days_remaining': None,
            'severity': 'error'
        }
    
    # Check if POP deadline exists
    if not project.pop_deadline:
        return {
            'valid': False,
            'message': 'Cannot schedule: POP deadline not calculated',
            'deadline': None,
            'days_remaining': None,
            'severity': 'error'
        }
    
    # Calculate days until deadline
    days_until_deadline = (project.pop_deadline - scheduled_date).days
    
    # Check if scheduled date is past the deadline
    if scheduled_date > project.pop_deadline:
        days_overdue = (scheduled_date - project.pop_deadline).days
        return {
            'valid': False,
            'message': f'Cannot schedule: Proposed date is {days_overdue} days past POP deadline ({project.pop_deadline.strftime("%Y-%m-%d")})',
            'deadline': project.pop_deadline,
            'days_remaining': days_until_deadline,
            'days_overdue': days_overdue,
            'severity': 'error'
        }
    
    # Check if deadline is today (warning)
    if days_until_deadline == 0:
        return {
            'valid': True,
            'message': f'Warning: POP deadline is today ({project.pop_deadline.strftime("%Y-%m-%d")}). Schedule immediately.',
            'deadline': project.pop_deadline,
            'days_remaining': 0,
            'severity': 'warning'
        }
    
    # Check if deadline is within 1 day (warning)
    if days_until_deadline == 1:
        return {
            'valid': True,
            'message': f'Warning: POP deadline is tomorrow ({project.pop_deadline.strftime("%Y-%m-%d")}). Schedule soon.',
            'deadline': project.pop_deadline,
            'days_remaining': 1,
            'severity': 'warning'
        }
    
    # All good
    return {
        'valid': True,
        'message': f'OK: {days_until_deadline} days remaining until POP deadline ({project.pop_deadline.strftime("%Y-%m-%d")})',
        'deadline': project.pop_deadline,
        'days_remaining': days_until_deadline,
        'severity': 'info'
    }


def check_overdue_projects() -> List[Dict[str, Any]]:
    """
    Check for projects with overdue POP deadlines.
    
    Returns:
        list: List of dictionaries with project info and overdue details
    
    Example:
        >>> overdue = check_overdue_projects()
        >>> for item in overdue:
        ...     print(f"{item['project_code']}: {item['days_overdue']} days overdue")
    """
    today = date.today()
    overdue_projects = []
    
    # Find all projects with POP received but deadline passed
    projects = Project.query.filter(
        Project.pop_received == True,
        Project.pop_deadline < today
    ).all()
    
    for project in projects:
        days_overdue = (today - project.pop_deadline).days
        
        overdue_projects.append({
            'project_id': project.id,
            'project_code': project.project_code,
            'project_name': project.name,
            'client_id': project.client_id,
            'client_name': project.client.name if project.client else None,
            'pop_received_date': project.pop_received_date,
            'pop_deadline': project.pop_deadline,
            'days_overdue': days_overdue,
            'status': project.status,
            'scheduled_cut_date': project.scheduled_cut_date
        })
    
    # Sort by days overdue (most overdue first)
    overdue_projects.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    return overdue_projects


def check_upcoming_deadlines(days_ahead: int = 3) -> List[Dict[str, Any]]:
    """
    Check for projects with POP deadlines approaching in the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 3)
    
    Returns:
        list: List of dictionaries with project info and deadline details
    
    Example:
        >>> upcoming = check_upcoming_deadlines(days_ahead=2)
        >>> for item in upcoming:
        ...     print(f"{item['project_code']}: {item['days_remaining']} days remaining")
    """
    today = date.today()
    future_date = today + timedelta(days=days_ahead)
    upcoming_projects = []
    
    # Find all projects with POP received and deadline within range
    projects = Project.query.filter(
        Project.pop_received == True,
        Project.pop_deadline >= today,
        Project.pop_deadline <= future_date
    ).all()
    
    for project in projects:
        days_remaining = (project.pop_deadline - today).days
        
        upcoming_projects.append({
            'project_id': project.id,
            'project_code': project.project_code,
            'project_name': project.name,
            'client_id': project.client_id,
            'client_name': project.client.name if project.client else None,
            'pop_received_date': project.pop_received_date,
            'pop_deadline': project.pop_deadline,
            'days_remaining': days_remaining,
            'status': project.status,
            'scheduled_cut_date': project.scheduled_cut_date
        })
    
    # Sort by days remaining (most urgent first)
    upcoming_projects.sort(key=lambda x: x['days_remaining'])
    
    return upcoming_projects


def validate_queue_capacity(
    scheduled_date: date,
    estimated_time_minutes: int,
    max_hours_per_day: int = 8
) -> Dict[str, Any]:
    """
    Validate if there's capacity to schedule a job on a given date.
    
    Args:
        scheduled_date: Date to check capacity for
        estimated_time_minutes: Estimated time for the new job (in minutes)
        max_hours_per_day: Maximum working hours per day (default: 8)
    
    Returns:
        dict: Validation result with 'valid', 'message', 'capacity_used', 'capacity_available'
    
    Example:
        >>> result = validate_queue_capacity(date(2024, 1, 15), 120)
        >>> if result['valid']:
        ...     print(f"Capacity available: {result['capacity_available']} minutes")
    """
    # Calculate total capacity in minutes
    total_capacity_minutes = max_hours_per_day * 60
    
    # Find all queue items scheduled for this date
    queue_items = QueueItem.query.filter(
        QueueItem.scheduled_date == scheduled_date,
        QueueItem.is_active == True
    ).all()
    
    # Calculate used capacity
    used_capacity_minutes = sum(item.estimated_cut_time or 0 for item in queue_items)
    
    # Calculate available capacity
    available_capacity_minutes = total_capacity_minutes - used_capacity_minutes
    
    # Check if there's enough capacity
    if estimated_time_minutes > available_capacity_minutes:
        return {
            'valid': False,
            'message': f'Insufficient capacity: {available_capacity_minutes} minutes available, {estimated_time_minutes} minutes required',
            'capacity_total': total_capacity_minutes,
            'capacity_used': used_capacity_minutes,
            'capacity_available': available_capacity_minutes,
            'capacity_required': estimated_time_minutes,
            'severity': 'error'
        }
    
    # Calculate utilization percentage
    utilization_after = ((used_capacity_minutes + estimated_time_minutes) / total_capacity_minutes) * 100
    
    # Warning if utilization will be high
    if utilization_after > 90:
        return {
            'valid': True,
            'message': f'Warning: High utilization ({utilization_after:.1f}%) after scheduling',
            'capacity_total': total_capacity_minutes,
            'capacity_used': used_capacity_minutes,
            'capacity_available': available_capacity_minutes,
            'capacity_required': estimated_time_minutes,
            'utilization_after': utilization_after,
            'severity': 'warning'
        }
    
    return {
        'valid': True,
        'message': f'OK: {available_capacity_minutes - estimated_time_minutes} minutes remaining after scheduling',
        'capacity_total': total_capacity_minutes,
        'capacity_used': used_capacity_minutes,
        'capacity_available': available_capacity_minutes,
        'capacity_required': estimated_time_minutes,
        'utilization_after': utilization_after,
        'severity': 'info'
    }


def validate_scheduling(
    project: Project,
    scheduled_date: Optional[date] = None,
    estimated_time_minutes: Optional[int] = None
) -> Dict[str, Any]:
    """
    Comprehensive scheduling validation combining all rules.
    
    Args:
        project: Project to schedule
        scheduled_date: Proposed scheduled date (defaults to today)
        estimated_time_minutes: Estimated time (defaults to project.estimated_cut_time)
    
    Returns:
        dict: Combined validation result with all checks
    
    Example:
        >>> result = validate_scheduling(project, date(2024, 1, 15))
        >>> if not result['valid']:
        ...     for error in result['errors']:
        ...         print(f"Error: {error}")
    """
    if scheduled_date is None:
        scheduled_date = date.today()
    
    if estimated_time_minutes is None:
        estimated_time_minutes = project.estimated_cut_time or 60  # Default 1 hour
    
    errors = []
    warnings = []
    
    # Check POP deadline
    pop_result = validate_pop_deadline(project, scheduled_date)
    if not pop_result['valid']:
        errors.append(pop_result['message'])
    elif pop_result['severity'] == 'warning':
        warnings.append(pop_result['message'])
    
    # Check capacity
    capacity_result = validate_queue_capacity(scheduled_date, estimated_time_minutes)
    if not capacity_result['valid']:
        errors.append(capacity_result['message'])
    elif capacity_result['severity'] == 'warning':
        warnings.append(capacity_result['message'])
    
    # Determine overall validity
    valid = len(errors) == 0
    
    return {
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'pop_validation': pop_result,
        'capacity_validation': capacity_result,
        'scheduled_date': scheduled_date,
        'estimated_time_minutes': estimated_time_minutes
    }

