# Status System Redesign - Implementation Plan

**Version:** 1.0  
**Date:** 2025-10-23  
**Status:** 📋 PLANNING PHASE

---

## 📊 Executive Summary

This document outlines the comprehensive plan to redesign Laser OS's project status system based on the new requirements. The redesign introduces:

- **Simplified status flow** (6 core statuses vs current 9)
- **Automated status transitions** with validation
- **30-day quote expiry timer** with auto-cancellation
- **Enhanced automation triggers** for notifications and scheduling
- **"On Hold" capability** for temporary pauses
- **Reinstate workflow** for cancelled projects

---

## 🔄 Current vs Proposed Status System

### Current System (9 Statuses)

| # | Current Status | Constant |
|---|----------------|----------|
| 1 | Request | `STATUS_REQUEST` |
| 2 | Quote & Approval | `STATUS_QUOTE_APPROVAL` |
| 3 | Approved (POP Received) | `STATUS_APPROVED_POP` |
| 4 | Queued (Scheduled for Cutting) | `STATUS_QUEUED` |
| 5 | In Progress | `STATUS_IN_PROGRESS` |
| 6 | Completed | `STATUS_COMPLETED` |
| 7 | Cancelled | `STATUS_CANCELLED` |
| 8 | Quote (Legacy) | `STATUS_QUOTE` |
| 9 | Approved (Legacy) | `STATUS_APPROVED` |

### Proposed System (7 Statuses)

| # | New Status | Constant | Description | Auto-Advance |
|---|------------|----------|-------------|--------------|
| 1 | Request | `STATUS_REQUEST` | Initial project creation | ✅ When all fields valid |
| 2 | Quote & Approval | `STATUS_QUOTE_APPROVAL` | Awaiting POP | ⏱️ 30-day timer |
| 3 | Approved / POP Received | `STATUS_APPROVED_POP` | Payment confirmed | ✅ Auto-queue |
| 4 | Queued for Cutting | `STATUS_QUEUED` | Scheduled for production | Manual/Auto |
| 5 | In Progress | `STATUS_IN_PROGRESS` | Active cutting | Manual |
| 6 | Completed | `STATUS_COMPLETED` | Job finished | Manual |
| 7 | Cancelled / On Hold | `STATUS_CANCELLED` | Not confirmed or paused | Manual/Timer |

**Key Changes:**
- ✅ Keep 6 core statuses (remove legacy statuses)
- ✅ Add "On Hold" flag (separate from Cancelled)
- ✅ Implement 30-day auto-cancel timer
- ✅ Add auto-advance from Request → Quote & Approval
- ✅ Enhanced validation at each status

---

## 🎯 Key Requirements Analysis

### 1. Status-Driven Validations

| Status | Required Fields | Validation Logic |
|--------|----------------|------------------|
| **Request** | Project name, Client, Material type, Material thickness, DXF files | Auto-advance when all valid |
| **Quote & Approval** | Quote document, Quote date | Start 30-day timer |
| **Approved / POP Received** | POP document, POP date | Trigger auto-queue |
| **Queued for Cutting** | Schedule time, Queue position | Check machine schedule |
| **In Progress** | Operator name, Start time | Log operator/time |
| **Completed** | Completion confirmation | Record final stats |

### 2. Automation Triggers

| Event | Trigger | Actions |
|-------|---------|---------|
| **Request → Quote & Approval** | All required fields filled | Auto-update status, Send quote notification |
| **Quote & Approval (30 days)** | Timer expiry, No POP | Auto-set Cancelled, Notify admin |
| **POP Received** | POP document uploaded | Auto-queue, Update status, Notify scheduler |
| **Queued → In Progress** | Operator starts job | Log start time, Notify dashboard |
| **In Progress → Completed** | Job finished | Notify client, Record stats |
| **Manual "Unconfirmed"** | User action | Set Cancelled, Log reason |

### 3. Notification Requirements

| Event | Recipients | Type | Content |
|-------|-----------|------|---------|
| POP Received | Scheduler, Admin | Email/Dashboard | "Project Approved and Queued" |
| Job Started | Admin, Dashboard | Real-time | "Job # in Progress" |
| Job Completed | Client, Operator | Email/SMS | "Job Completed — Ready for Collection" |
| Job Cancelled | Admin, Client | Email | "Job Cancelled — No POP in 30 Days" |
| 25-Day Reminder | Client, Sales | Email | "Quote expiring in 5 days" |

