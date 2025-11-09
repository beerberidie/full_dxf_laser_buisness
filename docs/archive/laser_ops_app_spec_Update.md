# Laser Cutting Management System — Application Specification (v1.0)

## 1. Dashboard
✅ **Status:** Approved and stable.
- Current layout, interactions, and button behavior are all satisfactory.
- No immediate design or functionality changes required.

---

## 2. Clients Module
### Overview
- Functionality confirmed as stable; all buttons working correctly.
- Auto-generated **Client Codes** functioning as intended.

### Form Fields
| Field | Requirement | Notes |
|-------|--------------|-------|
| Client Name | Required | Primary identifier |
| Contact Person | Required | Secondary identifier |
| Email | Optional | Used for comms matching |
| Phone Number | Optional | Used for comms matching |
| Address | Optional | Client records reference |
| Notes | Optional | General comments |

- Validation: required fields enforced.
- Behavior and UI confirmed as satisfactory.

---

## 3. Projects Module
### Overview
The **Projects tab** is the operational core of the system. It manages requests, quotes, approvals, scheduling, and completion.

### Table View
- Displays: Job code *(to be cleaned up)*, full date & day, client name, project name, status, due date, quoted price, created date, and actions (View/Edit).
- Filters by status: Quote, Approved, In Progress, Completed, Cancelled.
- **New Project** button launches project creation form.

### New Project Fields
| Field | Requirement | Description |
|--------|-------------|-------------|
| Project Name | Required | Core identifier |
| Client | Required | Auto-linked |
| DXF Files | Required to leave “Request” state |
| Material Type | Required | (Mild, Stainless, SureAZ, etc.) |
| Material Quantity (Sheets) | Required | For planning |
| Parts Quantity | Required | Used in ETA calc |
| Estimated Cut Time | Required | Total runtime |
| Number of Bins | Optional | For packaging organization |
| Drawing/DXF Creation Time | Optional | Manual input |
| Description / Notes | Optional | Supporting details |

### Status Lifecycle
| Status | Description | Transition Conditions |
|---------|--------------|-----------------------|
| **Request** | Intake phase | Created project awaiting DXFs/material/time data |
| **Quote & Approval** | Quote generated & attached | Triggered once all mandatory fields + DXF uploaded |
| **Approved (POP Received)** | Client approved & proof of payment confirmed | Manual tick (POP received) |
| **Queued (Scheduled for Cutting)** | Project scheduled | Auto-moved after POP confirmation; visible in “Today’s” and “Queue” |
| **In Progress** | Cutting active | Manual or system update |
| **Completed** | Job finalized | Status change triggers client comms |
| **Cancelled** | Job voided | Manual |

### Scheduling Logic (Enhanced Rule Integration)
- When **Proof of Payment (POP)** is confirmed (manual tick):
  - System sets a **3-day deadline window** from that date.
  - Job must be **scheduled, cut, and processed** within that period.
- **Due Date Logic:**
  - Preliminary due date may exist prior to payment.
  - Once POP is received, the system adjusts the due date (if earlier) or locks scheduling within the 3-day rule.
  - Queue system validates there are no overlaps or missed targets.
  - Conflict warnings displayed if rescheduling would cause violation of due date or 3-day cutoff.

### Files & Records
- Each project includes:
  - Quote (auto-parsed from file)
  - Invoice
  - Proof of Payment
  - Delivery Note *(optional)*
  - DXFs and related design data
- Manual toggles:
  - POP Received
  - Client Notified
  - Delivery Confirmed

### Notifications & Comms
- Automatic messages triggered on:
  - Project Completion
  - POP Receipt
  - Delivery Confirmation
- Mediums: Email, WhatsApp, and internal notifications.

---

## 4. Products Module
### Purpose
A **DXF Library** for reusable parts, templates, and custom items.

### Features
- SVG/DXF visual previews.
- Configurable by: Material Type, Thickness, Size/Shape, Quantity.
- Add to **Mini-Cart**, export as **Bundle (ZIP/JSON)** containing DXFs + metadata.
- SKU Codes aligned with internal project scheme.

### Admin Tools
- Upload new DXFs, assign SKUs, define base prices.
- Set pricing modifiers (material/thickness).
- Optional **Public Mode** for future web/e-commerce listing.

---

## 5. Queue Module
### Purpose
To manage scheduled and in-progress cutting tasks.

### Rules
- Jobs displayed with client, project name, estimated time, status, and run history.
- Rescheduling must respect:
  - Machine load
  - Estimated total cut time
  - Deadlines (including 3-day post-POP rule)
- Conflict handling:
  - Prevent overlaps
  - Offer next available slot suggestion
  - Record override reason

### Additional
- History view lists job, time, operator, and notes.
- Queue syncs with **Project statuses** and **Scheduling logic**.
- Includes **audit trail** for reschedules and conflicts.

---

## 6. Inventory Module
### UI Enhancements
- Standardized dropdowns, search bars, and input fields.

### Categories
- Sheet Materials
- Gases
- Consumables (gloves, brushes, cloths, greases, tape, etc.)
- Tools
- Other (misc supplies)

### Data Model
- Name, SKU, Category, Unit, Stock levels, Supplier, Cost, Tax, Location, Notes.
- Specifics per category (e.g., thickness for sheet, type for gas).

### Transactions
- Receive, Issue, Adjust, Return, Transfer.
- Attach invoices or GRNs.
- Full transaction history maintained with audit trail.

### Low Stock Alerts
- Auto-flag under minimum.
- Optional daily digest or dashboard badge.

---

## 7. Reports
- **Status:** Working and visually fine.
- **Requirement:** Ensure report data and filters are accurate.
- Must support PDF/CSV export, timestamps, and totals.
- Consistent UI design.

---

## 8. Comms Tab (New)
### Purpose
Unified communication hub for **Email**, **WhatsApp**, and **Notifications**.

### Features
- Send/receive emails directly.
- WhatsApp business API integration (future-ready).
- Auto-match communications to **Clients** and **Projects**.
- Unlinked messages remain in queue for manual assignment.
- View inbound/outbound messages with timestamps and attachments.

### Automation (Future Enhancements)
- Auto-detect client requests → create **Project Requests** from messages.
- AI parsing: detect part names, materials, quantities, delivery dates.
- Smart linking to historical projects for repeat orders.

### UI
- Sidebar filters (All / Email / WhatsApp / Notifications / Unlinked).
- Main pane: Conversations.
- Detail view: Thread + reply box + quick actions.
- Styling unified with app theme.

---

## 9. Scheduling Integration Summary
- **POP Confirmation** = trigger event.
- From confirmation day, schedule job for **cutting within 3 days**.
- **Due Date Reconciliation:**
  - Compare preliminary due date with POP+3-day rule.
  - Use whichever is sooner, unless overridden.
- **Queue Enforcer:**
  - Prevent conflicts/missed deadlines.
  - Display alerts for any approaching or breached 3-day window.

---

## Final Notes
- UI cohesion prioritized across all modules.
- Backend logic ties **Projects**, **Queue**, **Comms**, and **Scheduling** into a unified workflow.
- Future integrations (Comms automation, product publishing, AI parsing) layer cleanly on current structure.