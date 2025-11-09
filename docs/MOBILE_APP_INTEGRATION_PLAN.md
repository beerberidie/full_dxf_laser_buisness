# Mobile Application Integration Plan
## Laser Sync Flow → Laser OS Integration

**Document Version:** 1.0  
**Date:** 2025-10-27  
**Status:** Analysis & Planning Phase

---

## Executive Summary

This document outlines the comprehensive integration plan for the **Laser Sync Flow** mobile application with the main **Laser OS** desktop application. The mobile app is designed for field operators to log and manage laser cutting jobs ready for cutting, while the main application is a full-featured Flask-based laser cutting business management system.

### Key Integration Goals
1. Enable mobile operators to view and manage the cutting queue in real-time
2. Allow mobile job creation and status updates that sync with the main system
3. Provide field operators with project visibility and job scheduling capabilities
4. Maintain data consistency between mobile and desktop applications
5. Support offline-capable mobile operations with sync when connected

---

## 1. Technology Stack Analysis

### 1.1 Mobile Application (Laser Sync Flow)
- **Framework:** React 18.3.1 with TypeScript
- **Build Tool:** Vite 5.4.19
- **UI Library:** shadcn/ui (Radix UI components)
- **Styling:** Tailwind CSS 3.4.17
- **State Management:** React hooks (useState) + TanStack Query 5.83.0
- **Routing:** React Router DOM 6.30.1
- **Form Handling:** React Hook Form 7.61.1 + Zod 3.25.76
- **Data Storage:** Currently in-memory (mock data)
- **Platform:** Web-based (can be deployed as PWA)

