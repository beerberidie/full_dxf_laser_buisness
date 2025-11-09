"""
Performance Monitoring Middleware for Laser OS Tier 1

Tracks request performance metrics including:
- Total request time
- Database query count
- Database query time
- Template render time
"""

import time
import logging
from logging.handlers import RotatingFileHandler
from flask import g, request
from functools import wraps

# Performance logger will be configured in init_performance_monitoring
performance_logger = None


def init_performance_monitoring(app):
    """Initialize performance monitoring for the Flask application."""

    global performance_logger

    # Configure performance logger with rotating file handler
    performance_logger = logging.getLogger('performance')
    performance_logger.setLevel(logging.INFO)

    # Create rotating file handler
    log_file = app.config.get('LOG_FILE', 'logs/laser_os.log').replace('laser_os.log', 'performance.log')
    max_bytes = app.config.get('LOG_MAX_BYTES', 10485760)  # 10MB
    backup_count = app.config.get('LOG_BACKUP_COUNT', 10)

    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger (avoid duplicates)
    if not performance_logger.handlers:
        performance_logger.addHandler(handler)

    @app.before_request
    def before_request():
        """Record request start time and initialize query counter."""
        g.start_time = time.time()
        g.query_count = 0
        g.query_time = 0.0
    
    @app.after_request
    def after_request(response):
        """Log performance metrics after request completes."""
        
        # Skip static files and health checks
        if request.path.startswith('/static') or request.path == '/health':
            return response
        
        # Calculate total request time
        total_time = (time.time() - g.start_time) * 1000  # Convert to milliseconds
        
        # Get query metrics (if available)
        query_count = getattr(g, 'query_count', 0)
        query_time = getattr(g, 'query_time', 0.0) * 1000  # Convert to milliseconds
        
        # Calculate render time (total - query time)
        render_time = total_time - query_time
        
        # Log performance metrics
        performance_logger.info(
            f"PERFORMANCE | Route: {request.path} | "
            f"Load Time: {total_time:.0f}ms | "
            f"Queries: {query_count} | "
            f"DB Time: {query_time:.0f}ms | "
            f"Render Time: {render_time:.0f}ms | "
            f"Total: {total_time:.0f}ms"
        )
        
        # Add performance headers (for debugging)
        if app.config.get('DEBUG'):
            response.headers['X-Request-Time'] = f"{total_time:.0f}ms"
            response.headers['X-Query-Count'] = str(query_count)
            response.headers['X-Query-Time'] = f"{query_time:.0f}ms"
        
        return response


def track_query_performance(func):
    """Decorator to track database query performance."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Record query start time
        start_time = time.time()
        
        # Execute query
        result = func(*args, **kwargs)
        
        # Calculate query time
        query_time = time.time() - start_time
        
        # Update global query metrics
        if hasattr(g, 'query_count'):
            g.query_count += 1
            g.query_time += query_time
        
        return result
    
    return wrapper


def log_slow_query(query, duration_ms, threshold_ms=100):
    """Log slow queries that exceed the threshold."""
    
    if duration_ms > threshold_ms:
        performance_logger.warning(
            f"SLOW QUERY | Duration: {duration_ms:.0f}ms | Query: {query[:200]}"
        )


# SQLAlchemy event listeners for query tracking
def setup_sqlalchemy_listeners(db):
    """Set up SQLAlchemy event listeners to track query performance."""
    
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Record query start time."""
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Record query end time and update metrics."""
        
        # Calculate query duration
        start_time = conn.info['query_start_time'].pop(-1)
        duration = time.time() - start_time
        duration_ms = duration * 1000
        
        # Update global query metrics
        if hasattr(g, 'query_count'):
            g.query_count += 1
            g.query_time += duration
        
        # Log slow queries
        log_slow_query(statement, duration_ms)

