# Authentication & Authorization System Diagrams
## Visual Reference for Laser OS Tier 1

**Related Documents:**
- `AUTHENTICATION_AUTHORIZATION_DESIGN.md` - Complete design document
- `AUTH_IMPLEMENTATION_CHECKLIST.md` - Implementation checklist
- `AUTH_CODE_SNIPPETS.md` - Code examples

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Authentication Flow](#authentication-flow)
3. [Authorization Flow](#authorization-flow)
4. [Database Schema](#database-schema)
5. [Network Topology](#network-topology)
6. [User Role Hierarchy](#user-role-hierarchy)

---

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Web Browser (Client)                                          │ │
│  │  - HTML/CSS/JavaScript                                         │ │
│  │  - Forms with CSRF tokens                                      │ │
│  │  - Session cookies                                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Flask Application                                             │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Flask-Login (Session Management)                        │ │ │
│  │  │  - login_manager                                         │ │ │
│  │  │  - user_loader                                           │ │ │
│  │  │  - session handling                                      │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Flask-WTF (Form Handling & CSRF)                        │ │ │
│  │  │  - Form validation                                       │ │ │
│  │  │  - CSRF protection                                       │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Custom Decorators (Authorization)                       │ │ │
│  │  │  - @role_required                                        │ │ │
│  │  │  - @permission_required                                  │ │ │
│  │  │  - @admin_required                                       │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Routes (Blueprints)                                     │ │ │
│  │  │  - auth (login/logout)                                   │ │ │
│  │  │  - admin (user management)                               │ │ │
│  │  │  - clients, projects, products, queue, etc.              │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA ACCESS LAYER                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  SQLAlchemy ORM                                                │ │
│  │  - User model                                                  │ │
│  │  - Role model                                                  │ │
│  │  - UserRole model                                              │ │
│  │  - LoginHistory model                                          │ │
│  │  - Business models (Client, Project, etc.)                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  SQLite Database (laser_os.db)                                 │ │
│  │  - users                                                       │ │
│  │  - roles                                                       │ │
│  │  - user_roles                                                  │ │
│  │  - login_history                                               │ │
│  │  - clients, projects, products, queue, etc.                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow

### Login Process

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│ User visits         │
│ /auth/login         │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Display login form  │
│ with CSRF token     │
└────┬────────────────┘
     │
     │ User enters credentials
     ▼
┌─────────────────────┐
│ POST to /auth/login │
│ - username          │
│ - password          │
│ - remember_me       │
│ - csrf_token        │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Validate CSRF token │
└────┬────────────────┘
     │
     ├─── Invalid ────────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────┐
│ Valid?      │    │ Return 400   │
└────┬────────┘    │ Bad Request  │
     │             └──────────────┘
     │ Yes
     ▼
┌─────────────────────┐
│ Query User by       │
│ username            │
└────┬────────────────┘
     │
     ├─── Not Found ──────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────────┐
│ User exists?│    │ Log failed login │
└────┬────────┘    │ Flash error      │
     │             │ Redirect /login  │
     │ Yes         └──────────────────┘
     ▼
┌─────────────────────┐
│ Check if account    │
│ is locked           │
│ (locked_until >now) │
└────┬────────────────┘
     │
     ├─── Locked ─────────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────────┐
│ Not locked? │    │ Flash locked msg │
└────┬────────┘    │ Redirect /login  │
     │             └──────────────────┘
     │ Yes
     ▼
┌─────────────────────┐
│ Check if account    │
│ is active           │
│ (is_active=True)    │
└────┬────────────────┘
     │
     ├─── Inactive ───────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────────┐
│ Active?     │    │ Flash disabled   │
└────┬────────┘    │ Redirect /login  │
     │             └──────────────────┘
     │ Yes
     ▼
┌─────────────────────┐
│ Verify password     │
│ check_password_hash │
└────┬────────────────┘
     │
     ├─── Invalid ────────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────────────┐
│ Valid?      │    │ Increment failed     │
└────┬────────┘    │ attempts counter     │
     │             │ If >= 5: lock account│
     │ Yes         │ Log failed login     │
     ▼             │ Flash error          │
┌─────────────────────┐ │ Redirect /login      │
│ Reset failed        │ └──────────────────────┘
│ attempts = 0        │
│ Update last_login   │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Create session      │
│ login_user(user,    │
│   remember=True)    │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Log successful login│
│ - IP address        │
│ - User agent        │
│ - Session ID        │
│ - Timestamp         │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Flash success msg   │
│ Redirect to next    │
│ or dashboard        │
└────┬────────────────┘
     │
     ▼
┌──────────┐
│   END    │
└──────────┘
```

### Logout Process

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│ User clicks logout  │
│ GET /auth/logout    │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Check if user is    │
│ authenticated       │
└────┬────────────────┘
     │
     ├─── Not Auth ───────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────┐
│ Authenticated│   │ Redirect to  │
└────┬────────┘    │ /auth/login  │
     │             └──────────────┘
     │ Yes
     ▼
┌─────────────────────┐
│ Update logout_time  │
│ in login_history    │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Clear session       │
│ logout_user()       │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Flash info message  │
│ "You have been      │
│  logged out"        │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Redirect to         │
│ /auth/login         │
└────┬────────────────┘
     │
     ▼
┌──────────┐
│   END    │
└──────────┘
```

---

## Authorization Flow

### Route Access Check

```
┌──────────┐
│  START   │
│ User requests route │
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│ Route has           │
│ @login_required?    │
└────┬────────────────┘
     │
     ├─── Yes ────────────┐
     │                    │
     ▼                    ▼
┌─────────────┐    ┌──────────────────┐
│ No decorator│    │ Check if user is │
│ Allow access│    │ authenticated    │
└────┬────────┘    └────┬─────────────┘
     │                  │
     │                  ├─── Not Auth ──┐
     │                  │                │
     │                  ▼                ▼
     │            ┌─────────────┐  ┌─────────────┐
     │            │ Authenticated│  │ Redirect to │
     │            └────┬────────┘  │ /auth/login │
     │                 │           └─────────────┘
     │                 │ Yes
     │                 ▼
     │            ┌─────────────────────┐
     │            │ Route has           │
     │            │ @role_required?     │
     │            └────┬────────────────┘
     │                 │
     │                 ├─── Yes ────────┐
     │                 │                │
     │                 ▼                ▼
     │            ┌─────────────┐  ┌──────────────────┐
     │            │ No role     │  │ Check if user    │
     │            │ required    │  │ has required role│
     │            │ Allow access│  └────┬─────────────┘
     │            └────┬────────┘       │
     │                 │                ├─── No ────────┐
     │                 │                │               │
     │                 │                ▼               ▼
     │                 │          ┌─────────────┐ ┌─────────────┐
     │                 │          │ Has role?   │ │ Flash error │
     │                 │          └────┬────────┘ │ Return 403  │
     │                 │               │          └─────────────┘
     │                 │               │ Yes
     │                 │               ▼
     │                 │          ┌─────────────────────┐
     │                 │          │ Route has           │
     │                 │          │ @permission_required│
     │                 │          └────┬────────────────┘
     │                 │               │
     │                 │               ├─── Yes ────────┐
     │                 │               │                │
     │                 │               ▼                ▼
     │                 │          ┌─────────────┐  ┌──────────────────┐
     │                 │          │ No perm     │  │ Check if user    │
     │                 │          │ required    │  │ has permission   │
     │                 │          │ Allow access│  └────┬─────────────┘
     │                 │          └────┬────────┘       │
     │                 │               │                ├─── No ────┐
     │                 │               │                │           │
     │                 │               │                ▼           ▼
     │                 │               │          ┌─────────┐ ┌─────────┐
     │                 │               │          │Has perm?│ │Flash err│
     │                 │               │          └────┬────┘ │Ret 403  │
     │                 │               │               │      └─────────┘
     │                 │               │               │ Yes
     │                 │               │               ▼
     └─────────────────┴───────────────┴──────────────────┐
                                                           │
                                                           ▼
                                                    ┌──────────────┐
                                                    │ Execute route│
                                                    │ function     │
                                                    └──────┬───────┘
                                                           │
                                                           ▼
                                                    ┌──────────────┐
                                                    │ Return       │
                                                    │ response     │
                                                    └──────┬───────┘
                                                           │
                                                           ▼
                                                    ┌──────────────┐
                                                    │     END      │
                                                    └──────────────┘
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                            users                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                                   │
│    │ username          VARCHAR(80)    UNIQUE, NOT NULL           │
│    │ email             VARCHAR(120)   UNIQUE, NOT NULL           │
│    │ password_hash     VARCHAR(255)   NOT NULL                   │
│    │ full_name         VARCHAR(200)                              │
│    │ is_active         BOOLEAN        DEFAULT TRUE               │
│    │ is_superuser      BOOLEAN        DEFAULT FALSE              │
│    │ created_at        DATETIME       DEFAULT NOW                │
│    │ updated_at        DATETIME       DEFAULT NOW                │
│    │ last_login        DATETIME                                  │
│    │ failed_login_attempts INTEGER    DEFAULT 0                  │
│    │ locked_until      DATETIME                                  │
└────┬────────────────────────────────────────────────────────────┘
     │
     │ 1:N
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         login_history                            │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                                   │
│ FK │ user_id           INTEGER        NOT NULL → users.id        │
│    │ login_time        DATETIME       DEFAULT NOW                │
│    │ logout_time       DATETIME                                  │
│    │ ip_address        VARCHAR(45)                               │
│    │ user_agent        TEXT                                      │
│    │ success           BOOLEAN        DEFAULT TRUE               │
│    │ failure_reason    VARCHAR(200)                              │
│    │ session_id        VARCHAR(255)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                            users                                 │
└────┬────────────────────────────────────────────────────────────┘
     │
     │ N:M (through user_roles)
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         user_roles                               │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                                   │
│ FK │ user_id           INTEGER        NOT NULL → users.id        │
│ FK │ role_id           INTEGER        NOT NULL → roles.id        │
│    │ assigned_at       DATETIME       DEFAULT NOW                │
│ FK │ assigned_by       INTEGER        → users.id                 │
│    │ UNIQUE(user_id, role_id)                                    │
└────┬────────────────────────────────────────────────────────────┘
     │
     │ N:1
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                            roles                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                                   │
│    │ name              VARCHAR(50)    UNIQUE, NOT NULL           │
│    │ display_name      VARCHAR(100)   NOT NULL                   │
│    │ description       TEXT                                      │
│    │ permissions       TEXT           (JSON)                     │
│    │ created_at        DATETIME       DEFAULT NOW                │
│    │ updated_at        DATETIME       DEFAULT NOW                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Network Topology

### Local Network + VPN Access

```
                        INTERNET
                            │
                            │
                ┌───────────┴───────────┐
                │                       │
                │  VPN Server           │
                │  (WireGuard/OpenVPN)  │
                │  Public IP: X.X.X.X   │
                │  VPN Network:         │
                │  10.0.0.0/24          │
                └───────────┬───────────┘
                            │
                            │ VPN Tunnel (Encrypted)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Remote  │         │ Remote  │        │ Remote  │
   │ User 1  │         │ User 2  │        │ User 3  │
   │ 10.0.0.2│         │ 10.0.0.3│        │ 10.0.0.4│
   └─────────┘         └─────────┘        └─────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    Office LAN (192.168.1.0/24)                   │
│                                                                  │
│  ┌──────────────┐                                                │
│  │ Router/      │                                                │
│  │ Firewall     │                                                │
│  │ 192.168.1.1  │                                                │
│  └──────┬───────┘                                                │
│         │                                                        │
│         │                                                        │
│  ┌──────┴───────────────────────────────────┐                   │
│  │                                           │                   │
│  ▼                                           ▼                   │
│ ┌────────────────────┐              ┌────────────────────┐      │
│ │ Laser OS Server    │              │ Network Switch     │      │
│ │ 192.168.1.100:8080 │              │                    │      │
│ │ - Flask App        │              └────────┬───────────┘      │
│ │ - SQLite DB        │                       │                  │
│ │ - Waitress Server  │                       │                  │
│ └────────────────────┘                       │                  │
│                                               │                  │
│                                    ┌──────────┴──────────┐       │
│                                    │                     │       │
│                                    ▼                     ▼       │
│                              ┌──────────┐         ┌──────────┐  │
│                              │ Office   │         │ Office   │  │
│                              │ PC 1     │         │ PC 2     │  │
│                              │.101      │         │.102      │  │
│                              └──────────┘         └──────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## User Role Hierarchy

### Role Pyramid

```
                    ┌─────────────────┐
                    │     ADMIN       │
                    │   (Superuser)   │
                    │                 │
                    │ • All access    │
                    │ • User mgmt     │
                    │ • Settings      │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │    MANAGER     │       │    MANAGER     │
        │                │       │                │
        │ • Business ops │       │ • Business ops │
        │ • Create/Edit  │       │ • Create/Edit  │
        │ • Delete       │       │ • Delete       │
        │ • View logs    │       │ • View logs    │
        └───────┬────────┘       └───────┬────────┘
                │                        │
                └────────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │    OPERATOR     │
                    │                 │
                    │ • Production    │
                    │ • Edit data     │
                    │ • Manage queue  │
                    │ • Upload files  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     VIEWER      │
                    │                 │
                    │ • Read-only     │
                    │ • View all data │
                    │ • No edits      │
                    └─────────────────┘
```

### Permission Inheritance

```
Admin Permissions:
├── view_all
├── create_all
├── edit_all
├── delete_all
├── manage_users
├── manage_settings
└── view_logs

Manager Permissions:
├── view_all
├── create_business
├── edit_business
├── delete_business
└── view_logs

Operator Permissions:
├── view_all
├── edit_production
├── manage_queue
└── upload_files

Viewer Permissions:
└── view_all
```

---

**End of Diagrams**

For complete implementation details, refer to `AUTHENTICATION_AUTHORIZATION_DESIGN.md`.