### 1.2 Main Application (Laser OS)
- **Framework:** Flask (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Flask-Login with role-based access control (RBAC)
- **Frontend:** Jinja2 templates with traditional server-side rendering
- **API Capabilities:** Limited JSON endpoints (presets, queue reordering)
- **Architecture:** Monolithic with Blueprint-based modular routing

### 1.3 Technology Gap Analysis
| Aspect | Mobile App | Main App | Integration Challenge |
|--------|-----------|----------|----------------------|
| **Data Layer** | In-memory mock | SQLite database | Need API bridge |
| **Authentication** | None (mock user) | Flask-Login sessions | Need mobile auth strategy |
| **Real-time Updates** | None | None | Need WebSocket or polling |
| **API** | None | Minimal JSON endpoints | Need comprehensive REST API |
| **Offline Support** | None | N/A | Need local storage + sync |

---

## 2. Current Feature Analysis

### 2.1 Mobile App Features (Laser Sync Flow)

#### Dashboard View
- Queue summary (active/ready jobs count)
- Projects summary (unscheduled projects count)
- Quick navigation to Queue and Projects

#### Queue Management
- **View Jobs:** List all queued jobs with status (pending, running, paused, complete)
- **Job Details:** Material type, thickness, plate count, estimated cut time, preset, parts list, DXF files
- **Job Actions:**
  - Start job (with confirmation modal)
  - Pause running job
  - Complete job (records actual cut time)
  - Edit job details
  - View full job details
- **Status Tracking:** Visual status badges (pending, running, paused, complete)

#### Project Management
- **View Projects:** List unscheduled projects with completion progress
- **Project Details:** Parts list, missing data indicators, material info, preset
- **Project Actions:**
  - View project details
  - Edit project information
  - Add complete project to queue
- **Progress Tracking:** Visual progress bar showing data completeness

#### Settings/Profile
- Operator profile display
- Jobs completed counter
- Today's schedule view
- Connection status (to PC)
- Logout functionality

### 2.2 Main App Features (Laser OS)

#### Project Management
- **Full Lifecycle:** Request → Quote & Approval → Approved (POP Received) → Queued → In Progress → Completed
- **Client Association:** Projects linked to clients
- **Material Tracking:** Material type, thickness, quantity (sheets)
- **Pricing:** Quoted price, final price
- **Timeline:** Quote date, approval date, due date, completion date
- **POP Tracking:** Proof of payment received status and deadline
- **Documents:** Multiple document types (quotes, invoices, POP, delivery notes)
- **Design Files:** DXF and LBRN2 file uploads with metadata extraction
- **Status Automation:** Auto-advance to quote approval, auto-queue on POP

#### Queue System
- **Queue Items:** Projects scheduled for cutting with position ordering
- **Priority Levels:** High, Normal, Low
- **Scheduling:** Scheduled date for each queue item
- **Status Tracking:** Queued, In Progress, Completed, Cancelled
- **Laser Runs:** Historical record of completed cuts with operator, preset, actual cut time
- **Reordering:** Drag-and-drop queue position changes

#### Operator Management
- **Operator Records:** Name, employee ID, contact info
- **Laser Run Association:** Track which operator performed each cut
- **Performance Tracking:** Jobs completed, total cut time

#### Machine Settings Presets
- **Preset Library:** Material type + thickness combinations
- **Settings:** Power, speed, frequency, gas type, pressure, focus offset
- **Active/Inactive:** Enable/disable presets
- **API Endpoint:** `/queue/api/presets` returns JSON list

#### Authentication & Authorization
- **User Accounts:** Username, email, password (hashed)
- **Roles:** Admin, Manager, Operator, Viewer
- **Permissions:** Role-based access control
- **Session Management:** Flask-Login sessions
- **Login History:** Audit trail of login attempts

---

## 3. Data Model Mapping

### 3.1 Mobile App Data Models

```typescript
interface Job {
  id: string;
  projectName: string;
  parts: { name: string; quantity: number }[];
  rawPlateCount: number;
  estimatedCutTime: number; // minutes
  drawingTime: number; // minutes
  materialType: string;
  thickness: number;
  preset: string;
  dxfFiles: string[];
  status: "pending" | "running" | "paused" | "complete";
  actualCutTime?: number;
  startedAt?: Date;
  completedAt?: Date;
}

interface Project {
  id: string;
  name: string;
  progress: number;
  missingData: string[];
  parts: { name: string; quantity: number }[];
  status: "incomplete" | "unscheduled";
  materialType?: string;
  thickness?: number;
  preset?: string;
  rawPlateCount?: number;
  estimatedCutTime?: number;
  drawingTime?: number;
  dxfFiles?: string[];
}
```

### 3.2 Main App Data Models (Relevant to Mobile)

```python
class Project(db.Model):
    # Core fields
    id: int
    project_code: str  # JB-yyyy-mm-CLxxxx-###
    client_id: int
    name: str
    description: str
    status: str  # Request, Quote & Approval, Approved (POP Received), Queued, In Progress, Completed, Cancelled
    
    # Material & production
    material_type: str
    material_thickness: Decimal
    material_quantity_sheets: int
    parts_quantity: int
    estimated_cut_time: int  # minutes
    drawing_creation_time: int  # minutes
    
    # Timeline
    quote_date: date
    approval_date: date
    due_date: date
    completion_date: date
    
    # POP tracking
    pop_received: bool
    pop_received_date: date
    pop_deadline: date

class QueueItem(db.Model):
    id: int
    project_id: int
    queue_position: int
    status: str  # Queued, In Progress, Completed, Cancelled
    priority: str  # High, Normal, Low
    scheduled_date: date
    estimated_cut_time: int
    notes: str
    added_by: str
    added_at: datetime
    started_at: datetime
    completed_at: datetime

class LaserRun(db.Model):
    id: int
    project_id: int
    queue_item_id: int
    run_date: datetime
    operator_id: int
    preset_id: int
    cut_time_minutes: int
    material_type: str
    material_thickness: Decimal
    sheet_count: int
    parts_produced: int
    notes: str
    status: str

class Operator(db.Model):
    id: int
    name: str
    employee_id: str
    email: str
    phone: str
    is_active: bool

class MachineSettingsPreset(db.Model):
    id: int
    preset_name: str
    material_type: str
    thickness: Decimal
    power: int
    speed: int
    frequency: int
    gas_type: str
    gas_pressure: Decimal
    focus_offset: Decimal
    is_active: bool
```

### 3.3 Field Mapping

| Mobile Field | Main App Field | Notes |
|-------------|----------------|-------|
| `Job.id` | `QueueItem.id` | Queue item ID |
| `Job.projectName` | `Project.name` | Project name |
| `Job.rawPlateCount` | `Project.material_quantity_sheets` | Sheet count |
| `Job.estimatedCutTime` | `QueueItem.estimated_cut_time` or `Project.estimated_cut_time` | Minutes |
| `Job.drawingTime` | `Project.drawing_creation_time` | Minutes |
| `Job.materialType` | `Project.material_type` | Material name |
| `Job.thickness` | `Project.material_thickness` | Millimeters |
| `Job.preset` | `MachineSettingsPreset.preset_name` (via `LaserRun.preset_id`) | Preset name |
| `Job.status` | `QueueItem.status` | Mapped: pending→Queued, running→In Progress, complete→Completed |
| `Job.actualCutTime` | `LaserRun.cut_time_minutes` | Recorded after completion |
| `Job.startedAt` | `QueueItem.started_at` | Timestamp |
| `Job.completedAt` | `QueueItem.completed_at` | Timestamp |
| `Project.id` | `Project.id` | Project ID |
| `Project.name` | `Project.name` | Project name |
| `Project.status` | Derived from `Project.status` | incomplete→not all fields filled, unscheduled→ready but not queued |

---

## 4. Integration Architecture

### 4.1 Recommended Architecture: REST API + JWT Authentication

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile App (React)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Dashboard  │  │   Queue    │  │  Projects  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│         │                │                │                  │
│         └────────────────┴────────────────┘                  │
│                          │                                   │
│                   ┌──────▼──────┐                           │
│                   │ API Client  │                           │
│                   │ (Axios/Fetch)│                          │
│                   └──────┬──────┘                           │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTPS + JWT Token
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Laser OS Backend (Flask)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           NEW: Mobile API Blueprint                     │ │
│  │  /api/mobile/auth/login                                │ │
│  │  /api/mobile/auth/refresh                              │ │
│  │  /api/mobile/queue (GET, POST)                         │ │
│  │  /api/mobile/queue/{id} (GET, PATCH, DELETE)           │ │
│  │  /api/mobile/queue/{id}/start                          │ │
│  │  /api/mobile/queue/{id}/pause                          │ │
│  │  /api/mobile/queue/{id}/complete                       │ │
│  │  /api/mobile/projects (GET)                            │ │
│  │  /api/mobile/projects/{id} (GET, PATCH)                │ │
│  │  /api/mobile/projects/{id}/add-to-queue                │ │
│  │  /api/mobile/presets (GET)                             │ │
│  │  /api/mobile/operators/me (GET)                        │ │
│  │  /api/mobile/operators/me/stats (GET)                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        Existing Flask Blueprints                        │ │
│  │  /projects, /queue, /clients, /operators, etc.         │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              SQLAlchemy ORM                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           SQLite Database (laser_os.db)                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Authentication Strategy

**Option 1: JWT Token-Based (RECOMMENDED)**
- Mobile app sends username/password to `/api/mobile/auth/login`
- Backend validates credentials and returns JWT access token + refresh token
- Mobile app stores tokens in localStorage/sessionStorage
- All API requests include `Authorization: Bearer <token>` header
- Tokens expire after configurable time (e.g., 1 hour for access, 7 days for refresh)
- Refresh endpoint `/api/mobile/auth/refresh` issues new access token

**Benefits:**
- Stateless authentication (no server-side session storage)
- Works well with mobile/SPA applications
- Can include operator ID and role in JWT payload
- Easy to implement token refresh logic

**Implementation:**
- Use `PyJWT` library for token generation/validation
- Store operator ID and role in token payload
- Implement token blacklist for logout (optional)

**Option 2: Session-Based (Alternative)**
- Reuse existing Flask-Login sessions
- Mobile app maintains session cookie
- Requires CORS configuration and cookie handling

**Recommendation:** Use JWT (Option 1) for better mobile compatibility and stateless architecture.

---

## 5. API Endpoint Specifications

### 5.1 Authentication Endpoints

#### POST `/api/mobile/auth/login`
**Purpose:** Authenticate operator and receive JWT tokens

**Request Body:**
```json
{
  "username": "operator1",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "operator": {
    "id": 1,
    "name": "John Anderson",
    "employee_id": "OP-001",
    "email": "john@example.com",
    "role": "operator"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

#### POST `/api/mobile/auth/refresh`
**Purpose:** Refresh access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### POST `/api/mobile/auth/logout`
**Purpose:** Invalidate tokens (optional - for token blacklist)

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### 5.2 Queue Endpoints

#### GET `/api/mobile/queue`
**Purpose:** Get all active queue items

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status` (optional): Filter by status (queued, in_progress, completed, all)
- `limit` (optional): Limit results (default: 50)

**Response (200 OK):**
```json
{
  "success": true,
  "queue_items": [
    {
      "id": 1,
      "project_id": 42,
      "project_code": "JB-2025-10-CL0001-001",
      "project_name": "Steel Brackets - Series A",
      "queue_position": 1,
      "status": "queued",
      "priority": "normal",
      "scheduled_date": "2025-10-27",
      "estimated_cut_time": 45,
      "material_type": "Mild Steel",
      "material_thickness": 3.0,
      "raw_plate_count": 3,
      "drawing_time": 15,
      "preset_name": "Steel-3mm-Standard",
      "preset_id": 5,
      "parts": [
        {"name": "Bracket-L-100", "quantity": 25},
        {"name": "Bracket-R-100", "quantity": 25},
        {"name": "Support-Plate", "quantity": 10}
      ],
      "dxf_files": [
        {"id": 101, "filename": "bracket-left.dxf"},
        {"id": 102, "filename": "bracket-right.dxf"},
        {"id": 103, "filename": "support.dxf"}
      ],
      "added_at": "2025-10-26T14:30:00Z",
      "started_at": null,
      "completed_at": null
    }
  ],
  "stats": {
    "total_queued": 5,
    "total_in_progress": 1,
    "total_completed": 247,
    "total_active": 6
  }
}
```

#### GET `/api/mobile/queue/{id}`
**Purpose:** Get detailed information for a specific queue item

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "queue_item": {
    "id": 1,
    "project_id": 42,
    "project_code": "JB-2025-10-CL0001-001",
    "project_name": "Steel Brackets - Series A",
    "client_name": "ABC Manufacturing",
    "queue_position": 1,
    "status": "queued",
    "priority": "normal",
    "scheduled_date": "2025-10-27",
    "estimated_cut_time": 45,
    "material_type": "Mild Steel",
    "material_thickness": 3.0,
    "raw_plate_count": 3,
    "drawing_time": 15,
    "preset_name": "Steel-3mm-Standard",
    "preset_id": 5,
    "parts": [
      {"name": "Bracket-L-100", "quantity": 25},
      {"name": "Bracket-R-100", "quantity": 25},
      {"name": "Support-Plate", "quantity": 10}
    ],
    "dxf_files": [
      {"id": 101, "filename": "bracket-left.dxf", "file_size": 245678},
      {"id": 102, "filename": "bracket-right.dxf", "file_size": 245123},
      {"id": 103, "filename": "support.dxf", "file_size": 123456}
    ],
    "notes": "Customer requested priority completion",
    "added_by": "admin",
    "added_at": "2025-10-26T14:30:00Z",
    "started_at": null,
    "completed_at": null
  }
}
```

#### POST `/api/mobile/queue/{id}/start`
**Purpose:** Start a queued job

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "operator_id": 1,
  "preset_id": 5,
  "notes": "Starting job with standard settings"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job started successfully",
  "queue_item": {
    "id": 1,
    "status": "in_progress",
    "started_at": "2025-10-27T08:15:00Z"
  }
}
```

