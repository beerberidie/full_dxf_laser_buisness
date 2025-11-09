# 📋 LASER OS CHANGE REQUEST TEMPLATE

**Version:** 1.0  
**Date:** 2025-10-27  
**Application:** Laser Cutting Operations System (Laser OS)

---

## 📖 **HOW TO USE THIS TEMPLATE**

This template is optimized for AI assistant processing. When submitting requests:

1. **Copy the relevant section(s)** below (Issue Report, Change Request, Edit Request, or Feature Addition)
2. **Fill in all applicable fields** - be as specific as possible
3. **Delete unused sections** to keep the request focused
4. **Include file paths** relative to workspace root: `c:\Users\Garas\Documents\augment-projects\full_dxf_laser_buisness`
5. **Reference module names** from the 12 core modules (see Architecture Reference below)
6. **Set priority levels** to help with task planning

---

## 🏗️ **ARCHITECTURE REFERENCE**

### **12 Core Modules:**
1. **Dashboard** (`app/routes/main.py`) - Central statistics and overview
2. **Clients** (`app/routes/clients.py`) - Customer management
3. **Projects** (`app/routes/projects.py`) - Order tracking and management
4. **Products** (`app/routes/products.py`) - SKU catalog
5. **Queue** (`app/routes/queue.py`) - Production scheduling and laser runs
6. **Presets** (`app/routes/presets.py`) - Machine settings library
7. **Operators** (`app/routes/operators.py`) - Operator profiles
8. **Inventory** (`app/routes/inventory.py`) - Material stock tracking
9. **Reports** (`app/routes/reports.py`) - Analytics and BI
10. **Sage Integration** (`app/routes/sage.py`) - Accounting integration
11. **Communications** (`app/routes/comms.py`) - Email and messaging
12. **Admin** (`app/routes/admin.py`) - User and system administration

### **Key Database Models:**
- **Auth:** User, Role, UserRole, LoginHistory
- **Business:** Client, Project, Product, QueueItem, LaserRun, Operator, MachineSettingsPreset, InventoryItem, Communication, Quote, Invoice
- **Sage:** SageConnection, SageBusiness, SageSyncCursor, SageAuditLog

### **Critical Automation Systems:**
1. **Auto-Queue on POP Received** (`app/services/status_automation.py`)
2. **Queue-Project Status Sync** (`app/routes/queue.py` → `update_status()`)
3. **Operator Auto-bind** (`app/routes/auth.py` → `login()`)

---

## 🐛 **SECTION 1: ISSUE REPORT**

Use this section to report bugs, errors, or problems with existing functionality.

```markdown
### ISSUE REPORT

**Issue ID:** [Auto-generated or leave blank]  
**Date Reported:** YYYY-MM-DD  
**Reporter:** [Your name]

#### Issue Type
- [ ] Bug (functionality not working as intended)
- [ ] Error (application crash or exception)
- [ ] Performance Issue (slow loading, timeout)
- [ ] UI/UX Issue (display problem, usability)
- [ ] Data Integrity Issue (incorrect data, sync problem)
- [ ] Security Issue (authentication, authorization)

#### Priority Level
- [ ] CRITICAL (System down, data loss, security breach)
- [ ] HIGH (Major feature broken, blocking workflow)
- [ ] MEDIUM (Feature partially broken, workaround exists)
- [ ] LOW (Minor issue, cosmetic problem)

#### Affected Module(s)
- [ ] Dashboard
- [ ] Clients
- [ ] Projects
- [ ] Products
- [ ] Queue
- [ ] Presets
- [ ] Operators
- [ ] Inventory
- [ ] Reports
- [ ] Sage Integration
- [ ] Communications
- [ ] Admin
- [ ] Other: _______________

#### Issue Summary
[One-sentence description of the problem]

#### Detailed Description
[Detailed explanation of what's wrong]

#### Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]
...

#### Expected Behavior
[What should happen]

#### Actual Behavior
[What actually happens]

#### Error Messages / Stack Trace
```
[Paste any error messages or stack traces here]
```

#### Affected Files
- File: `app/routes/[module].py`
  - Lines: [line numbers if known]
  - Function: `[function_name]`

- File: `app/models/[model_file].py`
  - Model: `[ModelName]`
  - Fields: `[field_names]`

#### Screenshots / Logs
[Attach or describe any relevant screenshots or log entries]

#### Environment
- Browser: [Chrome/Firefox/Safari/Edge]
- OS: [Windows/Mac/Linux]
- Database: SQLite
- Python Version: 3.11+

#### Potential Root Cause
[If you have any ideas about what might be causing this]

#### Suggested Fix
[If you have ideas on how to fix it]

#### Related Issues
[Link to any related issues or change requests]
```