### 4. Timer System

**30-Day Quote Expiry:**
- **Start:** When status = "Quote & Approval"
- **Check:** Daily background job
- **Action:** If `quote_date + 30 days < today` AND `pop_received = False` → Set status = "Cancelled"
- **Notification:** Send cancellation notice to admin and client
- **Optional:** 25-day reminder (5 days before expiry)

---

## 📋 Implementation Tasks Breakdown

### Phase 1: Database Schema Changes

**Task 1.1: Add New Fields to Projects Table**

```sql
ALTER TABLE projects ADD COLUMN on_hold BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN on_hold_reason TEXT;
ALTER TABLE projects ADD COLUMN on_hold_date DATE;
ALTER TABLE projects ADD COLUMN quote_expiry_date DATE;
ALTER TABLE projects ADD COLUMN quote_reminder_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN cancellation_reason TEXT;
ALTER TABLE projects ADD COLUMN can_reinstate BOOLEAN DEFAULT FALSE;
```

**Task 1.2: Update Status CHECK Constraint**

```sql
-- Remove legacy statuses from CHECK constraint
-- Keep: Request, Quote & Approval, Approved (POP Received), 
--       Queued (Scheduled for Cutting), In Progress, Completed, Cancelled
```

**Task 1.3: Create Indexes**

```sql
CREATE INDEX idx_projects_on_hold ON projects(on_hold);
CREATE INDEX idx_projects_quote_expiry ON projects(quote_expiry_date);
CREATE INDEX idx_projects_can_reinstate ON projects(can_reinstate);
```

---

### Phase 2: Backend Model Updates

**Task 2.1: Update Project Model Constants**

**File:** `app/models/business.py`

```python
# Remove legacy statuses
# Update VALID_STATUSES list
VALID_STATUSES = [
    STATUS_REQUEST,
    STATUS_QUOTE_APPROVAL,
    STATUS_APPROVED_POP,
    STATUS_QUEUED,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_CANCELLED
]

# Add new fields
on_hold = db.Column(db.Boolean, default=False, index=True)
on_hold_reason = db.Column(db.Text)
on_hold_date = db.Column(db.Date)
quote_expiry_date = db.Column(db.Date, index=True)
quote_reminder_sent = db.Column(db.Boolean, default=False)
cancellation_reason = db.Column(db.Text)
can_reinstate = db.Column(db.Boolean, default=False)
```

**Task 2.2: Add Validation Methods**

```python
@property
def is_ready_for_quote_approval(self):
    """Check if project can advance to Quote & Approval."""
    return (
        self.name and
        self.client_id and
        self.material_type and
        self.material_thickness and
        len(self.design_files) > 0
    )

@property
def is_quote_expired(self):
    """Check if quote has expired (30 days)."""
    if self.quote_expiry_date:
        from datetime import date
        return date.today() > self.quote_expiry_date
    return False

@property
def days_until_quote_expiry(self):
    """Calculate days until quote expires."""
    if self.quote_expiry_date and not self.pop_received:
        from datetime import date
        delta = self.quote_expiry_date - date.today()
        return delta.days
    return None
```

---

### Phase 3: Status Automation Service

**Task 3.1: Create Status Automation Service**

**File:** `app/services/status_automation.py` (NEW)

```python
from datetime import date, timedelta
from app.models import Project, db
from app.services.activity_logger import log_activity
from app.services.notification_service import send_notification

def auto_advance_to_quote_approval(project: Project) -> dict:
    """
    Auto-advance project from Request to Quote & Approval if all fields valid.
    
    Returns:
        dict: {
            'advanced': bool,
            'message': str,
            'reasons': list
        }
    """
    if not project.is_ready_for_quote_approval:
        return {
            'advanced': False,
            'message': 'Project not ready for quote',
            'reasons': get_missing_fields(project)
        }
    
    old_status = project.status
    project.status = Project.STATUS_QUOTE_APPROVAL
    project.quote_date = date.today()
    project.quote_expiry_date = date.today() + timedelta(days=30)
    
    db.session.commit()
    
    log_activity('PROJECT', project.id, 'STATUS_AUTO_ADVANCED', {
        'old_status': old_status,
        'new_status': project.status,
        'reason': 'All required fields completed'
    })
    
    return {
        'advanced': True,
        'message': 'Project advanced to Quote & Approval',
        'reasons': []
    }
```

