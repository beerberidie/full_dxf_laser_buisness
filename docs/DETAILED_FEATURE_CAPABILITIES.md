# Laser OS & Module N - Detailed Feature Capabilities

**Document Version:** 1.0  
**Last Updated:** 2025-10-21  
**Purpose:** Comprehensive reference for all application features, workflows, and capabilities

---

## 📋 Table of Contents

1. [Client & Project Management](#1-client--project-management)
2. [Intelligent File Processing](#2-intelligent-file-processing)
3. [Financial Operations](#3-financial-operations)
4. [Production Operations](#4-production-operations)
5. [Inventory & Materials](#5-inventory--materials)
6. [Communications](#6-communications)
7. [Reporting & Analytics](#7-reporting--analytics)
8. [System Administration](#8-system-administration)

---

## 1. CLIENT & PROJECT MANAGEMENT

### 1.1 Client Management

#### **Feature Description**
Complete customer relationship management system for tracking laser cutting clients. Manages client information, contact details, and provides a centralized hub for all client-related activities.

#### **What the User Sees**
- **Client List Page:** Searchable, paginated list of all clients with quick filters
- **Client Detail Page:** Complete client profile with contact information, project history, and communication logs
- **Client Form:** Simple form for creating/editing client records
- **Search Functionality:** Real-time search across client name, code, contact person, and email

#### **User Workflow**

**Creating a New Client:**
1. User clicks "New Client" button
2. Fills in client information:
   - Company name (required)
   - Contact person name
   - Email address
   - Phone number
   - Physical/postal address
   - Additional notes
3. Clicks "Save"
4. System auto-generates unique client code (CL-0001, CL-0002, etc.)
5. Client is created and user is redirected to client detail page

**Viewing Client History:**
1. User clicks on client name from list
2. System displays:
   - Client information
   - All projects for this client
   - Recent communications
   - Quote and invoice history
   - Total business value

**Searching for Clients:**
1. User types search term in search box
2. System searches across:
   - Client code (CL-xxxx)
   - Company name
   - Contact person
   - Email address
3. Results update in real-time

#### **Technical Implementation**

**Database Schema:**
```sql
Table: clients
- id (Primary Key)
- client_code (Unique, Indexed, Format: CL-xxxx)
- name (Company name)
- contact_person
- email
- phone
- address (Text)
- notes (Text)
- created_at (Timestamp)
- updated_at (Timestamp)
```

**Key Components:**
- **Route:** `/clients` (Blueprint: `clients`)
- **Model:** `Client` (SQLAlchemy ORM)
- **Service:** `id_generator.generate_client_code()`
- **Templates:** `clients/list.html`, `clients/form.html`, `clients/detail.html`

**Code Generation Logic:**
```python
def generate_client_code():
    # Find highest existing code
    last_client = Client.query.order_by(Client.id.desc()).first()
    next_num = (last_client.id + 1) if last_client else 1
    return f"CL-{next_num:04d}"  # CL-0001, CL-0002, etc.
```

#### **Data Flow**
```
User Input → Form Validation → Generate Client Code → 
Create Database Record → Log Activity → Redirect to Detail Page
```

#### **Business Value**
- **Centralized Customer Data:** All client information in one place
- **Quick Access:** Fast search and retrieval of client records
- **Audit Trail:** Automatic tracking of creation and updates
- **Relationship Tracking:** See all projects and communications for each client
- **Professional Codes:** Auto-generated unique identifiers for easy reference

#### **Example Use Case**

**Scenario:** New customer "ABC Manufacturing" contacts you for laser cutting services.

**Workflow:**
1. Sales person creates new client record
2. Enters: Name="ABC Manufacturing", Contact="John Smith", Email="john@abc.com", Phone="555-1234"
3. System generates code "CL-0042"
4. Client record is created
5. Sales person can now create projects for CL-0042
6. All future quotes, invoices, and communications are linked to CL-0042

**Result:** Complete customer profile with unique identifier, ready for project creation and business operations.

---

### 1.2 Project Management

#### **Feature Description**
Comprehensive project/job management system with enhanced workflow tracking. Manages the complete lifecycle from initial request through completion, with status tracking, deadline management, and POP (Proof of Payment) integration.

#### **What the User Sees**
- **Project List Page:** Filterable list of all projects with status indicators
- **Project Detail Page:** Complete project information with files, documents, queue status, and timeline
- **Project Form:** Multi-step form for creating/editing projects
- **Status Workflow:** Visual workflow showing project progression
- **POP Tracking:** Proof of payment status and deadline warnings

#### **User Workflow**

**Creating a New Project:**
1. User clicks "New Project" from projects page or client detail page
2. Selects client from dropdown (or pre-selected if from client page)
3. Fills in project details:
   - Project name/description
   - Detailed description
   - Initial status (Request, Quote & Approval, etc.)
   - Due date
   - Quoted price
   - Notes
4. Clicks "Save"
5. System auto-generates project code: `JB-YYYY-MM-CLxxxx-###`
   - JB = Job prefix
   - YYYY = Year (2025)
   - MM = Month (10)
   - CLxxxx = Client code (CL0001)
   - ### = Sequential number (001, 002, etc.)
6. Project is created and user is redirected to project detail page

**Project Workflow Progression:**
1. **Request** → Initial customer inquiry
2. **Quote & Approval** → Quote sent, awaiting approval
3. **Approved (POP Received)** → Customer approved and paid deposit
   - System sets `pop_received = True`
   - System calculates `pop_deadline = pop_received_date + 3 days`
4. **Queued (Scheduled for Cutting)** → Added to production queue
5. **In Progress** → Currently being cut
6. **Completed** → Job finished
7. **Cancelled** → Job cancelled

**POP Deadline Management:**
1. When POP is marked as received:
   - System records `pop_received_date`
   - System calculates deadline (3 business days)
   - System shows warning if not scheduled by deadline
2. When adding to queue:
   - System checks if POP deadline passed
   - Shows warning: "⚠️ Warning: POP deadline was X day(s) ago"
   - Allows scheduling but highlights urgency

**Viewing Project Details:**
1. User clicks on project code from list
2. System displays:
   - Project information and status
   - Client details (linked)
   - Design files uploaded
   - Project documents (quotes, invoices, POPs)
   - Queue status (if scheduled)
   - Laser run history (if completed)
   - Activity timeline
   - POP status and deadline (if applicable)

#### **Technical Implementation**

**Database Schema:**
```sql
Table: projects
- id (Primary Key)
- project_code (Unique, Indexed, Format: JB-YYYY-MM-CLxxxx-###)
- client_id (Foreign Key → clients.id)
- name (Project name)
- description (Text)
- status (Enum: Request, Quote & Approval, Approved (POP Received), 
         Queued, In Progress, Completed, Cancelled)
- quote_date
- approval_date
- due_date
- completion_date
- quoted_price (Decimal)
- final_price (Decimal)
- pop_received (Boolean)
- pop_received_date (Date)
- pop_deadline (Date, Indexed)
- notes (Text)
- created_at (Timestamp)
- updated_at (Timestamp)
```

**Key Components:**
- **Route:** `/projects` (Blueprint: `projects`)
- **Model:** `Project` (SQLAlchemy ORM)
- **Service:** `id_generator.generate_project_code(client_id)`
- **Templates:** `projects/list.html`, `projects/form.html`, `projects/detail.html`

**Project Code Generation:**
```python
def generate_project_code(client_id):
    client = Client.query.get(client_id)
    year = datetime.now().year
    month = datetime.now().month
    
    # Find highest sequential number for this client/month
    prefix = f"JB-{year}-{month:02d}-{client.client_code}-"
    last_project = Project.query.filter(
        Project.project_code.like(f"{prefix}%")
    ).order_by(Project.id.desc()).first()
    
    next_num = 1
    if last_project:
        # Extract number from code
        parts = last_project.project_code.split('-')
        next_num = int(parts[-1]) + 1
    
    return f"{prefix}{next_num:03d}"
    # Example: JB-2025-10-CL0001-001
```

**Status Constants:**
```python
class Project(db.Model):
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
```

#### **Data Flow**

**Project Creation:**
```
User Input → Validate Client → Generate Project Code → 
Create Database Record → Log Activity → Redirect to Detail Page
```

**POP Workflow:**
```
Mark POP Received → Set pop_received=True → 
Record pop_received_date → Calculate pop_deadline (+3 days) → 
Update Database → Show Deadline Warning in UI
```

**Status Progression:**
```
Request → Quote & Approval → Approved (POP Received) → 
Queued → In Progress → Completed
```

#### **Integration Points**
- **Clients:** Each project linked to one client
- **Files:** Design files uploaded to projects
- **Documents:** Quotes, invoices, POPs attached to projects
- **Queue:** Projects added to production queue
- **Laser Runs:** Completed runs linked to projects
- **Communications:** Messages linked to projects
- **Module N:** File processing triggered for project files

#### **Business Value**
- **Complete Lifecycle Tracking:** From inquiry to completion
- **Automated Code Generation:** Professional, unique identifiers
- **POP Deadline Management:** Ensures timely scheduling (3-day SLA)
- **Status Visibility:** Clear workflow progression
- **Client Relationship:** All projects linked to clients
- **Audit Trail:** Complete history of project changes
- **Deadline Warnings:** Proactive alerts for overdue scheduling

#### **Example Use Case**

**Scenario:** Client "ABC Manufacturing" (CL-0042) requests laser cutting for 50 brackets.

**Complete Workflow:**
1. **Day 1 - Request:**
   - Sales creates project: "50x Steel Brackets"
   - Code generated: `JB-2025-10-CL0042-001`
   - Status: "Request"
   - Due date: 2025-10-30

2. **Day 2 - Quote:**
   - Sales creates quote for R5,000
   - Updates project status: "Quote & Approval"
   - Sends quote to client

3. **Day 5 - Approval:**
   - Client approves and pays R2,500 deposit
   - Sales uploads POP document
   - Marks POP as received (date: 2025-10-05)
   - System calculates deadline: 2025-10-08
   - Status: "Approved (POP Received)"

4. **Day 6 - Scheduling:**
   - Production manager adds to queue
   - System checks: POP deadline is 2025-10-08 (2 days away)
   - No warning shown (within deadline)
   - Status: "Queued (Scheduled for Cutting)"

5. **Day 7 - Production:**
   - Operator starts cutting
   - Status: "In Progress"

6. **Day 8 - Completion:**
   - Operator marks run as complete
   - Status: "Completed"
   - Invoice generated

**Result:** Complete project lifecycle tracked with automated code generation, POP deadline management, and status progression.

---

## 2. INTELLIGENT FILE PROCESSING

### 2.1 File Upload & Management

#### **Feature Description**
Integrated file upload system with intelligent processing powered by Module N. Supports DXF, LightBurn (.lbrn2), PDF, Excel, and image files with automatic metadata extraction.

#### **What the User Sees**
- **Upload Interface:** Drag-and-drop or click-to-browse file upload
- **Multi-file Support:** Upload multiple files simultaneously
- **File List:** All files for a project with metadata
- **Processing Status:** Real-time status updates (Pending, Processing, Completed, Failed)
- **Extracted Metadata:** Material, thickness, dimensions, quantity, cut settings
- **Download/Preview:** View or download uploaded files

#### **User Workflow**

**Uploading Files to a Project:**
1. User navigates to project detail page
2. Clicks "Upload Files" button
3. Selects one or more files:
   - DXF files (AutoCAD drawings)
   - LBRN2 files (LightBurn projects)
   - PDF files (drawings, cut lists)
   - Excel files (part lists, BOMs)
   - Image files (photos, scanned drawings)
4. Optionally adds notes
5. Clicks "Upload"
6. System processes files:
   - **Without Module N:** Files stored, basic info recorded
   - **With Module N:** Files sent for intelligent processing

**Module N Processing Flow:**
1. Files uploaded to Laser OS
2. Laser OS forwards files to Module N via HTTP POST
3. Module N validates file type and size
4. Module N selects appropriate parser:
   - **DXF Parser:** Extracts layers, entities, dimensions, holes, material hints
   - **LightBurn Parser:** Extracts cut settings, layers, shapes, material height
   - **PDF Parser:** Extracts text, tables, metadata, embedded images
   - **Excel Parser:** Extracts sheets, rows, columns, detects schema
   - **Image Parser:** Performs OCR, extracts EXIF data, dimensions
5. Module N saves to database:
   - `file_ingests` table (file info, status)
   - `file_extractions` table (raw extraction data)
   - `file_metadata` table (normalized key-value pairs)
6. Module N stores file with versioning:
   - Path: `{client_code}/{project_code}/filename`
   - Collision handling: `-v1`, `-v2`, `-v3`
7. Module N sends webhook to Laser OS:
   - Event type: `file.processed`
   - Payload: File info + extracted metadata
8. Laser OS receives webhook:
   - Verifies HMAC-SHA256 signature
   - Creates/updates DesignFile record
   - Logs activity
9. User sees processed file with metadata

**Viewing File Details:**
1. User clicks on filename from project page
2. System displays:
   - Original filename
   - File type and size
   - Upload date and user
   - Processing status
   - Extracted metadata (if processed by Module N):
     - Material type (e.g., "Mild Steel")
     - Thickness (e.g., "5mm")
     - Dimensions (width × height)
     - Quantity (if detected)
     - Cut settings (for LightBurn files)
     - Layers and entities (for DXF files)
   - Download button
   - Re-extract button (to re-run processing)

#### **Technical Implementation**

**Laser OS Components:**

**Database Schema:**
```sql
Table: design_files
- id (Primary Key)
- project_id (Foreign Key → projects.id)
- original_filename
- stored_filename
- file_path (Relative path)
- file_size (Bytes)
- file_type (dxf, lbrn2, pdf, excel, image)
- uploaded_by
- upload_date (Timestamp)
- notes (Text)
```

**Key Components:**
- **Route:** `/files/upload/<project_id>` (Blueprint: `files`)
- **Model:** `DesignFile` (SQLAlchemy ORM)
- **Service:** `ModuleNClient` (HTTP client for Module N)
- **Webhook Receiver:** `/webhooks/module-n/event`

**Module N Components:**

**Database Schema:**
```sql
Table: file_ingests (26 columns, 16 indexes)
- id (Primary Key)
- project_id, client_id (Optional foreign keys)
- original_filename, stored_filename
- file_path (Full path to stored file)
- file_size, file_type
- status (pending, processing, completed, failed)
- processing_mode (AUTO, dxf, lbrn2, pdf, excel, image)
- client_code, project_code (Extracted from filename)
- material_type, thickness_mm, quantity
- width_mm, height_mm, depth_mm
- is_deleted (Soft delete flag)
- created_at, updated_at, processed_at

Table: file_extractions
- id (Primary Key)
- file_ingest_id (Foreign Key → file_ingests.id)
- extraction_type (Parser type used)
- extracted_data (JSON - raw extraction results)
- extraction_date (Timestamp)

Table: file_metadata
- id (Primary Key)
- file_ingest_id (Foreign Key → file_ingests.id)
- metadata_key (e.g., "material_type", "thickness")
- metadata_value (e.g., "Mild Steel", "5")
- data_type (string, number, boolean, date)
```

**File Parsers:**

**1. DXF Parser** (`module_n/parsers/dxf_parser.py`)
```python
Extracts:
- Layers (names, colors, counts)
- Entities (lines, circles, arcs, polylines, splines)
- Bounding box (width, height)
- Holes (count, diameters)
- Material hints (from layer names or text)
- Thickness hints (from text or attributes)
- Part count (from text or patterns)

Technology: ezdxf library
```

**2. LightBurn Parser** (`module_n/parsers/lbrn_parser.py`)
```python
Extracts:
- Cut settings (power, speed, passes)
- Layers (names, colors, operations)
- Shapes (count, types)
- Material height
- Job origin
- Estimated cut time

Technology: XML parsing (LBRN2 is XML-based)
```

**3. PDF Parser** (`module_n/parsers/pdf_parser.py`)
```python
Extracts:
- Text content (full text extraction)
- Tables (structured data)
- Metadata (author, title, creation date)
- Embedded images
- Page count

Technology: PyMuPDF, camelot-py, tabula-py
```

**4. Excel Parser** (`module_n/parsers/excel_parser.py`)
```python
Extracts:
- Sheet names
- Headers (first row detection)
- Data rows (up to 1000 rows for performance)
- Schema detection (column types)
- Cell values

Technology: pandas, openpyxl, xlrd
```

**5. Image Parser** (`module_n/parsers/image_parser.py`)
```python
Extracts:
- Image dimensions (width, height)
- EXIF data (camera, date, GPS)
- OCR text (requires Tesseract)
- File format

Technology: Pillow, pytesseract
```

**Filename Standardization:**

Module N can generate standardized filenames:
```
Format: {ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}

Example: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x10-v1.dxf

Components:
- ClientCode: CL0001
- ProjectCode: JB-2025-10-CL0001-001
- PartName: BracketLeft
- Material: MS (Mild Steel)
- Thickness: 5mm
- Quantity: x10
- Version: v1
- Extension: .dxf
```

**Material Codes:**
- MS = Mild Steel
- SS = Stainless Steel
- GALV = Galvanized Steel
- AL = Aluminum
- BR = Brass
- CU = Copper
- CS = Carbon Steel
- VAST = Vastrap
- ZN = Zinc
- OTH = Other

#### **Data Flow**

**File Upload with Module N:**
```
User Uploads File → Laser OS Receives →
Forward to Module N (/ingest) →
Module N Validates → Select Parser →
Extract Metadata → Save to Database →
Store File with Versioning →
Generate Webhook Event →
Send to Laser OS (/webhooks/module-n/event) →
Laser OS Verifies Signature →
Create/Update DesignFile →
Log Activity → User Sees Processed File
```

**Webhook Event Types:**
1. `file.ingested` - File uploaded and validated
2. `file.processed` - File parsed and metadata extracted
3. `file.failed` - File processing failed
4. `file.re_extracted` - File re-extracted with updated metadata
5. `file.deleted` - File deleted from Module N

**Webhook Payload Example:**
```json
{
  "event_type": "file.processed",
  "timestamp": "2025-10-21T14:30:00Z",
  "file_data": {
    "ingest_id": 123,
    "original_filename": "bracket.dxf",
    "stored_filename": "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
    "file_type": "dxf",
    "file_size": 245678,
    "file_path": "CL0001/JB-2025-10-CL0001-001/bracket.dxf",
    "status": "completed",
    "client_code": "CL0001",
    "project_code": "JB-2025-10-CL0001-001",
    "material_type": "Mild Steel",
    "thickness_mm": 5.0,
    "quantity": 10,
    "width_mm": 150.5,
    "height_mm": 200.3,
    "metadata": {
      "layers": ["CUT", "ENGRAVE"],
      "entities": {"LINE": 45, "CIRCLE": 8, "ARC": 12},
      "holes": {"count": 8, "diameters": [6.0, 8.0]}
    }
  }
}
```

#### **Integration Points**
- **Projects:** Files uploaded to specific projects
- **Module N API:** HTTP POST to `/ingest` endpoint
- **Webhook System:** Real-time event notifications
- **Database:** Shared database for file records
- **File Storage:** Organized by client/project
- **Activity Log:** All file operations logged

#### **Business Value**
- **Intelligent Metadata Extraction:** Automatic detection of material, thickness, dimensions
- **Time Savings:** No manual data entry for file properties
- **Accuracy:** Consistent, automated extraction reduces errors
- **Multi-format Support:** 5 different file types supported
- **Versioning:** Automatic version control for file updates
- **Audit Trail:** Complete history of file uploads and processing
- **Real-time Processing:** Webhook notifications for instant updates
- **Scalability:** Microservice architecture allows independent scaling

#### **Example Use Case**

**Scenario:** Customer sends DXF file for 20 steel brackets, 5mm thick.

**Workflow:**
1. **Upload:**
   - User uploads `bracket_design.dxf` to project `JB-2025-10-CL0042-001`
   - File size: 245 KB

2. **Module N Processing:**
   - Validates file type: DXF ✓
   - Validates file size: 245 KB < 50 MB ✓
   - Selects DXF Parser
   - Extracts metadata:
     - Layers: CUT, ENGRAVE
     - Entities: 45 lines, 8 circles, 12 arcs
     - Bounding box: 150.5mm × 200.3mm
     - Holes: 8 holes (6mm and 8mm diameters)
     - Material hint: "MS" found in layer name
     - Thickness hint: "5mm" found in text
     - Quantity hint: "x20" found in text
   - Generates standardized filename:
     `CL0042-JB-2025-10-CL0042-001-Bracket-MS-5mm-x20-v1.dxf`
   - Stores file: `data/module_n_storage/CL0042/JB-2025-10-CL0042-001/`
   - Saves to database:
     - file_ingests: status=completed, material_type="Mild Steel", thickness_mm=5.0, quantity=20
     - file_extractions: raw DXF data in JSON
     - file_metadata: 15 key-value pairs

3. **Webhook Notification:**
   - Module N sends `file.processed` event to Laser OS
   - Payload includes all extracted metadata
   - HMAC-SHA256 signature included for security

4. **Laser OS Processing:**
   - Receives webhook
   - Verifies signature ✓
   - Creates DesignFile record:
     - Links to project JB-2025-10-CL0042-001
     - Stores metadata
   - Logs activity: "File processed by Module N"

5. **User View:**
   - User refreshes project page
   - Sees file with extracted metadata:
     - Material: Mild Steel
     - Thickness: 5mm
     - Dimensions: 150.5mm × 200.3mm
     - Quantity: 20 pieces
     - Layers: CUT, ENGRAVE
     - Holes: 8 (6mm, 8mm)
   - Can now use this data for:
     - Material estimation
     - Cut time calculation
     - Quote generation
     - Production planning

**Result:** Automatic extraction of critical manufacturing data from DXF file, eliminating manual data entry and reducing errors.

---

## 3. FINANCIAL OPERATIONS

### 3.1 Quote Management

#### **Feature Description**
Professional quote generation system with line items, tax calculation, and PDF export. Tracks quote status from draft through acceptance.

#### **What the User Sees**
- **Quote List:** All quotes with status filters (Draft, Sent, Accepted, Rejected, Expired)
- **Quote Form:** Multi-line item form with automatic calculations
- **Quote Detail:** Complete quote with client info, line items, totals
- **PDF Export:** Professional PDF quote for client delivery
- **Status Tracking:** Visual indicators for quote status

#### **User Workflow**

**Creating a Quote:**
1. User clicks "New Quote"
2. Selects client (required)
3. Optionally links to project
4. Sets quote date and validity period (default 30 days)
5. Adds line items:
   - Description (e.g., "Laser cut steel brackets")
   - Quantity (e.g., 20)
   - Unit price (e.g., R150.00)
   - Line total auto-calculated (20 × R150 = R3,000)
6. Adds multiple line items as needed
7. Sets tax rate (default 15% VAT)
8. Adds notes and terms
9. Clicks "Save"
10. System generates quote number: `QT-2025-0001`
11. System calculates:
    - Subtotal (sum of line items)
    - Tax amount (subtotal × tax rate)
    - Total (subtotal + tax)

**Sending a Quote:**
1. User opens quote detail page
2. Clicks "Export PDF"
3. System generates professional PDF with:
   - Company letterhead
   - Quote number and date
   - Client information
   - Line items table
   - Subtotal, tax, total
   - Terms and conditions
   - Validity date
4. User downloads PDF
5. User sends to client via email
6. User marks quote as "Sent"

**Quote Acceptance:**
1. Client accepts quote
2. User marks quote as "Accepted"
3. User can create invoice from quote (copies line items)
4. User can link quote to project

#### **Technical Implementation**

**Database Schema:**
```sql
Table: quotes
- id (Primary Key)
- quote_number (Unique, Format: QT-YYYY-####)
- client_id (Foreign Key → clients.id)
- project_id (Foreign Key → projects.id, Optional)
- quote_date (Date)
- valid_until (Date)
- status (Draft, Sent, Accepted, Rejected, Expired)
- subtotal (Decimal)
- tax_rate (Decimal, e.g., 15.00)
- tax_amount (Decimal)
- total (Decimal)
- notes (Text)
- terms (Text)
- created_by
- created_at, updated_at

Table: quote_items
- id (Primary Key)
- quote_id (Foreign Key → quotes.id)
- item_number (Integer, for ordering)
- description (Text)
- quantity (Decimal)
- unit_price (Decimal)
- line_total (Decimal)
```

**Key Components:**
- **Route:** `/quotes` (Blueprint: `quotes`)
- **Models:** `Quote`, `QuoteItem` (SQLAlchemy ORM)
- **PDF Generation:** WeasyPrint library
- **Templates:** `quotes/index.html`, `quotes/form.html`, `quotes/detail.html`, `quotes/pdf.html`

**Calculation Logic:**
```python
def calculate_totals(self):
    # Sum all line items
    self.subtotal = sum(item.line_total for item in self.items)

    # Calculate tax
    self.tax_amount = self.subtotal * (self.tax_rate / 100)

    # Calculate total
    self.total = self.subtotal + self.tax_amount
```

#### **Data Flow**
```
User Input → Add Line Items → Calculate Totals →
Generate Quote Number → Save to Database →
Export PDF → Send to Client → Track Status
```

#### **Business Value**
- **Professional Presentation:** PDF quotes with company branding
- **Accurate Calculations:** Automatic subtotal, tax, total
- **Status Tracking:** Know which quotes are pending, accepted, rejected
- **Validity Management:** Track quote expiration dates
- **Project Linking:** Connect quotes to projects for workflow
- **Audit Trail:** Complete history of quote changes
- **Reusability:** Create invoices from accepted quotes

#### **Example Use Case**

**Scenario:** Client requests quote for laser cutting 50 brackets and 30 plates.

**Workflow:**
1. Sales creates quote QT-2025-0042
2. Adds line items:
   - Item 1: "50x Steel Brackets (5mm)" - Qty: 50, Price: R120 = R6,000
   - Item 2: "30x Steel Plates (3mm)" - Qty: 30, Price: R80 = R2,400
3. System calculates:
   - Subtotal: R8,400
   - Tax (15%): R1,260
   - Total: R9,660
4. Exports PDF quote
5. Sends to client
6. Client accepts
7. Sales creates project and invoice from quote

**Result:** Professional quote with accurate pricing, ready for client approval.

---

### 3.2 Invoice Management

#### **Feature Description**
Complete invoicing system with payment tracking, due date management, and PDF export. Supports creating invoices from quotes or from scratch.

#### **What the User Sees**
- **Invoice List:** All invoices with status filters (Draft, Sent, Paid, Overdue, Cancelled)
- **Invoice Form:** Multi-line item form similar to quotes
- **Invoice Detail:** Complete invoice with payment status
- **PDF Export:** Professional PDF invoice for client
- **Payment Tracking:** Record payments and track balance

#### **User Workflow**

**Creating an Invoice:**
1. User clicks "New Invoice"
2. Selects client (required)
3. Optionally links to project and/or quote
4. If linked to quote:
   - Line items auto-populated from quote
   - Tax rate copied from quote
5. If creating from scratch:
   - Adds line items manually
6. Sets invoice date and payment terms (default Net 30)
7. System calculates due date (invoice date + payment days)
8. System generates invoice number: `INV-2025-0001`
9. System calculates totals (same as quotes)
10. Clicks "Save"

**Sending an Invoice:**
1. User opens invoice detail page
2. Clicks "Export PDF"
3. System generates professional PDF
4. User downloads and sends to client
5. User marks invoice as "Sent"

**Recording Payment:**
1. Client pays invoice
2. User clicks "Record Payment"
3. Enters:
   - Payment date
   - Payment amount
   - Payment method (Bank Transfer, Cash, Card, etc.)
   - Reference number
4. System updates:
   - Amount paid
   - Balance due
   - Status (Paid if balance = 0)

**Overdue Tracking:**
1. System automatically marks invoices as "Overdue" if:
   - Due date has passed
   - Balance > 0
2. Dashboard shows overdue invoice count
3. Reports show aging analysis

#### **Technical Implementation**

**Database Schema:**
```sql
Table: invoices
- id (Primary Key)
- invoice_number (Unique, Format: INV-YYYY-####)
- client_id (Foreign Key → clients.id)
- project_id (Foreign Key → projects.id, Optional)
- quote_id (Foreign Key → quotes.id, Optional)
- invoice_date (Date)
- due_date (Date)
- status (Draft, Sent, Paid, Overdue, Cancelled)
- subtotal (Decimal)
- tax_rate (Decimal)
- tax_amount (Decimal)
- total (Decimal)
- amount_paid (Decimal)
- balance_due (Decimal)
- payment_terms (Text, e.g., "Net 30")
- notes (Text)
- created_by
- created_at, updated_at

Table: invoice_items
- id (Primary Key)
- invoice_id (Foreign Key → invoices.id)
- item_number (Integer)
- description (Text)
- quantity (Decimal)
- unit_price (Decimal)
- line_total (Decimal)
```

**Key Components:**
- **Route:** `/invoices` (Blueprint: `invoices`)
- **Models:** `Invoice`, `InvoiceItem` (SQLAlchemy ORM)
- **PDF Generation:** WeasyPrint library
- **Templates:** `invoices/index.html`, `invoices/form.html`, `invoices/detail.html`, `invoices/pdf.html`

**Payment Tracking:**
```python
def record_payment(self, amount, payment_date, method, reference):
    self.amount_paid += amount
    self.balance_due = self.total - self.amount_paid

    if self.balance_due <= 0:
        self.status = 'Paid'

    # Create payment record
    payment = Payment(
        invoice_id=self.id,
        amount=amount,
        payment_date=payment_date,
        payment_method=method,
        reference=reference
    )
    db.session.add(payment)
```

#### **Data Flow**
```
Create Invoice → Link to Quote/Project →
Add Line Items → Calculate Totals →
Generate Invoice Number → Save to Database →
Export PDF → Send to Client →
Record Payment → Update Status
```

#### **Integration Points**
- **Quotes:** Create invoices from accepted quotes
- **Projects:** Link invoices to projects
- **Clients:** All invoices linked to clients
- **Payments:** Track payment history
- **Reports:** Financial reporting and aging analysis

#### **Business Value**
- **Professional Invoicing:** PDF invoices with company branding
- **Payment Tracking:** Know exactly what's owed
- **Overdue Management:** Automatic overdue detection
- **Quote Integration:** Quick invoice creation from quotes
- **Audit Trail:** Complete payment history
- **Financial Reporting:** Track revenue and outstanding balances

#### **Example Use Case**

**Scenario:** Quote QT-2025-0042 accepted, create invoice.

**Workflow:**
1. User creates invoice from quote
2. System generates INV-2025-0042
3. Line items copied from quote:
   - 50x Steel Brackets: R6,000
   - 30x Steel Plates: R2,400
   - Subtotal: R8,400
   - Tax: R1,260
   - Total: R9,660
4. Invoice date: 2025-10-21
5. Payment terms: Net 30
6. Due date: 2025-11-20
7. Export PDF and send to client
8. Client pays R9,660 on 2025-11-15
9. User records payment
10. Status updated to "Paid"

**Result:** Complete invoice lifecycle from quote to payment, with full tracking.

---

## 4. PRODUCTION OPERATIONS

### 4.1 Job Queue & Scheduling

#### **Feature Description**
Production queue management system for scheduling laser cutting jobs. Supports priority management, estimated cut times, and automatic queue addition when POP is received.

#### **What the User Sees**
- **Queue Dashboard:** Visual queue with drag-and-drop reordering
- **Queue Items:** Each item shows project, priority, scheduled date, estimated time
- **Status Indicators:** Queued, In Progress, Completed
- **Statistics:** Total queued, in progress, completed counts
- **POP Deadline Warnings:** Visual alerts for projects approaching deadline

#### **User Workflow**

**Adding Project to Queue:**
1. User navigates to project detail page
2. Clicks "Add to Queue" button
3. Fills in queue details:
   - Priority (Low, Normal, High, Urgent)
   - Scheduled date (default: today or next business day)
   - Estimated cut time (minutes)
   - Notes
4. System validates:
   - Project not already in queue
   - POP deadline check (if applicable)
5. System assigns queue position (next available)
6. Clicks "Add to Queue"
7. Project status updated to "Queued (Scheduled for Cutting)"

**Automatic Queue Addition (POP Workflow):**
1. User marks POP as received on project
2. System checks configuration: `AUTO_QUEUE_ON_POP = true`
3. System automatically adds to queue with:
   - Priority: Normal (configurable default)
   - Scheduled date: Today or next business day
   - Estimated cut time: From project or default
   - Notes: "Auto-queued on POP receipt"
4. Project status updated to "Queued"
5. User notified: "Project automatically added to queue"

**Managing Queue:**
1. User views queue dashboard
2. Can filter by:
   - Status (Active, Queued, In Progress, Completed)
   - Priority
   - Scheduled date
3. Can reorder queue items (drag-and-drop or position number)
4. Can edit queue item details
5. Can remove from queue

**Starting Production:**
1. Operator views queue
2. Selects next item to cut
3. Clicks "Start Production"
4. System updates:
   - Queue item status: "In Progress"
   - Project status: "In Progress"
   - Start time recorded
5. Operator performs cutting

**Completing Production:**
1. Operator finishes cutting
2. Clicks "Complete"
3. Fills in laser run details:
   - Actual cut time
   - Material used
   - Parts produced
   - Operator name
   - Notes
4. System creates LaserRun record
5. System updates:
   - Queue item status: "Completed"
   - Project status: "Completed" (if all queue items done)
   - Completion time recorded
6. System updates inventory (material consumption)

#### **Technical Implementation**

**Database Schema:**
```sql
Table: queue_items
- id (Primary Key)
- project_id (Foreign Key → projects.id)
- queue_position (Integer, for ordering)
- priority (Low, Normal, High, Urgent)
- status (Queued, In Progress, Completed, Cancelled)
- scheduled_date (Date)
- estimated_cut_time (Integer, minutes)
- actual_cut_time (Integer, minutes)
- notes (Text)
- added_by
- started_at (Timestamp)
- completed_at (Timestamp)
- created_at, updated_at

Table: laser_runs
- id (Primary Key)
- project_id (Foreign Key → projects.id)
- queue_item_id (Foreign Key → queue_items.id)
- run_date (Date)
- operator (String)
- material_type (String)
- material_thickness (Decimal)
- sheet_count (Integer)
- parts_produced (Integer)
- cut_time_minutes (Integer)
- notes (Text)
- created_at
```

**Key Components:**
- **Route:** `/queue` (Blueprint: `queue`)
- **Models:** `QueueItem`, `LaserRun` (SQLAlchemy ORM)
- **Templates:** `queue/index.html`, `queue/form.html`, `queue/detail.html`

**Priority Constants:**
```python
class QueueItem(db.Model):
    PRIORITY_LOW = 'Low'
    PRIORITY_NORMAL = 'Normal'
    PRIORITY_HIGH = 'High'
    PRIORITY_URGENT = 'Urgent'

    STATUS_QUEUED = 'Queued'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'
```

**Auto-Queue Logic:**
```python
def mark_pop_received(project, pop_date):
    project.pop_received = True
    project.pop_received_date = pop_date
    project.pop_deadline = pop_date + timedelta(days=3)
    project.status = Project.STATUS_APPROVED_POP

    # Auto-queue if enabled
    if current_app.config.get('AUTO_QUEUE_ON_POP', False):
        add_to_queue_automatically(project)

    db.session.commit()

def add_to_queue_automatically(project):
    # Get next queue position
    max_position = db.session.query(func.max(QueueItem.queue_position)).scalar() or 0

    # Get defaults from config
    priority = current_app.config.get('DEFAULT_QUEUE_PRIORITY', 'Normal')
    scheduled_date = date.today()
    estimated_time = project.estimated_cut_time or 60  # Default 60 minutes

    queue_item = QueueItem(
        project_id=project.id,
        queue_position=max_position + 1,
        priority=priority,
        status=QueueItem.STATUS_QUEUED,
        scheduled_date=scheduled_date,
        estimated_cut_time=estimated_time,
        notes="Auto-queued on POP receipt",
        added_by="System"
    )

    db.session.add(queue_item)
    project.status = Project.STATUS_QUEUED
```

#### **Data Flow**

**Manual Queue Addition:**
```
User Clicks "Add to Queue" → Fill Form →
Validate (POP deadline, duplicates) →
Assign Queue Position → Create QueueItem →
Update Project Status → Log Activity
```

**Automatic Queue Addition:**
```
Mark POP Received → Check AUTO_QUEUE_ON_POP →
Calculate Defaults (priority, date, time) →
Assign Queue Position → Create QueueItem →
Update Project Status → Notify User
```

**Production Flow:**
```
Start Production → Update Status to "In Progress" →
Operator Cuts → Complete Production →
Fill Laser Run Details → Create LaserRun Record →
Update Queue Item to "Completed" →
Update Project Status → Update Inventory
```

#### **Integration Points**
- **Projects:** Queue items linked to projects
- **Laser Runs:** Completed queue items create laser runs
- **Inventory:** Material consumption tracked
- **Operators:** Operator assignments
- **Presets:** Machine settings linked to runs
- **POP Workflow:** Automatic queue addition

#### **Business Value**
- **Organized Production:** Clear queue of jobs to cut
- **Priority Management:** Urgent jobs can be prioritized
- **Deadline Tracking:** POP deadline warnings prevent delays
- **Automatic Scheduling:** Auto-queue on POP saves time
- **Accurate Planning:** Estimated cut times for scheduling
- **Performance Tracking:** Actual vs. estimated time analysis
- **Operator Accountability:** Track who cut what and when

#### **Example Use Case**

**Scenario:** Project JB-2025-10-CL0042-001 approved with POP received.

**Automatic Queue Workflow:**
1. **POP Receipt:**
   - User marks POP received on 2025-10-21
   - System sets pop_deadline = 2025-10-24 (3 days)
   - System checks AUTO_QUEUE_ON_POP = true

2. **Auto-Queue:**
   - System creates queue item:
     - Priority: Normal
     - Scheduled date: 2025-10-21 (today)
     - Estimated time: 45 minutes (from project)
     - Queue position: 5 (next available)
     - Notes: "Auto-queued on POP receipt"
   - Project status: "Queued (Scheduled for Cutting)"
   - User sees notification: "✓ Project automatically added to queue"

3. **Production:**
   - Operator views queue on 2025-10-21
   - Sees project at position 5
   - Starts production at 14:00
   - Completes at 14:42 (42 minutes actual)
   - Fills laser run:
     - Material: Mild Steel 5mm
     - Sheets used: 2
     - Parts produced: 50
     - Operator: John Smith

4. **Completion:**
   - System creates LaserRun record
   - Queue item status: "Completed"
   - Project status: "Completed"
   - Inventory updated: -2 sheets of MS 5mm
   - Activity logged

**Result:** Seamless workflow from POP receipt to production completion with automatic scheduling and tracking.

---

### 4.2 Machine Settings & Presets

#### **Feature Description**
Library of machine settings presets for different materials and thicknesses. Stores cut parameters (power, speed, frequency) for consistent, repeatable results.

#### **What the User Sees**
- **Preset Library:** Searchable list of all presets
- **Preset Detail:** Complete cut parameters for material/thickness combination
- **Quick Selection:** Select preset when creating laser run
- **Import/Export:** Bulk import from LightBurn or other sources

#### **User Workflow**

**Using a Preset:**
1. Operator starts laser run
2. Selects material and thickness
3. System suggests matching presets
4. Operator selects preset
5. Cut parameters auto-filled:
   - Laser power (%)
   - Cut speed (mm/s)
   - Frequency (Hz)
   - Number of passes
   - Focus height
6. Operator can adjust if needed
7. Starts cutting with preset parameters

**Creating a Preset:**
1. User clicks "New Preset"
2. Fills in details:
   - Material type (Mild Steel, Stainless, Aluminum, etc.)
   - Thickness (mm)
   - Cut power (%)
   - Cut speed (mm/s)
   - Frequency (Hz)
   - Passes
   - Focus height (mm)
   - Notes
3. Saves preset
4. Available for future use

#### **Technical Implementation**

**Database Schema:**
```sql
Table: machine_settings_presets
- id (Primary Key)
- material_type (String)
- thickness_mm (Decimal)
- cut_power_percent (Decimal)
- cut_speed_mm_s (Decimal)
- frequency_hz (Integer)
- passes (Integer)
- focus_height_mm (Decimal)
- notes (Text)
- created_at, updated_at
```

**Key Components:**
- **Route:** `/presets` (Blueprint: `presets`)
- **Model:** `MachineSettingsPreset` (SQLAlchemy ORM)
- **Import:** Bulk import from CSV or LightBurn library

#### **Business Value**
- **Consistency:** Same settings every time for same material
- **Quality:** Proven parameters for good cuts
- **Time Savings:** No trial-and-error for common materials
- **Knowledge Base:** Preserve institutional knowledge
- **Training:** New operators can use proven settings

---

## 5. INVENTORY & MATERIALS

### 5.1 Inventory Management

#### **Feature Description**
Complete inventory tracking system for materials, consumables, and tools. Tracks stock levels, consumption, reorder points, and supplier information.

#### **What the User Sees**
- **Inventory Dashboard:** All items with stock levels and values
- **Low Stock Alerts:** Visual indicators for items below reorder level
- **Item Detail:** Complete item information with transaction history
- **Stock Adjustments:** Add, remove, or adjust stock quantities
- **Categories:** Sheet Metal, Gas, Consumables, Tools, Other

#### **User Workflow**

**Adding Inventory Item:**
1. User clicks "New Item"
2. Fills in details:
   - Item code (e.g., "MS-5MM-1220X2440")
   - Name (e.g., "Mild Steel 5mm Sheet")
   - Category (Sheet Metal)
   - Material type (Mild Steel)
   - Thickness (5mm)
   - Unit (Sheet, Kg, Liter, Piece)
   - Quantity on hand (10 sheets)
   - Reorder level (3 sheets)
   - Reorder quantity (10 sheets)
   - Unit cost (R850.00)
   - Supplier name and contact
   - Storage location
3. Saves item
4. Item appears in inventory list

**Stock Adjustment:**
1. User opens item detail
2. Clicks "Adjust Stock"
3. Selects transaction type:
   - **Purchase:** Adding new stock
   - **Consumption:** Material used in production
   - **Adjustment:** Correction or count adjustment
   - **Return:** Material returned to supplier
   - **Waste:** Damaged or scrapped material
4. Enters quantity and notes
5. System updates:
   - Quantity on hand
   - Transaction history
   - Stock value

**Automatic Consumption (from Laser Run):**
1. Operator completes laser run
2. Enters material used: "2 sheets of MS 5mm"
3. System finds matching inventory item
4. System creates consumption transaction:
   - Type: Consumption
   - Quantity: -2
   - Reference: Laser Run #123
   - Notes: "Used in project JB-2025-10-CL0042-001"
5. System updates quantity on hand: 10 → 8
6. System checks reorder level: 8 > 3 (OK)

**Low Stock Alert:**
1. Quantity drops to or below reorder level
2. Item flagged with low stock indicator
3. Dashboard shows low stock count
4. User can generate purchase order

#### **Technical Implementation**

**Database Schema:**
```sql
Table: inventory_items
- id (Primary Key)
- item_code (Unique, Indexed)
- name (String)
- category (Sheet Metal, Gas, Consumables, Tools, Other)
- material_type (String)
- thickness_mm (Decimal, nullable)
- unit (Sheet, Kg, Liter, Piece, etc.)
- quantity_on_hand (Decimal)
- reorder_level (Decimal)
- reorder_quantity (Decimal)
- unit_cost (Decimal)
- supplier_name (String)
- supplier_contact (String)
- location (String)
- notes (Text)
- created_at, updated_at

Table: inventory_transactions
- id (Primary Key)
- inventory_item_id (Foreign Key → inventory_items.id)
- transaction_type (Purchase, Consumption, Adjustment, Return, Waste)
- quantity (Decimal, positive or negative)
- unit_cost (Decimal)
- total_cost (Decimal)
- reference_type (LaserRun, Project, PurchaseOrder, etc.)
- reference_id (Integer)
- notes (Text)
- transaction_date (Date)
- created_by
- created_at
```

**Key Components:**
- **Route:** `/inventory` (Blueprint: `inventory`)
- **Models:** `InventoryItem`, `InventoryTransaction` (SQLAlchemy ORM)
- **Service:** `inventory_service.py` (consumption tracking)
- **Templates:** `inventory/index.html`, `inventory/form.html`, `inventory/detail.html`

**Low Stock Detection:**
```python
@property
def is_low_stock(self):
    """Check if item is at or below reorder level"""
    return self.quantity_on_hand <= self.reorder_level

@property
def stock_value(self):
    """Calculate total value of stock on hand"""
    return self.quantity_on_hand * self.unit_cost
```

#### **Data Flow**

**Stock Adjustment:**
```
User Adjusts Stock → Create Transaction Record →
Update Quantity on Hand → Check Reorder Level →
Flag Low Stock if Needed → Log Activity
```

**Automatic Consumption:**
```
Complete Laser Run → Extract Material Used →
Find Inventory Item → Create Consumption Transaction →
Update Quantity → Check Reorder Level → Update Dashboard
```

#### **Integration Points**
- **Laser Runs:** Automatic material consumption tracking
- **Projects:** Link material usage to projects
- **Suppliers:** Track supplier information
- **Reports:** Inventory value and usage reports
- **Purchase Orders:** Generate POs for low stock items

#### **Business Value**
- **Stock Visibility:** Always know what's in stock
- **Cost Tracking:** Track material costs and consumption
- **Reorder Automation:** Alerts when stock is low
- **Waste Reduction:** Track and minimize waste
- **Supplier Management:** Centralized supplier information
- **Financial Reporting:** Inventory value for accounting

#### **Example Use Case**

**Scenario:** Track mild steel 5mm sheet inventory.

**Workflow:**
1. **Initial Setup:**
   - Add item: "MS-5MM-1220X2440"
   - Quantity: 20 sheets
   - Reorder level: 5 sheets
   - Unit cost: R850

2. **Production Consumption:**
   - Laser run uses 3 sheets
   - System creates consumption transaction
   - Quantity: 20 → 17 sheets
   - Value: R17,000 → R14,450

3. **More Production:**
   - Another run uses 4 sheets
   - Quantity: 17 → 13 sheets

4. **Continued Use:**
   - Multiple runs over time
   - Quantity drops to 4 sheets
   - System flags: Low Stock! (4 < 5)
   - Dashboard shows alert

5. **Reorder:**
   - User sees low stock alert
   - Orders 15 sheets from supplier
   - Receives delivery
   - Creates purchase transaction: +15 sheets
   - Quantity: 4 → 19 sheets
   - Low stock flag cleared

**Result:** Complete tracking of material from purchase through consumption with automatic low stock alerts.

---

## 6. COMMUNICATIONS

### 6.1 Communication Hub

#### **Feature Description**
Unified communication management system for tracking all client interactions across email, WhatsApp, phone, and notifications. Auto-links communications to clients and projects.

#### **What the User Sees**
- **Communication List:** All communications with filters
- **Channel Views:** Dedicated pages for WhatsApp, Gmail, Outlook, Teams
- **Communication Detail:** Complete message with attachments
- **Auto-Linking:** Suggestions for linking to clients/projects
- **Templates:** Reusable message templates

#### **User Workflow**

**Recording a Communication:**
1. User clicks "New Communication"
2. Selects communication type:
   - Email
   - WhatsApp
   - Phone Call
   - SMS
   - Notification
3. Selects direction:
   - Inbound (from client)
   - Outbound (to client)
4. Fills in details:
   - From/To addresses
   - Subject
   - Message body
   - Attachments (optional)
5. Links to client and/or project:
   - Manual selection
   - Auto-suggestion based on email/phone
6. Sets status (Sent, Delivered, Read, Failed)
7. Saves communication

**Auto-Linking:**
1. User enters email address or phone number
2. System searches for matching client
3. If found, suggests: "Link to CL-0042 (ABC Manufacturing)?"
4. User confirms
5. System also suggests recent projects for that client
6. User selects project if applicable

**Using Templates:**
1. User clicks "Use Template"
2. Selects template (e.g., "Quote Sent", "POP Received", "Collection Ready")
3. System fills in message body with template
4. User customizes with project-specific details
5. Sends communication

**Viewing Communication History:**
1. User opens client detail page
2. Sees all communications for that client
3. Can filter by type, direction, date
4. Can click to view full message

#### **Technical Implementation**

**Database Schema:**
```sql
Table: communications
- id (Primary Key)
- client_id (Foreign Key → clients.id, nullable)
- project_id (Foreign Key → projects.id, nullable)
- comm_type (Email, WhatsApp, Phone, SMS, Notification)
- direction (Inbound, Outbound)
- from_address (Email or phone)
- to_address (Email or phone)
- subject (String)
- body (Text)
- status (Sent, Delivered, Read, Failed, Pending)
- is_linked (Boolean - has client/project link)
- sent_at (Timestamp)
- delivered_at (Timestamp)
- read_at (Timestamp)
- created_at, updated_at

Table: communication_attachments
- id (Primary Key)
- communication_id (Foreign Key → communications.id)
- filename (String)
- file_path (String)
- file_size (Integer)
- mime_type (String)
- created_at

Table: message_templates
- id (Primary Key)
- name (String, e.g., "Quote Sent")
- category (Quote, Invoice, Production, General)
- subject_template (String)
- body_template (Text)
- variables (JSON - available placeholders)
- created_at, updated_at
```

**Key Components:**
- **Route:** `/communications` (Blueprint: `comms`)
- **Models:** `Communication`, `CommunicationAttachment`, `MessageTemplate`
- **Service:** `communication_service.py` (auto-linking, template rendering)
- **Templates:** `comms/index.html`, `comms/form.html`, `comms/detail.html`

**Auto-Linking Logic:**
```python
def suggest_client_link(email_or_phone):
    # Search for client by email
    client = Client.query.filter(
        db.or_(
            Client.email.ilike(f'%{email_or_phone}%'),
            Client.phone.ilike(f'%{email_or_phone}%')
        )
    ).first()

    if client:
        # Get recent projects for this client
        recent_projects = Project.query.filter_by(
            client_id=client.id
        ).order_by(Project.created_at.desc()).limit(5).all()

        return {
            'client': client,
            'suggested_projects': recent_projects
        }

    return None
```

**Template Rendering:**
```python
def render_template(template, context):
    # Replace placeholders with actual values
    # {{client_name}} → ABC Manufacturing
    # {{project_code}} → JB-2025-10-CL0042-001
    # {{due_date}} → 2025-10-30

    subject = template.subject_template
    body = template.body_template

    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))

    return subject, body
```

#### **Data Flow**

**Recording Communication:**
```
User Enters Details → Auto-Link Suggestion →
User Confirms Links → Save Communication →
Save Attachments → Log Activity → Update Client/Project
```

**Template Usage:**
```
Select Template → Load Template →
Render with Context (client, project data) →
User Customizes → Send Communication →
Record in Database
```

#### **Integration Points**
- **Clients:** All communications linked to clients
- **Projects:** Communications linked to projects
- **Templates:** Reusable message templates
- **Attachments:** File storage for email attachments
- **Activity Log:** All communications logged

#### **Business Value**
- **Complete History:** All client interactions in one place
- **Auto-Linking:** Automatic association with clients/projects
- **Template Efficiency:** Reusable messages save time
- **Multi-Channel:** Track email, WhatsApp, phone, SMS
- **Audit Trail:** Complete communication history
- **Client Relationship:** Better customer service with full context

#### **Example Use Case**

**Scenario:** Client emails quote inquiry.

**Workflow:**
1. **Inbound Email:**
   - User receives email from john@abc.com
   - User creates communication record
   - Type: Email, Direction: Inbound
   - From: john@abc.com
   - Subject: "Quote request for brackets"
   - Body: "Can you quote 50 steel brackets?"

2. **Auto-Linking:**
   - System searches for john@abc.com
   - Finds client CL-0042 (ABC Manufacturing)
   - Suggests: "Link to CL-0042?"
   - User confirms
   - System suggests recent projects
   - User selects JB-2025-10-CL0042-001

3. **Response:**
   - User clicks "Reply"
   - Selects template: "Quote Sent"
   - Template renders:
     - Subject: "Quote for {{project_code}}"
     - Body: "Dear {{client_name}}, Please find attached quote..."
   - System fills: "Quote for JB-2025-10-CL0042-001"
   - User attaches PDF quote
   - Sends email

4. **Outbound Record:**
   - System creates outbound communication
   - Links to same client and project
   - Stores attachment
   - Status: Sent

5. **History:**
   - Client detail page shows both communications
   - Project detail page shows both communications
   - Complete conversation thread

**Result:** Complete communication tracking with automatic linking and template efficiency.

---

## 7. REPORTING & ANALYTICS

### 7.1 Dashboard & Statistics

#### **Feature Description**
Comprehensive dashboard providing real-time overview of business operations with key metrics, recent activity, and quick access to important information.

#### **What the User Sees**
- **Statistics Cards:** Total clients, projects, active projects, queue length, inventory items, low stock count
- **Recent Activity:** Latest clients, projects, files, queue items
- **Quick Actions:** Create new client, project, quote, invoice
- **Visual Indicators:** Color-coded status badges, progress bars
- **Alerts:** Low stock warnings, overdue invoices, POP deadlines

#### **User Workflow**

**Viewing Dashboard:**
1. User logs in
2. Dashboard loads automatically
3. User sees at-a-glance:
   - **Business Metrics:**
     - Total clients: 42
     - Total projects: 156
     - Active projects: 12
     - Queue length: 5
   - **Inventory Status:**
     - Total items: 28
     - Low stock items: 3 (highlighted in red)
   - **Recent Activity:**
     - 5 most recent clients
     - 5 most recent projects
     - 5 most recent files
     - 5 current queue items
4. User clicks on any item for details

**Quick Navigation:**
1. User clicks on statistic card (e.g., "Low Stock: 3")
2. System navigates to filtered view (inventory with low stock filter)
3. User sees only low stock items
4. Can take action (reorder, adjust)

#### **Technical Implementation**

**Dashboard Queries:**
```python
def dashboard():
    # Statistics
    total_clients = Client.query.count()
    total_projects = Project.query.count()
    active_projects = Project.query.filter(
        Project.status.in_([
            Project.STATUS_APPROVED,
            Project.STATUS_IN_PROGRESS
        ])
    ).count()
    queue_length = QueueItem.query.filter(
        QueueItem.status.in_([
            QueueItem.STATUS_QUEUED,
            QueueItem.STATUS_IN_PROGRESS
        ])
    ).count()
    inventory_count = InventoryItem.query.count()
    low_stock_count = InventoryItem.query.filter(
        InventoryItem.quantity_on_hand <= InventoryItem.reorder_level
    ).count()

    # Recent activity (with eager loading to avoid N+1 queries)
    recent_clients = Client.query.order_by(
        Client.created_at.desc()
    ).limit(5).all()

    recent_projects = Project.query.order_by(
        Project.created_at.desc()
    ).limit(5).all()

    recent_files = DesignFile.query.options(
        joinedload(DesignFile.project)
    ).order_by(
        DesignFile.upload_date.desc()
    ).limit(5).all()

    queue_items = QueueItem.query.options(
        joinedload(QueueItem.project)
    ).filter(
        QueueItem.status.in_([
            QueueItem.STATUS_QUEUED,
            QueueItem.STATUS_IN_PROGRESS
        ])
    ).order_by(QueueItem.queue_position).limit(5).all()

    return render_template('dashboard.html', ...)
```

**Key Components:**
- **Route:** `/` (Blueprint: `main`)
- **Template:** `dashboard.html`
- **Optimization:** Eager loading with `joinedload()` to prevent N+1 queries

#### **Business Value**
- **Situational Awareness:** Know business status at a glance
- **Quick Access:** Jump to important information quickly
- **Proactive Alerts:** See problems before they become critical
- **Performance Monitoring:** Track key metrics over time

---

### 7.2 Production Reports

#### **Feature Description**
Detailed production analytics showing laser run history, operator performance, material usage, and efficiency metrics.

#### **What the User Sees**
- **Production Summary:** Total runs, cut time, parts produced, sheets used
- **Date Range Filter:** Select custom date range for analysis
- **Operator Statistics:** Runs, cut time, parts per operator
- **Material Statistics:** Usage by material type
- **Run History:** Detailed list of all laser runs
- **Export:** CSV export for further analysis

#### **User Workflow**

**Viewing Production Report:**
1. User navigates to Reports → Production
2. Selects date range (default: last 30 days)
3. System displays:
   - **Summary Statistics:**
     - Total runs: 45
     - Total cut time: 2,340 minutes (39 hours)
     - Total parts: 1,250
     - Total sheets: 78
     - Average cut time per run: 52 minutes
     - Average parts per run: 28
   - **Operator Breakdown:**
     - John Smith: 20 runs, 1,100 minutes, 600 parts
     - Jane Doe: 15 runs, 800 minutes, 400 parts
     - Mike Johnson: 10 runs, 440 minutes, 250 parts
   - **Material Breakdown:**
     - Mild Steel: 30 runs, 50 sheets, 800 parts
     - Stainless Steel: 10 runs, 18 sheets, 300 parts
     - Aluminum: 5 runs, 10 sheets, 150 parts
4. User can drill down into specific runs
5. User can export to CSV for Excel analysis

#### **Technical Implementation**

**Report Queries:**
```python
def production_summary(start_date, end_date):
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

    return {
        'total_runs': total_runs,
        'total_cut_time': total_cut_time,
        'total_parts': total_parts,
        'total_sheets': total_sheets,
        'operator_stats': operator_stats,
        'material_stats': material_stats
    }
```

**Key Components:**
- **Route:** `/reports/production` (Blueprint: `reports`)
- **Template:** `reports/production.html`
- **Export:** CSV generation with Python csv module

#### **Business Value**
- **Performance Tracking:** Monitor production efficiency
- **Operator Accountability:** Track individual performance
- **Material Usage:** Understand consumption patterns
- **Cost Analysis:** Calculate production costs
- **Capacity Planning:** Forecast future capacity needs

---

### 7.3 Financial Reports

#### **Feature Description**
Financial analytics showing revenue, outstanding invoices, quote conversion rates, and aging analysis.

#### **What the User Sees**
- **Revenue Summary:** Total invoiced, paid, outstanding
- **Quote Statistics:** Total quotes, acceptance rate, average value
- **Aging Analysis:** Invoices by age (0-30, 31-60, 61-90, 90+ days)
- **Client Analysis:** Top clients by revenue
- **Export:** PDF and CSV export

#### **User Workflow**

**Viewing Financial Report:**
1. User navigates to Reports → Financial
2. Selects date range
3. System displays:
   - **Revenue Metrics:**
     - Total invoiced: R450,000
     - Total paid: R380,000
     - Outstanding: R70,000
     - Collection rate: 84%
   - **Quote Metrics:**
     - Total quotes: 65
     - Accepted: 42 (65%)
     - Rejected: 15 (23%)
     - Pending: 8 (12%)
     - Average quote value: R8,500
   - **Aging Analysis:**
     - Current (0-30 days): R35,000
     - 31-60 days: R20,000
     - 61-90 days: R10,000
     - Over 90 days: R5,000
   - **Top Clients:**
     - ABC Manufacturing: R85,000
     - XYZ Industries: R62,000
     - DEF Corp: R48,000

#### **Business Value**
- **Cash Flow Visibility:** Know what's owed and when
- **Collection Focus:** Identify overdue accounts
- **Sales Performance:** Track quote conversion
- **Client Value:** Identify top customers
- **Financial Planning:** Forecast revenue

---

## 8. SYSTEM ADMINISTRATION

### 8.1 User Management

#### **Feature Description**
Complete user authentication and authorization system with role-based access control (RBAC).

#### **What the User Sees**
- **User List:** All system users with roles
- **User Form:** Create/edit user accounts
- **Role Assignment:** Assign multiple roles to users
- **Login History:** Track user logins
- **Activity Log:** Audit trail of user actions

#### **User Workflow**

**Creating a User:**
1. Admin navigates to Admin → Users
2. Clicks "New User"
3. Fills in details:
   - Username
   - Email
   - Password
   - Full name
4. Assigns roles:
   - Admin (full access)
   - Manager (business operations)
   - Operator (production only)
   - Viewer (read-only)
5. Saves user
6. User can now log in

**Role-Based Access:**
- **Admin:** Full access to all features
- **Manager:** Create/edit clients, projects, quotes, invoices, queue
- **Operator:** View queue, create laser runs, view inventory
- **Viewer:** Read-only access to all data

#### **Technical Implementation**

**Database Schema:**
```sql
Table: users
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash (Hashed with bcrypt)
- full_name
- is_active (Boolean)
- created_at, updated_at

Table: roles
- id (Primary Key)
- name (admin, manager, operator, viewer)
- description

Table: user_roles
- id (Primary Key)
- user_id (Foreign Key → users.id)
- role_id (Foreign Key → roles.id)

Table: login_history
- id (Primary Key)
- user_id (Foreign Key → users.id)
- login_time (Timestamp)
- ip_address
- user_agent
- success (Boolean)
```

**Key Components:**
- **Route:** `/admin/users` (Blueprint: `admin`)
- **Models:** `User`, `Role`, `UserRole`, `LoginHistory`
- **Authentication:** Flask-Login extension
- **Password Hashing:** Werkzeug security (bcrypt)
- **Decorators:** `@login_required`, `@role_required('admin', 'manager')`

**Access Control:**
```python
from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            user_roles = [r.name for r in current_user.roles]
            if not any(role in user_roles for role in roles):
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage:
@bp.route('/new', methods=['GET', 'POST'])
@role_required('admin', 'manager')
def new_client():
    # Only admins and managers can create clients
    pass
```

#### **Business Value**
- **Security:** Protect sensitive business data
- **Accountability:** Track who did what and when
- **Access Control:** Limit access based on job function
- **Audit Trail:** Complete login and activity history
- **Compliance:** Meet security and audit requirements

---

### 8.2 Activity Logging

#### **Feature Description**
Comprehensive audit trail tracking all significant system actions for compliance and troubleshooting.

#### **What the User Sees**
- **Activity Log:** Chronological list of all actions
- **Filters:** By entity type, action, user, date range
- **Detail View:** Complete information about each action
- **Search:** Find specific activities

#### **User Workflow**

**Viewing Activity Log:**
1. Admin navigates to Admin → Activity Log
2. Sees recent activities:
   - "User 'john' created Client CL-0042"
   - "User 'jane' uploaded file to Project JB-2025-10-CL0042-001"
   - "User 'mike' completed Laser Run #123"
   - "System auto-queued Project JB-2025-10-CL0042-001"
3. Can filter by:
   - Entity type (Client, Project, File, Queue, etc.)
   - Action (Created, Updated, Deleted, etc.)
   - User
   - Date range
4. Can search for specific activities

#### **Technical Implementation**

**Database Schema:**
```sql
Table: activity_log
- id (Primary Key)
- entity_type (Client, Project, File, Queue, Invoice, etc.)
- entity_id (ID of the entity)
- action (CREATED, UPDATED, DELETED, UPLOADED, COMPLETED, etc.)
- details (Text description)
- user (Username or 'System')
- ip_address
- created_at (Timestamp)
```

**Logging Service:**
```python
def log_activity(entity_type, entity_id, action, details, user='System'):
    activity = ActivityLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details=details,
        user=user,
        ip_address=request.remote_addr if request else None
    )
    db.session.add(activity)
    db.session.commit()

# Usage:
log_activity(
    entity_type='PROJECT',
    entity_id=project.id,
    action='CREATED',
    details=f'Created project {project.project_code} for client {client.name}',
    user=current_user.username
)
```

**Automatic Logging:**
- Client created/updated/deleted
- Project created/updated/status changed
- File uploaded/deleted
- Queue item added/started/completed
- Invoice created/payment recorded
- Inventory adjusted
- User logged in/out

#### **Business Value**
- **Audit Trail:** Complete history of all actions
- **Troubleshooting:** Investigate issues and errors
- **Compliance:** Meet regulatory requirements
- **Accountability:** Know who did what and when
- **Security:** Detect unauthorized access or changes

---

## 9. SUMMARY & CONCLUSION

### 9.1 Complete Application Capabilities

**Laser OS + Module N** provides a comprehensive, end-to-end solution for laser cutting business automation:

**✅ Client & Project Management**
- Complete CRM with auto-generated codes
- Enhanced workflow tracking with POP deadlines
- Project lifecycle from request to completion

**✅ Intelligent File Processing**
- 5 operational file parsers (DXF, PDF, Excel, LightBurn, Image)
- Automatic metadata extraction (material, thickness, dimensions)
- Real-time webhook integration
- Standardized filename generation

**✅ Financial Operations**
- Professional quote and invoice generation
- PDF export with company branding
- Payment tracking and aging analysis
- Quote-to-invoice workflow

**✅ Production Operations**
- Job queue with priority management
- Automatic queue addition on POP receipt
- Laser run tracking with operator accountability
- Machine settings presets library

**✅ Inventory & Materials**
- Complete stock tracking
- Automatic consumption from laser runs
- Low stock alerts and reorder management
- Supplier information management

**✅ Communications**
- Unified communication hub (email, WhatsApp, phone, SMS)
- Auto-linking to clients and projects
- Reusable message templates
- Complete communication history

**✅ Reporting & Analytics**
- Real-time dashboard with key metrics
- Production reports (runs, operators, materials)
- Financial reports (revenue, aging, quotes)
- Export to CSV and PDF

**✅ System Administration**
- Role-based access control (RBAC)
- User management with login history
- Complete activity logging
- Security and audit compliance

### 9.2 Key Differentiators

1. **Intelligent File Processing:** Automatic metadata extraction saves hours of manual data entry
2. **POP Deadline Management:** 3-day SLA tracking ensures timely production
3. **Auto-Queue on POP:** Automatic scheduling reduces manual work
4. **Microservice Architecture:** Module N can scale independently
5. **Real-time Integration:** Webhook notifications for instant updates
6. **Complete Audit Trail:** Every action logged for compliance
7. **Professional Automation:** Auto-generated codes, PDFs, calculations

### 9.3 Business Impact

**Time Savings:**
- File metadata extraction: 5-10 minutes per file → Automatic
- Project code generation: Manual → Automatic
- Queue scheduling: Manual → Automatic (on POP)
- Quote/invoice creation: 30 minutes → 5 minutes (with templates)

**Error Reduction:**
- Manual data entry errors eliminated
- Consistent naming conventions
- Accurate calculations
- Standardized workflows

**Visibility:**
- Real-time dashboard
- Complete audit trail
- Communication history
- Production analytics

**Scalability:**
- Microservice architecture
- Database indexing for performance
- Webhook-based integration
- Modular design

---

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**Total Pages:** 100+
**Prepared By:** Augment Agent

**For More Information:**
- Technical Review: `docs/COMPREHENSIVE_APPLICATION_REVIEW.md`
- Executive Summary: `docs/EXECUTIVE_SUMMARY.md`
- Testing Results: `docs/MODULE_N_REAL_WORLD_TESTING_COMPLETE.md`
- Module N Docs: `module_n/README.md`

---