---

## 🔄 **SECTION 2: CHANGE REQUEST**

Use this section to request modifications to existing functionality.

```markdown
### CHANGE REQUEST

**Request ID:** [Auto-generated or leave blank]  
**Date Requested:** YYYY-MM-DD  
**Requester:** [Your name]

#### Priority Level
- [ ] CRITICAL (Urgent business need, blocking operations)
- [ ] HIGH (Important improvement, significant impact)
- [ ] MEDIUM (Nice to have, moderate impact)
- [ ] LOW (Minor improvement, low impact)

#### Affected Module(s)
- [ ] Dashboard
- [ ] Clients
- [ ] Projects
- [ ] Products
- [ ] Queue
- [ ] Presets
- [ ] Operators
- [ ] Inventory
- [ ] Reports
- [ ] Sage Integration
- [ ] Communications
- [ ] Admin
- [ ] Multiple modules: _______________

#### Change Summary
[One-sentence description of the requested change]

#### Current Behavior
[Describe how the feature currently works]

**Current Workflow:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

#### Desired Behavior
[Describe how you want the feature to work]

**Desired Workflow:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

#### Reason for Change
[Explain why this change is needed - business justification, user feedback, efficiency improvement, etc.]

#### Business Impact
- **Users Affected:** [All users / Specific roles / Specific workflows]
- **Frequency of Use:** [Daily / Weekly / Monthly / Occasional]
- **Time Savings:** [Estimated time saved per use]
- **Error Reduction:** [How this reduces errors or improves accuracy]

#### Files Potentially Affected
- **Routes:** `app/routes/[module].py`
  - Functions: `[function_names]`
  
- **Models:** `app/models/[model_file].py`
  - Models: `[ModelName]`
  - Fields to modify: `[field_names]`
  
- **Templates:** `app/templates/[module]/[template].html`
  
- **Services:** `app/services/[service].py`

#### Database Changes Required
- [ ] No database changes
- [ ] Modify existing field(s): `[field_names]`
- [ ] Add new field(s): `[field_names with types]`
- [ ] Add new relationship(s): `[relationship description]`
- [ ] Add new model: `[ModelName]`

#### UI/UX Changes Required
- [ ] No UI changes
- [ ] Modify existing form/page: `[page name]`
- [ ] Add new button/link: `[description]`
- [ ] Change layout/styling: `[description]`
- [ ] Add new page/view: `[page name]`

#### Integration Impact
[How does this change affect other modules or automation systems?]

- **Modules Affected:**
  - Module 1: [Impact description]
  - Module 2: [Impact description]

- **Automation Systems Affected:**
  - [ ] Auto-Queue on POP Received
  - [ ] Queue-Project Status Sync
  - [ ] Operator Auto-bind
  - [ ] Other: _______________

#### Backward Compatibility
- [ ] Fully backward compatible (no breaking changes)
- [ ] Requires data migration
- [ ] Requires user retraining
- [ ] Breaking change (explain): _______________

#### Testing Requirements
[What should be tested after this change?]
1. [Test case 1]
2. [Test case 2]
3. [Test case 3]

#### Related Requests
[Link to any related change requests or issues]
```

