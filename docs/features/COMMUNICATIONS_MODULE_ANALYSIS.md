# Communications Module - Current State & Future Roadmap

**Date:** October 18, 2025  
**Application:** Laser OS Tier 1  
**Module:** Communications (`app/routes/comms.py`)

---

## 📋 Executive Summary

The Communications module is **already implemented** with a solid foundation for tracking communications, but **email sending is not yet active** (requires SMTP configuration). The module is well-positioned for your future automation goals.

**Current Status:**
- ✅ Communication tracking (manual entry)
- ✅ Client/Project linking
- ✅ Email service infrastructure (ready, needs SMTP config)
- ❌ Automated message templates (not implemented)
- ❌ Triggered communications (not implemented)
- ❌ Inbound email processing (not implemented)
- ❌ User-specific routing (not implemented)

---

## 🔍 Current Capabilities (What's Already Built)

### 1. **Communication Tracking** ✅ FULLY IMPLEMENTED

**What it does:**
- Manually create communication records (emails, WhatsApp, notifications)
- Track inbound and outbound communications
- Link communications to clients and projects
- Store message content, subject, sender, recipient
- Track status (Pending, Sent, Delivered, Failed, Read)
- Support attachments

**Database Model** (`Communication`):
```python
Fields:
- comm_type: Email, WhatsApp, Notification
- direction: Inbound, Outbound
- client_id: Link to client (optional)
- project_id: Link to project (optional)
- subject: Message subject/title
- body: Message content
- from_address: Sender email/phone
- to_address: Recipient email/phone
- status: Pending, Sent, Delivered, Failed, Read
- sent_at, received_at, read_at: Timestamps
- has_attachments: Boolean
- is_linked: Whether linked to client/project
- comm_metadata: JSON for additional data
```

**Routes Available:**
- `/communications/` - List all communications with filtering
- `/communications/<id>` - View communication details
- `/communications/new` - Create new communication (manual)
- `/communications/<id>/link` - Link to client/project
- `/communications/<id>/unlink` - Unlink from client/project

**Filtering Capabilities:**
- By type (Email, WhatsApp, Notification)
- By direction (Inbound, Outbound)
- By client
- By project
- By status
- By linking status
- Search in subject/body/addresses

### 2. **Email Service Infrastructure** ✅ READY (Needs Configuration)

**What's built:**
- `app/services/communication_service.py` - Email sending service
- Flask-Mail integration
- SMTP configuration in `config.py`
- Database logging of sent emails

**Service Function:**
```python
send_email(
    to='client@example.com',
    subject='Your order is ready',
    body='Please collect your order.',
    from_address=None,  # Uses MAIL_DEFAULT_SENDER
    client_id=1,  # Optional linking
    project_id=5,  # Optional linking
    save_to_db=True  # Logs to database
)
```

**What's NOT configured:**
- SMTP credentials (MAIL_USERNAME, MAIL_PASSWORD)
- SMTP server details (currently defaults to Gmail)

**To activate email sending:**
1. Edit `.env` file (or create from `.env.example`)
2. Set SMTP credentials:
   ```bash
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password  # Gmail App Password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```
3. Restart application

### 3. **Client/Project Linking** ✅ FULLY IMPLEMENTED

**What it does:**
- Manually link communications to clients
- Manually link communications to projects
- Auto-detect linking based on email/phone matching (placeholder)
- View all communications for a client/project

**Use Cases:**
- Track all emails sent to a specific client
- View communication history for a project
- Manually categorize inbound emails

---

## ❌ What's NOT Implemented (Your Future Vision)

### 1. **Automated Message Templates** ❌ NOT IMPLEMENTED

**What you want:**
- Reusable message templates (e.g., "Collection Ready", "Quote Sent")
- Placeholders for dynamic data (client name, project code, etc.)
- Template management interface

**What's needed:**
- New database model: `MessageTemplate`
  - Fields: name, subject_template, body_template, template_type
- Template editor UI
- Placeholder system (e.g., `{{client_name}}`, `{{project_code}}`)
- Template rendering service

**Complexity:** 🟡 MEDIUM (2-3 days)

### 2. **Triggered Communications** ❌ NOT IMPLEMENTED

