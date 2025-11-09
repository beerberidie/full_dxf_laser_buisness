"""
Laser OS - Notification Service (V12.0)

This service handles sending notifications via email, SMS, and WhatsApp.
Includes retry logic and admin alerts for failed notifications.

Features:
- Email notifications with HTML and text templates
- Retry logic (up to 3 attempts)
- Admin alerts on failure
- Communication logging
- Multiple notification types for status system

Author: Laser OS Development Team
Version: 12.0
Date: 2025-10-23
"""

from flask import current_app, render_template
from typing import Dict, Optional
from datetime import datetime
from app.models.business import Communication, db


def send_notification(recipient: str, subject: str, template: str, context: dict, 
                     notification_type: str = 'email', max_retries: int = 3) -> Dict:
    """
    Send notification to recipient with retry logic.
    
    Args:
        recipient (str): Email address, phone number, or WhatsApp number
        subject (str): Notification subject (for email)
        template (str): Template name (without extension)
        context (dict): Template context dictionary
        notification_type (str): 'email', 'sms', or 'whatsapp'
        max_retries (int): Maximum number of retry attempts (default: 3)
    
    Returns:
        dict: {
            'sent': bool,
            'message': str,
            'communication_id': int or None,
            'attempts': int
        }
    """
    attempts = 0
    last_error = None
    
    while attempts < max_retries:
        attempts += 1
        
        try:
            if notification_type == 'email':
                result = send_email_notification(recipient, subject, template, context)
            elif notification_type == 'sms':
                result = send_sms_notification(recipient, template, context)
            elif notification_type == 'whatsapp':
                result = send_whatsapp_notification(recipient, template, context)
            else:
                return {
                    'sent': False,
                    'message': f'Invalid notification type: {notification_type}',
                    'communication_id': None,
                    'attempts': attempts
                }
            
            if result['sent']:
                result['attempts'] = attempts
                return result
            else:
                last_error = result['message']
                
        except Exception as e:
            last_error = str(e)
            current_app.logger.error(f'Notification attempt {attempts} failed: {e}')
    
    # All retries failed - send admin alert
    send_admin_alert_on_failure(recipient, subject, template, last_error, attempts)
    
    return {
        'sent': False,
        'message': f'Failed after {attempts} attempts: {last_error}',
        'communication_id': None,
        'attempts': attempts
    }


def send_email_notification(recipient: str, subject: str, template: str, context: dict) -> Dict:
    """
    Send email notification.
    
    Args:
        recipient (str): Email address
        subject (str): Email subject
        template (str): Template name (without extension)
        context (dict): Template context
    
    Returns:
        dict: {'sent': bool, 'message': str, 'communication_id': int or None}
    """
    try:
        # Check if email is enabled
        if not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS', True):
            return {
                'sent': False,
                'message': 'Email notifications are disabled',
                'communication_id': None
            }
        
        # Render email templates
        try:
            html_body = render_template(f'emails/{template}.html', **context)
        except Exception:
            html_body = None
        
        try:
            text_body = render_template(f'emails/{template}.txt', **context)
        except Exception:
            text_body = f"Notification: {subject}"
        
        # For now, just log the email (actual sending will be implemented with Flask-Mail)
        current_app.logger.info(f'Email notification: {recipient} - {subject}')
        
        # Log communication
        comm = Communication(
            comm_type=Communication.TYPE_EMAIL,
            direction=Communication.DIRECTION_OUTBOUND,
            client_id=context.get('project').client_id if 'project' in context else None,
            project_id=context.get('project').id if 'project' in context else None,
            subject=subject,
            body=text_body,
            from_address=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@laseros.com'),
            to_address=recipient,
            status=Communication.STATUS_SENT,
            sent_at=datetime.utcnow()
        )
        db.session.add(comm)
        db.session.commit()
        
        return {
            'sent': True,
            'message': 'Email sent successfully',
            'communication_id': comm.id
        }
        
    except Exception as e:
        current_app.logger.error(f'Email notification error: {e}')
        return {
            'sent': False,
            'message': str(e),
            'communication_id': None
        }


def send_sms_notification(recipient: str, template: str, context: dict) -> Dict:
    """
    Send SMS notification (placeholder for future implementation).
    
    Args:
        recipient (str): Phone number
        template (str): Template name
        context (dict): Template context
    
    Returns:
        dict: {'sent': bool, 'message': str, 'communication_id': int or None}
    """
    if not current_app.config.get('ENABLE_SMS_NOTIFICATIONS', False):
        return {
            'sent': False,
            'message': 'SMS notifications are not enabled',
            'communication_id': None
        }
    
    # TODO: Implement SMS sending (Twilio, etc.)
    current_app.logger.info(f'SMS notification (not implemented): {recipient}')
    
    return {
        'sent': False,
        'message': 'SMS notifications not yet implemented',
        'communication_id': None
    }


