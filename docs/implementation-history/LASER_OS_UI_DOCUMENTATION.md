# Laser OS - Complete UI Structure & Functionality Documentation
+
**Generated:** 2025-10-20  
**Application:** Laser OS Tier 1 - Laser Cutting Operations System  
**Version:** Phase 10 (Complete)

---

## Table of Contents

1. [Navigation Structure](#navigation-structure)
2. [Authentication & User Management](#authentication--user-management)
3. [Dashboard](#dashboard)
4. [Clients Module](#clients-module)
5. [Projects Module](#projects-module)
6. [Products Module](#products-module)
7. [Queue Module](#queue-module)
8. [Inventory Module](#inventory-module)
9. [Reports Module](#reports-module)
10. [Sage Information (Quotes & Invoices)](#sage-information-quotes--invoices)
11. [Communications Module](#communications-module)
12. [Presets Module](#presets-module)
13. [Admin Module](#admin-module)
14. [Automated Workflows](#automated-workflows)

---

## Navigation Structure

### Sidebar Navigation (Collapsible)
**Location:** Left side of screen  
**Features:** 
- Collapsible with hamburger toggle button
- Icon-only mode when collapsed
- localStorage persistence of state
- Mobile responsive

**Navigation Items:**

| Icon | Label | Route | Access Level |
|------|-------|-------|--------------|
| 📊 | Dashboard | `/` | All authenticated users |
| 👥 | Clients | `/clients` | All authenticated users |
| 📁 | Projects | `/projects` | All authenticated users |
| 📦 | Products | `/products` | All authenticated users |
| ⏱️ | Queue | `/queue` | All authenticated users |
| ⚙️ | Presets | `/presets` | All authenticated users |
| 📋 | Inventory | `/inventory` | All authenticated users |
| 📈 | Reports | `/reports` | All authenticated users |
| 💼 | **Sage Information** (Expandable) | - | - |
| ├─ 💰 | Quotes | `/quotes` | All authenticated users |
| └─ 🧾 | Invoices | `/invoices` | All authenticated users |
| ✉️ | **Communications** (Expandable) | - | - |
| ├─ 📧 | Gmail | `/communications?channel=gmail` | All authenticated users |
| ├─ 📨 | Outlook | `/communications?channel=outlook` | All authenticated users |
| ├─ 💬 | WhatsApp | `/communications?channel=whatsapp` | All authenticated users |
| ├─ 👥 | Teams | `/communications?channel=teams` | All authenticated users |
| └─ 📝 | Templates | `/comms/templates` | Admin, Manager, Operator |
| 🔧 | Admin | `/admin` | Admin & Superuser only |

**Header:**
- Logo: "Laser COS"
- User menu (right side):
  - Current user name
  - Profile link → `/auth/profile`
  - Change Password → `/auth/change-password`
  - Logout → `/auth/logout`

---

## Authentication & User Management

### Login Page
**Route:** `/auth/login`  
**Access:** Public (unauthenticated users)

**Display:**
- Login form with username and password fields
- "Remember Me" checkbox
- Submit button

**Interactive Elements:**
1. **Username Field** (text input)
   - Required field
   
2. **Password Field** (password input)
   - Required field
   
3. **Remember Me Checkbox**
   - Persists login session
   
4. **Login Button**
   - **Action:** Authenticates user
   - **Backend Process:**
     - Validates credentials
     - Checks account status (active/locked)
     - Tracks failed login attempts (locks after 5 failures for 30 minutes)
     - Creates login history record
     - Redirects to dashboard on success
   - **Database Changes:** Updates `users.last_login`, `users.failed_login_attempts`, creates `login_history` record

**Security Features:**
- Account lockout after 5 failed attempts (30 minutes)
- Login history tracking (IP address, user agent, timestamp)
- Session management

---

### Profile Page
**Route:** `/auth/profile`  
**Access:** All authenticated users

**Display:**
- User information (username, email, full name, roles)
- Recent login history (last 10 logins)
- Account status

**Interactive Elements:**
1. **Change Password Button** → Navigates to `/auth/change-password`
2. **Recent Logins Table** (read-only display)
   - Shows: Login time, IP address, logout time

---

### Change Password Page
**Route:** `/auth/change-password`  
**Access:** All authenticated users

**Display:**
- Password change form

**Interactive Elements:**
1. **Current Password Field** (password input)
   - Required, validates against stored password
   
2. **New Password Field** (password input)
   - Required, must meet password requirements
   
3. **Confirm New Password Field** (password input)
   - Required, must match new password
   
4. **Change Password Button**
   - **Action:** Updates user password
   - **Database Changes:** Updates `users.password_hash`
   - **Redirects to:** Profile page

---

## Dashboard

**Route:** `/`  
**Access:** All authenticated users

### Statistics Cards Section
**Display:** 5 stat cards in a grid

1. **Total Clients Card**
   - Shows: Count of all clients
   - Subtitle: "in database"

2. **Total Projects Card**
   - Shows: Count of all projects
   - Subtitle: "{X} active" (Approved + In Progress)

3. **Total Products Card**
   - Shows: Count of all products
   - Subtitle: "SKUs in catalog"

4. **Design Files Card**
   - Shows: Count of uploaded DXF files
   - Subtitle: "DXF files uploaded"

5. **Queue Length Card**
   - Shows: Count of queued + in-progress items
   - Subtitle: "jobs waiting"

### Recent Clients Section
**Display:** Table showing last 5 clients

**Columns:** Code, Name, Created Date

**Interactive Elements:**
1. **Client Code Links** → Navigate to `/clients/{id}` (client detail page)
2. **View All Button** → Navigates to `/clients` (clients list page)
3. **+ Create First Client Button** (if no clients exist, Admin/Manager only) → Navigates to `/clients/new`

### Recent Projects Section
**Display:** Table showing last 5 projects

**Columns:** Code, Name, Status (with badge)

**Interactive Elements:**
1. **Project Code Links** → Navigate to `/projects/{id}` (project detail page)
2. **View All Button** → Navigates to `/projects` (projects list page)
3. **+ Create First Project Button** (if no projects exist) → Navigates to `/projects/new`

### Recent Products Section
**Display:** Table showing last 5 products

**Columns:** SKU Code, Name, Material, Price

**Interactive Elements:**
1. **SKU Code Links** → Navigate to `/products/{id}` (product detail page)
2. **View All Button** → Navigates to `/products` (products list page)
3. **+ Create First Product Button** (if no products exist) → Navigates to `/products/new`

### Recent Files Section
**Display:** Table showing last 5 uploaded files

**Columns:** Filename, Project, Size (MB), Uploaded Date

**Interactive Elements:**
1. **Filename Links** → Navigate to `/files/{file_id}` (file detail page)
2. **Project Links** → Navigate to `/projects/{id}` (project detail page)

### Quick Actions Section
**Display:** Grid of action buttons

**Interactive Elements (Admin/Manager only):**
1. **+ New Client Button** → Navigates to `/clients/new`
2. **+ New Project Button** → Navigates to `/projects/new`
3. **+ New Product Button** → Navigates to `/products/new`
4. **View Projects Button** (all users) → Navigates to `/projects`

### Production Queue Section
**Display:** Table showing next 5 queue items

**Columns:** Position, Project, Priority (badge), Status (badge), Scheduled Date

**Interactive Elements:**
1. **Project Links** → Navigate to `/projects/{id}`
2. **View All Button** → Navigates to `/queue`

### Inventory Status Section
**Display:** Inventory statistics and low stock alert

**Statistics:**
- Total Items count
- Low Stock Items count (highlighted if > 0)
- View Low Stock button

**Interactive Elements:**
1. **View Low Stock Button** → Navigates to `/inventory/low_stock`
2. **View All Button** → Navigates to `/inventory`
3. **Low Stock Alert** (if items below reorder level) → Link to `/inventory/low_stock`

---

## Clients Module

### Clients List Page
**Route:** `/clients`  
**Access:** All authenticated users

**Display:**
- Search/filter form
- Paginated table of clients (50 per page)

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Name, Client Code, Contact Person, Email
   
2. **Search Button**
   - **Action:** Filters client list
   - **Database Query:** Applies LIKE filter to client fields
   
3. **Clear Button** → Resets filters

**Clients Table:**
**Columns:** Client Code, Name, Contact Person, Email, Phone, Created Date, Actions

**Interactive Elements:**
1. **Client Code Links** → Navigate to `/clients/{id}` (detail page)
2. **View Button** (each row) → Navigate to `/clients/{id}`
3. **Edit Button** (each row, Admin/Manager only) → Navigate to `/clients/{id}/edit`
4. **Delete Button** (each row, Admin/Manager only)
   - **Action:** Deletes client (POST to `/clients/{id}/delete`)
   - **Database Changes:** Deletes client record, logs activity
   - **Validation:** May fail if client has associated projects

**Top Actions:**
1. **+ New Client Button** (Admin/Manager only) → Navigates to `/clients/new`

**Pagination:**
- Previous/Next buttons
- Page numbers

---

### New Client Page
**Route:** `/clients/new`
**Access:** Admin, Manager

**Display:**
- Client creation form

**Interactive Elements:**
1. **Name Field** (text input, required)
2. **Contact Person Field** (text input, optional)
3. **Email Field** (email input, optional)
4. **Phone Field** (text input, optional)
5. **Address Field** (textarea, optional)
6. **Notes Field** (textarea, optional)
7. **Create Client Button**
   - **Action:** Creates new client
   - **Backend Process:**
     - Generates unique client code (format: CL-XXXX)
     - Validates required fields
     - Creates client record
     - Logs activity
   - **Database Changes:** Inserts into `clients` table, creates `activity_log` entry
   - **Redirects to:** Client detail page (`/clients/{id}`)
8. **Cancel Button** → Navigates back to `/clients`

---

### Client Detail Page
**Route:** `/clients/{id}`
**Access:** All authenticated users

**Display:**
- Client information card
- Projects table (all projects for this client)
- Activity log

**Client Information Section:**
**Display Fields:**
- Client Code
- Name
- Contact Person
- Email
- Phone
- Address
- Notes
- Created Date

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Navigates to `/clients/{id}/edit`
2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes client (POST to `/clients/{id}/delete`)
   - **Database Changes:** Deletes client, logs activity
   - **Validation:** Checks for associated projects

**Projects Section:**
**Display:** Table of all projects for this client

**Columns:** Project Code, Name, Status, Due Date, Quoted Price, Actions

**Interactive Elements:**
1. **Project Code Links** → Navigate to `/projects/{id}`
2. **View Button** (each row) → Navigate to `/projects/{id}`
3. **+ New Project Button** (Admin/Manager only) → Navigates to `/projects/new?client_id={id}` (pre-fills client)

**Activity Log Section:**
**Display:** Recent 20 activities related to this client
- Shows: Timestamp, Action, Details, User

---

### Edit Client Page
**Route:** `/clients/{id}/edit`
**Access:** Admin, Manager

**Display:**
- Client edit form (pre-filled with current data)

**Interactive Elements:**
1. **Name Field** (text input, required)
2. **Contact Person Field** (text input, optional)
3. **Email Field** (email input, optional)
4. **Phone Field** (text input, optional)
5. **Address Field** (textarea, optional)
6. **Notes Field** (textarea, optional)
7. **Update Client Button**
   - **Action:** Updates client information
   - **Backend Process:**
     - Validates fields
     - Tracks changes for activity log
     - Updates client record
   - **Database Changes:** Updates `clients` table, creates `activity_log` entry
   - **Redirects to:** Client detail page
8. **Cancel Button** → Navigates back to client detail page

---

## Projects Module

### Projects List Page
**Route:** `/projects`
**Access:** All authenticated users

**Display:**
- Search/filter form
- Paginated table of projects (50 per page)

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Project Name, Project Code, Description

2. **Client Filter** (dropdown)
   - Options: All clients + individual client names

3. **Status Filter** (dropdown)
   - Options: All, Request, Quote Sent, Approved, In Progress, Complete, Cancelled, On Hold

4. **Apply Filters Button**
   - **Action:** Filters project list
   - **Database Query:** Applies filters to projects query

5. **Clear Filters Button** → Resets all filters

**Projects Table:**
**Columns:** Project Code, Name, Client, Status (badge), Due Date, Quoted Price, Actions

**Interactive Elements:**
1. **Project Code Links** → Navigate to `/projects/{id}`
2. **Client Links** → Navigate to `/clients/{client_id}`
3. **View Button** (each row) → Navigate to `/projects/{id}`
4. **Edit Button** (each row, Admin/Manager only) → Navigate to `/projects/{id}/edit`
5. **Delete Button** (each row, Admin/Manager only)
   - **Action:** Deletes project (POST to `/projects/{id}/delete`)
   - **Database Changes:** Deletes project, associated files, queue items, logs activity

**Top Actions:**
1. **+ New Project Button** (Admin/Manager only) → Navigates to `/projects/new`

**Pagination:**
- Previous/Next buttons
- Page numbers

---

### New Project Page
**Route:** `/projects/new`
**Access:** Admin, Manager

**Display:**
- Project creation form with multiple sections

**Basic Information Section:**
**Interactive Elements:**
1. **Client Dropdown** (required)
   - Lists all clients

2. **Project Name Field** (text input, required)

3. **Description Field** (textarea, optional)

4. **Status Dropdown** (required)
   - Options: Request, Quote Sent, Approved, In Progress, Complete, Cancelled, On Hold
   - Default: Request

**Dates Section:**
5. **Quote Date Field** (date picker, optional)
6. **Approval Date Field** (date picker, optional)
7. **Due Date Field** (date picker, optional)
8. **Scheduled Cut Date Field** (date picker, optional)

**Pricing Section:**
9. **Quoted Price Field** (number input, optional)

**Project Details Section (Phase 9 enhancements):**
10. **Material Type Dropdown** (optional)
    - Options from config: Mild Steel, Stainless Steel, Aluminum, Copper, Brass, etc.

11. **Material Thickness Field** (number input, optional)
    - Unit: mm

12. **Material Quantity (Sheets) Field** (number input, optional)

13. **Parts Quantity Field** (number input, optional)

14. **Estimated Cut Time Field** (number input, optional)
    - Unit: minutes

15. **Drawing Creation Time Field** (number input, optional)
    - Unit: minutes

16. **Number of Bins Field** (number input, optional)

**Additional Information:**
17. **Notes Field** (textarea, optional)

18. **Create Project Button**
    - **Action:** Creates new project
    - **Backend Process:**
      - Generates unique project code (format: {CLIENT_CODE}-PXXXX)
      - Validates required fields
      - Parses dates
      - Creates project record
      - Logs activity
    - **Database Changes:** Inserts into `projects` table, creates `activity_log` entry
    - **Redirects to:** Project detail page

19. **Cancel Button** → Navigates back to `/projects`

---

### Project Detail Page
**Route:** `/projects/{id}`
**Access:** All authenticated users

**Display:**
- Project information card
- Design files section
- Queue status section
- Activity log

**Project Information Section:**
**Display Fields:**
- Project Code
- Client (link to client detail)
- Name
- Description
- Status (badge with color coding)
- Quote Date
- Approval Date
- Due Date
- Scheduled Cut Date
- Quoted Price
- Material Type
- Material Thickness
- Material Quantity (Sheets)
- Parts Quantity
- Estimated Cut Time
- Drawing Creation Time
- Number of Bins
- Notes
- Created Date

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Navigates to `/projects/{id}/edit`

2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes project (POST to `/projects/{id}/delete`)
   - **Database Changes:** Deletes project, files, queue items, logs activity

3. **Mark POP Received Button** (Admin/Manager only, if not already received)
   - **Action:** Marks Proof of Payment as received (POST to `/projects/{id}/mark-pop-received`)
   - **Backend Process:**
     - Sets `pop_received = True`
     - Sets `pop_received_date = today`
     - Calculates `pop_deadline = today + 3 days`
     - **AUTOMATED WORKFLOW:** Triggers automatic queue addition with sensible defaults:
       - Priority: Normal
       - Scheduled Date: Today or next business day
       - Estimated Cut Time: From project's `estimated_cut_time`
   - **Database Changes:** Updates `projects` table, creates `queue_items` entry, logs activity
   - **Redirects to:** Project detail page with success message

4. **Add to Queue Button** (Admin/Manager/Operator, if not in queue)
   - Opens modal/form with queue options
   - See "Add to Queue Form" below

**Design Files Section:**
**Display:** Table of uploaded DXF/LBRN2 files

**Columns:** Filename, Type, Size, Upload Date, Actions

**Interactive Elements:**
1. **Filename Links** → Navigate to `/files/{file_id}`
2. **Download Button** (each row)
   - **Action:** Downloads file (GET `/files/download/{file_id}`)
   - **Backend Process:** Logs download activity, serves file

3. **Delete Button** (each row, Admin/Manager only)
   - **Action:** Deletes file (POST to `/files/delete/{file_id}`)
   - **Database Changes:** Deletes file record and physical file, logs activity

4. **Upload Files Button** (Admin/Manager/Operator)
   - Opens file upload form
   - **Form Fields:**
     - File input (multiple files supported, .dxf and .lbrn2 only)
     - Notes field (optional, applies to all uploaded files)
   - **Upload Action:** (POST to `/files/upload/{project_id}`)
     - **Backend Process:**
       - Validates file types
       - Generates unique stored filenames
       - Saves files to disk
       - Creates database records
       - Logs activity
     - **Database Changes:** Inserts into `design_files` table, creates `activity_log` entries

**Queue Status Section:**
**Display:** Current queue status for this project (if in queue)

**Shows:**
- Queue position
- Priority (badge)
- Status (badge)
- Scheduled date
- Estimated cut time

**Interactive Elements:**
1. **View Queue Item Button** → Navigates to `/queue/{queue_item_id}`

**Activity Log Section:**
**Display:** Recent activities related to this project
- Shows: Timestamp, Action, Details, User

---

### Edit Project Page
**Route:** `/projects/{id}/edit`
**Access:** Admin, Manager

**Display:**
- Project edit form (pre-filled with current data)
- Same fields as New Project page

**Interactive Elements:**
- All fields from New Project page (pre-filled)
- **Update Project Button**
  - **Action:** Updates project information
  - **Backend Process:**
    - Validates fields
    - Tracks changes for activity log
    - Updates project record
  - **Database Changes:** Updates `projects` table, creates `activity_log` entry
  - **Redirects to:** Project detail page
- **Cancel Button** → Navigates back to project detail page

---

### Add to Queue Form
**Triggered from:** Project detail page "Add to Queue" button
**Access:** Admin, Manager, Operator

**Display:**
- Modal or inline form with queue parameters

**Interactive Elements:**
1. **Priority Dropdown** (required)
   - Options: Low, Normal, High, Urgent
   - Default: Normal

2. **Scheduled Date Field** (date picker, optional)
   - Suggests today or next business day

3. **Estimated Cut Time Field** (number input, optional)
   - Pre-filled from project's `estimated_cut_time` if available
   - Unit: minutes

4. **Notes Field** (textarea, optional)

5. **Add to Queue Button**
   - **Action:** Adds project to production queue (POST to `/queue/add/{project_id}`)
   - **Backend Process:**
     - Validates POP deadline (warns if overdue)
     - Calculates next queue position
     - Creates queue item
     - Logs activity
   - **Database Changes:** Inserts into `queue_items` table, creates `activity_log` entry
   - **Redirects to:** Project detail page with success message

6. **Cancel Button** → Closes form

---

## Products Module

### Products List Page
**Route:** `/products`
**Access:** All authenticated users

**Display:**
- Search/filter form
- Paginated table of products (50 per page)

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Product Name, SKU Code, Description

2. **Material Filter** (dropdown)
   - Options: All + unique materials from database

3. **Apply Filters Button**
   - **Action:** Filters product list
   - **Database Query:** Applies filters to products query

4. **Clear Filters Button** → Resets filters

**Products Table:**
**Columns:** SKU Code, Name, Material, Thickness, Unit Price, Actions

**Interactive Elements:**
1. **SKU Code Links** → Navigate to `/products/{id}`
2. **View Button** (each row) → Navigate to `/products/{id}`
3. **Edit Button** (each row, Admin/Manager only) → Navigate to `/products/{id}/edit`
4. **Delete Button** (each row, Admin/Manager only)
   - **Action:** Deletes product (POST to `/products/{id}/delete`)
   - **Database Changes:** Deletes product (if not used in projects), logs activity
   - **Validation:** Checks for usage in active projects

**Top Actions:**
1. **+ New Product Button** (Admin/Manager only) → Navigates to `/products/new`

**Pagination:**
- Previous/Next buttons
- Page numbers

---

### New Product Page
**Route:** `/products/new`
**Access:** Admin, Manager

**Display:**
- Product creation form

**Interactive Elements:**
1. **Name Field** (text input, required)

2. **Description Field** (textarea, optional)

3. **Material Dropdown** (optional)
   - Options from settings: Mild Steel, Stainless Steel, Aluminum, etc.
   - Allows custom entry

4. **Thickness Field** (number input, optional)
   - Unit: mm
   - Dropdown with common values from settings

5. **Unit Price Field** (number input, optional)
   - Currency: ZAR (Rands)

6. **Notes Field** (textarea, optional)

7. **Create Product Button**
   - **Action:** Creates new product
   - **Backend Process:**
     - Auto-generates SKU code (format: SKU-XXXX)
     - Validates required fields
     - Creates product record
     - Logs activity
   - **Database Changes:** Inserts into `products` table, creates `activity_log` entry
   - **Redirects to:** Product detail page

8. **Cancel Button** → Navigates back to `/products`

---

### Product Detail Page
**Route:** `/products/{id}`
**Access:** All authenticated users

**Display:**
- Product information card
- Product files section (DXF/LBRN2 templates)
- Projects using this product
- Activity log

**Product Information Section:**
**Display Fields:**
- SKU Code
- Name
- Description
- Material
- Thickness
- Unit Price
- Notes
- Created Date

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Navigates to `/products/{id}/edit`

2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes product (POST to `/products/{id}/delete`)
   - **Database Changes:** Deletes product (if not used), logs activity
   - **Validation:** Checks for usage in projects

**Product Files Section:**
**Display:** Table of uploaded template files (DXF/LBRN2)

**Columns:** Filename, Type, Size, Upload Date, Actions

**Interactive Elements:**
1. **Download Button** (each row)
   - **Action:** Downloads file (GET `/products/file/{file_id}/download`)
   - **Backend Process:** Logs download activity, serves file

2. **Delete Button** (each row, Admin/Manager only)
   - **Action:** Deletes file (POST to `/products/file/{file_id}/delete`)
   - **Database Changes:** Deletes file record and physical file, logs activity

3. **Upload Files Button** (Admin/Manager/Operator)
   - Opens file upload form
   - **Form Fields:**
     - File input (multiple files supported, .dxf and .lbrn2 only)
     - Notes field (optional)
   - **Upload Action:** (POST to `/products/{product_id}/upload-file`)
     - **Backend Process:**
       - Validates file types
       - Generates unique stored filenames
       - Saves files to disk
       - Creates database records
       - Logs activity
     - **Database Changes:** Inserts into `product_files` table, creates `activity_log` entries

**Projects Using This Product Section:**
**Display:** Table of projects that include this product

**Columns:** Project Code, Client, Status, Quantity

**Interactive Elements:**
1. **Project Code Links** → Navigate to `/projects/{id}`

**Activity Log Section:**
**Display:** Recent 20 activities related to this product
- Shows: Timestamp, Action, Details, User

---

### Edit Product Page
**Route:** `/products/{id}/edit`
**Access:** Admin, Manager

**Display:**
- Product edit form (pre-filled with current data)
- Same fields as New Product page

**Interactive Elements:**
- All fields from New Product page (pre-filled)
- **Update Product Button**
  - **Action:** Updates product information
  - **Backend Process:**
    - Validates fields
    - Tracks changes for activity log
    - Updates product record
  - **Database Changes:** Updates `products` table, creates `activity_log` entry
  - **Redirects to:** Product detail page
- **Cancel Button** → Navigates back to product detail page

---

## Queue Module

### Queue Index Page
**Route:** `/queue`
**Access:** All authenticated users

**Display:**
- Statistics cards
- Filter options
- Queue items table

**Statistics Section:**
**Display:** 4 stat cards

1. **Total Queued Card** - Count of items with status "Queued"
2. **In Progress Card** - Count of items with status "In Progress"
3. **Completed Card** - Count of items with status "Completed"
4. **Total Active Card** - Queued + In Progress

**Filter Section:**
**Interactive Elements:**
1. **Status Filter** (tabs or dropdown)
   - Options: Active (default), All, Queued, In Progress, Completed
   - **Action:** Filters queue items
   - **Database Query:** Applies status filter

**Queue Items Table:**
**Columns:** Position, Project Code, Client, Priority (badge), Status (badge), Scheduled Date, Est. Cut Time, Actions

**Interactive Elements:**
1. **Project Code Links** → Navigate to `/projects/{id}`
2. **Client Links** → Navigate to `/clients/{id}`
3. **View Button** (each row) → Navigate to `/queue/{id}`
4. **Start Button** (each row, if status=Queued, Admin/Manager/Operator only)
   - **Action:** Changes status to "In Progress" (POST to `/queue/{id}/start`)
   - **Database Changes:** Updates `queue_items.status`, logs activity

5. **Complete Button** (each row, if status=In Progress, Admin/Manager/Operator only)
   - **Action:** Changes status to "Completed" (POST to `/queue/{id}/complete`)
   - **Database Changes:** Updates `queue_items.status`, sets completion date, logs activity

6. **Move Up/Down Buttons** (each row, Admin/Manager only)
   - **Action:** Adjusts queue position (POST to `/queue/{id}/move-up` or `/move-down`)
   - **Database Changes:** Updates `queue_position` for affected items

7. **Remove from Queue Button** (each row, Admin/Manager only)
   - **Action:** Removes item from queue (POST to `/queue/{id}/remove`)
   - **Database Changes:** Deletes queue item, logs activity

---

### Queue Item Detail Page
**Route:** `/queue/{id}`
**Access:** All authenticated users

**Display:**
- Queue item information
- Associated project details
- Laser runs for this queue item
- Activity log

**Queue Item Information:**
**Display Fields:**
- Queue Position
- Project (link)
- Priority (badge)
- Status (badge)
- Scheduled Date
- Estimated Cut Time
- Notes
- Added By
- Added Date

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Opens edit form
2. **Start Button** (if Queued, Admin/Manager/Operator) → Changes status to In Progress
3. **Complete Button** (if In Progress, Admin/Manager/Operator) → Changes status to Completed
4. **Remove from Queue Button** (Admin/Manager only) → Removes from queue

**Laser Runs Section:**
**Display:** Table of laser runs logged for this queue item

**Columns:** Run Date, Operator, Cut Time, Material, Sheets, Parts, Status

**Interactive Elements:**
1. **View Run Button** (each row) → Navigate to `/queue/runs/{run_id}`
2. **+ Log New Run Button** (Admin/Manager/Operator) → Navigate to `/queue/runs/new/{project_id}`

**Activity Log Section:**
**Display:** Activities related to this queue item

---

### Laser Runs Page
**Route:** `/queue/runs`
**Access:** All authenticated users

**Display:**
- Filter form
- Laser runs table (last 100 runs)

**Filter Section:**
**Interactive Elements:**
1. **Operator Filter** (dropdown)
   - Options: All + unique operators from database

2. **Date From Field** (date picker)
3. **Date To Field** (date picker)
4. **Apply Filters Button** → Filters runs
5. **Clear Filters Button** → Resets filters

**Laser Runs Table:**
**Columns:** Run Date, Project, Operator, Cut Time (min), Material, Thickness, Sheets, Parts, Status

**Interactive Elements:**
1. **Project Links** → Navigate to `/projects/{id}`
2. **View Button** (each row) → Navigate to `/queue/runs/{run_id}` (if detail page exists)

---

### New Laser Run Page
**Route:** `/queue/runs/new/{project_id}`
**Access:** Admin, Manager, Operator

**Display:**
- Laser run logging form

**Interactive Elements:**
1. **Project** (read-only display)
2. **Queue Item Dropdown** (optional)
   - Lists active queue items for this project

3. **Operator Dropdown** (required)
   - Lists all operators from database

4. **Run Date/Time Field** (datetime picker, required)
   - Default: Current date/time

5. **Cut Time (minutes) Field** (number input, required)

6. **Material Type Dropdown** (optional)
   - Pre-filled from project if available

7. **Material Thickness Field** (number input, optional)
   - Pre-filled from project if available

8. **Sheet Count Field** (number input, optional)

9. **Parts Produced Field** (number input, optional)

10. **Machine Settings Preset Dropdown** (optional)
    - Lists active presets matching material/thickness

11. **Status Dropdown** (required)
    - Options: Success, Failed, Partial
    - Default: Success

12. **Notes Field** (textarea, optional)

13. **Log Run Button**
    - **Action:** Creates laser run record (POST to `/queue/runs/new/{project_id}`)
    - **Backend Process:**
      - Validates fields
      - Creates laser run record
      - Updates queue item if selected
      - Logs activity
    - **Database Changes:** Inserts into `laser_runs` table, updates `queue_items` if applicable, creates `activity_log` entry
    - **Redirects to:** Project detail page or queue page

14. **Cancel Button** → Navigates back

---

## Inventory Module

### Inventory Index Page
**Route:** `/inventory`
**Access:** All authenticated users

**Display:**
- Statistics cards
- Search/filter form
- Inventory items table

**Statistics Section:**
**Display:** 4 stat cards

1. **Total Items Card** - Count of all inventory items
2. **Low Stock Count Card** - Count of items below reorder level (highlighted if > 0)
3. **Total Value Card** - Sum of stock values (quantity × unit cost)
4. **Categories Count Card** - Number of categories

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Item Code, Name, Material Type

2. **Category Filter** (dropdown)
   - Options: All, Sheet Metal, Gas, Consumables, Tools, Other

3. **Low Stock Only Checkbox**
   - Filters to show only items below reorder level

4. **Apply Filters Button** → Filters inventory
5. **Clear Filters Button** → Resets filters

**Inventory Items Table:**
**Columns:** Item Code, Name, Category (badge), Material/Type, Quantity, Unit, Reorder Level, Unit Cost, Stock Value, Status, Actions

**Interactive Elements:**
1. **Item Code Links** → Navigate to `/inventory/{id}`
2. **View Button** (each row) → Navigate to `/inventory/{id}`
3. **Edit Button** (each row, Admin/Manager only) → Navigate to `/inventory/{id}/edit`
4. **Adjust Stock Button** (each row, Admin/Manager/Operator) → Opens stock adjustment form

**Top Actions:**
1. **+ New Item Button** (Admin/Manager only) → Navigates to `/inventory/new`
2. **View Low Stock Button** → Navigates to `/inventory/low_stock`
3. **View Transactions Button** → Navigates to `/inventory/transactions`

**Row Highlighting:**
- Rows with low stock (quantity ≤ reorder level) are highlighted in yellow

---

### New Inventory Item Page
**Route:** `/inventory/new`
**Access:** Admin, Manager

**Display:**
- Inventory item creation form

**Interactive Elements:**
1. **Item Code Field** (text input, required)
   - Must be unique

2. **Name Field** (text input, required)

3. **Category Dropdown** (required)
   - Options: Sheet Metal, Gas, Consumables, Tools, Other

4. **Material Type Field** (text input, optional)
   - For Sheet Metal category

5. **Thickness Field** (number input, optional)
   - For Sheet Metal category
   - Unit: mm

6. **Unit Field** (text input, required)
   - Examples: sheets, kg, liters, pieces

7. **Quantity on Hand Field** (number input, required)
   - Default: 0

8. **Reorder Level Field** (number input, optional)
   - Threshold for low stock alerts

9. **Reorder Quantity Field** (number input, optional)
   - Suggested reorder amount

10. **Unit Cost Field** (number input, optional)
    - Currency: ZAR

11. **Supplier Name Field** (text input, optional)

12. **Supplier Contact Field** (text input, optional)

13. **Location Field** (text input, optional)
    - Physical storage location

14. **Notes Field** (textarea, optional)

15. **Create Item Button**
    - **Action:** Creates inventory item
    - **Backend Process:**
      - Validates required fields
      - Checks for duplicate item code
      - Creates inventory item
      - Logs activity
    - **Database Changes:** Inserts into `inventory_items` table, creates `activity_log` entry
    - **Redirects to:** Inventory item detail page

16. **Cancel Button** → Navigates back to `/inventory`

---

### Inventory Item Detail Page
**Route:** `/inventory/{id}`
**Access:** All authenticated users

**Display:**
- Item information card
- Stock status
- Recent transactions
- Activity log

**Item Information Section:**
**Display Fields:**
- Item Code
- Name
- Category (badge)
- Material Type
- Thickness
- Unit
- Quantity on Hand (highlighted if low stock)
- Reorder Level
- Reorder Quantity
- Unit Cost
- Stock Value (calculated: quantity × unit cost)
- Supplier Name
- Supplier Contact
- Location
- Notes
- Created Date

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Navigates to `/inventory/{id}/edit`

2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes inventory item (POST to `/inventory/{id}/delete`)
   - **Database Changes:** Deletes item, logs activity

3. **Adjust Stock Button** (Admin/Manager/Operator)
   - Opens stock adjustment form
   - **Form Fields:**
     - Transaction Type (dropdown): Purchase, Usage, Adjustment, Return
     - Quantity (number input, can be positive or negative)
     - Unit Cost (number input, for purchases)
     - Reference (text input, optional - PO number, job number, etc.)
     - Notes (textarea, optional)
   - **Adjust Action:** (POST to `/inventory/{id}/adjust`)
     - **Backend Process:**
       - Validates quantity
       - Updates quantity on hand
       - Creates transaction record
       - Logs activity
     - **Database Changes:** Updates `inventory_items.quantity_on_hand`, inserts into `inventory_transactions`, creates `activity_log` entry

**Recent Transactions Section:**
**Display:** Table of last 20 transactions for this item

**Columns:** Date, Type (badge), Quantity, Unit Cost, Value, Reference, Notes

**Interactive Elements:**
1. **View All Transactions Button** → Navigates to `/inventory/transactions?item_id={id}`

**Activity Log Section:**
**Display:** Recent activities related to this item

---

### Low Stock Page
**Route:** `/inventory/low_stock`
**Access:** All authenticated users

**Display:**
- Alert message
- Table of items below reorder level

**Alert:**
- Shows count of low stock items
- Highlighted warning style

**Low Stock Items Table:**
**Columns:** Item Code, Name, Category, Quantity, Reorder Level, Deficit, Reorder Qty, Actions

**Interactive Elements:**
1. **Item Code Links** → Navigate to `/inventory/{id}`
2. **View Button** (each row) → Navigate to `/inventory/{id}`
3. **Reorder Button** (each row, Admin/Manager only)
   - Opens quick reorder form or navigates to adjustment form

---

### Inventory Transactions Page
**Route:** `/inventory/transactions`
**Access:** All authenticated users

**Display:**
- Filter form
- Transactions table

**Filter Section:**
**Interactive Elements:**
1. **Item Filter** (dropdown)
   - Options: All + all inventory items

2. **Transaction Type Filter** (dropdown)
   - Options: All, Purchase, Usage, Adjustment, Return

3. **Date From Field** (date picker)
4. **Date To Field** (date picker)
5. **Apply Filters Button** → Filters transactions
6. **Clear Filters Button** → Resets filters

**Transactions Table:**
**Columns:** Date, Item, Type (badge), Quantity, Unit Cost, Total Value, Reference, Notes

**Interactive Elements:**
1. **Item Links** → Navigate to `/inventory/{id}`

---

## Reports Module

### Reports Index Page
**Route:** `/reports`
**Access:** All authenticated users

**Display:**
- Grid of report cards/links

**Available Reports:**
1. **Production Summary Card**
   - Description: Laser runs, cut time, materials used
   - **Link:** → Navigate to `/reports/production`

2. **Efficiency Metrics Card**
   - Description: Estimated vs actual times, efficiency analysis
   - **Link:** → Navigate to `/reports/efficiency`

3. **Inventory Report Card**
   - Description: Stock levels, usage, value
   - **Link:** → Navigate to `/reports/inventory`

4. **Client Report Card**
   - Description: Client profitability, project counts
   - **Link:** → Navigate to `/reports/clients`

---

### Production Summary Report
**Route:** `/reports/production`
**Access:** All authenticated users

**Display:**
- Date range filter
- Summary statistics
- Production data table
- Charts/graphs

**Filter Section:**
**Interactive Elements:**
1. **Date From Field** (date picker)
   - Default: 30 days ago

2. **Date To Field** (date picker)
   - Default: Today

3. **Generate Report Button** → Refreshes report with selected date range

**Summary Statistics:**
**Display:**
- Total Laser Runs
- Total Cut Time (hours)
- Total Sheets Used
- Total Parts Produced
- Average Cut Time per Run

**Production Data Table:**
**Columns:** Date, Project, Operator, Material, Thickness, Sheets, Parts, Cut Time (min), Status

**Interactive Elements:**
1. **Project Links** → Navigate to `/projects/{id}`
2. **Export to CSV Button** (Admin/Manager only)
   - **Action:** Downloads CSV file (GET `/reports/production/export?from={date}&to={date}`)
   - **Backend Process:** Generates CSV from filtered data

**Charts Section:**
**Display:**
- Cut time by operator (bar chart)
- Material usage breakdown (pie chart)
- Daily production trend (line chart)

---

### Efficiency Metrics Report
**Route:** `/reports/efficiency`
**Access:** All authenticated users

**Display:**
- Date range filter
- Efficiency statistics
- Comparison table

**Filter Section:**
**Interactive Elements:**
1. **Date From Field** (date picker)
2. **Date To Field** (date picker)
3. **Generate Report Button** → Refreshes report

**Efficiency Statistics:**
**Display:**
- Average Estimated Cut Time
- Average Actual Cut Time
- Overall Efficiency Percentage
- Projects On Time vs Delayed

**Efficiency Comparison Table:**
**Columns:** Project, Estimated Time, Actual Time, Variance, Efficiency %, Status

**Interactive Elements:**
1. **Project Links** → Navigate to `/projects/{id}`
2. **Export to CSV Button** → Downloads CSV

**Charts:**
- Efficiency trend over time
- Operator efficiency comparison

---

### Inventory Report
**Route:** `/reports/inventory`
**Access:** All authenticated users

**Display:**
- Inventory summary statistics
- Stock status table
- Usage analysis

**Summary Statistics:**
**Display:**
- Total Items
- Low Stock Items
- Total Inventory Value
- Most Used Items (top 5)

**Stock Status Table:**
**Columns:** Item, Category, Quantity, Reorder Level, Status, Value

**Interactive Elements:**
1. **Item Links** → Navigate to `/inventory/{id}`
2. **Export to CSV Button** → Downloads CSV

**Usage Analysis:**
**Display:**
- Material consumption by type
- Monthly usage trends

---

### Client Report
**Route:** `/reports/clients`
**Access:** All authenticated users

**Display:**
- Client statistics
- Client profitability table

**Summary Statistics:**
**Display:**
- Total Clients
- Active Clients (with projects in last 90 days)
- Total Revenue
- Average Project Value

**Client Profitability Table:**
**Columns:** Client, Total Projects, Active Projects, Total Revenue, Avg Project Value, Last Project Date

**Interactive Elements:**
1. **Client Links** → Navigate to `/clients/{id}`
2. **Export to CSV Button** → Downloads CSV

---

## Sage Information (Quotes & Invoices)

### Quotes List Page
**Route:** `/quotes`
**Access:** All authenticated users

**Display:**
- Search/filter form
- Quotes table

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Quote Number, Client Name

2. **Status Filter** (dropdown)
   - Options: All, Draft, Sent, Accepted, Rejected

3. **Apply Filters Button** → Filters quotes
4. **Clear Filters Button** → Resets filters

**Quotes Table:**
**Columns:** Quote Number, Client, Date, Total Amount, Status (badge), Actions

**Interactive Elements:**
1. **Quote Number Links** → Navigate to `/quotes/{id}`
2. **Client Links** → Navigate to `/clients/{id}`
3. **View Button** (each row) → Navigate to `/quotes/{id}`
4. **Edit Button** (each row, Admin/Manager only, if status=Draft) → Navigate to `/quotes/{id}/edit`
5. **Delete Button** (each row, Admin/Manager only, if status=Draft) → Deletes quote

**Top Actions:**
1. **+ New Quote Button** (Admin/Manager only) → Navigates to `/quotes/new`

---

### New Quote Page
**Route:** `/quotes/new`
**Access:** Admin, Manager

**Display:**
- Quote creation form with line items

**Interactive Elements:**
1. **Client Dropdown** (required)
   - Lists all clients

2. **Quote Date Field** (date picker, required)
   - Default: Today

3. **Valid Until Date Field** (date picker, optional)
   - Default: 30 days from quote date

4. **Status Dropdown** (required)
   - Options: Draft, Sent, Accepted, Rejected
   - Default: Draft

**Line Items Section:**
**Display:** Dynamic table of line items

**Columns:** Description, Quantity, Unit Price, Total, Actions

**Interactive Elements:**
5. **Add Line Item Button**
   - Adds new row to line items table
   - **Fields per line item:**
     - Description (text input, required)
     - Quantity (number input, required)
     - Unit Price (number input, required)
     - Total (calculated: quantity × unit price, read-only)
     - Remove button (deletes this line item)

6. **Remove Line Item Button** (each row)
   - Removes line item from quote

**Totals Section:**
**Display:**
- Subtotal (sum of all line items)
- Tax Rate field (number input, default: 15%)
- Tax Amount (calculated)
- Total Amount (calculated)

7. **Notes Field** (textarea, optional)

8. **Create Quote Button**
   - **Action:** Creates quote
   - **Backend Process:**
     - Auto-generates quote number (format: QT-{year}-{number})
     - Validates line items
     - Calculates totals
     - Creates quote and line items
     - Logs activity
   - **Database Changes:** Inserts into `quotes` and `quote_line_items` tables, creates `activity_log` entry
   - **Redirects to:** Quote detail page

9. **Cancel Button** → Navigates back to `/quotes`

---

### Quote Detail Page
**Route:** `/quotes/{id}`
**Access:** All authenticated users

**Display:**
- Quote information
- Line items table
- PDF preview/download

**Quote Information:**
**Display Fields:**
- Quote Number
- Client (link)
- Quote Date
- Valid Until Date
- Status (badge)
- Created By
- Created Date

**Line Items Table:**
**Columns:** Description, Quantity, Unit Price, Total

**Totals Section:**
**Display:**
- Subtotal
- Tax (15%)
- Total Amount

**Notes Section:**
**Display:** Quote notes

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only, if status=Draft) → Navigates to `/quotes/{id}/edit`

2. **Delete Button** (Admin/Manager only, if status=Draft)
   - **Action:** Deletes quote (POST to `/quotes/{id}/delete`)
   - **Database Changes:** Deletes quote and line items, logs activity

3. **Mark as Sent Button** (Admin/Manager only, if status=Draft)
   - **Action:** Changes status to "Sent" (POST to `/quotes/{id}/mark-sent`)
   - **Database Changes:** Updates `quotes.status`, logs activity

4. **Mark as Accepted Button** (Admin/Manager only, if status=Sent)
   - **Action:** Changes status to "Accepted" (POST to `/quotes/{id}/mark-accepted`)
   - **Database Changes:** Updates `quotes.status`, logs activity

5. **Mark as Rejected Button** (Admin/Manager only, if status=Sent)
   - **Action:** Changes status to "Rejected" (POST to `/quotes/{id}/mark-rejected`)
   - **Database Changes:** Updates `quotes.status`, logs activity

6. **Download PDF Button**
   - **Action:** Downloads quote as PDF (GET `/quotes/{id}/pdf`)
   - **Backend Process:** Generates PDF from quote data

7. **Email Quote Button** (Admin/Manager only)
   - Opens email form or navigates to communications module

---

### Edit Quote Page
**Route:** `/quotes/{id}/edit`
**Access:** Admin, Manager (only if status=Draft)

**Display:**
- Quote edit form (pre-filled)
- Same fields as New Quote page

**Interactive Elements:**
- All fields from New Quote page (pre-filled)
- **Update Quote Button**
  - **Action:** Updates quote
  - **Backend Process:**
    - Validates fields
    - Updates quote and line items
    - Recalculates totals
    - Logs activity
  - **Database Changes:** Updates `quotes` and `quote_line_items` tables, creates `activity_log` entry
  - **Redirects to:** Quote detail page
- **Cancel Button** → Navigates back to quote detail page

---

### Invoices List Page
**Route:** `/invoices`
**Access:** All authenticated users

**Display:**
- Search/filter form
- Invoices table

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Invoice Number, Client Name

2. **Status Filter** (dropdown)
   - Options: All, Unpaid, Partially Paid, Paid

3. **Apply Filters Button** → Filters invoices
4. **Clear Filters Button** → Resets filters

**Invoices Table:**
**Columns:** Invoice Number, Client, Date, Due Date, Total Amount, Amount Paid, Balance, Status (badge), Actions

**Interactive Elements:**
1. **Invoice Number Links** → Navigate to `/invoices/{id}`
2. **Client Links** → Navigate to `/clients/{id}`
3. **View Button** (each row) → Navigate to `/invoices/{id}`
4. **Edit Button** (each row, Admin/Manager only, if status=Unpaid) → Navigate to `/invoices/{id}/edit`
5. **Delete Button** (each row, Admin/Manager only, if status=Unpaid and no payments) → Deletes invoice

**Top Actions:**
1. **+ New Invoice Button** (Admin/Manager only) → Navigates to `/invoices/new`

**Row Highlighting:**
- Overdue invoices (due date passed, status not Paid) highlighted in red

---

### New Invoice Page
**Route:** `/invoices/new`
**Access:** Admin, Manager

**Display:**
- Invoice creation form with line items

**Interactive Elements:**
1. **Client Dropdown** (required)
2. **Invoice Date Field** (date picker, required, default: Today)
3. **Due Date Field** (date picker, optional, default: 30 days from invoice date)
4. **Status Dropdown** (required, options: Unpaid, Partially Paid, Paid, default: Unpaid)

**Line Items Section:**
- Same as Quote line items

**Totals Section:**
- Same as Quote totals

5. **Notes Field** (textarea, optional)

6. **Create Invoice Button**
   - **Action:** Creates invoice
   - **Backend Process:**
     - Auto-generates invoice number (format: INV-{year}-{number})
     - Validates line items
     - Calculates totals
     - Creates invoice and line items
     - Logs activity
   - **Database Changes:** Inserts into `invoices` and `invoice_line_items` tables, creates `activity_log` entry
   - **Redirects to:** Invoice detail page

7. **Cancel Button** → Navigates back to `/invoices`

---

### Invoice Detail Page
**Route:** `/invoices/{id}`
**Access:** All authenticated users

**Display:**
- Invoice information
- Line items table
- Payment history
- PDF preview/download

**Invoice Information:**
**Display Fields:**
- Invoice Number
- Client (link)
- Invoice Date
- Due Date
- Status (badge)
- Total Amount
- Amount Paid
- Balance Due
- Created By
- Created Date

**Line Items Table:**
**Columns:** Description, Quantity, Unit Price, Total

**Totals Section:**
**Display:**
- Subtotal
- Tax (15%)
- Total Amount
- Amount Paid
- Balance Due

**Payment History Section:**
**Display:** Table of payments received

**Columns:** Payment Date, Amount, Payment Method, Reference, Notes

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only, if status=Unpaid) → Navigates to `/invoices/{id}/edit`

2. **Delete Button** (Admin/Manager only, if no payments)
   - **Action:** Deletes invoice (POST to `/invoices/{id}/delete`)
   - **Database Changes:** Deletes invoice and line items, logs activity

3. **Record Payment Button** (Admin/Manager only, if balance > 0)
   - Opens payment form
   - **Form Fields:**
     - Payment Date (date picker, required, default: Today)
     - Amount (number input, required, max: balance due)
     - Payment Method (dropdown: Cash, EFT, Credit Card, Cheque, Other)
     - Reference (text input, optional - transaction ID, cheque number)
     - Notes (textarea, optional)
   - **Record Action:** (POST to `/invoices/{id}/record-payment`)
     - **Backend Process:**
       - Validates payment amount
       - Creates payment record
       - Updates invoice amount_paid
       - Updates invoice status (Partially Paid or Paid)
       - Logs activity
     - **Database Changes:** Inserts into `invoice_payments`, updates `invoices.amount_paid` and `invoices.status`, creates `activity_log` entry

4. **Download PDF Button**
   - **Action:** Downloads invoice as PDF (GET `/invoices/{id}/pdf`)

5. **Email Invoice Button** (Admin/Manager only)
   - Opens email form or navigates to communications module

---

## Communications Module

### Communications Hub
**Route:** `/communications` or `/communications?channel={channel}`
**Access:** All authenticated users

**Display:**
- Channel tabs/filter
- Communications table
- Statistics

**Channel Filter:**
**Interactive Elements:**
1. **All Tab** → Shows all communications
2. **Gmail Tab** → Filters to `channel=gmail`
3. **Outlook Tab** → Filters to `channel=outlook`
4. **WhatsApp Tab** → Filters to `channel=whatsapp`
5. **Teams Tab** → Filters to `channel=teams`

**Statistics Section:**
**Display:**
- Total Communications
- By Channel breakdown
- Recent activity count

**Communications Table:**
**Columns:** Date/Time, Channel (badge), Type (badge), Subject/Message Preview, Client, Project, Status, Actions

**Interactive Elements:**
1. **Subject Links** → Navigate to `/communications/{id}`
2. **Client Links** → Navigate to `/clients/{id}`
3. **Project Links** → Navigate to `/projects/{id}`
4. **View Button** (each row) → Navigate to `/communications/{id}`
5. **Delete Button** (each row, Admin/Manager only) → Deletes communication

**Top Actions:**
1. **+ New Communication Button** (Admin/Manager/Operator) → Navigates to `/communications/new`

---

### New Communication Page
**Route:** `/communications/new`
**Access:** Admin, Manager, Operator

**Display:**
- Communication creation form

**Interactive Elements:**
1. **Channel Dropdown** (required)
   - Options: Gmail, Outlook, WhatsApp, Teams

2. **Type Dropdown** (required)
   - Options: Email, WhatsApp, Notification

3. **Subject Field** (text input, required for Email type)

4. **Message Body Field** (textarea, required)

5. **Client Dropdown** (optional)
   - Auto-links communication to client

6. **Project Dropdown** (optional)
   - Auto-links communication to project
   - Filtered by selected client if client is chosen

7. **Recipient(s) Field** (text input, required)
   - Email addresses or phone numbers

8. **Attachments Field** (file upload, optional)
   - Multiple files supported

9. **Send Communication Button**
   - **Action:** Creates communication record (POST to `/communications/new`)
   - **Backend Process:**
     - Validates fields
     - Saves attachments
     - Creates communication record
     - Logs activity
     - **Note:** Does NOT actually send email/message (logging only in current implementation)
   - **Database Changes:** Inserts into `communications` table, creates `activity_log` entry
   - **Redirects to:** Communications hub

10. **Cancel Button** → Navigates back to `/communications`

---

### Communication Detail Page
**Route:** `/communications/{id}`
**Access:** All authenticated users

**Display:**
- Communication information
- Message content
- Attachments
- Linked records

**Communication Information:**
**Display Fields:**
- Channel (badge)
- Type (badge)
- Subject
- Date/Time
- Sender
- Recipient(s)
- Client (link, if linked)
- Project (link, if linked)
- Status

**Message Content:**
**Display:** Full message body

**Attachments Section:**
**Display:** List of attached files

**Interactive Elements:**
1. **Download Attachment Button** (each file) → Downloads file
2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes communication (POST to `/communications/{id}/delete`)
   - **Database Changes:** Deletes communication record, logs activity

---

### Message Templates Page
**Route:** `/comms/templates`
**Access:** Admin, Manager, Operator

**Display:**
- Templates table
- Filter by type

**Filter Section:**
**Interactive Elements:**
1. **Type Filter** (dropdown)
   - Options: All, project_complete, order_confirmed, quote_sent, invoice_sent, payment_reminder, delivery_notification, custom

2. **Active Only Checkbox** → Filters to show only active templates

**Templates Table:**
**Columns:** Name, Type (badge), Subject, Active (toggle), Actions

**Interactive Elements:**
1. **Name Links** → Navigate to `/comms/templates/{id}`
2. **Active Toggle** (each row, Admin/Manager only)
   - **Action:** Toggles template active status (POST to `/comms/templates/{id}/toggle-active`)
   - **Database Changes:** Updates `message_templates.is_active`

3. **View Button** (each row) → Navigate to `/comms/templates/{id}`
4. **Edit Button** (each row, Admin/Manager only) → Navigate to `/comms/templates/{id}/edit`
5. **Delete Button** (each row, Admin/Manager only) → Deletes template

**Top Actions:**
1. **+ New Template Button** (Admin/Manager only) → Navigates to `/comms/templates/new`

---

### New Template Page
**Route:** `/comms/templates/new`
**Access:** Admin, Manager

**Display:**
- Template creation form

**Interactive Elements:**
1. **Name Field** (text input, required)

2. **Type Dropdown** (required)
   - Options: project_complete, order_confirmed, quote_sent, invoice_sent, payment_reminder, delivery_notification, custom

3. **Subject Field** (text input, required)
   - Supports placeholders: {client_name}, {project_code}, {project_name}, etc.

4. **Body Field** (textarea, required)
   - Supports placeholders

5. **Active Checkbox** (default: checked)

6. **Placeholder Help Section**
   - **Display:** List of available placeholders and their descriptions
   - Examples: {client_name}, {project_code}, {project_name}, {due_date}, {quoted_price}, etc.

7. **Create Template Button**
   - **Action:** Creates template
   - **Backend Process:**
     - Validates fields
     - Creates template record
     - Logs activity
   - **Database Changes:** Inserts into `message_templates` table, creates `activity_log` entry
   - **Redirects to:** Template detail page

8. **Cancel Button** → Navigates back to `/comms/templates`

---

### Template Detail Page
**Route:** `/comms/templates/{id}`
**Access:** Admin, Manager, Operator

**Display:**
- Template information
- Preview with sample data

**Template Information:**
**Display Fields:**
- Name
- Type (badge)
- Subject
- Body
- Active status (badge)
- Created Date
- Last Modified Date

**Preview Section:**
**Display:** Rendered template with sample data

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Navigates to `/comms/templates/{id}/edit`

2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes template (POST to `/comms/templates/{id}/delete`)
   - **Database Changes:** Deletes template, logs activity

3. **Toggle Active Button** (Admin/Manager only)
   - **Action:** Toggles active status (POST to `/comms/templates/{id}/toggle-active`)
   - **Database Changes:** Updates `message_templates.is_active`

4. **Preview with Data Button**
   - Opens preview modal with sample data

---

### Edit Template Page
**Route:** `/comms/templates/{id}/edit`
**Access:** Admin, Manager

**Display:**
- Template edit form (pre-filled)
- Same fields as New Template page

**Interactive Elements:**
- All fields from New Template page (pre-filled)
- **Update Template Button**
  - **Action:** Updates template
  - **Backend Process:**
    - Validates fields
    - Updates template record
    - Logs activity
  - **Database Changes:** Updates `message_templates` table, creates `activity_log` entry
  - **Redirects to:** Template detail page
- **Cancel Button** → Navigates back to template detail page

---

## Presets Module

### Presets List Page
**Route:** `/presets`
**Access:** All authenticated users

**Display:**
- Search/filter form
- Presets table

**Search & Filter Section:**
**Interactive Elements:**
1. **Search Field** (text input)
   - Searches: Preset Name, Material Type

2. **Material Filter** (dropdown)
   - Options: All + unique materials from database

3. **Active Only Checkbox** → Filters to show only active presets

4. **Apply Filters Button** → Filters presets
5. **Clear Filters Button** → Resets filters

**Presets Table:**
**Columns:** Name, Material Type, Thickness (mm), Power (%), Speed (mm/s), Frequency (Hz), Active (toggle), Actions

**Interactive Elements:**
1. **Name Links** → Navigate to `/presets/{id}`
2. **Active Toggle** (each row, Admin/Manager only)
   - **Action:** Toggles preset active status (POST to `/presets/{id}/toggle-active`)
   - **Database Changes:** Updates `machine_settings_presets.is_active`

3. **View Button** (each row) → Navigate to `/presets/{id}`
4. **Edit Button** (each row, Admin/Manager only) → Navigate to `/presets/{id}/edit`
5. **Delete Button** (each row, Admin/Manager only) → Deletes preset

**Top Actions:**
1. **+ New Preset Button** (Admin/Manager only) → Navigates to `/presets/new`

---

### New Preset Page
**Route:** `/presets/new`
**Access:** Admin, Manager

**Display:**
- Preset creation form

**Interactive Elements:**
1. **Name Field** (text input, required)

2. **Material Type Dropdown** (required)
   - Options from config: Mild Steel, Stainless Steel, Aluminum, Copper, Brass, etc.

3. **Thickness Field** (number input, required)
   - Unit: mm

4. **Power Field** (number input, required)
   - Unit: %
   - Range: 0-100

5. **Speed Field** (number input, required)
   - Unit: mm/s

6. **Frequency Field** (number input, required)
   - Unit: Hz

7. **Gas Type Field** (text input, optional)
   - Examples: Oxygen, Nitrogen, Air

8. **Gas Pressure Field** (number input, optional)
   - Unit: bar

9. **Nozzle Size Field** (number input, optional)
   - Unit: mm

10. **Focus Height Field** (number input, optional)
    - Unit: mm

11. **Notes Field** (textarea, optional)

12. **Active Checkbox** (default: checked)

13. **Create Preset Button**
    - **Action:** Creates preset
    - **Backend Process:**
      - Validates fields
      - Creates preset record
      - Logs activity
    - **Database Changes:** Inserts into `machine_settings_presets` table, creates `activity_log` entry
    - **Redirects to:** Preset detail page

14. **Cancel Button** → Navigates back to `/presets`

---

### Preset Detail Page
**Route:** `/presets/{id}`
**Access:** All authenticated users

**Display:**
- Preset information card
- Usage history

**Preset Information:**
**Display Fields:**
- Name
- Material Type
- Thickness (mm)
- Power (%)
- Speed (mm/s)
- Frequency (Hz)
- Gas Type
- Gas Pressure (bar)
- Nozzle Size (mm)
- Focus Height (mm)
- Notes
- Active status (badge)
- Created Date
- Last Modified Date

**Interactive Elements:**
1. **Edit Button** (Admin/Manager only) → Navigates to `/presets/{id}/edit`

2. **Delete Button** (Admin/Manager only)
   - **Action:** Deletes preset (POST to `/presets/{id}/delete`)
   - **Database Changes:** Deletes preset, logs activity
   - **Validation:** May check if preset is used in laser runs

3. **Toggle Active Button** (Admin/Manager only)
   - **Action:** Toggles active status (POST to `/presets/{id}/toggle-active`)
   - **Database Changes:** Updates `machine_settings_presets.is_active`

**Usage History Section:**
**Display:** Table of laser runs that used this preset

**Columns:** Date, Project, Operator, Cut Time

**Interactive Elements:**
1. **Project Links** → Navigate to `/projects/{id}`

---

### Edit Preset Page
**Route:** `/presets/{id}/edit`
**Access:** Admin, Manager

**Display:**
- Preset edit form (pre-filled)
- Same fields as New Preset page

**Interactive Elements:**
- All fields from New Preset page (pre-filled)
- **Update Preset Button**
  - **Action:** Updates preset
  - **Backend Process:**
    - Validates fields
    - Updates preset record
    - Logs activity
  - **Database Changes:** Updates `machine_settings_presets` table, creates `activity_log` entry
  - **Redirects to:** Preset detail page
- **Cancel Button** → Navigates back to preset detail page

---

### Presets API Endpoint
**Route:** `/presets/api/presets`
**Access:** All authenticated users
**Method:** GET

**Purpose:** Returns JSON list of all active presets for use in forms/dropdowns

**Response Format:**
```json
[
  {
    "id": 1,
    "name": "Mild Steel 3mm",
    "material_type": "Mild Steel",
    "thickness": 3.0,
    "power": 80,
    "speed": 1200,
    "frequency": 5000
  },
  ...
]
```

---

## Admin Module

### Admin Dashboard
**Route:** `/admin`
**Access:** Admin, Superuser only

**Display:**
- Admin menu/links
- System statistics

**Admin Menu:**
**Interactive Elements:**
1. **Manage Users Link** → Navigate to `/admin/users`
2. **View Activity Log Link** → Navigate to `/admin/activity`
3. **System Settings Link** → Navigate to `/admin/settings` (if implemented)

**System Statistics:**
**Display:**
- Total Users
- Active Users
- Total Activity Logs
- Recent Logins

---

### Users Management Page
**Route:** `/admin/users`
**Access:** Admin, Superuser only

**Display:**
- Users table
- Filter options

**Filter Section:**
**Interactive Elements:**
1. **Role Filter** (dropdown)
   - Options: All, Admin, Manager, Operator, Viewer

2. **Status Filter** (dropdown)
   - Options: All, Active, Locked

3. **Apply Filters Button** → Filters users

**Users Table:**
**Columns:** Username, Full Name, Email, Roles (badges), Status (badge), Last Login, Actions

**Interactive Elements:**
1. **Username Links** → Navigate to `/admin/users/{id}`
2. **View Button** (each row) → Navigate to `/admin/users/{id}`
3. **Edit Button** (each row) → Navigate to `/admin/users/{id}/edit`
4. **Lock/Unlock Button** (each row)
   - **Action:** Toggles account lock status (POST to `/admin/users/{id}/lock` or `/unlock`)
   - **Database Changes:** Updates `users.is_locked`, `users.locked_until`

5. **Delete Button** (each row, Superuser only)
   - **Action:** Deletes user (POST to `/admin/users/{id}/delete`)
   - **Database Changes:** Deletes user, logs activity
   - **Validation:** Cannot delete own account

**Top Actions:**
1. **+ New User Button** → Navigates to `/admin/users/new`

---

### New User Page
**Route:** `/admin/users/new`
**Access:** Admin, Superuser only

**Display:**
- User creation form

**Interactive Elements:**
1. **Username Field** (text input, required)
   - Must be unique

2. **Email Field** (email input, required)
   - Must be unique

3. **Full Name Field** (text input, required)

4. **Password Field** (password input, required)
   - Must meet password requirements

5. **Confirm Password Field** (password input, required)
   - Must match password

6. **Roles Checkboxes** (at least one required)
   - Options: Admin, Manager, Operator, Viewer
   - Multiple roles can be selected

7. **Active Checkbox** (default: checked)

8. **Create User Button**
   - **Action:** Creates user account
   - **Backend Process:**
     - Validates fields
     - Checks for duplicate username/email
     - Hashes password
     - Creates user record
     - Assigns roles
     - Logs activity
   - **Database Changes:** Inserts into `users` and `user_roles` tables, creates `activity_log` entry
   - **Redirects to:** User detail page

9. **Cancel Button** → Navigates back to `/admin/users`

---

### User Detail Page
**Route:** `/admin/users/{id}`
**Access:** Admin, Superuser only

**Display:**
- User information
- Assigned roles
- Login history
- Activity log

**User Information:**
**Display Fields:**
- Username
- Email
- Full Name
- Roles (badges)
- Account Status (Active/Locked badge)
- Last Login
- Failed Login Attempts
- Created Date

**Interactive Elements:**
1. **Edit Button** → Navigates to `/admin/users/{id}/edit`

2. **Delete Button** (Superuser only)
   - **Action:** Deletes user (POST to `/admin/users/{id}/delete`)
   - **Database Changes:** Deletes user, logs activity
   - **Validation:** Cannot delete own account

3. **Lock Account Button** (if active)
   - **Action:** Locks user account (POST to `/admin/users/{id}/lock`)
   - **Database Changes:** Updates `users.is_locked`, `users.locked_until`

4. **Unlock Account Button** (if locked)
   - **Action:** Unlocks user account (POST to `/admin/users/{id}/unlock`)
   - **Database Changes:** Updates `users.is_locked`, `users.locked_until`, resets `failed_login_attempts`

5. **Reset Password Button**
   - Opens password reset form
   - **Form Fields:**
     - New Password (password input, required)
     - Confirm Password (password input, required)
   - **Reset Action:** (POST to `/admin/users/{id}/reset-password`)
     - **Backend Process:**
       - Validates password
       - Hashes new password
       - Updates user record
       - Logs activity
     - **Database Changes:** Updates `users.password_hash`, creates `activity_log` entry

**Login History Section:**
**Display:** Table of last 20 logins for this user

**Columns:** Login Time, IP Address, User Agent, Logout Time

**Activity Log Section:**
**Display:** Recent activities performed by this user

---

### Edit User Page
**Route:** `/admin/users/{id}/edit`
**Access:** Admin, Superuser only

**Display:**
- User edit form (pre-filled)

**Interactive Elements:**
1. **Username Field** (text input, required, read-only)
   - Cannot change username

2. **Email Field** (email input, required)

3. **Full Name Field** (text input, required)

4. **Roles Checkboxes** (at least one required)
   - Options: Admin, Manager, Operator, Viewer
   - Pre-checked based on current roles

5. **Active Checkbox**

6. **Update User Button**
   - **Action:** Updates user information
   - **Backend Process:**
     - Validates fields
     - Updates user record
     - Updates role assignments
     - Logs activity
   - **Database Changes:** Updates `users` table, updates `user_roles` table, creates `activity_log` entry
   - **Redirects to:** User detail page

7. **Cancel Button** → Navigates back to user detail page

---

### Activity Log Page
**Route:** `/admin/activity`
**Access:** Admin, Superuser only

**Display:**
- Filter form
- Activity log table

**Filter Section:**
**Interactive Elements:**
1. **User Filter** (dropdown)
   - Options: All + all users

2. **Action Type Filter** (dropdown)
   - Options: All, Created, Updated, Deleted, Login, Logout, etc.

3. **Date From Field** (date picker)
4. **Date To Field** (date picker)
5. **Apply Filters Button** → Filters activity log
6. **Clear Filters Button** → Resets filters

**Activity Log Table:**
**Columns:** Timestamp, User, Action, Entity Type, Entity ID, Details, IP Address

**Interactive Elements:**
1. **User Links** → Navigate to `/admin/users/{user_id}`
2. **Entity Links** (if applicable) → Navigate to entity detail page (e.g., `/projects/{id}`)

**Pagination:**
- Shows 100 entries per page
- Previous/Next buttons

---

## Automated Workflows

This section describes the automated processes that are triggered by user actions.

### 1. POP Received → Auto-Queue Addition

**Trigger:** User clicks "Mark POP Received" button on project detail page

**Automated Process:**
1. Sets `project.pop_received = True`
2. Sets `project.pop_received_date = today`
3. Calculates `project.pop_deadline = today + 3 business days`
4. **Automatically creates queue item** with:
   - Priority: Normal
   - Scheduled Date: Today or next business day
   - Estimated Cut Time: From `project.estimated_cut_time`
   - Status: Queued
   - Position: Next available position in queue
5. Logs activity for both POP receipt and queue addition

**Database Changes:**
- Updates `projects` table (pop_received, pop_received_date, pop_deadline)
- Inserts into `queue_items` table
- Creates 2 `activity_log` entries

**User Feedback:**
- Success message: "POP marked as received. Project automatically added to queue."
- Redirects to project detail page showing queue status

---

### 2. Auto-Generated Codes

**Client Code Generation:**
- **Trigger:** Creating new client
- **Format:** `CL-XXXX` (e.g., CL-0001, CL-0002)
- **Process:** Finds highest existing number, increments by 1
- **Function:** `generate_client_code()`

**Project Code Generation:**
- **Trigger:** Creating new project
- **Format:** `{CLIENT_CODE}-PXXXX` (e.g., CL-0001-P0001)
- **Process:** Finds highest project number for that client, increments by 1
- **Function:** `generate_project_code(client_code)`

**SKU Code Generation:**
- **Trigger:** Creating new product
- **Format:** `SKU-XXXX` (e.g., SKU-0001)
- **Process:** Database event listener auto-generates on insert
- **Function:** Event listener in models

**Quote Number Generation:**
- **Trigger:** Creating new quote
- **Format:** `QT-{YEAR}-{NUMBER}` (e.g., QT-2025-0001)
- **Process:** Finds highest quote number for current year, increments by 1
- **Function:** Auto-generation in route handler

**Invoice Number Generation:**
- **Trigger:** Creating new invoice
- **Format:** `INV-{YEAR}-{NUMBER}` (e.g., INV-2025-0001)
- **Process:** Finds highest invoice number for current year, increments by 1
- **Function:** Auto-generation in route handler

---

### 3. POP Deadline Validation

**Trigger:** Adding project to queue (manual or automatic)

**Validation Process:**
1. Checks if `project.pop_received = True`
2. If yes, checks if `project.pop_deadline` has passed
3. If deadline passed:
   - Shows warning message: "Warning: POP deadline has passed!"
   - Still allows queue addition but highlights the issue
4. If deadline approaching (within 1 day):
   - Shows info message: "Note: POP deadline is approaching."

**Purpose:** Ensures 3-day turnaround commitment is tracked

---

### 4. Low Stock Alerts

**Trigger:** Inventory adjustment that brings quantity at or below reorder level

**Automated Process:**
1. After stock adjustment, checks if `quantity_on_hand <= reorder_level`
2. If true, item appears in low stock list
3. Dashboard shows low stock count
4. Inventory page highlights low stock items in yellow

**No automatic notifications yet** - this is a future enhancement planned for Communications module

---

### 5. Account Lockout

**Trigger:** Failed login attempt

**Automated Process:**
1. Increments `users.failed_login_attempts`
2. If `failed_login_attempts >= 5`:
   - Sets `users.is_locked = True`
   - Sets `users.locked_until = now + 30 minutes`
   - Prevents further login attempts
3. After 30 minutes, account automatically unlocks
4. Successful login resets `failed_login_attempts` to 0

**Security Feature:** Prevents brute-force password attacks

---

### 6. Activity Logging

**Trigger:** Almost all user actions

**Automated Process:**
1. After successful create/update/delete operation
2. Calls `log_activity()` service function
3. Records:
   - User who performed action
   - Action type (created, updated, deleted, etc.)
   - Entity type (client, project, product, etc.)
   - Entity ID
   - Details (what changed)
   - IP address
   - Timestamp

**Database Changes:**
- Inserts into `activity_log` table

**Purpose:** Complete audit trail for compliance and troubleshooting

---

## Future Enhancements (Planned)

Based on user memories and codebase comments, the following enhancements are planned:

### Communications Module Enhancements

1. **Automated Message Templates Triggered by Milestones:**
   - When project status changes to "Complete" → Auto-send "Collection Ready" message
   - When POP received → Auto-send "Order Confirmed" message
   - When quote created → Auto-send "Quote Sent" message
   - When invoice created → Auto-send "Invoice Sent" message

2. **Inbound Email Parsing:**
   - Parse incoming emails to auto-create/update projects
   - Extract client information, project details, attachments
   - Advanced/future feature

3. **User-Specific Communication Routing:**
   - Control which users receive which notification types
   - Per-user notification preferences
   - Email/SMS/WhatsApp routing rules

### Queue Automation Enhancements

- Already implemented: Auto-queue addition when POP received ✓
- Future: More sophisticated scheduling algorithms
- Future: Capacity planning and resource allocation

### UI Enhancements

- Collapsible sidebar navigation ✓ (already implemented)
- More responsive mobile layouts
- Dark mode theme
- Customizable dashboard widgets

---

## Summary

This documentation covers **14 main modules** with **100+ pages/routes** and **500+ interactive elements**.

**Key Statistics:**
- **14 Blueprints:** auth, admin, main, clients, projects, products, files, queue, inventory, reports, quotes, invoices, comms, presets, templates
- **100+ Routes:** Full CRUD operations across all modules
- **6 Automated Workflows:** POP→Queue, Code Generation, Deadline Validation, Low Stock Alerts, Account Lockout, Activity Logging
- **4 User Roles:** Admin, Manager, Operator, Viewer
- **8 Communication Channels:** Gmail, Outlook, WhatsApp, Teams (4 channels × 2 directions)
- **50+ Database Tables:** Comprehensive data model

**Navigation Type:** Collapsible left sidebar with expandable sections

**Security Features:**
- Role-based access control (RBAC)
- Account lockout after 5 failed attempts
- Activity logging for all operations
- Secure file upload with UUID naming

**File Management:**
- Multi-file upload support
- DXF and LBRN2 file types
- Secure storage with UUID filenames
- File association with projects and products

**Reporting:**
- Production summary
- Efficiency metrics
- Inventory reports
- Client profitability
- CSV export functionality

---

**End of Documentation**


