# Email Ingest System - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud account (for Gmail integration)
- Microsoft Azure account (optional, for M365 integration)

---

## 📋 Step 1: Configure Google OAuth Credentials

### A. Create Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Create a New Project**:
   - Click the project dropdown at the top
   - Click "New Project"
   - Name: "Email Ingest System" (or your preferred name)
   - Click "Create"

3. **Enable Gmail API**:
   - Navigate to: "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and click "Enable"

### B. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have Google Workspace)
3. Fill in the required fields:
   - **App name**: Email Ingest System
   - **User support email**: Your email address
   - **Developer contact**: Your email address
4. Click "Save and Continue"

5. **Add Scopes**:
   - Click "Add or Remove Scopes"
   - Add these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `openid`
     - `email`
   - Click "Update" then "Save and Continue"

6. **Add Test Users**:
   - Click "Add Users"
   - Add your Gmail address
   - Click "Save and Continue"

7. Click "Back to Dashboard"

### C. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure:
   - **Application type**: Web application
   - **Name**: Email Ingest OAuth Client
   - **Authorized redirect URIs**: 
     - Click "Add URI"
     - Enter: `http://localhost:8000/auth/gmail/callback`
4. Click "Create"
5. **IMPORTANT**: Copy the Client ID and Client Secret that appear
   - You'll need these for the `.env` file

---

## 📝 Step 2: Update the `.env` File

1. Open `backend/.env` in a text editor
2. Replace the placeholder values:

```env
# Replace these with your actual Google OAuth credentials
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_FROM_GOOGLE_CONSOLE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE
```

3. Save the file

---

## 🔄 Step 3: Restart the Backend Server

1. Stop the current backend server (Ctrl+C in the terminal)
2. Restart it:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

---

## ✅ Step 4: Test the Gmail Connection

1. Open the frontend: http://localhost:5173
2. Click "Connect Gmail" or navigate to the Gmail auth page
3. You should be redirected to Google's OAuth consent screen
4. Sign in with your Gmail account (must be added as a test user)
5. Grant the requested permissions
6. You should be redirected back to the app with a success message

---

## 🔧 Optional: Set Up Gmail Pub/Sub (for Real-time Webhooks)

If you want real-time email notifications instead of polling:

### A. Enable Pub/Sub API
1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Cloud Pub/Sub API"
3. Click "Enable"

### B. Create a Pub/Sub Topic
1. Go to "Pub/Sub" > "Topics"
2. Click "Create Topic"
3. Name: `gmail-notifications`
4. Click "Create"
5. Copy the full topic name (format: `projects/YOUR_PROJECT_ID/topics/gmail-notifications`)

### C. Grant Gmail Permission
1. In the topic details, click "Permissions"
2. Click "Add Principal"
3. Principal: `gmail-api-push@system.gserviceaccount.com`
4. Role: "Pub/Sub Publisher"
5. Click "Save"

### D. Update `.env`
```env
GMAIL_PUBSUB_TOPIC=projects/YOUR_PROJECT_ID/topics/gmail-notifications
```

### E. Set Up Public Webhook URL
For production, you'll need a public URL for webhooks. For local development:
- Use ngrok: `ngrok http 8000`
- Update `.env`: `PUBLIC_WEBHOOK_BASE=https://your-ngrok-url.ngrok.io`

---

## 🧪 Testing the Email Ingestion Flow

### 1. Send a Test Email
Send an email to your connected Gmail account with:

**Subject**: New Order Request

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

### 2. Verify Processing
1. Check the Orders page in the UI
2. Verify extracted data:
   - PO Number: 1234
   - Items: MS plate 3mm (qty: 4), SS sheet 1.5mm (qty: 2), etc.
   - Due Date: 21/10/2025
3. Check that the email received the appropriate label
4. Look for the auto-generated draft reply

### 3. Approve and Send Draft
1. Click "Approve & Send" on the draft
2. Verify the email is sent from your Gmail account

---

## 🐛 Troubleshooting

### Error: "GOOGLE_CLIENT_ID not set"
- Ensure `.env` file exists in `backend/` directory
- Check that `GOOGLE_CLIENT_ID` is set correctly
- Restart the backend server after updating `.env`

### Error: "redirect_uri_mismatch"
- Ensure the redirect URI in Google Console exactly matches: `http://localhost:8000/auth/gmail/callback`
- No trailing slashes
- Check for http vs https

### Error: "Access blocked: This app's request is invalid"
- Make sure you've added your email as a test user in OAuth consent screen
- Verify all required scopes are added

### Email not being processed
- Check backend logs for errors
- Verify Gmail API is enabled
- If using Pub/Sub, check topic permissions

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Gmail Push Notifications](https://developers.google.com/gmail/api/guides/push)

---

## 🔒 Security Notes

1. **Never commit `.env` to version control**
   - Already added to `.gitignore`
   
2. **Use environment-specific credentials**
   - Development: localhost redirect URIs
   - Production: proper domain redirect URIs

3. **Rotate credentials regularly**
   - Especially if exposed or compromised

4. **Use proper secret management in production**
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager

---

## 📞 Need Help?

If you encounter issues:
1. Check the backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure APIs are enabled in Google Cloud Console
4. Check that redirect URIs match exactly

