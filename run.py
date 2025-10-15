"""
Laser OS Tier 1 - Development Server

This script runs the Flask development server and provides CLI commands.
"""

import os
import sqlite3
from app import create_app, db

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.cli.command()
def init_db():
    """Initialize the database with schema."""
    print('Initializing database...')
    
    db_path = app.config['DATABASE_PATH']
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Run schema
    with open('migrations/schema_v1.sql', 'r') as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.close()
    
    print(f'✓ Database initialized at {db_path}')


@app.cli.command()
def seed_db():
    """Seed the database with initial data."""
    print('Seeding database...')
    
    db_path = app.config['DATABASE_PATH']
    
    # Run seed data
    with open('migrations/seed_data.sql', 'r') as f:
        seed_sql = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.executescript(seed_sql)
    conn.close()
    
    print('✓ Database seeded successfully')


@app.cli.command()
def reset_db():
    """Reset the database (drop all tables and recreate)."""
    print('Resetting database...')
    
    db_path = app.config['DATABASE_PATH']
    
    # Delete existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print('✓ Existing database removed')
    
    # Reinitialize
    init_db.callback()
    seed_db.callback()
    
    print('✓ Database reset complete')


@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell."""
    from app.models import Client, ActivityLog, Setting
    
    return {
        'db': db,
        'Client': Client,
        'ActivityLog': ActivityLog,
        'Setting': Setting
    }


if __name__ == '__main__':
    # Run development server
    app.run(host='0.0.0.0', port=5000, debug=True)

