"""
Laser OS Tier 1 - Flask Application Factory

This module creates and configures the Flask application instance.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
                          If None, uses FLASK_ENV environment variable or 'development'
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)

    # Phase 9: Initialize Flask-Mail for communication service
    from app.services.communication_service import init_mail
    init_mail(app)

    # Register blueprints
    from app.routes import main, clients, projects, products, files, queue, inventory, reports, quotes, invoices, comms
    app.register_blueprint(main.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(files.bp)
    app.register_blueprint(queue.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(quotes.bp)
    app.register_blueprint(invoices.bp)
    app.register_blueprint(comms.bp)  # Phase 9: Communications module

    # Placeholder blueprints (will be added in later phases)
    # from app.routes import inventory, reports, settings
    # app.register_blueprint(inventory.bp)
    # app.register_blueprint(reports.bp)
    # app.register_blueprint(settings.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Create placeholder routes for navigation (will be implemented in later phases)
    register_placeholder_routes(app)
    
    return app


def register_error_handlers(app):
    """Register error handlers for common HTTP errors."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors."""
        from flask import render_template
        return render_template('errors/403.html'), 403


def register_template_filters(app):
    """Register custom Jinja2 template filters."""
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format a datetime object."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%Y-%m-%d'):
        """Format a date object."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('currency')
    def format_currency(value):
        """Format a number as currency (ZAR)."""
        if value is None:
            return 'R 0.00'
        return f'R {value:,.2f}'
    
    @app.template_filter('filesize')
    def format_filesize(bytes):
        """Format bytes as human-readable file size."""
        if bytes is None:
            return '0 B'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f'{bytes:.1f} {unit}'
            bytes /= 1024.0
        return f'{bytes:.1f} TB'


def register_context_processors(app):
    """Register context processors to inject variables into templates."""
    
    @app.context_processor
    def inject_settings():
        """Inject common settings into all templates."""
        return {
            'company_name': app.config.get('COMPANY_NAME', 'Laser OS'),
            'current_year': __import__('datetime').datetime.now().year
        }


def register_placeholder_routes(app):
    """Register placeholder routes for features not yet implemented."""
    from flask import render_template, flash, redirect, url_for

    # Projects routes removed - now handled by projects blueprint (Phase 2)

    @app.route('/queue')
    def queue_index():
        flash('Queue feature coming in Phase 5', 'info')
        return redirect(url_for('main.dashboard'))
    
    @app.route('/inventory')
    def inventory_index():
        flash('Inventory feature coming in Phase 6', 'info')
        return redirect(url_for('main.dashboard'))
    
    @app.route('/reports')
    def reports_index():
        flash('Reports feature coming in Phase 7', 'info')
        return redirect(url_for('main.dashboard'))
    
    @app.route('/parameters')
    def parameters_index():
        flash('Parameters feature coming in Phase 7', 'info')
        return redirect(url_for('main.dashboard'))

