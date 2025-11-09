# Communications Module - Quick Start Guide

## 🎯 What Can You Do Right Now?

### ✅ Currently Working
1. **Track Communications** - Manually log emails, WhatsApp messages, notifications
2. **Link to Clients/Projects** - Associate communications with business records
3. **Search & Filter** - Find communications by type, client, project, status
4. **View History** - See all communications for a client or project

### ⚠️ Needs Configuration
- **Send Emails** - Infrastructure ready, needs SMTP credentials

### ❌ Not Yet Built
- **Message Templates** - Reusable templates for common messages
- **Automated Triggers** - Auto-send emails on status changes
- **Inbound Processing** - Parse incoming emails to create projects
- **User Routing** - Send specific types to specific users

---

## 📖 How to Use Current Features

### 1. Create a Communication Record

**Navigate to:** Communications → New Communication

**Fill in:**
- **Type:** Email, WhatsApp, or Notification
- **Direction:** Inbound (received) or Outbound (sent)
- **Subject:** Message title
- **From/To:** Email addresses or phone numbers
- **Message:** Full content
- **Status:** Pending, Sent, Delivered, Read, Failed
- **Link to Client:** (Optional) Select client
- **Link to Project:** (Optional) Select project

**Use Cases:**
- Log an email you sent to a client
- Record a WhatsApp conversation
- Track a phone call or in-person meeting
- Document a notification sent to a client

### 2. View Communications List

**Navigate to:** Communications

**Features:**
- **Filter by Type:** Email, WhatsApp, Notification
- **Filter by Direction:** Inbound, Outbound
- **Filter by Client:** See all comms for a specific client
- **Filter by Project:** See all comms for a specific project
- **Filter by Status:** Pending, Sent, Delivered, etc.
- **Search:** Find by subject, body, or addresses
- **Pagination:** 50 communications per page

### 3. Link Communication to Client/Project

**Two ways:**

**Option A: During Creation**
- When creating a new communication, select client/project from dropdowns

**Option B: After Creation**
1. Open communication detail page
2. Click "Link to Client/Project" button
3. Select client and/or project
4. Click "Link Communication"

**To Unlink:**
1. Open communication detail page
2. Click "Unlink" button

### 4. View Communication Details

**Navigate to:** Communications → Click on any communication

**You'll see:**
- Full message content
- Sender and recipient
- Linked client and project (with clickable links)
- Status and timestamps
- Attachments (if any)
- Metadata

---

## 🔧 How to Activate Email Sending

### Step 1: Get SMTP Credentials

**For Gmail:**
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Copy the 16-character password

**For Office 365:**
1. Use your Office 365 email and password
2. Server: `smtp.office365.com`
3. Port: `587`

**For Other Providers:**
- Check your email provider's SMTP settings
- Common ports: 587 (TLS) or 465 (SSL)

### Step 2: Configure Environment Variables

**Create/Edit `.env` file in project root:**

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**For Office 365:**
```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@company.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@company.com
```

### Step 3: Restart Application

```bash
# Stop the application (Ctrl+C)
# Start it again
python run.py
```

### Step 4: Test Email Sending

**Option A: Via Python Console**
```python
from app import create_app
from app.services.communication_service import send_email

app = create_app()
with app.app_context():
    result = send_email(
        to='test@example.com',
        subject='Test Email from Laser OS',
        body='This is a test email to verify SMTP configuration.',
        client_id=1  # Optional
    )
    print(result)
```

**Option B: Via UI**
1. Create a new communication (Type: Email, Direction: Outbound)
2. Fill in recipient and message
3. Save
4. Check if email was sent (status should change to "Sent")

---

## 💡 Common Use Cases

### Use Case 1: Log Client Email Conversation
**Scenario:** You emailed a client about their order

**Steps:**
1. Go to Communications → New
2. Type: Email
3. Direction: Outbound
4. Subject: "Order Update - Project ABC123"
5. To: client@example.com
6. Message: (paste email content)
7. Link to Client: Select client
8. Link to Project: Select project
9. Status: Sent
10. Save

**Benefit:** Complete communication history for the project

### Use Case 2: Track WhatsApp Messages
**Scenario:** Client sent you a WhatsApp message with changes

**Steps:**
1. Go to Communications → New
2. Type: WhatsApp
3. Direction: Inbound
4. Subject: "Design Changes Request"
5. From: +27123456789
6. Message: (paste WhatsApp message)
7. Link to Client: Select client
8. Link to Project: Select project
9. Status: Read
10. Save

