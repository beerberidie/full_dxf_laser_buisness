"""
Communication Service for Laser OS.

This service handles sending communications (emails, WhatsApp, notifications)
and logging them in the database.

Phase 9 Implementation.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from flask import current_app, render_template_string
from flask_mail import Mail, Message

from app import db
from app.models import Communication, Client, Project
from app.services.activity_logger import log_activity


# Global Mail instance (initialized in app factory)
mail = None


def init_mail(app):
    """
    Initialize Flask-Mail with the app.
    
    Args:
        app: Flask application instance
    
    Returns:
        Mail: Configured Mail instance
    """
    global mail
    mail = Mail(app)
    return mail


def send_email(
    to: str,
    subject: str,
    body: str,
    from_address: Optional[str] = None,
    client_id: Optional[int] = None,
    project_id: Optional[int] = None,
    save_to_db: bool = True
) -> Dict[str, Any]:
    """
    Send an email and optionally save it to the database.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text or HTML)
        from_address: Sender email address (defaults to MAIL_DEFAULT_SENDER)
        client_id: Optional client ID to link the communication
        project_id: Optional project ID to link the communication
        save_to_db: Whether to save the communication to database (default: True)
    
    Returns:
        dict: Result dictionary with 'success', 'message', and optionally 'communication_id'
    
    Example:
        >>> result = send_email(
        ...     to='client@example.com',
        ...     subject='Your order is ready',
        ...     body='Please collect your order.',
        ...     client_id=1
        ... )
        >>> if result['success']:
        ...     print(f"Email sent! Communication ID: {result['communication_id']}")
    """
    try:
        # Validate inputs
        if not to:
            return {'success': False, 'message': 'Recipient email address is required'}
        
        if not subject:
            return {'success': False, 'message': 'Email subject is required'}
        
        if not body:
            return {'success': False, 'message': 'Email body is required'}
        
        # Use default sender if not provided
        if not from_address:
            from_address = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@laseros.local')
        
        # Create Communication record first (before sending)
        communication = None
        if save_to_db:
            communication = Communication(
                comm_type='Email',
                direction='Outbound',
                subject=subject,
                from_address=from_address,
                to_address=to,
                body=body,
                status='Pending',
                client_id=client_id,
                project_id=project_id
            )
            db.session.add(communication)
            db.session.flush()  # Get the ID without committing
        
        # Send email via Flask-Mail
        if mail is None:
            # Mail not initialized (testing mode or missing config)
            if current_app.config.get('TESTING'):
                # In testing mode, just mark as sent
                if communication:
                    communication.status = 'Sent'
                    db.session.commit()
                return {
                    'success': True,
                    'message': 'Email queued (testing mode)',
                    'communication_id': communication.id if communication else None
                }
            else:
                return {'success': False, 'message': 'Email service not configured'}
        
        # Create Flask-Mail message
        msg = Message(
            subject=subject,
            sender=from_address,
            recipients=[to],
            body=body
        )
        
        # Send the email
        mail.send(msg)

        # Update communication status to Sent
        if communication:
            communication.status = 'Sent'
            communication.sent_at = datetime.utcnow()
            db.session.commit()
            
            # Log activity
            log_activity(
                'COMMUNICATION',
                communication.id,
                'EMAIL_SENT',
                {
                    'to': to,
                    'subject': subject,
                    'client_id': client_id,
                    'project_id': project_id
                }
            )
        
        return {
            'success': True,
            'message': 'Email sent successfully',
            'communication_id': communication.id if communication else None
        }
    
    except Exception as e:
        # Rollback database changes
        db.session.rollback()
        
        # Update communication status to Failed
        if communication:
            try:
                communication.status = 'Failed'
                communication.comm_metadata = f'{{"error": "{str(e)}"}}'
                db.session.commit()
            except:
                db.session.rollback()
        
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}',
            'communication_id': communication.id if communication else None
        }


def send_whatsapp(
    to: str,
    message: str,
    client_id: Optional[int] = None,
    project_id: Optional[int] = None,
    save_to_db: bool = True
) -> Dict[str, Any]:
    """
    Send a WhatsApp message (placeholder for future implementation).
    
    Currently saves the message to the database but does not actually send it.
    This is a placeholder for future WhatsApp API integration.
    
    Args:
        to: Recipient phone number (format: +1234567890)
        message: Message body
        client_id: Optional client ID to link the communication
        project_id: Optional project ID to link the communication
        save_to_db: Whether to save the communication to database (default: True)
    
    Returns:
        dict: Result dictionary with 'success', 'message', and optionally 'communication_id'
    
    Example:
        >>> result = send_whatsapp(
        ...     to='+27821234567',
        ...     message='Your order is ready for collection',
        ...     client_id=1
        ... )
    """
    try:
        # Validate inputs
        if not to:
            return {'success': False, 'message': 'Recipient phone number is required'}
        
        if not message:
            return {'success': False, 'message': 'Message body is required'}
        
        # Create Communication record
        communication = None
        if save_to_db:
            communication = Communication(
                comm_type='WhatsApp',
                direction='Outbound',
                subject='WhatsApp Message',
                from_address='LaserOS',
                to_address=to,
                body=message,
                status='Pending',
                client_id=client_id,
                project_id=project_id,
                comm_metadata='{"note": "WhatsApp integration not yet implemented"}'
            )
            db.session.add(communication)
            db.session.commit()
            
            # Log activity
            log_activity(
                'COMMUNICATION',
                communication.id,
                'WHATSAPP_QUEUED',
                {
                    'to': to,
                    'message_preview': message[:50],
                    'client_id': client_id,
                    'project_id': project_id
                }
            )
        
        return {
            'success': True,
            'message': 'WhatsApp message queued (integration pending)',
            'communication_id': communication.id if communication else None,
            'note': 'WhatsApp API integration not yet implemented'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Failed to queue WhatsApp message: {str(e)}'
        }


def send_notification(
    title: str,
    message: str,
    client_id: Optional[int] = None,
    project_id: Optional[int] = None,
    save_to_db: bool = True
) -> Dict[str, Any]:
    """
    Send an in-app notification (placeholder for future implementation).
    
    Currently saves the notification to the database but does not display it.
    This is a placeholder for future notification system.
    
    Args:
        title: Notification title
        message: Notification message
        client_id: Optional client ID to link the communication
        project_id: Optional project ID to link the communication
        save_to_db: Whether to save the communication to database (default: True)
    
    Returns:
        dict: Result dictionary with 'success', 'message', and optionally 'communication_id'
    
    Example:
        >>> result = send_notification(
        ...     title='Order Ready',
        ...     message='Project JB-2024-01-CL0001-001 is ready',
        ...     project_id=1
        ... )
    """
    try:
        # Validate inputs
        if not title:
            return {'success': False, 'message': 'Notification title is required'}
        
        if not message:
            return {'success': False, 'message': 'Notification message is required'}
        
        # Create Communication record
        communication = None
        if save_to_db:
            communication = Communication(
                comm_type='Notification',
                direction='Outbound',
                subject=title,
                from_address='LaserOS System',
                to_address='Internal',
                body=message,
                status='Sent',  # Notifications are immediately "sent" to the database
                client_id=client_id,
                project_id=project_id,
                sent_at=datetime.utcnow()
            )
            db.session.add(communication)
            db.session.commit()
            
            # Log activity
            log_activity(
                'COMMUNICATION',
                communication.id,
                'NOTIFICATION_CREATED',
                {
                    'title': title,
                    'client_id': client_id,
                    'project_id': project_id
                }
            )
        
        return {
            'success': True,
            'message': 'Notification created successfully',
            'communication_id': communication.id if communication else None
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Failed to create notification: {str(e)}'
        }

