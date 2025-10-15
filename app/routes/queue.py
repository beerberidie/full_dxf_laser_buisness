"""
Queue management routes for production queue and laser runs
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import QueueItem, LaserRun, Project, ActivityLog
from datetime import datetime, date

bp = Blueprint('queue', __name__, url_prefix='/queue')


@bp.route('/')
def index():
    """Display the production queue."""
    # Get filter parameters
    status_filter = request.args.get('status', 'active')
    
    # Build query
    query = QueueItem.query
    
    if status_filter == 'active':
        query = query.filter(QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS]))
    elif status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Order by queue position
    queue_items = query.order_by(QueueItem.queue_position).all()
    
    # Get statistics
    total_queued = QueueItem.query.filter_by(status=QueueItem.STATUS_QUEUED).count()
    total_in_progress = QueueItem.query.filter_by(status=QueueItem.STATUS_IN_PROGRESS).count()
    total_completed = QueueItem.query.filter_by(status=QueueItem.STATUS_COMPLETED).count()
    
    stats = {
        'total_queued': total_queued,
        'total_in_progress': total_in_progress,
        'total_completed': total_completed,
        'total_active': total_queued + total_in_progress
    }
    
    # Phase 9: Pass today's date for POP deadline calculations
    return render_template(
        'queue/index.html',
        queue_items=queue_items,
        stats=stats,
        status_filter=status_filter,
        today=date.today()
    )


@bp.route('/add/<int:project_id>', methods=['POST'])
def add_to_queue(project_id):
    """
    Add a project to the queue.

    Phase 9: Validates POP deadline before allowing scheduling.
    """
    project = Project.query.get_or_404(project_id)

    # Phase 9: Check POP deadline validation
    if project.pop_received and project.pop_deadline:
        if date.today() > project.pop_deadline:
            days_overdue = (date.today() - project.pop_deadline).days
            flash(f'⚠️ Warning: POP deadline was {days_overdue} day(s) ago ({project.pop_deadline}). '
                  f'Project should have been scheduled within 3 days of POP receipt.', 'warning')

    # Check if project is already in active queue
    existing = QueueItem.query.filter_by(
        project_id=project_id,
        status=QueueItem.STATUS_QUEUED
    ).first()

    if existing:
        flash(f'Project {project.project_code} is already in the queue', 'warning')
        return redirect(url_for('projects.detail', id=project_id))
    
    try:
        # Get next queue position
        max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
        next_position = max_position + 1
        
        # Get form data
        priority = request.form.get('priority', QueueItem.PRIORITY_NORMAL)
        scheduled_date_str = request.form.get('scheduled_date')
        estimated_cut_time = request.form.get('estimated_cut_time')
        notes = request.form.get('notes', '').strip()
        
        # Parse scheduled date
        scheduled_date = None
        if scheduled_date_str:
            try:
                scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Create queue item
        queue_item = QueueItem(
            project_id=project_id,
            queue_position=next_position,
            status=QueueItem.STATUS_QUEUED,
            priority=priority,
            scheduled_date=scheduled_date,
            estimated_cut_time=int(estimated_cut_time) if estimated_cut_time else None,
            notes=notes if notes else None,
            added_by='System'
        )
        
        db.session.add(queue_item)
        db.session.commit()
        
        # Log activity
        activity = ActivityLog(
            entity_type='QUEUE',
            entity_id=queue_item.id,
            action='ADDED',
            details=f'Added project {project.project_code} to queue at position {next_position}',
            user='System'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Project {project.project_code} added to queue', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding to queue: {str(e)}', 'error')
    
    return redirect(url_for('projects.detail', id=project_id))


@bp.route('/<int:id>')
def detail(id):
    """View queue item details."""
    queue_item = QueueItem.query.get_or_404(id)
    
    # Get activity logs
    logs = ActivityLog.query.filter_by(
        entity_type='QUEUE',
        entity_id=id
    ).order_by(ActivityLog.created_at.desc()).all()
    
    # Get laser runs for this queue item
    runs = LaserRun.query.filter_by(queue_item_id=id).order_by(LaserRun.run_date.desc()).all()
    
    return render_template('queue/detail.html', queue_item=queue_item, logs=logs, runs=runs)


@bp.route('/<int:id>/status', methods=['POST'])
def update_status(id):
    """Update queue item status."""
    queue_item = QueueItem.query.get_or_404(id)
    
    new_status = request.form.get('status')
    
    if new_status not in [QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS, 
                          QueueItem.STATUS_COMPLETED, QueueItem.STATUS_CANCELLED]:
        flash('Invalid status', 'error')
        return redirect(url_for('queue.detail', id=id))
    
    try:
        old_status = queue_item.status
        queue_item.status = new_status
        
        # Update timestamps
        if new_status == QueueItem.STATUS_IN_PROGRESS and not queue_item.started_at:
            queue_item.started_at = datetime.utcnow()
        elif new_status == QueueItem.STATUS_COMPLETED and not queue_item.completed_at:
            queue_item.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log activity
        activity = ActivityLog(
            entity_type='QUEUE',
            entity_id=id,
            action='STATUS_CHANGED',
            details=f'Status changed from {old_status} to {new_status}',
            user='System'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Status updated to {new_status}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('queue.detail', id=id))


@bp.route('/<int:id>/remove', methods=['POST'])
def remove(id):
    """Remove item from queue."""
    queue_item = QueueItem.query.get_or_404(id)
    project_id = queue_item.project_id
    
    try:
        # Log activity before deletion
        activity = ActivityLog(
            entity_type='QUEUE',
            entity_id=id,
            action='REMOVED',
            details=f'Removed project {queue_item.project.project_code} from queue',
            user='System'
        )
        db.session.add(activity)
        
        # Delete queue item
        db.session.delete(queue_item)
        db.session.commit()
        
        # Reorder remaining items
        reorder_queue()
        
        flash('Item removed from queue', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing from queue: {str(e)}', 'error')
    
    return redirect(url_for('queue.index'))


@bp.route('/reorder', methods=['POST'])
def reorder():
    """Reorder queue items (AJAX endpoint)."""
    try:
        # Get new order from request
        new_order = request.json.get('order', [])
        
        # Update positions
        for position, item_id in enumerate(new_order, start=1):
            queue_item = QueueItem.query.get(item_id)
            if queue_item:
                queue_item.queue_position = position
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Queue reordered successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


def reorder_queue():
    """Reorder queue items to fill gaps in positions."""
    active_items = QueueItem.query.filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).order_by(QueueItem.queue_position).all()
    
    for position, item in enumerate(active_items, start=1):
        item.queue_position = position
    
    db.session.commit()


@bp.route('/runs')
def runs():
    """View laser run history."""
    # Get filter parameters
    operator_filter = request.args.get('operator')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = LaserRun.query
    
    if operator_filter:
        query = query.filter_by(operator=operator_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(LaserRun.run_date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(LaserRun.run_date <= date_to_obj)
        except ValueError:
            pass
    
    # Order by run date descending
    runs = query.order_by(LaserRun.run_date.desc()).limit(100).all()
    
    # Get unique operators for filter
    operators = db.session.query(LaserRun.operator).distinct().filter(LaserRun.operator.isnot(None)).all()
    operators = [op[0] for op in operators]
    
    return render_template(
        'queue/runs.html',
        runs=runs,
        operators=operators,
        operator_filter=operator_filter,
        date_from=date_from,
        date_to=date_to
    )


@bp.route('/runs/new/<int:project_id>', methods=['GET', 'POST'])
def new_run(project_id):
    """Log a new laser run."""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            queue_item_id = request.form.get('queue_item_id')
            operator = request.form.get('operator', '').strip()
            cut_time_minutes = request.form.get('cut_time_minutes')
            material_type = request.form.get('material_type', '').strip()
            material_thickness = request.form.get('material_thickness')
            sheet_count = request.form.get('sheet_count', 1)
            parts_produced = request.form.get('parts_produced')
            machine_settings = request.form.get('machine_settings', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Create laser run
            laser_run = LaserRun(
                project_id=project_id,
                queue_item_id=int(queue_item_id) if queue_item_id else None,
                operator=operator if operator else None,
                cut_time_minutes=int(cut_time_minutes) if cut_time_minutes else None,
                material_type=material_type if material_type else None,
                material_thickness=float(material_thickness) if material_thickness else None,
                sheet_count=int(sheet_count) if sheet_count else 1,
                parts_produced=int(parts_produced) if parts_produced else None,
                machine_settings=machine_settings if machine_settings else None,
                notes=notes if notes else None
            )
            
            db.session.add(laser_run)
            db.session.commit()
            
            # Log activity
            activity = ActivityLog(
                entity_type='LASER_RUN',
                entity_id=laser_run.id,
                action='CREATED',
                details=f'Logged laser run for project {project.project_code}',
                user='System'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Laser run logged successfully', 'success')
            return redirect(url_for('projects.detail', id=project_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error logging run: {str(e)}', 'error')
    
    # Get active queue items for this project
    queue_items = QueueItem.query.filter_by(project_id=project_id).filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).all()
    
    return render_template('queue/run_form.html', project=project, queue_items=queue_items)

