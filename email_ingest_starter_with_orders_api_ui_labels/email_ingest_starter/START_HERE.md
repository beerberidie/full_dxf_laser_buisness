# 🚀 Quick Start Guide

This guide will help you start the Email Ingest Application quickly.

## 📋 Prerequisites

Before starting the application, make sure you have:

1. ✅ **Python 3.11+** installed
2. ✅ **Node.js 18+** and npm installed
3. ✅ **Dependencies installed**:
   - Backend: `cd backend && pip install -r requirements.txt`
   - Frontend: `cd frontend && npm install`
4. ✅ **Environment configured**: `.env` file in `backend/` directory with your credentials

## 🎯 Starting the Application

You have **3 options** to start the application:

### Option 1: Batch File (Easiest for Windows) ⭐ RECOMMENDED

Simply **double-click** `start_app.bat`

- Opens two separate windows (backend and frontend)
- Automatically opens your browser to http://localhost:5173
- Servers keep running even after you close the launcher window
- To stop: Close the backend and frontend windows

### Option 2: PowerShell Script

```powershell
.\start_app.ps1
```

- Runs both servers in separate windows
- Automatically opens your browser
- Press any key in the PowerShell window to stop both servers

### Option 3: Python Script

```bash
python start_app.py
```

- Runs both servers and monitors them
- Shows combined output in one terminal
- Press `Ctrl+C` to stop both servers

---

## 🌐 Application URLs

Once started, you can access:

- **Frontend (UI)**: http://localhost:5173
- **Backend (API)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📧 Testing the Email Ingestion

### Step 1: Connect Your Gmail

1. Go to http://localhost:5173
2. Click "Connect Gmail" (or similar button)
3. Authorize the application
4. You should see "Connected successfully"

### Step 2: Send a Test Email

Send an email **TO** your connected Gmail address with this content:

```
Subject: New Order Request

Hi,

We need the following items:

4 x MS plate 3mm
2 x SS sheet 1.5mm
1 x Aluminum bar 10mm

PO #1234
Due: 21/10/2025

Thanks!
```

### Step 3: Fetch Emails

Run this command in PowerShell:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/gmail/fetch/2 -Method POST
```

*(Replace `2` with your mailbox ID if different)*

### Step 4: View Results

1. Go to http://localhost:5173
2. Refresh the page
3. You should see the order in the "Recent Orders" table with:
   - PO Number: 1234
   - Items: 4x MS plate 3mm, 2x SS sheet 1.5mm, 1x Aluminum bar 10mm

---

## 🛠️ Manual Start (Alternative)

If the scripts don't work, you can start manually:

### Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

---

## 🔧 Troubleshooting

### "Port already in use" error

If you see port conflicts:

**Backend (port 8000):**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Frontend (port 5173):**
```powershell
# Find process using port 5173
netstat -ano | findstr :5173

# Kill the process
taskkill /PID <PID> /F
```

### "Module not found" error

Make sure dependencies are installed:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### "GOOGLE_CLIENT_ID not set" error

Make sure you have a `.env` file in the `backend/` directory with:

```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/gmail/callback
FERNET_KEY=your-fernet-key
```

See `backend/SETUP_GUIDE.md` for detailed OAuth setup instructions.

---

## 📚 Additional Resources

- **OAuth Setup**: See `backend/SETUP_GUIDE.md`
- **Testing Guide**: See `TESTING_GUIDE.md`
- **Quick Reference**: See `backend/QUICK_START.md`

---

## 🎉 Success!

If everything is working, you should see:

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ Browser automatically opened to the frontend
- ✅ No errors in the terminal windows

**Happy email ingesting!** 🚀

