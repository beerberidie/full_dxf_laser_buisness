"""
Seed Message Templates Script

This script creates common message templates for the Laser OS application.
Run this after creating the message_templates table.

Usage:
    python scripts/seed_message_templates.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import MessageTemplate, User


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


def create_template(name, template_type, subject, body, description, admin_user):
    """Create a message template if it doesn't exist."""
    existing = MessageTemplate.query.filter_by(name=name).first()
    
    if existing:
        print_info(f"Template '{name}' already exists, skipping...")
        return existing
    
    template = MessageTemplate(
        name=name,
        template_type=template_type,
        subject_template=subject,
        body_template=body,
        description=description,
        is_active=True,
        created_by_id=admin_user.id if admin_user else None
    )
    
    db.session.add(template)
    print_success(f"Created template: {name}")
    return template


def seed_templates():
    """Seed common message templates."""
    print_header("Seeding Message Templates")
    
    # Get admin user (first admin or superuser)
    admin_user = User.query.filter(
        db.or_(
            User.is_superuser == True,
            User.roles.any(name='admin')
        )
    ).first()
    
    if not admin_user:
        print_info("No admin user found, templates will be created without creator")
    else:
        print_info(f"Using admin user: {admin_user.username}")
    
    templates_created = 0
    
    # Template 1: Collection Ready
    create_template(
        name="Collection Ready",
        template_type=MessageTemplate.TYPE_PROJECT_COMPLETE,
        subject="Your order {{project_code}} is ready for collection",
        body="""Dear {{client_contact}},

We are pleased to inform you that your order {{project_code}} - {{project_name}} has been completed and is ready for collection.

Order Details:
- Project Code: {{project_code}}
- Project Name: {{project_name}}
- Quantity: {{project_quantity}}
- Material: {{project_material}} ({{project_thickness}}mm)

Collection Information:
- Available from: {{collection_date}}
- Operating Hours: Mon-Thu 07:00-16:00, Fri 07:00-14:30
- Location: [Your Address]

Please contact us to arrange a convenient collection time.

Thank you for your business!

Best regards,
{{company_name}}""",
        description="Sent when a project is marked as complete and ready for collection",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 2: Order Confirmed
    create_template(
        name="Order Confirmed",
        template_type=MessageTemplate.TYPE_ORDER_CONFIRMED,
        subject="Order Confirmation - {{project_code}}",
        body="""Dear {{client_contact}},

Thank you for your order! We have received your proof of payment and your order has been confirmed.

Order Details:
- Project Code: {{project_code}}
- Project Name: {{project_name}}
- Quantity: {{project_quantity}}
- Material: {{project_material}} ({{project_thickness}}mm)
- Estimated Completion: {{collection_date}}

Your order has been added to our production queue and will be processed according to our standard lead time.

We will notify you once your order is complete and ready for collection.

If you have any questions, please don't hesitate to contact us.

Best regards,
{{company_name}}""",
        description="Sent when proof of payment is received and order is confirmed",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 3: Quote Sent
    create_template(
        name="Quote Sent",
        template_type=MessageTemplate.TYPE_QUOTE_SENT,
        subject="Quote {{quote_code}} for {{client_name}}",
        body="""Dear {{client_contact}},

Thank you for your interest in our laser cutting services.

Please find attached our quote {{quote_code}} for your project.

Quote Details:
- Quote Code: {{quote_code}}
- Total Amount: {{quote_total}}
- Valid Until: {{quote_valid_until}}

To proceed with this order:
1. Review the quote details
2. Confirm your acceptance
3. Submit proof of payment

Once we receive your payment confirmation, we will add your order to our production queue.

If you have any questions or would like to discuss the quote, please feel free to contact us.

Best regards,
{{company_name}}""",
        description="Sent when a quote is created and sent to a client",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 4: Invoice Sent
    create_template(
        name="Invoice Sent",
        template_type=MessageTemplate.TYPE_INVOICE_SENT,
        subject="Invoice {{invoice_code}} from {{company_name}}",
        body="""Dear {{client_contact}},

Please find attached invoice {{invoice_code}} for your recent order.

Invoice Details:
- Invoice Code: {{invoice_code}}
- Total Amount: {{invoice_total}}
- Due Date: {{invoice_due_date}}

Payment Methods:
[Add your payment methods here]

Please submit proof of payment once the invoice has been settled.

If you have any questions regarding this invoice, please contact us.

Thank you for your business!

Best regards,
{{company_name}}""",
        description="Sent when an invoice is created and sent to a client",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 5: Payment Reminder
    create_template(
        name="Payment Reminder",
        template_type=MessageTemplate.TYPE_PAYMENT_REMINDER,
        subject="Payment Reminder - Invoice {{invoice_code}}",
        body="""Dear {{client_contact}},

This is a friendly reminder that invoice {{invoice_code}} is due for payment.

Invoice Details:
- Invoice Code: {{invoice_code}}
- Total Amount: {{invoice_total}}
- Due Date: {{invoice_due_date}}

If you have already made payment, please disregard this message and submit your proof of payment for our records.

If you have any questions or concerns regarding this invoice, please contact us.

Thank you for your prompt attention to this matter.

Best regards,
{{company_name}}""",
        description="Sent as a reminder for outstanding invoices",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 6: Delivery Notification
    create_template(
        name="Delivery Notification",
        template_type=MessageTemplate.TYPE_DELIVERY_NOTIFICATION,
        subject="Delivery Notification - {{project_code}}",
        body="""Dear {{client_contact}},

Your order {{project_code}} is scheduled for delivery.

Delivery Details:
- Project Code: {{project_code}}
- Project Name: {{project_name}}
- Delivery Date: {{current_date}}

Please ensure someone is available to receive the delivery.

If you have any questions or need to reschedule, please contact us as soon as possible.

Thank you!

Best regards,
{{company_name}}""",
        description="Sent when an order is scheduled for delivery",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 7: Welcome Message
    create_template(
        name="Welcome New Client",
        template_type=MessageTemplate.TYPE_CUSTOM,
        subject="Welcome to {{company_name}}!",
        body="""Dear {{client_contact}},

Welcome to {{company_name}}!

We are excited to have you as a new client and look forward to serving your laser cutting needs.

Your client code is: {{client_code}}

Our Services:
- Precision laser cutting
- Wide range of materials
- Fast turnaround times
- Competitive pricing

Operating Hours:
Mon-Thu: 07:00-16:00
Fri: 07:00-14:30

If you have any questions or would like to discuss your project requirements, please don't hesitate to contact us.

Best regards,
{{company_name}}""",
        description="Sent to welcome new clients",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Template 8: Project Status Update
    create_template(
        name="Project Status Update",
        template_type=MessageTemplate.TYPE_CUSTOM,
        subject="Status Update - {{project_code}}",
        body="""Dear {{client_contact}},

We wanted to provide you with an update on your project {{project_code}}.

Project Details:
- Project Code: {{project_code}}
- Project Name: {{project_name}}
- Current Status: {{project_status}}

We are making good progress on your order and will notify you once it is complete.

If you have any questions, please feel free to contact us.

Best regards,
{{company_name}}""",
        description="Sent to provide clients with project status updates",
        admin_user=admin_user
    )
    templates_created += 1
    
    # Commit all templates
    db.session.commit()
    
    print_header(f"✓ Seeding Complete!")
    print(f"\nCreated {templates_created} message templates")
    print("\nTemplates created:")
    print("1. Collection Ready (project_complete)")
    print("2. Order Confirmed (order_confirmed)")
    print("3. Quote Sent (quote_sent)")
    print("4. Invoice Sent (invoice_sent)")
    print("5. Payment Reminder (payment_reminder)")
    print("6. Delivery Notification (delivery_notification)")
    print("7. Welcome New Client (custom)")
    print("8. Project Status Update (custom)")
    
    print("\nNext steps:")
    print("1. View templates at: http://127.0.0.1:5000/templates/")
    print("2. Edit templates to customize for your business")
    print("3. Use templates when sending communications")


def main():
    """Main seeding function."""
    app = create_app()
    
    with app.app_context():
        seed_templates()


if __name__ == '__main__':
    main()

