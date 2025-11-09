"""
Set Admin and Manager Roles

This script allows you to manually set admin and manager roles for specific users.
Run this after initialize_user_roles.py to assign proper roles.

Usage: python set_admin_roles.py
"""

from app import create_app, db
from app.models.auth import User

def set_roles():
    """Set admin and manager roles for specific users."""
    print("=" * 80)
    print("SET ADMIN AND MANAGER ROLES")
    print("=" * 80)
    
    app = create_app('development')
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        print(f"\nCurrent users:")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user.username:20} (current role: {user.role})")
        
        print("\n" + "=" * 80)
        print("RECOMMENDED ROLE ASSIGNMENTS")
        print("=" * 80)
        
        # Recommended assignments based on usernames
        print("\nBased on usernames, here are recommended role assignments:")
        print("\n  garason  → admin    (appears to be owner/administrator)")
        print("  kieran   → manager  (appears to be manager)")
        print("  dalan    → manager  (appears to be manager)")
        print("  operator1 → operator (production operator)")
        print("  viewer1  → operator (viewer/operator)")
        
        print("\n" + "-" * 80)
        response = input("\nApply these recommended roles? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            # Apply recommended roles
            garason = User.query.filter_by(username='garason').first()
            if garason:
                garason.role = 'admin'
                garason.display_name = 'Garason'
                print(f"✓ Set garason → admin")
            
            kieran = User.query.filter_by(username='kieran').first()
            if kieran:
                kieran.role = 'manager'
                kieran.display_name = 'Kieran'
                print(f"✓ Set kieran → manager")
            
            dalan = User.query.filter_by(username='dalan').first()
            if dalan:
                dalan.role = 'manager'
                dalan.display_name = 'Dalan'
                print(f"✓ Set dalan → manager")
            
            operator1 = User.query.filter_by(username='operator1').first()
            if operator1:
                operator1.role = 'operator'
                operator1.is_active_operator = True
                operator1.display_name = 'Operator 1'
                print(f"✓ Set operator1 → operator")
            
            viewer1 = User.query.filter_by(username='viewer1').first()
            if viewer1:
                viewer1.role = 'operator'
                viewer1.is_active_operator = True
                viewer1.display_name = 'Viewer 1'
                print(f"✓ Set viewer1 → operator")
            
            # Commit changes
            try:
                db.session.commit()
                print("\n" + "=" * 80)
                print("✅ SUCCESS: Roles updated")
                print("=" * 80)
                
                # Display final summary
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
                
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ ERROR: Failed to commit changes: {str(e)}")
                return False
        else:
            print("\n❌ Cancelled - no changes made")
            return False


if __name__ == '__main__':
    success = set_roles()
    exit(0 if success else 1)

