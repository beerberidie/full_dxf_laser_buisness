# Laser OS - Usage Guide & Examples

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Workflow](#project-workflow)
3. [POP Management](#pop-management)
4. [Communications](#communications)
5. [Document Management](#document-management)
6. [Queue Management](#queue-management)
7. [Common Tasks](#common-tasks)
8. [API Examples](#api-examples)

---

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
cd full_dxf_laser_buisness

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask db upgrade

# Run the application
python run.py
```

### First Time Setup

1. **Configure Email** (optional but recommended):
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

2. **Create Upload Directories**:
   The application will automatically create these on first run:
   - `data/files/` - DXF design files
   - `data/documents/quotes/` - Quote documents
   - `data/documents/invoices/` - Invoice documents
   - `data/documents/pops/` - Proof of Payment documents
   - `data/documents/delivery_notes/` - Delivery notes

3. **Access the Application**:
   - Open browser to `http://localhost:5000`
   - Default development mode runs on port 5000

---

## 📋 Project Workflow

### Complete Project Lifecycle

#### 1. **Create Client**
```
Navigate to: Clients → Add New Client

Fill in:
- Name: "ABC Manufacturing"
- Contact Person: "John Smith"
- Email: "john@abc.com"
- Phone: "+27 11 123 4567"
- Address: "123 Industrial Road, Johannesburg"

Result: Client code auto-generated (e.g., CLI-001)
```

#### 2. **Create Project**
```
Navigate to: Projects → Add New Project

Fill in:
- Client: Select "ABC Manufacturing"
- Name: "Custom Brackets - 100 units"
- Description: "Stainless steel mounting brackets"
- Status: "Quote"
- Quote Date: Today's date
- Quoted Price: R 5,000.00

Result: Project code auto-generated (e.g., PRJ-001)
```

#### 3. **Upload Design Files**
```
Navigate to: Project Detail → Design Files → Upload

Select: bracket_design.dxf
Result: File uploaded and validated
```

#### 4. **Add Material & Production Details** 🆕
```
Navigate to: Project Detail → Edit

Fill in Phase 9 fields:
- Material Type: "Stainless Steel"
- Material Quantity (Sheets): 5
- Parts Quantity: 100
- Estimated Cutting Time: 120 (minutes)
- Number of Bins: 2
- Drawing Creation Time: 30 (minutes)

Result: Production details saved
```

#### 5. **Upload Quote Document** 🆕
```
Navigate to: Project Detail → Documents → Upload Document

Select:
- Document Type: "Quote"
- File: quote_ABC_001.pdf

Result: Document saved to data/documents/quotes/
```

#### 6. **Send Quote to Client** 🆕
```
Navigate to: Communications → Create Communication

Fill in:
- Type: "Email"
- Direction: "Outbound"
- Client: "ABC Manufacturing"
- Project: "Custom Brackets - 100 units"
- Subject: "Quote for Custom Brackets"
- Body: "Please find attached quote..."

Result: Email sent and logged
```

#### 7. **Receive POP** 🆕
```
Navigate to: Project Detail → Edit

Fill in:
- POP Received: ✓ (checked)
- POP Received Date: Today's date

Result: 
- POP Deadline auto-calculated (today + 3 days)
- Project appears in POP deadline warnings
```

#### 8. **Upload POP Document** 🆕
```
Navigate to: Project Detail → Documents → Upload Document

Select:
- Document Type: "Proof of Payment"
- File: pop_ABC_001.pdf

Result: POP document saved
```

#### 9. **Schedule for Cutting**
```
Navigate to: Queue → Add to Queue

Fill in:
- Project: "Custom Brackets - 100 units"
- Priority: "Normal"
- Scheduled Date: Within 3 days of POP deadline
- Estimated Cut Time: 120 (auto-filled from project)

Result: 
- Project added to queue
- POP deadline validation passed
- Capacity check performed
```

#### 10. **Complete Production**
```
Navigate to: Queue → Mark as Completed

Result:
- Queue item status: "Completed"
- Project status can be updated to "Completed"
```

#### 11. **Notify Client** 🆕
```
Navigate to: Project Detail → Edit

Fill in:
- Client Notified: ✓ (checked)
- Client Notified Date: Today's date

Or send communication:
Navigate to: Communications → Create Communication
Type: "Email"
Subject: "Your order is ready for collection"

Result: Client notification recorded
```

#### 12. **Confirm Delivery** 🆕
```
Navigate to: Project Detail → Edit

Fill in:
- Delivery Confirmed: ✓ (checked)
- Delivery Confirmed Date: Today's date

Upload delivery note:
Navigate to: Project Detail → Documents → Upload Document
Document Type: "Delivery Note"

Result: Project lifecycle complete
```

---

## 💰 POP Management

### Understanding the 3-Day Rule

**Business Rule:** Projects must be scheduled for cutting within 3 days of receiving Proof of Payment (POP).

### POP Workflow

#### 1. **Mark POP as Received**
```
Project Detail → Edit
- Check "POP Received"
- Set "POP Received Date"
- Save

System automatically:
- Calculates POP Deadline (POP Date + 3 days)
- Adds project to deadline tracking
```

#### 2. **View POP Deadlines**
```
Queue Page shows:
- ⚠️ Warning: Projects with deadlines within 1 day
- 🔴 Alert: Projects past deadline
- Days remaining/overdue displayed
```

#### 3. **Schedule Before Deadline**
```
Add to Queue:
- System validates scheduled date ≤ POP deadline
- Shows error if past deadline
- Shows warning if deadline is today/tomorrow
```

### POP Deadline Validation Examples

#### ✅ Valid Scheduling:
```
POP Received: 2025-10-15
POP Deadline: 2025-10-18
Scheduled Date: 2025-10-17
Result: ✓ Valid (1 day remaining)
```

#### ⚠️ Warning:
```
POP Received: 2025-10-15
POP Deadline: 2025-10-18
Scheduled Date: 2025-10-18
Result: ⚠️ Warning - Deadline is today
```

#### ❌ Invalid:
```
POP Received: 2025-10-15
POP Deadline: 2025-10-18
Scheduled Date: 2025-10-19
Result: ❌ Error - 1 day past deadline
```

---

## 💬 Communications

### Communication Types

1. **Email** - Sent via SMTP (Flask-Mail)
2. **Phone** - Manual logging
3. **WhatsApp** - Manual logging (integration placeholder)
4. **SMS** - Manual logging
5. **In-Person** - Face-to-face meetings
6. **Notification** - In-app notifications

### Sending an Email

```
Navigate to: Communications → Create Communication

Fill in:
- Type: "Email"
- Direction: "Outbound"
- Client: Select client (optional)
- Project: Select project (optional)
- Subject: "Your quote is ready"
- Body: "Dear Customer, please find your quote attached..."
- To Address: "customer@example.com"

Click: Send Email

Result:
- Email sent via SMTP
- Communication logged in database
- Status: "Sent" (or "Failed" if error)
- Activity logged
```

### Logging a Phone Call

```
Navigate to: Communications → Create Communication

Fill in:
- Type: "Phone"
- Direction: "Inbound" or "Outbound"
- Client: Select client
- Project: Select project (if applicable)
- Subject: "Follow-up on quote"
- Body: "Customer called to ask about delivery time. Advised 3-5 days."

Click: Save

Result:
- Communication logged
- Linked to client and project
- Searchable and filterable
```

### Viewing Communication History

```
Navigate to: Communications → List

Filter by:
- Type (Email, Phone, etc.)
- Direction (Inbound, Outbound)
- Status (Sent, Delivered, etc.)
- Client
- Project
- Date range

Result: Filtered list of communications
```

---

## 📄 Document Management

### Document Types

1. **Quote** - Saved to `data/documents/quotes/`
2. **Invoice** - Saved to `data/documents/invoices/`
3. **Proof of Payment** - Saved to `data/documents/pops/`
4. **Delivery Note** - Saved to `data/documents/delivery_notes/`

### Uploading a Document

```
Navigate to: Project Detail → Documents → Upload Document

Select:
- Document Type: "Quote"
- File: Choose file (PDF, DOC, DOCX, JPG, PNG)
- Notes: "Initial quote v1" (optional)

Click: Upload

System validates:
- File type (must be in ALLOWED_EXTENSIONS)
- File size (max 50 MB)
- Document type (must be valid)

Result:
- File saved with unique name
- Metadata stored in database
- Activity logged
```

### Document Naming Convention

```
Format: project_{project_id}_{doc_type}_{timestamp}_{hash}.{ext}

Example: project_5_quote_20251015_a3f2.pdf

Benefits:
- Unique filenames (no collisions)
- Easy to identify project
- Timestamp for sorting
- Original extension preserved
```

### Downloading a Document

```
Navigate to: Project Detail → Documents

Click: Document name or Download button

Result: File downloaded to browser
```

### Deleting a Document

```
Navigate to: Project Detail → Documents

Click: Delete button

Confirm: Yes

Result:
- Database record deleted
- Physical file deleted
- Activity logged
```

---

## 📅 Queue Management

### Adding to Queue

```
Navigate to: Queue → Add to Queue

Fill in:
- Project: Select project
- Priority: Low / Normal / High / Urgent
- Scheduled Date: Select date
- Estimated Cut Time: Auto-filled from project (editable)
- Notes: Any special instructions

Click: Add to Queue

System validates:
- POP deadline (if POP received)
- Daily capacity (default 8 hours)

Result:
- Queue item created
- Position assigned
- Validation warnings shown
```

### Queue Priorities

- **Urgent** - Red badge, highest priority
- **High** - Orange badge
- **Normal** - Blue badge (default)
- **Low** - Gray badge

### Capacity Planning

```
Daily Capacity: 8 hours (480 minutes)

Example:
- Project A: 120 minutes
- Project B: 180 minutes
- Project C: 150 minutes
Total: 450 minutes (93.75% utilization)

Result: ⚠️ Warning - High utilization
```

### Queue Statuses

- **Queued** - Waiting to start
- **In Progress** - Currently being cut
- **Completed** - Finished
- **Cancelled** - Cancelled

---

## 🔧 Common Tasks

### Task 1: Check Overdue POP Projects

```python
# In Python shell or service
from app.services.scheduling_validator import check_overdue_projects

overdue = check_overdue_projects()
for project in overdue:
    print(f"{project['project_code']}: {project['days_overdue']} days overdue")
```

### Task 2: Check Upcoming Deadlines

```python
from app.services.scheduling_validator import check_upcoming_deadlines

upcoming = check_upcoming_deadlines(days_ahead=2)
for project in upcoming:
    print(f"{project['project_code']}: {project['days_remaining']} days remaining")
```

### Task 3: Validate Scheduling

```python
from app.services.scheduling_validator import validate_scheduling
from app.models import Project
from datetime import date

project = Project.query.get(1)
result = validate_scheduling(project, scheduled_date=date(2025, 10, 20))

if result['valid']:
    print("✓ Can schedule")
else:
    for error in result['errors']:
        print(f"✗ {error}")
```

### Task 4: Send Email Programmatically

```python
from app.services.communication_service import send_email

result = send_email(
    to_email="customer@example.com",
    subject="Your order is ready",
    body="Dear Customer, your order is ready for collection.",
    project_id=1,
    client_id=1
)

if result['success']:
    print(f"✓ Email sent: {result['communication_id']}")
else:
    print(f"✗ Failed: {result['message']}")
```

---

## 🔌 API Examples

### Get Project with Phase 9 Data

```python
from app.models import Project

project = Project.query.get(1)

# Access Phase 9 fields
print(f"POP Received: {project.pop_received}")
print(f"POP Deadline: {project.pop_deadline}")
print(f"Material: {project.material_type}")
print(f"Sheets: {project.material_quantity_sheets}")
print(f"Parts: {project.parts_quantity}")
print(f"Cut Time: {project.estimated_cut_time} minutes")

# Check deadline status
if project.is_within_pop_deadline:
    print(f"✓ Within deadline ({project.days_until_pop_deadline} days remaining)")
else:
    print(f"✗ Past deadline ({abs(project.days_until_pop_deadline)} days overdue)")
```

### Get Project Communications

```python
from app.models import Project

project = Project.query.get(1)

# Get all communications
for comm in project.communications:
    print(f"{comm.comm_type}: {comm.subject} ({comm.status})")
```

### Get Project Documents

```python
from app.services.document_service import get_project_documents

# Get all documents
docs = get_project_documents(project_id=1)

# Get only POPs
pops = get_project_documents(project_id=1, document_type="Proof of Payment")

for doc in pops:
    print(f"{doc.original_filename} - {doc.file_size_formatted}")
```

---

## 📊 Best Practices

### 1. **Always Upload POP Documents**
- Upload POP document when marking POP as received
- Helps with record-keeping and auditing

### 2. **Schedule Within Deadline**
- Check queue before marking POP as received
- Ensure capacity available within 3-day window

### 3. **Log All Communications**
- Log phone calls, emails, and meetings
- Helps track customer interactions

### 4. **Use Priorities Wisely**
- Reserve "Urgent" for true emergencies
- Use "Normal" for most projects

### 5. **Keep Material Data Updated**
- Fill in material details early
- Helps with capacity planning

### 6. **Regular Queue Review**
- Check queue daily for deadline warnings
- Adjust priorities as needed

---

## 🆘 Troubleshooting

### Email Not Sending

**Check:**
1. MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD in .env
2. Gmail: Use App Password, not regular password
3. Check Flask logs for error messages

### File Upload Failing

**Check:**
1. File size < 50 MB
2. File type in ALLOWED_EXTENSIONS
3. Upload folder exists and is writable
4. Disk space available

### POP Deadline Validation Failing

**Check:**
1. POP Received is checked
2. POP Received Date is set
3. Scheduled date ≤ POP Deadline
4. Project status not Completed/Cancelled

---

**For more help, see CONFIGURATION_GUIDE.md and FINAL_COMPREHENSIVE_SUMMARY.md**