**What you want:**
- Automatically send emails when project status changes
- Trigger "Collection Ready" when status = "Complete"
- Trigger "Order Confirmed" when POP received
- Trigger "Quote Ready" when quote created

**What's needed:**
- Event system or hooks in existing routes
- Template-to-trigger mapping
- Configuration for which triggers are active
- Background task queue (optional, for reliability)

**Complexity:** 🟠 MEDIUM-HIGH (3-5 days)

**Implementation approach:**
1. Add hooks to existing routes (e.g., `projects.update_status`)
2. Check if trigger conditions met
3. Load appropriate template
4. Render template with project/client data
5. Call `send_email()` service
6. Log communication

### 3. **Inbound Email Processing** ❌ NOT IMPLEMENTED

**What you want:**
- Receive incoming emails from clients
- Parse email content to extract project info
- Auto-create or update projects based on email

**What's needed:**
- Email receiving service (IMAP/POP3 or webhook)
- Email parsing logic (AI/NLP or rule-based)
- Project creation/update logic
- Conflict resolution (duplicate detection)
- Security (verify sender, prevent spam)

**Complexity:** 🔴 HIGH (1-2 weeks)

**Challenges:**
- Email parsing is complex (varied formats, attachments)
- AI/NLP integration required for reliable extraction
- Security concerns (malicious emails, spam)
- Error handling (what if parsing fails?)

**Recommendation:** **Defer this to Phase 2** - Focus on outbound automation first

### 4. **User-Specific Communication Routing** ❌ NOT IMPLEMENTED

**What you want:**
- Assign communication types to specific users
- User A gets delivery notifications
- User B gets all client communications
- User C gets urgent messages only

**What's needed:**
- New database model: `CommunicationRouting`
  - Fields: user_id, comm_type, priority_filter, enabled
- User notification preferences UI
- Routing logic in email sending service
- Multi-recipient support

**Complexity:** 🟡 MEDIUM (2-3 days)

---

## 🎯 Recommended Implementation Roadmap

### **Phase 1: Activate Email Sending** (1 hour)
**Priority:** 🔴 HIGH  
**Effort:** 🟢 MINIMAL

**Tasks:**
1. Configure SMTP credentials in `.env`
2. Test email sending with `send_email()` function
3. Verify emails are received

**Outcome:** Email infrastructure becomes functional

---

### **Phase 2: Message Templates** (2-3 days)
**Priority:** 🟠 MEDIUM-HIGH  
**Effort:** 🟡 MEDIUM

**Tasks:**
1. Create `MessageTemplate` database model
2. Build template management UI (list, create, edit, delete)
3. Implement placeholder system (`{{client_name}}`, etc.)
4. Create template rendering service
5. Add "Send from Template" button to communications

**Outcome:** Reusable message templates for common communications

**Database Model:**
```python
class MessageTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Collection Ready"
    template_type = db.Column(db.String(50))  # "project_complete", "quote_sent"
    subject_template = db.Column(db.String(500))  # "Your order {{project_code}} is ready"
    body_template = db.Column(db.Text)  # "Dear {{client_name}}, ..."
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Placeholders:**
- `{{client_name}}` - Client name
- `{{client_code}}` - Client code
- `{{project_code}}` - Project code
- `{{project_name}}` - Project name
- `{{collection_date}}` - Calculated collection date
- `{{quote_total}}` - Quote total amount
- `{{company_name}}` - Your company name

---

### **Phase 3: Automated Triggers** (3-5 days)
**Priority:** 🟠 MEDIUM  
**Effort:** 🟠 MEDIUM-HIGH

**Tasks:**
1. Create trigger configuration system
2. Add hooks to project status updates
3. Add hooks to POP received
4. Add hooks to quote creation
5. Implement trigger-to-template mapping
6. Add trigger enable/disable settings
7. Test all trigger scenarios

**Outcome:** Automatic emails sent when business events occur

**Trigger Examples:**
```python
# In projects.update_status route:
if new_status == 'Complete':
    trigger_communication(
        template_type='project_complete',
        client_id=project.client_id,
        project_id=project.id
    )