---

## ✏️ **SECTION 3: EDIT REQUEST**

Use this section for specific, targeted code edits.

```markdown
### EDIT REQUEST

**Request ID:** [Auto-generated or leave blank]  
**Date Requested:** YYYY-MM-DD  
**Requester:** [Your name]

#### Priority Level
- [ ] CRITICAL
- [ ] HIGH
- [ ] MEDIUM
- [ ] LOW

#### Edit Type
- [ ] Bug fix
- [ ] Code refactoring
- [ ] Performance optimization
- [ ] Security fix
- [ ] Code cleanup
- [ ] Documentation update

#### File(s) to Edit
**File 1:** `app/routes/[module].py`
- **Lines:** [start_line - end_line] (if known)
- **Function/Class:** `[name]`
- **Current Code:**
```python
# Paste current code here
```
- **Requested Changes:**
```python
# Paste desired code here OR describe the change
```
- **Reason:** [Why this edit is needed]

**File 2:** `app/models/[model_file].py`
- **Lines:** [start_line - end_line]
- **Model/Field:** `[ModelName.field_name]`
- **Current Code:**
```python
# Paste current code here
```
- **Requested Changes:**
```python
# Paste desired code here OR describe the change
```
- **Reason:** [Why this edit is needed]

#### Context
[Explain the broader context of why this edit is needed]

#### Expected Outcome
[What should happen after this edit is applied?]

#### Downstream Changes Required
[Are there other files that need to be updated as a result of this edit?]
- [ ] Update imports in: `[file_path]`
- [ ] Update tests in: `[file_path]`
- [ ] Update templates in: `[file_path]`
- [ ] Update documentation in: `[file_path]`

#### Testing
[How should this edit be tested?]
1. [Test step 1]
2. [Test step 2]
```

---

## ✨ **SECTION 4: FEATURE ADDITION**

Use this section to request new features or functionality.

```markdown
### FEATURE ADDITION REQUEST

**Feature ID:** [Auto-generated or leave blank]
**Date Requested:** YYYY-MM-DD
**Requester:** [Your name]

#### Priority Level
- [ ] CRITICAL (Essential for business operations)
- [ ] HIGH (Important for efficiency/competitiveness)
- [ ] MEDIUM (Valuable enhancement)
- [ ] LOW (Nice to have)

#### Feature Category
- [ ] New Module (entirely new functionality)
- [ ] Module Enhancement (add to existing module)
- [ ] Automation/Integration (connect existing features)
- [ ] Reporting/Analytics (new reports or metrics)
- [ ] UI/UX Improvement (better user experience)
- [ ] API/Integration (external system connection)

#### Affected/Related Module(s)
- [ ] Dashboard
- [ ] Clients
- [ ] Projects
- [ ] Products
- [ ] Queue
- [ ] Presets
- [ ] Operators
- [ ] Inventory
- [ ] Reports
- [ ] Sage Integration
- [ ] Communications
- [ ] Admin
- [ ] New Module: _______________

#### Feature Name
[Short, descriptive name for the feature]

#### Feature Description
[Detailed description of what this feature does and why it's needed]

#### Business Justification
**Problem Statement:**
[What problem does this solve?]

**Business Value:**
[How does this benefit the business?]

**User Impact:**
- **Users Affected:** [Roles/departments]
- **Frequency of Use:** [Daily/Weekly/Monthly]
- **Time Savings:** [Estimated]
- **Error Reduction:** [Estimated]

#### User Workflow / Use Case

**Scenario:**
[Describe a real-world scenario where this feature would be used]

**User Story:**
As a [role], I want to [action] so that [benefit].

**Workflow Steps:**
1. User navigates to [location]
2. User clicks [button/link]
3. User enters [data]
4. System performs [action]
5. User sees [result]

#### Database Changes Needed

**New Models Required:**
```python
class NewModel(db.Model):
    __tablename__ = 'new_table'

    id = db.Column(db.Integer, primary_key=True)
    # Add fields here
    field_name = db.Column(db.String(100), nullable=False)

    # Relationships
    related_model_id = db.Column(db.Integer, db.ForeignKey('related_table.id'))
