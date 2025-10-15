"""
Laser OS Tier 1 - Phase 1 Setup Script

This script sets up the Phase 1 environment:
1. Creates necessary directories
2. Initializes the database
3. Seeds initial data
4. Verifies the setup
"""

import os
import sys
import sqlite3
from pathlib import Path


def create_directories():
    """Create necessary directories for the application."""
    print("Creating directories...")
    
    directories = [
        'data',
        'data/files',
        'data/files/clients',
        'data/files/reports',
        'instance',
        'app/templates/clients',
        'app/templates/errors',
        'app/static/css',
        'app/static/js',
        'logs',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {directory}")
    
    print("✅ Directories created successfully\n")


def create_env_file():
    """Create .env file if it doesn't exist."""
    print("Checking .env file...")
    
    if Path('.env').exists():
        print("  ℹ .env file already exists\n")
        return
    
    if not Path('.env.example').exists():
        print("  ⚠ .env.example not found, skipping\n")
        return
    
    # Copy .env.example to .env
    with open('.env.example', 'r') as src:
        content = src.read()
    
    with open('.env', 'w') as dst:
        dst.write(content)
    
    print("  ✓ Created .env from .env.example")
    print("  ⚠ Please edit .env and set your SECRET_KEY for production\n")


def initialize_database():
    """Initialize the database with schema and seed data."""
    print("Initializing database...")
    
    db_path = Path('data/laser_os.db')
    
    # Remove existing database if it exists
    if db_path.exists():
        response = input("  Database already exists. Recreate? (y/N): ")
        if response.lower() != 'y':
            print("  ℹ Keeping existing database\n")
            return
        db_path.unlink()
        print("  ✓ Removed existing database")
    
    # Create database
    conn = sqlite3.connect(str(db_path))
    
    # Run schema
    print("  Running schema...")
    with open('migrations/schema_v1.sql', 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    print("  ✓ Schema created")
    
    # Run seed data
    print("  Running seed data...")
    with open('migrations/seed_data.sql', 'r') as f:
        seed_sql = f.read()
    conn.executescript(seed_sql)
    print("  ✓ Seed data inserted")
    
    conn.close()
    print("✅ Database initialized successfully\n")


def verify_setup():
    """Verify that the setup was successful."""
    print("Verifying setup...")
    
    # Check directories
    required_dirs = ['data', 'data/files', 'app/templates', 'app/static']
    for directory in required_dirs:
        if not Path(directory).exists():
            print(f"  ✗ Missing directory: {directory}")
            return False
    print("  ✓ All required directories exist")
    
    # Check database
    db_path = Path('data/laser_os.db')
    if not db_path.exists():
        print("  ✗ Database not found")
        return False
    print("  ✓ Database exists")
    
    # Check database tables
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    required_tables = ['clients', 'activity_log', 'settings', 'materials']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in required_tables:
        if table not in tables:
            print(f"  ✗ Missing table: {table}")
            conn.close()
            return False
    print("  ✓ All required tables exist")
    
    # Check seed data
    cursor.execute("SELECT COUNT(*) FROM settings")
    settings_count = cursor.fetchone()[0]
    if settings_count == 0:
        print("  ✗ No seed data found")
        conn.close()
        return False
    print(f"  ✓ Seed data loaded ({settings_count} settings)")
    
    cursor.execute("SELECT COUNT(*) FROM materials")
    materials_count = cursor.fetchone()[0]
    print(f"  ✓ Materials loaded ({materials_count} materials)")
    
    conn.close()
    
    print("✅ Setup verified successfully\n")
    return True


def print_next_steps():
    """Print next steps for the user."""
    print("=" * 60)
    print("PHASE 1 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print()
    print("2. Install dependencies (if not already done):")
    print("   pip install -r requirements.txt")
    print()
    print("3. Run the development server:")
    print("   python run.py")
    print()
    print("4. Open your browser and navigate to:")
    print("   http://localhost:5000")
    print()
    print("5. Run tests:")
    print("   pytest")
    print()
    print("For more information, see PHASE1_README.md")
    print("=" * 60)


def main():
    """Main setup function."""
    print()
    print("=" * 60)
    print("LASER OS TIER 1 - PHASE 1 SETUP")
    print("=" * 60)
    print()
    
    try:
        create_directories()
        create_env_file()
        initialize_database()
        
        if verify_setup():
            print_next_steps()
            return 0
        else:
            print("❌ Setup verification failed")
            return 1
    
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