**Task 3.2: Create Quote Expiry Checker**

```python
def check_quote_expiry() -> dict:
    """
    Background job to check for expired quotes and auto-cancel.
    
    Returns:
        dict: {
            'checked': int,
            'expired': int,
            'cancelled': list
        }
    """
    # Find projects in Quote & Approval with expired quotes
    expired_projects = Project.query.filter(
        Project.status == Project.STATUS_QUOTE_APPROVAL,
        Project.pop_received == False,
        Project.quote_expiry_date < date.today()
    ).all()
    
    cancelled_ids = []
    
    for project in expired_projects:
        project.status = Project.STATUS_CANCELLED
        project.cancellation_reason = 'Quote expired - No POP received within 30 days'
        project.can_reinstate = True
        
        log_activity('PROJECT', project.id, 'AUTO_CANCELLED', {
            'reason': 'Quote expired',
            'quote_date': project.quote_date.isoformat(),
            'expiry_date': project.quote_expiry_date.isoformat()
        })
        
        # Send notification
        send_notification(
            recipient=project.client.email,
            subject=f'Quote Expired - Project {project.project_code}',
            template='quote_expired',
            context={'project': project}
        )
        
        cancelled_ids.append(project.id)
    
    db.session.commit()
    
    return {
        'checked': Project.query.filter_by(status=Project.STATUS_QUOTE_APPROVAL).count(),
        'expired': len(cancelled_ids),
        'cancelled': cancelled_ids
    }
```

---

### Phase 4: Background Scheduler

**Task 4.1: Create Scheduler Service**

**File:** `app/services/scheduler.py` (NEW)

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.status_automation import check_quote_expiry, send_quote_reminders

scheduler = BackgroundScheduler()

def init_scheduler(app):
    """Initialize background scheduler with app context."""
    
    # Check for expired quotes daily at 9 AM
    scheduler.add_job(
        func=lambda: check_quote_expiry_with_context(app),
        trigger=CronTrigger(hour=9, minute=0),
        id='check_quote_expiry',
        name='Check for expired quotes',
        replace_existing=True
    )
    
    # Send 25-day reminders daily at 10 AM
    scheduler.add_job(
        func=lambda: send_quote_reminders_with_context(app),
        trigger=CronTrigger(hour=10, minute=0),
        id='send_quote_reminders',
        name='Send quote expiry reminders',
        replace_existing=True
    )
    
    scheduler.start()

def check_quote_expiry_with_context(app):
    """Run quote expiry check with Flask app context."""
    with app.app_context():
        result = check_quote_expiry()
        app.logger.info(f"Quote expiry check: {result}")
```

---

### Phase 5: Route Updates

**Task 5.1: Update Project Create Route**

**File:** `app/routes/projects.py`

```python
@bp.route('/create', methods=['POST'])
def create():
    # ... existing code ...
    
    # After creating project
    db.session.add(project)
    db.session.commit()
    
    # Check if ready for auto-advance
    from app.services.status_automation import auto_advance_to_quote_approval
    result = auto_advance_to_quote_approval(project)
    
    if result['advanced']:
        flash(f'✅ Project created and advanced to Quote & Approval', 'success')
    else:
        flash(f'✅ Project created. Complete missing fields to generate quote', 'info')
```

**Task 5.2: Add On Hold Toggle Route**

```python
@bp.route('/<int:id>/toggle-hold', methods=['POST'])
@role_required('admin', 'manager')
def toggle_hold(id):
    """Toggle project on hold status."""
    project = Project.query.get_or_404(id)
    
    project.on_hold = not project.on_hold
    
    if project.on_hold:
        project.on_hold_date = date.today()
        project.on_hold_reason = request.form.get('reason', '')
        flash('Project placed on hold', 'warning')
    else:
        project.on_hold_date = None
        project.on_hold_reason = None
        flash('Project resumed from hold', 'success')
    
    db.session.commit()
    
    log_activity('PROJECT', id, 'HOLD_TOGGLED', {
        'on_hold': project.on_hold,
        'reason': project.on_hold_reason
    })
    
    return redirect(url_for('projects.detail', id=id))
