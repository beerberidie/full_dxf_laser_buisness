"""
Notification Logic Service for Laser OS Production Automation.

This module handles notification creation, evaluation, and auto-clearing logic including:
- Stage escalation timing (QuotesAndApproval > 4 days, WaitingOnMaterial > 2 days, etc.)
- Low stock notifications
- Missing preset notifications
- Auto-clear when conditions resolve
- Draft client message generation
"""

from datetime import datetime, timedelta
from app import db
from app.models.business import Notification, Project, InventoryItem, OutboundDraft


# Stage escalation time limits
STAGE_LIMITS = {
    'QuotesAndApproval': timedelta(days=4),
    'WaitingOnMaterial': timedelta(days=2),
    'Cutting': timedelta(days=1),
    'ReadyForPickup': timedelta(days=2),
}

# Notification type constants
NOTIF_APPROVAL_WAIT = 'approval_wait'
NOTIF_MATERIAL_BLOCK = 'material_block'
NOTIF_CUTTING_STALL = 'cutting_stall'
NOTIF_PICKUP_WAIT = 'pickup_wait'
NOTIF_LOW_STOCK = 'low_stock'
NOTIF_PRESET_MISSING = 'preset_missing'


def evaluate_notifications_for_project(project_id):
    """
    Evaluate and update notifications for a project.
    
    Steps:
    1. Clear any resolved notifications for this project
    2. Check if project stage has exceeded time limit
    3. Create new notification if overdue
    4. Generate draft outbound message if client-facing
    
    Args:
        project_id (int): Project ID to evaluate
    """
    project = Project.query.get(project_id)
    if not project:
        return
    
    # Step 1: Auto-clear resolved notifications
    auto_clear_resolved_notifications(project)
    
    # Step 2: Check stage timing
    if project.stage in STAGE_LIMITS:
        time_limit = STAGE_LIMITS[project.stage]
        time_in_stage = datetime.utcnow() - project.stage_last_updated
        
        if time_in_stage > time_limit:
            # Stage is overdue - create notification if not already exists
            create_stage_escalation_notification(project)


def auto_clear_resolved_notifications(project):
    """
    Auto-clear notifications that are no longer relevant.
    
    For example:
    - approval_wait notification when project moves past QuotesAndApproval stage
    - material_block notification when project moves past WaitingOnMaterial stage
    
    Args:
        project (Project): Project to check
    """
    # Get all unresolved notifications for this project
    notifications = Notification.query.filter_by(
        project_id=project.id,
        resolved=False
    ).all()
    
    for notif in notifications:
        should_clear = False
        
        # Check if notification is no longer relevant
        if notif.notif_type == NOTIF_APPROVAL_WAIT and project.stage != Project.STAGE_QUOTES_APPROVAL:
            should_clear = True
        elif notif.notif_type == NOTIF_MATERIAL_BLOCK and project.stage != Project.STAGE_WAITING_MATERIAL:
            should_clear = True
        elif notif.notif_type == NOTIF_CUTTING_STALL and project.stage != Project.STAGE_CUTTING:
            should_clear = True
        elif notif.notif_type == NOTIF_PICKUP_WAIT and project.stage != Project.STAGE_READY_PICKUP:
            should_clear = True
        
        if should_clear:
            notif.resolved = True
            notif.auto_cleared = True
            notif.resolved_at = datetime.utcnow()
            db.session.add(notif)
    
    db.session.commit()


def create_stage_escalation_notification(project):
    """
    Create a stage escalation notification for an overdue project.
    
    Also generates a draft outbound message for client-facing stages.
    
    Args:
        project (Project): Project that is overdue
    """
    # Check if notification already exists
    existing = Notification.query.filter_by(
        project_id=project.id,
        notif_type=get_notification_type_for_stage(project.stage),
        resolved=False
    ).first()
    
    if existing:
        # Notification already exists, don't create duplicate
        return
    
    # Determine notification type and message
    notif_type = get_notification_type_for_stage(project.stage)
    message = generate_notification_message(project)
    
    # Create notification
    notification = Notification(
        project_id=project.id,
        notif_type=notif_type,
        message=message,
        resolved=False,
        auto_cleared=False
    )
    
    db.session.add(notification)
    db.session.commit()
    
    # Generate draft client message for client-facing stages
    if project.stage in [Project.STAGE_QUOTES_APPROVAL, Project.STAGE_READY_PICKUP]:
        generate_draft_client_message(project)


