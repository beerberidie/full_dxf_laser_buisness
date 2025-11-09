#!/usr/bin/env python
"""
Reset test user password for development/testing
"""
from app import create_app, db
from app.models.auth import User

def reset_password():
    """Reset the garason user password to 'test123' for easy testing."""
    app = create_app('development')
    
    with app.app_context():
        # Find the user
        user = User.query.filter_by(username='garason').first()
        
        if not user:
            print("❌ User 'garason' not found!")
            return
        
        # Reset password
        user.set_password('test123')
        db.session.commit()
        
        print("✅ Password reset successful!")
        print("")
        print("=" * 50)
        print("TEST LOGIN CREDENTIALS")
        print("=" * 50)
        print("Username: garason")
        print("Password: test123")
        print("=" * 50)
        print("")
        print("You can now log in at: http://127.0.0.1:5000/auth/login")

if __name__ == '__main__':
    reset_password()