```

**Task 5.3: Add Reinstate Route**

```python
@bp.route('/<int:id>/reinstate', methods=['POST'])
@role_required('admin', 'manager')
def reinstate(id):
    """Reinstate a cancelled project."""
    project = Project.query.get_or_404(id)
    
    if project.status != Project.STATUS_CANCELLED or not project.can_reinstate:
        flash('Project cannot be reinstated', 'error')
        return redirect(url_for('projects.detail', id=id))
    
    # Reinstate to Quote & Approval
    project.status = Project.STATUS_QUOTE_APPROVAL
    project.quote_expiry_date = date.today() + timedelta(days=30)
    project.can_reinstate = False
    project.cancellation_reason = None
    
    db.session.commit()
    
    log_activity('PROJECT', id, 'REINSTATED', {
        'new_expiry_date': project.quote_expiry_date.isoformat()
    })
    
    flash('✅ Project reinstated with new 30-day quote period', 'success')
    return redirect(url_for('projects.detail', id=id))
```

---

## 🔄 Migration Strategy

### Migration v10.0: Status System Redesign

**File:** `migrations/schema_v10_0_status_redesign.sql`

**Steps:**
1. Add new columns (on_hold, quote_expiry_date, etc.)
2. Remove legacy statuses from CHECK constraint
3. Update existing projects:
   - Set `quote_expiry_date` for projects in "Quote & Approval"
   - Mark old "Cancelled" projects as `can_reinstate = True`
4. Create new indexes
5. Update schema version to 10.0

**Rollback:** `migrations/rollback_v10_0.sql`

---

## 📊 Testing Plan

### Unit Tests

1. **Status Validation Tests**
   - Test `is_ready_for_quote_approval` property
   - Test `is_quote_expired` property
   - Test field validation logic

2. **Automation Tests**
   - Test auto-advance from Request → Quote & Approval
   - Test 30-day expiry auto-cancellation
   - Test POP received auto-queue

3. **Route Tests**
   - Test on hold toggle
   - Test reinstate workflow
   - Test status update with validation

### Integration Tests

1. **End-to-End Workflow**
   - Create project → Auto-advance → Send quote → Receive POP → Auto-queue → Complete
   - Create project → Quote expires → Auto-cancel → Reinstate

2. **Timer Tests**
   - Test quote expiry checker
   - Test 25-day reminder sender

---

## 📅 Implementation Timeline

| Phase | Tasks | Duration | Dependencies |
|-------|-------|----------|--------------|
| **Phase 1** | Database schema changes | 1 day | None |
| **Phase 2** | Backend model updates | 1 day | Phase 1 |
| **Phase 3** | Status automation service | 2 days | Phase 2 |
| **Phase 4** | Background scheduler | 1 day | Phase 3 |
| **Phase 5** | Route updates | 2 days | Phase 2-4 |
| **Phase 6** | Frontend/UI updates | 2 days | Phase 5 |
| **Phase 7** | Notification system | 2 days | Phase 3-5 |
| **Phase 8** | Testing | 2 days | All phases |
| **Phase 9** | Documentation | 1 day | All phases |

**Total Estimated Time:** 14 days

---

## 🎨 Frontend/UI Changes

### Phase 6: Template Updates

**Task 6.1: Update Project Detail Page**

**File:** `app/templates/projects/detail.html`

**Changes:**
1. Add "On Hold" badge display
2. Add "Reinstate" button for cancelled projects
3. Add quote expiry countdown
4. Update status badge colors

```html
<!-- Status Badge with On Hold Indicator -->
<div class="status-badges">
    <span class="badge badge-lg badge-{{ project.status|lower|replace(' ', '-') }}">
        {{ project.status }}
    </span>

    {% if project.on_hold %}
        <span class="badge badge-lg badge-warning">
            ⏸️ ON HOLD
        </span>
    {% endif %}

    {% if project.status == 'Quote & Approval' and project.days_until_quote_expiry %}
        {% if project.days_until_quote_expiry <= 5 %}
            <span class="badge badge-lg badge-danger">
                ⏰ Quote expires in {{ project.days_until_quote_expiry }} days
            </span>
        {% elif project.days_until_quote_expiry <= 10 %}
            <span class="badge badge-lg badge-warning">
                ⏰ Quote expires in {{ project.days_until_quote_expiry }} days
            </span>
        {% endif %}
    {% endif %}

    {% if project.status == 'Cancelled' and project.can_reinstate %}
        <span class="badge badge-lg badge-info">
            ♻️ CAN REINSTATE
        </span>
    {% endif %}
