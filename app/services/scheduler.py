"""
Laser OS - Background Scheduler Service (V12.0)

This service manages background jobs for the status system redesign.
Uses APScheduler to run daily jobs for quote expiry checking and reminders.

Features:
- Daily quote expiry check (9:00 AM)
- Daily quote reminder sending (10:00 AM)
- Catch-up logic for missed jobs during downtime
- Flask app context management
- Persistent job store (optional)

Author: Laser OS Development Team
Version: 12.0
Date: 2025-10-23
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from flask import Flask
import logging

# Create scheduler instance
scheduler = BackgroundScheduler()

# Configure logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)


def check_quote_expiry_with_context(app: Flask):
    """
    Run quote expiry check with Flask app context.
    
    This wrapper ensures the job runs within the Flask application context,
    allowing access to database, config, and other Flask features.
    
    Args:
        app (Flask): Flask application instance
    """
    with app.app_context():
        from app.services.status_automation import check_quote_expiry
        
        try:
            result = check_quote_expiry()
            
            app.logger.info(
                f"Quote expiry check completed: "
                f"Checked {result['checked']} projects, "
                f"Cancelled {result['expired']} expired quotes"
            )
            
            if result['errors']:
                app.logger.error(f"Quote expiry check errors: {result['errors']}")
            
            if result['cancelled_ids']:
                app.logger.info(f"Auto-cancelled project IDs: {result['cancelled_ids']}")
                
        except Exception as e:
            app.logger.error(f"Quote expiry check failed: {e}", exc_info=True)


def send_quote_reminders_with_context(app: Flask):
    """
    Run quote reminder sending with Flask app context.
    
    This wrapper ensures the job runs within the Flask application context.
    
    Args:
        app (Flask): Flask application instance
    """
    with app.app_context():
        from app.services.status_automation import send_quote_reminders
        
        try:
            result = send_quote_reminders()
            
            app.logger.info(
                f"Quote reminder check completed: "
                f"Checked {result['checked']} projects, "
                f"Sent {result['reminders_sent']} reminders"
            )
            
            if result['errors']:
                app.logger.error(f"Quote reminder errors: {result['errors']}")
            
            if result['project_ids']:
                app.logger.info(f"Reminders sent for project IDs: {result['project_ids']}")
                
        except Exception as e:
            app.logger.error(f"Quote reminder sending failed: {e}", exc_info=True)


def job_listener(event):
    """
    Listen to job execution events for logging and monitoring.
    
    Args:
        event: APScheduler event object
    """
    if event.exception:
        logging.error(f"Job {event.job_id} failed: {event.exception}")
    else:
        logging.info(f"Job {event.job_id} executed successfully")


def init_scheduler(app: Flask):
    """
    Initialize background scheduler with Flask app.
    
    This function sets up all scheduled jobs and starts the scheduler.
    Should be called once during application startup.
    
    Args:
        app (Flask): Flask application instance
    
    Example:
        >>> from app import create_app
        >>> from app.services.scheduler import init_scheduler
        >>> app = create_app()
        >>> init_scheduler(app)
    """
    # Check if scheduler is enabled in config
    if not app.config.get('ENABLE_BACKGROUND_SCHEDULER', True):
        app.logger.info("Background scheduler is disabled in config")
        return
    
    # Get schedule times from config
    expiry_check_hour = app.config.get('QUOTE_EXPIRY_CHECK_HOUR', 9)
    reminder_check_hour = app.config.get('QUOTE_REMINDER_CHECK_HOUR', 10)
    
    # Add job: Check for expired quotes daily at configured hour
    scheduler.add_job(
        func=lambda: check_quote_expiry_with_context(app),
        trigger=CronTrigger(hour=expiry_check_hour, minute=0),
        id='check_quote_expiry',
        name='Check for expired quotes and auto-cancel',
        replace_existing=True,
        misfire_grace_time=3600,  # Allow 1 hour grace period for missed jobs
        coalesce=True  # Combine multiple missed runs into one
    )
    
    # Add job: Send quote reminders daily at configured hour
    scheduler.add_job(
        func=lambda: send_quote_reminders_with_context(app),
        trigger=CronTrigger(hour=reminder_check_hour, minute=0),
        id='send_quote_reminders',
        name='Send 25-day quote expiry reminders',
        replace_existing=True,
        misfire_grace_time=3600,  # Allow 1 hour grace period for missed jobs
        coalesce=True  # Combine multiple missed runs into one
    )
    
    # Add event listener
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        app.logger.info(
            f"Background scheduler started successfully. "
            f"Quote expiry check: {expiry_check_hour}:00, "
            f"Quote reminders: {reminder_check_hour}:00"
        )
    else:
        app.logger.info("Background scheduler already running")


def shutdown_scheduler():
    """
    Shutdown the background scheduler gracefully.
    
    Should be called during application shutdown.
    """
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logging.info("Background scheduler shut down successfully")


def get_scheduler_status() -> dict:
    """
    Get current status of the scheduler and its jobs.
    
    Returns:
        dict: {
            'running': bool,
            'jobs': list of job info dicts
        }
    """
    jobs_info = []
    
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
    
    return {
        'running': scheduler.running,
        'jobs': jobs_info
    }


def run_job_now(job_id: str, app: Flask) -> dict:
    """
    Manually trigger a scheduled job to run immediately.
    
    Useful for testing or manual intervention.
    
    Args:
        job_id (str): ID of the job to run ('check_quote_expiry' or 'send_quote_reminders')
        app (Flask): Flask application instance
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'result': dict or None
        }
    """
    try:
        if job_id == 'check_quote_expiry':
            with app.app_context():
                from app.services.status_automation import check_quote_expiry
                result = check_quote_expiry()
            
            return {
                'success': True,
                'message': f'Quote expiry check completed: {result["expired"]} projects cancelled',
                'result': result
            }
            
        elif job_id == 'send_quote_reminders':
            with app.app_context():
                from app.services.status_automation import send_quote_reminders
                result = send_quote_reminders()
            
            return {
                'success': True,
                'message': f'Quote reminders sent: {result["reminders_sent"]} reminders',
                'result': result
            }
            
        else:
            return {
                'success': False,
                'message': f'Unknown job ID: {job_id}',
                'result': None
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Job execution failed: {str(e)}',
            'result': None
        }


# ============================================================================
# Catch-up Logic for Missed Jobs
# ============================================================================

def run_catchup_on_startup(app: Flask):
    """
    Run catch-up logic on application startup to process missed jobs.
    
    This function checks for quotes that should have been expired or reminded
    during downtime and processes them immediately.
    
    Args:
        app (Flask): Flask application instance
    """
    with app.app_context():
        from app.services.status_automation import get_expired_quotes, get_projects_expiring_soon
        from datetime import date, timedelta
        
        app.logger.info("Running catch-up logic for missed jobs...")
        
        # Check for expired quotes that weren't auto-cancelled
        expired_quotes = get_expired_quotes()
        if expired_quotes:
            app.logger.warning(
                f"Found {len(expired_quotes)} expired quotes that weren't auto-cancelled. "
                f"Running expiry check now..."
            )
            check_quote_expiry_with_context(app)
        
        # Check for projects that should have received reminders
        # (expiry date is within 5 days and reminder not sent)
        from app.models.business import Project
        projects_needing_reminder = Project.query.filter(
            Project.status == Project.STATUS_QUOTE_APPROVAL,
            Project.pop_received == False,
            Project.quote_expiry_date.isnot(None),
            Project.quote_expiry_date >= date.today(),
            Project.quote_expiry_date <= date.today() + timedelta(days=5),
            Project.quote_reminder_sent == False
        ).all()
        
        if projects_needing_reminder:
            app.logger.warning(
                f"Found {len(projects_needing_reminder)} projects that should have received reminders. "
                f"Running reminder check now..."
            )
            send_quote_reminders_with_context(app)
        
        app.logger.info("Catch-up logic completed")

