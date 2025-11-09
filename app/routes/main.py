"""
Laser OS Tier 1 - Main Routes

This module defines the main routes including the dashboard.
"""

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy.orm import joinedload
from app.models import Client, Project, Product, DesignFile, QueueItem, LaserRun, InventoryItem, Notification

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def dashboard():
    """
    Display the main dashboard.

    Returns:
        Rendered dashboard template with statistics
    """
    # Get basic statistics
    total_clients = Client.query.count()
    total_projects = Project.query.count()
    active_projects = Project.query.filter(
        Project.status.in_([Project.STATUS_APPROVED, Project.STATUS_IN_PROGRESS])
    ).count()
    total_products = Product.query.count()
    total_files = DesignFile.query.count()
    queue_length = QueueItem.query.filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).count()

    # Get recent clients
    recent_clients = Client.query.order_by(
        Client.created_at.desc()
    ).limit(5).all()

    # Get recent projects
    recent_projects = Project.query.order_by(
        Project.created_at.desc()
    ).limit(5).all()

    # Get recent products
    recent_products = Product.query.order_by(
        Product.created_at.desc()
    ).limit(5).all()

    # Get recent files with eager loading to avoid N+1 queries
    # Template accesses file.project.project_code, so we load the project relationship
    recent_files = DesignFile.query.options(
        joinedload(DesignFile.project)
    ).order_by(
        DesignFile.upload_date.desc()
    ).limit(5).all()

    # Get queue items with eager loading to avoid N+1 queries
    # Template accesses item.project.project_code, so we load the project relationship
    queue_items = QueueItem.query.options(
        joinedload(QueueItem.project)
    ).filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).order_by(QueueItem.queue_position).limit(5).all()

    # Get inventory statistics
    # Optimized: Use database query instead of loading all items into memory
    inventory_count = InventoryItem.query.count()
    low_stock_count = InventoryItem.query.filter(
        InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
    ).count()

    # Production Automation: Get attention items (unresolved notifications)
    # Group notifications by type for attention cards
    low_stock_notifications = Notification.query.filter_by(
        resolved=False,
        notif_type='low_stock'
    ).count()

    approval_wait_notifications = Notification.query.filter_by(
        resolved=False,
        notif_type='approval_wait'
    ).count()

    pickup_wait_notifications = Notification.query.filter_by(
        resolved=False,
        notif_type='pickup_wait'
    ).count()

    material_block_notifications = Notification.query.filter_by(
        resolved=False,
        notif_type='material_block'
    ).count()

    # More statistics will be added in later phases
    stats = {
        'total_clients': total_clients,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_products': total_products,
        'total_files': total_files,
        'queue_length': queue_length,
        'inventory_count': inventory_count,
        'low_stock_count': low_stock_count,
    }

    # Attention cards data (Production Automation)
    attention_cards = {
        'low_stock': low_stock_notifications,
        'approval_wait': approval_wait_notifications,
        'pickup_wait': pickup_wait_notifications,
        'material_block': material_block_notifications,
    }

    return render_template(
        'dashboard.html',
        stats=stats,
        attention_cards=attention_cards,
        recent_clients=recent_clients,
        recent_projects=recent_projects,
        recent_products=recent_products,
        recent_files=recent_files,
        queue_items=queue_items
    )