</div>

<!-- Action Buttons -->
<div class="action-buttons">
    {% if project.status == 'Cancelled' and project.can_reinstate %}
        <form method="POST" action="{{ url_for('projects.reinstate', id=project.id) }}" style="display: inline;">
            <button type="submit" class="btn btn-success" onclick="return confirm('Reinstate this project with a new 30-day quote period?')">
                ♻️ Reinstate Project
            </button>
        </form>
    {% endif %}

    {% if project.status not in ['Completed', 'Cancelled'] %}
        <button type="button" class="btn btn-warning" onclick="toggleHold({{ project.id }}, {{ 'true' if project.on_hold else 'false' }})">
            {% if project.on_hold %}
                ▶️ Resume Project
            {% else %}
                ⏸️ Put On Hold
            {% endif %}
        </button>
    {% endif %}
</div>
```

**Task 6.2: Add On Hold Modal**

```html
<!-- On Hold Modal -->
<div id="holdModal" class="modal">
    <div class="modal-content">
        <h3>Put Project On Hold</h3>
        <form method="POST" action="{{ url_for('projects.toggle_hold', id=project.id) }}">
            <div class="form-group">
                <label for="hold_reason">Reason for Hold:</label>
                <textarea id="hold_reason" name="reason" class="form-control" rows="3" required></textarea>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-warning">Put On Hold</button>
                <button type="button" class="btn btn-secondary" onclick="closeHoldModal()">Cancel</button>
            </div>
        </form>
    </div>
</div>

<script>
function toggleHold(projectId, isOnHold) {
    if (isOnHold === 'true') {
        // Resume - direct submit
        if (confirm('Resume this project?')) {
            fetch(`/projects/${projectId}/toggle-hold`, {
                method: 'POST'
            }).then(() => location.reload());
        }
    } else {
        // Put on hold - show modal
        document.getElementById('holdModal').style.display = 'block';
    }
}

function closeHoldModal() {
    document.getElementById('holdModal').style.display = 'none';
}
</script>
```

**Task 6.3: Update Project List Page**

**File:** `app/templates/projects/index.html`

**Changes:**
1. Add "On Hold" filter
2. Show quote expiry warnings
3. Add reinstate action

```html
<!-- Filter Bar -->
<div class="filter-bar">
    <a href="{{ url_for('projects.index', status='active') }}"
       class="filter-btn {% if status_filter == 'active' %}active{% endif %}">
        Active
    </a>
    <a href="{{ url_for('projects.index', status='on_hold') }}"
       class="filter-btn {% if status_filter == 'on_hold' %}active{% endif %}">
        On Hold
    </a>
    <a href="{{ url_for('projects.index', status='expiring_soon') }}"
       class="filter-btn {% if status_filter == 'expiring_soon' %}active{% endif %}">
        Expiring Soon (< 5 days)
    </a>
    <!-- ... existing filters ... -->
</div>

