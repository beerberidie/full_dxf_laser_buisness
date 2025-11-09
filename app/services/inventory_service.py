"""
Laser OS - Inventory Service

This module provides inventory-related business logic for Phase 10 automation.
"""

from app import db
from app.models import InventoryItem, Project
from typing import Dict, Optional, Tuple
from decimal import Decimal


def check_inventory_availability(material_type: str, thickness: float, required_quantity: float,
                                fuzzy_tolerance: float = 0.3) -> Dict:
    """
    Check if inventory has enough material for a project.

    Uses fuzzy matching for thickness to handle nominal vs. actual thickness variations
    (e.g., "1mm nominal" material that is actually 1.2mm thick).

    Args:
        material_type: Material type (e.g., 'Mild Steel', 'Aluminum')
        thickness: Material thickness in mm (nominal)
        required_quantity: Required quantity in sheets
        fuzzy_tolerance: Tolerance for fuzzy thickness matching in mm (default: ±0.3mm)

    Returns:
        Dictionary with:
            - available: bool - Whether enough inventory is available
            - inventory_item: InventoryItem or None - Matching inventory item
            - quantity_on_hand: float - Current quantity in inventory
            - required_quantity: float - Required quantity
            - shortage: float - Shortage amount (0 if available)
            - match_type: str - 'exact', 'fuzzy', or 'none'
            - message: str - Human-readable status message
    """
    # Step 1: Try exact match first (preferred)
    inventory_item = InventoryItem.query.filter_by(
        category=InventoryItem.CATEGORY_SHEET_METAL,
        material_type=material_type,
        thickness=thickness
    ).first()

    match_type = 'exact' if inventory_item else None

    # Step 2: If no exact match, try fuzzy match within tolerance
    if not inventory_item and fuzzy_tolerance > 0:
        # Calculate thickness range
        min_thickness = thickness - fuzzy_tolerance
        max_thickness = thickness + fuzzy_tolerance

        # Query for items within tolerance range
        fuzzy_matches = InventoryItem.query.filter(
            InventoryItem.category == InventoryItem.CATEGORY_SHEET_METAL,
            InventoryItem.material_type == material_type,
            InventoryItem.thickness.isnot(None),
            InventoryItem.thickness >= min_thickness,
            InventoryItem.thickness <= max_thickness
        ).all()

        if fuzzy_matches:
            # Prioritize by closest thickness match, then by highest quantity
            fuzzy_matches.sort(
                key=lambda item: (
                    abs(float(item.thickness) - thickness),  # Closest thickness first
                    -float(item.quantity_on_hand)  # Highest quantity second (negative for descending)
                )
            )
            inventory_item = fuzzy_matches[0]
            match_type = 'fuzzy'

    # Step 3: Return result
    if not inventory_item:
        return {
            'available': False,
            'inventory_item': None,
            'quantity_on_hand': 0,
            'required_quantity': required_quantity,
            'shortage': required_quantity,
            'match_type': 'none',
            'message': f'No inventory item found for {material_type} {thickness}mm (searched ±{fuzzy_tolerance}mm)'
        }

    quantity_on_hand = float(inventory_item.quantity_on_hand)
    shortage = max(0, required_quantity - quantity_on_hand)

    # Build message with match type indicator
    if match_type == 'exact':
        match_indicator = ''
    else:
        actual_thickness = float(inventory_item.thickness)
        match_indicator = f' (using {actual_thickness}mm material - fuzzy match)'

    availability_msg = 'Sufficient inventory available' if quantity_on_hand >= required_quantity \
                       else f'Insufficient inventory: need {shortage} more sheets'

    return {
        'available': quantity_on_hand >= required_quantity,
        'inventory_item': inventory_item,
        'quantity_on_hand': quantity_on_hand,
        'required_quantity': required_quantity,
        'shortage': shortage,
        'match_type': match_type,
        'message': f'{availability_msg}{match_indicator}'
    }


