"""
Inventory management routes for materials and consumables tracking
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from app import db
from app.models import InventoryItem, InventoryTransaction, ActivityLog, Setting
from app.utils.decorators import role_required
from datetime import datetime

bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@bp.route('/')
@login_required
def index():
    """Display inventory dashboard."""
    # Get filter parameters
    category_filter = request.args.get('category')
    low_stock_only = request.args.get('low_stock') == 'true'
    search = request.args.get('search', '').strip()
    
    # Build query
    query = InventoryItem.query
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if search:
        query = query.filter(
            db.or_(
                InventoryItem.item_code.ilike(f'%{search}%'),
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.material_type.ilike(f'%{search}%')
            )
        )
    
    # Get all items first
    all_items = query.order_by(InventoryItem.name).all()
    
    # Filter for low stock if requested
    if low_stock_only:
        items = [item for item in all_items if item.is_low_stock]
    else:
        items = all_items
    
    # Get statistics
    total_items = InventoryItem.query.count()
    low_stock_count = len([item for item in InventoryItem.query.all() if item.is_low_stock])
    total_value = sum(item.stock_value for item in InventoryItem.query.all())
    
    # Get categories
    categories = [
        InventoryItem.CATEGORY_SHEET_METAL,
        InventoryItem.CATEGORY_GAS,
        InventoryItem.CATEGORY_CONSUMABLES,
        InventoryItem.CATEGORY_TOOLS,
        InventoryItem.CATEGORY_OTHER
    ]
    
    stats = {
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'total_value': total_value,
        'categories_count': len(categories)
    }
    
    return render_template(
        'inventory/index.html',
        items=items,
        stats=stats,
        categories=categories,
        category_filter=category_filter,
        low_stock_only=low_stock_only,
        search=search
    )


@bp.route('/new', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def new_item():
    """Create a new inventory item."""
    if request.method == 'POST':
        try:
            # Get form data
            item_code = request.form.get('item_code', '').strip()
            name = request.form.get('name', '').strip()
            category = request.form.get('category')
            material_type = request.form.get('material_type', '').strip()
            thickness = request.form.get('thickness')
            unit = request.form.get('unit', '').strip()
            quantity_on_hand = request.form.get('quantity_on_hand', 0)
            reorder_level = request.form.get('reorder_level')
            reorder_quantity = request.form.get('reorder_quantity')
            unit_cost = request.form.get('unit_cost')
            supplier_name = request.form.get('supplier_name', '').strip()
            supplier_contact = request.form.get('supplier_contact', '').strip()
            location = request.form.get('location', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Validate required fields
            if not all([item_code, name, category, unit]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('inventory.new_item'))
            
            # Check for duplicate item code
            existing = InventoryItem.query.filter_by(item_code=item_code).first()
            if existing:
                flash(f'Item code {item_code} already exists', 'error')
                return redirect(url_for('inventory.new_item'))
            
            # Create inventory item
            item = InventoryItem(
                item_code=item_code,
                name=name,
                category=category,
                material_type=material_type if material_type else None,
                thickness=float(thickness) if thickness else None,
                unit=unit,
                quantity_on_hand=float(quantity_on_hand) if quantity_on_hand else 0,
                reorder_level=float(reorder_level) if reorder_level else None,
                reorder_quantity=float(reorder_quantity) if reorder_quantity else None,
                unit_cost=float(unit_cost) if unit_cost else None,
                supplier_name=supplier_name if supplier_name else None,
                supplier_contact=supplier_contact if supplier_contact else None,
                location=location if location else None,
                notes=notes if notes else None
            )
            
            db.session.add(item)
            db.session.commit()
            
            # Log activity
            activity = ActivityLog(
                entity_type='INVENTORY',
                entity_id=item.id,
                action='CREATED',
                details=f'Created inventory item: {item.item_code} - {item.name}',
                user='System'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash(f'Inventory item {item.item_code} created successfully', 'success')
            return redirect(url_for('inventory.detail', id=item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating inventory item: {str(e)}', 'error')
    
    # Get categories and units
    categories = [
        InventoryItem.CATEGORY_SHEET_METAL,
        InventoryItem.CATEGORY_GAS,
        InventoryItem.CATEGORY_CONSUMABLES,
        InventoryItem.CATEGORY_TOOLS,
        InventoryItem.CATEGORY_OTHER
    ]

    units = ['sheets', 'kg', 'liters', 'pieces', 'meters', 'hours']

    # Get material types from config
    material_types = current_app.config.get('MATERIAL_TYPES', [])

    # Get thicknesses from settings (same as products)
    thicknesses_setting = Setting.query.filter_by(key='default_thicknesses').first()
    thicknesses = thicknesses_setting.value.split(',') if thicknesses_setting else []

    return render_template(
        'inventory/form.html',
        item=None,
        categories=categories,
        units=units,
        material_types=material_types,
        thicknesses=thicknesses
    )


@bp.route('/<int:id>')
@login_required
def detail(id):
    """View inventory item details."""
    item = InventoryItem.query.get_or_404(id)
    
    # Get recent transactions
    transactions = InventoryTransaction.query.filter_by(
        inventory_item_id=id
    ).order_by(InventoryTransaction.transaction_date.desc()).limit(20).all()
    
    # Get activity logs
    logs = ActivityLog.query.filter_by(
        entity_type='INVENTORY',
        entity_id=id
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return render_template('inventory/detail.html', item=item, transactions=transactions, logs=logs)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def edit(id):
    """Edit an inventory item."""
    item = InventoryItem.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get form data
            item.name = request.form.get('name', '').strip()
            item.category = request.form.get('category')
            item.material_type = request.form.get('material_type', '').strip() or None
            
            thickness = request.form.get('thickness')
            item.thickness = float(thickness) if thickness else None
            
            item.unit = request.form.get('unit', '').strip()
            
            reorder_level = request.form.get('reorder_level')
            item.reorder_level = float(reorder_level) if reorder_level else None
            
            reorder_quantity = request.form.get('reorder_quantity')
            item.reorder_quantity = float(reorder_quantity) if reorder_quantity else None
            
            unit_cost = request.form.get('unit_cost')
            item.unit_cost = float(unit_cost) if unit_cost else None
            
            item.supplier_name = request.form.get('supplier_name', '').strip() or None
            item.supplier_contact = request.form.get('supplier_contact', '').strip() or None
            item.location = request.form.get('location', '').strip() or None
            item.notes = request.form.get('notes', '').strip() or None
            
            db.session.commit()
            
            # Log activity
            activity = ActivityLog(
                entity_type='INVENTORY',
                entity_id=item.id,
                action='UPDATED',
                details=f'Updated inventory item: {item.item_code}',
                user='System'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash(f'Inventory item {item.item_code} updated successfully', 'success')
            return redirect(url_for('inventory.detail', id=item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating inventory item: {str(e)}', 'error')
    
    # Get categories and units
    categories = [
        InventoryItem.CATEGORY_SHEET_METAL,
        InventoryItem.CATEGORY_GAS,
        InventoryItem.CATEGORY_CONSUMABLES,
        InventoryItem.CATEGORY_TOOLS,
        InventoryItem.CATEGORY_OTHER
    ]

    units = ['sheets', 'kg', 'liters', 'pieces', 'meters', 'hours']

    # Get material types from config
    material_types = current_app.config.get('MATERIAL_TYPES', [])

    # Get thicknesses from settings (same as products)
    thicknesses_setting = Setting.query.filter_by(key='default_thicknesses').first()
    thicknesses = thicknesses_setting.value.split(',') if thicknesses_setting else []

    return render_template(
        'inventory/form.html',
        item=item,
        categories=categories,
        units=units,
        material_types=material_types,
        thicknesses=thicknesses
    )


@bp.route('/<int:id>/delete', methods=['POST'])
@role_required('admin', 'manager')
def delete(id):
    """Delete an inventory item."""
    item = InventoryItem.query.get_or_404(id)
    
    try:
        item_code = item.item_code
        
        # Log activity before deletion
        activity = ActivityLog(
            entity_type='INVENTORY',
            entity_id=id,
            action='DELETED',
            details=f'Deleted inventory item: {item_code}',
            user='System'
        )
        db.session.add(activity)
        
        # Delete item
        db.session.delete(item)
        db.session.commit()
        
        flash(f'Inventory item {item_code} deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting inventory item: {str(e)}', 'error')
    
    return redirect(url_for('inventory.index'))


@bp.route('/<int:id>/adjust', methods=['POST'])
@role_required('admin', 'manager', 'operator')
def adjust_stock(id):
    """Adjust inventory stock."""
    item = InventoryItem.query.get_or_404(id)
    
    try:
        # Get form data
        transaction_type = request.form.get('transaction_type')
        quantity = request.form.get('quantity')
        notes = request.form.get('notes', '').strip()
        
        if not quantity:
            flash('Please enter a quantity', 'error')
            return redirect(url_for('inventory.detail', id=id))
        
        quantity = float(quantity)
        
        # Adjust stock
        item.adjust_stock(
            quantity=quantity,
            transaction_type=transaction_type,
            performed_by='System',
            notes=notes if notes else None
        )
        
        db.session.commit()
        
        # Log activity
        activity = ActivityLog(
            entity_type='INVENTORY',
            entity_id=item.id,
            action='STOCK_ADJUSTED',
            details=f'Stock adjusted: {transaction_type} {quantity} {item.unit}',
            user='System'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Stock adjusted successfully. New quantity: {item.quantity_on_hand} {item.unit}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adjusting stock: {str(e)}', 'error')
    
    return redirect(url_for('inventory.detail', id=id))


@bp.route('/low-stock')
@login_required
def low_stock():
    """View low stock items."""
    items = [item for item in InventoryItem.query.all() if item.is_low_stock]
    
    return render_template('inventory/low_stock.html', items=items)


@bp.route('/transactions')
@login_required
def transactions():
    """View all inventory transactions."""
    # Get filter parameters
    item_id = request.args.get('item_id', type=int)
    transaction_type = request.args.get('type')
    
    # Build query
    query = InventoryTransaction.query
    
    if item_id:
        query = query.filter_by(inventory_item_id=item_id)
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    # Get transactions
    transactions = query.order_by(InventoryTransaction.transaction_date.desc()).limit(100).all()
    
    # Get transaction types
    transaction_types = [
        InventoryTransaction.TYPE_PURCHASE,
        InventoryTransaction.TYPE_USAGE,
        InventoryTransaction.TYPE_ADJUSTMENT,
        InventoryTransaction.TYPE_RETURN,
        InventoryTransaction.TYPE_WASTE
    ]
    
    return render_template(
        'inventory/transactions.html',
        transactions=transactions,
        transaction_types=transaction_types,
        item_id=item_id,
        transaction_type=transaction_type
    )