<!-- Project Table -->
<table class="table">
    <thead>
        <tr>
            <th>Code</th>
            <th>Client</th>
            <th>Name</th>
            <th>Status</th>
            <th>Quote Expiry</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for project in projects %}
        <tr class="{% if project.on_hold %}on-hold-row{% endif %}">
            <td>{{ project.project_code }}</td>
            <td>{{ project.client.name }}</td>
            <td>{{ project.name }}</td>
            <td>
                <span class="badge badge-{{ project.status|lower|replace(' ', '-') }}">
                    {{ project.status }}
                </span>
                {% if project.on_hold %}
                    <span class="badge badge-warning badge-sm">ON HOLD</span>
                {% endif %}
            </td>
            <td>
                {% if project.status == 'Quote & Approval' and project.days_until_quote_expiry %}
                    {% if project.days_until_quote_expiry <= 0 %}
                        <span class="text-danger">EXPIRED</span>
                    {% elif project.days_until_quote_expiry <= 5 %}
                        <span class="text-danger">{{ project.days_until_quote_expiry }} days</span>
                    {% else %}
                        <span class="text-muted">{{ project.days_until_quote_expiry }} days</span>
                    {% endif %}
                {% else %}
                    —
                {% endif %}
            </td>
            <td>
                <a href="{{ url_for('projects.detail', id=project.id) }}" class="btn btn-sm btn-primary">View</a>
                {% if project.can_reinstate %}
                    <a href="{{ url_for('projects.reinstate', id=project.id) }}"
                       class="btn btn-sm btn-success"
                       onclick="return confirm('Reinstate this project?')">
                        Reinstate
                    </a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## 📧 Notification System

### Phase 7: Notification Service

**Task 7.1: Create Notification Service**

**File:** `app/services/notification_service.py` (NEW)

```python
from flask import current_app, render_template
from flask_mail import Message
from app import mail
from app.models import Communication, db
from datetime import datetime

def send_notification(recipient, subject, template, context, notification_type='email'):
    """
    Send notification to recipient.

    Args:
        recipient: Email address or phone number
        subject: Notification subject
        template: Template name (without extension)
        context: Template context dictionary
        notification_type: 'email', 'sms', or 'whatsapp'

    Returns:
        dict: {
            'sent': bool,
            'message': str,
            'communication_id': int or None
        }
    """
    try:
        if notification_type == 'email':
            return send_email_notification(recipient, subject, template, context)
        elif notification_type == 'sms':
            return send_sms_notification(recipient, template, context)
        elif notification_type == 'whatsapp':
            return send_whatsapp_notification(recipient, template, context)
        else:
            return {'sent': False, 'message': 'Invalid notification type'}
    except Exception as e:
        current_app.logger.error(f'Notification error: {str(e)}')
        return {'sent': False, 'message': str(e)}

def send_email_notification(recipient, subject, template, context):
    """Send email notification."""
    try:
        # Render email template
        html_body = render_template(f'emails/{template}.html', **context)
        text_body = render_template(f'emails/{template}.txt', **context)

        # Create message
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_body,
            body=text_body
        )

        # Send email
        mail.send(msg)

        # Log communication
        comm = Communication(
            comm_type=Communication.TYPE_EMAIL,
            direction=Communication.DIRECTION_OUTBOUND,
            client_id=context.get('project').client_id if 'project' in context else None,
            project_id=context.get('project').id if 'project' in context else None,
            subject=subject,
            body=text_body,
            from_address=current_app.config['MAIL_DEFAULT_SENDER'],
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
        return {'sent': False, 'message': str(e)}

def send_quote_expiry_reminder(project):
    """Send quote expiry reminder to client."""
    return send_notification(
        recipient=project.client.email,
        subject=f'Quote Expiring Soon - {project.project_code}',
        template='quote_expiry_reminder',
        context={
            'project': project,
            'days_remaining': project.days_until_quote_expiry
        },
        notification_type='email'
    )

def send_quote_expired_notice(project):
    """Send quote expired notice to client and admin."""
    # Send to client
    client_result = send_notification(
        recipient=project.client.email,
        subject=f'Quote Expired - {project.project_code}',
        template='quote_expired',
        context={'project': project},
        notification_type='email'
    )

    # Send to admin
    admin_result = send_notification(
        recipient=current_app.config['ADMIN_EMAIL'],
        subject=f'Quote Expired - {project.project_code}',
        template='quote_expired_admin',
        context={'project': project},
        notification_type='email'
    )

    return {
        'client_sent': client_result['sent'],
        'admin_sent': admin_result['sent']
    }

def send_pop_received_notice(project):
    """Send POP received notice to scheduler."""
    return send_notification(
        recipient=current_app.config['SCHEDULER_EMAIL'],
        subject=f'POP Received - {project.project_code} Queued',
        template='pop_received',
        context={'project': project},
        notification_type='email'
    )

def send_job_started_notice(project, operator):
    """Send job started notice to admin."""
    return send_notification(
        recipient=current_app.config['ADMIN_EMAIL'],
        subject=f'Job Started - {project.project_code}',
        template='job_started',
        context={
            'project': project,
            'operator': operator
        },
        notification_type='email'
    )

def send_job_completed_notice(project):
    """Send job completed notice to client and operator."""
    # Send to client
    client_result = send_notification(
        recipient=project.client.email,
        subject=f'Job Completed - {project.project_code}',
        template='job_completed_client',
        context={'project': project},
        notification_type='email'
    )

    return client_result
```