```

**Modifications to Existing Models:**
- **Model:** `[ModelName]`
  - **Add Fields:**
    - `field_name` (Type: String(100), Nullable: False, Default: None)
    - `another_field` (Type: Integer, Nullable: True)
  - **Add Relationships:**
    - `relationship_name` → `RelatedModel` (One-to-Many / Many-to-One / Many-to-Many)

**Foreign Keys / Relationships:**
- `new_table.project_id` → `projects.id` (Many-to-One)
- `new_table.client_id` → `clients.id` (Many-to-One)

#### UI/UX Requirements

**New Pages/Views:**
1. **Page Name:** [e.g., "Feature Management Dashboard"]
   - **Route:** `/feature/dashboard`
   - **Template:** `app/templates/feature/dashboard.html`
   - **Components:**
     - Statistics cards
     - Data table with filters
     - Action buttons

2. **Page Name:** [e.g., "Create New Feature"]
   - **Route:** `/feature/new`
   - **Template:** `app/templates/feature/form.html`
   - **Form Fields:**
     - Field 1: [Type, Required/Optional]
     - Field 2: [Type, Required/Optional]

**Modifications to Existing Pages:**
- **Page:** `[existing_page_name]`
  - **Add:** [New button/section/field]
  - **Modify:** [Existing element]

**Navigation Changes:**
- [ ] Add new sidebar menu item: "[Feature Name]"
- [ ] Add submenu under existing module: "[Module Name]" → "[Feature Name]"
- [ ] Add button to existing page: "[Page Name]"

#### Backend Implementation

**New Routes Required:**
```python
# app/routes/feature.py

@bp.route('/feature')
@login_required
def index():
    """List all feature items"""
    pass

@bp.route('/feature/new', methods=['GET', 'POST'])
@login_required
def create():
    """Create new feature item"""
    pass

@bp.route('/feature/<int:id>')
@login_required
def view(id):
    """View feature details"""
    pass
```

**New Services/Business Logic:**
- **Service File:** `app/services/feature_service.py`
- **Functions:**
  - `process_feature_data(data)` - [Description]
  - `validate_feature_input(input)` - [Description]
  - `send_feature_notification(feature)` - [Description]

#### Integration Points with Existing Modules

**Module 1: [Module Name]**
- **Integration Type:** [Data sharing / Trigger / Display]
- **Description:** [How they interact]
- **Data Flow:** [Module 1] → [New Feature] → [Module 2]

**Module 2: [Module Name]**
- **Integration Type:** [Data sharing / Trigger / Display]
- **Description:** [How they interact]

**Automation Triggers:**
- [ ] Trigger new feature action when [event] occurs in [module]
- [ ] Update [module] when new feature status changes
- [ ] Send notification when [condition] is met

#### Permissions & Access Control

**Role-Based Access:**
- **Admin:** [Full access / Create / Edit / Delete / View]
- **Manager:** [Create / Edit / View]
- **Operator:** [View only]
- **Viewer:** [View only / No access]

**Decorator Required:**
```python
@role_required('admin', 'manager')
```

#### Data Validation & Business Rules

**Validation Rules:**
1. [Field name] must be [condition]
2. [Field name] cannot be [condition]
3. [Field name] must be unique within [scope]

**Business Rules:**
1. [Rule description]
2. [Rule description]

#### Error Handling

**Expected Errors:**
1. **Error:** [Description]
   - **Cause:** [What causes this error]
   - **Handling:** [How to handle it]
   - **User Message:** "[User-friendly error message]"

2. **Error:** [Description]
   - **Cause:** [What causes this error]
   - **Handling:** [How to handle it]
   - **User Message:** "[User-friendly error message]"

#### Testing Requirements

**Unit Tests:**
- Test model creation and validation
- Test business logic functions
- Test data validation rules

**Integration Tests:**
- Test feature workflow end-to-end
- Test integration with [Module 1]
- Test integration with [Module 2]

**User Acceptance Tests:**
1. [Test scenario 1]
2. [Test scenario 2]
3. [Test scenario 3]

#### Performance Considerations

- **Expected Data Volume:** [Number of records]
- **Query Optimization:** [Indexes needed, eager loading, etc.]
- **Caching Requirements:** [What should be cached]
- **Background Jobs:** [Any async processing needed]

#### Migration Plan

**Database Migration:**
```python
# migrations/versions/xxx_add_feature.py
def upgrade():
    # Add migration code here
    pass

