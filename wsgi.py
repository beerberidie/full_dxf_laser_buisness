"""
Laser OS Tier 1 - WSGI Entry Point

This module provides the WSGI application for production deployment.
"""

import os
from app import create_app

# Create app instance with production configuration
app = create_app('production')

if __name__ == '__main__':
    # Run with Waitress production server
    from waitress import serve
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    print(f'Starting Laser OS on {host}:{port}')
    serve(app, host=host, port=port)