**Task 7.2: Create Email Templates**

**Files to Create:**
- `app/templates/emails/quote_expiry_reminder.html`
- `app/templates/emails/quote_expiry_reminder.txt`
- `app/templates/emails/quote_expired.html`
- `app/templates/emails/quote_expired.txt`
- `app/templates/emails/pop_received.html`
- `app/templates/emails/pop_received.txt`
- `app/templates/emails/job_started.html`
- `app/templates/emails/job_started.txt`
- `app/templates/emails/job_completed_client.html`
- `app/templates/emails/job_completed_client.txt`

---

## 🔧 Configuration Updates

### Task 8.1: Update Config File

**File:** `config.py`

```python
# Status System Configuration
AUTO_ADVANCE_TO_QUOTE = True  # Auto-advance from Request to Quote & Approval
QUOTE_EXPIRY_DAYS = 30  # Days until quote expires
QUOTE_REMINDER_DAYS = 25  # Send reminder at this many days
AUTO_CANCEL_EXPIRED_QUOTES = True  # Auto-cancel expired quotes
AUTO_QUEUE_ON_POP = True  # Auto-queue when POP received

# Notification Configuration
ADMIN_EMAIL = 'admin@laseros.com'
SCHEDULER_EMAIL = 'scheduler@laseros.com'
ENABLE_EMAIL_NOTIFICATIONS = True
ENABLE_SMS_NOTIFICATIONS = False
ENABLE_WHATSAPP_NOTIFICATIONS = False

# Scheduler Configuration
ENABLE_BACKGROUND_SCHEDULER = True
QUOTE_EXPIRY_CHECK_HOUR = 9  # Check at 9 AM daily
QUOTE_REMINDER_CHECK_HOUR = 10  # Send reminders at 10 AM daily
```

---

## 📊 Impact Analysis

### Affected Components

| Component | Impact Level | Changes Required |
|-----------|-------------|------------------|
| **Database Schema** | 🔴 HIGH | Add columns, update constraints, create indexes |
| **Project Model** | 🔴 HIGH | Add fields, properties, validation methods |
| **Project Routes** | 🟡 MEDIUM | Add new routes, update existing logic |
| **Templates** | 🟡 MEDIUM | Update UI, add new components |
| **Status Automation** | 🔴 HIGH | Create new service, implement timers |
| **Notification System** | 🟡 MEDIUM | Create service, add email templates |
| **Background Scheduler** | 🔴 HIGH | Implement APScheduler, add jobs |
| **Activity Logging** | 🟢 LOW | Add new event types |
| **Queue System** | 🟢 LOW | Minor updates to auto-queue logic |
| **API Endpoints** | 🟡 MEDIUM | Add new endpoints, update responses |

### Backward Compatibility

**Breaking Changes:**
- ❌ Legacy status values removed from VALID_STATUSES
- ❌ Existing projects with legacy statuses need migration

**Migration Strategy:**
```sql
-- Migrate legacy statuses to new equivalents
UPDATE projects SET status = 'Quote & Approval' WHERE status = 'Quote';
UPDATE projects SET status = 'Approved (POP Received)' WHERE status = 'Approved';
```

**Non-Breaking Changes:**
- ✅ New fields added with defaults
- ✅ Existing automation logic preserved
- ✅ API responses remain compatible

---