**Business Logic:**
1. Validate queue item exists and is in "queued" status
2. Update `QueueItem.status` to "In Progress"
3. Set `QueueItem.started_at` to current timestamp
4. Update `Project.status` to "In Progress" if not already
5. Log activity in `ActivityLog`

#### POST `/api/mobile/queue/{id}/pause`
**Purpose:** Pause a running job

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "reason": "Material shortage - waiting for delivery"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job paused successfully",
  "queue_item": {
    "id": 1,
    "status": "queued",
    "notes": "Paused: Material shortage - waiting for delivery"
  }
}
```

**Business Logic:**
1. Validate queue item is in "in_progress" status
2. Update `QueueItem.status` back to "Queued"
3. Append pause reason to notes
4. Log activity in `ActivityLog`

#### POST `/api/mobile/queue/{id}/complete`
**Purpose:** Mark a job as completed and record laser run

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "operator_id": 1,
  "preset_id": 5,
  "actual_cut_time": 48,
  "sheet_count": 3,
  "parts_produced": 60,
  "notes": "Job completed successfully, all parts within tolerance"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job completed successfully",
  "queue_item": {
    "id": 1,
    "status": "completed",
    "completed_at": "2025-10-27T09:03:00Z"
  },
  "laser_run": {
    "id": 523,
    "run_date": "2025-10-27T09:03:00Z",
    "cut_time_minutes": 48,
    "operator_name": "John Anderson"
  }
}
```

**Business Logic:**
1. Validate queue item is in "in_progress" status
2. Update `QueueItem.status` to "Completed"
3. Set `QueueItem.completed_at` to current timestamp
4. Create new `LaserRun` record with:
   - `project_id`, `queue_item_id`
   - `operator_id`, `preset_id`
   - `cut_time_minutes` (actual_cut_time)
   - `sheet_count`, `parts_produced`
   - `material_type`, `material_thickness` (from project)
   - `run_date` (current timestamp)
   - `notes`
5. Update `Project.status` to "Completed" if all queue items for project are done
6. Log activity in `ActivityLog`

#### PATCH `/api/mobile/queue/{id}`
**Purpose:** Update queue item details

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "priority": "high",
  "scheduled_date": "2025-10-28",
  "estimated_cut_time": 50,
  "notes": "Updated priority due to customer request"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Queue item updated successfully",
  "queue_item": {
    "id": 1,
    "priority": "high",
    "scheduled_date": "2025-10-28",
    "estimated_cut_time": 50,
    "notes": "Updated priority due to customer request"
  }
}
```

### 5.3 Project Endpoints

#### GET `/api/mobile/projects`
**Purpose:** Get unscheduled projects ready to be added to queue

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status` (optional): Filter by status (default: approved_pop, unscheduled)
- `limit` (optional): Limit results (default: 50)

**Response (200 OK):**
```json
{
  "success": true,
  "projects": [
    {
      "id": 45,
      "project_code": "JB-2025-10-CL0002-003",
      "name": "Enclosure Panels - Series B",
      "client_name": "XYZ Corp",
      "status": "Approved (POP Received)",
      "material_type": "Aluminum",
      "material_thickness": 2.0,
      "raw_plate_count": 4,
      "estimated_cut_time": 55,
      "drawing_time": 18,
      "parts_quantity": 60,
      "parts": [
        {"name": "Side-Panel-Left", "quantity": 20},
        {"name": "Side-Panel-Right", "quantity": 20},
        {"name": "Top-Cover", "quantity": 20}
      ],
      "dxf_files": [
        {"id": 201, "filename": "side-left.dxf"},
        {"id": 202, "filename": "side-right.dxf"},
        {"id": 203, "filename": "top-cover.dxf"}
      ],
      "preset_id": 8,
      "preset_name": "Aluminum-2mm-Fine",
      "pop_received": true,
      "pop_deadline": "2025-10-29",
      "due_date": "2025-11-05",
      "data_completeness": 100,
      "missing_fields": []
    }
  ]
}
```

