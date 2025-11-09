# Authentication & Authorization Testing Plan

## Test User Accounts

The following test user accounts have been created:

| Username   | Password      | Role          | Description                    |
|------------|---------------|---------------|--------------------------------|
| garason    | Admin123!     | Administrator | Full system access (superuser) |
| kieran     | Manager123!   | Manager       | Business management access     |
| operator1  | Operator123!  | Operator      | Production management access   |
| viewer1    | Viewer123!    | Viewer        | Read-only access               |

## Permission Matrix

| Feature/Action                  | Admin | Manager | Operator | Viewer |
|---------------------------------|-------|---------|----------|--------|
| **Dashboard**                   |       |         |          |        |
| View Dashboard                  | ✅    | ✅      | ✅       | ✅     |
| Quick Actions (New buttons)     | ✅    | ✅      | ❌       | ❌     |
|                                 |       |         |          |        |
| **Clients**                     |       |         |          |        |
| View Clients List               | ✅    | ✅      | ✅       | ✅     |
| View Client Details             | ✅    | ✅      | ✅       | ✅     |
| Create New Client               | ✅    | ✅      | ❌       | ❌     |
| Edit Client                     | ✅    | ✅      | ❌       | ❌     |
| Delete Client                   | ✅    | ✅      | ❌       | ❌     |
|                                 |       |         |          |        |
| **Projects**                    |       |         |          |        |
| View Projects List              | ✅    | ✅      | ✅       | ✅     |
| View Project Details            | ✅    | ✅      | ✅       | ✅     |
| Create New Project              | ✅    | ✅      | ❌       | ❌     |
| Edit Project                    | ✅    | ✅      | ❌       | ❌     |
| Delete Project                  | ✅    | ✅      | ❌       | ❌     |
| Log Laser Run                   | ✅    | ✅      | ✅       | ❌     |
| Add to Queue                    | ✅    | ✅      | ✅       | ❌     |
|                                 |       |         |          |        |
| **Products**                    |       |         |          |        |
| View Products List              | ✅    | ✅      | ✅       | ✅     |
| View Product Details            | ✅    | ✅      | ✅       | ✅     |
| Create New Product              | ✅    | ✅      | ❌       | ❌     |
| Edit Product                    | ✅    | ✅      | ❌       | ❌     |
| Delete Product                  | ✅    | ✅      | ❌       | ❌     |
|                                 |       |         |          |        |
| **Queue**                       |       |         |          |        |
| View Queue                      | ✅    | ✅      | ✅       | ✅     |
| Update Queue Status             | ✅    | ✅      | ✅       | ❌     |
| Remove from Queue               | ✅    | ✅      | ❌       | ❌     |
| Reorder Queue                   | ✅    | ✅      | ✅       | ❌     |
|                                 |       |         |          |        |
| **Inventory**                   |       |         |          |        |
| View Inventory                  | ✅    | ✅      | ✅       | ✅     |
| Add Inventory Item              | ✅    | ✅      | ❌       | ❌     |
| Edit Inventory Item             | ✅    | ✅      | ❌       | ❌     |
| Adjust Stock                    | ✅    | ✅      | ✅       | ❌     |
|                                 |       |         |          |        |
| **Quotes & Invoices**           |       |         |          |        |
| View Quotes/Invoices            | ✅    | ✅      | ✅       | ✅     |
| Create Quote/Invoice            | ✅    | ✅      | ❌       | ❌     |
| Edit Quote/Invoice              | ✅    | ✅      | ❌       | ❌     |
|                                 |       |         |          |        |
| **Communications**              |       |         |          |        |
| View Communications             | ✅    | ✅      | ✅       | ✅     |
| New Communication               | ✅    | ✅      | ✅       | ❌     |
|                                 |       |         |          |        |
| **Presets**                     |       |         |          |        |
| View Presets                    | ✅    | ✅      | ✅       | ✅     |
| Add/Edit/Delete Preset          | ✅    | ✅      | ❌       | ❌     |
|                                 |       |         |          |        |
| **Reports**                     |       |         |          |        |
| View Reports                    | ✅    | ✅      | ✅       | ✅     |
| Export CSV                      | ✅    | ✅      | ❌       | ❌     |
|                                 |       |         |          |        |
| **Admin**                       |       |         |          |        |
| Access Admin Panel              | ✅    | ❌      | ❌       | ❌     |
| Manage Users                    | ✅    | ❌      | ❌       | ❌     |

