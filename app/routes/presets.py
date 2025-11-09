"""
Laser OS - Machine Settings Presets Routes

This module defines routes for managing machine settings presets.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from app.models import MachineSettingsPreset, ActivityLog
from app.utils.decorators import role_required
from datetime import datetime

bp = Blueprint('presets', __name__, url_prefix='/presets')


@bp.route('/')
@login_required
def index():
    """
    List all machine settings presets.
    
    Query Parameters:
        search (str): Search term for preset name or material type
        material (str): Filter by material type
        active (str): Filter by active status ('1' for active, '0' for inactive)
    
    Returns:
        Rendered template with preset list
    """
    # Get filter parameters
    search = request.args.get('search', '').strip()
    material_filter = request.args.get('material', '').strip()
    active_filter = request.args.get('active', '').strip()
    
    # Build query
    query = MachineSettingsPreset.query
    
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                MachineSettingsPreset.preset_name.like(search_filter),
                MachineSettingsPreset.material_type.like(search_filter)
            )
        )
    
    if material_filter:
        query = query.filter(MachineSettingsPreset.material_type == material_filter)
    
    if active_filter:
        is_active = active_filter == '1'
        query = query.filter(MachineSettingsPreset.is_active == is_active)
    
    # Order by material type and thickness
    query = query.order_by(
        MachineSettingsPreset.material_type,
        MachineSettingsPreset.thickness
    )
    
    presets = query.all()
    
    # Get unique material types for filter dropdown
    material_types = db.session.query(MachineSettingsPreset.material_type)\
        .distinct()\
        .order_by(MachineSettingsPreset.material_type)\
        .all()
    material_types = [m[0] for m in material_types if m[0]]
    
    return render_template('presets/index.html',
                         presets=presets,
                         material_types=material_types,
                         search=search,
                         material_filter=material_filter,
                         active_filter=active_filter)


@bp.route('/new', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def new_preset():
    """Create a new machine settings preset."""
    if request.method == 'POST':
        try:
            # Get form data
            preset_name = request.form.get('preset_name', '').strip()
            material_type = request.form.get('material_type', '').strip()
            thickness = request.form.get('thickness')
            
            # Validate required fields
            if not preset_name:
                flash('Preset name is required', 'error')
                raise ValueError('Missing preset name')
            
            if not material_type:
                flash('Material type is required', 'error')
                raise ValueError('Missing material type')
            
            if not thickness:
                flash('Thickness is required', 'error')
                raise ValueError('Missing thickness')
            
            # Check for duplicate preset name
            existing = MachineSettingsPreset.query.filter_by(preset_name=preset_name).first()
            if existing:
                flash(f'A preset with the name "{preset_name}" already exists', 'error')
                raise ValueError('Duplicate preset name')
            
            # Create preset
            preset = MachineSettingsPreset(
                preset_name=preset_name,
                material_type=material_type,
                thickness=float(thickness),
                nozzle=request.form.get('nozzle', '').strip() or None,
                cut_speed=float(request.form.get('cut_speed')) if request.form.get('cut_speed') else None,
                nozzle_height=float(request.form.get('nozzle_height')) if request.form.get('nozzle_height') else None,
                gas_type=request.form.get('gas_type', '').strip() or None,
                gas_pressure=float(request.form.get('gas_pressure')) if request.form.get('gas_pressure') else None,
                peak_power=float(request.form.get('peak_power')) if request.form.get('peak_power') else None,
                actual_power=float(request.form.get('actual_power')) if request.form.get('actual_power') else None,
                duty_cycle=float(request.form.get('duty_cycle')) if request.form.get('duty_cycle') else None,
                pulse_frequency=float(request.form.get('pulse_frequency')) if request.form.get('pulse_frequency') else None,
                beam_width=float(request.form.get('beam_width')) if request.form.get('beam_width') else None,
                focus_position=float(request.form.get('focus_position')) if request.form.get('focus_position') else None,
                laser_on_delay=float(request.form.get('laser_on_delay')) if request.form.get('laser_on_delay') else None,
                laser_off_delay=float(request.form.get('laser_off_delay')) if request.form.get('laser_off_delay') else None,
                pierce_time=float(request.form.get('pierce_time')) if request.form.get('pierce_time') else None,
                pierce_power=float(request.form.get('pierce_power')) if request.form.get('pierce_power') else None,
                corner_power=float(request.form.get('corner_power')) if request.form.get('corner_power') else None,
                notes=request.form.get('notes', '').strip() or None,
                is_active=True
            )
            
            db.session.add(preset)
            db.session.commit()
            
            # Log activity
            activity = ActivityLog(
                entity_type='PRESET',
                entity_id=preset.id,
                action='CREATED',
                details=f'Created preset: {preset_name}',
                user='System'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash(f'Preset "{preset_name}" created successfully', 'success')
            return redirect(url_for('presets.index'))
            
        except ValueError:
            # Validation error already flashed
            pass
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating preset: {str(e)}', 'error')
    
    # GET request - show form
    from config import Config
    material_types = Config.MATERIAL_TYPES
    
    return render_template('presets/form.html',
                         preset=None,
                         material_types=material_types,
                         action='new')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def edit_preset(id):
    """Edit an existing machine settings preset."""
    preset = MachineSettingsPreset.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get form data
            preset_name = request.form.get('preset_name', '').strip()
            material_type = request.form.get('material_type', '').strip()
            thickness = request.form.get('thickness')
            
            # Validate required fields
            if not preset_name:
                flash('Preset name is required', 'error')
                raise ValueError('Missing preset name')
            
            if not material_type:
                flash('Material type is required', 'error')
                raise ValueError('Missing material type')
            
            if not thickness:
                flash('Thickness is required', 'error')
                raise ValueError('Missing thickness')
            
            # Check for duplicate preset name (excluding current preset)
            existing = MachineSettingsPreset.query.filter(
                MachineSettingsPreset.preset_name == preset_name,
                MachineSettingsPreset.id != id
            ).first()
            if existing:
                flash(f'A preset with the name "{preset_name}" already exists', 'error')
                raise ValueError('Duplicate preset name')
            
            # Track changes for activity log
            changes = []
            if preset.preset_name != preset_name:
                changes.append(f'name: {preset.preset_name} → {preset_name}')
            if preset.material_type != material_type:
                changes.append(f'material: {preset.material_type} → {material_type}')
            if preset.thickness != float(thickness):
                changes.append(f'thickness: {preset.thickness} → {thickness}')
            
            # Update preset
            preset.preset_name = preset_name
            preset.material_type = material_type
            preset.thickness = float(thickness)
            preset.nozzle = request.form.get('nozzle', '').strip() or None
            preset.cut_speed = float(request.form.get('cut_speed')) if request.form.get('cut_speed') else None
            preset.nozzle_height = float(request.form.get('nozzle_height')) if request.form.get('nozzle_height') else None
            preset.gas_type = request.form.get('gas_type', '').strip() or None
            preset.gas_pressure = float(request.form.get('gas_pressure')) if request.form.get('gas_pressure') else None
            preset.peak_power = float(request.form.get('peak_power')) if request.form.get('peak_power') else None
            preset.actual_power = float(request.form.get('actual_power')) if request.form.get('actual_power') else None
            preset.duty_cycle = float(request.form.get('duty_cycle')) if request.form.get('duty_cycle') else None
            preset.pulse_frequency = float(request.form.get('pulse_frequency')) if request.form.get('pulse_frequency') else None
            preset.beam_width = float(request.form.get('beam_width')) if request.form.get('beam_width') else None
            preset.focus_position = float(request.form.get('focus_position')) if request.form.get('focus_position') else None
            preset.laser_on_delay = float(request.form.get('laser_on_delay')) if request.form.get('laser_on_delay') else None
            preset.laser_off_delay = float(request.form.get('laser_off_delay')) if request.form.get('laser_off_delay') else None
            preset.pierce_time = float(request.form.get('pierce_time')) if request.form.get('pierce_time') else None
            preset.pierce_power = float(request.form.get('pierce_power')) if request.form.get('pierce_power') else None
            preset.corner_power = float(request.form.get('corner_power')) if request.form.get('corner_power') else None
            preset.notes = request.form.get('notes', '').strip() or None
            preset.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log activity
            details = f'Updated preset: {preset_name}'
            if changes:
                details += f' ({", ".join(changes[:3])})'
            
            activity = ActivityLog(
                entity_type='PRESET',
                entity_id=preset.id,
                action='UPDATED',
                details=details,
                user='System'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash(f'Preset "{preset_name}" updated successfully', 'success')
            return redirect(url_for('presets.index'))
            
        except ValueError:
            # Validation error already flashed
            pass
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating preset: {str(e)}', 'error')
    
    # GET request - show form
    from config import Config
    material_types = Config.MATERIAL_TYPES
    
    return render_template('presets/form.html',
                         preset=preset,
                         material_types=material_types,
                         action='edit')


@bp.route('/<int:id>/delete', methods=['POST'])
@role_required('admin', 'manager')
def delete_preset(id):
    """Delete a machine settings preset."""
    preset = MachineSettingsPreset.query.get_or_404(id)

    try:
        preset_name = preset.preset_name

        # Check if preset is being used by any laser runs
        if preset.laser_runs.count() > 0:
            flash(f'Cannot delete preset "{preset_name}" - it is being used by {preset.laser_runs.count()} laser run(s). Consider deactivating it instead.', 'error')
            return redirect(url_for('presets.index'))

        # Log activity before deletion
        activity = ActivityLog(
            entity_type='PRESET',
            entity_id=preset.id,
            action='DELETED',
            details=f'Deleted preset: {preset_name}',
            user='System'
        )
        db.session.add(activity)

        # Delete preset
        db.session.delete(preset)
        db.session.commit()

        flash(f'Preset "{preset_name}" deleted successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting preset: {str(e)}', 'error')

    return redirect(url_for('presets.index'))


@bp.route('/<int:id>/toggle-active', methods=['POST'])
@role_required('admin', 'manager')
def toggle_active(id):
    """Toggle the active status of a preset."""
    preset = MachineSettingsPreset.query.get_or_404(id)

    try:
        # Toggle active status
        preset.is_active = not preset.is_active
        preset.updated_at = datetime.utcnow()

        db.session.commit()

        # Log activity
        status = 'activated' if preset.is_active else 'deactivated'
        activity = ActivityLog(
            entity_type='PRESET',
            entity_id=preset.id,
            action='UPDATED',
            details=f'{status.capitalize()} preset: {preset.preset_name}',
            user='System'
        )
        db.session.add(activity)
        db.session.commit()

        flash(f'Preset "{preset.preset_name}" {status} successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating preset status: {str(e)}', 'error')

    return redirect(url_for('presets.index'))


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

