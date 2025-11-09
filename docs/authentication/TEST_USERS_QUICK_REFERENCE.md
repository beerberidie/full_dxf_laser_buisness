# Test User Accounts - Quick Reference

## 🔐 Login Credentials

### Administrator (Full Access)
```
Username: garason
Password: Admin123!
Role: Administrator (Superuser)
```
**Can do:** Everything - full system access, user management, all features

---

### Manager (Business Management)
```
Username: kieran
Password: Manager123!
Role: Manager
```
**Can do:** Create/edit clients, projects, products, quotes, invoices, export reports  
**Cannot do:** Access admin panel, manage users

---

### Operator (Production Management)
```
Username: operator1
Password: Operator123!
Role: Operator
```
**Can do:** Manage queue, log laser runs, adjust inventory, upload files, create communications  
**Cannot do:** Create/edit clients, projects, products, export reports, access admin panel

---

### Viewer (Read-Only)
```
Username: viewer1
Password: Viewer123!
Role: Viewer
```
**Can do:** View all data (clients, projects, products, queue, inventory, reports)  
**Cannot do:** Any create, edit, or delete actions

---

## 🌐 Application URL

**Local:** http://127.0.0.1:5000  
**Network:** http://192.168.1.7:5000

---

## 🧪 Quick Test Scenarios

### Test 1: Admin Access
1. Login as `garason` / `Admin123!`
2. Click "Admin" in navigation
3. View user list
4. Try creating a new user
5. View login history

### Test 2: Manager Restrictions
1. Login as `kieran` / `Manager123!`
2. Verify "Admin" link is NOT visible
3. Try accessing `/admin/users` directly (should get 403)
4. Create a new client (should work)
5. Export a report (should work)

### Test 3: Operator Production Focus
1. Login as `operator1` / `Operator123!`
2. Go to Projects
3. Verify "New Project" button is NOT visible
4. Verify "Log Laser Run" button IS visible
5. Go to Queue and update a status (should work)
6. Try accessing `/projects/new` directly (should get 403)

### Test 4: Viewer Read-Only
1. Login as `viewer1` / `Viewer123!`
2. Navigate through all modules
3. Verify NO action buttons are visible
4. Try accessing `/clients/new` directly (should get 403)
5. Verify all data is viewable

---

## 📊 Permission Matrix (Quick View)

| Action                  | Admin | Manager | Operator | Viewer |
|-------------------------|-------|---------|----------|--------|
| View Data               | ✅    | ✅      | ✅       | ✅     |
| Create/Edit Business    | ✅    | ✅      | ❌       | ❌     |
| Manage Production       | ✅    | ✅      | ✅       | ❌     |
| Export Reports          | ✅    | ✅      | ❌       | ❌     |
| Manage Users            | ✅    | ❌      | ❌       | ❌     |

---

## 🔧 Admin Functions

### Create New User
1. Login as admin
2. Go to Admin → Users
3. Click "New User"
4. Fill in details
5. Select roles
6. Set password
7. Save

### Reset User Password
1. Login as admin
2. Go to Admin → Users
3. Click on user
4. Click "Reset Password"
5. Enter new password
6. Save

### Unlock Account
1. Login as admin
2. Go to Admin → Users
3. Find locked user (yellow "Locked" badge)
4. Click on user
5. Click "Unlock Account"

### View Login History
1. Login as admin
2. Go to Admin → Login History
3. View all login attempts
4. Filter by success/failure

---

## 🚨 Security Features

- **Password Requirements:** Min 8 chars, uppercase, lowercase, number, special character
- **Account Lockout:** 5 failed attempts = 30 minute lock
- **Session Security:** Automatic logout on browser close (unless "Remember Me" checked)
- **Admin Safeguards:** Cannot delete own account or last admin

---

## 📝 Notes

- All passwords follow the pattern: `[Role]123!` (e.g., Admin123!, Manager123!)
- Test users are for development/testing only
- Change passwords before production deployment
- Admin user `garason` is marked as superuser
- Login history tracks all attempts with IP and user agent

---

**Created:** October 18, 2025  
**Last Updated:** October 18, 2025

