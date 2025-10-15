"""
Laser OS Tier 1 - Main Routes

This module defines the main routes including the dashboard.
"""

from flask import Blueprint, render_template
from app.models import Client, Project, Product, DesignFile, QueueItem, LaserRun, InventoryItem

bp = Blueprint('main', __name__)


@bp.route('/')
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

    # Get recent files
    recent_files = DesignFile.query.order_by(
        DesignFile.upload_date.desc()
    ).limit(5).all()

    # Get queue items
    queue_items = QueueItem.query.filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).order_by(QueueItem.queue_position).limit(5).all()

    # Get inventory statistics
    inventory_count = InventoryItem.query.count()
    low_stock_count = len([item for item in InventoryItem.query.all() if item.is_low_stock])

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

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_clients=recent_clients,
        recent_projects=recent_projects,
        recent_products=recent_products,
        recent_files=recent_files,
        queue_items=queue_items
    )

