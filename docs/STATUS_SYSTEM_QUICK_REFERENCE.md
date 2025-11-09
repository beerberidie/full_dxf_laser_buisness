# Laser OS - Status System Quick Reference

**Version:** 1.0  
**Date:** 2025-10-23

---

## 📊 Status Values at a Glance

### Project Statuses (9 Total)

| # | Status | Constant | Color | Description |
|---|--------|----------|-------|-------------|
| 1 | Request | `STATUS_REQUEST` | 🟡 Yellow | Initial customer inquiry |
| 2 | Quote & Approval | `STATUS_QUOTE_APPROVAL` | 🟡 Yellow | Quote sent to client |
| 3 | Approved (POP Received) | `STATUS_APPROVED_POP` | 🔵 Blue | Payment received |
| 4 | Queued (Scheduled for Cutting) | `STATUS_QUEUED` | 🔵 Blue | Added to production queue |
| 5 | In Progress | `STATUS_IN_PROGRESS` | 🟣 Purple | Active production |
| 6 | Completed | `STATUS_COMPLETED` | 🟢 Green | Delivered to client |
| 7 | Cancelled | `STATUS_CANCELLED` | 🔴 Red | Project cancelled |
| 8 | Quote (Legacy) | `STATUS_QUOTE` | 🟡 Yellow | Legacy status |
| 9 | Approved (Legacy) | `STATUS_APPROVED` | 🔵 Blue | Legacy status |

**Default:** `Quote`  
**File:** `app/models/business.py` (Lines 90-114)

---

### Queue Statuses (4 Total)

| # | Status | Constant | Color | Description |
|---|--------|----------|-------|-------------|
| 1 | Queued | `STATUS_QUEUED` | 🔵 Blue | Waiting in queue |
| 2 | In Progress | `STATUS_IN_PROGRESS` | 🔵 Blue | Currently being cut |
| 3 | Completed | `STATUS_COMPLETED` | 🟢 Green | Cutting finished |
| 4 | Cancelled | `STATUS_CANCELLED` | ⚪ Gray | Removed from queue |

**Default:** `Queued`  
**File:** `app/models/business.py` (Lines 728-732)

---

### Queue Priorities (4 Levels)

| # | Priority | Constant | Color | Description |
|---|----------|----------|-------|-------------|
| 1 | Urgent | `PRIORITY_URGENT` | 🔴 Red | Critical/rush jobs |
| 2 | High | `PRIORITY_HIGH` | 🟡 Yellow | High priority jobs |
| 3 | Normal | `PRIORITY_NORMAL` | ⚪ Gray | Standard jobs |
| 4 | Low | `PRIORITY_LOW` | ⚪ Gray | Low priority jobs |

**Default:** `Normal`  
**File:** `app/models/business.py` (Lines 734-738)

---

### Quote Statuses (5 Total)

| # | Status | Constant | Color | Description |
|---|--------|----------|-------|-------------|
| 1 | Draft | `STATUS_DRAFT` | ⚪ Gray | Quote being prepared |
| 2 | Sent | `STATUS_SENT` | 🔵 Blue | Quote sent to client |
| 3 | Accepted | `STATUS_ACCEPTED` | 🟢 Green | Client accepted quote |
| 4 | Rejected | `STATUS_REJECTED` | 🔴 Red | Client rejected quote |
| 5 | Expired | `STATUS_EXPIRED` | 🟡 Yellow | Quote validity expired |

**Default:** `Draft`  
**File:** `app/models/business.py` (Lines 1038-1043)

---

### Invoice Statuses (6 Total)

| # | Status | Constant | Color | Description |
|---|--------|----------|-------|-------------|
| 1 | Draft | `STATUS_DRAFT` | ⚪ Gray | Invoice being prepared |
| 2 | Sent | `STATUS_SENT` | 🔵 Blue | Invoice sent to client |
| 3 | Paid | `STATUS_PAID` | 🟢 Green | Fully paid |
| 4 | Partially Paid | `STATUS_PARTIAL` | 🟡 Yellow | Partial payment received |
| 5 | Overdue | `STATUS_OVERDUE` | 🔴 Red | Past due date, unpaid |
| 6 | Cancelled | `STATUS_CANCELLED` | 🔴 Red | Invoice cancelled |

**Default:** `Draft`  
**File:** `app/models/business.py` (Lines 1098-1104)

---

### Communication Statuses (5 Total)

| # | Status | Constant | Color | Description |
|---|--------|----------|-------|-------------|
| 1 | Pending | `STATUS_PENDING` | 🟡 Yellow | Queued for sending |
| 2 | Sent | `STATUS_SENT` | 🔵 Blue | Successfully sent |
| 3 | Delivered | `STATUS_DELIVERED` | 🟢 Green | Delivered to recipient |
| 4 | Read | `STATUS_READ` | 🟢 Light Green | Read by recipient |
| 5 | Failed | `STATUS_FAILED` | 🔴 Red | Failed to send |

**Default:** `Pending`  
**File:** `app/models/business.py` (Lines 1294-1301)

---

## 🔄 Status Workflows

### Project Lifecycle

```
Request → Quote & Approval → Approved (POP Received) → Queued → In Progress → Completed
                                                                                    ↓
                                                                              Cancelled
```

### Queue Lifecycle

```
Queued → In Progress → Completed
   ↓
Cancelled
```

### Quote Lifecycle

```
Draft → Sent → Accepted
         ↓       ↓
      Rejected  Expired
```