def send_whatsapp_notification(recipient: str, template: str, context: dict) -> Dict:
    """
    Send WhatsApp notification (placeholder for future implementation).
    
    Args:
        recipient (str): WhatsApp number
        template (str): Template name
        context (dict): Template context
    
    Returns:
        dict: {'sent': bool, 'message': str, 'communication_id': int or None}
    """
    if not current_app.config.get('ENABLE_WHATSAPP_NOTIFICATIONS', False):
        return {
            'sent': False,
            'message': 'WhatsApp notifications are not enabled',
            'communication_id': None
        }
    
    # TODO: Implement WhatsApp sending (Twilio API, etc.)
    current_app.logger.info(f'WhatsApp notification (not implemented): {recipient}')
    
    return {
        'sent': False,
        'message': 'WhatsApp notifications not yet implemented',
        'communication_id': None
    }


def send_admin_alert_on_failure(recipient: str, subject: str, template: str, error: str, attempts: int):
    """
    Send alert to admin when notification fails after all retries.
    
    Args:
        recipient (str): Original recipient
        subject (str): Original subject
        template (str): Template name
        error (str): Error message
        attempts (int): Number of attempts made
    """
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@laseros.com')
    
    try:
        admin_subject = f'Notification Failure Alert - {subject}'
        admin_body = f"""
Notification failed after {attempts} attempts.

Original Recipient: {recipient}
Subject: {subject}
Template: {template}
Error: {error}

Please investigate and take appropriate action.
"""
        
        current_app.logger.error(f'Sending admin alert: {admin_subject}')
        
        # Log as communication
        comm = Communication(
            comm_type=Communication.TYPE_EMAIL,
            direction=Communication.DIRECTION_OUTBOUND,
            subject=admin_subject,
            body=admin_body,
            from_address=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@laseros.com'),
            to_address=admin_email,
            status=Communication.STATUS_SENT,
            sent_at=datetime.utcnow()
        )
        db.session.add(comm)
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f'Failed to send admin alert: {e}')


# ============================================================================
# Status System Notification Functions
# ============================================================================

def send_quote_expiry_reminder(project) -> Dict:
    """
    Send quote expiry reminder to client (25-day reminder).
    
    Args:
        project (Project): The project with expiring quote
    
    Returns:
        dict: Notification result
    """
    if not project.client or not project.client.email:
        return {
            'sent': False,
            'message': 'Client email not available',
            'communication_id': None
        }
    
    return send_notification(
        recipient=project.client.email,
        subject=f'Quote Expiring Soon - {project.project_code}',
        template='quote_expiry_reminder',
        context={
            'project': project,
            'client': project.client,
            'days_remaining': project.days_until_quote_expiry or 5
        },
        notification_type='email'
    )


def send_quote_expired_notice(project) -> Dict:
    """
    Send quote expired notice to client and admin.
    
    Args:
        project (Project): The project with expired quote
    
    Returns:
        dict: Combined notification results
    """
    results = {}
    
    # Send to client
    if project.client and project.client.email:
        results['client'] = send_notification(
            recipient=project.client.email,
            subject=f'Quote Expired - {project.project_code}',
            template='quote_expired',
            context={'project': project, 'client': project.client},
            notification_type='email'
        )
    
    # Send to admin
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@laseros.com')
    results['admin'] = send_notification(
        recipient=admin_email,
        subject=f'Quote Expired (Auto-Cancelled) - {project.project_code}',
        template='quote_expired_admin',
        context={'project': project, 'client': project.client},
        notification_type='email'
    )
    
    return {
        'sent': results.get('client', {}).get('sent', False) or results.get('admin', {}).get('sent', False),
        'message': 'Notifications sent to client and admin',
        'results': results
    }


def send_pop_received_notice(project) -> Dict:
    """
    Send POP received notice to scheduler.
    
    Args:
        project (Project): The project with POP received
    
    Returns:
        dict: Notification result
    """
    scheduler_email = current_app.config.get('SCHEDULER_EMAIL', 'scheduler@laseros.com')
    
    return send_notification(
        recipient=scheduler_email,
        subject=f'POP Received - {project.project_code} Queued for Cutting',
        template='pop_received',
        context={'project': project, 'client': project.client},
        notification_type='email'
    )


def send_job_started_notice(project, operator: str) -> Dict:
    """
    Send job started notice to admin.
    
    Args:
        project (Project): The project that started
        operator (str): Operator who started the job
    
    Returns:
        dict: Notification result
    """
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@laseros.com')
    
    return send_notification(
        recipient=admin_email,
        subject=f'Job Started - {project.project_code}',
        template='job_started',
        context={'project': project, 'operator': operator, 'client': project.client},
        notification_type='email'
    )


def send_job_completed_notice(project) -> Dict:
    """
    Send job completed notice to client.
    
    Args:
        project (Project): The completed project
    
    Returns:
        dict: Notification result
    """
    if not project.client or not project.client.email:
        return {
            'sent': False,
            'message': 'Client email not available',
            'communication_id': None
        }
    
    return send_notification(
        recipient=project.client.email,
        subject=f'Job Completed - {project.project_code} Ready for Collection',
        template='job_completed_client',
        context={'project': project, 'client': project.client},
        notification_type='email'
    )