#### GET `/api/mobile/projects/{id}`
**Purpose:** Get detailed project information

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "project": {
    "id": 45,
    "project_code": "JB-2025-10-CL0002-003",
    "name": "Enclosure Panels - Series B",
    "description": "Custom enclosure panels for industrial equipment",
    "client_id": 2,
    "client_name": "XYZ Corp",
    "client_contact": "Jane Smith",
    "status": "Approved (POP Received)",
    "material_type": "Aluminum",
    "material_thickness": 2.0,
    "raw_plate_count": 4,
    "estimated_cut_time": 55,
    "drawing_time": 18,
    "parts_quantity": 60,
    "parts": [
      {"name": "Side-Panel-Left", "quantity": 20},
      {"name": "Side-Panel-Right", "quantity": 20},
      {"name": "Top-Cover", "quantity": 20}
    ],
    "dxf_files": [
      {"id": 201, "filename": "side-left.dxf", "file_size": 345678, "upload_date": "2025-10-25T10:00:00Z"},
      {"id": 202, "filename": "side-right.dxf", "file_size": 345123, "upload_date": "2025-10-25T10:00:00Z"},
      {"id": 203, "filename": "top-cover.dxf", "file_size": 234567, "upload_date": "2025-10-25T10:00:00Z"}
    ],
    "preset_id": 8,
    "preset_name": "Aluminum-2mm-Fine",
    "pop_received": true,
    "pop_received_date": "2025-10-26",
    "pop_deadline": "2025-10-29",
    "due_date": "2025-11-05",
    "quoted_price": 15000.00,
    "notes": "Customer requires delivery by Nov 5th",
    "created_at": "2025-10-20T09:00:00Z"
  }
}
```

#### POST `/api/mobile/projects/{id}/add-to-queue`
**Purpose:** Add a project to the cutting queue

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "priority": "normal",
  "scheduled_date": "2025-10-28",
  "estimated_cut_time": 55,
  "notes": "Customer priority - deliver by Nov 5th"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Project added to queue successfully",
  "queue_item": {
    "id": 15,
    "project_id": 45,
    "queue_position": 6,
    "status": "queued",
    "priority": "normal",
    "scheduled_date": "2025-10-28"
  }
}
```

**Business Logic:**
1. Validate project exists and is in "Approved (POP Received)" status
2. Check if project is already in active queue (prevent duplicates)
3. Calculate next queue position
4. Create new `QueueItem` record
5. Update `Project.status` to "Queued (Scheduled for Cutting)"
6. Log activity in `ActivityLog`

#### PATCH `/api/mobile/projects/{id}`
**Purpose:** Update project details (limited fields for mobile)

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "material_type": "Aluminum",
  "material_thickness": 2.0,
  "raw_plate_count": 4,
  "estimated_cut_time": 60,
  "preset_id": 8,
  "notes": "Updated material specifications"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Project updated successfully",
  "project": {
    "id": 45,
    "material_type": "Aluminum",
    "material_thickness": 2.0,
    "raw_plate_count": 4,
    "estimated_cut_time": 60,
    "preset_id": 8
  }
}
```

### 5.4 Preset Endpoints

#### GET `/api/mobile/presets`
**Purpose:** Get all active machine settings presets

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `material_type` (optional): Filter by material type
- `thickness` (optional): Filter by thickness

**Response (200 OK):**
```json
{
  "success": true,
  "presets": [
    {
      "id": 5,
      "preset_name": "Steel-3mm-Standard",
      "material_type": "Mild Steel",
      "thickness": 3.0,
      "power": 80,
      "speed": 1200,
      "frequency": 5000,
      "gas_type": "Air",
      "gas_pressure": 1.5,
      "focus_offset": 0.0,
      "is_active": true
    },
    {
      "id": 8,
      "preset_name": "Aluminum-2mm-Fine",
      "material_type": "Aluminum",
      "thickness": 2.0,
      "power": 75,
      "speed": 1500,
      "frequency": 6000,
      "gas_type": "Nitrogen",
      "gas_pressure": 2.0,
      "focus_offset": 0.5,
      "is_active": true
    }
  ]
}
```

### 5.5 Operator Endpoints

#### GET `/api/mobile/operators/me`
**Purpose:** Get current operator's profile information

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "operator": {
    "id": 1,
    "name": "John Anderson",
    "employee_id": "OP-001",
    "email": "john@example.com",
    "phone": "+27 11 123 4567",
    "is_active": true,
    "created_at": "2024-01-15T08:00:00Z"
  }
}
```

#### GET `/api/mobile/operators/me/stats`
**Purpose:** Get current operator's performance statistics

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_jobs_completed": 247,
    "total_cut_time_hours": 1523.5,
    "jobs_this_month": 18,
    "jobs_this_week": 4,
    "jobs_today": 1,
    "average_cut_time_minutes": 52.3,
    "most_used_material": "Mild Steel",
    "most_used_preset": "Steel-3mm-Standard"
  },
  "recent_jobs": [
    {
      "id": 520,
      "project_code": "JB-2025-10-CL0005-012",
      "project_name": "Custom Brackets",
      "run_date": "2025-10-26T14:30:00Z",
      "cut_time_minutes": 45,
      "material_type": "Mild Steel",
      "parts_produced": 50
    }
  ],
  "todays_schedule": [
    {
      "queue_item_id": 1,
      "project_code": "JB-2025-10-CL0001-001",
      "project_name": "Steel Brackets - Series A",
      "scheduled_time": "08:00",
      "estimated_cut_time": 45,
      "status": "queued"
    },
    {
      "queue_item_id": 3,
      "project_code": "JB-2025-10-CL0003-005",
      "project_name": "Aluminum Panels - QTY 50",
      "scheduled_time": "10:30",
      "estimated_cut_time": 60,
      "status": "queued"
    }
  ]
}
```

---

## 6. Data Synchronization Strategy

### 6.1 Real-Time Updates

**Challenge:** The mobile app needs to reflect changes made in the desktop application and vice versa.

**Solution Options:**

#### Option A: Polling (RECOMMENDED for MVP)
- Mobile app polls `/api/mobile/queue` and `/api/mobile/projects` every 30-60 seconds
- Simple to implement, no additional infrastructure
- Works well for low-frequency updates
- Can use HTTP `If-Modified-Since` headers to reduce bandwidth

**Implementation:**
```typescript
// Mobile app polling logic
useEffect(() => {
  const pollInterval = setInterval(() => {
    fetchQueueItems();
    fetchProjects();
  }, 30000); // Poll every 30 seconds

  return () => clearInterval(pollInterval);
}, []);
```

#### Option B: WebSockets (Future Enhancement)
- Real-time bidirectional communication
- Server pushes updates to mobile clients immediately
- Requires WebSocket server (Flask-SocketIO)
- Better user experience but more complex

**Implementation (Future):**
```python
# Backend: Flask-SocketIO
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to Laser OS'})

# Emit events when queue changes
def notify_queue_update(queue_item_id):
    socketio.emit('queue_updated', {'queue_item_id': queue_item_id})
```

```typescript
// Mobile app: Socket.IO client
import io from 'socket.io-client';

const socket = io('http://laser-os-server:5000');

socket.on('queue_updated', (data) => {
  // Refresh queue item
  fetchQueueItem(data.queue_item_id);
});
```

**Recommendation:** Start with polling (Option A) for MVP, migrate to WebSockets (Option B) if real-time updates become critical.

### 6.2 Offline Support

**Challenge:** Mobile operators may work in areas with intermittent connectivity.

**Solution: Progressive Web App (PWA) with Service Workers**

**Capabilities:**
1. **Cache API responses** for offline viewing
2. **Queue actions** when offline, sync when online
3. **Store JWT tokens** in localStorage
4. **Background sync** for pending actions

**Implementation:**
```typescript
// Service Worker registration
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// Offline action queue
const offlineQueue = [];

