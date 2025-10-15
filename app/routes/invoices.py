"""
Invoices routes for Laser OS
Handles invoice management operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Invoice, InvoiceItem, Client, Project, Quote, ActivityLog
from datetime import datetime, timedelta
from decimal import Decimal

bp = Blueprint('invoices', __name__, url_prefix='/invoices')


@bp.route('/')
def index():
    """Display invoices list."""
    # Get filter parameters
    status = request.args.get('status', '')
    client_id = request.args.get('client_id', type=int)
    
    # Build query
    query = Invoice.query
    
    if status:
        query = query.filter_by(status=status)
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    # Order by invoice date descending
    invoices = query.order_by(Invoice.invoice_date.desc()).all()
    
    # Get clients for filter
    clients = Client.query.order_by(Client.name).all()
    
    return render_template('invoices/index.html', invoices=invoices, clients=clients)


@bp.route('/new', methods=['GET', 'POST'])
def new_invoice():
    """Create a new invoice."""
    if request.method == 'POST':
        # Get form data
        client_id = request.form.get('client_id', type=int)
        project_id = request.form.get('project_id', type=int) or None
        quote_id = request.form.get('quote_id', type=int) or None
        invoice_date = datetime.strptime(request.form.get('invoice_date'), '%Y-%m-%d').date()
        payment_days = request.form.get('payment_days', type=int, default=30)
        due_date = invoice_date + timedelta(days=payment_days)
        tax_rate = Decimal(request.form.get('tax_rate', '15.0'))
        payment_terms = request.form.get('payment_terms', 'Net 30')
        notes = request.form.get('notes', '')
        
        # Generate invoice number
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        next_num = (last_invoice.id + 1) if last_invoice else 1
        invoice_number = f"INV-{datetime.now().year}-{next_num:04d}"
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            client_id=client_id,
            project_id=project_id,
            quote_id=quote_id,
            invoice_date=invoice_date,
            due_date=due_date,
            tax_rate=tax_rate,
            payment_terms=payment_terms,
            notes=notes,
            created_by='System'
        )
        
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Add line items
        item_count = int(request.form.get('item_count', 0))
        for i in range(1, item_count + 1):
            description = request.form.get(f'item_{i}_description')
            if description:
                quantity = Decimal(request.form.get(f'item_{i}_quantity', '1'))
                unit_price = Decimal(request.form.get(f'item_{i}_unit_price', '0'))
                line_total = quantity * unit_price
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_number=i,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
                db.session.add(item)
        
        # Calculate totals
        invoice.calculate_totals()
        
        # Log activity
        activity = ActivityLog(
            entity_type='Invoice',
            entity_id=invoice.id,
            action='Created',
            user='System',
            details=f'Created invoice {invoice.invoice_number}'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        flash(f'Invoice {invoice.invoice_number} created successfully!', 'success')
        return redirect(url_for('invoices.detail', id=invoice.id))
    
    # GET request
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.project_code.desc()).limit(50).all()
    quotes = Quote.query.filter_by(status=Quote.STATUS_ACCEPTED).order_by(Quote.quote_date.desc()).limit(50).all()
    
    return render_template('invoices/form.html', clients=clients, projects=projects, quotes=quotes)


@bp.route('/<int:id>')
def detail(id):
    """Display invoice details."""
    invoice = Invoice.query.get_or_404(id)
    return render_template('invoices/detail.html', invoice=invoice)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an invoice."""
    invoice = Invoice.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update invoice
        invoice.status = request.form.get('status')
        invoice.amount_paid = Decimal(request.form.get('amount_paid', '0'))
        invoice.notes = request.form.get('notes', '')
        
        # Log activity
        activity = ActivityLog(
            entity_type='Invoice',
            entity_id=invoice.id,
            action='Updated',
            user='System',
            details=f'Updated invoice {invoice.invoice_number}'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        flash(f'Invoice {invoice.invoice_number} updated successfully!', 'success')
        return redirect(url_for('invoices.detail', id=invoice.id))
    
    # GET request
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.project_code.desc()).limit(50).all()
    quotes = Quote.query.order_by(Quote.quote_date.desc()).limit(50).all()
    
    return render_template('invoices/form.html', invoice=invoice, clients=clients, projects=projects, quotes=quotes)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete an invoice."""
    invoice = Invoice.query.get_or_404(id)
    invoice_number = invoice.invoice_number
    
    # Log activity
    activity = ActivityLog(
        entity_type='Invoice',
        entity_id=invoice.id,
        action='Deleted',
        user='System',
        details=f'Deleted invoice {invoice_number}'
    )
    db.session.add(activity)
    
    db.session.delete(invoice)
    db.session.commit()
    
    flash(f'Invoice {invoice_number} deleted successfully!', 'success')
    return redirect(url_for('invoices.index'))

