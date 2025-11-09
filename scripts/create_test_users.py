"""
Create Test User Accounts for Laser OS

This script creates test user accounts for each role:
- Operator: Can manage production (queue, runs, files)
- Viewer: Read-only access to all data

Run this script to populate the database with test users.
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.auth import User, Role, UserRole
from datetime import datetime

def create_test_users():
    """Create test user accounts for operator and viewer roles."""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("CREATING TEST USER ACCOUNTS")
        print("=" * 70)
        print()
        
        # Get roles
        operator_role = Role.query.filter_by(name='operator').first()
        viewer_role = Role.query.filter_by(name='viewer').first()
        
        if not operator_role or not viewer_role:
            print("❌ ERROR: Operator or Viewer role not found in database!")
            print("   Please run scripts/init_auth.py first to create roles.")
            return
        
        # Get admin user for assignment tracking
        admin_user = User.query.filter_by(username='garason').first()
        if not admin_user:
            admin_user = User.query.filter(User.has_role('admin')).first()
        
        admin_id = admin_user.id if admin_user else None
        
        # Create Operator User
        print("Creating Operator User...")
        print("-" * 70)
        
        operator_user = User.query.filter_by(username='operator1').first()
        if operator_user:
            print("⚠️  User 'operator1' already exists. Skipping creation.")
        else:
            operator_user = User(
                username='operator1',
                email='operator@laserco.com',
                full_name='Test Operator',
                is_active=True,
                is_superuser=False
            )
            operator_user.set_password('Operator123!')
            
            db.session.add(operator_user)
            db.session.flush()  # Get user ID
            
            # Assign operator role
            user_role = UserRole(
                user_id=operator_user.id,
                role_id=operator_role.id,
                assigned_by=admin_id
            )
            db.session.add(user_role)
            
            print(f"✅ Created operator user:")
            print(f"   Username: operator1")
            print(f"   Password: Operator123!")
            print(f"   Email: operator@laserco.com")
            print(f"   Full Name: Test Operator")
            print(f"   Role: {operator_role.display_name}")
        
        print()
        
        # Create Viewer User
        print("Creating Viewer User...")
        print("-" * 70)
        
        viewer_user = User.query.filter_by(username='viewer1').first()
        if viewer_user:
            print("⚠️  User 'viewer1' already exists. Skipping creation.")
        else:
            viewer_user = User(
                username='viewer1',
                email='viewer@laserco.com',
                full_name='Test Viewer',
                is_active=True,
                is_superuser=False
            )
            viewer_user.set_password('Viewer123!')
            
            db.session.add(viewer_user)
            db.session.flush()  # Get user ID
            
            # Assign viewer role
            user_role = UserRole(
                user_id=viewer_user.id,
                role_id=viewer_role.id,
                assigned_by=admin_id
            )
            db.session.add(user_role)
            
            print(f"✅ Created viewer user:")
            print(f"   Username: viewer1")
            print(f"   Password: Viewer123!")
            print(f"   Email: viewer@laserco.com")
            print(f"   Full Name: Test Viewer")
            print(f"   Role: {viewer_role.display_name}")
        
        print()
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 70)
        print("TEST USERS CREATED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Summary of all test users:")
        print("-" * 70)
        
        # List all users
        all_users = User.query.order_by(User.username).all()
        for user in all_users:
            roles = [role.display_name for role in user.roles.all()]
            role_str = ', '.join(roles) if roles else 'No roles'
            status = "Active" if user.is_active else "Inactive"
            superuser = " (SUPERUSER)" if user.is_superuser else ""
            
            print(f"  • {user.username:15} - {role_str:20} - {status}{superuser}")
        
        print()
        print("=" * 70)
        print("READY FOR TESTING!")
        print("=" * 70)
        print()
        print("You can now test the authentication system with these accounts:")
        print()
        print("1. ADMIN (Full Access):")
        print("   Username: garason")
        print("   Password: Admin123!")
        print()
        print("2. MANAGER (Business Management):")
        print("   Username: kieran")
        print("   Password: Manager123!")
        print()
        print("3. OPERATOR (Production Management):")
        print("   Username: operator1")
        print("   Password: Operator123!")
        print()
        print("4. VIEWER (Read-Only Access):")
        print("   Username: viewer1")
        print("   Password: Viewer123!")
        print()
        print("=" * 70)


if __name__ == '__main__':
    create_test_users()