def downgrade():
    # Add rollback code here
    pass
```

**Data Migration:**
- [ ] No existing data to migrate
- [ ] Migrate data from [source] to [destination]
- [ ] Populate default values for existing records

**Deployment Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

#### Documentation Requirements

- [ ] Update `docs/SYSTEM_ARCHITECTURE_GUIDE.md` with new module/feature
- [ ] Create user guide for new feature
- [ ] Update API documentation (if applicable)
- [ ] Add inline code comments
- [ ] Update README.md (if applicable)

#### Future Enhancements

[Optional: List potential future improvements to this feature]
1. [Enhancement 1]
2. [Enhancement 2]

#### Related Features/Requests

[Link to any related features or change requests]
```

---

## 📝 **EXAMPLES**

### **Example 1: Issue Report**

```markdown
### ISSUE REPORT

**Issue ID:** ISS-2025-001
**Date Reported:** 2025-10-27
**Reporter:** Gaz

#### Issue Type
- [x] Bug (functionality not working as intended)

#### Priority Level
- [x] HIGH (Major feature broken, blocking workflow)

#### Affected Module(s)
- [x] Queue
- [x] Projects

#### Issue Summary
Queue status update does not sync with project status, causing data inconsistency.

#### Detailed Description
When updating a queue item status from "Queued" to "In Progress", the corresponding project status remains unchanged at "Approved (POP Received)" instead of updating to "In Progress".

#### Steps to Reproduce
1. Navigate to Queue module
2. Select a queue item with status "Queued"
3. Click "Update Status" and change to "In Progress"
4. Navigate to Projects module
5. View the linked project

#### Expected Behavior
Project status should automatically update to "In Progress" when queue status changes to "In Progress".

#### Actual Behavior
Project status remains at "Approved (POP Received)" and does not sync.

#### Error Messages / Stack Trace
```
No error messages - silent failure
```

#### Affected Files
- File: `app/routes/queue.py`
  - Lines: 167-222
  - Function: `update_status(id)`

- File: `app/models/business.py`
  - Model: `QueueItem`
  - Model: `Project`

#### Potential Root Cause
Missing synchronization logic in the `update_status()` function.

#### Suggested Fix
Add project status update logic in `app/routes/queue.py` → `update_status()` function to sync queue status changes with project status.
```

---

### **Example 2: Change Request**

