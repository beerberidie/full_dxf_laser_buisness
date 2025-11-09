"""
Queue management routes for production queue and laser runs
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_required
from app import db
from app.models import QueueItem, LaserRun, Project, ActivityLog, Operator, MachineSettingsPreset
from app.utils.decorators import role_required
from datetime import datetime, date

bp = Blueprint('queue', __name__, url_prefix='/queue')


@bp.route('/')
@login_required
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
@role_required('admin', 'manager', 'operator')
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
@login_required
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
@role_required('admin', 'manager', 'operator')
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

        # CRITICAL FIX: Synchronize Project status with Queue status
        project = queue_item.project
        if project:
            old_project_status = project.status

            # Map Queue status to Project status
            if new_status == QueueItem.STATUS_IN_PROGRESS:
                project.status = Project.STATUS_IN_PROGRESS
                project.updated_at = datetime.utcnow()
            elif new_status == QueueItem.STATUS_COMPLETED:
                project.status = Project.STATUS_COMPLETED
                project.completion_date = date.today()
                project.updated_at = datetime.utcnow()
            elif new_status == QueueItem.STATUS_CANCELLED:
                project.status = Project.STATUS_CANCELLED
                project.updated_at = datetime.utcnow()

            # Log project status change if it changed
            if old_project_status != project.status:
                project_activity = ActivityLog(
                    entity_type='PROJECT',
                    entity_id=project.id,
                    action='STATUS_CHANGED',
                    details=f'Status auto-updated from {old_project_status} to {project.status} (triggered by Queue status change)',
                    user='System (Queue Sync)'
                )
                db.session.add(project_activity)

        # Log queue activity
        activity = ActivityLog(
            entity_type='QUEUE',
            entity_id=id,
            action='STATUS_CHANGED',
            details=f'Status changed from {old_status} to {new_status}',
            user='System'
        )
        db.session.add(activity)

        # CRITICAL: Single atomic commit for all changes
        db.session.commit()

        flash(f'Status updated to {new_status}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'error')

    return redirect(url_for('queue.detail', id=id))


@bp.route('/<int:id>/remove', methods=['POST'])
@role_required('admin', 'manager')
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
@role_required('admin', 'manager', 'operator')
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
@login_required
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
@role_required('admin', 'manager', 'operator')
def new_run(project_id):
    """Log a new laser run."""
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        try:
            # Get form data
            queue_item_id = request.form.get('queue_item_id')
            operator_id = request.form.get('operator_id')
            preset_id = request.form.get('preset_id')
            cut_time_minutes = request.form.get('cut_time_minutes')
            material_type = request.form.get('material_type', '').strip()
            material_thickness = request.form.get('material_thickness')
            sheet_count = request.form.get('sheet_count', 1)
            parts_produced = request.form.get('parts_produced')
            machine_settings = request.form.get('machine_settings', '').strip()
            notes = request.form.get('notes', '').strip()

            # Validate operator if provided
            operator_name = None
            if operator_id:
                operator = Operator.query.get(int(operator_id))
                if not operator:
                    flash('Selected operator not found', 'error')
                    raise ValueError('Invalid operator')
                if not operator.is_active:
                    flash('Selected operator is not active', 'error')
                    raise ValueError('Inactive operator')
                operator_name = operator.name

            # Validate preset if provided
            if preset_id:
                preset = MachineSettingsPreset.query.get(int(preset_id))
                if not preset:
                    flash('Selected preset not found', 'error')
                    raise ValueError('Invalid preset')
                if not preset.is_active:
                    flash('Selected preset is not active', 'error')
                    raise ValueError('Inactive preset')

            # Create laser run
            laser_run = LaserRun(
                project_id=project_id,
                queue_item_id=int(queue_item_id) if queue_item_id else None,
                operator_id=int(operator_id) if operator_id else None,
                operator=operator_name if operator_name else None,  # Legacy field for backward compatibility
                preset_id=int(preset_id) if preset_id else None,
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

    # GET request - prepare form data
    # Get active queue items for this project
    queue_items = QueueItem.query.filter_by(project_id=project_id).filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).all()

    # Get active operators
    operators = Operator.query.filter_by(is_active=True).order_by(Operator.name).all()

    # Get active presets
    presets = MachineSettingsPreset.query.filter_by(is_active=True).order_by(
        MachineSettingsPreset.material_type,
        MachineSettingsPreset.thickness
    ).all()

    # Get material types from config
    material_types = current_app.config.get('MATERIAL_TYPES', [])

    # CRITICAL FIX: Get operator_id from session for auto-population
    session_operator_id = session.get('operator_id')

    return render_template(
        'queue/run_form.html',
        project=project,
        queue_items=queue_items,
        operators=operators,
        presets=presets,
        material_types=material_types,
        session_operator_id=session_operator_id
    )


@bp.route('/api/presets')
@login_required
def api_presets():
    """API endpoint to get all active presets as JSON."""
    presets = MachineSettingsPreset.query.filter_by(is_active=True).order_by(
        MachineSettingsPreset.material_type,
        MachineSettingsPreset.thickness
    ).all()

    return jsonify({
        'presets': [preset.to_dict() for preset in presets]
    })

