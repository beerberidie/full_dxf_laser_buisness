"""
Quotes routes for Laser OS
Handles quote management operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Quote, QuoteItem, Client, Project, ActivityLog
from datetime import datetime, timedelta
from decimal import Decimal

bp = Blueprint('quotes', __name__, url_prefix='/quotes')


@bp.route('/')
def index():
    """Display quotes list."""
    # Get filter parameters
    status = request.args.get('status', '')
    client_id = request.args.get('client_id', type=int)
    
    # Build query
    query = Quote.query
    
    if status:
        query = query.filter_by(status=status)
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    # Order by quote date descending
    quotes = query.order_by(Quote.quote_date.desc()).all()
    
    # Get clients for filter
    clients = Client.query.order_by(Client.name).all()
    
    return render_template('quotes/index.html', quotes=quotes, clients=clients)


@bp.route('/new', methods=['GET', 'POST'])
def new_quote():
    """Create a new quote."""
    if request.method == 'POST':
        # Get form data
        client_id = request.form.get('client_id', type=int)
        project_id = request.form.get('project_id', type=int) or None
        quote_date = datetime.strptime(request.form.get('quote_date'), '%Y-%m-%d').date()
        valid_days = request.form.get('valid_days', type=int, default=30)
        valid_until = quote_date + timedelta(days=valid_days)
        tax_rate = Decimal(request.form.get('tax_rate', '15.0'))
        notes = request.form.get('notes', '')
        terms = request.form.get('terms', '')
        
        # Generate quote number
        last_quote = Quote.query.order_by(Quote.id.desc()).first()
        next_num = (last_quote.id + 1) if last_quote else 1
        quote_number = f"QT-{datetime.now().year}-{next_num:04d}"
        
        # Create quote
        quote = Quote(
            quote_number=quote_number,
            client_id=client_id,
            project_id=project_id,
            quote_date=quote_date,
            valid_until=valid_until,
            tax_rate=tax_rate,
            notes=notes,
            terms=terms,
            created_by='System'
        )
        
        db.session.add(quote)
        db.session.flush()  # Get quote ID
        
        # Add line items
        item_count = int(request.form.get('item_count', 0))
        for i in range(1, item_count + 1):
            description = request.form.get(f'item_{i}_description')
            if description:
                quantity = Decimal(request.form.get(f'item_{i}_quantity', '1'))
                unit_price = Decimal(request.form.get(f'item_{i}_unit_price', '0'))
                line_total = quantity * unit_price
                
                item = QuoteItem(
                    quote_id=quote.id,
                    item_number=i,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
                db.session.add(item)
        
        # Calculate totals
        quote.calculate_totals()
        
        # Log activity
        activity = ActivityLog(
            entity_type='Quote',
            entity_id=quote.id,
            action='Created',
            user='System',
            details=f'Created quote {quote.quote_number}'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        flash(f'Quote {quote.quote_number} created successfully!', 'success')
        return redirect(url_for('quotes.detail', id=quote.id))
    
    # GET request
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.project_code.desc()).limit(50).all()
    
    return render_template('quotes/form.html', clients=clients, projects=projects)


@bp.route('/<int:id>')
def detail(id):
    """Display quote details."""
    quote = Quote.query.get_or_404(id)
    return render_template('quotes/detail.html', quote=quote)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit a quote."""
    quote = Quote.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update quote
        quote.status = request.form.get('status')
        quote.notes = request.form.get('notes', '')
        quote.terms = request.form.get('terms', '')
        
        # Log activity
        activity = ActivityLog(
            entity_type='Quote',
            entity_id=quote.id,
            action='Updated',
            user='System',
            details=f'Updated quote {quote.quote_number}'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        flash(f'Quote {quote.quote_number} updated successfully!', 'success')
        return redirect(url_for('quotes.detail', id=quote.id))
    
    # GET request
    clients = Client.query.order_by(Client.name).all()
    projects = Project.query.order_by(Project.project_code.desc()).limit(50).all()
    
    return render_template('quotes/form.html', quote=quote, clients=clients, projects=projects)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a quote."""
    quote = Quote.query.get_or_404(id)
    quote_number = quote.quote_number
    
    # Log activity
    activity = ActivityLog(
        entity_type='Quote',
        entity_id=quote.id,
        action='Deleted',
        user='System',
        details=f'Deleted quote {quote_number}'
    )
    db.session.add(activity)
    
    db.session.delete(quote)
    db.session.commit()
    
    flash(f'Quote {quote_number} deleted successfully!', 'success')
    return redirect(url_for('quotes.index'))

