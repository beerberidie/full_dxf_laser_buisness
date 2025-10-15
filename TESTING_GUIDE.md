# Phase 1 Testing Guide - Manual Testing Checklist

This guide will help you manually test the Phase 1: Client Management features in your browser.

---

## Prerequisites

✅ Flask server running at http://127.0.0.1:5000  
✅ Database populated with 5 test clients  
✅ All automated tests passed

---

## Manual Testing Checklist

### 1. Dashboard Testing

**URL:** http://127.0.0.1:5000/

**Tests:**
- [ ] Dashboard loads without errors
- [ ] "Total Clients" shows 5
- [ ] "Total Projects" shows 0 (Phase 2 not implemented)
- [ ] "Active Projects" shows 0
- [ ] "Queue Length" shows 0
- [ ] Recent clients section shows up to 5 clients
- [ ] Navigation menu is visible
- [ ] All navigation links are present

**Expected Result:** Dashboard displays statistics and recent clients

---

### 2. Client List Testing

**URL:** http://127.0.0.1:5000/clients

**Tests:**
- [ ] Client list page loads
- [ ] All 5 test clients are displayed:
  - [ ] CL-0001: Test Client - Acme Manufacturing
  - [ ] CL-0002: Test Client - Precision Engineering
  - [ ] CL-0003: Test Client - BuildCo Construction
  - [ ] CL-0004: Test Client - Design Studio
  - [ ] CL-0005: Test Client - AutoParts Suppliers
- [ ] Client codes are clickable links
- [ ] Contact persons are displayed
- [ ] Email addresses are displayed
- [ ] Phone numbers are displayed
- [ ] "New Client" button is visible

**Expected Result:** Table showing all clients with their details

---

### 3. Client Search Testing

**URL:** http://127.0.0.1:5000/clients

**Test Cases:**

#### Test 3.1: Search by Name
- [ ] Enter "Engineering" in search box
- [ ] Click Search or press Enter
- [ ] Only "Precision Engineering" is shown
- [ ] Other clients are hidden

#### Test 3.2: Search by Contact Person
- [ ] Enter "Sarah" in search box
- [ ] Click Search
- [ ] Only client with contact "Sarah Johnson" is shown

#### Test 3.3: Search by Email
- [ ] Enter "acme" in search box
- [ ] Click Search
- [ ] Only "Acme Manufacturing" is shown

#### Test 3.4: Clear Search
- [ ] Clear search box
- [ ] Click Search
- [ ] All 5 clients are shown again

**Expected Result:** Search filters clients correctly

---

### 4. Client Detail Testing

**URL:** http://127.0.0.1:5000/clients/1

**Tests:**
- [ ] Client detail page loads
- [ ] Client code is displayed (CL-0001)
- [ ] Client name is displayed
- [ ] Contact person is displayed
- [ ] Email is displayed (clickable mailto: link)
- [ ] Phone is displayed (clickable tel: link)
- [ ] Address is displayed (multi-line)
- [ ] Notes are displayed
- [ ] Created timestamp is displayed
- [ ] Updated timestamp is displayed
- [ ] "Edit Client" button is visible
- [ ] "Delete Client" button is visible
- [ ] "Back to Clients" link is visible
- [ ] Activity Log section is present
- [ ] At least 1 activity log entry is shown (CREATE)

**Expected Result:** All client details displayed correctly

---

### 5. Create New Client Testing

**URL:** http://127.0.0.1:5000/clients/new

#### Test 5.1: Valid Client Creation
- [ ] Click "New Client" button from client list
- [ ] Form loads with all fields
- [ ] Fill in the form:
  - Name: "Test Client - Manual Test"
  - Contact Person: "Test User"
  - Email: "test@example.com"
  - Phone: "+27 11 000 0000"
  - Address: "123 Test Street\nTest City\n1234"
  - Notes: "Created during manual testing"
- [ ] Click "Create Client" button
- [ ] Redirected to client detail page
- [ ] Success message displayed
- [ ] Client code auto-generated (CL-0006)
- [ ] All entered data is displayed correctly

#### Test 5.2: Validation - Empty Name
- [ ] Go to new client form
- [ ] Leave "Name" field empty
- [ ] Fill in other fields
- [ ] Click "Create Client"
- [ ] Error message displayed: "Client name is required"
- [ ] Form is not submitted
- [ ] Other field values are preserved

#### Test 5.3: Optional Fields
- [ ] Go to new client form
- [ ] Fill in only "Name" field
- [ ] Leave all other fields empty
- [ ] Click "Create Client"
- [ ] Client created successfully
- [ ] Optional fields show as "N/A" or empty

**Expected Result:** Client creation works with validation

---

### 6. Edit Client Testing

**URL:** http://127.0.0.1:5000/clients/1/edit

#### Test 6.1: Edit Client Information
- [ ] Go to client detail page (CL-0001)
- [ ] Click "Edit Client" button
- [ ] Edit form loads with current values pre-filled
- [ ] Change phone number to "+27 11 888 7777"
- [ ] Change notes to "Updated during manual testing"
- [ ] Click "Update Client" button
- [ ] Redirected to client detail page
- [ ] Success message displayed
- [ ] Updated phone number is shown
- [ ] Updated notes are shown
- [ ] "Updated" timestamp has changed
- [ ] Activity log shows UPDATE entry