```markdown
### CHANGE REQUEST

**Request ID:** CHG-2025-001
**Date Requested:** 2025-10-27
**Requester:** Gaz

#### Priority Level
- [x] MEDIUM (Nice to have, moderate impact)

#### Affected Module(s)
- [x] Queue
- [x] Operators

#### Change Summary
Auto-select logged-in operator when creating a new laser run.

#### Current Behavior
When logging a new laser run, the operator dropdown is empty and requires manual selection.

**Current Workflow:**
1. Navigate to Queue → Log Laser Run
2. Manually select operator from dropdown
3. Enter cut time and other details
4. Submit

#### Desired Behavior
The operator dropdown should automatically pre-select the logged-in user's operator profile.

**Desired Workflow:**
1. Navigate to Queue → Log Laser Run
2. Operator is already selected (logged-in user)
3. Enter cut time and other details
4. Submit

#### Reason for Change
Reduces data entry time and improves accuracy since operators typically log their own runs.

#### Business Impact
- **Users Affected:** All operators (daily users)
- **Frequency of Use:** Multiple times per day
- **Time Savings:** ~5 seconds per laser run entry
- **Error Reduction:** Eliminates operator selection errors

#### Files Potentially Affected
- **Routes:** `app/routes/auth.py`, `app/routes/queue.py`
- **Templates:** `app/templates/queue/run_form.html`

#### Database Changes Required
- [x] No database changes

#### UI/UX Changes Required
- [x] Modify existing form/page: Laser Run Form
- Auto-select operator in dropdown
- Show "(You)" indicator next to logged-in operator

#### Integration Impact
- **Modules Affected:**
  - Operators: Need to link user account to operator profile
  - Queue: Need to pass operator context to form

- **Automation Systems Affected:**
  - [x] Operator Auto-bind (NEW automation system)

#### Testing Requirements
1. Test with user who has operator profile
2. Test with user who does NOT have operator profile
3. Verify "(You)" indicator displays correctly
```

---

### **Example 3: Feature Addition**

```markdown
### FEATURE ADDITION REQUEST

**Feature ID:** FEAT-2025-001
**Date Requested:** 2025-10-27
**Requester:** Gaz

#### Priority Level
- [x] MEDIUM (Valuable enhancement)

#### Feature Category
- [x] Module Enhancement (add to existing module)

#### Affected/Related Module(s)
- [x] Communications
- [x] Projects

#### Feature Name
Automated Message Templates with Milestone Triggers

#### Feature Description
Automatically send templated emails to clients when projects reach specific milestones (e.g., "Collection Ready" when status changes to "Completed").

#### Business Justification
**Problem Statement:**
Currently, staff must manually remember to send client notifications when projects are ready for collection, leading to delays and inconsistent communication.

**Business Value:**
- Improved customer satisfaction through timely notifications
- Reduced staff workload (no manual email sending)
- Consistent professional communication

**User Impact:**
- **Users Affected:** Admin, Managers (reduced workload)
- **Frequency of Use:** Automatic (triggered by project status changes)
- **Time Savings:** ~5 minutes per project completion
- **Error Reduction:** Eliminates forgotten notifications

#### User Workflow / Use Case

**Scenario:**
A laser cutting project is completed. The system should automatically notify the client that their order is ready for collection.

**User Story:**
As a manager, I want the system to automatically send "Collection Ready" emails when projects are completed, so that I don't have to manually notify each client.

**Workflow Steps:**
1. Operator marks queue item as "Completed"
2. System auto-updates project status to "Completed"
3. **NEW:** System detects status change to "Completed"
4. **NEW:** System finds "Collection Ready" message template
5. **NEW:** System populates template with project details
6. **NEW:** System sends email to client
7. **NEW:** System logs communication in database

#### Database Changes Needed

**Modifications to Existing Models:**
- **Model:** `MessageTemplate`
  - **Add Fields:**
    - `trigger_event` (Type: String(50), Nullable: True, Default: None)
      - Values: 'project_completed', 'pop_received', 'quote_sent', etc.
    - `is_auto_send` (Type: Boolean, Nullable: False, Default: False)

**No new models required** - uses existing `Communication` and `MessageTemplate` models.

#### UI/UX Requirements

**Modifications to Existing Pages:**
- **Page:** Message Template Form (`/comms/templates/<id>/edit`)
  - **Add:** Checkbox "Auto-send when triggered"
  - **Add:** Dropdown "Trigger Event" (project_completed, pop_received, etc.)

#### Backend Implementation

**New Services/Business Logic:**
- **Service File:** `app/services/communication_service.py`
- **Functions:**
  - `send_milestone_notification(project, trigger_event)` - Send templated email based on trigger
  - `get_template_for_trigger(trigger_event)` - Find active template for specific trigger

**Integration in Existing Routes:**
- **File:** `app/routes/queue.py` → `update_status()`
  - **Add:** Call `send_milestone_notification()` when project status changes to "Completed"

#### Integration Points with Existing Modules

**Module 1: Projects**
- **Integration Type:** Trigger
- **Description:** When project status changes, trigger notification check

**Module 2: Queue**
- **Integration Type:** Trigger
- **Description:** When queue status changes (which syncs to project), trigger notification

**Automation Triggers:**
- [x] Trigger email notification when project status changes to "Completed"
- [x] Trigger email notification when POP is marked received

#### Testing Requirements

**Integration Tests:**
- Test email sent when project status changes to "Completed"
- Test email NOT sent if no template configured for trigger
- Test email NOT sent if template is inactive
- Test template variables populated correctly

**User Acceptance Tests:**
1. Create message template with trigger "project_completed"
2. Mark project as completed
3. Verify email sent to client
4. Verify communication logged in database
```