async function completeJob(queueItemId, data) {
  try {
    const response = await fetch(`/api/mobile/queue/${queueItemId}/complete`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error('Network error');
    return await response.json();
  } catch (error) {
    // Queue for later sync
    offlineQueue.push({
      action: 'complete_job',
      queueItemId,
      data,
      timestamp: Date.now()
    });

    // Store in IndexedDB
    await saveToIndexedDB('offline_queue', offlineQueue);

    // Show offline notification
    toast.warning('Action queued - will sync when online');
  }
}

// Sync when online
window.addEventListener('online', async () => {
  const queue = await loadFromIndexedDB('offline_queue');

  for (const action of queue) {
    try {
      await executeAction(action);
      // Remove from queue on success
    } catch (error) {
      // Keep in queue for retry
    }
  }
});
```

### 6.3 Conflict Resolution

**Scenario:** Desktop user and mobile operator modify the same queue item simultaneously.

**Strategy: Last-Write-Wins with Optimistic Locking**

**Implementation:**
1. Include `updated_at` timestamp in all API responses
2. Mobile app sends `updated_at` with PATCH requests
3. Backend checks if `updated_at` matches current database value
4. If mismatch, return 409 Conflict error
5. Mobile app prompts user to refresh and retry

**Example:**
```python
# Backend conflict detection
@bp.route('/api/mobile/queue/<int:id>', methods=['PATCH'])
def update_queue_item(id):
    queue_item = QueueItem.query.get_or_404(id)

    # Get client's last known updated_at
    client_updated_at = request.json.get('updated_at')

    if client_updated_at:
        client_dt = datetime.fromisoformat(client_updated_at)
        if queue_item.updated_at > client_dt:
            return jsonify({
                'success': False,
                'error': 'Conflict: Item was modified by another user',
                'current_data': queue_item.to_dict()
            }), 409

    # Proceed with update
    # ...
```

---

## 7. Implementation Roadmap

### Phase 1: Backend API Development (Week 1-2)

**Tasks:**
1. ✅ Create new Flask blueprint: `app/routes/mobile_api.py`
2. ✅ Implement JWT authentication:
   - Install `PyJWT` library
   - Create token generation/validation utilities
   - Implement `/api/mobile/auth/login` endpoint
   - Implement `/api/mobile/auth/refresh` endpoint
3. ✅ Implement Queue API endpoints:
   - `GET /api/mobile/queue` (list)
   - `GET /api/mobile/queue/{id}` (detail)
   - `POST /api/mobile/queue/{id}/start`
   - `POST /api/mobile/queue/{id}/pause`
   - `POST /api/mobile/queue/{id}/complete`
   - `PATCH /api/mobile/queue/{id}` (update)
4. ✅ Implement Project API endpoints:
   - `GET /api/mobile/projects` (list unscheduled)
   - `GET /api/mobile/projects/{id}` (detail)
   - `POST /api/mobile/projects/{id}/add-to-queue`
   - `PATCH /api/mobile/projects/{id}` (update)
5. ✅ Implement Preset API endpoint:
   - `GET /api/mobile/presets`
6. ✅ Implement Operator API endpoints:
   - `GET /api/mobile/operators/me`
   - `GET /api/mobile/operators/me/stats`
7. ✅ Add CORS support for mobile app origin
8. ✅ Write API documentation
9. ✅ Create Postman/Thunder Client collection for testing

**Deliverables:**
- Fully functional REST API
- API documentation
- Test collection

### Phase 2: Mobile App Integration (Week 3-4)

**Tasks:**
1. ✅ Set up API client in mobile app:
   - Create Axios instance with interceptors
   - Implement token storage (localStorage)
   - Implement automatic token refresh
2. ✅ Implement authentication flow:
   - Login screen
   - Token management
   - Logout functionality
3. ✅ Replace mock data with API calls:
   - Queue list → `GET /api/mobile/queue`
   - Queue detail → `GET /api/mobile/queue/{id}`
   - Projects list → `GET /api/mobile/projects`
   - Project detail → `GET /api/mobile/projects/{id}`
   - Presets → `GET /api/mobile/presets`
4. ✅ Implement job actions:
   - Start job → `POST /api/mobile/queue/{id}/start`
   - Pause job → `POST /api/mobile/queue/{id}/pause`
   - Complete job → `POST /api/mobile/queue/{id}/complete`
   - Edit job → `PATCH /api/mobile/queue/{id}`
5. ✅ Implement project actions:
   - Add to queue → `POST /api/mobile/projects/{id}/add-to-queue`
   - Edit project → `PATCH /api/mobile/projects/{id}`
6. ✅ Update Settings drawer:
   - Fetch operator profile → `GET /api/mobile/operators/me`
   - Fetch operator stats → `GET /api/mobile/operators/me/stats`
   - Display today's schedule
7. ✅ Implement polling for real-time updates
8. ✅ Add error handling and loading states
9. ✅ Add toast notifications for actions

**Deliverables:**
- Fully integrated mobile app
- Working authentication
- Real-time data sync

### Phase 3: Testing & Refinement (Week 5)

**Tasks:**
1. ✅ End-to-end testing:
   - Test all user flows
   - Test concurrent desktop + mobile usage
   - Test offline scenarios
2. ✅ Performance testing:
   - API response times
   - Mobile app rendering performance
   - Database query optimization
3. ✅ Security testing:
   - JWT token validation
   - Authorization checks
   - SQL injection prevention
4. ✅ User acceptance testing:
   - Operator feedback
   - UI/UX improvements
5. ✅ Bug fixes and refinements

**Deliverables:**
- Test reports
- Bug fixes
- Performance optimizations

### Phase 4: Deployment & Training (Week 6)

**Tasks:**
1. ✅ Deploy backend API:
   - Configure production environment
   - Set up HTTPS/SSL
   - Configure CORS for production domain
2. ✅ Deploy mobile app:
   - Build production bundle
   - Deploy to web server or PWA hosting
   - Configure service workers for offline support
3. ✅ Create user documentation:
   - Mobile app user guide
   - Operator training materials
   - Troubleshooting guide
4. ✅ Conduct operator training sessions
5. ✅ Monitor initial usage and gather feedback

**Deliverables:**
- Production deployment
- User documentation
- Training completion

---

## 8. Technical Implementation Details

### 8.1 Backend: Mobile API Blueprint

**File:** `app/routes/mobile_api.py`

```python
"""
Mobile API Blueprint for Laser OS
Provides REST API endpoints for mobile application integration
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from functools import wraps
import jwt
from datetime import datetime, timedelta
from app import db
from app.models import (
    User, Operator, Project, QueueItem, LaserRun,
    MachineSettingsPreset, DesignFile, ProjectProduct
)

bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# JWT Configuration
JWT_SECRET_KEY = 'your-secret-key-change-in-production'  # Use app.config['SECRET_KEY']
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


def generate_tokens(operator_id, operator_name, role='operator'):
    """Generate access and refresh JWT tokens."""
    now = datetime.utcnow()

    access_payload = {
        'operator_id': operator_id,
        'operator_name': operator_name,
        'role': role,
        'type': 'access',
        'exp': now + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': now
    }

    refresh_payload = {
        'operator_id': operator_id,
        'type': 'refresh',
        'exp': now + JWT_REFRESH_TOKEN_EXPIRES,
        'iat': now
    }

    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return access_token, refresh_token


def token_required(f):
    """Decorator to require valid JWT token for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401

        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            # Verify token type
            if payload.get('type') != 'access':
                return jsonify({'success': False, 'error': 'Invalid token type'}), 401

            # Attach operator info to request
            request.operator_id = payload['operator_id']
            request.operator_name = payload['operator_name']
            request.operator_role = payload.get('role', 'operator')

        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated


# Authentication Endpoints

@bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate operator and return JWT tokens."""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400

    # Find user
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'success': False, 'error': 'Account is inactive'}), 401

    # Check if user has operator role
    if not user.has_role('operator') and not user.has_role('admin'):
        return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

    # Find associated operator record
    operator = Operator.query.filter_by(email=user.email).first()

    if not operator:
        return jsonify({'success': False, 'error': 'No operator profile found'}), 404

    # Generate tokens
    access_token, refresh_token = generate_tokens(
        operator.id,
        operator.name,
        user.get_primary_role().name if user.get_primary_role() else 'operator'
    )

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds()),
        'operator': {
            'id': operator.id,
            'name': operator.name,
            'employee_id': operator.employee_id,
            'email': operator.email,
            'role': user.get_primary_role().name if user.get_primary_role() else 'operator'
        }
    }), 200


@bp.route('/auth/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token."""
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'success': False, 'error': 'Refresh token required'}), 400

    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get('type') != 'refresh':
            return jsonify({'success': False, 'error': 'Invalid token type'}), 401

        # Get operator
        operator_id = payload['operator_id']
        operator = Operator.query.get(operator_id)

        if not operator:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404

        # Generate new access token
        access_token, _ = generate_tokens(operator.id, operator.name)

        return jsonify({
            'success': True,
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'error': 'Invalid refresh token'}), 401