## Manual Testing Checklist

### Test 1: Administrator (garason / Admin123!)

**Login Test:**
- [ ] Can log in successfully
- [ ] Redirected to dashboard
- [ ] User menu shows "garason" and "ADMINISTRATOR"
- [ ] "Admin" link visible in navigation

**UI Visibility Test:**
- [ ] Dashboard: "New Client", "New Project", "New Product" buttons visible
- [ ] Clients: "New Client" button visible
- [ ] Projects: "New Project", "Edit", "Delete" buttons visible
- [ ] Products: "New Product", "Edit", "Delete" buttons visible
- [ ] Queue: "Remove" button visible
- [ ] Inventory: "Add Inventory Item", "Edit", "Adjust Stock" visible
- [ ] Reports: "Export CSV" button visible
- [ ] Presets: "Add Preset", "Edit", "Delete" buttons visible

**Route Access Test:**
- [ ] Can access /admin/users
- [ ] Can access /clients/new
- [ ] Can access /projects/new
- [ ] Can access /products/new
- [ ] Can access /inventory/new
- [ ] Can access /presets/new

**Admin Functions:**
- [ ] Can view user list
- [ ] Can create new user
- [ ] Can edit user
- [ ] Can reset password
- [ ] Can view login history

### Test 2: Manager (kieran / Manager123!)

**Login Test:**
- [ ] Can log in successfully
- [ ] Redirected to dashboard
- [ ] User menu shows "kieran" and "MANAGER"
- [ ] "Admin" link NOT visible in navigation

**UI Visibility Test:**
- [ ] Dashboard: "New Client", "New Project", "New Product" buttons visible
- [ ] Clients: "New Client" button visible
- [ ] Projects: "New Project", "Edit", "Delete" buttons visible
- [ ] Products: "New Product", "Edit", "Delete" buttons visible
- [ ] Queue: "Remove" button visible
- [ ] Inventory: "Add Inventory Item", "Edit", "Adjust Stock" visible
- [ ] Reports: "Export CSV" button visible
- [ ] Presets: "Add Preset", "Edit", "Delete" buttons visible

**Route Access Test:**
- [ ] CANNOT access /admin/users (403 Forbidden)
- [ ] Can access /clients/new
- [ ] Can access /projects/new
- [ ] Can access /products/new
- [ ] Can access /inventory/new
- [ ] Can access /presets/new

### Test 3: Operator (operator1 / Operator123!)

**Login Test:**
- [ ] Can log in successfully
- [ ] Redirected to dashboard
- [ ] User menu shows "operator1" and "OPERATOR"
- [ ] "Admin" link NOT visible in navigation

**UI Visibility Test:**
- [ ] Dashboard: "New Client", "New Project", "New Product" buttons NOT visible
- [ ] Clients: "New Client" button NOT visible
- [ ] Clients: "Edit" button NOT visible in list
- [ ] Projects: "New Project" button NOT visible
- [ ] Projects: "Edit", "Delete" buttons NOT visible
- [ ] Projects: "Log Laser Run", "Add to Queue" buttons VISIBLE
- [ ] Products: "New Product" button NOT visible
- [ ] Products: "Edit", "Delete" buttons NOT visible
- [ ] Queue: "Remove" button NOT visible
- [ ] Queue: "Update Status" form VISIBLE
- [ ] Inventory: "Add Inventory Item" button NOT visible
- [ ] Inventory: "Edit" button NOT visible
- [ ] Inventory: "Adjust Stock" form VISIBLE
- [ ] Reports: "Export CSV" button NOT visible
- [ ] Presets: "Add Preset" button NOT visible
- [ ] Communications: "New Communication" button VISIBLE

