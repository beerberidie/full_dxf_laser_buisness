# 🚀 Laser OS - Quick Access Guide

## For Server Administrator (You)

### **Start the Server**
```cmd
cd "C:\Users\Garas\Documents\augment-projects\full_dxf_laser_buisness"
python run.py
```

### **Configure Firewall (One-Time Setup)**
```powershell
# Run PowerShell as Administrator
.\scripts\configure_firewall.ps1
```

### **Check Your IP Address**
```cmd
ipconfig
```
Look for: **Wi-Fi adapter → IPv4 Address: 192.168.88.31**

---

## For Colleagues (Users)

### **Access URL**
```
http://192.168.88.31:5000
```

### **Login Credentials**
- **Username:** `garason`
- **Password:** `test123`

### **Requirements**
- ✅ Connected to office Wi-Fi (192.168.88.x network)
- ✅ Modern web browser (Chrome, Firefox, Edge)
- ✅ Server must be running on administrator's computer

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect | Ask admin if server is running |
| Wrong IP | Admin: run `ipconfig` to check current IP |
| Login fails | Use credentials: garason / test123 |
| Slow/timeout | Check you're on office Wi-Fi (192.168.88.x) |

---

## Quick Commands

### **Check if server is running (Admin)**
```cmd
netstat -an | findstr :5000
```

### **Test connectivity (User)**
```cmd
ping 192.168.88.31
```

### **Verify firewall rule (Admin)**
```powershell
Get-NetFirewallRule -DisplayName "Laser OS*"
```

---

**📧 Questions?** Contact the server administrator (Garas)

**🔒 Security:** Local network only - not accessible from internet

