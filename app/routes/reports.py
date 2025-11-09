"""
Reporting and analytics routes
"""

from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from app import db
from app.models import Client, Project, Product, DesignFile, QueueItem, LaserRun, InventoryItem, InventoryTransaction
from app.utils.decorators import role_required
from datetime import datetime, timedelta
from sqlalchemy import func
import csv
import io

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/')
@login_required
def index():
    """Display reports dashboard."""
    return render_template('reports/index.html')


@bp.route('/production')
@login_required
def production_summary():
    """Production summary report."""
    # Get date range from request
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Default to last 30 days
    if not end_date_str:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    if not start_date_str:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    
    # Get laser runs in date range
    runs = LaserRun.query.filter(
        LaserRun.run_date >= start_date,
        LaserRun.run_date <= end_date
    ).order_by(LaserRun.run_date.desc()).all()
    
    # Calculate statistics
    total_runs = len(runs)
    total_cut_time = sum(run.cut_time_minutes or 0 for run in runs)
    total_parts = sum(run.parts_produced or 0 for run in runs)
    total_sheets = sum(run.sheet_count or 0 for run in runs)
    
    # Group by operator
    operator_stats = {}
    for run in runs:
        operator = run.operator or 'Unknown'
        if operator not in operator_stats:
            operator_stats[operator] = {
                'runs': 0,
                'cut_time': 0,
                'parts': 0
            }
        operator_stats[operator]['runs'] += 1
        operator_stats[operator]['cut_time'] += run.cut_time_minutes or 0
        operator_stats[operator]['parts'] += run.parts_produced or 0
    
    # Group by material
    material_stats = {}
    for run in runs:
        material = run.material_type or 'Unknown'
        if material not in material_stats:
            material_stats[material] = {
                'runs': 0,
                'sheets': 0,
                'parts': 0
            }
        material_stats[material]['runs'] += 1
        material_stats[material]['sheets'] += run.sheet_count or 0
        material_stats[material]['parts'] += run.parts_produced or 0
    
    stats = {
        'total_runs': total_runs,
        'total_cut_time': total_cut_time,
        'total_cut_hours': round(total_cut_time / 60, 2) if total_cut_time else 0,
        'total_parts': total_parts,
        'total_sheets': total_sheets,
        'avg_cut_time': round(total_cut_time / total_runs, 2) if total_runs else 0,
        'avg_parts_per_run': round(total_parts / total_runs, 2) if total_runs else 0
    }
    
    return render_template(
        'reports/production.html',
        runs=runs,
        stats=stats,
        operator_stats=operator_stats,
        material_stats=material_stats,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )


@bp.route('/efficiency')
@login_required
def efficiency_metrics():
    """Efficiency metrics report."""
    # Get queue items with estimated vs actual times
    completed_items = QueueItem.query.filter_by(
        status=QueueItem.STATUS_COMPLETED
    ).all()
    
    efficiency_data = []
    for item in completed_items:
        # Get laser runs for this queue item
        runs = LaserRun.query.filter_by(queue_item_id=item.id).all()
        
        if runs and item.estimated_cut_time:
            actual_time = sum(run.cut_time_minutes or 0 for run in runs)
            estimated_time = item.estimated_cut_time
            
            variance = actual_time - estimated_time
            variance_pct = (variance / estimated_time * 100) if estimated_time else 0
            
            efficiency_data.append({
                'project': item.project,
                'estimated': estimated_time,
                'actual': actual_time,
                'variance': variance,
                'variance_pct': round(variance_pct, 1),
                'efficiency': round((estimated_time / actual_time * 100), 1) if actual_time else 0
            })
    
    # Calculate overall statistics
    if efficiency_data:
        avg_efficiency = sum(d['efficiency'] for d in efficiency_data) / len(efficiency_data)
        total_estimated = sum(d['estimated'] for d in efficiency_data)
        total_actual = sum(d['actual'] for d in efficiency_data)
    else:
        avg_efficiency = 0
        total_estimated = 0
        total_actual = 0
    
    stats = {
        'avg_efficiency': round(avg_efficiency, 1),
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'total_variance': total_actual - total_estimated,
        'projects_analyzed': len(efficiency_data)
    }
    
    return render_template(
        'reports/efficiency.html',
        efficiency_data=efficiency_data,
        stats=stats
    )


@bp.route('/inventory')
@login_required
def inventory_report():
    """Inventory usage and value report."""
    # Get all inventory items
    items = InventoryItem.query.order_by(InventoryItem.category, InventoryItem.name).all()
    
    # Calculate statistics
    total_value = sum(item.stock_value for item in items)
    low_stock_count = len([item for item in items if item.is_low_stock])
    
    # Group by category
    category_stats = {}
    for item in items:
        if item.category not in category_stats:
            category_stats[item.category] = {
                'items': 0,
                'value': 0,
                'low_stock': 0
            }
        category_stats[item.category]['items'] += 1
        category_stats[item.category]['value'] += item.stock_value
        if item.is_low_stock:
            category_stats[item.category]['low_stock'] += 1
    
    # Get recent transactions
    recent_transactions = InventoryTransaction.query.order_by(
        InventoryTransaction.transaction_date.desc()
    ).limit(50).all()
    
    # Calculate transaction statistics
    total_purchases = sum(
        txn.transaction_value for txn in recent_transactions 
        if txn.transaction_type == InventoryTransaction.TYPE_PURCHASE
    )
    total_usage = sum(
        txn.transaction_value for txn in recent_transactions 
        if txn.transaction_type == InventoryTransaction.TYPE_USAGE
    )
    
    stats = {
        'total_items': len(items),
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'total_purchases': total_purchases,
        'total_usage': total_usage
    }
    
    return render_template(
        'reports/inventory.html',
        items=items,
        stats=stats,
        category_stats=category_stats,
        recent_transactions=recent_transactions
    )


