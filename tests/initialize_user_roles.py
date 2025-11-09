"""
Initialize User Roles for Production Automation

This script sets up user roles for the Production Automation system.
Run this script once after the database migration to assign roles to existing users.

Usage: python initialize_user_roles.py
"""

from app import create_app, db
from app.models.auth import User

def initialize_roles():
    """Initialize user roles for Production Automation."""
    print("=" * 80)
    print("INITIALIZING USER ROLES FOR PRODUCTION AUTOMATION")
    print("=" * 80)
    
    app = create_app('development')
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        if not users:
            print("\n⚠️  No users found in database")
            print("Please create users first before running this script")
            return False
        
        print(f"\nFound {len(users)} user(s) in database")
        print("\nCurrent users:")
        for user in users:
            print(f"  - {user.username} (email: {user.email})")
        
        print("\n" + "=" * 80)
        print("ROLE ASSIGNMENT")
        print("=" * 80)
        print("\nRoles available:")
        print("  1. admin    - Full access to all modules")
        print("  2. manager  - Dashboard, Projects, Queue, Reports, Communications")
        print("  3. operator - Phone Mode only, can log production runs")
        
        print("\n" + "-" * 80)
        
        # Auto-assign roles based on username patterns
        updated_count = 0
        
        for user in users:
            username_lower = user.username.lower()
            
            # Determine role based on username
            if 'admin' in username_lower or 'administrator' in username_lower:
                user.role = 'admin'
                user.display_name = user.username.title()
                print(f"✓ {user.username:20} → admin")
                updated_count += 1
                
            elif 'manager' in username_lower or 'supervisor' in username_lower:
                user.role = 'manager'
                user.display_name = user.username.title()
                print(f"✓ {user.username:20} → manager")
                updated_count += 1
                
            elif 'operator' in username_lower or 'worker' in username_lower:
                user.role = 'operator'
                user.is_active_operator = True
                user.display_name = user.username.title()
                print(f"✓ {user.username:20} → operator (active)")
                updated_count += 1
                
            else:
                # Default to operator for unknown users
                user.role = 'operator'
                user.is_active_operator = True
                user.display_name = user.username.title()
                print(f"✓ {user.username:20} → operator (default)")
                updated_count += 1
        
        # Commit changes
        try:
            db.session.commit()
            print("\n" + "=" * 80)
            print(f"✅ SUCCESS: Updated {updated_count} user(s)")
            print("=" * 80)
            
            # Display final role summary
            print("\nFinal role assignments:")
            admins = User.query.filter_by(role='admin').all()
            managers = User.query.filter_by(role='manager').all()
            operators = User.query.filter_by(role='operator').all()
            
            print(f"\n  Admins ({len(admins)}):")
            for user in admins:
                print(f"    - {user.username} ({user.display_name})")
            
            print(f"\n  Managers ({len(managers)}):")
            for user in managers:
                print(f"    - {user.username} ({user.display_name})")
            
            print(f"\n  Operators ({len(operators)}):")
            for user in operators:
                active = "✓ active" if user.is_active_operator else "✗ inactive"
                print(f"    - {user.username} ({user.display_name}) [{active}]")
            
            print("\n" + "=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            print("\n1. Start the application:")
            print("   python run.py")
            print("\n2. Login with any user account")
            print("\n3. You will be redirected to mode selection:")
            print("   - Operators: Select 'Phone Mode'")
            print("   - Managers/Admins: Select 'PC Mode'")
            print("\n4. Test the features:")
            print("   - Phone Mode: Start/end runs")
            print("   - Notifications: Click bell icon")
            print("   - Daily Reports: Reports → Daily Reports")
            print("   - Drafts: Communications → Drafts")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to commit changes: {str(e)}")
            return False


if __name__ == '__main__':
    success = initialize_roles()
    exit(0 if success else 1)

