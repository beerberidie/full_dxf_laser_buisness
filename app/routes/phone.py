"""
Phone Mode Routes for Laser OS Production Automation.

This module provides mobile-optimized routes for operators to log production runs
from their phones on the shop floor.

Features:
- View active jobs ready to cut
- Start laser run (creates LaserRun with started_at timestamp)
- End laser run (records ended_at, sheets_used, triggers inventory deduction)
- Simple, touch-friendly interface
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models.business import Project, LaserRun, QueueItem, MachineSettingsPreset
from app.security.decorators import can_access_phone_mode

bp = Blueprint('phone', __name__, url_prefix='/phone')


@bp.before_request
@login_required
def check_phone_access():
    """Ensure user can access phone mode before any phone route."""
    if not can_access_phone_mode():
        flash('You do not have permission to access Phone Mode.', 'danger')
        return redirect(url_for('main.dashboard'))


@bp.route('/')
@bp.route('/home')
def home():
    """
    Phone Mode home page.
    
    Shows:
    - Active jobs ready to cut (status = 'Queued' or 'In Progress')
    - Currently running job for this operator (if any)
    - Simple interface for starting runs
    """
    # Check if operator has an active run
    active_run = LaserRun.query.filter_by(
        operator_id=current_user.id,
        status='running'
    ).first()
    
    if active_run:
        # Operator has an active run - redirect to run view
        return redirect(url_for('phone.run_active', run_id=active_run.id))
    
    # Get projects ready to cut (Queued or In Progress status)
    ready_projects = Project.query.filter(
        Project.status.in_([Project.STATUS_QUEUED, Project.STATUS_IN_PROGRESS]),
        Project.on_hold == False
    ).order_by(Project.scheduled_cut_date.asc()).limit(20).all()
    
    return render_template('phone/home.html', 
                         ready_projects=ready_projects,
                         operator_name=current_user.display_name or current_user.full_name or current_user.username)


@bp.route('/run/start/<int:project_id>', methods=['POST'])
def start_run(project_id):
    """
    Start a new laser run for a project.
    
    Creates LaserRun record with:
    - started_at timestamp
    - operator_id (current user)
    - status = 'running'
    - Material details from project
    - Auto-attached preset (if available)
    
    Updates project stage to 'Cutting'
    """
    project = Project.query.get_or_404(project_id)
    
    # Check if operator already has an active run
    existing_run = LaserRun.query.filter_by(
        operator_id=current_user.id,
        status='running'
    ).first()
    
    if existing_run:
        flash('You already have an active run. Please end it before starting a new one.', 'warning')
        return redirect(url_for('phone.run_active', run_id=existing_run.id))
    
    # Auto-attach preset based on material type and thickness
    preset = None
    if project.material_type and project.thickness_mm:
        preset = MachineSettingsPreset.query.filter_by(
            material_type=project.material_type,
            thickness_mm=project.thickness_mm
        ).first()
    
    # Create new laser run
    new_run = LaserRun(
        project_id=project.id,
        operator_id=current_user.id,
        started_at=datetime.utcnow(),
        status='running',
        material_type=project.material_type,
        material_thickness=project.material_thickness,
        thickness_mm=project.thickness_mm,
        sheet_size=project.sheet_size,
        preset_id=preset.id if preset else None,
        run_date=datetime.utcnow()
    )
    
    db.session.add(new_run)
    
    # Update project stage to Cutting
    project.stage = Project.STAGE_CUTTING
    project.stage_last_updated = datetime.utcnow()
    
    # Update project status to In Progress if not already
    if project.status != Project.STATUS_IN_PROGRESS:
        project.status = Project.STATUS_IN_PROGRESS
    
    db.session.commit()
    
    flash(f'Started laser run for {project.project_code}', 'success')
    return redirect(url_for('phone.run_active', run_id=new_run.id))


@bp.route('/run/<int:run_id>')
def run_active(run_id):
    """
    View active laser run.
    
    Shows:
    - Project details
    - Run start time
    - Elapsed time
    - Material details
    - Preset settings (read-only)
    - Form to end run (enter sheets used)
    """
    run = LaserRun.query.get_or_404(run_id)
    
    # Verify this run belongs to current operator
    if run.operator_id != current_user.id:
        flash('You can only view your own runs.', 'danger')
        return redirect(url_for('phone.home'))
    
    # Verify run is still active
    if run.status != 'running':
        flash('This run has already been completed.', 'info')
        return redirect(url_for('phone.home'))
    
    # Calculate elapsed time
    elapsed_seconds = (datetime.utcnow() - run.started_at).total_seconds()
    elapsed_minutes = int(elapsed_seconds / 60)
    
    return render_template('phone/run_active.html',
                         run=run,
                         project=run.project,
                         preset=run.preset,
                         elapsed_minutes=elapsed_minutes,
                         operator_name=current_user.display_name or current_user.full_name or current_user.username)


@bp.route('/run/<int:run_id>/end', methods=['POST'])
def end_run(run_id):
    """
    End an active laser run.
    
    Records:
    - ended_at timestamp
    - sheets_used (from form)
    - parts_produced (from form)
    - notes (from form)
    - Calculates cut_time_minutes
    
    Triggers:
    - Inventory deduction (via production_logic service)
    - Report updates
    - Notification evaluation
    - Project stage update (if appropriate)
    """
    run = LaserRun.query.get_or_404(run_id)
    
    # Verify this run belongs to current operator
    if run.operator_id != current_user.id:
        flash('You can only end your own runs.', 'danger')
        return redirect(url_for('phone.home'))
    
    # Verify run is still active
    if run.status != 'running':
        flash('This run has already been completed.', 'info')
        return redirect(url_for('phone.home'))
    
    # Get form data
    sheets_used = request.form.get('sheets_used', type=int, default=0)
    parts_produced = request.form.get('parts_produced', type=int, default=0)
    notes = request.form.get('notes', '').strip()
    
    # Update run record
    run.ended_at = datetime.utcnow()
    run.status = 'completed'
    run.sheets_used = sheets_used
    run.parts_produced = parts_produced
    if notes:
        run.notes = notes
    
    # Calculate cut time in minutes
    if run.started_at and run.ended_at:
        cut_time_seconds = (run.ended_at - run.started_at).total_seconds()
        run.cut_time_minutes = int(cut_time_seconds / 60)
    
    db.session.commit()
    
    # Import production logic service for inventory deduction
    try:
        from app.services.production_logic import apply_run_inventory_deduction
        apply_run_inventory_deduction(run)
    except ImportError:
        # Service not yet created - will be added in next step
        pass
    
    # Import notification logic for evaluation
    try:
        from app.services.notification_logic import evaluate_notifications_for_project
        evaluate_notifications_for_project(run.project_id)
    except ImportError:
        # Service not yet created - will be added in Phase 4
        pass
    
    flash(f'Completed laser run for {run.project.project_code}. Sheets used: {sheets_used}', 'success')
    return redirect(url_for('phone.home'))


@bp.route('/switch-to-pc')
def switch_to_pc():
    """Switch from Phone Mode to PC Mode."""
    session['ui_mode'] = 'pc'
    flash('Switched to PC Mode', 'success')
    return redirect(url_for('main.dashboard'))