def get_notification_type_for_stage(stage):
    """
    Get notification type for a given stage.
    
    Args:
        stage (str): Project stage
        
    Returns:
        str: Notification type constant
    """
    stage_to_notif = {
        Project.STAGE_QUOTES_APPROVAL: NOTIF_APPROVAL_WAIT,
        Project.STAGE_WAITING_MATERIAL: NOTIF_MATERIAL_BLOCK,
        Project.STAGE_CUTTING: NOTIF_CUTTING_STALL,
        Project.STAGE_READY_PICKUP: NOTIF_PICKUP_WAIT,
    }
    return stage_to_notif.get(stage, 'unknown')


def generate_notification_message(project):
    """
    Generate notification message text for a project.
    
    Args:
        project (Project): Project
        
    Returns:
        str: Notification message
    """
    days_in_stage = (datetime.utcnow() - project.stage_last_updated).days
    
    messages = {
        Project.STAGE_QUOTES_APPROVAL: f"Project {project.project_code} waiting for approval for {days_in_stage} days (limit: 4 days)",
        Project.STAGE_WAITING_MATERIAL: f"Project {project.project_code} blocked by material for {days_in_stage} days (limit: 2 days)",
        Project.STAGE_CUTTING: f"Project {project.project_code} in cutting stage for {days_in_stage} days (limit: 1 day) - possible stall",
        Project.STAGE_READY_PICKUP: f"Project {project.project_code} ready for pickup for {days_in_stage} days (limit: 2 days)",
    }
    
    return messages.get(project.stage, f"Project {project.project_code} requires attention")


def generate_draft_client_message(project):
    """
    Generate a draft outbound message for client follow-up.
    
    Args:
        project (Project): Project requiring client communication
    """
    # Check if draft already exists
    existing = OutboundDraft.query.filter_by(
        project_id=project.id,
        sent=False
    ).first()
    
    if existing:
        # Draft already exists
        return
    
    # Generate message body based on stage
    if project.stage == Project.STAGE_QUOTES_APPROVAL:
        body_text = (
            f"Hi {project.client.contact_person or project.client.name},\n\n"
            f"Following up on quote for project {project.project_code} - {project.name}.\n\n"
            f"We sent the quote on {project.quote_date.strftime('%Y-%m-%d') if project.quote_date else 'recently'}. "
            f"Please let us know if you have any questions or would like to proceed.\n\n"
            f"Best regards,\nLaser OS Team"
        )
        channel_hint = 'whatsapp'
    elif project.stage == Project.STAGE_READY_PICKUP:
        body_text = (
            f"Hi {project.client.contact_person or project.client.name},\n\n"
            f"Your project {project.project_code} - {project.name} is ready for pickup!\n\n"
            f"Please let us know when you'd like to collect it.\n\n"
            f"Best regards,\nLaser OS Team"
        )
        channel_hint = 'whatsapp'
    else:
        return  # No draft for other stages
    
    # Create draft
    draft = OutboundDraft(
        project_id=project.id,
        client_id=project.client_id,
        channel_hint=channel_hint,
        body_text=body_text,
        sent=False
    )
    
    db.session.add(draft)
    db.session.commit()


def create_low_stock_notification(inventory_item):
    """
    Create a low stock notification for an inventory item.
    
    Args:
        inventory_item (InventoryItem): Inventory item below reorder level
    """
    # Check if notification already exists
    existing = Notification.query.filter_by(
        inventory_item_id=inventory_item.id,
        notif_type=NOTIF_LOW_STOCK,
        resolved=False
    ).first()
    
    if existing:
        # Notification already exists
        return
    
    # Create notification
    message = (
        f"Low stock: {inventory_item.name} - "
        f"Current: {int(inventory_item.quantity_on_hand)} sheets, "
        f"Minimum: {int(inventory_item.reorder_level)} sheets"
    )
    
    notification = Notification(
        inventory_item_id=inventory_item.id,
        notif_type=NOTIF_LOW_STOCK,
        message=message,
        resolved=False,
        auto_cleared=False
    )
    
    db.session.add(notification)
    db.session.commit()


def get_unresolved_notifications(limit=50):
    """
    Get all unresolved notifications.
    
    Args:
        limit (int): Maximum number of notifications to return
        
    Returns:
        list: List of Notification objects
    """
    return Notification.query.filter_by(
        resolved=False
    ).order_by(Notification.created_at.desc()).limit(limit).all()


def get_notification_count():
    """
    Get count of unresolved notifications.
    
    Returns:
        int: Number of unresolved notifications
    """
    return Notification.query.filter_by(resolved=False).count()


def mark_notification_resolved(notification_id):
    """
    Manually mark a notification as resolved.
    
    Args:
        notification_id (int): Notification ID
        
    Returns:
        bool: True if successful
    """
    notification = Notification.query.get(notification_id)
    if not notification:
        return False
    
    notification.resolved = True
    notification.resolved_at = datetime.utcnow()
    notification.auto_cleared = False  # Manually resolved
    
    db.session.add(notification)
    db.session.commit()
    
    return True

