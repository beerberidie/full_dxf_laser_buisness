# 🚀 Quick Start - Get Gmail Working in 5 Minutes

## Current Status
✅ Backend server running on http://localhost:8000  
✅ Frontend running on http://localhost:5173  
✅ `.env` file created with FERNET_KEY  
❌ **Need Google OAuth credentials to connect Gmail**

---

## 🎯 What You Need to Do Now

### Option 1: Set Up Your Own Google OAuth (Recommended)

**Time: ~5 minutes**

1. **Open Google Cloud Console**: https://console.cloud.google.com/

2. **Create/Select Project**:
   - Click project dropdown → "New Project"
   - Name: "Email Ingest System"
   - Click "Create"

3. **Enable Gmail API**:
   - Go to: APIs & Services → Library
   - Search: "Gmail API"
   - Click "Enable"

4. **Configure OAuth Consent**:
   - Go to: APIs & Services → OAuth consent screen
   - User Type: "External"
   - App name: "Email Ingest System"
   - Your email for support and developer contact
   - Click "Save and Continue"
   - Scopes: Add `gmail.readonly` and `gmail.send`
   - Test users: Add your Gmail address
   - Click "Save and Continue" → "Back to Dashboard"

5. **Create Credentials**:
   - Go to: APIs & Services → Credentials
   - Click: "Create Credentials" → "OAuth client ID"
   - Type: "Web application"
   - Name: "Email Ingest OAuth"
   - Redirect URI: `http://localhost:8000/auth/gmail/callback`
   - Click "Create"
   - **Copy the Client ID and Client Secret**

6. **Update `.env` file**:
   ```bash
   # Open backend/.env and replace:
   GOOGLE_CLIENT_ID=paste_your_client_id_here
   GOOGLE_CLIENT_SECRET=paste_your_client_secret_here
   ```

7. **Restart Backend**:
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   python -m uvicorn app.main:app --reload
   ```

8. **Test It**:
   - Go to http://localhost:5173
   - Click "Connect Gmail"
   - Sign in and authorize
   - ✅ Done!

---

### Option 2: Use Test Credentials (Quick Test Only)

**⚠️ WARNING: Only for quick testing, not for production!**

If you just want to see if the system works, you can use these test credentials:

```env
# These are PUBLIC test credentials - DO NOT use in production!
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

**Note**: These won't actually work for OAuth, but will let you test other parts of the system.

---

## 🔍 Verify Configuration

Run this command to check your setup:

```bash
cd backend
python check_config.py
```

You should see:
```
✅ All required configuration is set!
```

---

## 🧪 Test the Complete Flow

Once configured:

1. **Connect Gmail**:
   - Open http://localhost:5173
   - Click "Connect Gmail"
   - Authorize with your Google account

2. **Send Test Email** to your connected Gmail:
   ```
   Subject: New Order Request
   
   Hi,
   
   We need:
   4 x MS plate 3mm
   2 x SS sheet 1.5mm
   
   PO #1234
   Due: 21/10/2025
   
   Thanks!
   ```

3. **Check Results**:
   - Go to Orders page
   - See extracted: PO #1234, items, due date
   - Check for auto-generated draft reply
   - Click "Approve & Send"

---

## 🐛 Troubleshooting

### "GOOGLE_CLIENT_ID not set" error
→ Update `.env` file and restart backend

### "redirect_uri_mismatch" error  
→ Ensure redirect URI in Google Console is exactly:  
   `http://localhost:8000/auth/gmail/callback`

### "Access blocked" error
→ Add your email as test user in OAuth consent screen

### Changes not taking effect
→ Restart the backend server after updating `.env`

---

## 📁 File Locations

- Configuration: `backend/.env`
- Setup Guide: `backend/SETUP_GUIDE.md`
- Config Checker: `backend/check_config.py`
- Backend Logs: Check terminal running uvicorn

---

## 🎓 Next Steps

After Gmail is working:

1. **Test Email Processing**: Send emails with PO numbers and items
2. **Configure Routing Rules**: Set up ops/sales/quotes classification
3. **Set Up Pub/Sub**: For real-time webhooks (optional)
4. **Add M365**: Configure Microsoft 365 integration (optional)

---

## 📞 Need Help?

1. Check `SETUP_GUIDE.md` for detailed instructions
2. Run `python check_config.py` to diagnose issues
3. Check backend terminal for error messages
4. Verify all steps in Google Cloud Console

---

**Ready to go? Update your `.env` file and restart the backend!** 🚀