## ⚠️ Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Data Loss During Migration** | 🔴 HIGH | 🟢 LOW | Full database backup before migration, rollback script ready |
| **Timer Jobs Failing** | 🟡 MEDIUM | 🟡 MEDIUM | Comprehensive error handling, logging, manual fallback |
| **Email Delivery Issues** | 🟡 MEDIUM | 🟡 MEDIUM | Queue failed emails, retry logic, admin alerts |
| **Performance Impact** | 🟢 LOW | 🟢 LOW | Indexed columns, optimized queries, background jobs |
| **User Confusion** | 🟡 MEDIUM | 🟡 MEDIUM | Clear documentation, training, UI tooltips |
| **Scheduler Downtime** | 🟡 MEDIUM | 🟢 LOW | Persistent job store, catch-up logic on restart |

---

## ✅ Acceptance Criteria

### Functional Requirements

- [ ] Projects auto-advance from Request to Quote & Approval when all fields valid
- [ ] 30-day timer starts when project enters Quote & Approval status
- [ ] Projects auto-cancel after 30 days if no POP received
- [ ] 25-day reminder email sent to clients
- [ ] POP received triggers auto-queue with inventory check
- [ ] On Hold flag can be toggled with reason
- [ ] Cancelled projects can be reinstated with new 30-day period
- [ ] All status changes logged in activity log
- [ ] Notifications sent for all key events
- [ ] Background scheduler runs daily checks

### Non-Functional Requirements

- [ ] Migration completes without data loss
- [ ] All existing projects migrated to new status values
- [ ] Performance impact < 5% on project queries
- [ ] Email delivery rate > 95%
- [ ] Background jobs complete within 5 minutes
- [ ] UI responsive on mobile devices
- [ ] Documentation complete and accurate

---

## 📚 Documentation Requirements

### User Documentation

1. **Status System Guide** - Updated with new workflow
2. **On Hold Feature Guide** - How to use on hold functionality
3. **Reinstate Workflow Guide** - How to reinstate cancelled projects
4. **Quote Expiry Guide** - Understanding the 30-day timer

### Technical Documentation

1. **API Documentation** - New endpoints and updated responses
2. **Database Schema** - Updated ERD and field descriptions
3. **Automation Logic** - Flow diagrams for all automations
4. **Scheduler Configuration** - How to configure and monitor jobs
5. **Notification Templates** - Available templates and customization

### Migration Documentation

1. **Migration Guide** - Step-by-step migration instructions
2. **Rollback Procedure** - How to rollback if needed
3. **Data Mapping** - Old status → New status mapping
4. **Verification Checklist** - Post-migration verification steps

---

## 🚀 Deployment Plan

### Pre-Deployment

1. ✅ Complete all development tasks
2. ✅ Pass all unit and integration tests
3. ✅ Complete code review
4. ✅ Update documentation
5. ✅ Create full database backup
6. ✅ Test migration on staging environment
7. ✅ Prepare rollback scripts

### Deployment Steps

1. **Maintenance Mode** - Put application in maintenance mode
2. **Database Backup** - Create timestamped backup
3. **Run Migration** - Execute schema_v10_0_status_redesign.sql
4. **Verify Migration** - Run verification script
5. **Deploy Code** - Deploy updated application code
6. **Start Scheduler** - Initialize background scheduler
7. **Smoke Tests** - Test critical workflows
8. **Exit Maintenance** - Return to normal operation
9. **Monitor** - Watch logs for errors

### Post-Deployment

1. Monitor background jobs for 24 hours
2. Verify email notifications working
3. Check quote expiry timer accuracy
4. Review activity logs for anomalies
5. Gather user feedback
6. Address any issues immediately

---

## 📞 Support and Rollback

### Rollback Procedure

If critical issues arise:

```bash
# 1. Put application in maintenance mode
# 2. Stop background scheduler
# 3. Restore database backup
cp data/laser_os.db.backup_v9_2 data/laser_os.db

# 4. Run rollback migration
python scripts/migrations/rollback_v10_0.py

# 5. Deploy previous code version
git checkout v9.2

# 6. Restart application
# 7. Exit maintenance mode
```

### Support Contacts

- **Technical Lead:** [Name]
- **Database Admin:** [Name]
- **DevOps:** [Name]

---

**Document Version:** 1.0
**Last Updated:** 2025-10-23
**Status:** 📋 AWAITING APPROVAL