@bp.route('/clients')
@login_required
def client_report():
    """Client and project profitability report."""
    # Get all clients with their projects
    clients = Client.query.order_by(Client.name).all()
    
    client_data = []
    for client in clients:
        project_count = len(client.projects)
        active_projects = len([p for p in client.projects if p.status in [Project.STATUS_APPROVED, Project.STATUS_IN_PROGRESS]])
        
        # Calculate total project value (use final_price if available, otherwise quoted_price)
        total_value = sum(float(p.final_price or p.quoted_price or 0) for p in client.projects)
        
        # Count laser runs for client projects
        total_runs = 0
        total_cut_time = 0
        for project in client.projects:
            runs = LaserRun.query.filter_by(project_id=project.id).all()
            total_runs += len(runs)
            total_cut_time += sum(run.cut_time_minutes or 0 for run in runs)
        
        client_data.append({
            'client': client,
            'project_count': project_count,
            'active_projects': active_projects,
            'total_value': total_value,
            'total_runs': total_runs,
            'total_cut_hours': round(total_cut_time / 60, 2) if total_cut_time else 0
        })
    
    # Sort by total value
    client_data.sort(key=lambda x: x['total_value'], reverse=True)
    
    # Calculate statistics
    total_clients = len(clients)
    total_projects = sum(d['project_count'] for d in client_data)
    total_value = sum(d['total_value'] for d in client_data)
    
    stats = {
        'total_clients': total_clients,
        'total_projects': total_projects,
        'total_value': total_value,
        'avg_value_per_client': round(total_value / total_clients, 2) if total_clients else 0
    }
    
    return render_template(
        'reports/clients.html',
        client_data=client_data,
        stats=stats
    )


@bp.route('/export/production')
@role_required('admin', 'manager')
def export_production_csv():
    """Export production report to CSV."""
    # Get date range
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not end_date_str:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    if not start_date_str:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    
    # Get laser runs
    runs = LaserRun.query.filter(
        LaserRun.run_date >= start_date,
        LaserRun.run_date <= end_date
    ).order_by(LaserRun.run_date.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Project Code', 'Operator', 'Cut Time (min)', 
        'Material', 'Thickness', 'Sheets', 'Parts', 'Status'
    ])
    
    # Write data
    for run in runs:
        writer.writerow([
            run.run_date.strftime('%Y-%m-%d %H:%M'),
            run.project.project_code if run.project else '',
            run.operator or '',
            run.cut_time_minutes or '',
            run.material_type or '',
            run.material_thickness or '',
            run.sheet_count or '',
            run.parts_produced or '',
            run.status or ''
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=production_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv'

    return response


# Production Automation: Daily Report Routes

@bp.route('/daily')
@login_required
def daily_reports():
    """List all daily reports."""
    from app.services.daily_report import get_reports_for_date_range
    from datetime import date

    # Get last 30 days of reports
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    reports = get_reports_for_date_range(start_date, end_date)

    return render_template('reports/daily_reports.html', reports=reports)


@bp.route('/daily/<report_date>')
@login_required
def view_daily_report(report_date):
    """View a specific daily report."""
    from app.services.daily_report import get_report_by_date, generate_daily_report
    from datetime import datetime

    # Parse date
    try:
        date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('reports.daily_reports'))

    # Get or generate report
    report = get_report_by_date(date_obj)
    if not report:
        # Generate report for this date
        report = generate_daily_report(date_obj)

    return render_template('reports/daily_report.html', report=report)


@bp.route('/daily/generate', methods=['POST'])
@login_required
@role_required('admin', 'manager')
def generate_daily_report_now():
    """Manually generate daily report for yesterday."""
    from app.services.daily_report import generate_daily_report
    from flask import flash, redirect, url_for

    report = generate_daily_report()

    flash(f'Daily report generated for {report.report_date.strftime("%Y-%m-%d")}.', 'success')
    return redirect(url_for('reports.view_daily_report', report_date=report.report_date.strftime('%Y-%m-%d')))


@bp.route('/daily/<report_date>/export')
@login_required
@role_required('admin', 'manager')
def export_daily_report_txt(report_date):
    """Export daily report as .txt file."""
    from app.services.daily_report import get_report_by_date
    from flask import send_file, flash, redirect, url_for
    from datetime import datetime
    import tempfile

    # Parse date
    try:
        date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('reports.daily_reports'))

    # Get report
    report = get_report_by_date(date_obj)
    if not report:
        flash('Report not found.', 'error')
        return redirect(url_for('reports.daily_reports'))

    # Write to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
    temp_file.write(report.report_body)
    temp_file.close()

    # Send file
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f'DailyReport_{report_date}.txt',
        mimetype='text/plain'
    )
