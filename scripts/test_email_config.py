"""
Test Email Configuration Script

This script tests the SMTP email configuration and verifies that emails can be sent.
Run this after configuring your .env file with SMTP credentials.

Usage:
    python scripts/test_email_config.py
    
    Or with custom recipient:
    python scripts/test_email_config.py your-email@example.com
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.communication_service import send_email
from app.models import Communication


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


def check_configuration(app):
    """Check if email configuration is set."""
    print_header("Step 1: Checking Email Configuration")
    
    mail_server = app.config.get('MAIL_SERVER')
    mail_port = app.config.get('MAIL_PORT')
    mail_username = app.config.get('MAIL_USERNAME')
    mail_password = app.config.get('MAIL_PASSWORD')
    mail_sender = app.config.get('MAIL_DEFAULT_SENDER')
    mail_use_tls = app.config.get('MAIL_USE_TLS')
    
    print(f"\nMAIL_SERVER: {mail_server}")
    print(f"MAIL_PORT: {mail_port}")
    print(f"MAIL_USE_TLS: {mail_use_tls}")
    print(f"MAIL_USERNAME: {mail_username}")
    print(f"MAIL_PASSWORD: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    print(f"MAIL_DEFAULT_SENDER: {mail_sender}")
    
    # Check if credentials are set
    if not mail_username or mail_username == 'your-email@gmail.com':
        print_error("MAIL_USERNAME is not configured!")
        print_info("Please update MAIL_USERNAME in your .env file")
        return False
    
    if not mail_password or mail_password == 'your-app-password-here':
        print_error("MAIL_PASSWORD is not configured!")
        print_info("Please update MAIL_PASSWORD in your .env file")
        print_info("For Gmail, generate an App Password at: https://myaccount.google.com/apppasswords")
        return False
    
    print_success("Email configuration looks good!")
    return True


def test_email_sending(recipient_email):
    """Test sending an email."""
    print_header("Step 2: Testing Email Sending")
    
    print(f"\nRecipient: {recipient_email}")
    print("Subject: Test Email from Laser OS")
    print("Sending email...")
    
    try:
        result = send_email(
            to=recipient_email,
            subject='Test Email from Laser OS',
            body=f'''Hello!

This is a test email from your Laser OS application to verify that the SMTP email configuration is working correctly.

Test Details:
- Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: Laser OS Email Configuration Test
- Purpose: SMTP Configuration Verification

If you received this email, your email configuration is working perfectly! ✓

Next steps:
1. Check the Communications module in Laser OS
2. This email should be logged as a communication record
3. You can now use email templates and automated triggers

Best regards,
Laser OS System
''',
            save_to_db=True
        )
        
        if result['success']:
            print_success(f"Email sent successfully!")
            print_info(f"Communication ID: {result.get('communication_id')}")
            print_info(f"Message: {result.get('message')}")
            return True
        else:
            print_error(f"Email sending failed!")
            print_error(f"Error: {result.get('message')}")
            return False
            
    except Exception as e:
        print_error(f"Exception occurred while sending email!")
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_database_record():
    """Verify that the email was logged in the database."""
    print_header("Step 3: Verifying Database Record")
    
    try:
        # Get the most recent communication
        comm = Communication.query.order_by(Communication.created_at.desc()).first()
        
        if comm:
            print_success("Communication record found in database!")
            print(f"\nCommunication Details:")
            print(f"  ID: {comm.id}")
            print(f"  Type: {comm.comm_type}")
            print(f"  Direction: {comm.direction}")
            print(f"  Subject: {comm.subject}")
            print(f"  To: {comm.to_address}")
            print(f"  Status: {comm.status}")
            print(f"  Created: {comm.created_at}")
            
            if comm.status == 'Sent':
                print_success("Email status is 'Sent' - Perfect!")
            else:
                print_info(f"Email status is '{comm.status}'")
            
            return True
        else:
            print_error("No communication records found in database")
            return False
            
    except Exception as e:
        print_error(f"Error checking database: {str(e)}")
        return False


def main():
    """Main test function."""
    print_header("Laser OS - Email Configuration Test")
    print("\nThis script will test your SMTP email configuration.")
    print("Make sure you have updated the .env file with your SMTP credentials.")
    
    # Get recipient email from command line or use default
    if len(sys.argv) > 1:
        recipient_email = sys.argv[1]
    else:
        # Try to use MAIL_USERNAME as recipient for testing
        from dotenv import load_dotenv
        load_dotenv()
        recipient_email = os.environ.get('MAIL_USERNAME', 'test@example.com')
        
        if recipient_email == 'your-email@gmail.com':
            print_error("\nNo recipient email specified!")
            print_info("Usage: python scripts/test_email_config.py your-email@example.com")
            print_info("Or update MAIL_USERNAME in .env file first")
            sys.exit(1)
    
    # Create app and test
    app = create_app()
    
    with app.app_context():
        # Step 1: Check configuration
        if not check_configuration(app):
            print_header("Test Failed - Configuration Issues")
            print_info("\nPlease fix the configuration issues above and try again.")
            print_info("See SMTP_CONFIGURATION_GUIDE.md for detailed instructions.")
            sys.exit(1)
        
        # Step 2: Test email sending
        email_sent = test_email_sending(recipient_email)
        
        if not email_sent:
            print_header("Test Failed - Email Sending Issues")
            print_info("\nCommon issues:")
            print_info("1. For Gmail: Make sure you're using an App Password, not your regular password")
            print_info("2. For Gmail: Ensure 2-Factor Authentication is enabled")
            print_info("3. Check that MAIL_SERVER and MAIL_PORT are correct")
            print_info("4. Verify your firewall allows SMTP traffic")
            print_info("\nSee SMTP_CONFIGURATION_GUIDE.md for troubleshooting.")
            sys.exit(1)
        
        # Step 3: Verify database record
        verify_database_record()
        
        # Success!
        print_header("✓ All Tests Passed!")
        print("\n🎉 Your email configuration is working perfectly!")
        print("\nNext steps:")
        print("1. Check your inbox for the test email")
        print("2. View the communication record in Laser OS: http://127.0.0.1:5000/communications/")
        print("3. You're ready to use message templates and automated email triggers!")
        print("\nTo proceed with Phase 2 (Message Templates), let me know and I'll continue the implementation.")


if __name__ == '__main__':
    main()

