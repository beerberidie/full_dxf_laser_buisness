"""
Production Logic Service for Laser OS.

This module handles production-related business logic including:
- Inventory deduction when laser runs complete
- Material availability checking
- Production metrics calculation
"""

from datetime import datetime
from app import db
from app.models.business import InventoryItem, LaserRun, Project


def apply_run_inventory_deduction(laser_run):
    """
    Apply inventory deduction after a laser run completes.
    
    Finds the matching inventory item by:
    - material_type
    - thickness_mm
    - sheet_size
    
    Deducts sheets_used from inventory count.
    
    Args:
        laser_run (LaserRun): Completed laser run with sheets_used populated
        
    Returns:
        bool: True if deduction was successful, False if inventory item not found
    """
    if not laser_run.sheets_used or laser_run.sheets_used <= 0:
        # No sheets used, nothing to deduct
        return True
    
    # Find matching inventory item
    inv_item = InventoryItem.query.filter_by(
        material_type=laser_run.material_type,
        thickness_mm=laser_run.thickness_mm,
        sheet_size=laser_run.sheet_size,
        category=InventoryItem.CATEGORY_SHEET_METAL
    ).first()
    
    if not inv_item:
        # No matching inventory item found
        # Log warning but don't fail the run completion
        print(f"WARNING: No inventory item found for {laser_run.material_type} "
              f"{laser_run.thickness_mm}mm {laser_run.sheet_size}")
        return False
    
    # Deduct sheets from inventory
    # Use max(0, ...) to prevent negative inventory
    inv_item.quantity_on_hand = max(0, inv_item.quantity_on_hand - laser_run.sheets_used)
    
    db.session.add(inv_item)
    db.session.commit()
    
    print(f"INFO: Deducted {laser_run.sheets_used} sheets from {inv_item.name}. "
          f"New count: {inv_item.quantity_on_hand}")
    
    # Check if inventory is now below reorder level
    if inv_item.quantity_on_hand < inv_item.reorder_level:
        # Create low stock notification
        try:
            from app.services.notification_logic import create_low_stock_notification
            create_low_stock_notification(inv_item)
        except ImportError:
            # Notification service not yet created
            pass
    
    return True


def check_material_availability(material_type, thickness_mm, sheet_size, sheets_required):
    """
    Check if sufficient material is available in inventory.
    
    Args:
        material_type (str): Material type (e.g., "Mild Steel")
        thickness_mm (str): Thickness in mm (e.g., "3.0")
        sheet_size (str): Sheet size (e.g., "3000x1500")
        sheets_required (int): Number of sheets needed
        
    Returns:
        dict: {
            'available': bool,
            'current_stock': int,
            'required': int,
            'shortage': int (if not available)
        }
    """
    inv_item = InventoryItem.query.filter_by(
        material_type=material_type,
        thickness_mm=thickness_mm,
        sheet_size=sheet_size,
        category=InventoryItem.CATEGORY_SHEET_METAL
    ).first()
    
    if not inv_item:
        return {
            'available': False,
            'current_stock': 0,
            'required': sheets_required,
            'shortage': sheets_required,
            'message': 'Material not found in inventory'
        }
    
    current_stock = int(inv_item.quantity_on_hand)
    available = current_stock >= sheets_required
    
    result = {
        'available': available,
        'current_stock': current_stock,
        'required': sheets_required,
        'inventory_item_id': inv_item.id,
        'inventory_item_name': inv_item.name
    }
    
    if not available:
        result['shortage'] = sheets_required - current_stock
        result['message'] = f'Insufficient stock. Need {sheets_required}, have {current_stock}'
    else:
        result['message'] = f'Sufficient stock available ({current_stock} sheets)'
    
    return result


def calculate_project_production_metrics(project_id):
    """
    Calculate production metrics for a project.
    
    Args:
        project_id (int): Project ID
        
    Returns:
        dict: {
            'total_runs': int,
            'total_sheets_used': int,
            'total_parts_produced': int,
            'total_cut_time_minutes': int,
            'average_cut_time_minutes': float,
            'operators': list of operator names
        }
    """
    runs = LaserRun.query.filter_by(
        project_id=project_id,
        status='completed'
    ).all()
    
    if not runs:
        return {
            'total_runs': 0,
            'total_sheets_used': 0,
            'total_parts_produced': 0,
            'total_cut_time_minutes': 0,
            'average_cut_time_minutes': 0,
            'operators': []
        }
    
    total_sheets = sum(run.sheets_used or 0 for run in runs)
    total_parts = sum(run.parts_produced or 0 for run in runs)
    total_time = sum(run.cut_time_minutes or 0 for run in runs)
    
    # Get unique operators
    operators = set()
    for run in runs:
        if run.operator_obj:
            operators.add(run.operator_obj.name)
        elif run.operator:
            operators.add(run.operator)
    
    return {
        'total_runs': len(runs),
        'total_sheets_used': total_sheets,
        'total_parts_produced': total_parts,
        'total_cut_time_minutes': total_time,
        'average_cut_time_minutes': total_time / len(runs) if runs else 0,
        'operators': list(operators)
    }


def get_active_runs():
    """
    Get all currently active laser runs.
    
    Returns:
        list: List of LaserRun objects with status='running'
    """
    return LaserRun.query.filter_by(status='running').order_by(LaserRun.started_at.desc()).all()


def get_projects_ready_to_cut():
    """
    Get projects that are ready to be cut.
    
    Criteria:
    - Status is 'Queued' or 'In Progress'
    - Not on hold
    - Has material requirements defined
    
    Returns:
        list: List of Project objects ready for cutting
    """
    return Project.query.filter(
        Project.status.in_([Project.STATUS_QUEUED, Project.STATUS_IN_PROGRESS]),
        Project.on_hold == False,
        Project.material_type.isnot(None)
    ).order_by(Project.scheduled_cut_date.asc()).all()


def get_projects_blocked_by_material():
    """
    Get projects blocked due to insufficient material.
    
    Criteria:
    - Stage is 'WaitingOnMaterial'
    - Material requirements defined
    
    Returns:
        list: List of Project objects blocked by material
    """
    return Project.query.filter(
        Project.stage == Project.STAGE_WAITING_MATERIAL,
        Project.material_type.isnot(None)
    ).order_by(Project.stage_last_updated.asc()).all()

