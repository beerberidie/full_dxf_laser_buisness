"""
Initialize Authentication System for Laser OS Tier 1

This script initializes the authentication system by:
1. Creating authentication database tables
2. Creating default roles (admin, manager, operator, viewer)
3. Creating initial user accounts (garason, kieran, dalan)

Usage:
    python scripts/init_auth.py
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.auth import User, Role, UserRole
from datetime import datetime


def create_roles():
    """
    Create default roles with permissions.
    
    Returns:
        dict: Dictionary of role objects keyed by role name
    """
    print("\n📋 Creating roles...")
    
    roles_data = {
        'admin': {
            'display_name': 'Administrator',
            'description': 'Full system access including user management and settings',
            'permissions': [
                'view_all',
                'create_all',
                'edit_all',
                'delete_all',
                'manage_users',
                'manage_settings',
                'view_logs',
                'export_data'
            ]
        },
        'manager': {
            'display_name': 'Manager',
            'description': 'Business operations access without user management',
            'permissions': [
                'view_all',
                'create_business',
                'edit_business',
                'delete_business',
                'view_logs',
                'export_data',
                'manage_quotes',
                'manage_invoices'
            ]
        },
        'operator': {
            'display_name': 'Operator',
            'description': 'Production operations access',
            'permissions': [
                'view_all',
                'edit_production',
                'manage_queue',
                'upload_files',
                'run_laser'
            ]
        },
        'viewer': {
            'display_name': 'Viewer',
            'description': 'Read-only access to all data',
            'permissions': [
                'view_all'
            ]
        }
    }
    
    roles = {}
    
    for role_name, role_info in roles_data.items():
        # Check if role already exists
        role = Role.query.filter_by(name=role_name).first()
        
        if role:
            print(f"  ✓ Role '{role_name}' already exists")
        else:
            role = Role(
                name=role_name,
                display_name=role_info['display_name'],
                description=role_info['description']
            )
            role.set_permissions(role_info['permissions'])
            db.session.add(role)
            print(f"  ✓ Created role '{role_name}' ({role_info['display_name']})")
        
        roles[role_name] = role
    
    db.session.commit()
    print("✅ Roles created successfully\n")
    
    return roles


def create_initial_users(roles):
    """
    Create initial user accounts.
    
    Args:
        roles (dict): Dictionary of role objects
    """
    print("👥 Creating initial users...")
    
    users_data = [
        {
            'username': 'garason',
            'email': 'garason@laserco.com',
            'full_name': 'Garason Griesel',
            'role': 'admin',
            'password': 'Admin123!',
            'is_superuser': True
        },
        {
            'username': 'kieran',
            'email': 'kieran@laserco.com',
            'full_name': 'Kieran',
            'role': 'manager',
            'password': 'Manager123!',
            'is_superuser': False
        },
        {
            'username': 'dalan',
            'email': 'dalan@laserco.com',
            'full_name': 'Dalan',
            'role': 'manager',
            'password': 'Manager123!',
            'is_superuser': False
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Check if user already exists
        user = User.query.filter_by(username=user_data['username']).first()
        
        if user:
            print(f"  ⚠️  User '{user_data['username']}' already exists - skipping")
            continue
        
        # Create user
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            is_active=True,
            is_superuser=user_data['is_superuser'],
            created_at=datetime.utcnow()
        )
        
        # Set password
        user.set_password(user_data['password'])
        
        # Add to session
        db.session.add(user)
        db.session.flush()  # Flush to get user.id
        
        # Assign role
        role = roles[user_data['role']]
        user.roles.append(role)
        
        created_users.append({
            'username': user_data['username'],
            'password': user_data['password'],
            'role': user_data['role']
        })
        
        print(f"  ✓ Created user '{user_data['username']}' ({user_data['full_name']}) - Role: {user_data['role']}")
    
    db.session.commit()
    print("✅ Users created successfully\n")
    
    return created_users


def display_credentials(created_users):
    """
    Display login credentials for created users.
    
    Args:
        created_users (list): List of created user dictionaries
    """
    if not created_users:
        print("ℹ️  No new users were created (all users already exist)\n")
        return
    
    print("=" * 70)
    print("🔐 LOGIN CREDENTIALS")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Save these credentials securely!\n")
    print("These are temporary passwords. Users should change them on first login.\n")
    
    for user in created_users:
        print(f"Username: {user['username']}")
        print(f"Password: {user['password']}")
        print(f"Role:     {user['role']}")
        print("-" * 70)
    
    print("\n✅ Authentication system initialized successfully!")
    print("\nNext steps:")
    print("1. Start the application: python run.py")
    print("2. Navigate to: http://127.0.0.1:5000/auth/login")
    print("3. Log in with one of the accounts above")
    print("4. Change your password immediately")
    print("\n" + "=" * 70 + "\n")


def main():
    """Main initialization function."""
    print("\n" + "=" * 70)
    print("🚀 LASER OS TIER 1 - AUTHENTICATION SYSTEM INITIALIZATION")
    print("=" * 70)
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        print("\n📦 Creating database tables...")

        # Import all models to ensure tables are created
        from app.models.auth import User, Role, UserRole, LoginHistory

        # Drop existing auth tables if they exist (to ensure clean schema)
        print("  Dropping existing auth tables (if any)...")
        db.session.execute(db.text('DROP TABLE IF EXISTS login_history'))
        db.session.execute(db.text('DROP TABLE IF EXISTS user_roles'))
        db.session.execute(db.text('DROP TABLE IF EXISTS users'))
        db.session.execute(db.text('DROP TABLE IF EXISTS roles'))
        db.session.commit()
        print("  ✓ Old tables dropped")

        # Create all tables
        db.create_all()
        print("✅ Database tables created\n")
        
        # Create roles
        roles = create_roles()
        
        # Create initial users
        created_users = create_initial_users(roles)
        
        # Display credentials
        display_credentials(created_users)


if __name__ == '__main__':
    main()

