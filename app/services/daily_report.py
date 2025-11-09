"""
Daily Report Service for Laser OS Production Automation.

This module generates daily production reports including:
- Runs completed yesterday
- Material consumed
- Projects that advanced stages
- Low stock warnings
- Overdue projects
"""

from datetime import datetime, timedelta
from app import db
from app.models.business import DailyReport, LaserRun, Project, InventoryItem, Notification


def generate_daily_report(report_date=None):
    """
    Generate a daily report for the specified date.
    
    Args:
        report_date (datetime): Date to generate report for (defaults to yesterday)
        
    Returns:
        DailyReport: Generated report object
    """
    if report_date is None:
        # Default to yesterday
        report_date = datetime.utcnow().date() - timedelta(days=1)
    elif isinstance(report_date, datetime):
        report_date = report_date.date()
    
    # Check if report already exists for this date
    existing = DailyReport.query.filter_by(report_date=report_date).first()
    if existing:
        return existing
    
    # Calculate report data
    start_datetime = datetime.combine(report_date, datetime.min.time())
    end_datetime = datetime.combine(report_date, datetime.max.time())
    
    # 1. Runs completed
    completed_runs = LaserRun.query.filter(
        LaserRun.status == 'completed',
        LaserRun.ended_at >= start_datetime,
        LaserRun.ended_at <= end_datetime
    ).all()
    
    runs_count = len(completed_runs)
    total_sheets = sum(run.sheets_used or 0 for run in completed_runs)
    total_parts = sum(run.parts_produced or 0 for run in completed_runs)
    total_cut_time = sum(run.cut_time_minutes or 0 for run in completed_runs)
    
    # Get unique operators
    operators = set()
    for run in completed_runs:
        if run.operator_obj:
            operators.add(run.operator_obj.name)
        elif run.operator:
            operators.add(run.operator)
    
    # 2. Projects that advanced stages
    projects_advanced = Project.query.filter(
        Project.stage_last_updated >= start_datetime,
        Project.stage_last_updated <= end_datetime
    ).all()
    
    # 3. Low stock items
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.quantity_on_hand < InventoryItem.reorder_level,
        InventoryItem.category == InventoryItem.CATEGORY_SHEET_METAL
    ).all()
    
    # 4. Overdue projects (unresolved notifications)
    overdue_notifications = Notification.query.filter(
        Notification.resolved == False,
        Notification.notif_type.in_([
            'approval_wait',
            'material_block',
            'cutting_stall',
            'pickup_wait'
        ])
    ).all()
    
    # Build report body
    report_body = build_report_body(
        report_date=report_date,
        runs_count=runs_count,
        total_sheets=total_sheets,
        total_parts=total_parts,
        total_cut_time=total_cut_time,
        operators=list(operators),
        completed_runs=completed_runs,
        projects_advanced=projects_advanced,
        low_stock_items=low_stock_items,
        overdue_notifications=overdue_notifications
    )
    
    # Create report
    report = DailyReport(
        report_date=report_date,
        runs_count=runs_count,
        total_sheets_used=total_sheets,
        total_parts_produced=total_parts,
        total_cut_time_minutes=total_cut_time,
        report_body=report_body
    )
    
    db.session.add(report)
    db.session.commit()
    
    return report


def build_report_body(report_date, runs_count, total_sheets, total_parts, total_cut_time,
                     operators, completed_runs, projects_advanced, low_stock_items, overdue_notifications):
    """
    Build the report body text.
    
    Returns:
        str: Formatted report body
    """
    lines = []
    
    # Header
    lines.append(f"# Daily Production Report - {report_date.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Runs Completed:** {runs_count}")
    lines.append(f"- **Sheets Used:** {total_sheets}")
    lines.append(f"- **Parts Produced:** {total_parts}")
    lines.append(f"- **Total Cut Time:** {total_cut_time} minutes ({total_cut_time / 60:.1f} hours)")
    lines.append(f"- **Operators:** {', '.join(operators) if operators else 'None'}")
    lines.append("")
    
    # Completed Runs Detail
    if completed_runs:
        lines.append("## Completed Runs")
        lines.append("")
        for run in completed_runs:
            project_code = run.project.project_code if run.project else 'N/A'
            operator_name = run.operator_obj.name if run.operator_obj else (run.operator or 'Unknown')
            lines.append(f"- **{project_code}** - {run.material_type} {run.thickness_mm}mm")
            lines.append(f"  - Operator: {operator_name}")
            lines.append(f"  - Sheets: {run.sheets_used or 0}, Parts: {run.parts_produced or 0}")
            lines.append(f"  - Time: {run.cut_time_minutes or 0} min")
            if run.notes:
                lines.append(f"  - Notes: {run.notes}")
            lines.append("")
    
    # Projects Advanced
    if projects_advanced:
        lines.append("## Projects Advanced")
        lines.append("")
        for project in projects_advanced:
            lines.append(f"- **{project.project_code}** - {project.name}")
            lines.append(f"  - New Stage: {project.stage}")
            lines.append(f"  - Client: {project.client.name}")
            lines.append("")
    
    # Low Stock Warnings
    if low_stock_items:
        lines.append("## ⚠️ Low Stock Warnings")
        lines.append("")
        for item in low_stock_items:
            current = int(item.quantity_on_hand)
            minimum = int(item.reorder_level)
            shortage = minimum - current
            lines.append(f"- **{item.name}**")
            lines.append(f"  - Current: {current} sheets")
            lines.append(f"  - Minimum: {minimum} sheets")
            lines.append(f"  - Shortage: {shortage} sheets")
            lines.append("")
    
    # Overdue Projects
    if overdue_notifications:
        lines.append("## ⚠️ Overdue Projects")
        lines.append("")
        for notif in overdue_notifications:
            lines.append(f"- {notif.message}")
            if notif.project:
                lines.append(f"  - Client: {notif.project.client.name}")
            lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Report generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
    
    return "\n".join(lines)


def get_latest_report():
    """
    Get the most recent daily report.
    
    Returns:
        DailyReport: Latest report or None
    """
    return DailyReport.query.order_by(DailyReport.report_date.desc()).first()


def get_report_by_date(report_date):
    """
    Get report for a specific date.
    
    Args:
        report_date (date): Date to get report for
        
    Returns:
        DailyReport: Report for the date or None
    """
    if isinstance(report_date, datetime):
        report_date = report_date.date()
    
    return DailyReport.query.filter_by(report_date=report_date).first()


def get_reports_for_date_range(start_date, end_date):
    """
    Get all reports within a date range.
    
    Args:
        start_date (date): Start date
        end_date (date): End date
        
    Returns:
        list: List of DailyReport objects
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    return DailyReport.query.filter(
        DailyReport.report_date >= start_date,
        DailyReport.report_date <= end_date
    ).order_by(DailyReport.report_date.desc()).all()

