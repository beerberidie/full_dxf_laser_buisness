#!/usr/bin/env python
"""
Phase 10 Migration Script
Adds user_id column to operators table for user account linking.

Usage:
    python run_phase10_migration.py
"""

from app import create_app, db

def run_migration():
    """Execute Phase 10 migration."""
    app = create_app()
    
    with app.app_context():
        print("Starting Phase 10 migration...")
        
        # Read migration SQL
        with open('migrations/schema_v10_operator_user_link.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        try:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
            
            for statement in statements:
                print(f"Executing: {statement[:50]}...")
                db.session.execute(db.text(statement))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   - Added user_id column to operators table")
            print("   - Created index on user_id")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    run_migration()

