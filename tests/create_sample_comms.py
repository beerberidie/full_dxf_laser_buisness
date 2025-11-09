"""
Create sample communications data for testing the Communications module.

This script creates:
- 5 Email communications (to test Gmail/Outlook tabs)
- 3 WhatsApp communications
- 2 Notifications
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Communication, Client, Project
from datetime import datetime, timedelta
import random

def create_sample_communications():
    """Create sample communications for testing."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("CREATING SAMPLE COMMUNICATIONS DATA")
        print("="*70)
        
        # Check if we already have data
        existing_count = Communication.query.count()
        if existing_count > 0:
            print(f"\n⚠️  WARNING: {existing_count} communications already exist.")
            response = input("Do you want to create more sample data? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        # Get first client and project (if they exist)
        client = Client.query.first()
        project = Project.query.first()
        
        if not client:
            print("\n⚠️  WARNING: No clients found in database.")
            print("Creating a sample client...")
            client = Client(
                name="Sample Client Ltd",
                email="client@example.com",
                phone="0123456789",
                address="123 Sample Street"
            )
            db.session.add(client)
            db.session.commit()
            print(f"✓ Created client: {client.name}")
        
        if not project:
            print("\n⚠️  WARNING: No projects found in database.")
            print("Creating a sample project...")
            project = Project(
                project_code="PROJ-001",
                name="Sample Project",
                client_id=client.id,
                status="Quote & Approval"
            )
            db.session.add(project)
            db.session.commit()
            print(f"✓ Created project: {project.project_code}")
        
        communications = []
        
        # Create 5 Email communications
        print("\n✓ Creating Email communications...")
        email_subjects = [
            "Quote Request - Laser Cutting Services",
            "RE: Project Update Required",
            "Invoice #12345 - Payment Confirmation",
            "Delivery Schedule for Order #789",
            "Technical Specifications Clarification"
        ]
        
        for i, subject in enumerate(email_subjects):
            comm = Communication(
                comm_type='Email',
                direction='Inbound' if i % 2 == 0 else 'Outbound',
                client_id=client.id if i < 3 else None,
                project_id=project.id if i < 2 else None,
                subject=subject,
                body=f"This is a sample email body for {subject}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                from_address='client@example.com' if i % 2 == 0 else 'sales@laseros.com',
                to_address='sales@laseros.com' if i % 2 == 0 else 'client@example.com',
                status='Pending' if i < 2 else 'Sent',
                is_linked=i < 3,
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            communications.append(comm)
            db.session.add(comm)
        
        print(f"  ✓ Created {len(email_subjects)} Email communications")
        
        # Create 3 WhatsApp communications
        print("\n✓ Creating WhatsApp communications...")
        whatsapp_messages = [
            "Hi, I need a quote for laser cutting",
            "When will my order be ready?",
            "Thank you for the quick service!"
        ]
        
        for i, message in enumerate(whatsapp_messages):
            comm = Communication(
                comm_type='WhatsApp',
                direction='Inbound' if i % 2 == 0 else 'Outbound',
                client_id=client.id,
                project_id=project.id if i == 0 else None,
                subject=None,  # WhatsApp doesn't have subjects
                body=message,
                from_address='+27123456789' if i % 2 == 0 else '+27987654321',
                to_address='+27987654321' if i % 2 == 0 else '+27123456789',
                status='Delivered',
                is_linked=i == 0,
                created_at=datetime.utcnow() - timedelta(hours=i*2)
            )
            communications.append(comm)
            db.session.add(comm)
        
        print(f"  ✓ Created {len(whatsapp_messages)} WhatsApp communications")
        
        # Create 2 Notifications
        print("\n✓ Creating Notification communications...")
        notifications = [
            "New quote request received from Sample Client Ltd",
            "Project PROJ-001 status changed to In Progress"
        ]
        
        for i, message in enumerate(notifications):
            comm = Communication(
                comm_type='Notification',
                direction='Outbound',
                client_id=client.id if i == 0 else None,
                project_id=project.id,
                subject=message,
                body=f"System notification: {message}",
                from_address='system@laseros.com',
                to_address='admin@laseros.com',
                status='Sent',
                is_linked=True,
                created_at=datetime.utcnow() - timedelta(minutes=i*30)
            )
            communications.append(comm)
            db.session.add(comm)
        
        print(f"  ✓ Created {len(notifications)} Notification communications")
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "="*70)
            print("✅ SUCCESS: Sample data created successfully!")
            print("="*70)
            
            # Summary
            total = Communication.query.count()
            email_count = Communication.query.filter_by(comm_type='Email').count()
            whatsapp_count = Communication.query.filter_by(comm_type='WhatsApp').count()
            notification_count = Communication.query.filter_by(comm_type='Notification').count()
            
            print(f"\n📊 Database Summary:")
            print(f"  • Total communications: {total}")
            print(f"  • Email: {email_count}")
            print(f"  • WhatsApp: {whatsapp_count}")
            print(f"  • Notification: {notification_count}")
            
            print(f"\n✅ Next steps:")
            print(f"   1. Navigate to http://127.0.0.1:5000/communications")
            print(f"   2. Click the Gmail tab - should show {email_count} emails with Gmail badge")
            print(f"   3. Click the Outlook tab - should show {email_count} emails with Outlook badge")
            print(f"   4. Click the WhatsApp tab - should show {whatsapp_count} messages")
            print(f"   5. Verify no AttributeError occurs")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to create sample data: {str(e)}")
            return False
        
        return True


if __name__ == '__main__':
    success = create_sample_communications()
    sys.exit(0 if success else 1)