def check_project_inventory_availability(project: Project) -> Dict:
    """
    Check if inventory has enough material for a specific project.

    Args:
        project: Project instance

    Returns:
        Dictionary with availability information (same as check_inventory_availability)
    """
    if not project.material_type or not project.material_thickness or not project.material_quantity_sheets:
        return {
            'available': False,
            'inventory_item': None,
            'quantity_on_hand': 0,
            'required_quantity': 0,
            'shortage': 0,
            'match_type': 'none',
            'message': 'Project missing material information (type, thickness, or quantity)'
        }

    return check_inventory_availability(
        material_type=project.material_type,
        thickness=float(project.material_thickness),
        required_quantity=float(project.material_quantity_sheets)
    )


def reserve_inventory(inventory_item: InventoryItem, quantity: float, 
                     reference_type: str = 'PROJECT', reference_id: int = None,
                     performed_by: str = 'System', notes: str = None) -> bool:
    """
    Reserve inventory for a project (deduct from available stock).
    
    Args:
        inventory_item: InventoryItem instance
        quantity: Quantity to reserve (positive number)
        reference_type: Type of reference (e.g., 'PROJECT', 'QUEUE_ITEM')
        reference_id: ID of the reference entity
        performed_by: User who performed the action
        notes: Optional notes
    
    Returns:
        bool: True if successful, False if insufficient stock
    """
    if float(inventory_item.quantity_on_hand) < quantity:
        return False
    
    # Deduct inventory (negative quantity for usage)
    inventory_item.adjust_stock(
        quantity=-quantity,
        transaction_type='Usage',
        performed_by=performed_by,
        notes=notes or f'Reserved for {reference_type} #{reference_id}',
        reference_type=reference_type,
        reference_id=reference_id
    )
    
    db.session.commit()
    return True


def release_inventory(inventory_item: InventoryItem, quantity: float,
                     reference_type: str = 'PROJECT', reference_id: int = None,
                     performed_by: str = 'System', notes: str = None) -> bool:
    """
    Release reserved inventory back to available stock.
    
    Args:
        inventory_item: InventoryItem instance
        quantity: Quantity to release (positive number)
        reference_type: Type of reference (e.g., 'PROJECT', 'QUEUE_ITEM')
        reference_id: ID of the reference entity
        performed_by: User who performed the action
        notes: Optional notes
    
    Returns:
        bool: True if successful
    """
    # Add inventory back (positive quantity for return)
    inventory_item.adjust_stock(
        quantity=quantity,
        transaction_type='Return',
        performed_by=performed_by,
        notes=notes or f'Released from {reference_type} #{reference_id}',
        reference_type=reference_type,
        reference_id=reference_id
    )
    
    db.session.commit()
    return True


def get_low_stock_items() -> list:
    """
    Get all inventory items that are below reorder level.
    
    Returns:
        List of InventoryItem instances that are low on stock
    """
    items = InventoryItem.query.filter(
        InventoryItem.reorder_level.isnot(None)
    ).all()
    
    return [item for item in items if item.is_low_stock]


def get_material_ordering_suggestions(project: Project) -> Dict:
    """
    Get material ordering suggestions for a project.
    
    Args:
        project: Project instance
    
    Returns:
        Dictionary with ordering suggestions
    """
    availability = check_project_inventory_availability(project)
    
    if availability['available']:
        return {
            'needs_ordering': False,
            'message': 'Sufficient inventory available'
        }
    
    shortage = availability['shortage']
    inventory_item = availability['inventory_item']
    
    # Calculate order quantity (shortage + reorder quantity if set)
    if inventory_item and inventory_item.reorder_quantity:
        suggested_order_qty = max(shortage, float(inventory_item.reorder_quantity))
    else:
        # Round up to nearest 10 sheets
        suggested_order_qty = ((int(shortage) // 10) + 1) * 10
    
    return {
        'needs_ordering': True,
        'shortage': shortage,
        'suggested_order_quantity': suggested_order_qty,
        'material_type': project.material_type,
        'thickness': float(project.material_thickness),
        'supplier_name': inventory_item.supplier_name if inventory_item else None,
        'supplier_contact': inventory_item.supplier_contact if inventory_item else None,
        'estimated_cost': (suggested_order_qty * float(inventory_item.unit_cost)) if inventory_item and inventory_item.unit_cost else None,
        'message': f'Order {suggested_order_qty} sheets of {project.material_type} {project.material_thickness}mm'
    }

