"""
Laser OS - Auto-Scheduling Service

This module provides automatic queue scheduling logic for Phase 10 automation.
"""

from app import db
from app.models import Project, QueueItem, ActivityLog
from app.services.inventory_service import check_project_inventory_availability, reserve_inventory
from datetime import date, datetime, timedelta
from typing import Dict, Optional


def check_auto_schedule_conditions(project: Project) -> Dict:
    """
    Check if a project meets all conditions for auto-scheduling.
    
    Conditions:
    1. POP received
    2. All Material & Production fields filled
    3. Inventory available
    
    Args:
        project: Project instance
    
    Returns:
        Dictionary with:
            - eligible: bool - Whether project can be auto-scheduled
            - reasons: list - List of reasons why not eligible (if applicable)
            - inventory_check: dict - Inventory availability check result
    """
    reasons = []
    
    # Condition 1: POP received
    if not project.pop_received:
        reasons.append('POP not received')
    
    # Condition 2: Material & Production fields filled
    missing_fields = []
    if not project.material_type:
        missing_fields.append('material_type')
    if not project.material_thickness:
        missing_fields.append('material_thickness')
    if not project.material_quantity_sheets:
        missing_fields.append('material_quantity_sheets')
    if not project.parts_quantity:
        missing_fields.append('parts_quantity')
    if not project.estimated_cut_time:
        missing_fields.append('estimated_cut_time')
    
    if missing_fields:
        reasons.append(f'Missing fields: {", ".join(missing_fields)}')
    
    # Condition 3: Inventory available
    inventory_check = check_project_inventory_availability(project)
    if not inventory_check['available']:
        reasons.append(inventory_check['message'])
    
    return {
        'eligible': len(reasons) == 0,
        'reasons': reasons,
        'inventory_check': inventory_check
    }


def get_next_business_day(from_date: date = None) -> date:
    """
    Get the next business day (Monday-Friday).
    
    Args:
        from_date: Starting date (default: today)
    
    Returns:
        Next business day
    """
    if from_date is None:
        from_date = date.today()
    
    next_day = from_date
    
    # If it's Friday (4), Saturday (5), or Sunday (6), move to Monday
    if next_day.weekday() >= 4:  # Friday or later
        days_to_add = 7 - next_day.weekday()  # Days until Monday
        next_day = next_day + timedelta(days=days_to_add)
    
    return next_day


def auto_schedule_project(project: Project, performed_by: str = 'System (Auto)') -> Dict:
    """
    Automatically schedule a project for cutting if conditions are met.
    
    Args:
        project: Project instance
        performed_by: User who triggered the action
    
    Returns:
        Dictionary with:
            - scheduled: bool - Whether project was scheduled
            - message: str - Result message
            - queue_item: QueueItem or None - Created queue item (if scheduled)
            - reasons: list - Reasons why not scheduled (if applicable)
    """
    # Check if already in queue
    existing_queue_item = QueueItem.query.filter_by(
        project_id=project.id,
        status=QueueItem.STATUS_QUEUED
    ).first()
    
    if existing_queue_item:
        return {
            'scheduled': False,
            'message': f'Project already in queue at position {existing_queue_item.queue_position}',
            'queue_item': existing_queue_item,
            'reasons': ['Already in queue']
        }
    
    # Check auto-schedule conditions
    conditions = check_auto_schedule_conditions(project)
    
    if not conditions['eligible']:
        return {
            'scheduled': False,
            'message': 'Project not eligible for auto-scheduling',
            'queue_item': None,
            'reasons': conditions['reasons']
        }
    
    try:
        # Get next queue position
        max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
        next_position = max_position + 1
        
        # Determine scheduled date (today or next business day)
        scheduled_date = get_next_business_day(date.today())
        
        # Create queue item with sensible defaults
        queue_item = QueueItem(
            project_id=project.id,
            queue_position=next_position,
            status=QueueItem.STATUS_QUEUED,
            priority=QueueItem.PRIORITY_NORMAL,
            scheduled_date=scheduled_date,
            estimated_cut_time=project.estimated_cut_time,
            notes='Automatically scheduled: POP received + inventory available',
            added_by=performed_by
        )
        
        db.session.add(queue_item)
        db.session.flush()  # Get the queue_item.id
        
        # Reserve inventory
        inventory_item = conditions['inventory_check']['inventory_item']
        if inventory_item:
            reserve_success = reserve_inventory(
                inventory_item=inventory_item,
                quantity=float(project.material_quantity_sheets),
                reference_type='QUEUE_ITEM',
                reference_id=queue_item.id,
                performed_by=performed_by,
                notes=f'Reserved for project {project.project_code} (auto-scheduled)'
            )
            
            if not reserve_success:
                db.session.rollback()
                return {
                    'scheduled': False,
                    'message': 'Failed to reserve inventory',
                    'queue_item': None,
                    'reasons': ['Inventory reservation failed']
                }
        
        # Log activity
        activity = ActivityLog(
            entity_type='QUEUE',
            entity_id=queue_item.id,
            action='ADDED',
            details=f'Auto-scheduled project {project.project_code} at position {next_position} (POP received + inventory available)',
            user=performed_by
        )
        db.session.add(activity)
        db.session.commit()
        
        return {
            'scheduled': True,
            'message': f'Project auto-scheduled at position {next_position} for {scheduled_date}',
            'queue_item': queue_item,
            'reasons': []
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'scheduled': False,
            'message': f'Error auto-scheduling: {str(e)}',
            'queue_item': None,
            'reasons': [f'Exception: {str(e)}']
        }


def check_and_schedule_project(project: Project, performed_by: str = 'System (Auto)') -> Dict:
    """
    Check if project should be auto-scheduled and schedule if eligible.
    
    This is a convenience function that combines checking and scheduling.
    
    Args:
        project: Project instance
        performed_by: User who triggered the action
    
    Returns:
        Dictionary with scheduling result
    """
    return auto_schedule_project(project, performed_by)


def get_auto_schedule_status(project: Project) -> Dict:
    """
    Get the auto-schedule status for a project without actually scheduling it.
    
    Args:
        project: Project instance
    
    Returns:
        Dictionary with status information
    """
    conditions = check_auto_schedule_conditions(project)
    
    if conditions['eligible']:
        return {
            'can_schedule': True,
            'message': 'Project is ready for auto-scheduling',
            'reasons': []
        }
    else:
        return {
            'can_schedule': False,
            'message': 'Project not ready for auto-scheduling',
            'reasons': conditions['reasons']
        }

