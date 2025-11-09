"""
Daily Scheduled Jobs for Laser OS Production Automation.

This module contains scheduled jobs that run daily including:
- Daily report generation at 07:30 SAST
- Notification evaluation
- Stage escalation checks
"""

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz


def generate_daily_report_job():
    """
    Job to generate daily report for yesterday.
    
    Runs at 07:30 SAST (South African Standard Time = UTC+2).
    """
    from app.services.daily_report import generate_daily_report
    
    try:
        # Generate report for yesterday
        report = generate_daily_report()
        print(f"[SCHEDULER] Daily report generated for {report.report_date.strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"[SCHEDULER ERROR] Failed to generate daily report: {str(e)}")


def evaluate_project_notifications_job():
    """
    Job to evaluate all projects for stage escalation notifications.
    
    Runs hourly.
    """
    from app.services.notification_logic import evaluate_notifications_for_project
    from app.models.business import Project
    
    try:
        # Get all active projects (not completed, not cancelled, not on hold)
        projects = Project.query.filter(
            ~Project.status.in_([
                Project.STATUS_COMPLETED,
                Project.STATUS_CANCELLED
            ]),
            Project.on_hold == False
        ).all()
        
        notifications_created = 0
        for project in projects:
            try:
                evaluate_notifications_for_project(project.id)
                notifications_created += 1
            except Exception as e:
                print(f"[SCHEDULER ERROR] Failed to evaluate project {project.id}: {str(e)}")
        
        print(f"[SCHEDULER] Evaluated {len(projects)} projects for notifications")
    except Exception as e:
        print(f"[SCHEDULER ERROR] Failed to evaluate project notifications: {str(e)}")


def check_low_stock_job():
    """
    Job to check for low stock items and create notifications.
    
    Runs every 6 hours.
    """
    from app.services.notification_logic import create_low_stock_notification
    from app.models.business import InventoryItem
    
    try:
        # Get all low stock items
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.quantity_on_hand < InventoryItem.reorder_level,
            InventoryItem.category == InventoryItem.CATEGORY_SHEET_METAL
        ).all()
        
        for item in low_stock_items:
            try:
                create_low_stock_notification(item)
            except Exception as e:
                print(f"[SCHEDULER ERROR] Failed to create low stock notification for item {item.id}: {str(e)}")
        
        print(f"[SCHEDULER] Checked {len(low_stock_items)} low stock items")
    except Exception as e:
        print(f"[SCHEDULER ERROR] Failed to check low stock: {str(e)}")


def init_scheduler(app):
    """
    Initialize and start the background scheduler.
    
    Args:
        app: Flask application instance
    """
    # Create scheduler
    scheduler = BackgroundScheduler()
    
    # Define SAST timezone (UTC+2)
    sast = pytz.timezone('Africa/Johannesburg')
    
    # Add jobs
    
    # 1. Daily report generation at 07:30 SAST
    scheduler.add_job(
        func=generate_daily_report_job,
        trigger=CronTrigger(hour=7, minute=30, timezone=sast),
        id='daily_report_generation',
        name='Generate Daily Report',
        replace_existing=True
    )
    
    # 2. Project notification evaluation every hour
    scheduler.add_job(
        func=evaluate_project_notifications_job,
        trigger=CronTrigger(minute=0, timezone=sast),  # Every hour at :00
        id='project_notification_evaluation',
        name='Evaluate Project Notifications',
        replace_existing=True
    )
    
    # 3. Low stock check every 6 hours
    scheduler.add_job(
        func=check_low_stock_job,
        trigger=CronTrigger(hour='*/6', timezone=sast),  # Every 6 hours
        id='low_stock_check',
        name='Check Low Stock',
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    
    print("[SCHEDULER] Background scheduler started")
    print(f"[SCHEDULER] Daily report generation: 07:30 SAST")
    print(f"[SCHEDULER] Project notifications: Every hour")
    print(f"[SCHEDULER] Low stock check: Every 6 hours")
    
    # Shutdown scheduler when app exits
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler

