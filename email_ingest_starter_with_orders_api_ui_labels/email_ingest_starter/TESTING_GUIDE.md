# 🧪 Email Ingestion System - Testing Guide

## ✅ Current Status

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ Gmail connected: garasongriesel@gmail.com
- ✅ Mailbox ID: 2

---

## 📧 Test the Complete Email Ingestion Flow

### Step 1: Send a Test Email

**Send an email TO**: `garasongriesel@gmail.com`

**Subject**: `New Order Request`

**Body**:
```
Hi,

We need the following items:

4 x MS plate 3mm
2 x SS sheet 1.5mm
1 x Aluminum bar 10mm

PO #1234
Due: 21/10/2025

Thanks!
```

**How to send**:
- Use any email client (Gmail, Outlook, etc.)
- Send from any email address
- Send TO your connected Gmail: garasongriesel@gmail.com

---

### Step 2: Fetch and Process the Email

Since webhooks aren't configured, you need to manually trigger email fetching.

**Option A: Use PowerShell Script** (Easiest)
```powershell
cd backend
.\fetch_emails.ps1
```

**Option B: Use PowerShell Command**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/gmail/fetch/2 -Method POST
```

**Option C: Use Browser**
- Open: http://localhost:8000/docs
- Find the `POST /gmail/fetch/{mailbox_id}` endpoint
- Click "Try it out"
- Enter mailbox_id: `2`
- Click "Execute"

---

### Step 3: Check the Results

**In the Frontend** (http://localhost:5173):
1. Refresh the page
2. Look at the "Recent Orders" table
3. You should see:
   - **PO**: 1234
   - **Due**: 21/10/2025
   - **Items**: 3 items listed
   - **Draft**: Status of the auto-generated draft reply

**Expected Data**:
- Client name: (extracted from email)
- PO Number: 1234
- Due Date: 21/10/2025
- Items:
  - 4 x MS plate 3mm
  - 2 x SS sheet 1.5mm
  - 1 x Aluminum bar 10mm

---

### Step 4: Test Draft Reply (Optional)

If a draft reply was created:
1. In the orders table, look for the "Draft" column
2. Click "Approve & Send" button
3. The draft will be sent from your Gmail account
4. Check your Gmail sent folder to verify

---

## 🔍 Troubleshooting

### No orders appear after fetching

**Check backend logs**:
- Look at the terminal running uvicorn
- Check for errors during email processing

**Verify email was received**:
- Log into garasongriesel@gmail.com
- Confirm the test email is in your inbox

**Check the database**:
```powershell
# In backend directory
python -c "from app.db import SessionLocal; from app.models import Email, Order; db = SessionLocal(); print(f'Emails: {db.query(Email).count()}'); print(f'Orders: {db.query(Order).count()}')"
```

### "Processed: 0 new messages"

This means the emails were already processed. The system tracks which messages have been processed to avoid duplicates.

**To test again**:
- Send a NEW email with different content
- Or delete the database and restart:
  ```powershell
  Remove-Item app.db
  # Restart the backend server
  ```

### Fetch endpoint returns error

**Check mailbox ID**:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/mailboxes | Select-Object -ExpandProperty Content
```

Use the correct ID from the response.

---

## 📊 API Endpoints for Testing

### List Mailboxes
```
GET http://localhost:8000/mailboxes
```

### Fetch Gmail Messages
```
POST http://localhost:8000/gmail/fetch/{mailbox_id}
```

### List Orders
```
GET http://localhost:8000/orders
```

### Get Specific Order
```
GET http://localhost:8000/orders/{order_id}
```

### Approve and Send Draft
```
POST http://localhost:8000/emails/{email_id}/approve_send
```

### List Routing Rules
```
GET http://localhost:8000/routing_rules
```

### Add Routing Rule
```
POST http://localhost:8000/routing_rules
Body: {"pattern": "sales@", "label": "sales"}
```

---

## 🎯 Advanced Testing

### Test Different Email Patterns

**Sales Email**:
```
To: sales@yourcompany.com
Subject: Quote Request
Body: Can you quote 10 x SS plate 2mm?
```

**Operations Email**:
```
To: ops@yourcompany.com
Subject: Urgent Order
Body: Need 5 x MS bar 12mm by tomorrow
```

### Test Email Classification

1. **Add routing rules**:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/routing_rules -Method POST -Body '{"pattern":"sales@","label":"sales"}' -ContentType "application/json"
```

2. **Send emails to different addresses**

3. **Check the "Route" column** in the orders table

---

## 📈 Expected Workflow

```
1. Email arrives → Gmail inbox
2. Manual fetch → POST /gmail/fetch/2
3. Email normalized → Extract text, subject, sender
4. AI analysis → Extract PO, items, due date
5. Order created → Saved to database
6. Label applied → Email tagged in Gmail
7. Draft created → Auto-reply generated
8. Display in UI → Shows in orders table
9. User approves → Click "Approve & Send"
10. Email sent → Draft sent via Gmail API
```

---

## 🚀 Next Steps

After successful testing:

1. **Set up Gmail Pub/Sub** for real-time webhooks (see SETUP_GUIDE.md)
2. **Configure routing rules** for automatic email classification
3. **Customize AI prompts** in `app/ai/engine.py`
4. **Add more email patterns** for different order formats
5. **Set up Microsoft 365** for Outlook integration (optional)

---

## 📞 Need Help?

- Check backend logs in the uvicorn terminal
- Use the API docs: http://localhost:8000/docs
- Review SETUP_GUIDE.md for configuration details
- Check QUICK_START.md for common issues

---

**Happy Testing! 🎉**

