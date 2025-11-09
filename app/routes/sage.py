"""
Sage Business Cloud Accounting Integration Routes

This module handles all routes for Sage integration including:
- OAuth authentication flow
- Dashboard with statistics
- Invoices management
- Quotes management
- Contacts management
- Settings and connection management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import SageConnection, SageBusiness, SageAuditLog
from app.services.sage_auth import SageAuthService
from app.services.sage_client import SageAPIClient

# Create blueprint
bp = Blueprint('sage', __name__, url_prefix='/sage')


# ============================================================================
# OAuth Authentication Routes
# ============================================================================

@bp.route('/connect')
@login_required
def connect():
    """Initiate OAuth connection to Sage."""
    current_app.logger.info("=== SAGE CONNECT ROUTE CALLED ===")
    try:
        # Get redirect URI from config
        redirect_uri = current_app.config.get('SAGE_REDIRECT_URI')
        current_app.logger.info(f"Redirect URI: {redirect_uri}")

        if not redirect_uri:
            current_app.logger.warning("Sage redirect URI not configured")
            flash('Sage integration is not configured. Please contact your administrator.', 'error')
            return redirect(url_for('sage.dashboard'))

        # Generate authorization URL
        auth_url, state = SageAuthService.get_authorization_url(redirect_uri)
        current_app.logger.info(f"Generated auth URL, redirecting to Sage")

        # Redirect user to Sage authorization page
        return redirect(auth_url)

    except Exception as e:
        current_app.logger.error(f"Error initiating Sage connection: {str(e)}")
        flash('Failed to connect to Sage. Please try again.', 'error')
        return redirect(url_for('sage.dashboard'))


@bp.route('/oauth/callback')
@login_required
def oauth_callback():
    """Handle OAuth callback from Sage."""
    try:
        # Get authorization code and state from query parameters
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        # Check for errors
        if error:
            flash(f'Sage authorization failed: {error}', 'error')
            return redirect(url_for('sage.dashboard'))
        
        if not code or not state:
            flash('Invalid OAuth callback. Missing code or state.', 'error')
            return redirect(url_for('sage.dashboard'))
        
        # Verify state to prevent CSRF
        if not SageAuthService.verify_state(state):
            flash('Invalid OAuth state. Possible CSRF attack.', 'error')
            return redirect(url_for('sage.dashboard'))
        
        # Exchange code for tokens
        redirect_uri = current_app.config.get('SAGE_REDIRECT_URI')
        token_data = SageAuthService.exchange_code_for_tokens(code, redirect_uri)
        
        # Create or update connection
        connection = SageAuthService.create_or_update_connection(current_user, token_data)
        
        # Load businesses
        businesses = SageAuthService.load_businesses(connection)
        
        if len(businesses) == 0:
            flash('No businesses found in your Sage account.', 'warning')
            return redirect(url_for('sage.dashboard'))
        elif len(businesses) == 1:
            # Auto-select if only one business
            SageAuthService.select_business(connection, businesses[0].id)
            flash('Successfully connected to Sage!', 'success')
            return redirect(url_for('sage.dashboard'))
        else:
            # Redirect to business selection
            flash('Please select which business you want to work with.', 'info')
            return redirect(url_for('sage.select_business'))
        
    except Exception as e:
        current_app.logger.error(f"Error in OAuth callback: {str(e)}")
        flash('Failed to complete Sage connection. Please try again.', 'error')
        return redirect(url_for('sage.dashboard'))


@bp.route('/select-business', methods=['GET', 'POST'])
@login_required
def select_business():
    """Select which Sage business to work with."""
    # Get user's connection
    connection = SageConnection.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not connection:
        flash('No active Sage connection found. Please connect first.', 'error')
        return redirect(url_for('sage.connect'))
    
    # Get businesses
    businesses = SageBusiness.query.filter_by(connection_id=connection.id).all()
    
    if request.method == 'POST':
        business_id = request.form.get('business_id', type=int)
        
        if not business_id:
            flash('Please select a business.', 'error')
            return render_template('sage/select_business.html', businesses=businesses)
        
        try:
            # Select the business
            SageAuthService.select_business(connection, business_id)
            flash('Business selected successfully!', 'success')
            return redirect(url_for('sage.dashboard'))
        except Exception as e:
            current_app.logger.error(f"Error selecting business: {str(e)}")
            flash('Failed to select business. Please try again.', 'error')
    
    return render_template('sage/select_business.html', businesses=businesses)


@bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Sage integration."""
    try:
        SageAuthService.disconnect(current_user)
        flash('Disconnected from Sage successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error disconnecting Sage: {str(e)}")
        flash('Failed to disconnect from Sage.', 'error')
    
    return redirect(url_for('sage.dashboard'))


# ============================================================================
# Dashboard Route
# ============================================================================

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Sage dashboard with statistics and recent data."""
    # Get connection status
    status = SageAuthService.get_connection_status(current_user)

    # Debug logging
    current_app.logger.info(f"Sage dashboard accessed - Connected: {status['connected']}, Status: {status.get('status')}")

    if not status['connected']:
        # Not connected - show connection prompt
        current_app.logger.info("Rendering not-connected state")
        return render_template('sage/dashboard.html', status=status)
    
    if status['status'] == 'pending_business_selection':
        # Redirect to business selection
        return redirect(url_for('sage.select_business'))
    
    # Get connection and business
    connection = SageConnection.query.get(status['connection_id'])
    business = SageBusiness.query.get(status['business_id'])
    
    try:
        # Create API client
        client = SageAPIClient(connection, business)
        
        # Get dashboard data
        invoices_data = client.get_sales_invoices(page=1, items_per_page=5)
        quotes_data = client.get_sales_quotes(page=1, items_per_page=5)
        
        # Calculate statistics
        stats = {
            'total_invoices': len(invoices_data.get('$items', [])),
            'total_quotes': len(quotes_data.get('$items', [])),
            'total_revenue': sum(float(inv.get('total_amount', 0)) for inv in invoices_data.get('$items', [])),
            'pending_payments': sum(
                float(inv.get('total_amount', 0))
                for inv in invoices_data.get('$items', [])
                if inv.get('status') in ['SENT', 'UNPAID']
            )
        }
        
        return render_template(
            'sage/dashboard.html',
            status=status,
            business=business,
            stats=stats,
            recent_invoices=invoices_data.get('$items', [])[:5],
            recent_quotes=quotes_data.get('$items', [])[:5]
        )
        
    except Exception as e:
        current_app.logger.error(f"Error loading Sage dashboard: {str(e)}")
        flash('Failed to load dashboard data from Sage.', 'error')
        return render_template('sage/dashboard.html', status=status, business=business, error=str(e))


# ============================================================================
# Invoices Routes
# ============================================================================

@bp.route('/invoices')
@login_required
def invoices():
    """List all sales invoices from Sage."""
    # Get connection status
    status = SageAuthService.get_connection_status(current_user)
    
    if not status['connected'] or status['status'] != 'active':
        flash('Please connect to Sage first.', 'error')
        return redirect(url_for('sage.dashboard'))
    
    # Get connection and business
    connection = SageConnection.query.get(status['connection_id'])
    business = SageBusiness.query.get(status['business_id'])
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    items_per_page = request.args.get('items_per_page', 20, type=int)
    
    try:
        # Create API client
        client = SageAPIClient(connection, business)
        
        # Get invoices
        invoices_data = client.get_sales_invoices(page=page, items_per_page=items_per_page)
        
        return render_template(
            'sage/invoices.html',
            invoices=invoices_data.get('$items', []),
            page=page,
            items_per_page=items_per_page,
            business=business
        )
        
    except Exception as e:
        current_app.logger.error(f"Error loading invoices: {str(e)}")
        flash('Failed to load invoices from Sage.', 'error')
        return redirect(url_for('sage.dashboard'))


@bp.route('/invoices/new', methods=['GET', 'POST'])
@login_required
def new_invoice():
    """Create a new sales invoice."""
    # Get connection status
    status = SageAuthService.get_connection_status(current_user)
    
    if not status['connected'] or status['status'] != 'active':
        flash('Please connect to Sage first.', 'error')
        return redirect(url_for('sage.dashboard'))
    
    # Get connection and business
    connection = SageConnection.query.get(status['connection_id'])
    business = SageBusiness.query.get(status['business_id'])
    
    if request.method == 'POST':
        try:
            # Get form data
            invoice_data = {
                'contact_id': request.form.get('contact_id'),
                'date': request.form.get('date'),
                'due_date': request.form.get('due_date'),
                'reference': request.form.get('reference'),
                'notes': request.form.get('notes'),
                'invoice_lines': []  # TODO: Add line items
            }
            
            # Create API client
            client = SageAPIClient(connection, business)
            
            # Create invoice
            created_invoice = client.create_sales_invoice(invoice_data)
            
            flash('Invoice created successfully!', 'success')
            return redirect(url_for('sage.invoices'))
            
        except Exception as e:
            current_app.logger.error(f"Error creating invoice: {str(e)}")
            flash('Failed to create invoice.', 'error')
    
    # Get contacts for dropdown
    try:
        client = SageAPIClient(connection, business)
        contacts_data = client.get_contacts(contact_type='CUSTOMER')
        contacts = contacts_data.get('$items', [])
    except:
        contacts = []
    
    return render_template('sage/invoice_form.html', contacts=contacts, business=business)


# ============================================================================
# Quotes Routes
# ============================================================================

@bp.route('/quotes')
@login_required
def quotes():
    """List all sales quotes from Sage."""
    # Similar to invoices route
    status = SageAuthService.get_connection_status(current_user)
    
    if not status['connected'] or status['status'] != 'active':
        flash('Please connect to Sage first.', 'error')
        return redirect(url_for('sage.dashboard'))
    
    connection = SageConnection.query.get(status['connection_id'])
    business = SageBusiness.query.get(status['business_id'])
    
    page = request.args.get('page', 1, type=int)
    items_per_page = request.args.get('items_per_page', 20, type=int)
    
    try:
        client = SageAPIClient(connection, business)
        quotes_data = client.get_sales_quotes(page=page, items_per_page=items_per_page)
        
        return render_template(
            'sage/quotes.html',
            quotes=quotes_data.get('$items', []),
            page=page,
            items_per_page=items_per_page,
            business=business
        )
        
    except Exception as e:
        current_app.logger.error(f"Error loading quotes: {str(e)}")
        flash('Failed to load quotes from Sage.', 'error')
        return redirect(url_for('sage.dashboard'))


# ============================================================================
# Contacts Routes
# ============================================================================

@bp.route('/contacts')
@login_required
def contacts():
    """List all contacts from Sage."""
    status = SageAuthService.get_connection_status(current_user)

    if not status['connected'] or status['status'] != 'active':
        flash('Please connect to Sage first.', 'error')
        return redirect(url_for('sage.dashboard'))

    connection = SageConnection.query.get(status['connection_id'])
    business = SageBusiness.query.get(status['business_id'])

    page = request.args.get('page', 1, type=int)
    items_per_page = request.args.get('items_per_page', 20, type=int)
    contact_type = request.args.get('type')  # CUSTOMER, SUPPLIER, or None for all

    try:
        client = SageAPIClient(connection, business)
        contacts_data = client.get_contacts(
            page=page,
            items_per_page=items_per_page,
            contact_type=contact_type
        )

        return render_template(
            'sage/contacts.html',
            contacts=contacts_data.get('$items', []),
            page=page,
            items_per_page=items_per_page,
            contact_type=contact_type,
            business=business
        )

    except Exception as e:
        current_app.logger.error(f"Error loading contacts: {str(e)}")
        flash('Failed to load contacts from Sage.', 'error')
        return redirect(url_for('sage.dashboard'))


# ============================================================================
# Settings Route
# ============================================================================

@bp.route('/settings')
@login_required
def settings():
    """Sage integration settings and connection management."""
    status = SageAuthService.get_connection_status(current_user)

    connection = None
    business = None
    businesses = []

    if status['connected']:
        connection = SageConnection.query.get(status['connection_id'])
        if status['status'] == 'active':
            business = SageBusiness.query.get(status['business_id'])
        businesses = SageBusiness.query.filter_by(connection_id=connection.id).all()

    return render_template(
        'sage/settings.html',
        status=status,
        connection=connection,
        business=business,
        businesses=businesses
    )


# ============================================================================
# API Endpoints (for AJAX requests)
# ============================================================================

@bp.route('/api/status')
@login_required
def api_status():
    """Get Sage connection status (JSON)."""
    status = SageAuthService.get_connection_status(current_user)
    return jsonify(status)


@bp.route('/api/businesses')
@login_required
def api_businesses():
    """Get list of businesses (JSON)."""
    connection = SageConnection.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not connection:
        return jsonify({'error': 'No active connection'}), 404

    businesses = SageBusiness.query.filter_by(connection_id=connection.id).all()

    return jsonify({
        'businesses': [b.to_dict() for b in businesses]
    })


@bp.route('/api/select-business', methods=['POST'])
@login_required
def api_select_business():
    """Select a business (JSON)."""
    connection = SageConnection.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not connection:
        return jsonify({'error': 'No active connection'}), 404

    business_id = request.json.get('business_id')

    if not business_id:
        return jsonify({'error': 'business_id required'}), 400

    try:
        business = SageAuthService.select_business(connection, business_id)
        return jsonify({
            'success': True,
            'business': business.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

