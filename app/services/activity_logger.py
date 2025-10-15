"""
Laser OS Tier 1 - Activity Logger Service

This module provides functions to log activities for audit trail.
"""

import json
from flask import request
from app import db
from app.models import ActivityLog


def log_activity(entity_type, entity_id, action, details=None, user='admin'):
    """
    Log an activity to the audit trail.
    
    Args:
        entity_type (str): Type of entity (CLIENT, PROJECT, FILE, etc.)
        entity_id (int): ID of the entity
        action (str): Action performed (CREATED, UPDATED, DELETED, etc.)
        details (dict, optional): Additional details as dictionary
        user (str, optional): Username who performed the action. Defaults to 'admin'.
    
    Returns:
        ActivityLog: The created activity log entry
    
    Example:
        >>> log_activity('CLIENT', 1, 'CREATED', {'name': 'ACME Corp'})
        <ActivityLog CLIENT:1 CREATED>
    """
    # Get IP address from request context if available
    ip_address = None
    try:
        if request:
            ip_address = request.remote_addr
    except RuntimeError:
        # Outside request context
        pass
    
    # Convert details dict to JSON string
    details_json = None
    if details:
        try:
            details_json = json.dumps(details)
        except (TypeError, ValueError):
            details_json = str(details)
    
    # Create activity log entry
    activity = ActivityLog(
        entity_type=entity_type.upper(),
        entity_id=entity_id,
        action=action.upper(),
        user=user,
        details=details_json,
        ip_address=ip_address
    )
    
    db.session.add(activity)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log the error but don't fail the main operation
        print(f'Error logging activity: {e}')
    
    return activity


def get_entity_activities(entity_type, entity_id, limit=50):
    """
    Get activity log entries for a specific entity.
    
    Args:
        entity_type (str): Type of entity
        entity_id (int): ID of the entity
        limit (int, optional): Maximum number of entries to return. Defaults to 50.
    
    Returns:
        list: List of ActivityLog objects
    
    Example:
        >>> activities = get_entity_activities('CLIENT', 1)
        >>> for activity in activities:
        ...     print(activity.action, activity.created_at)
    """
    return ActivityLog.query.filter_by(
        entity_type=entity_type.upper(),
        entity_id=entity_id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()


def get_recent_activities(limit=100):
    """
    Get recent activity log entries across all entities.
    
    Args:
        limit (int, optional): Maximum number of entries to return. Defaults to 100.
    
    Returns:
        list: List of ActivityLog objects
    
    Example:
        >>> activities = get_recent_activities(20)
        >>> for activity in activities:
        ...     print(f'{activity.entity_type} {activity.action}')
    """
    return ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(limit).all()


def get_user_activities(user, limit=50):
    """
    Get activity log entries for a specific user.

    Args:
        user (str): Username
        limit (int, optional): Maximum number of entries to return. Defaults to 50.

    Returns:
        list: List of ActivityLog objects

    Example:
        >>> activities = get_user_activities('admin')
        >>> print(f'User has {len(activities)} activities')
    """
    return ActivityLog.query.filter_by(
        user=user
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()


# ============================================================================
# Phase 9: Enhanced Activity Logging Functions
# ============================================================================

def log_pop_status_change(project_id, pop_received, pop_received_date=None, user='admin'):
    """
    Log a change to POP (Proof of Payment) status.

    Args:
        project_id (int): Project ID
        pop_received (bool): New POP received status
        pop_received_date (date, optional): Date POP was received
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_pop_status_change(1, True, date.today())
    """
    action = 'POP_RECEIVED' if pop_received else 'POP_CLEARED'
    details = {
        'pop_received': pop_received,
        'pop_received_date': pop_received_date.isoformat() if pop_received_date else None
    }

    return log_activity('PROJECT', project_id, action, details, user)


def log_notification_status_change(project_id, client_notified, notification_date=None, user='admin'):
    """
    Log a change to client notification status.

    Args:
        project_id (int): Project ID
        client_notified (bool): New notification status
        notification_date (date, optional): Date client was notified
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_notification_status_change(1, True, date.today())
    """
    action = 'CLIENT_NOTIFIED' if client_notified else 'NOTIFICATION_CLEARED'
    details = {
        'client_notified': client_notified,
        'notification_date': notification_date.isoformat() if notification_date else None
    }

    return log_activity('PROJECT', project_id, action, details, user)


def log_delivery_status_change(project_id, delivery_confirmed, delivery_date=None, user='admin'):
    """
    Log a change to delivery confirmation status.

    Args:
        project_id (int): Project ID
        delivery_confirmed (bool): New delivery status
        delivery_date (date, optional): Date delivery was confirmed
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_delivery_status_change(1, True, date.today())
    """
    action = 'DELIVERY_CONFIRMED' if delivery_confirmed else 'DELIVERY_CLEARED'
    details = {
        'delivery_confirmed': delivery_confirmed,
        'delivery_date': delivery_date.isoformat() if delivery_date else None
    }

    return log_activity('PROJECT', project_id, action, details, user)


def log_communication_link(communication_id, client_id=None, project_id=None, user='admin'):
    """
    Log linking a communication to a client/project.

    Args:
        communication_id (int): Communication ID
        client_id (int, optional): Client ID
        project_id (int, optional): Project ID
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_communication_link(5, client_id=1, project_id=3)
    """
    details = {
        'client_id': client_id,
        'project_id': project_id
    }

    return log_activity('COMMUNICATION', communication_id, 'LINKED', details, user)


def log_communication_unlink(communication_id, user='admin'):
    """
    Log unlinking a communication from client/project.

    Args:
        communication_id (int): Communication ID
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_communication_unlink(5)
    """
    return log_activity('COMMUNICATION', communication_id, 'UNLINKED', {}, user)


def log_material_update(project_id, material_type, material_quantity=None, user='admin'):
    """
    Log an update to project material information.

    Args:
        project_id (int): Project ID
        material_type (str): Material type
        material_quantity (int, optional): Material quantity in sheets
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_material_update(1, 'Mild Steel', 5)
    """
    details = {
        'material_type': material_type,
        'material_quantity_sheets': material_quantity
    }

    return log_activity('PROJECT', project_id, 'MATERIAL_UPDATED', details, user)


def log_scheduling_update(project_id, scheduled_cut_date, estimated_cut_time=None, user='admin'):
    """
    Log an update to project scheduling information.

    Args:
        project_id (int): Project ID
        scheduled_cut_date (date): Scheduled cut date
        estimated_cut_time (int, optional): Estimated cut time in minutes
        user (str, optional): Username who made the change

    Returns:
        ActivityLog: The created activity log entry

    Example:
        >>> log_scheduling_update(1, date(2024, 1, 15), 120)
    """
    details = {
        'scheduled_cut_date': scheduled_cut_date.isoformat() if scheduled_cut_date else None,
        'estimated_cut_time': estimated_cut_time
    }

    return log_activity('PROJECT', project_id, 'SCHEDULING_UPDATED', details, user)

