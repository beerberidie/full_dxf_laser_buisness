# Laser OS - Local Network Access Guide

## 📋 Overview

This guide explains how to make Laser OS accessible to other computers on your local office network, allowing colleagues to access the application from their devices.

---

## 🔧 Server Configuration (Already Complete ✅)

Your Flask application is already configured to accept network connections:

**File:** `run.py` (Line 133)
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

- **`host='0.0.0.0'`** - Binds to all network interfaces (allows external connections)
- **`port=5000`** - Application runs on port 5000
- **`debug=True`** - Development mode with auto-reload

✅ **No changes needed to Flask configuration!**

---

## 🔥 Windows Firewall Configuration

### **Option 1: Automated Script (Recommended)**

1. **Open PowerShell as Administrator:**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to project directory:**
   ```powershell
   cd "C:\Users\Garas\Documents\augment-projects\full_dxf_laser_buisness"
   ```

3. **Run the firewall configuration script:**
   ```powershell
   .\scripts\configure_firewall.ps1
   ```

4. **Follow the prompts** - The script will:
   - Check for existing firewall rules
   - Create a new rule allowing inbound TCP connections on port 5000
   - Display your local IP addresses
   - Show the URL to share with colleagues

### **Option 2: Manual Configuration**

If you prefer to configure the firewall manually:

1. **Open Windows Defender Firewall:**
   - Press `Win + R`
   - Type `wf.msc` and press Enter

2. **Create Inbound Rule:**
   - Click "Inbound Rules" in left panel
   - Click "New Rule..." in right panel
   - Select "Port" → Next
   - Select "TCP" and enter port `5000` → Next
   - Select "Allow the connection" → Next
   - Check "Domain" and "Private" (uncheck "Public") → Next
   - Name: `Laser OS Flask Server (Port 5000)` → Finish

---

## 🌐 Finding Your IP Address

### **Current Network Configuration**

Based on your `ipconfig` output:

| Adapter | IP Address | Status | Use For |
|---------|------------|--------|---------|
| **Wi-Fi** | **192.168.88.31** | ✅ **Connected** | **Use this IP** |
| Local Area Connection* 2 | 192.168.137.1 | Connected | Mobile hotspot (ignore) |
| Ethernet | - | Disconnected | Not available |

### **Your Access URL**

Share this URL with your colleagues:

```
http://192.168.88.31:5000
```

### **How to Check Your IP Address Anytime**

1. **Open Command Prompt:**
   - Press `Win + R`
   - Type `cmd` and press Enter

2. **Run ipconfig:**
   ```cmd
   ipconfig
   ```

3. **Look for "Wi-Fi" adapter:**
   - Find the line: `IPv4 Address. . . . . . . . . . . : 192.168.88.31`
   - This is your current IP address

---

## 🚀 Starting the Server

### **Step 1: Start Flask Application**

1. **Open Command Prompt or PowerShell:**
   ```cmd
   cd "C:\Users\Garas\Documents\augment-projects\full_dxf_laser_buisness"
   ```

2. **Run the server:**
   ```cmd
   python run.py
   ```

3. **Verify server is running:**
   - Look for: `Running on http://192.168.88.31:5000`
   - Server should show both `127.0.0.1:5000` (localhost) and your network IP

### **Step 2: Test Local Access**

Before sharing with colleagues, test on your own computer:

1. **Open browser**
2. **Navigate to:** `http://192.168.88.31:5000`
3. **Login with test credentials:**
   - Username: `garason`
   - Password: `test123`

If this works, you're ready to share with colleagues!

---

## 👥 Colleague Access Instructions

### **For Your Colleagues**

Share these instructions with your team:

---

**📧 Email Template:**

```
Subject: Access to Laser OS Application

Hi Team,

I've set up the Laser OS application on my computer for local network access.

🌐 Access URL:
http://192.168.88.31:5000

🔐 Login Credentials:
Username: garason
Password: test123

📋 Requirements:
- You must be connected to the office Wi-Fi network (192.168.88.x)
- Use any modern web browser (Chrome, Firefox, Edge)
- My computer must be running and the server must be started

⚠️ Important Notes:
- This is a development server - please save your work frequently
- If you can't connect, let me know and I'll check if the server is running
- The application is only accessible within our office network

Let me know if you have any issues!
```

---

### **Troubleshooting for Colleagues**

If colleagues can't access the application:

1. **Check they're on the same network:**
   - They should be connected to the same Wi-Fi network
   - Their IP should be `192.168.88.x` (same subnet)

2. **Verify server is running:**
   - Check your terminal - server should be active
   - Look for "Running on http://192.168.88.31:5000"

3. **Test from your computer first:**
   - Navigate to `http://192.168.88.31:5000` on your machine
   - If it doesn't work for you, it won't work for others

4. **Check firewall rule:**
   - Run: `Get-NetFirewallRule -DisplayName "Laser OS*"` in PowerShell
   - Should show enabled rule for port 5000

