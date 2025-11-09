"""
Notifications Routes for Laser OS Production Automation.

This module provides routes for the bell icon notification system including:
- List all notifications
- Mark notification as resolved
- Get notification count (for badge)
- Notification dropdown partial
"""

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.business import Notification
from app.services.notification_logic import (
    get_unresolved_notifications,
    get_notification_count,
    mark_notification_resolved
)
from app.security.decorators import require_any_role

bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@bp.route('/')
@login_required
@require_any_role('admin', 'manager')
def list_notifications():
    """
    List all notifications page.
    
    Shows:
    - Unresolved notifications (active)
    - Recently resolved notifications
    - Filter by type
    """
    # Get filter parameters
    show_resolved = request.args.get('show_resolved', 'false') == 'true'
    notif_type = request.args.get('type', None)
    
    # Build query
    query = Notification.query
    
    if not show_resolved:
        query = query.filter_by(resolved=False)
    
    if notif_type:
        query = query.filter_by(notif_type=notif_type)
    
    notifications = query.order_by(
        Notification.resolved.asc(),  # Unresolved first
        Notification.created_at.desc()
    ).limit(100).all()
    
    # Get notification type counts
    type_counts = {}
    for notif in notifications:
        type_counts[notif.notif_type] = type_counts.get(notif.notif_type, 0) + 1
    
    return render_template('notifications/list.html',
                         notifications=notifications,
                         show_resolved=show_resolved,
                         selected_type=notif_type,
                         type_counts=type_counts)


@bp.route('/<int:notification_id>/resolve', methods=['POST'])
@login_required
@require_any_role('admin', 'manager')
def resolve_notification(notification_id):
    """
    Mark a notification as resolved.
    
    Args:
        notification_id (int): Notification ID
    """
    success = mark_notification_resolved(notification_id)
    
    if success:
        flash('Notification marked as resolved.', 'success')
    else:
        flash('Notification not found.', 'error')
    
    # Redirect back to referrer or notifications list
    return redirect(request.referrer or url_for('notifications.list_notifications'))


@bp.route('/count')
@login_required
def notification_count():
    """
    Get count of unresolved notifications (for badge).
    
    Returns:
        JSON: {'count': int}
    """
    count = get_notification_count()
    return jsonify({'count': count})


@bp.route('/dropdown')
@login_required
def notification_dropdown():
    """
    Get notification dropdown HTML (for bell icon).
    
    Returns:
        HTML: Partial template for dropdown
    """
    notifications = get_unresolved_notifications(limit=10)
    count = get_notification_count()
    
    return render_template('partials/bell_dropdown.html',
                         notifications=notifications,
                         count=count)


@bp.route('/mark-all-read', methods=['POST'])
@login_required
@require_any_role('admin', 'manager')
def mark_all_read():
    """
    Mark all unresolved notifications as resolved.
    """
    notifications = Notification.query.filter_by(resolved=False).all()
    
    for notif in notifications:
        mark_notification_resolved(notif.id)
    
    flash(f'Marked {len(notifications)} notifications as resolved.', 'success')
    return redirect(url_for('notifications.list_notifications'))