---

## ✅ **IMPLEMENTATION TRACKING**

Use this section to track progress on requests.

```markdown
### IMPLEMENTATION STATUS

**Request ID:** [ID from above]
**Status:** [ ] Not Started / [ ] In Progress / [ ] Testing / [ ] Complete / [ ] Cancelled

#### Tasks
- [ ] Task 1: [Description]
- [ ] Task 2: [Description]
- [ ] Task 3: [Description]

#### Files Modified
- [ ] `app/routes/[module].py`
- [ ] `app/models/[model].py`
- [ ] `app/templates/[module]/[template].html`

#### Testing Completed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] User acceptance testing completed

#### Documentation Updated
- [ ] Code comments added
- [ ] Architecture guide updated
- [ ] User guide updated (if applicable)

#### Deployment
- [ ] Database migration created
- [ ] Migration tested on staging
- [ ] Deployed to production
- [ ] Post-deployment verification completed

#### Notes
[Any additional notes about implementation]
```

---

## 🎯 **TIPS FOR EFFECTIVE REQUESTS**

### **For AI Assistant Processing:**

1. **Be Specific:** Include exact file paths, line numbers, and function names when known
2. **Provide Context:** Explain the "why" behind the request, not just the "what"
3. **Reference Architecture:** Mention which of the 12 modules are affected
4. **Set Clear Priorities:** Use the priority levels to help with task planning
5. **Include Examples:** Show sample data or workflows when possible
6. **Think Downstream:** Consider what other files/modules might be affected
7. **One Request Per Template:** Don't combine multiple unrelated requests

### **Priority Level Guidelines:**

- **CRITICAL:** System down, data loss, security breach, blocking all work
- **HIGH:** Major feature broken, blocking important workflows, significant business impact
- **MEDIUM:** Feature partially broken, workaround exists, moderate business impact
- **LOW:** Minor issue, cosmetic problem, nice-to-have enhancement

### **File Path Format:**

Always use paths relative to workspace root:
```
✅ CORRECT: app/routes/queue.py
✅ CORRECT: app/models/business.py
✅ CORRECT: app/templates/queue/run_form.html

❌ INCORRECT: queue.py
❌ INCORRECT: /full_dxf_laser_buisness/app/routes/queue.py
```

---

## 📚 **ADDITIONAL RESOURCES**

- **System Architecture Guide:** `docs/SYSTEM_ARCHITECTURE_GUIDE.md`
- **Database Models:** `app/models/auth.py`, `app/models/business.py`, `app/models/sage.py`
- **Application Factory:** `app/__init__.py`
- **Main Entry Point:** `run.py`

---

**Template Version:** 1.0
**Last Updated:** 2025-10-27
**Maintained By:** Laser OS Development Team