### Invoice Lifecycle

```
Draft → Sent → Partially Paid → Paid
         ↓           ↓
      Overdue    Cancelled
```

### Communication Lifecycle

```
Pending → Sent → Delivered → Read
   ↓
Failed
```

---

## ⚡ Status-Triggered Automations

### POP Received → Auto-Queue

**Trigger:** User marks POP as received  
**Actions:**
1. Set `pop_received = True`
2. Set `pop_received_date = today`
3. Calculate `pop_deadline = today + 3 days`
4. Update `project.status = 'Approved (POP Received)'`
5. Create QueueItem with defaults
6. Log activity

**File:** `app/routes/projects.py` (Lines 618-681)

---

### Queue Status → Timestamp Updates

**Trigger:** Queue status changed  
**Actions:**
- `Queued` → `In Progress`: Set `started_at = now`
- `In Progress` → `Completed`: Set `completed_at = now`

**File:** `app/routes/queue.py` (Lines 167-176)

---

### Project Status → Date Updates

**Trigger:** Project status changed  
**Actions:**
- `Approved`: Set `approval_date = today`
- `Completed`: Set `completion_date = today`

**File:** `app/routes/projects.py` (Lines 490-494)

---

## 💻 Code Snippets

### Check Project Status

```python
from app.models import Project

project = Project.query.get(1)

if project.status == Project.STATUS_COMPLETED:
    print("Project is completed!")
```

### Update Project Status

```python
project.status = Project.STATUS_IN_PROGRESS
project.updated_at = datetime.utcnow()
db.session.commit()
```

### Filter by Status

```python
# Get all completed projects
completed = Project.query.filter_by(
    status=Project.STATUS_COMPLETED
).all()

# Get active projects
active = Project.query.filter(
    Project.status.in_([
        Project.STATUS_IN_PROGRESS,
        Project.STATUS_QUEUED
    ])
).all()
```

### Create Queue Item

```python
queue_item = QueueItem(
    project_id=1,
    queue_position=1,
    status=QueueItem.STATUS_QUEUED,
    priority=QueueItem.PRIORITY_NORMAL,
    scheduled_date=date.today()
)
db.session.add(queue_item)
db.session.commit()
```

### Validate Status

```python
new_status = 'In Progress'

if new_status not in Project.VALID_STATUSES:
    raise ValueError(f'Invalid status: {new_status}')

project.status = new_status
```

---

## 🎨 CSS Badge Classes

### Project Status Badges

```css
.badge-request              /* Yellow */
.badge-quote-&-approval     /* Yellow */
.badge-approved-(pop-received) /* Blue */
.badge-queued-(scheduled-for-cutting) /* Blue */
.badge-in-progress          /* Purple */
.badge-completed            /* Green */
.badge-cancelled            /* Red */
```

### Queue Status Badges

```css
.badge-info      /* Queued - Blue */
.badge-primary   /* In Progress - Blue */
.badge-success   /* Completed - Green */
.badge-secondary /* Cancelled - Gray */
```

### Priority Badges

```css
.badge-danger    /* Urgent - Red */
.badge-warning   /* High - Yellow */
.badge-secondary /* Normal/Low - Gray */
```

### Communication Status Badges

```css
.badge-pending   /* Yellow */
.badge-sent      /* Blue */
.badge-delivered /* Green */
.badge-read      /* Light Green */
.badge-failed    /* Red */
```

---

## 📁 Key Files

| File | Description |
|------|-------------|
| `app/models/business.py` | Status constants and model definitions |
| `app/routes/projects.py` | Project status update logic |
| `app/routes/queue.py` | Queue status update logic |
| `app/services/activity_logger.py` | Status change logging |
| `app/services/auto_scheduler.py` | Auto-queue automation |
| `app/static/css/main.css` | Status badge styling |
| `migrations/schema_v9_1_fix_project_status_constraint.sql` | Project status CHECK constraint |

---

## 🔍 Database Schema

### Status Columns

```sql
-- Projects
status VARCHAR(50) NOT NULL DEFAULT 'Quote'

-- Queue Items
status VARCHAR(50) NOT NULL DEFAULT 'Queued'
priority VARCHAR(20) DEFAULT 'Normal'

-- Quotes
status VARCHAR(50) NOT NULL DEFAULT 'Draft'

-- Invoices
status VARCHAR(50) NOT NULL DEFAULT 'Draft'

-- Communications
status VARCHAR(50) DEFAULT 'Pending'
```

### Status Indexes

```sql
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_queue_items_status_position ON queue_items(status, queue_position);
CREATE INDEX idx_quotes_status ON quotes(status);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_communications_status ON communications(status);
```

---

## ✅ Best Practices

1. ✅ **Use constants** - `Project.STATUS_COMPLETED` not `'Completed'`
2. ✅ **Validate status** - Check against `VALID_STATUSES` before setting
3. ✅ **Log changes** - Use activity logger for audit trail
4. ✅ **Update timestamps** - Set relevant date fields on status changes
5. ✅ **Use transactions** - Wrap status updates in database transactions
6. ✅ **Check automations** - Some status changes trigger side effects

---

## 📚 Full Documentation

For comprehensive details, see:
- **`docs/STATUS_SYSTEM_COMPREHENSIVE_GUIDE.md`** - Complete status system documentation

---

**Quick Reference Version:** 1.0  
**Last Updated:** 2025-10-23
