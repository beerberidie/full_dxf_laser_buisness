"""
Database Migration: Add MessageTemplate Table

This script adds the message_templates table to the database.
Run this after adding the MessageTemplate model to app/models/business.py

Usage:
    python scripts/migrate_add_message_templates.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import MessageTemplate


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text):
    """Print info message."""
    print(f"ℹ {text}")


def check_table_exists():
    """Check if message_templates table already exists."""
    try:
        # Try to query the table
        MessageTemplate.query.first()
        return True
    except Exception:
        return False


def create_message_templates_table():
    """Create the message_templates table."""
    print_header("Database Migration: Add MessageTemplate Table")
    
    print_info("Checking if message_templates table exists...")
    
    if check_table_exists():
        print_success("message_templates table already exists!")
        print_info("No migration needed.")
        return True
    
    print_info("Creating message_templates table...")
    
    try:
        # Create the table
        db.create_all()
        
        print_success("message_templates table created successfully!")
        
        # Verify table was created
        if check_table_exists():
            print_success("Table verification passed!")
            return True
        else:
            print_error("Table verification failed!")
            return False
            
    except Exception as e:
        print_error(f"Error creating table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main migration function."""
    app = create_app()
    
    with app.app_context():
        success = create_message_templates_table()
        
        if success:
            print_header("✓ Migration Complete!")
            print("\nThe message_templates table has been added to your database.")
            print("\nNext steps:")
            print("1. Run scripts/seed_message_templates.py to create default templates")
            print("2. Access template management at: http://127.0.0.1:5000/templates/")
            print("3. Start using templates in your communications!")
        else:
            print_header("✗ Migration Failed!")
            print("\nPlease check the error messages above and try again.")
            sys.exit(1)


if __name__ == '__main__':
    main()

