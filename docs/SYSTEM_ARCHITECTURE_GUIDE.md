# 🏗️ **LASER OS: COMPREHENSIVE SYSTEM ARCHITECTURE & MODULE INTERCONNECTION GUIDE**

**Version:** 1.0  
**Date:** 2025-10-27  
**Application:** Laser Cutting Operations System (Laser OS)  
**Framework:** Flask (Python) + SQLAlchemy ORM + SQLite

---

## **📋 TABLE OF CONTENTS**

1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Database Architecture & Entity Relationships](#2-database-architecture--entity-relationships)
3. [Module Deep Dive (All 12 Modules)](#3-module-deep-dive)
4. [Complete Business Workflow Lifecycle](#4-complete-business-workflow-lifecycle)
5. [Automation & Triggers](#5-automation--triggers)
6. [Session Management & Context](#6-session-management--context)
7. [Integration Points & Data Flow](#7-integration-points--data-flow)

---

## **1. SYSTEM OVERVIEW & ARCHITECTURE**

### **1.1 Application Structure**

```
laser_os/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/
│   │   ├── auth.py              # User, Role, LoginHistory
│   │   ├── business.py          # All business models
│   │   └── sage.py              # Sage integration models
│   ├── routes/                  # 12 Blueprint modules
│   │   ├── main.py              # Dashboard
│   │   ├── clients.py           # Client management
│   │   ├── projects.py          # Project management
│   │   ├── products.py          # Product catalog
│   │   ├── queue.py             # Production queue
│   │   ├── presets.py           # Machine settings
│   │   ├── operators.py         # Operator management
│   │   ├── inventory.py         # Inventory tracking
│   │   ├── reports.py           # Analytics & BI
│   │   ├── sage.py              # Accounting integration
│   │   ├── comms.py             # Communications
│   │   └── admin.py             # System administration
│   ├── services/                # Business logic services
│   │   ├── status_automation.py # Auto-queue on POP
│   │   ├── communication_service.py
│   │   └── scheduler.py         # Background jobs
│   └── templates/               # Jinja2 templates
├── migrations/                  # SQL schema migrations
├── data/                        # SQLite database & uploads
└── run.py                       # Application entry point
```

### **1.2 Technology Stack**

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 2.x (Python 3.11+) |
| **ORM** | SQLAlchemy 2.x |
| **Database** | SQLite 3 |
| **Authentication** | Flask-Login + RBAC |
| **Templates** | Jinja2 |
| **Email** | Flask-Mail (SMTP) |
| **Scheduling** | APScheduler |
| **Frontend** | Vanilla JavaScript + CSS3 |

### **1.3 Blueprint Registration**

**File:** `app/__init__.py` (Lines 69-87)

The application registers 17 blueprints for modular routing:

```python
from app.routes import auth, admin, main, clients, projects, products, files, queue, inventory, reports, quotes, invoices, comms, presets, templates, operators, webhooks, sage

app.register_blueprint(auth.bp)        # Authentication routes
app.register_blueprint(admin.bp)       # Admin routes
app.register_blueprint(main.bp)        # Dashboard
app.register_blueprint(clients.bp)     # Client management
app.register_blueprint(projects.bp)    # Project management
app.register_blueprint(products.bp)    # Product catalog
app.register_blueprint(files.bp)       # File management
app.register_blueprint(queue.bp)       # Production queue
app.register_blueprint(inventory.bp)   # Inventory tracking
app.register_blueprint(reports.bp)     # Analytics & BI
app.register_blueprint(quotes.bp)      # Quote generation
app.register_blueprint(invoices.bp)    # Invoice management
app.register_blueprint(comms.bp)       # Communications module
app.register_blueprint(presets.bp)     # Machine settings presets
app.register_blueprint(operators.bp)   # Operator management
app.register_blueprint(templates.bp, url_prefix='/comms/templates')
app.register_blueprint(webhooks.bp)    # Webhook receiver
app.register_blueprint(sage.bp)        # Sage Business Cloud Accounting integration
```

---

## **2. DATABASE ARCHITECTURE & ENTITY RELATIONSHIPS**

### **2.1 Core Entity Relationship Diagram**

```
┌─────────────┐
│    User     │──────┐
│  (auth.py)  │      │
└─────────────┘      │
                     │ user_id (FK)
                     ↓
┌─────────────┐  ┌──────────────┐
│   Client    │  │   Operator   │
│ (business)  │  │  (business)  │
└──────┬──────┘  └──────┬───────┘
       │                │
       │ client_id (FK) │ operator_id (FK)
       ↓                ↓
┌─────────────┐  ┌──────────────┐
│   Project   │──│   LaserRun   │
│ (business)  │  │  (business)  │
└──────┬──────┘  └──────────────┘
       │
       │ project_id (FK)
       ├────────────────┬────────────────┬──────────────┬──────────────┐
       ↓                ↓                ↓              ↓              ↓
┌─────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│  QueueItem  │  │ DesignFile   │  │  Quote   │  │ Invoice  │  │Communication │
│ (business)  │  │  (business)  │  │(business)│  │(business)│  │  (business)  │
└─────────────┘  └──────────────┘  └──────────┘  └──────────┘  └──────────────┘
```

### **2.2 Complete Model Inventory**

| Model | Table | Primary Purpose | Key Relationships |
|-------|-------|-----------------|-------------------|
| **User** | `users` | Authentication & authorization | → Operator (1:1), → LoginHistory (1:N) |
| **Client** | `clients` | Customer management | → Project (1:N), → Communication (1:N) |
| **Project** | `projects` | Job/order tracking | → Client (N:1), → QueueItem (1:N), → LaserRun (1:N), → Quote (1:N), → Invoice (1:N), → DesignFile (1:N), → Communication (1:N) |
| **Product** | `products` | SKU catalog | → ProjectProduct (N:N via junction), → ProductFile (1:N) |
| **QueueItem** | `queue_items` | Production scheduling | → Project (N:1), → LaserRun (1:N) |
| **LaserRun** | `laser_runs` | Production logging | → Project (N:1), → QueueItem (N:1), → Operator (N:1), → MachineSettingsPreset (N:1) |
| **Operator** | `operators` | Machine operator profiles | → User (N:1), → LaserRun (1:N) |
| **MachineSettingsPreset** | `machine_settings_presets` | Cutting parameters | → LaserRun (1:N) |
| **InventoryItem** | `inventory_items` | Material stock tracking | → InventoryTransaction (1:N) |
| **Quote** | `quotes` | Customer quotations | → Project (N:1), → QuoteItem (1:N) |
| **Invoice** | `invoices` | Billing documents | → Project (N:1), → InvoiceItem (1:N) |
| **Communication** | `communications` | Email/message log | → Client (N:1), → Project (N:1) |
| **ActivityLog** | `activity_logs` | System audit trail | All entities (polymorphic) |

### **2.3 Key Foreign Key Relationships**

```sql
-- Client → Project (One-to-Many)
projects.client_id → clients.id (CASCADE DELETE)

-- Project → QueueItem (One-to-Many)
queue_items.project_id → projects.id (CASCADE DELETE)

-- Project → LaserRun (One-to-Many)
laser_runs.project_id → projects.id (CASCADE DELETE)

-- QueueItem → LaserRun (One-to-Many)
laser_runs.queue_item_id → queue_items.id (SET NULL)

-- Operator → LaserRun (One-to-Many)
laser_runs.operator_id → operators.id (SET NULL)

-- User → Operator (One-to-One)
operators.user_id → users.id (SET NULL)

-- MachineSettingsPreset → LaserRun (One-to-Many)
laser_runs.preset_id → machine_settings_presets.id (SET NULL)

-- Project → Product (Many-to-Many via ProjectProduct)
project_products.project_id → projects.id (CASCADE DELETE)
project_products.product_id → products.id (CASCADE DELETE)
```

---

## **3. MODULE DEEP DIVE**

### **MODULE 1: DASHBOARD** 📊

#### **Purpose & Functionality**
Central command center displaying real-time system statistics and recent activity across all modules.

#### **File Location**
- **Route:** `app/routes/main.py`
- **Template:** `app/templates/dashboard.html`
- **Blueprint:** `main` (URL prefix: `/`)

#### **Database Models Used**
- **Client** - Total count
- **Project** - Total count, active count
- **Product** - Total count
- **DesignFile** - Total count
- **QueueItem** - Active queue length
- **InventoryItem** - Total count, low stock count

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/` | GET | `dashboard()` | Main dashboard view |

#### **Data Aggregation Logic**

**File:** `app/routes/main.py` (Lines 24-84)

```python
# Get basic statistics
total_clients = Client.query.count()
total_projects = Project.query.count()
active_projects = Project.query.filter(
    Project.status.in_([Project.STATUS_APPROVED, Project.STATUS_IN_PROGRESS])
).count()
total_products = Product.query.count()
total_files = DesignFile.query.count()
queue_length = QueueItem.query.filter(
    QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
).count()

# Get recent clients (last 5)
recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()

# Get recent projects (last 5)
recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()

# Get active queue items (next 5)
queue_items = QueueItem.query.options(
    joinedload(QueueItem.project)
).filter(
    QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS])
).order_by(QueueItem.queue_position).limit(5).all()

# Get inventory statistics
inventory_count = InventoryItem.query.count()
low_stock_count = InventoryItem.query.filter(
    InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
).count()
```

#### **User Workflow**
1. User logs in → Redirected to dashboard
2. Dashboard displays:
   - **Statistics Cards:** Total clients, projects, products, files, queue length, inventory
   - **Recent Activity:** Last 5 clients, projects, products, files
   - **Active Queue:** Next 5 queue items
   - **Inventory Alerts:** Low stock warnings

#### **Data Dependencies**

**Receives From:**
- **Clients Module:** Client count, recent clients
- **Projects Module:** Project count, active projects, recent projects
- **Products Module:** Product count, recent products
- **Queue Module:** Active queue items
- **Inventory Module:** Stock levels, low stock alerts
- **Files Module:** Recent file uploads

**Provides To:**
- **All Modules:** Quick navigation links
- **Users:** System health overview

---

### **MODULE 2: CLIENTS** 👥

#### **Purpose & Functionality**
Customer relationship management - create, view, edit, and delete client records.

#### **File Location**
- **Route:** `app/routes/clients.py`
- **Model:** `app/models/business.py` → `Client`
- **Templates:** `app/templates/clients/`
- **Blueprint:** `clients` (URL prefix: `/clients`)

#### **Database Model: Client**

**File:** `app/models/business.py` (Lines 13-63)

```python
class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(10), unique=True, nullable=False, index=True)  # CL-0001
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True, cascade='all, delete-orphan')
    communications = db.relationship('Communication', backref='client', lazy=True)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/clients` | GET | `list_clients()` | List all clients with search/filter |
| `/clients/new` | GET/POST | `create_client()` | Create new client |
| `/clients/<id>` | GET | `view_client(id)` | View client details + projects |
| `/clients/<id>/edit` | GET/POST | `edit_client(id)` | Edit client information |
| `/clients/<id>/delete` | POST | `delete_client(id)` | Delete client (cascades to projects) |

#### **Relationships**

**Foreign Keys:**
- None (root entity)

**Backrefs:**
- `projects` → One client has many projects
- `communications` → One client has many communications

#### **User Workflow**
1. **Create Client:**
   - Navigate to Clients → New Client
   - Enter: Name, Contact Person, Email, Phone, Address
   - System auto-generates `client_code` (CL-0001, CL-0002, etc.)
   - Save → Client created

2. **View Client:**
   - Click client from list
   - See: Client details + All associated projects
   - Quick actions: Edit, Delete, Create Project

#### **Data Dependencies**

**Receives From:**
- None (root entity)

**Provides To:**
- **Projects Module:** Client information for project creation
- **Communications Module:** Client contact details for emails
- **Reports Module:** Client profitability analysis
- **Dashboard:** Client count, recent clients

#### **Automation & Triggers**
- **Auto-generate client_code:** SQLAlchemy event listener creates sequential code on insert
- **Cascade delete:** Deleting client deletes all associated projects (with confirmation)

---

### **MODULE 3: PROJECTS** 📁

#### **Purpose & Functionality**
Core business entity - tracks customer orders from quote to completion, including material specs, pricing, timelines, and POP (Proof of Payment) tracking.

#### **File Location**
- **Route:** `app/routes/projects.py`
- **Model:** `app/models/business.py` → `Project`
- **Templates:** `app/templates/projects/`
- **Blueprint:** `projects` (URL prefix: `/projects`)

#### **Database Model: Project**

**File:** `app/models/business.py` (Lines 66-187)

```python
class Project(db.Model):
    __tablename__ = 'projects'

    # Status constants - V12.0: Status System Redesign
    STATUS_REQUEST = 'Request'
    STATUS_QUOTE_APPROVAL = 'Quote & Approval'
    STATUS_APPROVED_POP = 'Approved (POP Received)'
    STATUS_QUEUED = 'Queued (Scheduled for Cutting)'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    VALID_STATUSES = [
        STATUS_REQUEST,
        STATUS_QUOTE_APPROVAL,
        STATUS_APPROVED_POP,
        STATUS_QUEUED,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED
    ]

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(30), unique=True, nullable=False, index=True)  # JB-2025-10-CL0001-001
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default=STATUS_QUOTE, index=True)

    # Timeline
    quote_date = db.Column(db.Date)
    approval_date = db.Column(db.Date)
    due_date = db.Column(db.Date, index=True)
    completion_date = db.Column(db.Date)

    # Pricing
    quoted_price = db.Column(db.Numeric(10, 2))
    final_price = db.Column(db.Numeric(10, 2))

    # Material & Production (Phase 9 enhancements)
    material_type = db.Column(db.String(100))
    material_thickness = db.Column(db.Numeric(10, 2))
    material_quantity_sheets = db.Column(db.Integer)
    parts_quantity = db.Column(db.Integer)
    estimated_cut_time = db.Column(db.Integer)  # minutes
    drawing_creation_time = db.Column(db.Integer)  # minutes
    number_of_bins = db.Column(db.Integer)
    scheduled_cut_date = db.Column(db.Date)

    # POP Tracking
    pop_received = db.Column(db.Boolean, default=False)
    pop_received_date = db.Column(db.Date)
    pop_deadline = db.Column(db.Date, index=True)

    # Client notification tracking
    client_notified = db.Column(db.Boolean, default=False)
    client_notified_date = db.Column(db.DateTime)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project_products = db.relationship('ProjectProduct', backref='project', lazy=True, cascade='all, delete-orphan')
    design_files = db.relationship('DesignFile', backref='project', lazy=True, cascade='all, delete-orphan')
    queue_items = db.relationship('QueueItem', backref='project', lazy=True, cascade='all, delete-orphan')
    laser_runs = db.relationship('LaserRun', backref='project', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('ProjectDocument', backref='project', lazy=True, cascade='all, delete-orphan')
    communications = db.relationship('Communication', backref='project', lazy=True)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/projects` | GET | `index()` | List all projects with filters (status, client, search, on-hold, expiring) |
| `/projects/new` | GET/POST | `create()` | Create new project |
| `/projects/<id>` | GET | `view(id)` | View project details + files + queue + runs |
| `/projects/<id>/edit` | GET/POST | `edit(id)` | Edit project information |
| `/projects/<id>/status` | POST | `update_status(id)` | Update project status |
| `/projects/<id>/pop` | POST | `mark_pop_received(id)` | Mark POP as received → **TRIGGERS AUTO-QUEUE** |
| `/projects/<id>/delete` | POST | `delete(id)` | Delete project |

#### **Relationships**

**Foreign Keys:**
- `client_id` → `clients.id` (Many projects to one client)

**Backrefs:**
- `queue_items` → One project has many queue items
- `laser_runs` → One project has many laser runs
- `design_files` → One project has many DXF files
- `communications` → One project has many communications
- `quotes` → One project has many quotes
- `invoices` → One project has many invoices
- `project_products` → Many-to-many with products via junction table

#### **User Workflow - Complete Project Lifecycle**

**1. Request Stage:**
- Client calls/emails with inquiry
- Create project with status = "Request"
- Enter: Client, Name, Description

**2. Quote & Approval Stage:**
- Upload DXF files
- Enter material specs (type, thickness, quantity)
- Enter estimated cut time
- Generate quote
- Send quote to client
- Update status = "Quote & Approval"

**3. POP Received Stage:**
- Client approves and pays
- Click "Mark POP Received"
- **AUTOMATION TRIGGER:** System automatically:
  - Sets `pop_received = True`
  - Sets `pop_received_date = today`
  - Calculates `pop_deadline = today + 10 days`
  - Updates status = "Approved (POP Received)"
  - **Creates QueueItem** with sensible defaults
  - Sends confirmation email to client

**4. Queued Stage:**
- Project appears in Queue module
- Scheduler assigns queue position
- Status = "Queued (Scheduled for Cutting)"

**5. In Progress Stage:**
- Operator starts cutting
- Queue status updated → **Project status auto-syncs**
- Status = "In Progress"

**6. Completed Stage:**
- Operator logs laser run
- Queue status = "Completed" → **Project status auto-syncs**
- System sets `completion_date = today`
- Status = "Completed"

#### **Data Dependencies**

**Receives From:**
- **Clients Module:** Client information (client_id, name, contact)
- **Products Module:** Product SKUs for project items
- **Presets Module:** Material types for dropdown

**Provides To:**
- **Queue Module:** Project details for queue items
- **LaserRun Module:** Project context for production logging
- **Reports Module:** Project data for analytics
- **Communications Module:** Project details for notifications
- **Quotes Module:** Project data for quote generation
- **Invoices Module:** Project data for billing
- **Dashboard:** Project count, active projects

#### **Automation & Triggers**

**1. Auto-generate project_code:**
- Format: `JB-YYYY-MM-CLxxxx-###`
- Example: `JB-2025-10-CL0001-001`
- SQLAlchemy event listener on insert

**2. Auto-queue on POP received:**
- File: `app/services/status_automation.py`
- Trigger: When `pop_received` set to `True`
- Action: Creates `QueueItem` with:
  - `status = 'Queued'`
  - `priority = 'Normal'`
  - `scheduled_date = today or next business day`
  - `estimated_cut_time = project.estimated_cut_time`
  - `queue_position = max + 1`

**3. Queue-Project status sync:**
- File: `app/routes/queue.py` → `update_status()`
- Trigger: When QueueItem status changes
- Action: Updates Project status to match:
  - Queue "In Progress" → Project "In Progress"
  - Queue "Completed" → Project "Completed" + sets `completion_date`
  - Queue "Cancelled" → Project "Cancelled"

---

### **MODULE 4: PRODUCTS** 📦

#### **Purpose & Functionality**
Product catalog management - maintain SKU library of laser-cut products with DXF files, pricing, and material specifications.

#### **File Location**
- **Route:** `app/routes/products.py`
- **Model:** `app/models/business.py` → `Product`, `ProductFile`
- **Templates:** `app/templates/products/`
- **Blueprint:** `products` (URL prefix: `/products`)

#### **Database Models**

**Product:**
```python
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku_code = db.Column(db.String(30), unique=True, nullable=False, index=True)  # SKU-0001
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material = db.Column(db.String(100))
    thickness = db.Column(db.Numeric(10, 3))  # mm
    unit_price = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    product_files = db.relationship('ProductFile', backref='product', lazy=True, cascade='all, delete-orphan')
    project_products = db.relationship('ProjectProduct', backref='product', lazy=True, cascade='all, delete-orphan')
```

**ProductFile:**
```python
class ProductFile(db.Model):
    __tablename__ = 'product_files'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10))  # DXF, PDF, etc.
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/products` | GET | `index()` | List all products with search/filter |
| `/products/new` | GET/POST | `create()` | Create new product |
| `/products/<id>` | GET | `view(id)` | View product details + files |
| `/products/<id>/edit` | GET/POST | `edit(id)` | Edit product information |
| `/products/<id>/delete` | POST | `delete(id)` | Delete product |
| `/products/<id>/files/upload` | POST | `upload_file(id)` | Upload DXF/PDF file |

#### **Relationships**

**Foreign Keys:**
- None (standalone catalog)

**Backrefs:**
- `product_files` → One product has many files
- `project_products` → Many-to-many with projects via junction table

#### **User Workflow**
1. **Create Product:**
   - Navigate to Products → New Product
   - Enter: SKU, Name, Description, Material, Thickness, Price
   - Upload DXF file
   - Save → Product added to catalog

2. **Add to Project:**
   - When creating/editing project
   - Select products from catalog
   - Specify quantity
   - System copies `unit_price` to `ProjectProduct` junction

#### **Data Dependencies**

**Receives From:**
- None (standalone catalog)

**Provides To:**
- **Projects Module:** Product catalog for selection
- **Reports Module:** Product usage statistics
- **Dashboard:** Product count

---

### **MODULE 5: QUEUE** ⏱️

#### **Purpose & Functionality**
Production scheduling and queue management - prioritize jobs, track cutting progress, log laser runs, and sync status with projects.

#### **File Location**
- **Route:** `app/routes/queue.py`
- **Model:** `app/models/business.py` → `QueueItem`, `LaserRun`
- **Templates:** `app/templates/queue/`
- **Blueprint:** `queue` (URL prefix: `/queue`)

#### **Database Models**

**QueueItem:**
```python
class QueueItem(db.Model):
    __tablename__ = 'queue_items'

    # Status constants
    STATUS_QUEUED = 'Queued'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    # Priority constants
    PRIORITY_LOW = 'Low'
    PRIORITY_NORMAL = 'Normal'
    PRIORITY_HIGH = 'High'
    PRIORITY_URGENT = 'Urgent'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    queue_position = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default=STATUS_QUEUED, index=True)
    priority = db.Column(db.String(20), default=PRIORITY_NORMAL)
    scheduled_date = db.Column(db.Date, index=True)
    estimated_cut_time = db.Column(db.Integer)  # minutes
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    laser_runs = db.relationship('LaserRun', backref='queue_item', lazy=True)
```

**LaserRun:**
```python
class LaserRun(db.Model):
    __tablename__ = 'laser_runs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    queue_item_id = db.Column(db.Integer, db.ForeignKey('queue_items.id', ondelete='SET NULL'))
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id', ondelete='SET NULL'))
    preset_id = db.Column(db.Integer, db.ForeignKey('machine_settings_presets.id', ondelete='SET NULL'))

    run_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    cut_time_minutes = db.Column(db.Integer, nullable=False)
    material_type = db.Column(db.String(100))
    material_thickness = db.Column(db.Numeric(10, 2))
    sheet_count = db.Column(db.Integer)
    parts_produced = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/queue` | GET | `index()` | List queue items with filter (active/all) |
| `/queue/<id>` | GET | `detail(id)` | View queue item details + runs |
| `/queue/<id>/status` | POST | `update_status(id)` | Update queue status → **SYNCS PROJECT STATUS** |
| `/queue/runs/new/<project_id>` | GET/POST | `new_run(project_id)` | Log new laser run (operator auto-selected) |
| `/queue/runs` | GET | `list_runs()` | List all laser runs |
| `/queue/reorder` | POST | `reorder()` | Reorder queue positions |

#### **Relationships**

**Foreign Keys:**
- `project_id` → `projects.id` (Many queue items to one project)

**Backrefs:**
- `laser_runs` → One queue item has many laser runs

#### **User Workflow**

**Queue Management:**

**1. Auto-Added to Queue:**
- Project POP marked received → Queue item auto-created
- Appears in queue with position, priority, scheduled date

**2. Manual Queue Management:**
- Drag-and-drop reordering (queue_position)
- Change priority (Low/Normal/High/Urgent)
- Reschedule date

**3. Start Production:**
- Operator clicks "Start" on queue item
- Status → "In Progress"
- **TRIGGER:** Project status auto-updates to "In Progress"
- Sets `started_at = now`

**4. Log Laser Run:**
- Navigate to "Log Laser Run"
- **AUTO-POPULATED:**
  - Operator (from session - logged-in user's operator profile)
  - Project details
  - Queue item
- Enter:
  - Cut time (minutes)
  - Material type/thickness
  - Sheet count
  - Parts produced
  - Machine preset used
  - Notes
- Save → Run logged

**5. Complete Queue Item:**
- Click "Mark Complete"
- Status → "Completed"
- **TRIGGER:** Project status auto-updates to "Completed"
- Sets `completed_at = now`
- Sets `project.completion_date = today`

#### **Data Dependencies**

**Receives From:**
- **Projects Module:** Auto-created when POP received
- **Operators Module:** Operator selection for laser runs
- **Presets Module:** Machine settings for laser runs

**Provides To:**
- **Projects Module:** Status updates (bidirectional sync)
- **Reports Module:** Production data (runs, cut times, efficiency)
- **Dashboard:** Active queue length

#### **Automation & Triggers**

**1. Queue-Project Status Sync (CRITICAL):**

**File:** `app/routes/queue.py` → `update_status()` (Lines 167-222)

**Logic:**
```python
# CRITICAL FIX: Synchronize Project status with Queue status
project = queue_item.project
if project:
    old_project_status = project.status

    # Map Queue status to Project status
    if new_status == QueueItem.STATUS_IN_PROGRESS:
        project.status = Project.STATUS_IN_PROGRESS
        project.updated_at = datetime.utcnow()
    elif new_status == QueueItem.STATUS_COMPLETED:
        project.status = Project.STATUS_COMPLETED
        project.completion_date = date.today()
        project.updated_at = datetime.utcnow()
    elif new_status == QueueItem.STATUS_CANCELLED:
        project.status = Project.STATUS_CANCELLED
        project.updated_at = datetime.utcnow()

    # Log project status change if it changed
    if old_project_status != project.status:
        project_activity = ActivityLog(
            entity_type='PROJECT',
            entity_id=project.id,
            action='STATUS_CHANGED',
            details=f'Status auto-updated from {old_project_status} to {project.status} (triggered by Queue status change)',
            user='System (Queue Sync)'
        )
        db.session.add(project_activity)

# Log queue activity
activity = ActivityLog(
    entity_type='QUEUE',
    entity_id=id,
    action='STATUS_CHANGED',
    details=f'Status changed from {old_status} to {new_status}',
    user='System'
)
db.session.add(activity)

# CRITICAL: Single atomic commit for all changes
db.session.commit()
```

**Key Features:**
- **Atomic Transaction:** All changes committed in single transaction
- **Activity Logging:** Both queue and project status changes logged
- **Bidirectional Sync:** Queue status drives project status

**2. Operator Auto-bind (NEW):**

**File:** `app/routes/auth.py` → `login()` (Lines 93-99)

On login, if user has operator profile:
```python
if hasattr(user, 'operator_profile') and user.operator_profile:
    session['operator_id'] = user.operator_profile.id
    session['operator_name'] = user.operator_profile.name
else:
    session.pop('operator_id', None)
    session.pop('operator_name', None)
```

**File:** `app/routes/queue.py` → `new_run()` (Lines 436-450)

Passes `session_operator_id` to template:
```python
session_operator_id = session.get('operator_id')
return render_template('queue/run_form.html', session_operator_id=session_operator_id, ...)
```

**File:** `app/templates/queue/run_form.html` (Lines 41-55)

Template auto-selects operator in dropdown with "(You)" indicator:
```html
<option value="{{ operator.id }}" {% if session_operator_id and operator.id == session_operator_id %}selected{% endif %}>
    {{ operator.name }}{% if session_operator_id and operator.id == session_operator_id %} (You){% endif %}
</option>
```

---

### **MODULE 6: PRESETS** ⚙️

#### **Purpose & Functionality**
Machine settings library - store and manage laser cutting parameters (power, speed, gas, pressure) for different material/thickness combinations.

#### **File Location**
- **Route:** `app/routes/presets.py`
- **Model:** `app/models/business.py` → `MachineSettingsPreset`
- **Templates:** `app/templates/presets/`
- **Blueprint:** `presets` (URL prefix: `/presets`)

#### **Database Model**

```python
class MachineSettingsPreset(db.Model):
    __tablename__ = 'machine_settings_presets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    material_type = db.Column(db.String(100), nullable=False, index=True)
    thickness = db.Column(db.Numeric(10, 2), nullable=False, index=True)

    # Cutting parameters
    power = db.Column(db.Integer)  # Watts
    speed = db.Column(db.Integer)  # mm/min
    frequency = db.Column(db.Integer)  # Hz
    gas_type = db.Column(db.String(50))  # O2, N2, Air
    gas_pressure = db.Column(db.Numeric(10, 2))  # Bar
    nozzle_size = db.Column(db.Numeric(10, 2))  # mm
    focus_position = db.Column(db.Numeric(10, 2))  # mm

    is_active = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    laser_runs = db.relationship('LaserRun', backref='preset', lazy=True)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/presets` | GET | `index()` | List all presets with filter (material, thickness) |
| `/presets/new` | GET/POST | `create()` | Create new preset |
| `/presets/<id>` | GET | `view(id)` | View preset details |
| `/presets/<id>/edit` | GET/POST | `edit(id)` | Edit preset |
| `/presets/<id>/toggle` | POST | `toggle_active(id)` | Activate/deactivate preset |

#### **Relationships**

**Foreign Keys:**
- None (standalone library)

**Backrefs:**
- `laser_runs` → One preset used in many laser runs

#### **User Workflow**
1. **Create Preset:**
   - Navigate to Presets → New Preset
   - Enter: Material Type, Thickness
   - Enter cutting parameters (power, speed, gas, etc.)
   - Save → Preset available for laser runs

2. **Use in Production:**
   - When logging laser run
   - Select preset from dropdown (filtered by material/thickness)
   - System applies preset parameters

#### **Data Dependencies**

**Receives From:**
- None (standalone library)

**Provides To:**
- **Queue Module:** Preset selection for laser runs
- **Projects Module:** Material type suggestions
- **Reports Module:** Preset usage statistics

---

### **MODULE 7: OPERATORS** 👷

#### **Purpose & Functionality**
Operator profile management - link machine operators to user accounts for authentication, tracking, and auto-binding in production logging.

#### **File Location**
- **Route:** `app/routes/operators.py`
- **Model:** `app/models/business.py` → `Operator`
- **Templates:** `app/templates/operators/`
- **Blueprint:** `operators` (URL prefix: `/operators`)

#### **Database Model**

```python
class Operator(db.Model):
    __tablename__ = 'operators'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Link to User account
    is_active = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='operator_profile', foreign_keys=[user_id])
    laser_runs = db.relationship('LaserRun', backref='operator_obj', lazy='dynamic')
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/operators` | GET | `list()` | List all operators |
| `/operators/new` | GET/POST | `create()` | Create new operator |
| `/operators/<id>` | GET | `view(id)` | View operator details + production stats |
| `/operators/<id>/edit` | GET/POST | `edit(id)` | Edit operator (including user_id link) |
| `/operators/<id>/toggle` | POST | `toggle_active(id)` | Activate/deactivate operator |

#### **Relationships**

**Foreign Keys:**
- `user_id` → `users.id` (One operator to one user, nullable)

**Backrefs:**
- `laser_runs` → One operator has many laser runs
- `user.operator_profile` → User has one operator profile

#### **User Workflow**

**Operator-User Linking:**

**1. Create Operator:**
- Admin creates operator profile
- Optionally links to existing user account (`user_id`)

**2. Auto-bind on Login:**
- User logs in
- System checks if `user.operator_profile` exists
- If yes: Stores `operator_id` and `operator_name` in session
- File: `app/routes/auth.py` → `login()` (Lines 93-99)

**3. Auto-select in Forms:**
- When logging laser run
- Operator dropdown auto-selects logged-in user's operator
- Shows "(You)" indicator
- File: `app/templates/queue/run_form.html` (Lines 41-55)

#### **Data Dependencies**

**Receives From:**
- **Admin Module:** User accounts for linking

**Provides To:**
- **Queue Module:** Operator selection for laser runs
- **Reports Module:** Operator performance statistics
- **Session:** Operator context for auto-binding

#### **Session Management**

**Operator Context Storage:**

```python
# On login (app/routes/auth.py)
if hasattr(user, 'operator_profile') and user.operator_profile:
    session['operator_id'] = user.operator_profile.id
    session['operator_name'] = user.operator_profile.name

# On logout (app/routes/auth.py)
session.pop('operator_id', None)
session.pop('operator_name', None)

# In laser run form (app/routes/queue.py)
session_operator_id = session.get('operator_id')
return render_template('queue/run_form.html', session_operator_id=session_operator_id, ...)
```

---

### **MODULE 8: INVENTORY** 📋

#### **Purpose & Functionality**
Material inventory tracking - manage stock levels, record transactions (purchases/usage), track costs, and alert on low stock.

#### **File Location**
- **Route:** `app/routes/inventory.py`
- **Model:** `app/models/business.py` → `InventoryItem`, `InventoryTransaction`
- **Templates:** `app/templates/inventory/`
- **Blueprint:** `inventory` (URL prefix: `/inventory`)

#### **Database Models**

**InventoryItem:**
```python
class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    # Category constants
    CATEGORY_RAW_MATERIAL = 'Raw Material'
    CATEGORY_CONSUMABLE = 'Consumable'
    CATEGORY_SPARE_PART = 'Spare Part'
    CATEGORY_TOOL = 'Tool'

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    material_type = db.Column(db.String(100), index=True)
    thickness = db.Column(db.Numeric(10, 3))
    unit = db.Column(db.String(20), nullable=False)  # sheets, kg, liters, pieces
    quantity_on_hand = db.Column(db.Numeric(10, 3), nullable=False, default=0)
    reorder_level = db.Column(db.Numeric(10, 3), default=0)
    reorder_quantity = db.Column(db.Numeric(10, 3))
    unit_cost = db.Column(db.Numeric(10, 2))
    supplier_name = db.Column(db.String(255))
    supplier_contact = db.Column(db.String(255))
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    transactions = db.relationship('InventoryTransaction', backref='item', lazy='dynamic', cascade='all, delete-orphan')
```

**InventoryTransaction:**
```python
class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'

    # Transaction type constants
    TYPE_PURCHASE = 'Purchase'
    TYPE_USAGE = 'Usage'
    TYPE_ADJUSTMENT = 'Adjustment'
    TYPE_RETURN = 'Return'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False, index=True)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    reference = db.Column(db.String(100))  # PO number, project code, etc.
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_by = db.Column(db.String(100))
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/inventory` | GET | `index()` | List all inventory items with low stock alerts |
| `/inventory/new` | GET/POST | `create()` | Create new inventory item |
| `/inventory/<id>` | GET | `view(id)` | View item details + transaction history |
| `/inventory/<id>/edit` | GET/POST | `edit(id)` | Edit item information |
| `/inventory/<id>/transaction` | POST | `add_transaction(id)` | Record purchase/usage/adjustment |
| `/inventory/transactions` | GET | `list_transactions()` | List all transactions |

#### **Relationships**

**Foreign Keys:**
- None (root entity)

**Backrefs:**
- `transactions` → One item has many transactions

#### **User Workflow**

**Stock Management:**

**1. Add Inventory Item:**
- Navigate to Inventory → New Item
- Enter: Item Code, Name, Category, Material Type, Thickness
- Set: Unit, Reorder Level, Unit Cost, Supplier
- Save → Item added

**2. Record Purchase:**
- Click item → "Add Transaction"
- Type: Purchase
- Quantity: +50 (positive)
- Unit Cost: R 500.00
- Reference: PO-12345
- Save → `quantity_on_hand` increases

**3. Record Usage:**
- Type: Usage
- Quantity: -10 (negative)
- Reference: JB-2025-10-CL0001-001 (project code)
- Save → `quantity_on_hand` decreases

**4. Low Stock Alert:**
- Dashboard shows low stock count
- Inventory list highlights items where `quantity_on_hand <= reorder_level`

#### **Data Dependencies**

**Receives From:**
- None (standalone tracking)

**Provides To:**
- **Dashboard:** Inventory count, low stock alerts
- **Reports Module:** Inventory valuation, usage statistics
- **Projects Module:** Material availability checking (future)

---

### **MODULE 9: REPORTS** 📈

#### **Purpose & Functionality**
Business intelligence and analytics - generate production reports, efficiency metrics, inventory reports, and client profitability analysis.

#### **File Location**
- **Route:** `app/routes/reports.py`
- **Templates:** `app/templates/reports/`
- **Blueprint:** `reports` (URL prefix: `/reports`)

#### **Database Models Used**
- **LaserRun** - Production data
- **QueueItem** - Queue statistics
- **Project** - Project data
- **Client** - Client data
- **Operator** - Operator performance
- **InventoryItem** - Stock data
- **InventoryTransaction** - Usage data

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/reports` | GET | `index()` | Reports dashboard |
| `/reports/production` | GET | `production_summary()` | Production summary (runs, hours, parts, operators) |
| `/reports/efficiency` | GET | `efficiency_metrics()` | Efficiency analysis (estimated vs actual cut time) |
| `/reports/inventory` | GET | `inventory_report()` | Inventory valuation and usage |
| `/reports/clients` | GET | `client_report()` | Client profitability and project counts |

#### **Report Types**

**1. Production Summary Report:**
- **Data Sources:** LaserRun, Operator, Project
- **Metrics:**
  - Total runs
  - Total cut hours
  - Total parts produced
  - Total sheets used
  - Breakdown by operator
  - Breakdown by material type
- **Filters:** Date range
- **Export:** CSV (admin/manager only)

**2. Efficiency Metrics Report:**
- **Data Sources:** LaserRun, Project
- **Metrics:**
  - Estimated cut time vs Actual cut time
  - Variance (minutes and percentage)
  - Efficiency percentage
  - Color-coded badges (green = efficient, red = over-time)
- **Calculations:**
  ```python
  variance_minutes = actual_time - estimated_time
  variance_percent = (variance_minutes / estimated_time) * 100
  efficiency = (estimated_time / actual_time) * 100
  ```

**3. Inventory Report:**
- **Data Sources:** InventoryItem, InventoryTransaction
- **Metrics:**
  - Total inventory value
  - Items by category
  - Low stock items
  - Recent transactions (last 50)
  - Purchase vs Usage statistics

**4. Client/Project Report:**
- **Data Sources:** Client, Project, LaserRun
- **Metrics:**
  - Total clients
  - Projects per client
  - Revenue per client
  - Total cut hours per client
  - Active vs completed projects

#### **User Workflow**
1. Navigate to Reports
2. Select report type
3. Apply filters (date range, client, etc.)
4. View report
5. Export to CSV (if authorized)

#### **Data Dependencies**

**Receives From:**
- **Queue Module:** LaserRun data
- **Projects Module:** Project data
- **Clients Module:** Client data
- **Operators Module:** Operator data
- **Inventory Module:** Stock and transaction data

**Provides To:**
- **Management:** Business insights
- **Dashboard:** Summary statistics

---

### **MODULE 10: SAGE INTEGRATION** 💼

#### **Purpose & Functionality**
Accounting system integration - connect to Sage Business Cloud Accounting API, sync customers, invoices, and payments.

#### **File Location**
- **Route:** `app/routes/sage.py`
- **Model:** `app/models/sage.py` → `SageConnection`, `SageBusiness`, `SageSyncCursor`, `SageAuditLog`
- **Templates:** `app/templates/sage/`
- **Blueprint:** `sage` (URL prefix: `/sage`)

#### **Database Models**

**SageConnection:**
```python
class SageConnection(db.Model):
    __tablename__ = 'sage_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('sage_connection', uselist=False))
    businesses = db.relationship('SageBusiness', backref='connection', lazy='dynamic')
```

**SageBusiness:**
```python
class SageBusiness(db.Model):
    __tablename__ = 'sage_businesses'

    id = db.Column(db.Integer, primary_key=True)
    connection_id = db.Column(db.Integer, db.ForeignKey('sage_connections.id', ondelete='CASCADE'))
    sage_business_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/sage` | GET | `dashboard()` | Sage integration dashboard |
| `/sage/connect` | GET | `connect()` | Initiate OAuth flow |
| `/sage/callback` | GET | `callback()` | OAuth callback handler |
| `/sage/disconnect` | POST | `disconnect()` | Disconnect Sage account |
| `/sage/sync/customers` | POST | `sync_customers()` | Sync Sage customers to Laser OS clients |
| `/sage/sync/invoices` | POST | `sync_invoices()` | Sync Laser OS invoices to Sage |

#### **Integration Flow**

**OAuth Connection:**
1. User clicks "Connect to Sage"
2. Redirected to Sage OAuth authorization
3. User authorizes
4. Sage redirects back with authorization code
5. System exchanges code for access token
6. Stores tokens in `SageConnection`

**Customer Sync:**
1. Fetch customers from Sage API
2. Match by email/name to existing Laser OS clients
3. Create new clients if no match
4. Update `client.sage_customer_id` for linking

**Invoice Sync:**
1. Select Laser OS invoice
2. Create corresponding invoice in Sage
3. Link via `invoice.sage_invoice_id`
4. Track sync status in `SageAuditLog`

#### **Data Dependencies**

**Receives From:**
- **Projects Module:** Invoice data for sync
- **Clients Module:** Customer data for matching

**Provides To:**
- **Clients Module:** Sage customer IDs
- **Invoices Module:** Sage invoice IDs
- **Reports Module:** Sync status and audit logs

---

### **MODULE 11: COMMUNICATIONS** ✉️

#### **Purpose & Functionality**
Email and messaging system - send automated notifications, track communication history, manage message templates.

#### **File Location**
- **Route:** `app/routes/comms.py`, `app/routes/templates.py`
- **Model:** `app/models/business.py` → `Communication`, `MessageTemplate`
- **Service:** `app/services/communication_service.py`
- **Templates:** `app/templates/comms/`
- **Blueprint:** `comms` (URL prefix: `/comms`)

#### **Database Models**

**Communication:**
```python
class Communication(db.Model):
    __tablename__ = 'communications'

    # Status constants
    STATUS_PENDING = 'Pending'
    STATUS_SENT = 'Sent'
    STATUS_DELIVERED = 'Delivered'
    STATUS_READ = 'Read'
    STATUS_FAILED = 'Failed'

    # Type constants
    TYPE_EMAIL = 'Email'
    TYPE_SMS = 'SMS'
    TYPE_WHATSAPP = 'WhatsApp'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='SET NULL'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'))
    communication_type = db.Column(db.String(20), nullable=False, index=True)
    subject = db.Column(db.String(255))
    message_body = db.Column(db.Text, nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
```

**MessageTemplate:**
```python
class MessageTemplate(db.Model):
    __tablename__ = 'message_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    subject = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)
    template_type = db.Column(db.String(20), nullable=False)  # Email, SMS
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/comms` | GET | `index()` | List all communications |
| `/comms/send` | GET/POST | `send_communication()` | Send new email/SMS |
| `/comms/<id>` | GET | `view(id)` | View communication details |
| `/comms/templates` | GET | `list_templates()` | List message templates |
| `/comms/templates/new` | GET/POST | `create_template()` | Create new template |
| `/comms/templates/<id>/edit` | GET/POST | `edit_template(id)` | Edit template |

#### **Communication Service**

**File:** `app/services/communication_service.py`

**Functions:**
- `send_email(to, subject, body, attachments=None)` - Send email via SMTP
- `send_project_notification(project, template_name)` - Send templated notification
- `send_pop_confirmation(project)` - Auto-send POP confirmation email

**Template Variables:**
- `{{client_name}}` - Client name
- `{{project_code}}` - Project code
- `{{project_name}}` - Project name
- `{{pop_deadline}}` - POP deadline date
- `{{due_date}}` - Project due date
- `{{company_name}}` - Company name

#### **User Workflow**

**Manual Communication:**
1. Navigate to Communications → Send
2. Select: Client, Project (optional)
3. Choose template or write custom message
4. Enter recipient email
5. Send → Email sent, logged in database

**Automated Communication:**

**1. POP Confirmation:**
- Trigger: Project POP marked received
- Template: "POP Confirmation"
- Recipient: Client email
- Content: Confirms payment, provides deadline

**2. Quote Expiring Soon:**
- Trigger: Scheduled job (daily)
- Condition: Quote expiring in ≤3 days
- Template: "Quote Expiring Reminder"

#### **Data Dependencies**

**Receives From:**
- **Clients Module:** Client contact information
- **Projects Module:** Project details for notifications

**Provides To:**
- **Clients Module:** Communication history
- **Projects Module:** Notification status
- **Reports Module:** Communication statistics

#### **Future Enhancements (Planned)**

**From User Memories:**

1. **Automated Message Templates:**
   - Trigger: Project milestone (e.g., "Collection Ready" when status=Complete)
   - Template: Auto-send notification

2. **Inbound Email Parsing:**
   - Parse incoming emails
   - Auto-create/update projects
   - Extract POP attachments

3. **User-Specific Routing:**
   - Control which users receive which notification types
   - Role-based notification preferences

---

### **MODULE 12: ADMIN** 🔧

#### **Purpose & Functionality**
System administration - manage users, roles, permissions, system settings, and view activity logs.

#### **File Location**
- **Route:** `app/routes/admin.py`
- **Model:** `app/models/auth.py` → `User`, `Role`, `UserRole`, `LoginHistory`
- **Templates:** `app/templates/admin/`
- **Blueprint:** `admin` (URL prefix: `/admin`)

#### **Database Models**

**User:**
```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref='users', lazy='dynamic')
    login_history = db.relationship('LoginHistory', backref='user', lazy='dynamic')
```

**Role:**
```python
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)  # admin, manager, operator, viewer
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON array of permission codes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

**LoginHistory:**
```python
class LoginHistory(db.Model):
    __tablename__ = 'login_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    success = db.Column(db.Boolean, nullable=False)
```

#### **Key Routes**

| Route | Method | Function | Description |
|-------|--------|----------|-------------|
| `/admin/users` | GET | `users()` | List all users |
| `/admin/users/new` | GET/POST | `create_user()` | Create new user |
| `/admin/users/<id>/edit` | GET/POST | `edit_user(id)` | Edit user (roles, active status) |
| `/admin/users/<id>/reset-password` | POST | `reset_password(id)` | Reset user password |
| `/admin/roles` | GET | `roles()` | List all roles |
| `/admin/activity` | GET | `activity_log()` | View system activity log |
| `/admin/settings` | GET/POST | `settings()` | System settings |

#### **Role-Based Access Control (RBAC)**

**Roles:**
- **admin** - Full system access
- **manager** - Manage projects, queue, reports
- **operator** - Log laser runs, view queue
- **viewer** - Read-only access

**Decorator:** `@role_required('admin', 'manager')`

**Usage:**
```python
from app.utils.decorators import role_required

@bp.route('/admin/users')
@role_required('admin')
def users():
    # Only admins can access
```

#### **User Workflow**

**User Management:**
1. Admin navigates to Admin → Users
2. Click "New User"
3. Enter: Username, Email, Full Name, Password
4. Assign roles (checkboxes)
5. Save → User created

**Role Assignment:**
1. Edit user
2. Check/uncheck role checkboxes
3. Save → Roles updated in `user_roles` junction table

**Activity Monitoring:**
1. Navigate to Admin → Activity Log
2. View: All system actions (project created, status changed, etc.)
3. Filter by: Entity type, action, date range

#### **Data Dependencies**

**Receives From:**
- All modules (activity logging)

**Provides To:**
- **All Modules:** User authentication and authorization
- **Operators Module:** User accounts for operator linking
- **Reports Module:** User activity statistics

---

## **4. COMPLETE BUSINESS WORKFLOW LIFECYCLE**

### **4.1 End-to-End Workflow: From Inquiry to Completion**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LASER OS BUSINESS WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────┘

STAGE 1: CLIENT ONBOARDING
┌──────────────┐
│   Clients    │ → Create client record (CL-0001)
│    Module    │   Store contact information
└──────┬───────┘
       │
       ↓
STAGE 2: PROJECT REQUEST
┌──────────────┐
│   Projects   │ → Create project (JB-2025-10-CL0001-001)
│    Module    │   Status: "Request"
└──────┬───────┘   Link to client
       │
       ↓
STAGE 3: QUOTE PREPARATION
┌──────────────┐
│    Files     │ → Upload DXF files
│    Module    │   Attach to project
└──────┬───────┘
       │
┌──────────────┐
│   Projects   │ → Enter material specs (type, thickness, quantity)
│    Module    │   Enter estimated cut time
└──────┬───────┘   Update status: "Quote & Approval"
       │
┌──────────────┐
│    Quotes    │ → Generate quote document
│    Module    │   Send to client
└──────┬───────┘
       │
       ↓
STAGE 4: APPROVAL & PAYMENT
┌──────────────┐
│   Projects   │ → Client approves and pays
│    Module    │   Click "Mark POP Received"
└──────┬───────┘
       │
       ├─────────────────────────────────────────────────────────┐
       │                                                         │
       │  🔥 AUTOMATION TRIGGER #1: Auto-Queue on POP Received  │
       │                                                         │
       │  File: app/services/status_automation.py               │
       │  Actions:                                              │
       │  1. Set pop_received = True                            │
       │  2. Set pop_received_date = today                      │
       │  3. Calculate pop_deadline = today + 10 days           │
       │  4. Update status = "Approved (POP Received)"          │
       │  5. CREATE QueueItem:                                  │
       │     - status = "Queued"                                │
       │     - priority = "Normal"                              │
       │     - scheduled_date = today/next business day         │
       │     - estimated_cut_time = project.estimated_cut_time  │
       │     - queue_position = max + 1                         │
       │  6. Send POP confirmation email to client              │
       │                                                         │
       └─────────────────────────────────────────────────────────┘
       │
       ↓
STAGE 5: PRODUCTION SCHEDULING
┌──────────────┐
│    Queue     │ → Queue item auto-created
│    Module    │   Appears in queue list
└──────┬───────┘   Manager can adjust priority/position
       │
       ↓
STAGE 6: PRODUCTION START
┌──────────────┐
│    Queue     │ → Operator clicks "Start"
│    Module    │   Update queue status: "In Progress"
└──────┬───────┘
       │
       ├─────────────────────────────────────────────────────────┐
       │                                                         │
       │  🔥 AUTOMATION TRIGGER #2: Queue-Project Status Sync   │
       │                                                         │
       │  File: app/routes/queue.py → update_status()           │
       │  Actions:                                              │
       │  1. Queue status → "In Progress"                       │
       │  2. Project status → "In Progress" (auto-sync)         │
       │  3. Set queue.started_at = now                         │
       │  4. Log activity for both entities                     │
       │  5. Commit in single atomic transaction                │
       │                                                         │
       └─────────────────────────────────────────────────────────┘
       │
       ↓
STAGE 7: PRODUCTION LOGGING
┌──────────────┐
│    Queue     │ → Operator logs laser run
│    Module    │
└──────┬───────┘
       │
       ├─────────────────────────────────────────────────────────┐
       │                                                         │
       │  🔥 AUTOMATION TRIGGER #3: Operator Auto-bind          │
       │                                                         │
       │  File: app/routes/auth.py → login()                    │
       │  File: app/routes/queue.py → new_run()                 │
       │  Actions:                                              │
       │  1. On login: Store operator_id in session             │
       │  2. In laser run form: Auto-select operator            │
       │  3. Show "(You)" indicator                             │
       │  4. Display "Auto-selected based on your login"        │
       │                                                         │
       └─────────────────────────────────────────────────────────┘
       │
       ↓
       Enter: Cut time, material, sheets, parts, preset
       Save → LaserRun created
       │
       ↓
STAGE 8: PRODUCTION COMPLETION
┌──────────────┐
│    Queue     │ → Operator clicks "Mark Complete"
│    Module    │   Update queue status: "Completed"
└──────┬───────┘
       │
       ├─────────────────────────────────────────────────────────┐
       │                                                         │
       │  🔥 AUTOMATION TRIGGER #4: Queue-Project Status Sync   │
       │                                                         │
       │  File: app/routes/queue.py → update_status()           │
       │  Actions:                                              │
       │  1. Queue status → "Completed"                         │
       │  2. Project status → "Completed" (auto-sync)           │
       │  3. Set queue.completed_at = now                       │
       │  4. Set project.completion_date = today                │
       │  5. Log activity for both entities                     │
       │  6. Commit in single atomic transaction                │
       │                                                         │
       └─────────────────────────────────────────────────────────┘
       │
       ↓
STAGE 9: INVOICING & ACCOUNTING
┌──────────────┐
│   Invoices   │ → Generate invoice for project
│    Module    │   Send to client
└──────┬───────┘
       │
┌──────────────┐
│     Sage     │ → Sync invoice to Sage Accounting
│ Integration  │   Track payment status
└──────┬───────┘
       │
       ↓
STAGE 10: REPORTING & ANALYTICS
┌──────────────┐
│   Reports    │ → Production summary
│    Module    │   Efficiency metrics
└──────────────┘   Client profitability
                   Inventory usage
```

### **4.2 Data Flow Example: Project Creation to Completion**

**Example Project:** Custom metal brackets for Client "ABC Manufacturing"

**Step 1: Client Creation**
```
Module: Clients
Action: Create client
Data Created:
  - Client ID: 1
  - Client Code: CL-0001
  - Name: ABC Manufacturing
  - Email: orders@abc.com
```

**Step 2: Project Creation**
```
Module: Projects
Action: Create project
Data Created:
  - Project ID: 1
  - Project Code: JB-2025-10-CL0001-001
  - Client ID: 1 (FK → clients.id)
  - Name: Custom Metal Brackets
  - Status: Request
```

**Step 3: File Upload**
```
Module: Files
Action: Upload DXF
Data Created:
  - DesignFile ID: 1
  - Project ID: 1 (FK → projects.id)
  - Filename: bracket_design.dxf
  - File Path: /uploads/projects/1/bracket_design.dxf
```

**Step 4: Material Specs & Quote**
```
Module: Projects
Action: Update project
Data Updated:
  - Material Type: Mild Steel
  - Thickness: 3mm
  - Quantity: 50 sheets
  - Estimated Cut Time: 120 minutes
  - Status: Quote & Approval

Module: Quotes
Action: Generate quote
Data Created:
  - Quote ID: 1
  - Project ID: 1 (FK → projects.id)
  - Total Amount: R 15,000.00
```

**Step 5: POP Received (AUTOMATION TRIGGER)**
```
Module: Projects
Action: Mark POP received
Data Updated:
  - pop_received: True
  - pop_received_date: 2025-10-27
  - pop_deadline: 2025-11-06 (today + 10 days)
  - Status: Approved (POP Received)

AUTOMATION: Auto-Queue
Data Created:
  - QueueItem ID: 1
  - Project ID: 1 (FK → projects.id)
  - Status: Queued
  - Priority: Normal
  - Scheduled Date: 2025-10-28
  - Estimated Cut Time: 120 minutes
  - Queue Position: 1

Module: Communications
Action: Send POP confirmation email
Data Created:
  - Communication ID: 1
  - Client ID: 1 (FK → clients.id)
  - Project ID: 1 (FK → projects.id)
  - Type: Email
  - Subject: Payment Confirmed - JB-2025-10-CL0001-001
  - Status: Sent
```

**Step 6: Production Start (AUTOMATION TRIGGER)**
```
Module: Queue
Action: Update queue status to "In Progress"
Data Updated:
  - QueueItem.status: In Progress
  - QueueItem.started_at: 2025-10-28 08:00:00

AUTOMATION: Queue-Project Status Sync
Data Updated:
  - Project.status: In Progress (auto-synced)
  - Project.updated_at: 2025-10-28 08:00:00

Data Created:
  - ActivityLog (Queue): Status changed to In Progress
  - ActivityLog (Project): Status auto-updated to In Progress
```

**Step 7: Laser Run Logging (AUTOMATION TRIGGER)**
```
Module: Queue
Action: Log laser run
Session Data:
  - operator_id: 3 (from session - logged-in user)
  - operator_name: John Smith

AUTOMATION: Operator Auto-bind
Form Pre-populated:
  - Operator: John Smith (You) [auto-selected]

Data Created:
  - LaserRun ID: 1
  - Project ID: 1 (FK → projects.id)
  - Queue Item ID: 1 (FK → queue_items.id)
  - Operator ID: 3 (FK → operators.id) [auto-selected]
  - Preset ID: 5 (FK → machine_settings_presets.id)
  - Run Date: 2025-10-28 08:15:00
  - Cut Time: 125 minutes (actual)
  - Material Type: Mild Steel
  - Thickness: 3mm
  - Sheet Count: 50
  - Parts Produced: 200
```

**Step 8: Production Completion (AUTOMATION TRIGGER)**
```
Module: Queue
Action: Update queue status to "Completed"
Data Updated:
  - QueueItem.status: Completed
  - QueueItem.completed_at: 2025-10-28 10:20:00

AUTOMATION: Queue-Project Status Sync
Data Updated:
  - Project.status: Completed (auto-synced)
  - Project.completion_date: 2025-10-28
  - Project.updated_at: 2025-10-28 10:20:00

Data Created:
  - ActivityLog (Queue): Status changed to Completed
  - ActivityLog (Project): Status auto-updated to Completed, completion_date set
```

**Step 9: Invoicing**
```
Module: Invoices
Action: Generate invoice
Data Created:
  - Invoice ID: 1
  - Project ID: 1 (FK → projects.id)
  - Invoice Number: INV-2025-001
  - Total Amount: R 15,000.00
  - Status: Sent

Module: Sage Integration
Action: Sync invoice to Sage
Data Updated:
  - Invoice.sage_invoice_id: sage_inv_12345
Data Created:
  - SageAuditLog: Invoice synced successfully
```

**Step 10: Reporting**
```
Module: Reports
Action: View production summary
Data Aggregated:
  - Total Runs: 1
  - Total Cut Hours: 2.08 (125 minutes)
  - Total Parts: 200
  - Efficiency: 96% (120 estimated / 125 actual)
  - Operator: John Smith - 2.08 hours
```

---

## **5. AUTOMATION & TRIGGERS**

### **5.1 Critical Automation Systems**

#### **AUTOMATION #1: Auto-Queue on POP Received**

**Trigger:** Project POP marked as received
**File:** `app/services/status_automation.py`
**Invoked From:** `app/routes/projects.py` → `mark_pop_received()`

**Logic:**
```python
def auto_queue_project(project):
    """
    Automatically create queue item when POP is received.

    User Memory: "User prefers automatic queue addition when POP is marked
    as received, with sensible defaults (Normal priority, today/next business
    day scheduling, using project's estimated_cut_time)."
    """
    # Calculate scheduled date (today or next business day)
    scheduled_date = get_next_business_day()

    # Get next queue position
    max_position = db.session.query(func.max(QueueItem.queue_position)).scalar() or 0

    # Create queue item
    queue_item = QueueItem(
        project_id=project.id,
        status=QueueItem.STATUS_QUEUED,
        priority=QueueItem.PRIORITY_NORMAL,  # Sensible default
        scheduled_date=scheduled_date,
        estimated_cut_time=project.estimated_cut_time,
        queue_position=max_position + 1
    )

    db.session.add(queue_item)

    # Log activity
    activity = ActivityLog(
        entity_type='QUEUE',
        entity_id=queue_item.id,
        action='AUTO_CREATED',
        details=f'Queue item auto-created when POP received for project {project.project_code}',
        user='System (Auto-Queue)'
    )
    db.session.add(activity)

    # Send POP confirmation email
    send_pop_confirmation_email(project)

    db.session.commit()
```

**Impact:**
- Eliminates manual queue creation step
- Ensures consistent queue defaults
- Reduces human error
- Speeds up workflow

---

#### **AUTOMATION #2: Queue-Project Status Synchronization**

**Trigger:** Queue item status changes
**File:** `app/routes/queue.py` → `update_status()` (Lines 167-222)
**Invoked From:** Queue status update form

**Logic:**
```python
@bp.route('/queue/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    """
    Update queue item status and synchronize with project status.

    CRITICAL: This function implements bidirectional status sync between
    Queue and Project entities to maintain data consistency.
    """
    queue_item = QueueItem.query.get_or_404(id)
    old_status = queue_item.status
    new_status = request.form.get('status')

    # Update queue status
    queue_item.status = new_status
    queue_item.updated_at = datetime.utcnow()

    # Set timestamps
    if new_status == QueueItem.STATUS_IN_PROGRESS and not queue_item.started_at:
        queue_item.started_at = datetime.utcnow()
    elif new_status == QueueItem.STATUS_COMPLETED and not queue_item.completed_at:
        queue_item.completed_at = datetime.utcnow()

    # CRITICAL FIX: Synchronize Project status with Queue status
    project = queue_item.project
    if project:
        old_project_status = project.status

        # Map Queue status to Project status
        if new_status == QueueItem.STATUS_IN_PROGRESS:
            project.status = Project.STATUS_IN_PROGRESS
            project.updated_at = datetime.utcnow()
        elif new_status == QueueItem.STATUS_COMPLETED:
            project.status = Project.STATUS_COMPLETED
            project.completion_date = date.today()
            project.updated_at = datetime.utcnow()
        elif new_status == QueueItem.STATUS_CANCELLED:
            project.status = Project.STATUS_CANCELLED
            project.updated_at = datetime.utcnow()

        # Log project status change if it changed
        if old_project_status != project.status:
            project_activity = ActivityLog(
                entity_type='PROJECT',
                entity_id=project.id,
                action='STATUS_CHANGED',
                details=f'Status auto-updated from {old_project_status} to {project.status} (triggered by Queue status change)',
                user='System (Queue Sync)'
            )
            db.session.add(project_activity)

    # Log queue activity
    activity = ActivityLog(
        entity_type='QUEUE',
        entity_id=id,
        action='STATUS_CHANGED',
        details=f'Status changed from {old_status} to {new_status}',
        user='System'
    )
    db.session.add(activity)

    # CRITICAL: Single atomic commit for all changes
    db.session.commit()

    flash('Queue status updated successfully', 'success')
    return redirect(url_for('queue.index'))
```

**Status Mapping:**
| Queue Status | Project Status | Additional Actions |
|--------------|----------------|-------------------|
| Queued | (No change) | - |
| In Progress | In Progress | Set `started_at` |
| Completed | Completed | Set `completed_at`, `completion_date` |
| Cancelled | Cancelled | - |

**Impact:**
- Maintains data consistency across modules
- Eliminates manual status updates
- Provides audit trail via ActivityLog
- Atomic transaction prevents partial updates

---

#### **AUTOMATION #3: Operator Auto-bind on Login**

**Trigger:** User login
**File:** `app/routes/auth.py` → `login()` (Lines 93-99)
**Invoked From:** Login form submission

**Logic:**
```python
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # ... authentication logic ...

    if user and check_password_hash(user.password_hash, password):
        login_user(user)

        # CRITICAL FIX: Auto-bind operator identity to session
        # Check if user has an associated operator profile
        if hasattr(user, 'operator_profile') and user.operator_profile:
            session['operator_id'] = user.operator_profile.id
            session['operator_name'] = user.operator_profile.name
        else:
            # Clear operator session data if no profile exists
            session.pop('operator_id', None)
            session.pop('operator_name', None)

        # ... redirect logic ...
```

**Usage in Forms:**

**File:** `app/routes/queue.py` → `new_run()` (Lines 436-450)
```python
@bp.route('/queue/runs/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_run(project_id):
    # Get operator from session
    session_operator_id = session.get('operator_id')

    # Pass to template
    return render_template(
        'queue/run_form.html',
        session_operator_id=session_operator_id,
        operators=operators,
        ...
    )
```

**File:** `app/templates/queue/run_form.html` (Lines 47-48)
```html
<select name="operator_id" required>
    {% for operator in operators %}
    <option value="{{ operator.id }}"
            {% if session_operator_id and operator.id == session_operator_id %}selected{% endif %}>
        {{ operator.name }}{% if session_operator_id and operator.id == session_operator_id %} (You){% endif %}
    </option>
    {% endfor %}
</select>
```

**Impact:**
- Reduces data entry time
- Improves accuracy (operators select themselves)
- Better user experience
- Maintains accountability

---

### **5.2 Future Automation (Planned)**

**From User Memories:**

#### **1. Automated Message Templates**
- **Trigger:** Project milestone reached
- **Example:** When `project.status = 'Completed'`, auto-send "Collection Ready" email
- **Implementation:** Scheduled job checks for status changes, sends templated emails

#### **2. Inbound Email Parsing**
- **Trigger:** Email received at designated address
- **Action:** Parse email content, extract project details, auto-create/update projects
- **Advanced:** Extract POP attachments, auto-mark POP received

#### **3. User-Specific Communication Routing**
- **Trigger:** Notification event
- **Action:** Check user preferences, route to appropriate users based on role/settings
- **Example:** Only managers receive "Quote Expiring" notifications

---

## **6. SESSION MANAGEMENT & CONTEXT**

### **6.1 Operator Session Context**

**Purpose:** Maintain operator identity across requests for auto-population in forms

**Storage:**
```python
session['operator_id'] = 3
session['operator_name'] = 'John Smith'
```

**Lifecycle:**
1. **Set on Login:** `app/routes/auth.py` → `login()`
2. **Used in Forms:** `app/routes/queue.py` → `new_run()`
3. **Cleared on Logout:** `app/routes/auth.py` → `logout()`

**Security:**
- Session data stored server-side (Flask session)
- Encrypted session cookie
- Cleared on logout

---

## **7. INTEGRATION POINTS & DATA FLOW**

### **7.1 Module Interconnection Matrix**

| From Module | To Module | Data Exchanged | Trigger |
|-------------|-----------|----------------|---------|
| **Clients** | Projects | Client ID, contact info | Project creation |
| **Projects** | Queue | Project details, estimated time | POP received (auto) |
| **Projects** | Communications | Project details, client email | POP received, status change |
| **Queue** | Projects | Status updates | Queue status change (auto) |
| **Queue** | LaserRun | Queue item ID, project ID | Laser run logging |
| **Operators** | LaserRun | Operator ID | Laser run logging (auto-selected) |
| **Operators** | Session | Operator ID, name | User login (auto) |
| **Presets** | LaserRun | Preset ID, cutting parameters | Laser run logging |
| **Projects** | Sage | Invoice data | Manual sync |
| **Clients** | Sage | Customer data | Manual sync |
| **All Modules** | Reports | Aggregated data | Report generation |
| **All Modules** | Dashboard | Statistics | Page load |
| **All Modules** | ActivityLog | Audit trail | Any CRUD operation |

### **7.2 Critical Data Dependencies**

**Project is the Central Entity:**
- **Depends on:** Client (required)
- **Feeds into:** Queue, LaserRun, Quote, Invoice, Communication, Reports
- **Status drives:** Queue status (bidirectional sync)

**Queue is the Production Hub:**
- **Depends on:** Project (required)
- **Feeds into:** LaserRun, Project status (bidirectional sync)
- **Coordinates:** Operator, Preset, Production timeline

**LaserRun is the Production Record:**
- **Depends on:** Project (required), Queue (optional), Operator (optional), Preset (optional)
- **Feeds into:** Reports (efficiency, production summary)

---

## **8. CONCLUSION**

This Laser OS system is a comprehensive, tightly-integrated business management platform with:

- **12 Core Modules** working in harmony
- **3 Critical Automation Systems** reducing manual work
- **Bidirectional Data Sync** maintaining consistency
- **Session-Based Context** improving user experience
- **Complete Audit Trail** via ActivityLog
- **Scalable Architecture** with Blueprint-based routing

**Key Strengths:**
1. **Automation:** Auto-queue, status sync, operator auto-bind
2. **Integration:** Sage accounting, email communications
3. **Tracking:** Complete lifecycle from inquiry to completion
4. **Reporting:** Comprehensive analytics and BI
5. **Security:** RBAC, session management, audit logging

**Recent Enhancements:**
- Queue-Project status synchronization (atomic transactions)
- Operator auto-bind on login
- Sidebar UI improvements (SVG icons, collapsible)
- Project filter layout optimization

This architecture document serves as the definitive technical reference for understanding how all components of Laser OS work together to deliver a seamless laser cutting business management experience.