# Queue Endpoints

@bp.route('/queue', methods=['GET'])
@token_required
def get_queue():
    """Get all queue items with optional filtering."""
    status_filter = request.args.get('status', 'active')
    limit = request.args.get('limit', 50, type=int)

    # Build query
    query = QueueItem.query.join(Project)

    if status_filter == 'active':
        query = query.filter(QueueItem.status.in_([QueueItem.STATUS_QUEUED, QueueItem.STATUS_IN_PROGRESS]))
    elif status_filter != 'all':
        query = query.filter_by(status=status_filter)

    # Order by queue position
    queue_items = query.order_by(QueueItem.queue_position).limit(limit).all()

    # Get statistics
    stats = {
        'total_queued': QueueItem.query.filter_by(status=QueueItem.STATUS_QUEUED).count(),
        'total_in_progress': QueueItem.query.filter_by(status=QueueItem.STATUS_IN_PROGRESS).count(),
        'total_completed': QueueItem.query.filter_by(status=QueueItem.STATUS_COMPLETED).count(),
    }
    stats['total_active'] = stats['total_queued'] + stats['total_in_progress']

    # Format response
    items = []
    for qi in queue_items:
        project = qi.project

        # Get parts from project_products
        parts = [
            {'name': pp.product.name, 'quantity': pp.quantity}
            for pp in project.project_products
        ]

        # Get DXF files
        dxf_files = [
            {'id': df.id, 'filename': df.original_filename}
            for df in project.design_files
        ]

        # Get preset if laser run exists
        preset_name = None
        preset_id = None
        if qi.laser_runs:
            latest_run = qi.laser_runs[-1]
            if latest_run.preset:
                preset_name = latest_run.preset.preset_name
                preset_id = latest_run.preset.id

        items.append({
            'id': qi.id,
            'project_id': project.id,
            'project_code': project.project_code,
            'project_name': project.name,
            'queue_position': qi.queue_position,
            'status': qi.status.lower().replace(' ', '_'),
            'priority': qi.priority.lower(),
            'scheduled_date': qi.scheduled_date.isoformat() if qi.scheduled_date else None,
            'estimated_cut_time': qi.estimated_cut_time or project.estimated_cut_time,
            'material_type': project.material_type,
            'material_thickness': float(project.material_thickness) if project.material_thickness else None,
            'raw_plate_count': project.material_quantity_sheets,
            'drawing_time': project.drawing_creation_time,
            'preset_name': preset_name,
            'preset_id': preset_id,
            'parts': parts,
            'dxf_files': dxf_files,
            'added_at': qi.added_at.isoformat() if qi.added_at else None,
            'started_at': qi.started_at.isoformat() if qi.started_at else None,
            'completed_at': qi.completed_at.isoformat() if qi.completed_at else None
        })

    return jsonify({
        'success': True,
        'queue_items': items,
        'stats': stats
    }), 200
```

### 8.2 Frontend: API Client Setup

**File:** `laser-sync-flow-main/src/lib/apiClient.ts`

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/mobile';

// Token storage keys
const ACCESS_TOKEN_KEY = 'laser_os_access_token';
const REFRESH_TOKEN_KEY = 'laser_os_refresh_token';
const OPERATOR_KEY = 'laser_os_operator';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // If 401 and not already retrying, attempt token refresh
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

        if (!refreshToken) {
          // No refresh token, redirect to login
          logout();
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Attempt to refresh token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;

        // Store new access token
        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);

      } catch (refreshError) {
        // Refresh failed, logout user
        logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication functions
export const login = async (username: string, password: string) => {
  const response = await apiClient.post('/auth/login', { username, password });
  const { access_token, refresh_token, operator } = response.data;

  // Store tokens and operator info
  localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
  localStorage.setItem(OPERATOR_KEY, JSON.stringify(operator));

  return response.data;
};

export const logout = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(OPERATOR_KEY);
};

export const getOperator = () => {
  const operatorStr = localStorage.getItem(OPERATOR_KEY);
  return operatorStr ? JSON.parse(operatorStr) : null;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem(ACCESS_TOKEN_KEY);
};

// Queue API functions
export const getQueue = async (status = 'active') => {
  const response = await apiClient.get('/queue', { params: { status } });
  return response.data;
};

export const getQueueItem = async (id: number) => {
  const response = await apiClient.get(`/queue/${id}`);
  return response.data;
};

export const startJob = async (id: number, data: { operator_id: number; preset_id: number; notes?: string }) => {
  const response = await apiClient.post(`/queue/${id}/start`, data);
  return response.data;
};

export const pauseJob = async (id: number, reason: string) => {
  const response = await apiClient.post(`/queue/${id}/pause`, { reason });
  return response.data;
};

export const completeJob = async (id: number, data: {
  operator_id: number;
  preset_id: number;
  actual_cut_time: number;
  sheet_count: number;
  parts_produced: number;
  notes?: string;
}) => {
  const response = await apiClient.post(`/queue/${id}/complete`, data);
  return response.data;
};

export const updateQueueItem = async (id: number, data: Partial<{
  priority: string;
  scheduled_date: string;
  estimated_cut_time: number;
  notes: string;
}>) => {
  const response = await apiClient.patch(`/queue/${id}`, data);
  return response.data;
};

// Project API functions
export const getProjects = async () => {
  const response = await apiClient.get('/projects');
  return response.data;
};

export const getProject = async (id: number) => {
  const response = await apiClient.get(`/projects/${id}`);
  return response.data;
};

export const addProjectToQueue = async (id: number, data: {
  priority: string;
  scheduled_date: string;
  estimated_cut_time?: number;
  notes?: string;
}) => {
  const response = await apiClient.post(`/projects/${id}/add-to-queue`, data);
  return response.data;
};

export const updateProject = async (id: number, data: Partial<{
  material_type: string;
  material_thickness: number;
  raw_plate_count: number;
  estimated_cut_time: number;
  preset_id: number;
  notes: string;
}>) => {
  const response = await apiClient.patch(`/projects/${id}`, data);
  return response.data;
};

// Preset API functions
export const getPresets = async (materialType?: string, thickness?: number) => {
  const response = await apiClient.get('/presets', {
    params: { material_type: materialType, thickness }
  });
  return response.data;
};

// Operator API functions
export const getOperatorProfile = async () => {
  const response = await apiClient.get('/operators/me');
  return response.data;
};

export const getOperatorStats = async () => {
  const response = await apiClient.get('/operators/me/stats');
  return response.data;
};

export default apiClient;
```

