# SMTP Email Configuration Guide

## 🎯 Quick Start

Your `.env` file has been updated with email configuration placeholders. Follow the steps below to activate email sending.

---

## 📧 Option 1: Gmail (Recommended for Testing)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/security
2. Click on "2-Step Verification"
3. Follow the prompts to enable 2FA (if not already enabled)

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select app: **Mail**
3. Select device: **Windows Computer** (or "Other" and name it "Laser OS")
4. Click **Generate**
5. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
6. **Important:** Remove spaces when pasting into `.env` file

### Step 3: Update `.env` File
Open `.env` and update these lines:

```bash
MAIL_USERNAME=your-actual-email@gmail.com
MAIL_PASSWORD=abcdabcdabcdabcd  # 16 characters, no spaces
MAIL_DEFAULT_SENDER=your-actual-email@gmail.com
```

**Example:**
```bash
MAIL_USERNAME=garason@gmail.com
MAIL_PASSWORD=abcd1234efgh5678
MAIL_DEFAULT_SENDER=garason@gmail.com
```

### Step 4: Restart Application
```bash
# Stop the application (Ctrl+C in the terminal)
# Start it again
python run.py
```

---

## 📧 Option 2: Office 365 / Outlook

### Step 1: Update `.env` File
```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@company.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@company.com
```

### Step 2: Restart Application
```bash
python run.py
```

---

## 📧 Option 3: Other Email Providers

### Common SMTP Settings

**Yahoo Mail:**
```bash
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

**Outlook.com (Personal):**
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

**Custom SMTP Server:**
```bash
MAIL_SERVER=smtp.yourdomain.com
MAIL_PORT=587  # or 465 for SSL
MAIL_USE_TLS=True  # or False if using SSL
MAIL_USE_SSL=False  # or True if using port 465
```

---

## 🧪 Testing Email Configuration

### Method 1: Using Python Console (Recommended)

1. Open a new terminal in your project directory
2. Activate virtual environment (if using one):
   ```bash
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   ```
3. Run Python:
   ```bash
   python
   ```
4. Test email sending:
   ```python
   from app import create_app
   from app.services.communication_service import send_email
   
   app = create_app()
   with app.app_context():
       result = send_email(
           to='your-test-email@gmail.com',  # Use your email
           subject='Test Email from Laser OS',
           body='This is a test email to verify SMTP configuration is working correctly.'
       )
       print(result)
   ```

5. Check the result:
   - **Success:** `{'success': True, 'message': 'Email sent successfully', 'communication_id': 1}`
   - **Failure:** `{'success': False, 'message': 'Error description'}`

6. Check your inbox for the test email

### Method 2: Using Test Script (Automated)

I'll create a test script for you that you can run directly.

---

## ❌ Common Issues & Solutions

### Issue 1: "Username and Password not accepted"
**Cause:** Using regular password instead of App Password (Gmail)  
**Solution:** Generate App Password (see Step 2 above)

### Issue 2: "SMTP AUTH extension not supported"
**Cause:** Wrong SMTP server or port  
**Solution:** Verify MAIL_SERVER and MAIL_PORT settings

### Issue 3: "Connection refused"
**Cause:** Firewall blocking SMTP port  
**Solution:** Check firewall settings, try port 465 with SSL

### Issue 4: "Email service not configured"
**Cause:** `.env` file not loaded or missing credentials  
**Solution:** 
- Restart application after editing `.env`
- Verify MAIL_USERNAME and MAIL_PASSWORD are set
- Check for typos in variable names

### Issue 5: "SMTPAuthenticationError"
**Cause:** Incorrect credentials  
**Solution:** 
- Double-check email and password
- For Gmail, ensure App Password is used (not regular password)
- Verify 2FA is enabled (Gmail requirement)

---

## 🔒 Security Best Practices

### 1. Never Commit `.env` to Git
The `.env` file is already in `.gitignore`, but verify:
```bash
git status
# .env should NOT appear in the list
```

### 2. Use App Passwords (Gmail)
- Never use your main Google account password
- App Passwords are safer and can be revoked independently

### 3. Rotate Passwords Regularly
- Change App Passwords every 6-12 months
- Revoke old App Passwords when no longer needed

### 4. Use Environment-Specific Credentials
- Development: Use test email account
- Production: Use dedicated business email account

---

## 📊 Email Configuration Status Check

Run this command to check your configuration:

```bash
python -c "from app import create_app; app = create_app(); app.config.print_config()"
```

Look for:
```
📧 Email Configured: ✓ Yes
   Server: smtp.gmail.com:587
   Username: your-email@gmail.com
```

If you see `✗ No (using defaults)`, your credentials are not set correctly.

---

## 🎯 Next Steps After Configuration

Once email is configured and tested:

1. ✅ **Test email sending** - Verify emails are received
2. ✅ **Create communication records** - Log emails in the system
3. ✅ **Use message templates** - Send templated emails (Phase 2)
4. ✅ **Enable automated triggers** - Auto-send emails on events (Phase 3)

---

## 📞 Need Help?

If you encounter issues:

1. Check the error message carefully
2. Verify all settings in `.env` file
3. Ensure application was restarted after editing `.env`
4. Try the test script to isolate the issue
5. Check your email provider's SMTP documentation

---

## ✅ Configuration Checklist

Before testing, verify:

- [ ] 2-Factor Authentication enabled (Gmail only)
- [ ] App Password generated (Gmail only)
- [ ] `.env` file updated with correct credentials
- [ ] No spaces in App Password
- [ ] MAIL_USERNAME matches MAIL_DEFAULT_SENDER
- [ ] Application restarted after editing `.env`
- [ ] Firewall allows SMTP traffic (port 587 or 465)

---

## 🚀 Ready to Test!

Once you've updated the `.env` file with your credentials, let me know and I'll create a test script to verify everything works!