**Benefit:** All communication channels in one place

### Use Case 3: Find All Emails for a Client
**Scenario:** Need to review all communications with a specific client

**Steps:**
1. Go to Communications
2. Filter by Client: Select client from dropdown
3. Filter by Type: Email (optional)
4. View filtered list

**Benefit:** Quick access to communication history

### Use Case 4: Track Unlinked Communications
**Scenario:** Find communications that haven't been linked to clients/projects

**Steps:**
1. Go to Communications
2. Filter by Linking Status: Unlinked
3. Review and link as needed

**Benefit:** Ensure all communications are properly categorized

---

## 🚀 Future Enhancements (Roadmap)

### Phase 2: Message Templates (2-3 days)
**What:** Reusable templates for common messages
**Example:** "Collection Ready" template with placeholders
**Benefit:** Save time, ensure consistency

### Phase 3: Automated Triggers (3-5 days)
**What:** Auto-send emails when events occur
**Example:** Send "Order Confirmed" when POP received
**Benefit:** Reduce manual work, improve customer experience

### Phase 4: User-Specific Routing (2-3 days)
**What:** Route communications to specific users
**Example:** User A gets delivery notifications only
**Benefit:** Reduce noise, improve focus

### Phase 5: Inbound Email Processing (1-2 weeks)
**What:** Parse incoming emails to create projects
**Example:** Client emails order, system creates project
**Benefit:** Fully automated order intake

---

## 📊 Current Database Schema

```sql
-- Communications Table
CREATE TABLE communications (
    id INTEGER PRIMARY KEY,
    comm_type VARCHAR(20) NOT NULL,  -- Email, WhatsApp, Notification
    direction VARCHAR(10) NOT NULL,  -- Inbound, Outbound
    client_id INTEGER,  -- Foreign key to clients
    project_id INTEGER,  -- Foreign key to projects
    subject VARCHAR(500),
    body TEXT,
    from_address VARCHAR(255),
    to_address VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Pending',
    sent_at DATETIME,
    received_at DATETIME,
    read_at DATETIME,
    has_attachments BOOLEAN DEFAULT FALSE,
    is_linked BOOLEAN DEFAULT FALSE,
    comm_metadata TEXT,  -- JSON format
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Communication Attachments Table
CREATE TABLE communication_attachments (
    id INTEGER PRIMARY KEY,
    communication_id INTEGER NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50),
    created_at DATETIME NOT NULL
);
```

---

## 🔍 API Reference (For Developers)

### Send Email Programmatically

```python
from app.services.communication_service import send_email

# Simple email
result = send_email(
    to='client@example.com',
    subject='Your order is ready',
    body='Please collect your order.'
)

# Email with client/project linking
result = send_email(
    to='client@example.com',
    subject='Order Update',
    body='Your order ABC123 is ready for collection.',
    client_id=1,
    project_id=5
)

# Check result
if result['success']:
    print(f"Email sent! Communication ID: {result['communication_id']}")
else:
    print(f"Failed: {result['message']}")
```

### Available Service Functions

```python
# Email
send_email(to, subject, body, from_address=None, client_id=None, project_id=None, save_to_db=True)

# WhatsApp (placeholder)
send_whatsapp(to, message, client_id=None, project_id=None, save_to_db=True)

# Notification (placeholder)
send_notification(user_id, title, message, client_id=None, project_id=None, save_to_db=True)
```

---

## ❓ FAQ

**Q: Can I send emails right now?**  
A: Yes, but you need to configure SMTP credentials first (see "How to Activate Email Sending" above).

**Q: Are emails automatically sent when I create a communication?**  
A: No, currently you need to use the `send_email()` service function to actually send emails. The UI just logs communications.

**Q: Can I import emails from my email client?**  
A: Not yet. This would be part of the "Inbound Email Processing" feature (Phase 5).

**Q: Can I create message templates?**  
A: Not yet. This is planned for Phase 2 (2-3 days to implement).

**Q: Will emails automatically send when project status changes?**  
A: Not yet. This is planned for Phase 3 (3-5 days to implement).

**Q: Can I attach files to communications?**  
A: The database supports it, but the UI doesn't have file upload yet. This can be added if needed.

---

## 📞 Next Steps

**To start using communications:**
1. ✅ Start logging communications manually (works now)
2. ⚙️ Configure SMTP to enable email sending (1 hour)
3. 🎯 Request message templates feature (2-3 days to build)
4. 🚀 Request automated triggers feature (3-5 days to build)

**Questions?** Let me know what you'd like to implement next!