---

## 🔒 Security Considerations

### **What's Protected**

✅ **Firewall configured for Private/Domain networks only**
- Public networks are blocked
- Only devices on your local network can access

✅ **Not exposed to the internet**
- Only accessible within your office network (192.168.88.x)
- External internet users cannot access

✅ **Authentication required**
- Users must log in with valid credentials
- Flask-Login session management

### **What's NOT Protected**

⚠️ **Development server limitations:**
- Flask development server is NOT production-ready
- No HTTPS/SSL encryption (traffic is unencrypted on local network)
- Limited concurrent user support
- No rate limiting or DDoS protection

⚠️ **Shared credentials:**
- Test account (garason/test123) is shared
- All users will appear as the same user in logs
- Consider creating individual user accounts for production use

### **Recommendations**

1. **For Development/Testing Only:**
   - This setup is suitable for development and testing
   - Do NOT use for production or sensitive data

2. **Create Individual User Accounts:**
   - Each colleague should have their own login
   - Better audit trails and access control

3. **Consider Production Deployment:**
   - For production use, deploy with:
     - Gunicorn or uWSGI (production WSGI server)
     - Nginx reverse proxy
     - HTTPS/SSL certificates
     - Proper authentication and authorization

---

## 📡 Static IP Configuration (Optional)

### **Why You Might Need This**

If your computer's IP address changes frequently (DHCP), colleagues will need to use a new URL each time. Setting a static IP prevents this.

### **Current Setup**

- **Current IP:** 192.168.88.31 (DHCP assigned)
- **Router:** 192.168.88.1
- **Subnet:** 255.255.255.0

### **How to Set Static IP**

1. **Open Network Settings:**
   - Press `Win + I` (Settings)
   - Go to "Network & Internet" → "Wi-Fi"
   - Click your network name
   - Scroll down and click "Edit" under IP assignment

2. **Configure Static IP:**
   - Change from "Automatic (DHCP)" to "Manual"
   - Enable IPv4
   - Enter:
     - **IP address:** `192.168.88.31` (your current IP)
     - **Subnet mask:** `255.255.255.0`
     - **Gateway:** `192.168.88.1`
     - **Preferred DNS:** `192.168.88.1` (or `8.8.8.8` for Google DNS)
   - Click "Save"

3. **Verify:**
   - Run `ipconfig` in Command Prompt
   - IP should still be `192.168.88.31`
   - Test connectivity: `ping 192.168.88.1`

### **Recommendation**

⚠️ **Only set static IP if:**
- Your IP changes frequently
- Colleagues complain about URL changing
- You're running the server long-term

✅ **For now, DHCP is fine:**
- Most routers assign the same IP to the same device
- Your IP will likely stay `192.168.88.31` for weeks/months

---

## 🧪 Testing Checklist

### **Before Sharing with Colleagues**

- [ ] Flask server is running (`python run.py`)
- [ ] Firewall rule is created and enabled
- [ ] You can access `http://192.168.88.31:5000` from your computer
- [ ] Login works with test credentials (garason/test123)
- [ ] You've tested from another device on the network (if available)

### **When Colleague Reports Issue**

1. [ ] Verify server is running (check terminal)
2. [ ] Verify your IP hasn't changed (`ipconfig`)
3. [ ] Test access from your computer (`http://192.168.88.31:5000`)
4. [ ] Check firewall rule is enabled
5. [ ] Verify colleague is on same network (192.168.88.x)
6. [ ] Ask colleague to try different browser

---

## 📞 Support & Troubleshooting

### **Common Issues**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Can't reach this page" | Server not running | Start server: `python run.py` |
| "Connection refused" | Firewall blocking | Run firewall script as Admin |
| "Connection timeout" | Different network | Verify colleague is on 192.168.88.x |
| IP changed | DHCP reassignment | Check new IP with `ipconfig`, update URL |
| Login fails | Wrong credentials | Use garason/test123 |

### **Quick Diagnostics**

**On your computer:**
```cmd
# Check if server is listening on port 5000
netstat -an | findstr :5000

# Should show:
# TCP    0.0.0.0:5000           0.0.0.0:0              LISTENING
```

**From colleague's computer:**
```cmd
# Test network connectivity
ping 192.168.88.31

# Test port connectivity (if telnet is enabled)
telnet 192.168.88.31 5000
```

---

## 📚 Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **Windows Firewall Guide:** https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/
- **Network Troubleshooting:** Run `ipconfig /all` for detailed network info

---

## ✅ Summary

1. ✅ **Flask is configured** to accept network connections (`host='0.0.0.0'`)
2. 🔥 **Configure Windows Firewall** using the provided script
3. 🌐 **Share URL** with colleagues: `http://192.168.88.31:5000`
4. 🔐 **Provide credentials:** garason / test123
5. 🧪 **Test thoroughly** before sharing widely

**Your application is now accessible to your office network!** 🎉

