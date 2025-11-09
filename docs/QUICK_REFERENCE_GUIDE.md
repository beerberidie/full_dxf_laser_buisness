# Laser OS & Module N - Quick Reference Guide

**Version:** 1.0  
**Date:** 2025-10-21  
**Purpose:** Quick lookup for common tasks and workflows

---

## 📋 Common Workflows

### Client Onboarding
1. Navigate to **Clients** → **New Client**
2. Enter company name (required)
3. Add contact details (optional)
4. Click **Save**
5. System generates code: `CL-0001`, `CL-0002`, etc.

### Project Creation
1. Navigate to **Projects** → **New Project** (or from Client detail page)
2. Select client
3. Enter project name and details
4. Set due date
5. Click **Save**
6. System generates code: `JB-YYYY-MM-CLxxxx-###`

### File Upload with Intelligent Processing
1. Open project detail page
2. Click **Upload Files**
3. Select files (DXF, LBRN2, PDF, Excel, Image)
4. Click **Upload**
5. Module N automatically extracts metadata
6. View extracted material, thickness, dimensions

### Quote Creation
1. Navigate to **Quotes** → **New Quote**
2. Select client and project
3. Add line items (description, quantity, price)
4. System calculates subtotal, tax, total
5. Click **Save**
6. Export PDF for client

### Invoice from Quote
1. Open accepted quote
2. Click **Create Invoice**
3. Line items auto-populated
4. Adjust if needed
5. Click **Save**
6. Export PDF and send to client

### POP Receipt & Auto-Queue
1. Open project detail page
2. Upload POP document
3. Mark **POP Received** with date
4. System calculates deadline (date + 3 days)
5. If auto-queue enabled: Project automatically added to queue
6. Otherwise: Manually add to queue

### Manual Queue Addition
1. Open project detail page
2. Click **Add to Queue**
3. Set priority, scheduled date, estimated time
4. Click **Add**
5. Project appears in queue

### Production Workflow
1. Operator views **Queue** page
2. Selects next job
3. Clicks **Start Production**
4. Performs cutting
5. Clicks **Complete**
6. Enters actual cut time, material used, parts produced
7. System creates laser run record
8. System updates inventory (material consumption)

### Inventory Management
1. Navigate to **Inventory**
2. View all items with stock levels
3. Low stock items highlighted in red
4. Click item to view details
5. Click **Adjust Stock** to add/remove
6. System tracks all transactions

### Communication Logging
1. Navigate to **Communications** → **New**
2. Select type (Email, WhatsApp, Phone, etc.)
3. Enter from/to, subject, message
4. System suggests client/project links
5. Confirm links
6. Click **Save**

---

## 🔑 Key Codes & Formats

### Client Codes
- **Format:** `CL-####`
- **Example:** `CL-0001`, `CL-0042`, `CL-0156`
- **Auto-generated:** Sequential numbering

### Project Codes
- **Format:** `JB-YYYY-MM-CLxxxx-###`
- **Example:** `JB-2025-10-CL0042-001`
- **Components:**
  - `JB` = Job prefix
  - `YYYY` = Year (2025)
  - `MM` = Month (10)
  - `CLxxxx` = Client code (CL0042)
  - `###` = Sequential number (001, 002, etc.)

### Quote Numbers
- **Format:** `QT-YYYY-####`
- **Example:** `QT-2025-0001`, `QT-2025-0042`

### Invoice Numbers
- **Format:** `INV-YYYY-####`
- **Example:** `INV-2025-0001`, `INV-2025-0042`

### Standardized Filenames (Module N)
- **Format:** `{ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}`
- **Example:** `CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x10-v1.dxf`

### Material Codes
- `MS` = Mild Steel
- `SS` = Stainless Steel
- `GALV` = Galvanized Steel
- `AL` = Aluminum
- `BR` = Brass
- `CU` = Copper
- `CS` = Carbon Steel
- `VAST` = Vastrap
- `ZN` = Zinc
- `OTH` = Other

---

## 📊 Project Status Workflow

```
Request
  ↓
Quote & Approval
  ↓
Approved (POP Received) ← POP deadline set (date + 3 days)
  ↓
Queued (Scheduled for Cutting) ← Auto-queue if enabled
  ↓
In Progress
  ↓
Completed
```

**Alternative:** `Cancelled` (can happen at any stage)

---

## 🎯 Priority Levels

**Queue Items:**
- **Urgent:** Critical jobs, immediate attention
- **High:** Important jobs, prioritize
- **Normal:** Standard jobs (default)
- **Low:** Non-urgent jobs

---

## 📈 Dashboard Metrics

**Statistics Shown:**
- Total clients
- Total projects
- Active projects (Approved + In Progress)
- Total products
- Total files
- Queue length (Queued + In Progress)
- Inventory items
- Low stock count

**Recent Activity:**
- 5 most recent clients
- 5 most recent projects
- 5 most recent files
- 5 current queue items

