# Laser OS - Comprehensive Status System Guide

**Version:** 1.0  
**Date:** 2025-10-23  
**Author:** System Documentation

---

## 📋 Table of Contents

1. [Project Status System](#1-project-status-system)
2. [Queue Status System](#2-queue-status-system)
3. [Quote Status System](#3-quote-status-system)
4. [Invoice Status System](#4-invoice-status-system)
5. [Communication Status System](#5-communication-status-system)
6. [Status-Triggered Automations](#6-status-triggered-automations)
7. [Database Schema](#7-database-schema)
8. [Visual Indicators & UI](#8-visual-indicators--ui)
9. [Code Examples](#9-code-examples)

---

## 1. Project Status System

### 1.1 Available Status Values

**File:** `app/models/business.py` (Lines 90-114)

#### **Phase 9 Enhanced Statuses (Current)**

| Status Constant | Status Value | Description | Use Case |
|----------------|--------------|-------------|----------|
| `STATUS_REQUEST` | `'Request'` | Initial project request | Customer inquiry received |
| `STATUS_QUOTE_APPROVAL` | `'Quote & Approval'` | Quote sent, awaiting approval | Quote generated and sent to client |
| `STATUS_APPROVED_POP` | `'Approved (POP Received)'` | Approved with proof of payment | Client approved and paid |
| `STATUS_QUEUED` | `'Queued (Scheduled for Cutting)'` | Scheduled in production queue | Added to laser cutting queue |
| `STATUS_IN_PROGRESS` | `'In Progress'` | Currently being worked on | Active production |
| `STATUS_COMPLETED` | `'Completed'` | Project finished | Delivered to client |
| `STATUS_CANCELLED` | `'Cancelled'` | Project cancelled | Client cancelled or rejected |

#### **Legacy Statuses (Backward Compatibility)**

| Status Constant | Status Value | Description |
|----------------|--------------|-------------|
| `STATUS_QUOTE` | `'Quote'` | Legacy quote status |
| `STATUS_APPROVED` | `'Approved'` | Legacy approved status |

**Total Valid Statuses:** 9 (7 current + 2 legacy)

### 1.2 Status Workflow & Lifecycle

```
┌─────────────┐
│   Request   │ ← Initial customer inquiry
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│ Quote & Approval    │ ← Quote sent to client
└──────┬──────────────┘
       │
       ↓
┌──────────────────────────┐
│ Approved (POP Received)  │ ← Payment received
└──────┬───────────────────┘
       │
       ↓ (Auto-queue trigger)
┌────────────────────────────────┐
│ Queued (Scheduled for Cutting) │ ← Added to production queue
└──────┬─────────────────────────┘
       │
       ↓
┌─────────────────┐
│  In Progress    │ ← Active production
└──────┬──────────┘
       │
       ↓
┌─────────────┐
│  Completed  │ ← Delivered to client
└─────────────┘

       OR (at any stage)
       
┌─────────────┐
│  Cancelled  │ ← Project cancelled
└─────────────┘
```

### 1.3 Status Change Triggers

#### **Manual Status Changes**

**Route:** `app/routes/projects.py` - `update_status()` (Lines 467-509)

- User selects new status from dropdown
- AJAX endpoint validates status
- Updates `project.status` and `project.updated_at`
- Auto-sets dates based on status
- Logs activity

#### **Automatic Status Changes**

| Trigger | Old Status | New Status | Automation |
|---------|-----------|------------|------------|
| POP Received | Any | `Approved (POP Received)` | Sets `pop_received_date`, calculates `pop_deadline` |
| Auto-Queue | `Approved (POP Received)` | `Queued (Scheduled for Cutting)` | Creates QueueItem, adds to queue |
| Queue Start | `Queued` | `In Progress` | Updates `started_at` timestamp |
| Queue Complete | `In Progress` | `Completed` | Updates `completed_at` timestamp |

### 1.4 Status-Related Properties

**File:** `app/models/business.py` (Lines 220-236)

```python
@property
def is_overdue(self):
    """Check if project is overdue."""
    if self.due_date and self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
        from datetime import date
        return date.today() > self.due_date
    return False

@property
def days_until_due(self):
    """Calculate days until due date."""
    if self.due_date and self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
        from datetime import date
        delta = self.due_date - date.today()
        return delta.days
    return None
```

### 1.5 Timestamp Tracking

**Auto-set Dates on Status Change:**

**File:** `app/routes/projects.py` (Lines 490-494)

```python
# Auto-set dates based on status
if new_status == Project.STATUS_APPROVED and not project.approval_date:
    project.approval_date = date.today()
elif new_status == Project.STATUS_COMPLETED and not project.completion_date:
    project.completion_date = date.today()
```

**Tracked Timestamps:**
- `quote_date` - When quote was created
- `approval_date` - When project was approved
- `due_date` - Project deadline
- `completion_date` - When project was completed
- `pop_received_date` - When proof of payment was received
- `pop_deadline` - Auto-calculated (POP date + 3 days)
- `created_at` - Project creation timestamp
- `updated_at` - Last update timestamp

---

## 2. Queue Status System

### 2.1 Available Status Values

**File:** `app/models/business.py` (Lines 728-732)

| Status Constant | Status Value | Description |
|----------------|--------------|-------------|
| `STATUS_QUEUED` | `'Queued'` | Waiting in queue |
| `STATUS_IN_PROGRESS` | `'In Progress'` | Currently being cut |
| `STATUS_COMPLETED` | `'Completed'` | Cutting finished |
| `STATUS_CANCELLED` | `'Cancelled'` | Removed from queue |

**Total Valid Statuses:** 4

### 2.2 Priority Levels

**File:** `app/models/business.py` (Lines 734-738)

| Priority Constant | Priority Value | Description | Queue Ordering |
|------------------|----------------|-------------|----------------|
| `PRIORITY_URGENT` | `'Urgent'` | Critical/rush jobs | Highest priority |
| `PRIORITY_HIGH` | `'High'` | High priority jobs | High priority |
| `PRIORITY_NORMAL` | `'Normal'` | Standard jobs | Normal priority |
| `PRIORITY_LOW` | `'Low'` | Low priority jobs | Lowest priority |

**Default Priority:** `PRIORITY_NORMAL`

### 2.3 Queue Ordering Logic

**Primary Sort:** `queue_position` (ascending)  
**Secondary Sort:** `priority` (Urgent > High > Normal > Low)  
**Tertiary Sort:** `scheduled_date` (ascending)

**File:** `app/routes/queue.py` (Lines 23-31)

```python
# Build query
query = QueueItem.query

if status_filter == 'active':
    query = query.filter(QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS]))
elif status_filter != 'all':
    query = query.filter_by(status=status_filter)

# Order by queue position
queue_items = query.order_by(QueueItem.queue_position).all()
```

### 2.4 Status Change Automations

**File:** `app/routes/queue.py` (Lines 167-176)

```python
# Update timestamps
if new_status == QueueItem.STATUS_IN_PROGRESS and not queue_item.started_at:
    queue_item.started_at = datetime.utcnow()
elif new_status == QueueItem.STATUS_COMPLETED and not queue_item.completed_at:
    queue_item.completed_at = datetime.utcnow()
```

**Tracked Timestamps:**
- `added_at` - When added to queue
- `started_at` - When cutting started
- `completed_at` - When cutting finished
- `scheduled_date` - Planned cutting date

### 2.5 Automatic Queue Creation

**Trigger:** POP (Proof of Payment) marked as received

**File:** `app/routes/projects.py` (Lines 587-608)

```python
# Get next queue position
max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
next_position = max_position + 1

# Determine scheduled date (today or next business day)
scheduled_date = date.today()

# Create queue item with sensible defaults
queue_item = QueueItem(
    project_id=project.id,
    queue_position=next_position,
    status=QueueItem.STATUS_QUEUED,
    priority=QueueItem.PRIORITY_NORMAL,
    scheduled_date=scheduled_date,
    estimated_cut_time=project.estimated_cut_time if project.estimated_cut_time else None,
    notes='Automatically added to queue when POP was received',
    added_by='System (Auto)'
)
```

**Default Values:**
- Status: `Queued`
- Priority: `Normal`
- Scheduled Date: Today
- Estimated Cut Time: From `project.estimated_cut_time`
- Queue Position: Auto-calculated (max + 1)
- Added By: `System (Auto)`

---

## 3. Quote Status System

### 3.1 Available Status Values

**File:** `app/models/business.py` (Lines 1038-1043)

| Status Constant | Status Value | Description |
|----------------|--------------|-------------|
| `STATUS_DRAFT` | `'Draft'` | Quote being prepared |
| `STATUS_SENT` | `'Sent'` | Quote sent to client |
| `STATUS_ACCEPTED` | `'Accepted'` | Client accepted quote |
| `STATUS_REJECTED` | `'Rejected'` | Client rejected quote |
| `STATUS_EXPIRED` | `'Expired'` | Quote validity expired |

**Total Valid Statuses:** 5

### 3.2 Quote Workflow

```
┌────────┐
│ Draft  │ ← Quote being prepared
└───┬────┘
    │
    ↓
┌────────┐
│  Sent  │ ← Quote sent to client
└───┬────┘
    │
    ├─→ ┌──────────┐
    │   │ Accepted │ ← Client approved
    │   └──────────┘
    │
    ├─→ ┌──────────┐
    │   │ Rejected │ ← Client declined
    │   └──────────┘
    │
    └─→ ┌──────────┐
        │ Expired  │ ← Past valid_until date
        └──────────┘
```

### 3.3 Quote Status Fields

**File:** `app/models/business.py` (Lines 1045-1056)

```python
id = db.Column(db.Integer, primary_key=True)
quote_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'))
client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
quote_date = db.Column(db.Date, nullable=False)
valid_until = db.Column(db.Date)
status = db.Column(db.String(50), nullable=False, default=STATUS_DRAFT, index=True)
```

**Default Status:** `Draft`

---

## 4. Invoice Status System

### 4.1 Available Status Values

**File:** `app/models/business.py` (Lines 1098-1104)

| Status Constant | Status Value | Description |
|----------------|--------------|-------------|
| `STATUS_DRAFT` | `'Draft'` | Invoice being prepared |
| `STATUS_SENT` | `'Sent'` | Invoice sent to client |
| `STATUS_PAID` | `'Paid'` | Fully paid |
| `STATUS_PARTIAL` | `'Partially Paid'` | Partial payment received |
| `STATUS_OVERDUE` | `'Overdue'` | Past due date, unpaid |
| `STATUS_CANCELLED` | `'Cancelled'` | Invoice cancelled |

**Total Valid Statuses:** 6

### 4.2 Invoice Workflow

```
┌────────┐
│ Draft  │ ← Invoice being prepared
└───┬────┘
    │
    ↓
┌────────┐
│  Sent  │ ← Invoice sent to client
└───┬────┘
    │
    ├─→ ┌──────────────────┐
    │   │ Partially Paid   │ ← Partial payment
    │   └────────┬─────────┘
    │            │
    │            ↓
    ├─→ ┌────────────┐
    │   │    Paid    │ ← Full payment
    │   └────────────┘
    │
    ├─→ ┌──────────┐
    │   │ Overdue  │ ← Past due date
    │   └──────────┘
    │
    └─→ ┌───────────┐
        │ Cancelled │ ← Invoice cancelled
        └───────────┘
```

### 4.3 Invoice Status Fields

**File:** `app/models/business.py` (Lines 1106-1113)

```python
id = db.Column(db.Integer, primary_key=True)
invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'))
client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id', ondelete='SET NULL'))
invoice_date = db.Column(db.Date, nullable=False)
due_date = db.Column(db.Date)
status = db.Column(db.String(50), nullable=False, default=STATUS_DRAFT, index=True)
```

**Default Status:** `Draft`

---

## 5. Communication Status System

### 5.1 Available Status Values

**File:** `app/models/business.py` (Lines 1294-1301)

| Status Constant | Status Value | Description |
|----------------|--------------|-------------|
| `STATUS_PENDING` | `'Pending'` | Queued for sending |
| `STATUS_SENT` | `'Sent'` | Successfully sent |
| `STATUS_DELIVERED` | `'Delivered'` | Delivered to recipient |
| `STATUS_READ` | `'Read'` | Read by recipient |
| `STATUS_FAILED` | `'Failed'` | Failed to send |

**Total Valid Statuses:** 5

### 5.2 Communication Types

**File:** `app/models/business.py` (Lines 1281-1286)

| Type Constant | Type Value | Description |
|--------------|------------|-------------|
| `TYPE_EMAIL` | `'Email'` | Email communication |
| `TYPE_WHATSAPP` | `'WhatsApp'` | WhatsApp message |
| `TYPE_NOTIFICATION` | `'Notification'` | System notification |

### 5.3 Communication Direction

**File:** `app/models/business.py` (Lines 1288-1292)

| Direction Constant | Direction Value | Description |
|-------------------|----------------|-------------|
| `DIRECTION_INBOUND` | `'Inbound'` | Received message |
| `DIRECTION_OUTBOUND` | `'Outbound'` | Sent message |

### 5.4 Communication Workflow

```
┌──────────┐
│ Pending  │ ← Queued for sending
└────┬─────┘
     │
     ├─→ ┌────────┐
     │   │  Sent  │ ← Successfully sent
     │   └───┬────┘
     │       │
     │       ↓
     │   ┌────────────┐
     │   │ Delivered  │ ← Delivered to recipient
     │   └─────┬──────┘
     │         │
     │         ↓
     │   ┌────────┐
     │   │  Read  │ ← Read by recipient
     │   └────────┘
     │
     └─→ ┌─────────┐
         │ Failed  │ ← Failed to send
         └─────────┘
```

### 5.5 Communication Status Fields

**File:** `app/models/business.py` (Lines 1303-1316)

```python
id = db.Column(db.Integer, primary_key=True)
comm_type = db.Column(db.String(20), nullable=False, index=True)
direction = db.Column(db.String(10), nullable=False)
client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='SET NULL'), index=True)
project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'), index=True)
status = db.Column(db.String(50), default=STATUS_PENDING, index=True)
sent_at = db.Column(db.DateTime)
received_at = db.Column(db.DateTime)
read_at = db.Column(db.DateTime)
```

**Default Status:** `Pending`

---

## 6. Status-Triggered Automations

### 6.1 POP Received Automation

**Trigger:** User clicks "Toggle POP" button to mark POP as received

**File:** `app/routes/projects.py` - `toggle_pop()` (Lines 618-681)

**Actions Performed:**

1. ✅ Set `pop_received = True`
2. ✅ Set `pop_received_date = today`
3. ✅ Calculate `pop_deadline = today + 3 days`
4. ✅ Update `project.status = STATUS_APPROVED_POP`
5. ✅ Check for duplicate queue items
6. ✅ Calculate next queue position
7. ✅ Create QueueItem with defaults
8. ✅ Log activity (POP_RECEIVED)
9. ✅ Display flash messages

**Activity Logging:**

**File:** `app/services/activity_logger.py` (Lines 137-159)

```python
def log_pop_status_change(project_id, pop_received, pop_received_date=None, user='admin'):
    """Log a change to POP (Proof of Payment) status."""
    action = 'POP_RECEIVED' if pop_received else 'POP_CLEARED'
    details = {
        'pop_received': pop_received,
        'pop_received_date': pop_received_date.isoformat() if pop_received_date else None
    }
    return log_activity('PROJECT', project_id, action, details, user)
```

### 6.2 Auto-Queue on POP

**File:** `app/services/auto_scheduler.py` (Lines 128-147)

```python
# Get next queue position
max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
next_position = max_position + 1

# Determine scheduled date (today or next business day)
scheduled_date = get_next_business_day(date.today())

# Create queue item with sensible defaults
queue_item = QueueItem(
    project_id=project.id,
    queue_position=next_position,
    status=QueueItem.STATUS_QUEUED,
    priority=QueueItem.PRIORITY_NORMAL,
    scheduled_date=scheduled_date,
    estimated_cut_time=project.estimated_cut_time,
    notes='Automatically scheduled: POP received + inventory available',
    added_by=performed_by
)
```

### 6.3 Queue Status Change Automation

**File:** `app/routes/queue.py` (Lines 167-189)

```python
old_status = queue_item.status
queue_item.status = new_status

# Update timestamps
if new_status == QueueItem.STATUS_IN_PROGRESS and not queue_item.started_at:
    queue_item.started_at = datetime.utcnow()
elif new_status == QueueItem.STATUS_COMPLETED and not queue_item.completed_at:
    queue_item.completed_at = datetime.utcnow()

db.session.commit()

# Log activity
activity = ActivityLog(
    entity_type='QUEUE',
    entity_id=id,
    action='STATUS_CHANGED',
    details=f'Status changed from {old_status} to {new_status}',
    user='System'
)
db.session.add(activity)
db.session.commit()
```

### 6.4 Project Status Change Automation

**File:** `app/routes/projects.py` (Lines 486-494)

```python
old_status = project.status
project.status = new_status
project.updated_at = datetime.utcnow()

# Auto-set dates based on status
if new_status == Project.STATUS_APPROVED and not project.approval_date:
    project.approval_date = date.today()
elif new_status == Project.STATUS_COMPLETED and not project.completion_date:
    project.completion_date = date.today()
```

---

## 7. Database Schema

### 7.1 Project Status CHECK Constraint

**File:** `migrations/schema_v9_1_fix_project_status_constraint.sql` (Lines 72-83)

```sql
CHECK (status IN (
    'Request',                          -- New Phase 9 status
    'Quote & Approval',                 -- New Phase 9 status
    'Approved (POP Received)',          -- New Phase 9 status
    'Queued (Scheduled for Cutting)',   -- New Phase 9 status
    'In Progress',
    'Completed',
    'Cancelled',
    'Quote',                            -- Legacy status (backward compatibility)
    'Approved'                          -- Legacy status (backward compatibility)
))
```

**Schema Version:** 9.1  
**Migration Applied:** 2025-10-20

### 7.2 Queue Status Configuration

**File:** `migrations/schema_v5_queue.sql` (Lines 61-66)

```sql
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('queue_auto_position', 'true', 'Automatically assign queue positions'),
    ('default_priority', 'Normal', 'Default priority for new queue items'),
    ('queue_statuses', 'Queued,In Progress,Completed,Cancelled', 'Available queue statuses'),
    ('priority_levels', 'Low,Normal,High,Urgent', 'Available priority levels');
```

### 7.3 Status Column Definitions

**Projects Table:**
```sql
status VARCHAR(50) NOT NULL DEFAULT 'Quote'
```

**Queue Items Table:**
```sql
status VARCHAR(50) NOT NULL DEFAULT 'Queued'
priority VARCHAR(20) DEFAULT 'Normal'
```

**Quotes Table:**
```sql
status VARCHAR(50) NOT NULL DEFAULT 'Draft'
```

**Invoices Table:**
```sql
status VARCHAR(50) NOT NULL DEFAULT 'Draft'
```

**Communications Table:**
```sql
status VARCHAR(50) DEFAULT 'Pending'
```

### 7.4 Status Indexes

**File:** `migrations/schema_v11_indexes.sql`

```sql
-- Project status index
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Queue status and position composite index
CREATE INDEX IF NOT EXISTS idx_queue_items_status_position 
ON queue_items(status, queue_position);

-- Quote status index
CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status);

-- Invoice status index
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

-- Communication status index
CREATE INDEX IF NOT EXISTS idx_communications_status ON communications(status);
```

---

## 8. Visual Indicators & UI

### 8.1 Status Badge Colors

**File:** `app/static/css/main.css` (Lines 817-895)

#### **Project Status Badges**

| Status | CSS Class | Background Color | Text Color | Visual |
|--------|-----------|-----------------|------------|--------|
| Request | `.badge-request` | `#fef3c7` (Light Yellow) | `#92400e` (Dark Brown) | 🟡 |
| Quote & Approval | `.badge-quote-&-approval` | `#fef3c7` (Light Yellow) | `#92400e` (Dark Brown) | 🟡 |
| Quote (Legacy) | `.badge-quote` | `#fef3c7` (Light Yellow) | `#92400e` (Dark Brown) | 🟡 |
| Approved (POP Received) | `.badge-approved-(pop-received)` | `#dbeafe` (Light Blue) | `#1e40af` (Dark Blue) | 🔵 |
| Approved (Legacy) | `.badge-approved` | `#dbeafe` (Light Blue) | `#1e40af` (Dark Blue) | 🔵 |
| Queued | `.badge-queued-(scheduled-for-cutting)` | `#dbeafe` (Light Blue) | `#1e40af` (Dark Blue) | 🔵 |
| In Progress | `.badge-in-progress` | `#ddd6fe` (Light Purple) | `#5b21b6` (Dark Purple) | 🟣 |
| Completed | `.badge-completed` | `#d1fae5` (Light Green) | `#065f46` (Dark Green) | 🟢 |
| Cancelled | `.badge-cancelled` | `#fee2e2` (Light Red) | `#991b1b` (Dark Red) | 🔴 |

**CSS Implementation:**

```css
/* Project Status Badges */
.badge-quote {
    background-color: #fef3c7;
    color: #92400e;
}

.badge-approved {
    background-color: #dbeafe;
    color: #1e40af;
}

.badge-in-progress {
    background-color: #ddd6fe;
    color: #5b21b6;
}

.badge-completed {
    background-color: #d1fae5;
    color: #065f46;
}

.badge-cancelled {
    background-color: #fee2e2;
    color: #991b1b;
}
```

#### **Queue Status Badges**

| Status | CSS Class | Background Color | Text Color | Visual |
|--------|-----------|-----------------|------------|--------|
| Queued | `.badge-info` | `#dbeafe` (Light Blue) | `#1e40af` (Dark Blue) | 🔵 |
| In Progress | `.badge-primary` | `#dbeafe` (Light Blue) | `#1e40af` (Dark Blue) | 🔵 |
| Completed | `.badge-success` | `#d1fae5` (Light Green) | `#065f46` (Dark Green) | 🟢 |
| Cancelled | `.badge-secondary` | `#e5e7eb` (Light Gray) | `#374151` (Dark Gray) | ⚪ |

#### **Queue Priority Badges**

| Priority | CSS Class | Background Color | Text Color | Visual |
|----------|-----------|-----------------|------------|--------|
| Urgent | `.badge-danger` | `#fee2e2` (Light Red) | `#991b1b` (Dark Red) | 🔴 |
| High | `.badge-warning` | `#fef3c7` (Light Yellow) | `#92400e` (Dark Brown) | 🟡 |
| Normal | `.badge-secondary` | `#e5e7eb` (Light Gray) | `#374151` (Dark Gray) | ⚪ |
| Low | `.badge-secondary` | `#e5e7eb` (Light Gray) | `#374151` (Dark Gray) | ⚪ |

#### **Communication Status Badges**

**File:** `app/static/css/main.css` (Lines 935-958)

| Status | CSS Class | Background Color | Text Color | Visual |
|--------|-----------|-----------------|------------|--------|
| Pending | `.badge-pending` | `#ffc107` (Yellow) | `#000` (Black) | 🟡 |
| Sent | `.badge-sent` | `#2196f3` (Blue) | `white` | 🔵 |
| Delivered | `.badge-delivered` | `#4caf50` (Green) | `white` | 🟢 |
| Read | `.badge-read` | `#8bc34a` (Light Green) | `white` | 🟢 |
| Failed | `.badge-failed` | `#f44336` (Red) | `white` | 🔴 |

**CSS Implementation:**

```css
/* Communication Status Badges */
.badge-pending {
    background-color: #ffc107;
    color: #000;
}

.badge-sent {
    background-color: #2196f3;
    color: white;
}

.badge-delivered {
    background-color: #4caf50;
    color: white;
}

.badge-read {
    background-color: #8bc34a;
    color: white;
}

.badge-failed {
    background-color: #f44336;
    color: white;
}
```

#### **Communication Type Badges**

**File:** `app/static/css/main.css` (Lines 901-929)

| Type | CSS Class | Background Color | Text Color | Visual |
|------|-----------|-----------------|------------|--------|
| Email | `.badge-email` | `#4285f4` (Google Blue) | `white` | 📧 |
| WhatsApp | `.badge-whatsapp` | `#25d366` (WhatsApp Green) | `white` | 💬 |
| Notification | `.badge-notification` | `#ff9800` (Orange) | `white` | 🔔 |

### 8.2 Badge Size Variants

**File:** `app/static/css/main.css` (Lines 964-972)

```css
.badge-lg {
    font-size: 1rem;
    padding: 0.5rem 1rem;
}

.badge-md {
    font-size: var(--font-size-sm);
    padding: var(--spacing-xs) var(--spacing-md);
}

.badge-sm {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}
```

### 8.3 UI Implementation Examples

#### **Project Detail Page Status Badge**

**File:** `app/templates/projects/detail.html` (Lines 94-98)

```html
<!-- Status Badge and Alerts -->
<div class="status-badges">
    <span class="badge badge-lg badge-{{ project.status|lower|replace(' ', '-') }}">
        {{ project.status }}
    </span>
    {% if project.is_overdue %}
        <span class="badge badge-lg badge-danger">
            ⚠️ OVERDUE
        </span>
    {% endif %}
</div>
```

**Dynamic Badge Class Generation:**
- Status: `"In Progress"` → Class: `.badge-in-progress`
- Status: `"Quote & Approval"` → Class: `.badge-quote-&-approval`

#### **Queue Item Status Badge**

**File:** `app/templates/queue/index.html` (Lines 122-124)

```html
<span class="badge badge-{{ 'info' if item.status == 'Queued' else 'primary' if item.status == 'In Progress' else 'success' if item.status == 'Completed' else 'secondary' }}">
    {{ item.status }}
</span>
```

#### **Queue Priority Badge**

**File:** `app/templates/queue/index.html` (Lines 117-119)

```html
<span class="badge badge-{{ 'danger' if item.priority == 'Urgent' else 'warning' if item.priority == 'High' else 'secondary' }}">
    {{ item.priority }}
</span>
```

#### **POP Received Indicator**

**File:** `app/templates/queue/index.html` (Lines 109-114)

```html
{% if item.project.pop_received %}
    <br>
    <span class="badge badge-success badge-sm">
        ✅ POP Received - Auto-scheduled
    </span>
{% endif %}
```

### 8.4 Status Dropdown in Forms

**File:** `app/templates/projects/form.html` (Lines 85-101)

```html
<div class="form-group">
    <label for="status" class="form-label required">Status</label>
    <select
        id="status"
        name="status"
        class="form-control"
        required
    >
        {% for status in statuses %}
            <option value="{{ status }}" {% if project and project.status == status %}selected{% endif %}>
                {{ status }}
            </option>
        {% endfor %}
    </select>
    <small class="form-help">Current project status</small>
</div>
```

**Statuses Passed from Route:**

**File:** `app/routes/projects.py` (Lines 81, 126)

```python
# In create() and edit() routes
statuses = Project.VALID_STATUSES
```

### 8.5 Status Filtering UI

**File:** `app/templates/queue/index.html` (Lines 60-75)

```html
<div class="filter-bar">
    <a href="{{ url_for('queue.index', status='active') }}"
       class="filter-btn {% if status_filter == 'active' %}active{% endif %}">
        Active ({{ stats.total_active }})
    </a>
    <a href="{{ url_for('queue.index', status='Queued') }}"
       class="filter-btn {% if status_filter == 'Queued' %}active{% endif %}">
        Queued ({{ stats.total_queued }})
    </a>
    <a href="{{ url_for('queue.index', status='In Progress') }}"
       class="filter-btn {% if status_filter == 'In Progress' %}active{% endif %}">
        In Progress ({{ stats.total_in_progress }})
    </a>
    <a href="{{ url_for('queue.index', status='all') }}"
       class="filter-btn {% if status_filter == 'all' %}active{% endif %}">
        All
    </a>
</div>
```

---

## 9. Code Examples

### 9.1 Checking Project Status

```python
from app.models import Project

# Get project
project = Project.query.get(1)

# Check specific status
if project.status == Project.STATUS_COMPLETED:
    print("Project is completed!")

# Check if in active statuses
active_statuses = [
    Project.STATUS_IN_PROGRESS,
    Project.STATUS_QUEUED
]
if project.status in active_statuses:
    print("Project is active")

# Check if overdue
if project.is_overdue:
    print(f"Project is {project.days_until_due * -1} days overdue!")
```

### 9.2 Updating Project Status

```python
from app.models import Project
from app import db
from datetime import date, datetime

# Get project
project = Project.query.get(1)

# Update status
old_status = project.status
project.status = Project.STATUS_COMPLETED
project.updated_at = datetime.utcnow()

# Auto-set completion date
if not project.completion_date:
    project.completion_date = date.today()

# Commit changes
db.session.commit()

# Log activity
from app.services.activity_logger import log_activity
log_activity(
    'PROJECT',
    project.id,
    'STATUS_CHANGED',
    {
        'old_status': old_status,
        'new_status': project.status
    },
    user='admin'
)
```

### 9.3 Filtering Projects by Status

```python
from app.models import Project

# Get all completed projects
completed_projects = Project.query.filter_by(
    status=Project.STATUS_COMPLETED
).all()

# Get all active projects (not completed or cancelled)
active_projects = Project.query.filter(
    Project.status.in_([
        Project.STATUS_REQUEST,
        Project.STATUS_QUOTE_APPROVAL,
        Project.STATUS_APPROVED_POP,
        Project.STATUS_QUEUED,
        Project.STATUS_IN_PROGRESS
    ])
).all()

# Get projects by multiple statuses
pending_projects = Project.query.filter(
    Project.status.in_([
        Project.STATUS_REQUEST,
        Project.STATUS_QUOTE_APPROVAL
    ])
).order_by(Project.created_at.desc()).all()
```

### 9.4 Creating Queue Item with Status

```python
from app.models import QueueItem, Project
from app import db
from datetime import date

# Get project
project = Project.query.get(1)

# Get next queue position
max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
next_position = max_position + 1

# Create queue item
queue_item = QueueItem(
    project_id=project.id,
    queue_position=next_position,
    status=QueueItem.STATUS_QUEUED,
    priority=QueueItem.PRIORITY_NORMAL,
    scheduled_date=date.today(),
    estimated_cut_time=project.estimated_cut_time,
    notes='Added to queue',
    added_by='admin'
)

db.session.add(queue_item)
db.session.commit()
```

### 9.5 Updating Queue Status with Timestamps

```python
from app.models import QueueItem
from app import db
from datetime import datetime

# Get queue item
queue_item = QueueItem.query.get(1)

# Update to In Progress
old_status = queue_item.status
queue_item.status = QueueItem.STATUS_IN_PROGRESS

# Auto-set started_at timestamp
if not queue_item.started_at:
    queue_item.started_at = datetime.utcnow()

db.session.commit()

# Log activity
from app.models import ActivityLog
activity = ActivityLog(
    entity_type='QUEUE',
    entity_id=queue_item.id,
    action='STATUS_CHANGED',
    details=f'Status changed from {old_status} to {queue_item.status}',
    user='admin'
)
db.session.add(activity)
db.session.commit()
```

### 9.6 Validating Status Values

```python
from app.models import Project

# Validate status before setting
new_status = 'In Progress'

if new_status not in Project.VALID_STATUSES:
    raise ValueError(f'Invalid status: {new_status}')

project.status = new_status
db.session.commit()
```

### 9.7 Getting Status Statistics

```python
from app.models import Project, QueueItem
from app import db

# Project status counts
status_counts = db.session.query(
    Project.status,
    db.func.count(Project.id)
).group_by(Project.status).all()

for status, count in status_counts:
    print(f"{status}: {count} projects")

# Queue status counts
queue_stats = {
    'total_queued': QueueItem.query.filter_by(status=QueueItem.STATUS_QUEUED).count(),
    'total_in_progress': QueueItem.query.filter_by(status=QueueItem.STATUS_IN_PROGRESS).count(),
    'total_completed': QueueItem.query.filter_by(status=QueueItem.STATUS_COMPLETED).count()
}

print(f"Queue Statistics: {queue_stats}")
```

### 9.8 Status-Based Conditional Logic

```python
from app.models import Project

project = Project.query.get(1)

# Different actions based on status
if project.status == Project.STATUS_REQUEST:
    # Send quote to client
    print("Generate and send quote")

elif project.status == Project.STATUS_QUOTE_APPROVAL:
    # Wait for client approval
    print("Awaiting client approval")

elif project.status == Project.STATUS_APPROVED_POP:
    # Add to queue
    print("Add to production queue")

elif project.status == Project.STATUS_QUEUED:
    # Schedule for cutting
    print("Schedule laser cutting")

elif project.status == Project.STATUS_IN_PROGRESS:
    # Track progress
    print("Monitor cutting progress")

elif project.status == Project.STATUS_COMPLETED:
    # Notify client for collection
    print("Notify client - ready for collection")

elif project.status == Project.STATUS_CANCELLED:
    # Archive project
    print("Archive cancelled project")
```

### 9.9 Auto-Queue on POP Received

```python
from app.models import Project, QueueItem
from app import db
from datetime import date

def mark_pop_received(project_id, pop_date):
    """Mark POP as received and auto-queue project."""
    project = Project.query.get(project_id)

    # Update POP status
    project.pop_received = True
    project.pop_received_date = pop_date
    project.pop_deadline = pop_date + timedelta(days=3)
    project.status = Project.STATUS_APPROVED_POP

    # Check if already in queue
    existing_queue_item = QueueItem.query.filter_by(
        project_id=project.id
    ).filter(
        QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
    ).first()

    if existing_queue_item:
        return False, "Project already in queue"

    # Get next queue position
    max_position = db.session.query(db.func.max(QueueItem.queue_position)).scalar() or 0
    next_position = max_position + 1

    # Create queue item
    queue_item = QueueItem(
        project_id=project.id,
        queue_position=next_position,
        status=QueueItem.STATUS_QUEUED,
        priority=QueueItem.PRIORITY_NORMAL,
        scheduled_date=date.today(),
        estimated_cut_time=project.estimated_cut_time,
        notes='Automatically added to queue when POP was received',
        added_by='System (Auto)'
    )

    db.session.add(queue_item)
    db.session.commit()

    return True, "Project added to queue successfully"
```

### 9.10 Communication Status Workflow

```python
from app.models import Communication
from app import db
from datetime import datetime

# Create communication
comm = Communication(
    comm_type=Communication.TYPE_EMAIL,
    direction=Communication.DIRECTION_OUTBOUND,
    client_id=1,
    project_id=1,
    subject='Quote Ready',
    body='Your quote is ready for review',
    from_address='sales@laseros.com',
    to_address='client@example.com',
    status=Communication.STATUS_PENDING
)

db.session.add(comm)
db.session.commit()

# Update to Sent
comm.status = Communication.STATUS_SENT
comm.sent_at = datetime.utcnow()
db.session.commit()

# Update to Delivered
comm.status = Communication.STATUS_DELIVERED
db.session.commit()

# Update to Read
comm.status = Communication.STATUS_READ
comm.read_at = datetime.utcnow()
db.session.commit()
```

---

## 10. Summary

### Status System Overview

| Entity | Total Statuses | Default Status | Indexed | CHECK Constraint |
|--------|---------------|----------------|---------|------------------|
| **Project** | 9 (7 + 2 legacy) | `Quote` | ✅ Yes | ✅ Yes |
| **Queue** | 4 | `Queued` | ✅ Yes | ❌ No |
| **Quote** | 5 | `Draft` | ✅ Yes | ❌ No |
| **Invoice** | 6 | `Draft` | ✅ Yes | ❌ No |
| **Communication** | 5 | `Pending` | ✅ Yes | ❌ No |

### Key Features

✅ **Comprehensive Status Tracking** - All major entities have status fields
✅ **Automatic Status Updates** - Timestamps auto-set on status changes
✅ **Status-Triggered Automations** - POP received → Auto-queue
✅ **Activity Logging** - All status changes logged
✅ **Visual Indicators** - Color-coded badges for all statuses
✅ **Validation** - CHECK constraints and VALID_STATUSES lists
✅ **Backward Compatibility** - Legacy statuses supported
✅ **Indexed for Performance** - All status columns indexed

### Best Practices

1. **Always use constants** - Use `Project.STATUS_COMPLETED` instead of `'Completed'`
2. **Validate before setting** - Check against `VALID_STATUSES` list
3. **Log status changes** - Use activity logger for audit trail
4. **Update timestamps** - Set relevant date fields on status changes
5. **Use transactions** - Wrap status updates in database transactions
6. **Check for side effects** - Some status changes trigger automations

---

## 11. Related Documentation

- **Project Status Constraint Fix:** `docs/fixes/PROJECT_STATUS_CONSTRAINT_FIX_APPLIED.md`
- **Auto-Queue Feature:** `docs/features/AUTO_QUEUE_ADDITION_DOCUMENTATION.md`
- **Activity Logging:** `docs/DETAILED_FEATURE_CAPABILITIES.md` (Section 8)
- **Database Schema:** `migrations/schema_v9_1_fix_project_status_constraint.sql`
- **CSS Styling:** `app/static/css/main.css` (Lines 817-1000)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-23
**Maintained By:** Laser OS Development Team