**Route Access Test:**
- [ ] CANNOT access /admin/users (403 Forbidden)
- [ ] CANNOT access /clients/new (403 Forbidden)
- [ ] CANNOT access /projects/new (403 Forbidden)
- [ ] CANNOT access /products/new (403 Forbidden)
- [ ] CANNOT access /inventory/new (403 Forbidden)
- [ ] CANNOT access /presets/new (403 Forbidden)
- [ ] Can access /queue/
- [ ] Can access /comms/new

### Test 4: Viewer (viewer1 / Viewer123!)

**Login Test:**
- [ ] Can log in successfully
- [ ] Redirected to dashboard
- [ ] User menu shows "viewer1" and "VIEWER"
- [ ] "Admin" link NOT visible in navigation

**UI Visibility Test:**
- [ ] Dashboard: "New Client", "New Project", "New Product" buttons NOT visible
- [ ] Clients: "New Client" button NOT visible
- [ ] Clients: "Edit" button NOT visible in list
- [ ] Projects: "New Project" button NOT visible
- [ ] Projects: "Edit", "Delete", "Log Laser Run", "Add to Queue" buttons NOT visible
- [ ] Products: "New Product" button NOT visible
- [ ] Products: "Edit", "Delete" buttons NOT visible
- [ ] Queue: "Remove" button NOT visible
- [ ] Queue: "Update Status" form NOT visible
- [ ] Inventory: "Add Inventory Item" button NOT visible
- [ ] Inventory: "Edit" button NOT visible
- [ ] Inventory: "Adjust Stock" form NOT visible
- [ ] Reports: "Export CSV" button NOT visible
- [ ] Presets: "Add Preset", "Edit", "Delete" buttons NOT visible
- [ ] Communications: "New Communication" button NOT visible

**Route Access Test:**
- [ ] CANNOT access /admin/users (403 Forbidden)
- [ ] CANNOT access /clients/new (403 Forbidden)
- [ ] CANNOT access /projects/new (403 Forbidden)
- [ ] CANNOT access /products/new (403 Forbidden)
- [ ] CANNOT access /inventory/new (403 Forbidden)
- [ ] CANNOT access /presets/new (403 Forbidden)
- [ ] CANNOT access /comms/new (403 Forbidden)
- [ ] Can access / (dashboard)
- [ ] Can access /clients/ (view only)
- [ ] Can access /projects/ (view only)
- [ ] Can access /products/ (view only)
- [ ] Can access /queue/ (view only)
- [ ] Can access /inventory/ (view only)
- [ ] Can access /reports/production (view only)

## Expected Results

### Administrator
- ✅ Full access to all features
- ✅ Can see all action buttons
- ✅ Can access admin panel
- ✅ Can manage users

### Manager
- ✅ Full business management access
- ✅ Can create/edit/delete business records
- ✅ Can export reports
- ❌ Cannot access admin panel

### Operator
- ✅ Can view all data
- ✅ Can manage production (queue, runs, stock adjustments)
- ✅ Can create communications
- ❌ Cannot create/edit business records (clients, projects, products)
- ❌ Cannot export reports
- ❌ Cannot access admin panel

### Viewer
- ✅ Can view all data
- ❌ Cannot perform any create/edit/delete actions
- ❌ Cannot access production management
- ❌ Cannot export reports
- ❌ Cannot access admin panel

## Testing Instructions

1. Open browser to http://127.0.0.1:5000
2. For each user role:
   - Log out if currently logged in
   - Log in with test credentials
   - Navigate through each module
   - Verify UI buttons match expected visibility
   - Try to access restricted routes directly
   - Verify proper 403 Forbidden responses
   - Check that user experience is clean and intuitive
3. Document any discrepancies or issues
4. Test edge cases (e.g., trying to access edit routes by URL)

## Success Criteria

- ✅ All users can log in successfully
- ✅ UI buttons are shown/hidden based on role
- ✅ Route protection prevents unauthorized access
- ✅ 403 errors are returned for forbidden routes
- ✅ User experience is clean for all roles
- ✅ No broken links or confusing UI elements
- ✅ Login history is tracked correctly