### 8.3 Mobile App: Authentication Flow

**File:** `laser-sync-flow-main/src/pages/Login.tsx`

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { login } from '@/lib/apiClient';
import { Loader2 } from 'lucide-react';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !password) {
      toast({
        title: 'Error',
        description: 'Please enter username and password',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    try {
      const response = await login(username, password);

      toast({
        title: 'Login Successful',
        description: `Welcome back, ${response.operator.name}!`,
      });

      navigate('/');
    } catch (error: any) {
      toast({
        title: 'Login Failed',
        description: error.response?.data?.error || 'Invalid credentials',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Laser OS Mobile</CardTitle>
          <CardDescription className="text-center">
            Sign in to access the cutting queue
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                autoComplete="username"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                autoComplete="current-password"
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
```

---

## 9. Security Considerations

### 9.1 Authentication & Authorization

**Implemented Security Measures:**

1. **Password Hashing:** User passwords stored with bcrypt (via Werkzeug)
2. **JWT Tokens:** Stateless authentication with expiration
3. **Token Refresh:** Short-lived access tokens (1 hour) with long-lived refresh tokens (7 days)
4. **Role-Based Access:** Only users with 'operator' or 'admin' roles can access mobile API
5. **HTTPS Required:** All API communication must use HTTPS in production

**Additional Recommendations:**

1. **Rate Limiting:** Implement rate limiting on login endpoint to prevent brute force attacks
   ```python
   from flask_limiter import Limiter

   limiter = Limiter(app, key_func=lambda: request.remote_addr)

   @bp.route('/auth/login', methods=['POST'])
   @limiter.limit("5 per minute")
   def login():
       # ...
   ```

2. **Token Blacklist:** Implement token blacklist for logout (store revoked tokens in Redis)
3. **IP Whitelisting:** Restrict API access to known IP ranges (optional for internal networks)
4. **Audit Logging:** Log all authentication attempts and critical actions

### 9.2 Data Validation

**Input Validation:**
- Validate all request data using schemas (e.g., Marshmallow, Pydantic)
- Sanitize user inputs to prevent SQL injection
- Validate file uploads (type, size, content)

**Example:**
```python
from marshmallow import Schema, fields, validate

class StartJobSchema(Schema):
    operator_id = fields.Int(required=True)
    preset_id = fields.Int(required=True)
    notes = fields.Str(validate=validate.Length(max=500))

@bp.route('/queue/<int:id>/start', methods=['POST'])
@token_required
def start_job(id):
    schema = StartJobSchema()
    errors = schema.validate(request.json)

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Proceed with validated data
    # ...
```

### 9.3 CORS Configuration

**Production CORS Setup:**
```python
from flask_cors import CORS

# In app/__init__.py
CORS(app, resources={
    r"/api/mobile/*": {
        "origins": ["https://mobile.laseros.com"],  # Production mobile app domain
        "methods": ["GET", "POST", "PATCH", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,  # JWT doesn't need credentials
        "max_age": 3600
    }
})
```

---

## 10. Potential Challenges & Solutions

### 10.1 Data Consistency

**Challenge:** Desktop and mobile users modifying the same data simultaneously.

**Solutions:**
1. **Optimistic Locking:** Include `updated_at` timestamp in PATCH requests
2. **Conflict Detection:** Return 409 Conflict if data was modified
3. **User Notification:** Prompt user to refresh and retry
4. **Activity Logging:** Track all changes for audit trail

### 10.2 Real-Time Updates

**Challenge:** Mobile app needs to reflect desktop changes quickly.

**Solutions:**
1. **Short-term:** Polling every 30 seconds (acceptable for MVP)
2. **Long-term:** WebSocket integration for push notifications
3. **Hybrid:** Polling + manual refresh button
4. **Optimization:** Use HTTP `If-Modified-Since` headers to reduce bandwidth

### 10.3 Offline Functionality

**Challenge:** Operators may work in areas with poor connectivity.

**Solutions:**
1. **Service Workers:** Cache API responses for offline viewing
2. **IndexedDB:** Store pending actions locally
3. **Background Sync:** Sync queued actions when connection restored
4. **Conflict Resolution:** Handle conflicts when syncing offline changes

### 10.4 Performance

**Challenge:** Large datasets may slow down mobile app.

**Solutions:**
1. **Pagination:** Limit API responses (default 50 items)
2. **Lazy Loading:** Load details only when needed
3. **Caching:** Cache frequently accessed data (presets, operator profile)
4. **Database Indexing:** Ensure proper indexes on frequently queried fields
5. **Query Optimization:** Use SQLAlchemy `joinedload` to reduce N+1 queries

### 10.5 File Access

**Challenge:** Mobile app needs to access DXF files stored on server.

**Solutions:**
1. **File Download API:** Add endpoint to download design files
   ```python
   @bp.route('/files/<int:file_id>/download', methods=['GET'])
   @token_required
   def download_file(file_id):
       design_file = DesignFile.query.get_or_404(file_id)
       return send_file(design_file.file_path, as_attachment=True)
   ```

2. **File Previews:** Generate thumbnails/previews for DXF files (future enhancement)
3. **File Metadata:** Return file info (name, size, type) without downloading

---

## 11. Testing Strategy

### 11.1 Backend API Testing

**Unit Tests:**
```python
# tests/test_mobile_api.py
import pytest
from app import create_app, db
from app.models import User, Operator

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_login_success(client):
    # Create test user and operator
    user = User(username='testop', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)

    operator = Operator(name='Test Operator', email='test@example.com')
    db.session.add(operator)
    db.session.commit()

    # Test login
    response = client.post('/api/mobile/auth/login', json={
        'username': 'testop',
        'password': 'password123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_invalid_credentials(client):
    response = client.post('/api/mobile/auth/login', json={
        'username': 'invalid',
        'password': 'wrong'
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] == False

def test_get_queue_unauthorized(client):
    response = client.get('/api/mobile/queue')
    assert response.status_code == 401

def test_get_queue_authorized(client):
    # Login and get token
    # ... (setup code)

    response = client.get('/api/mobile/queue', headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'queue_items' in data
    assert 'stats' in data
```

**Integration Tests:**
- Test complete workflows (login → view queue → start job → complete job)
- Test concurrent access scenarios
- Test error handling and edge cases

### 11.2 Frontend Testing

**Component Tests:**
```typescript
// tests/JobCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { JobCard } from '@/components/JobCard';

const mockJob = {
  id: '1',
  projectName: 'Test Project',
  status: 'pending',
  // ... other fields
};

test('renders job card with correct data', () => {
  render(<JobCard job={mockJob} onView={() => {}} onStart={() => {}} />);

  expect(screen.getByText('Test Project')).toBeInTheDocument();
  expect(screen.getByText('Pending')).toBeInTheDocument();
});

test('calls onStart when start button clicked', () => {
  const onStart = jest.fn();
  render(<JobCard job={mockJob} onView={() => {}} onStart={onStart} />);

  fireEvent.click(screen.getByText('Start'));
  expect(onStart).toHaveBeenCalledTimes(1);
});
```

**E2E Tests (Playwright/Cypress):**
```typescript
// e2e/queue-management.spec.ts
import { test, expect } from '@playwright/test';

test('operator can start and complete a job', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('input[name="username"]', 'testop');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Navigate to queue
  await page.click('text=Queue');

  // Start first job
  await page.click('button:has-text("Start")').first();
  await page.click('button:has-text("Confirm")');

  // Verify status changed
  await expect(page.locator('text=Running')).toBeVisible();

  // Complete job
  await page.click('button:has-text("Complete")');
  await page.fill('input[name="actual_cut_time"]', '45');
  await page.click('button:has-text("Confirm")');

  // Verify completion
  await expect(page.locator('text=Completed')).toBeVisible();
});
```

---

## 12. Deployment Guide

### 12.1 Backend Deployment

**Prerequisites:**
- Python 3.9+
- SQLite database
- HTTPS/SSL certificate
- Reverse proxy (Nginx/Apache)

**Steps:**

1. **Install Dependencies:**
   ```bash
   pip install PyJWT flask-cors
   ```

2. **Configure Environment:**
   ```bash
   # .env
   FLASK_ENV=production
   SECRET_KEY=your-production-secret-key-change-this
   JWT_SECRET_KEY=your-jwt-secret-key-change-this
   CORS_ORIGINS=https://mobile.laseros.com
   ```

3. **Register Mobile API Blueprint:**
   ```python
   # app/__init__.py
   from app.routes import mobile_api
   app.register_blueprint(mobile_api.bp)
   ```

4. **Configure CORS:**
   ```python
   # app/__init__.py
   from flask_cors import CORS

   CORS(app, resources={
       r"/api/mobile/*": {
           "origins": app.config.get('CORS_ORIGINS', '*').split(','),
           "methods": ["GET", "POST", "PATCH", "DELETE"],
           "allow_headers": ["Content-Type", "Authorization"]
       }
   })
   ```

5. **Configure Nginx:**
   ```nginx
   server {
       listen 443 ssl;
       server_name api.laseros.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location /api/mobile {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### 12.2 Mobile App Deployment

**Build for Production:**
```bash
cd laser-sync-flow-main
npm run build
```

**Configure API URL:**
```bash
# .env.production
VITE_API_BASE_URL=https://api.laseros.com/api/mobile
```

**Deploy Options:**

1. **Static Hosting (Netlify/Vercel):**
   - Upload `dist/` folder
   - Configure redirects for SPA routing

2. **Self-Hosted (Nginx):**
   ```nginx
   server {
       listen 443 ssl;
       server_name mobile.laseros.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       root /var/www/laser-mobile/dist;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

3. **PWA Configuration:**
   - Add service worker for offline support
   - Configure manifest.json for installability
   - Add app icons

---

## 13. Future Enhancements

### 13.1 Phase 2 Features

1. **Real-Time Notifications:**
   - WebSocket integration for instant updates
   - Push notifications for job assignments
   - Desktop notifications for mobile actions

2. **Advanced Offline Support:**
   - Full offline mode with local database (IndexedDB)
   - Conflict resolution UI
   - Sync status indicators

3. **File Management:**
   - DXF file preview in mobile app
   - File upload from mobile
   - Annotation/markup tools

4. **Reporting:**
   - Operator performance dashboards
   - Daily/weekly production reports
   - Export to PDF/Excel

5. **Barcode/QR Code Scanning:**
   - Scan project codes to quickly access jobs
   - Scan material sheets for inventory tracking
   - Generate QR codes for projects

### 13.2 Phase 3 Features

1. **Voice Commands:**
   - Start/pause/complete jobs via voice
   - Hands-free operation for operators

2. **Machine Integration:**
   - Direct communication with laser cutter
   - Real-time machine status
   - Automatic job start/stop

3. **Advanced Analytics:**
   - Machine learning for cut time prediction
   - Material optimization suggestions
   - Predictive maintenance alerts

4. **Multi-Language Support:**
   - Internationalization (i18n)
   - Support for multiple languages

---

## 14. Conclusion

This integration plan provides a comprehensive roadmap for connecting the Laser Sync Flow mobile application with the main Laser OS desktop application. The recommended approach uses:

- **REST API** with JWT authentication for secure, stateless communication
- **Polling** for real-time updates (MVP), with WebSocket upgrade path
- **Progressive Web App** architecture for offline support
- **Phased implementation** to minimize risk and ensure quality

### Key Success Factors

1. **Security First:** Implement robust authentication and authorization
2. **Data Integrity:** Ensure consistency between mobile and desktop
3. **User Experience:** Provide fast, responsive mobile interface
4. **Offline Support:** Enable operators to work without constant connectivity
5. **Testing:** Comprehensive testing at all levels
6. **Documentation:** Clear API docs and user guides
7. **Training:** Proper operator training on mobile app usage

### Next Steps

1. **Review and Approve:** Stakeholder review of integration plan
2. **Environment Setup:** Prepare development/staging environments
3. **Phase 1 Kickoff:** Begin backend API development
4. **Iterative Development:** Build, test, and refine in phases
5. **Pilot Program:** Test with small group of operators
6. **Full Rollout:** Deploy to all operators after successful pilot

---

**Document End**