#### Test 6.2: Cancel Edit
- [ ] Go to edit form
- [ ] Make some changes
- [ ] Click "Cancel" or "Back to Client" link
- [ ] Redirected to client detail page
- [ ] Changes are NOT saved

**Expected Result:** Client editing works correctly

---

### 7. Delete Client Testing

**URL:** http://127.0.0.1:5000/clients/6/delete

#### Test 7.1: Delete with Confirmation
- [ ] Go to client detail page (CL-0006 - the manually created one)
- [ ] Click "Delete Client" button
- [ ] Confirmation dialog appears
- [ ] Click "OK" or "Confirm"
- [ ] Redirected to client list
- [ ] Success message displayed
- [ ] Deleted client is no longer in the list
- [ ] Client count decreased by 1

#### Test 7.2: Cancel Delete
- [ ] Go to another client detail page
- [ ] Click "Delete Client" button
- [ ] Confirmation dialog appears
- [ ] Click "Cancel"
- [ ] Client is NOT deleted
- [ ] Still on client detail page

**Expected Result:** Client deletion works with confirmation

---

### 8. Activity Logging Testing

**Tests:**
- [ ] Create a new client
- [ ] Check activity log shows CREATE entry
- [ ] Edit the client
- [ ] Check activity log shows UPDATE entry
- [ ] Activity log entries show:
  - [ ] Timestamp
  - [ ] Action (CREATE, UPDATE, DELETE)
  - [ ] Details (what changed)
  - [ ] IP address
  - [ ] User (admin)

**Expected Result:** All actions are logged

---

### 9. Navigation Testing

**Tests:**
- [ ] Click "Dashboard" - goes to /
- [ ] Click "Clients" - goes to /clients
- [ ] Click "Projects" - shows "Coming in Phase 2" message
- [ ] Click "Queue" - shows "Coming in Phase 3" message
- [ ] Click "Inventory" - shows "Coming in Phase 4" message
- [ ] Click "Reports" - shows "Coming in Phase 5" message
- [ ] Click "Parameters" - shows "Coming in Phase 6" message
- [ ] Logo/brand name links back to dashboard

**Expected Result:** Navigation works, placeholders shown for future phases

---

### 10. Responsive Design Testing

**Tests:**
- [ ] Resize browser window to mobile size (375px width)
- [ ] Navigation menu collapses or stacks vertically
- [ ] Tables are scrollable or responsive
- [ ] Forms are usable on mobile
- [ ] Buttons are touch-friendly
- [ ] Text is readable (not too small)

**Expected Result:** Interface works on mobile devices

---

### 11. Error Handling Testing

#### Test 11.1: Invalid Client ID
- [ ] Go to http://127.0.0.1:5000/clients/999
- [ ] 404 error page displayed
- [ ] Error message: "Client not found"

#### Test 11.2: Invalid Route
- [ ] Go to http://127.0.0.1:5000/invalid-route
- [ ] 404 error page displayed

**Expected Result:** Errors handled gracefully

---

## Test Data Summary

After automated tests, you should have these clients:

| Code | Name | Contact | Email | Phone |
|------|------|---------|-------|-------|
| CL-0001 | Test Client - Acme Manufacturing | John Smith | john.smith@acme.co.za | +27 11 999 8888 |
| CL-0002 | Test Client - Precision Engineering | Sarah Johnson | sarah@precision.co.za | +27 31 555 8888 |
| CL-0003 | Test Client - BuildCo Construction | Mike Williams | mike.w@buildco.co.za | +27 21 777 9999 |
| CL-0004 | Test Client - Design Studio | Emma Davis | emma@designstudio.co.za | +27 11 444 3333 |
| CL-0005 | Test Client - AutoParts Suppliers | David Brown | david@autoparts.co.za | +27 31 222 1111 |

---

## Browser Compatibility Testing

Test in these browsers:
- [ ] Google Chrome (latest)
- [ ] Mozilla Firefox (latest)
- [ ] Microsoft Edge (latest)
- [ ] Safari (if on Mac)

---

## Performance Testing

- [ ] Dashboard loads in < 1 second
- [ ] Client list loads in < 1 second
- [ ] Search responds instantly
- [ ] Form submissions are quick
- [ ] No lag or freezing

---

## Accessibility Testing

- [ ] All forms have labels
- [ ] All buttons have descriptive text
- [ ] Tab navigation works
- [ ] Focus indicators visible
- [ ] Color contrast is sufficient
- [ ] Alt text on images (if any)

---

## Security Testing

- [ ] SQL injection protection (try entering `'; DROP TABLE clients; --` in search)
- [ ] XSS protection (try entering `<script>alert('XSS')</script>` in name field)
- [ ] CSRF protection (forms have CSRF tokens)

---

## Sign-Off

Once all tests pass, sign off on Phase 1:

**Tested By:** ___________________________  
**Date:** ___________________________  
**Status:** [ ] PASS [ ] FAIL  
**Notes:** ___________________________

---

**Ready to proceed to Phase 2?** ✅