---

## 🔐 User Roles & Permissions

### Admin
- **Access:** Full access to all features
- **Can:** Create/edit/delete everything, manage users, view all reports

### Manager
- **Access:** Business operations
- **Can:** Create/edit clients, projects, quotes, invoices, queue, inventory
- **Cannot:** Manage users, system settings

### Operator
- **Access:** Production operations
- **Can:** View queue, create laser runs, view inventory, view projects
- **Cannot:** Create clients, quotes, invoices, manage users

### Viewer
- **Access:** Read-only
- **Can:** View all data
- **Cannot:** Create, edit, or delete anything

---

## 🔧 Module N File Parsers

### DXF Parser
- **Extracts:** Layers, entities, dimensions, holes, material hints, thickness hints
- **Use Case:** AutoCAD drawings, technical drawings

### LightBurn Parser (.lbrn2)
- **Extracts:** Cut settings (power, speed), layers, shapes, material height
- **Use Case:** LightBurn project files

### PDF Parser
- **Extracts:** Text, tables, metadata, embedded images
- **Use Case:** Scanned drawings, cut lists, specifications

### Excel Parser
- **Extracts:** Sheets, headers, data rows, schema detection
- **Use Case:** Part lists, BOMs, cut lists

### Image Parser
- **Extracts:** Dimensions, EXIF data, OCR text (requires Tesseract)
- **Use Case:** Photos, scanned drawings, sketches

---

## 📡 Webhook Events (Module N → Laser OS)

### Event Types
1. **file.ingested** - File uploaded and validated
2. **file.processed** - File parsed, metadata extracted
3. **file.failed** - Processing failed
4. **file.re_extracted** - File re-processed
5. **file.deleted** - File deleted

### Webhook Flow
```
Module N processes file → Generates event → 
Signs with HMAC-SHA256 → Sends to Laser OS → 
Laser OS verifies signature → Creates/updates DesignFile → 
Logs activity → User sees result
```

---

## 💾 Database Tables

### Core Business Tables
- `clients` - Customer information
- `projects` - Jobs/projects
- `products` - Product catalog
- `design_files` - Project files
- `project_documents` - Quotes, invoices, POPs

### Production Tables
- `queue_items` - Job queue
- `laser_runs` - Completed runs
- `operators` - Machine operators
- `machine_settings_presets` - Cut parameters

### Financial Tables
- `quotes` - Customer quotes
- `quote_items` - Quote line items
- `invoices` - Customer invoices
- `invoice_items` - Invoice line items

### Inventory Tables
- `inventory_items` - Material stock
- `inventory_transactions` - Stock movements

### Communication Tables
- `communications` - All communications
- `communication_attachments` - Email attachments
- `message_templates` - Reusable templates

### System Tables
- `users` - User accounts
- `roles` - User roles
- `user_roles` - Role assignments
- `login_history` - Login tracking
- `activity_log` - Audit trail
- `settings` - System configuration

### Module N Tables
- `file_ingests` - Uploaded files (26 columns, 16 indexes)
- `file_extractions` - Raw extraction data
- `file_metadata` - Normalized metadata

---

## 🚀 Quick Tips

### Performance
- Use search filters to narrow results
- Dashboard uses eager loading for speed
- Pagination limits results to 50 per page

### Best Practices
- Always link communications to clients/projects
- Use message templates for common messages
- Set realistic estimated cut times for queue planning
- Record POP immediately when received
- Review low stock alerts weekly

### Shortcuts
- Click on statistic cards to filter views
- Use "Create from Quote" for invoices
- Use templates for faster communication
- Drag-and-drop for queue reordering

### Troubleshooting
- Check Activity Log for recent changes
- Verify Module N is running (health check)
- Check webhook queue for failed events
- Review login history for access issues

---

## 📞 Support & Documentation

### Full Documentation
- **Detailed Features:** `docs/DETAILED_FEATURE_CAPABILITIES.md`
- **Technical Review:** `docs/COMPREHENSIVE_APPLICATION_REVIEW.md`
- **Executive Summary:** `docs/EXECUTIVE_SUMMARY.md`
- **Testing Results:** `docs/MODULE_N_REAL_WORLD_TESTING_COMPLETE.md`
- **Module N Docs:** `module_n/README.md`

### Configuration Files
- **Laser OS Config:** `config.py` + `.env`
- **Module N Config:** `module_n/config.py` + `.env.module_n`

### Key Settings
- `MODULE_N_ENABLED` - Enable/disable Module N integration
- `MODULE_N_URL` - Module N service URL (default: http://localhost:8081)
- `AUTO_QUEUE_ON_POP` - Auto-add to queue when POP received
- `WEBHOOK_SECRET` - HMAC signature secret for security
- `WEBHOOK_RETRY_ATTEMPTS` - Number of retry attempts (default: 3)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-21  
**Prepared By:** Augment Agent