# In projects.mark_pop_received route:
if pop_received:
    trigger_communication(
        template_type='order_confirmed',
        client_id=project.client_id,
        project_id=project.id
    )
```

---

### **Phase 4: User-Specific Routing** (2-3 days)
**Priority:** 🟡 LOW-MEDIUM  
**Effort:** 🟡 MEDIUM

**Tasks:**
1. Create `CommunicationRouting` model
2. Build user notification preferences UI
3. Implement routing logic in email service
4. Add CC/BCC support for multiple recipients
5. Test routing scenarios

**Outcome:** Users receive only relevant communications

---

### **Phase 5: Inbound Email Processing** (1-2 weeks)
**Priority:** 🟢 LOW (Future Enhancement)  
**Effort:** 🔴 HIGH

**Tasks:**
1. Research email receiving options (IMAP, webhooks)
2. Implement email fetching service
3. Build email parsing logic (AI/NLP or rules)
4. Create project extraction logic
5. Implement security measures
6. Build error handling and manual review queue
7. Extensive testing

**Outcome:** Emails from clients automatically create/update projects

**Recommendation:** **Defer to later** - Complex and requires AI integration

---

## 💡 Practical Next Steps (What to Do Now)

### **Option 1: Just Activate Email (Recommended First Step)**
**Time:** 1 hour  
**Benefit:** Make existing infrastructure functional

1. Copy `.env.example` to `.env`
2. Configure SMTP settings
3. Test with manual communication creation
4. Start using email tracking

### **Option 2: Build Message Templates**
**Time:** 2-3 days  
**Benefit:** Reusable templates for common messages

1. Implement Phase 2 from roadmap
2. Create templates for common scenarios
3. Use templates when sending communications

### **Option 3: Full Automation (Recommended Long-term)**
**Time:** 1-2 weeks  
**Benefit:** Complete automation of outbound communications

1. Implement Phases 2 + 3 from roadmap
2. Configure triggers for key events
3. Test automation thoroughly
4. Monitor and refine

---

## 📊 Feasibility Assessment

### **Workflow 1: Automated Message Templates** ✅ FEASIBLE
**Complexity:** 🟡 MEDIUM  
**Timeline:** 2-3 days  
**Dependencies:** None  
**Recommendation:** **START HERE** - High value, moderate effort

### **Workflow 2: Inbound Email Processing** ⚠️ COMPLEX
**Complexity:** 🔴 HIGH  
**Timeline:** 1-2 weeks  
**Dependencies:** AI/NLP service, email receiving infrastructure  
**Recommendation:** **DEFER** - Complex, lower ROI initially

### **Workflow 3: User-Specific Routing** ✅ FEASIBLE
**Complexity:** 🟡 MEDIUM  
**Timeline:** 2-3 days  
**Dependencies:** User management (already implemented)  
**Recommendation:** **PHASE 4** - Useful but not critical

---

## 🎯 My Recommendation

**Start with this sequence:**

1. **Week 1:** Activate email sending (1 hour) + Build message templates (2-3 days)
2. **Week 2:** Implement automated triggers (3-5 days)
3. **Week 3:** Add user-specific routing (2-3 days)
4. **Future:** Consider inbound email processing (requires AI integration)

**Why this order?**
- Quick win: Email activation
- High value: Templates save time immediately
- Automation: Triggers reduce manual work
- Refinement: Routing improves user experience
- Advanced: Inbound processing is complex, defer until core automation is proven

---

## 📝 Summary

**Current State:**
- ✅ Communication tracking works
- ✅ Email infrastructure ready (needs SMTP config)
- ✅ Client/Project linking works
- ❌ No automated templates
- ❌ No triggered communications
- ❌ No inbound processing

**Your Vision:**
- ✅ **Feasible:** Automated message templates
- ✅ **Feasible:** Triggered communications
- ⚠️ **Complex:** Inbound email processing (defer)
- ✅ **Feasible:** User-specific routing

**Recommended First Step:**
Configure SMTP and build message templates (Phase 1 + 2) - **High value, low risk**

---

**Questions? Let me know if you'd like me to:**
1. Configure SMTP email sending now
2. Start building message templates
3. Implement automated triggers
4. Create a detailed technical specification for any phase

