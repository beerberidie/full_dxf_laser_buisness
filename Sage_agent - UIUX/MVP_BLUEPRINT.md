# Sage Business Cloud Accounting Integration - MVP Blueprint

**Version:** 1.0  
**Date:** 2025-10-10  
**Target Region:** South Africa  
**API Version:** Sage Business Cloud Accounting v3.1

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Complete Architecture Overview](#complete-architecture-overview)
3. [Current State Analysis](#current-state-analysis)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Database Schema Enhancements](#database-schema-enhancements)
6. [API Endpoint Specifications](#api-endpoint-specifications)
7. [Custom UI Design Specifications](#custom-ui-design-specifications)
8. [Configuration Guide](#configuration-guide)
9. [Security Considerations](#security-considerations)
10. [Deployment Strategy](#deployment-strategy)
11. [Testing Strategy](#testing-strategy)
12. [Appendices](#appendices)

---

## Executive Summary

### Project Overview

This MVP Blueprint provides a comprehensive implementation guide for building a production-ready Sage Business Cloud Accounting integration for South African businesses. The system enables:

- **OAuth 2.0 Authentication** with Sage Business Cloud Accounting
- **Multi-business Support** with X-Business context management
- **Sales Invoice Management** (create, read, release)
- **Contact Management** (customers and suppliers)
- **Audit Logging** for compliance and traceability
- **Incremental Sync** for efficient data synchronization
- **South African Localization** (ZAR currency, 15% VAT)

### Technology Stack

**Backend:**
- FastAPI (Python 3.10+)
- SQLModel + SQLite (upgradeable to PostgreSQL)
- httpx for async HTTP requests
- Pydantic for data validation

**Frontend:**
- React 18
- Vite for build tooling
- Native fetch API for HTTP requests

**Infrastructure:**
- OAuth 2.0 with token refresh
- SQLite database (development)
- CORS-enabled API

### Key Deliverables

1. ✅ Corrected OAuth 2.0 implementation
2. ✅ X-Business header management
3. ✅ Token refresh mechanism
4. ✅ South African localization
5. ✅ Audit logging system
6. ✅ Incremental sync mechanism
7. ✅ Enhanced UI components
8. ✅ Production deployment guide

---

## Complete Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  OAuth Flow  │  │  Business    │  │  Invoice     │          │
│  │  Component   │  │  Selector    │  │  Management  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                    HTTP/JSON (Port 8081)                         │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Vite Proxy     │
                    │  /api → :8777   │
                    │  /auth → :8777  │
                    └────────┬────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Layer                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │   │
│  │  │  OAuth   │  │  Sage    │  │ Settings │  │  Audit  │  │   │
│  │  │  Router  │  │  Router  │  │  Router  │  │  Router │  │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  │   │
│  └───────┼─────────────┼─────────────┼─────────────┼────────┘   │
│          │             │             │             │            │
│  ┌───────▼─────────────▼─────────────▼─────────────▼────────┐   │
│  │              Business Logic Layer                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ SageV31Client│  │ TokenManager │  │ AuditService │   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │   │
│  └─────────┼──────────────────┼──────────────────┼───────────┘   │
│            │                  │                  │               │
│  ┌─────────▼──────────────────▼──────────────────▼───────────┐   │
│  │                  Data Access Layer                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ Tenant   │  │Connection│  │ Setting  │  │ AuditLog │  │   │
│  │  │  Model   │  │  Model   │  │  Model   │  │  Model   │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  └────────────────────────────┬───────────────────────────────┘   │
│                               │                                   │
│                      ┌────────▼────────┐                          │
│                      │  SQLite/Postgres│                          │
│                      │    Database     │                          │
│                      └─────────────────┘                          │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                      HTTPS (OAuth 2.0)
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│              Sage Business Cloud Accounting API                  │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ OAuth Server     │  │ API Gateway      │  │ Business Data  │ │
│  │ oauth.accounting │  │ api.accounting   │  │ (Multi-tenant) │ │
│  │ .sage.com        │  │ .sage.com/v3.1   │  │                │ │
│  └──────────────────┘  └──────────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagrams

#### 1. OAuth Authentication Flow

```
┌──────┐                ┌──────────┐              ┌──────────┐              ┌──────────┐
│ User │                │ Frontend │              │ Backend  │              │   Sage   │
└──┬───┘                └────┬─────┘              └────┬─────┘              └────┬─────┘
   │                         │                         │                         │
   │ 1. Click "Connect"      │                         │                         │
   ├────────────────────────>│                         │                         │
   │                         │                         │                         │
   │                         │ 2. GET /auth/start      │                         │
   │                         ├────────────────────────>│                         │
   │                         │                         │                         │
   │                         │                         │ 3. Generate state token │
   │                         │                         │ 4. Build authorize URL  │
   │                         │                         │                         │
   │                         │ 5. Redirect to Sage     │                         │
   │                         │<────────────────────────┤                         │
   │                         │                         │                         │
   │ 6. Redirect to Sage OAuth                         │                         │
   ├───────────────────────────────────────────────────┼────────────────────────>│
   │                         │                         │                         │
   │ 7. User authenticates & authorizes                │                         │
   │<────────────────────────────────────────────────────────────────────────────┤
   │                         │                         │                         │
   │ 8. Redirect to callback with code                 │                         │
   ├───────────────────────────────────────────────────>│                         │
   │                         │                         │                         │
   │                         │                         │ 9. POST /token          │
   │                         │                         │    (exchange code)      │
   │                         │                         ├────────────────────────>│
   │                         │                         │                         │
   │                         │                         │ 10. Return tokens       │
   │                         │                         │<────────────────────────┤
   │                         │                         │                         │
   │                         │                         │ 11. GET /businesses     │
   │                         │                         ├────────────────────────>│
   │                         │                         │                         │
   │                         │                         │ 12. Return businesses   │
   │                         │                         │<────────────────────────┤
   │                         │                         │                         │
   │                         │                         │ 13. Store connection    │
   │                         │                         │     + tokens in DB      │
   │                         │                         │                         │
   │                         │ 14. Redirect to         │                         │
   │                         │     business selector   │                         │
   │<────────────────────────┼─────────────────────────┤                         │
   │                         │                         │                         │
```

#### 2. API Request Flow with Token Refresh

```
┌──────────┐              ┌──────────┐              ┌──────────┐              ┌──────────┐
│ Frontend │              │ Backend  │              │ Database │              │   Sage   │
└────┬─────┘              └────┬─────┘              └────┬─────┘              └────┬─────┘
     │                         │                         │                         │
     │ 1. GET /api/sage/       │                         │                         │
     │    sales_invoices       │                         │                         │
     ├────────────────────────>│                         │                         │
     │                         │                         │                         │
     │                         │ 2. Get connection       │                         │
     │                         ├────────────────────────>│                         │
     │                         │                         │                         │
     │                         │ 3. Return connection    │                         │
     │                         │    with access_token    │                         │
     │                         │<────────────────────────┤                         │
     │                         │                         │                         │
     │                         │ 4. Check token expiry   │                         │
     │                         │    (expires_at)         │                         │
     │                         │                         │                         │
     │                         │ 5. If expired:          │                         │
     │                         │    POST /token          │                         │
     │                         │    (refresh_token)      │                         │
     │                         ├─────────────────────────┼────────────────────────>│
     │                         │                         │                         │
     │                         │ 6. New tokens           │                         │
     │                         │<─────────────────────────────────────────────────┤
     │                         │                         │                         │
     │                         │ 7. Update connection    │                         │
     │                         ├────────────────────────>│                         │
     │                         │                         │                         │
     │                         │ 8. GET /v3.1/           │                         │
     │                         │    sales_invoices       │                         │
     │                         │    Headers:             │                         │
     │                         │    - Authorization      │                         │
     │                         │    - X-Business         │                         │
     │                         ├─────────────────────────┼────────────────────────>│
     │                         │                         │                         │
     │                         │ 9. Return invoices      │                         │
     │                         │<─────────────────────────────────────────────────┤
     │                         │                         │                         │
     │ 10. Return JSON         │                         │                         │
     │<────────────────────────┤                         │                         │
     │                         │                         │                         │
```

#### 3. Invoice Creation with Audit Flow

```
┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ User │     │ Frontend │     │ Backend  │     │ Database │     │   Sage   │
└──┬───┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
   │              │                │                │                │
   │ 1. Fill form │                │                │                │
   ├─────────────>│                │                │                │
   │              │                │                │                │
   │ 2. Preview   │                │                │                │
   ├─────────────>│                │                │                │
   │              │                │                │                │
   │              │ 3. POST /api/  │                │                │
   │              │    sage/sales_ │                │                │
   │              │    invoices/   │                │                │
   │              │    preview     │                │                │
   │              ├───────────────>│                │                │
   │              │                │                │                │
   │              │                │ 4. Create      │                │
   │              │                │    audit log   │                │
   │              │                │    (preview)   │                │
   │              │                ├───────────────>│                │
   │              │                │                │                │
   │              │ 5. Return      │                │                │
   │              │    preview     │                │                │
   │              │<───────────────┤                │                │
   │              │                │                │                │
   │ 6. Show      │                │                │                │
   │    preview   │                │                │                │
   │<─────────────┤                │                │                │
   │              │                │                │                │
   │ 7. Confirm   │                │                │                │
   ├─────────────>│                │                │                │
   │              │                │                │                │
   │              │ 8. POST /api/  │                │                │
   │              │    sage/sales_ │                │                │
   │              │    invoices    │                │                │
   │              ├───────────────>│                │                │
   │              │                │                │                │
   │              │                │ 9. Update      │                │
   │              │                │    audit log   │                │
   │              │                │    (confirmed) │                │
   │              │                ├───────────────>│                │
   │              │                │                │                │
   │              │                │ 10. POST /v3.1/│                │
   │              │                │     sales_     │                │
   │              │                │     invoices   │                │
   │              │                ├────────────────┼───────────────>│
   │              │                │                │                │
   │              │                │ 11. Invoice    │                │
   │              │                │     created    │                │
   │              │                │<────────────────────────────────┤
   │              │                │                │                │
   │              │                │ 12. Update     │                │
   │              │                │     audit log  │                │
   │              │                │     (success)  │                │
   │              │                ├───────────────>│                │
   │              │                │                │                │
   │              │ 13. Return     │                │                │
   │              │     invoice    │                │                │
   │              │<───────────────┤                │                │
   │              │                │                │                │
   │ 14. Success  │                │                │                │
   │<─────────────┤                │                │                │
   │              │                │                │                │
```

---

## Current State Analysis

### Existing Implementation

#### ✅ What's Working

1. **Basic FastAPI Setup**
   - CORS middleware configured
   - Router structure in place
   - Health check endpoint
   - SQLModel database integration

2. **Database Models**
   - Tenant, User, Connection models defined
   - Setting model for key-value storage
   - AuditLog model structure
   - SyncCursor model for incremental sync

3. **Frontend Foundation**
   - React + Vite setup
   - Proxy configuration for API calls
   - Basic UI components
   - Settings management UI

4. **API Client Structure**
   - SageV31Client class with async methods
   - Basic endpoint methods (invoices, contacts)
   - Request wrapper with headers

#### ❌ What Needs Fixing

1. **OAuth Implementation**
   - ❌ Incorrect authorization URL: `https://www.sage.com/oauth/authorize`
   - ❌ Incorrect token URL: `https://www.sage.com/oauth/token`
   - ❌ Missing token expiry tracking
   - ❌ No token refresh mechanism
   - ❌ No business selection after OAuth

2. **X-Business Header**
   - ❌ Commented out in `_request` method
   - ❌ No business_id stored in Connection
   - ❌ No UI for business selection

3. **Token Management**
   - ❌ No automatic token refresh on 401
   - ❌ No token expiry calculation
   - ❌ Tokens stored in plaintext (security risk)

4. **South African Localization**
   - ❌ No ZAR currency defaults
   - ❌ No ZA_STANDARD VAT code configuration
   - ❌ Invoice payload incomplete

5. **Audit Logging**
   - ❌ AuditLog model exists but not used
   - ❌ No preview/confirm pattern
   - ❌ No audit trail for operations

6. **Sync Mechanism**
   - ❌ SyncCursor model exists but not used
   - ❌ No incremental sync implementation

---

## Implementation Roadmap

### Phase 1: OAuth 2.0 Correction & Token Management (Priority: CRITICAL)

**Estimated Time:** 2-3 days

#### Task 1.1: Fix OAuth URLs

**File:** `backend/app/oauth.py`

**Changes Required:**

```python
# Line 20: Replace incorrect authorize URL
# OLD:
authorize_url = "https://www.sage.com/oauth/authorize"

# NEW:
authorize_url = "https://www.sageone.com/oauth2/auth/central?filter=apiv3.1"

# Line 34: Replace incorrect token URL
# OLD:
token_url = "https://www.sage.com/oauth/token"

# NEW:
token_url = "https://oauth.accounting.sage.com/token"
```

**Additional Parameters:**

```python
params = {
    "response_type": "code",
    "client_id": s.sage_client_id,
    "redirect_uri": s.sage_redirect_uri,
    "scope": "full_access",
    "state": state,
    "country": "za",  # Pre-select South Africa
    "filter": "apiv3.1",  # Only show v3.1 compatible countries
}
```

#### Task 1.2: Add Token Expiry Tracking

**File:** `backend/app/oauth.py`

**Update callback handler:**

```python
@router.get("/callback")
async def auth_callback(request: Request, code: str, state: str, session=Depends(get_session)):
    s = get_settings()
    token_url = "https://oauth.accounting.sage.com/token"

    # Add required headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": s.sage_redirect_uri,
        "client_id": s.sage_client_id,
        "client_secret": s.sage_client_secret,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(token_url, data=data, headers=headers)
        resp.raise_for_status()
        tok = resp.json()

    # Calculate token expiry
    expires_in = tok.get("expires_in", 300)  # Default 5 minutes
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Fetch available businesses
    async with httpx.AsyncClient(timeout=30) as client:
        businesses_resp = await client.get(
            f"{s.sage_base_url}/businesses",
            headers={"Authorization": f"Bearer {tok['access_token']}"}
        )
        businesses = businesses_resp.json()

    # Store connection WITHOUT business_id (user will select)
    tenant_id = _tenant_id()
    conn = Connection(
        id=f"conn-sbca-{tenant_id}",
        tenant_id=tenant_id,
        provider="sbca",
        access_token=tok.get("access_token"),
        refresh_token=tok.get("refresh_token"),
        expires_at=expires_at,
        status="pending_business_selection",  # New status
    )
    session.add(conn)
    session.commit()

    # Redirect to business selection page with businesses data
    # Store businesses temporarily in session or pass as query param
    return RedirectResponse(f"/select-business?connection_id={conn.id}")
```

#### Task 1.3: Implement Token Refresh Mechanism

**File:** `backend/app/token_manager.py` (NEW FILE)

```python
from datetime import datetime, timedelta
from typing import Optional
import httpx
from .db import Connection, get_session
from .settings import get_settings
from sqlmodel import select

class TokenManager:
    """Manages OAuth token refresh for Sage API"""

    def __init__(self):
        self.settings = get_settings()

    async def refresh_token(self, connection: Connection, session) -> Connection:
        """Refresh access token using refresh token"""

        if not connection.refresh_token:
            raise ValueError("No refresh token available")

        token_url = "https://oauth.accounting.sage.com/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": connection.refresh_token,
            "client_id": self.settings.sage_client_id,
            "client_secret": self.settings.sage_client_secret,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(token_url, data=data, headers=headers)
            resp.raise_for_status()
            tok = resp.json()

        # Update connection with new tokens
        connection.access_token = tok.get("access_token")
        connection.refresh_token = tok.get("refresh_token")  # New refresh token!

        expires_in = tok.get("expires_in", 300)
        connection.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        session.add(connection)
        session.commit()
        session.refresh(connection)

        return connection

    def is_token_expired(self, connection: Connection) -> bool:
        """Check if access token is expired or will expire soon"""
        if not connection.expires_at:
            return True

        # Refresh if token expires in less than 60 seconds
        buffer = timedelta(seconds=60)
        return datetime.utcnow() >= (connection.expires_at - buffer)

    async def get_valid_token(self, connection: Connection, session) -> str:
        """Get a valid access token, refreshing if necessary"""

        if self.is_token_expired(connection):
            connection = await self.refresh_token(connection, session)

        return connection.access_token
```

#### Task 1.4: Update SageV31Client to Use Token Manager

**File:** `backend/app/sage_v31.py`

**Update imports:**

```python
from .token_manager import TokenManager
```

**Update `_request` method:**

```python
async def _request(self, method: str, path: str, *, params: Dict[str, Any] | None=None,
                   json: Dict[str, Any] | None=None, headers: Dict[str,str] | None=None):
    base = self.settings.sage_base_url.rstrip("/")
    url = f"{base}{path}"

    token_manager = TokenManager()

    async with httpx.AsyncClient(timeout=60) as client, get_session() as session:
        conn = self._get_connection(session)

        # Ensure we have a valid token
        access_token = await token_manager.get_valid_token(conn, session)

        # Build headers
        h = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Add X-Business header if business_id is set
        if conn.business_id:
            h["X-Business"] = conn.business_id

        if headers:
            h.update(headers)

        # Make request
        resp = await client.request(method, url, params=params, json=json, headers=h)

        # Handle 401 - token might have expired despite our check
        if resp.status_code == 401:
            # Try refreshing token once
            conn = await token_manager.refresh_token(conn, session)
            h["Authorization"] = f"Bearer {conn.access_token}"

            # Retry request
            resp = await client.request(method, url, params=params, json=json, headers=h)

        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)

        return resp.json()
```

**Acceptance Criteria:**
- ✅ OAuth URLs point to correct Sage endpoints
- ✅ Token expiry is calculated and stored
- ✅ Tokens are automatically refreshed before expiry
- ✅ 401 errors trigger token refresh and retry
- ✅ New refresh tokens are stored after each refresh

---

### Phase 2: X-Business Context Management (Priority: CRITICAL)

**Estimated Time:** 2 days

#### Task 2.1: Update Database Schema

**File:** `backend/app/db.py`

**Connection model already has `business_id` field** ✅

Verify the field exists:

```python
class Connection(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    provider: str  # 'sbca'
    business_id: Optional[str] = None  # ✅ Already present
    secret_ref: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    status: str = "active"
```

Add new model for storing business metadata:

```python
class Business(SQLModel, table=True):
    """Stores Sage business metadata"""
    id: str = Field(primary_key=True)  # Sage business ID
    connection_id: str = Field(foreign_key="connection.id")
    tenant_id: str = Field(foreign_key="tenant.id")
    name: str
    country: str = "ZA"
    currency: str = "ZAR"
    is_selected: bool = False  # Currently selected business
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Task 2.2: Create Business Selection Endpoint

**File:** `backend/app/routes_business.py` (NEW FILE)

```python
from fastapi import APIRouter, Depends, HTTPException
from .db import get_session, Connection, Business
from .settings import get_settings
from sqlmodel import select
import httpx
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/business", tags=["business"])

def _tenant_id() -> str:
    return "demo-tenant"

class BusinessInfo(BaseModel):
    id: str
    name: str
    country: str
    currency: str

class SelectBusinessRequest(BaseModel):
    business_id: str

@router.get("/list")
async def list_businesses(connection_id: str, session=Depends(get_session)):
    """Fetch available businesses from Sage API"""

    conn = session.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    s = get_settings()

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{s.sage_base_url}/businesses",
            headers={"Authorization": f"Bearer {conn.access_token}"}
        )
        resp.raise_for_status()
        data = resp.json()

    businesses = []
    for item in data.get("$items", []):
        businesses.append(BusinessInfo(
            id=item["id"],
            name=item.get("name", "Unnamed Business"),
            country=item.get("country", "ZA"),
            currency=item.get("base_currency", {}).get("id", "ZAR")
        ))

    return {"businesses": businesses}

@router.post("/select")
async def select_business(
    connection_id: str,
    request: SelectBusinessRequest,
    session=Depends(get_session)
):
    """Select a business for the connection"""

    conn = session.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Update connection with selected business
    conn.business_id = request.business_id
    conn.status = "active"

    session.add(conn)
    session.commit()

    return {"success": True, "business_id": request.business_id}
```

**Register router in `main.py`:**

```python
from .routes_business import router as business_router
app.include_router(business_router)
```

#### Task 2.3: Build Business Selection UI

**File:** `frontend/src/pages/SelectBusiness.jsx` (NEW FILE)

```jsx
import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

export default function SelectBusiness() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const connectionId = searchParams.get('connection_id')

  const [businesses, setBusinesses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!connectionId) {
      setError('No connection ID provided')
      setLoading(false)
      return
    }

    fetch(`/api/business/list?connection_id=${connectionId}`)
      .then(r => r.json())
      .then(data => {
        setBusinesses(data.businesses || [])
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [connectionId])

  const selectBusiness = async (businessId) => {
    try {
      await fetch(`/api/business/select?connection_id=${connectionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ business_id: businessId })
      })

      // Redirect to main app
      navigate('/')
    } catch (err) {
      alert('Failed to select business: ' + err.message)
    }
  }

  if (loading) return <div style={{padding: 40}}>Loading businesses...</div>
  if (error) return <div style={{padding: 40, color: 'red'}}>Error: {error}</div>

  return (
    <div style={{maxWidth: 600, margin: '40px auto', fontFamily: 'Inter, system-ui'}}>
      <h1>Select Your Business</h1>
      <p>Choose which Sage business you want to connect to this workspace:</p>

      <div style={{marginTop: 24}}>
        {businesses.map(biz => (
          <div
            key={biz.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: 8,
              padding: 16,
              marginBottom: 12,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onClick={() => selectBusiness(biz.id)}
            onMouseEnter={e => e.currentTarget.style.borderColor = '#0066cc'}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#ddd'}
          >
            <h3 style={{margin: 0}}>{biz.name}</h3>
            <p style={{margin: '8px 0 0', color: '#666', fontSize: 14}}>
              {biz.country} • {biz.currency}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Acceptance Criteria:**
- ✅ Business ID stored in Connection model
- ✅ X-Business header included in all API requests
- ✅ User can select business after OAuth
- ✅ Business selection UI is intuitive
- ✅ Selected business persists across sessions

---

### Phase 3: South African Localization (Priority: HIGH)

**Estimated Time:** 2 days

#### Task 3.1: Create South African Defaults

**File:** `backend/app/za_defaults.py` (NEW FILE)

```python
"""South African business defaults for Sage Business Cloud Accounting"""

# Currency
DEFAULT_CURRENCY = "ZAR"

# VAT Rates
VAT_RATES = {
    "STANDARD": {
        "id": "ZA_STANDARD",
        "rate": 15.0,
        "name": "Standard VAT 15%"
    },
    "ZERO": {
        "id": "ZA_ZERO",
        "rate": 0.0,
        "name": "Zero-rated VAT 0%"
    },
    "EXEMPT": {
        "id": "ZA_EXEMPT",
        "rate": 0.0,
        "name": "VAT Exempt"
    }
}

# Payment Terms
PAYMENT_TERMS = {
    "IMMEDIATE": {
        "days": 0,
        "name": "Immediate"
    },
    "7_DAYS": {
        "days": 7,
        "name": "7 Days"
    },
    "30_DAYS": {
        "days": 30,
        "name": "30 Days"
    },
    "60_DAYS": {
        "days": 60,
        "name": "60 Days"
    },
    "90_DAYS": {
        "days": 90,
        "name": "90 Days"
    }
}

# Invoice Defaults
INVOICE_DEFAULTS = {
    "currency": DEFAULT_CURRENCY,
    "tax_rate": VAT_RATES["STANDARD"]["id"],
    "payment_terms_days": PAYMENT_TERMS["30_DAYS"]["days"],
}

def get_invoice_template(contact_id: str, date: str, due_date: str,
                         reference: str, line_items: list) -> dict:
    """Generate a South African invoice payload template"""

    return {
        "contact": {
            "id": contact_id
        },
        "date": date,
        "due_date": due_date,
        "reference": reference,
        "currency": {
            "id": DEFAULT_CURRENCY
        },
        "invoice_lines": [
            {
                "description": item["description"],
                "quantity": item.get("quantity", 1),
                "unit_price": item["unit_price"],
                "tax_rate": {
                    "id": item.get("tax_rate_id", VAT_RATES["STANDARD"]["id"])
                },
                "ledger_account": {
                    "id": item["ledger_account_id"]
                }
            }
            for item in line_items
        ]
    }

def calculate_vat(net_amount: float, vat_rate_id: str = "ZA_STANDARD") -> dict:
    """Calculate VAT for South African invoices"""

    rate = 0.0
    for vat in VAT_RATES.values():
        if vat["id"] == vat_rate_id:
            rate = vat["rate"]
            break

    vat_amount = round(net_amount * (rate / 100), 2)
    gross_amount = round(net_amount + vat_amount, 2)

    return {
        "net_amount": net_amount,
        "vat_rate": rate,
        "vat_amount": vat_amount,
        "gross_amount": gross_amount
    }
```

#### Task 3.2: Enhance Invoice Creation Endpoint

**File:** `backend/app/routes_sage.py`

**Add imports:**

```python
from .za_defaults import get_invoice_template, calculate_vat, VAT_RATES
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
```

**Add request models:**

```python
class InvoiceLineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float
    tax_rate_id: str = "ZA_STANDARD"
    ledger_account_id: str

class CreateInvoiceRequest(BaseModel):
    contact_id: str
    reference: str
    date: str  # YYYY-MM-DD
    due_date: str  # YYYY-MM-DD
    line_items: List[InvoiceLineItem]
    notes: str = ""

class InvoicePreview(BaseModel):
    contact_id: str
    reference: str
    date: str
    due_date: str
    currency: str
    line_items: List[dict]
    net_amount: float
    vat_amount: float
    gross_amount: float
```

**Update create endpoint:**

```python
@router.post("/sales_invoices/preview")
async def preview_sales_invoice(request: CreateInvoiceRequest):
    """Preview invoice before creation (for confirmation)"""

    # Calculate totals
    net_total = sum(item.quantity * item.unit_price for item in request.line_items)
    vat_calc = calculate_vat(net_total, request.line_items[0].tax_rate_id if request.line_items else "ZA_STANDARD")

    # Build preview
    preview = InvoicePreview(
        contact_id=request.contact_id,
        reference=request.reference,
        date=request.date,
        due_date=request.due_date,
        currency="ZAR",
        line_items=[item.dict() for item in request.line_items],
        net_amount=vat_calc["net_amount"],
        vat_amount=vat_calc["vat_amount"],
        gross_amount=vat_calc["gross_amount"]
    )

    return preview

@router.post("/sales_invoices")
async def create_sales_invoice(request: CreateInvoiceRequest):
    """Create a sales invoice with South African defaults"""

    client = SageV31Client(_tenant_id())

    # Build payload using ZA template
    line_items = [
        {
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "tax_rate_id": item.tax_rate_id,
            "ledger_account_id": item.ledger_account_id
        }
        for item in request.line_items
    ]

    payload = get_invoice_template(
        contact_id=request.contact_id,
        date=request.date,
        due_date=request.due_date,
        reference=request.reference,
        line_items=line_items
    )

    # Add notes if provided
    if request.notes:
        payload["notes"] = request.notes

    return await client.create_sales_invoice(payload)
```

#### Task 3.3: Create Settings Initialization

**File:** `backend/app/routes_settings.py`

**Add endpoint to initialize ZA defaults:**

```python
from .za_defaults import INVOICE_DEFAULTS, VAT_RATES, PAYMENT_TERMS

@router.post("/initialize-za-defaults")
def initialize_za_defaults(session=Depends(get_session)):
    """Initialize South African default settings"""

    tenant_id = _tenant_id()

    # Invoice defaults
    for key, value in INVOICE_DEFAULTS.items():
        setting = Setting(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            scope="workspace",
            key=f"invoice_default_{key}",
            value=json.dumps(value)
        )
        session.add(setting)

    # VAT rates
    setting = Setting(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        scope="workspace",
        key="vat_rates",
        value=json.dumps(VAT_RATES)
    )
    session.add(setting)

    # Payment terms
    setting = Setting(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        scope="workspace",
        key="payment_terms",
        value=json.dumps(PAYMENT_TERMS)
    )
    session.add(setting)

    session.commit()

    return {"success": True, "message": "South African defaults initialized"}
```

**Acceptance Criteria:**
- ✅ ZAR currency set as default
- ✅ ZA_STANDARD (15%) VAT rate configured
- ✅ Payment terms (30 days default) configured
- ✅ Invoice template includes all required fields
- ✅ VAT calculation is accurate

---

### Phase 4: Audit Logging & Preview/Confirm Pattern (Priority: HIGH)

**Estimated Time:** 2 days

#### Task 4.1: Create Audit Service

**File:** `backend/app/audit_service.py` (NEW FILE)

```python
from .db import AuditLog, get_session
from datetime import datetime
import uuid
import json
from typing import Optional, Dict, Any

class AuditService:
    """Service for creating and managing audit logs"""

    def __init__(self, tenant_id: str, user_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id or "system"

    def create_log(
        self,
        action: str,
        target: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        status: str = "preview"
    ) -> str:
        """Create a new audit log entry"""

        with get_session() as session:
            log_id = str(uuid.uuid4())

            audit_log = AuditLog(
                id=log_id,
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                action=action,
                target=target,
                request=json.dumps(request_data) if request_data else None,
                status=status,
                created_at=datetime.utcnow()
            )

            session.add(audit_log)
            session.commit()

            return log_id

    def update_log(
        self,
        log_id: str,
        status: str,
        response_data: Optional[Dict[str, Any]] = None
    ):
        """Update an existing audit log"""

        with get_session() as session:
            log = session.get(AuditLog, log_id)
            if log:
                log.status = status
                if response_data:
                    log.response = json.dumps(response_data)
                session.add(log)
                session.commit()

    def get_logs(self, limit: int = 100, action: Optional[str] = None):
        """Retrieve audit logs"""

        with get_session() as session:
            from sqlmodel import select

            query = select(AuditLog).where(AuditLog.tenant_id == self.tenant_id)

            if action:
                query = query.where(AuditLog.action == action)

            query = query.order_by(AuditLog.created_at.desc()).limit(limit)

            logs = session.exec(query).all()

            return [
                {
                    "id": log.id,
                    "action": log.action,
                    "target": log.target,
                    "status": log.status,
                    "created_at": log.created_at.isoformat(),
                    "user_id": log.user_id
                }
                for log in logs
            ]
```

#### Task 4.2: Integrate Audit Logging into Invoice Creation

**File:** `backend/app/routes_sage.py`

**Update imports:**

```python
from .audit_service import AuditService
```

**Update create_sales_invoice endpoint:**

```python
@router.post("/sales_invoices")
async def create_sales_invoice(request: CreateInvoiceRequest, audit_log_id: Optional[str] = None):
    """Create a sales invoice with audit logging"""

    tenant_id = _tenant_id()
    audit = AuditService(tenant_id)

    # Create or update audit log
    if not audit_log_id:
        audit_log_id = audit.create_log(
            action="create_sales_invoice",
            target=request.reference,
            request_data=request.dict(),
            status="confirmed"
        )
    else:
        audit.update_log(audit_log_id, status="confirmed")

    try:
        client = SageV31Client(tenant_id)

        # Build payload
        line_items = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "tax_rate_id": item.tax_rate_id,
                "ledger_account_id": item.ledger_account_id
            }
            for item in request.line_items
        ]

        payload = get_invoice_template(
            contact_id=request.contact_id,
            date=request.date,
            due_date=request.due_date,
            reference=request.reference,
            line_items=line_items
        )

        if request.notes:
            payload["notes"] = request.notes

        # Create invoice
        result = await client.create_sales_invoice(payload)

        # Update audit log with success
        audit.update_log(audit_log_id, status="success", response_data=result)

        return result

    except Exception as e:
        # Update audit log with failure
        audit.update_log(audit_log_id, status="failure", response_data={"error": str(e)})
        raise
```

**Add audit log viewer endpoint:**

```python
@router.get("/audit-logs")
async def get_audit_logs(limit: int = 100, action: Optional[str] = None):
    """Get audit logs for the tenant"""

    audit = AuditService(_tenant_id())
    return {"logs": audit.get_logs(limit=limit, action=action)}
```

**Acceptance Criteria:**
- ✅ All write operations create audit logs
- ✅ Preview creates log with status="preview"
- ✅ Confirm updates log to status="confirmed"
- ✅ Success/failure status recorded
- ✅ Request and response data stored

---

### Phase 5: Incremental Sync Mechanism (Priority: MEDIUM)

**Estimated Time:** 2 days

#### Task 5.1: Create Sync Service

**File:** `backend/app/sync_service.py` (NEW FILE)

```python
from .db import SyncCursor, get_session
from .sage_v31 import SageV31Client
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class SyncService:
    """Service for incremental data synchronization"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = SageV31Client(tenant_id)

    def get_cursor(self, resource: str) -> Optional[str]:
        """Get last sync timestamp for a resource"""

        with get_session() as session:
            from sqlmodel import select

            cursor = session.exec(
                select(SyncCursor).where(
                    SyncCursor.tenant_id == self.tenant_id,
                    SyncCursor.id == resource
                )
            ).first()

            return cursor.last_ts if cursor else None

    def update_cursor(self, resource: str, timestamp: str):
        """Update last sync timestamp for a resource"""

        with get_session() as session:
            from sqlmodel import select

            cursor = session.exec(
                select(SyncCursor).where(
                    SyncCursor.tenant_id == self.tenant_id,
                    SyncCursor.id == resource
                )
            ).first()

            if cursor:
                cursor.last_ts = timestamp
            else:
                cursor = SyncCursor(
                    id=resource,
                    tenant_id=self.tenant_id,
                    last_ts=timestamp
                )

            session.add(cursor)
            session.commit()

    async def sync_sales_invoices(self) -> Dict[str, Any]:
        """Sync sales invoices incrementally"""

        last_sync = self.get_cursor("sales_invoices")

        # Fetch updated/created invoices
        result = await self.client.list_sales_invoices(
            updated_since=last_sync,
            items_per_page=200
        )

        items = result.get("$items", [])

        # Update cursor with current timestamp
        current_ts = datetime.utcnow().isoformat() + "Z"
        self.update_cursor("sales_invoices", current_ts)

        return {
            "resource": "sales_invoices",
            "last_sync": last_sync,
            "current_sync": current_ts,
            "items_synced": len(items),
            "items": items
        }

    async def sync_contacts(self) -> Dict[str, Any]:
        """Sync contacts incrementally"""

        last_sync = self.get_cursor("contacts")

        # Note: Contacts endpoint might not support updated_since
        # In that case, fetch all and compare locally
        result = await self.client.list_contacts(items_per_page=200)

        items = result.get("$items", [])

        current_ts = datetime.utcnow().isoformat() + "Z"
        self.update_cursor("contacts", current_ts)

        return {
            "resource": "contacts",
            "last_sync": last_sync,
            "current_sync": current_ts,
            "items_synced": len(items),
            "items": items
        }

    async def sync_all(self) -> List[Dict[str, Any]]:
        """Sync all resources"""

        results = []

        # Sync invoices
        results.append(await self.sync_sales_invoices())

        # Sync contacts
        results.append(await self.sync_contacts())

        return results
```

#### Task 5.2: Create Sync Endpoints

**File:** `backend/app/routes_sync.py` (NEW FILE)

```python
from fastapi import APIRouter, BackgroundTasks
from .sync_service import SyncService
from typing import Optional

router = APIRouter(prefix="/api/sync", tags=["sync"])

def _tenant_id() -> str:
    return "demo-tenant"

@router.post("/sales_invoices")
async def sync_sales_invoices():
    """Trigger incremental sync for sales invoices"""

    sync = SyncService(_tenant_id())
    result = await sync.sync_sales_invoices()

    return result

@router.post("/contacts")
async def sync_contacts():
    """Trigger incremental sync for contacts"""

    sync = SyncService(_tenant_id())
    result = await sync.sync_contacts()

    return result

@router.post("/all")
async def sync_all(background_tasks: BackgroundTasks):
    """Trigger full incremental sync (background)"""

    async def run_sync():
        sync = SyncService(_tenant_id())
        await sync.sync_all()

    background_tasks.add_task(run_sync)

    return {"status": "sync_started"}

@router.get("/status")
async def sync_status():
    """Get sync status for all resources"""

    sync = SyncService(_tenant_id())

    return {
        "sales_invoices": {
            "last_sync": sync.get_cursor("sales_invoices")
        },
        "contacts": {
            "last_sync": sync.get_cursor("contacts")
        }
    }
```

**Register router in `main.py`:**

```python
from .routes_sync import router as sync_router
app.include_router(sync_router)
```

**Acceptance Criteria:**
- ✅ Sync cursors stored per resource
- ✅ `updated_or_created_since` parameter used
- ✅ Incremental sync reduces API calls
- ✅ Background sync option available
- ✅ Sync status visible to users

---

## Database Schema Enhancements

### Complete Schema Diagram

```sql
┌─────────────────────────────────────────────────────────────────┐
│                           TENANT                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR                              │   │
│  │ name                 VARCHAR                              │   │
│  │ region               VARCHAR  DEFAULT 'ZA'                │   │
│  │ created_at           TIMESTAMP                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ 1:N
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                           USER                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR                              │   │
│  │ tenant_id (FK)       VARCHAR → tenant.id                  │   │
│  │ email                VARCHAR                              │   │
│  │ display_name         VARCHAR                              │   │
│  │ role                 VARCHAR  DEFAULT 'Owner'             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         CONNECTION                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR                              │   │
│  │ tenant_id (FK)       VARCHAR → tenant.id                  │   │
│  │ provider             VARCHAR  'sbca'                      │   │
│  │ business_id          VARCHAR  (Sage business ID)          │   │
│  │ secret_ref           VARCHAR  (KMS reference)             │   │
│  │ access_token         VARCHAR  (encrypted)                 │   │
│  │ refresh_token        VARCHAR  (encrypted)                 │   │
│  │ expires_at           TIMESTAMP                            │   │
│  │ status               VARCHAR  'active'|'pending'|'error'  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          BUSINESS                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR  (Sage business ID)          │   │
│  │ connection_id (FK)   VARCHAR → connection.id              │   │
│  │ tenant_id (FK)       VARCHAR → tenant.id                  │   │
│  │ name                 VARCHAR                              │   │
│  │ country              VARCHAR  DEFAULT 'ZA'                │   │
│  │ currency             VARCHAR  DEFAULT 'ZAR'               │   │
│  │ is_selected          BOOLEAN  DEFAULT false               │   │
│  │ created_at           TIMESTAMP                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          SETTING                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR                              │   │
│  │ tenant_id (FK)       VARCHAR → tenant.id                  │   │
│  │ scope                VARCHAR  'workspace'|'personal'|...  │   │
│  │ key                  VARCHAR                              │   │
│  │ value                TEXT     (JSON)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  INDEX: (tenant_id, scope, key)                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         AUDIT_LOG                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR                              │   │
│  │ tenant_id (FK)       VARCHAR → tenant.id                  │   │
│  │ user_id              VARCHAR                              │   │
│  │ action               VARCHAR  'create_invoice'|...        │   │
│  │ target               VARCHAR  (reference/ID)              │   │
│  │ request              TEXT     (JSON)                      │   │
│  │ response             TEXT     (JSON)                      │   │
│  │ status               VARCHAR  'preview'|'confirmed'|...   │   │
│  │ created_at           TIMESTAMP                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  INDEX: (tenant_id, created_at DESC)                            │
│  INDEX: (tenant_id, action)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        SYNC_CURSOR                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ id (PK)              VARCHAR  (resource name)             │   │
│  │ tenant_id (FK)       VARCHAR → tenant.id                  │   │
│  │ last_ts              VARCHAR  (ISO timestamp)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  UNIQUE: (tenant_id, id)                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Migration Strategy

**File:** `backend/alembic/versions/001_initial_schema.py`

```python
"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-10

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables
    op.create_table(
        'tenant',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=False, server_default='ZA'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False, server_default='Owner'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'])
    )

    op.create_table(
        'connection',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('business_id', sa.String(), nullable=True),
        sa.Column('secret_ref', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'])
    )

    # Add indexes
    op.create_index('idx_connection_tenant', 'connection', ['tenant_id'])
    op.create_index('idx_connection_status', 'connection', ['status'])

def downgrade():
    op.drop_table('connection')
    op.drop_table('user')
    op.drop_table('tenant')
```

**Indexing Recommendations:**

1. **Connection Table:**
   - Index on `(tenant_id, provider)` for fast connection lookup
   - Index on `expires_at` for token refresh queries

2. **AuditLog Table:**
   - Index on `(tenant_id, created_at DESC)` for recent logs
   - Index on `(tenant_id, action)` for filtering by action type
   - Index on `status` for filtering by status

3. **Setting Table:**
   - Unique index on `(tenant_id, scope, key)` for fast lookups

4. **SyncCursor Table:**
   - Unique index on `(tenant_id, id)` for resource lookups

---

## API Endpoint Specifications

### Complete API Reference

#### Authentication Endpoints

**1. Start OAuth Flow**

```http
GET /auth/start
```

**Response:** Redirect to Sage OAuth authorization page

**Example:**
```bash
curl http://localhost:8777/auth/start
# Redirects to: https://www.sageone.com/oauth2/auth/central?filter=apiv3.1&...
```

---

**2. OAuth Callback**

```http
GET /auth/callback?code={code}&state={state}
```

**Query Parameters:**
- `code` (string, required) - Authorization code from Sage
- `state` (string, required) - CSRF protection token

**Response:** Redirect to business selection page

---

#### Business Management Endpoints

**3. List Available Businesses**

```http
GET /api/business/list?connection_id={connection_id}
```

**Query Parameters:**
- `connection_id` (string, required) - Connection ID

**Response:**
```json
{
  "businesses": [
    {
      "id": "12345678-1234-1234-1234-123456789012",
      "name": "Acme Corp (Pty) Ltd",
      "country": "ZA",
      "currency": "ZAR"
    }
  ]
}
```

---

**4. Select Business**

```http
POST /api/business/select?connection_id={connection_id}
Content-Type: application/json

{
  "business_id": "12345678-1234-1234-1234-123456789012"
}
```

**Response:**
```json
{
  "success": true,
  "business_id": "12345678-1234-1234-1234-123456789012"
}
```

---

#### Sales Invoice Endpoints

**5. List Sales Invoices**

```http
GET /api/sage/sales_invoices?updated_since={timestamp}
```

**Query Parameters:**
- `updated_since` (string, optional) - ISO 8601 timestamp for incremental sync

**Response:**
```json
{
  "$total": 150,
  "$page": 1,
  "$itemsPerPage": 50,
  "$items": [
    {
      "id": "invoice-id-123",
      "displayed_as": "SI-2025-001",
      "reference": "INV-001",
      "contact": {
        "id": "contact-id",
        "displayed_as": "Acme Corp"
      },
      "date": "2025-10-10",
      "due_date": "2025-11-09",
      "total_amount": "6900.00",
      "outstanding_amount": "6900.00",
      "currency": {
        "id": "ZAR"
      },
      "status": {
        "id": "DRAFT",
        "displayed_as": "Draft"
      }
    }
  ]
}
```

---

**6. Preview Sales Invoice**

```http
POST /api/sage/sales_invoices/preview
Content-Type: application/json

{
  "contact_id": "contact-id-123",
  "reference": "INV-2025-001",
  "date": "2025-10-10",
  "due_date": "2025-11-09",
  "line_items": [
    {
      "description": "Professional Services",
      "quantity": 40,
      "unit_price": 150.00,
      "tax_rate_id": "ZA_STANDARD",
      "ledger_account_id": "account-id-123"
    }
  ],
  "notes": "Payment due within 30 days"
}
```

**Response:**
```json
{
  "contact_id": "contact-id-123",
  "reference": "INV-2025-001",
  "date": "2025-10-10",
  "due_date": "2025-11-09",
  "currency": "ZAR",
  "line_items": [...],
  "net_amount": 6000.00,
  "vat_amount": 900.00,
  "gross_amount": 6900.00
}
```

---

**7. Create Sales Invoice**

```http
POST /api/sage/sales_invoices
Content-Type: application/json

{
  "contact_id": "contact-id-123",
  "reference": "INV-2025-001",
  "date": "2025-10-10",
  "due_date": "2025-11-09",
  "line_items": [
    {
      "description": "Professional Services",
      "quantity": 40,
      "unit_price": 150.00,
      "tax_rate_id": "ZA_STANDARD",
      "ledger_account_id": "account-id-123"
    }
  ],
  "notes": "Payment due within 30 days"
}
```

**Response:** Sage API invoice object (see SAGE_API_ANALYSIS.md)

---

**8. Release Sales Invoice**

```http
POST /api/sage/sales_invoices/{invoice_id}/release
```

**Response:**
```json
{
  "id": "invoice-id-123",
  "status": {
    "id": "UNPAID",
    "displayed_as": "Unpaid"
  }
}
```

---

#### Contact Endpoints

**9. List Contacts**

```http
GET /api/sage/contacts?search={query}
```

**Query Parameters:**
- `search` (string, optional) - Search term

**Response:**
```json
{
  "$total": 50,
  "$items": [
    {
      "id": "contact-id-123",
      "displayed_as": "Acme Corp (ACM001)",
      "name": "Acme Corp",
      "reference": "ACM001",
      "email": "info@acmecorp.com",
      "contact_types": [
        {
          "id": "CUSTOMER",
          "displayed_as": "Customer"
        }
      ]
    }
  ]
}
```

---

**10. Create Contact**

```http
POST /api/sage/contacts
Content-Type: application/json

{
  "contact_types": [{"id": "CUSTOMER"}],
  "name": "Acme Corporation",
  "reference": "ACM001",
  "email": "info@acmecorp.com",
  "tax_number": "ZA1234567890",
  "credit_limit": 5000.00,
  "credit_days": 30,
  "currency": {"id": "ZAR"},
  "main_address": {
    "address_line_1": "123 Main Street",
    "city": "Johannesburg",
    "postal_code": "2000",
    "country": {"id": "ZA"}
  }
}
```

**Response:** Sage API contact object

---

#### Settings Endpoints

**11. Get Settings by Scope**

```http
GET /api/settings/{scope}
```

**Path Parameters:**
- `scope` (string) - One of: workspace, personal, automation, template, security

**Response:**
```json
{
  "invoice_default_currency": "ZAR",
  "invoice_default_tax_rate": "ZA_STANDARD",
  "invoice_default_payment_terms_days": 30
}
```

---

**12. Update Setting**

```http
PUT /api/settings/{scope}/{key}
Content-Type: application/json

{
  "value": "ZAR"
}
```

**Response:**
```json
{
  "ok": true
}
```

---

**13. Initialize ZA Defaults**

```http
POST /api/settings/initialize-za-defaults
```

**Response:**
```json
{
  "success": true,
  "message": "South African defaults initialized"
}
```

---

#### Sync Endpoints

**14. Sync Sales Invoices**

```http
POST /api/sync/sales_invoices
```

**Response:**
```json
{
  "resource": "sales_invoices",
  "last_sync": "2025-10-09T14:00:00Z",
  "current_sync": "2025-10-10T14:00:00Z",
  "items_synced": 15,
  "items": [...]
}
```

---

**15. Sync All Resources**

```http
POST /api/sync/all
```

**Response:**
```json
{
  "status": "sync_started"
}
```

---

**16. Get Sync Status**

```http
GET /api/sync/status
```

**Response:**
```json
{
  "sales_invoices": {
    "last_sync": "2025-10-10T14:00:00Z"
  },
  "contacts": {
    "last_sync": "2025-10-10T13:30:00Z"
  }
}
```

---

#### Audit Endpoints

**17. Get Audit Logs**

```http
GET /api/sage/audit-logs?limit=100&action=create_sales_invoice
```

**Query Parameters:**
- `limit` (integer, optional) - Max number of logs (default: 100)
- `action` (string, optional) - Filter by action type

**Response:**
```json
{
  "logs": [
    {
      "id": "log-id-123",
      "action": "create_sales_invoice",
      "target": "INV-2025-001",
      "status": "success",
      "created_at": "2025-10-10T14:30:00",
      "user_id": "user-123"
    }
  ]
}
```

---

#### Health Check

**18. Health Check**

```http
GET /healthz
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## Custom UI Design Specifications

### 1. OAuth Connection Flow

**Component:** `OAuthConnect.jsx`

**Wireframe:**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              Connect to Sage Accounting                 │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │                                                   │ │
│  │   [Sage Logo]                                     │ │
│  │                                                   │ │
│  │   Connect your Sage Business Cloud Accounting    │ │
│  │   account to start managing invoices and          │ │
│  │   contacts.                                       │ │
│  │                                                   │ │
│  │   ┌─────────────────────────────────────────┐    │ │
│  │   │  🔒 Connect with Sage                   │    │ │
│  │   └─────────────────────────────────────────┘    │ │
│  │                                                   │ │
│  │   ✓ Secure OAuth 2.0 authentication              │ │
│  │   ✓ Your credentials are never stored            │ │
│  │   ✓ You can revoke access anytime                │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```jsx
export default function OAuthConnect() {
  const handleConnect = () => {
    window.location.href = '/auth/start'
  }

  return (
    <div style={{maxWidth: 500, margin: '80px auto', textAlign: 'center'}}>
      <img src="/sage-logo.svg" alt="Sage" style={{width: 120, marginBottom: 24}} />

      <h1>Connect to Sage Accounting</h1>
      <p style={{color: '#666', marginBottom: 32}}>
        Connect your Sage Business Cloud Accounting account to start managing
        invoices and contacts.
      </p>

      <button
        onClick={handleConnect}
        style={{
          background: '#00A651',
          color: 'white',
          border: 'none',
          padding: '16px 32px',
          fontSize: 16,
          borderRadius: 8,
          cursor: 'pointer',
          fontWeight: 600
        }}
      >
        🔒 Connect with Sage
      </button>

      <div style={{marginTop: 32, fontSize: 14, color: '#888'}}>
        <div>✓ Secure OAuth 2.0 authentication</div>
        <div>✓ Your credentials are never stored</div>
        <div>✓ You can revoke access anytime</div>
      </div>
    </div>
  )
}
```

---

### 2. Business Selection Screen

**Component:** `SelectBusiness.jsx` (already provided in Phase 2)

**Wireframe:**

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              Select Your Business                       │
│                                                         │
│  Choose which Sage business you want to connect:       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Acme Corp (Pty) Ltd                              │ │
│  │  ZA • ZAR                                         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Beta Trading CC                                  │ │
│  │  ZA • ZAR                                         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Gamma Services                                   │ │
│  │  ZA • ZAR                                         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 3. Sales Invoice Creation Form

**Component:** `CreateInvoice.jsx`

**Wireframe:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Create Sales Invoice                                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Customer *                                              │   │
│  │ [Select customer ▼]                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │ Invoice Date *       │  │ Due Date *           │           │
│  │ [2025-10-10]         │  │ [2025-11-09]         │           │
│  └──────────────────────┘  └──────────────────────┘           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Reference *                                             │   │
│  │ [INV-2025-001]                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Line Items                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Description          Qty    Price    VAT      Total     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Professional Svc     40     150.00   15%     6,900.00   │   │
│  │ [Edit] [Delete]                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [+ Add Line Item]                                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Notes                                                   │   │
│  │ [Payment due within 30 days]                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Summary                                                 │   │
│  │ Net Amount:          R 6,000.00                         │   │
│  │ VAT (15%):           R   900.00                         │   │
│  │ ─────────────────────────────────                       │   │
│  │ Total:               R 6,900.00                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Cancel]                              [Preview] [Create]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation:** (See full implementation in appendix)

---

### 4. Invoice Preview/Confirm Modal

**Component:** `InvoicePreviewModal.jsx`

**Wireframe:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Preview Invoice                                          [X]   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Invoice: INV-2025-001                                   │   │
│  │ Customer: Acme Corp                                     │   │
│  │ Date: 10 Oct 2025                                       │   │
│  │ Due: 09 Nov 2025                                        │   │
│  │                                                         │   │
│  │ Line Items:                                             │   │
│  │ • Professional Services (40 × R150.00)    R 6,000.00    │   │
│  │                                                         │   │
│  │ Net Amount:                               R 6,000.00    │   │
│  │ VAT (15%):                                R   900.00    │   │
│  │ ───────────────────────────────────────────────────     │   │
│  │ Total:                                    R 6,900.00    │   │
│  │                                                         │   │
│  │ Notes: Payment due within 30 days                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ⚠️  This will create a draft invoice in Sage. You can edit   │
│     or delete it before releasing.                             │
│                                                                 │
│  [Cancel]                                    [Confirm Create]  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5. Contact Management Interface

**Component:** `Contacts.jsx`

**Wireframe:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Contacts                                      [+ New Contact]  │
│                                                                 │
│  [Search contacts...]                          [Filter ▼]      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Name              Type        Email           Balance   │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Acme Corp         Customer    info@acme.com   R 6,900   │   │
│  │ Beta Trading      Customer    beta@bt.co.za   R     0   │   │
│  │ Gamma Services    Supplier    gamma@gs.com    R 2,500   │   │
│  │ Delta Ltd         Customer    delta@dl.com    R 1,200   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Showing 4 of 48 contacts                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 6. Settings and Configuration Page

**Component:** `Settings.jsx`

**Wireframe:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Settings                                                       │
│                                                                 │
│  ┌─ Connection ──────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  Sage Business Cloud Accounting                          │ │
│  │  Connected to: Acme Corp (Pty) Ltd                       │ │
│  │  Business ID: 12345678-1234-1234-1234-123456789012       │ │
│  │                                                           │ │
│  │  [Disconnect]  [Switch Business]                         │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ Invoice Defaults ────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  Currency:        [ZAR ▼]                                │ │
│  │  VAT Rate:        [ZA_STANDARD (15%) ▼]                  │ │
│  │  Payment Terms:   [30 Days ▼]                            │ │
│  │                                                           │ │
│  │  [Save Defaults]                                         │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ Sync Settings ───────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  Last Sync: 10 Oct 2025, 14:00                           │ │
│  │  Auto-sync: [✓] Enabled                                  │ │
│  │  Frequency:  [Every 15 minutes ▼]                        │ │
│  │                                                           │ │
│  │  [Sync Now]                                              │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 7. Audit Log Viewer

**Component:** `AuditLogs.jsx`

**Wireframe:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Audit Log                                                      │
│                                                                 │
│  [Filter by action ▼]  [Filter by status ▼]  [Last 7 days ▼]  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Time              Action              Target    Status  │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ 14:30 10 Oct     Create Invoice      INV-001   ✓       │   │
│  │ 14:25 10 Oct     Create Contact      ACM001    ✓       │   │
│  │ 14:20 10 Oct     Create Invoice      INV-002   ✗       │   │
│  │ 14:15 10 Oct     Update Settings     -         ✓       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Load More]                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration Guide

### Step-by-Step Setup Instructions

#### 1. Prerequisites

**Required Software:**
- Python 3.10 or higher
- Node.js 18 or higher
- Git

**Accounts Needed:**
- Sage Developer Account (https://developer.sage.com/)
- Sage Business Cloud Accounting trial account (South Africa)

---

#### 2. Sage Developer Portal Registration

**Step 2.1: Create Developer Account**

1. Visit https://developer.sage.com/
2. Click "Sign Up" in the top right
3. Fill in your details:
   - Email address
   - Password
   - Company name
   - Country: South Africa
4. Verify your email address
5. Log in to the developer portal

**Step 2.2: Register Your Application**

1. Navigate to **Console** → **Get API Keys (Accounting)**
2. Click **"Create New App"**
3. Fill in application details:
   - **App Name:** "Sage Agent MVP" (or your preferred name)
   - **Description:** "AI-powered Sage Business Cloud Accounting integration"
   - **Callback URLs:**
     - Development: `http://localhost:8777/auth/callback`
     - Production: `https://yourdomain.com/auth/callback`
4. Click **"Create Application"**
5. Save your credentials:
   - **Client ID:** `abc123...` (copy this)
   - **Client Secret:** `xyz789...` (copy this - shown only once!)

⚠️ **Important:** Store your Client Secret securely. It will only be shown once!

---

#### 3. Get Sage Trial Account

**Step 3.1: Sign Up for Trial**

1. Visit https://www.sage.com/en-za/sage-business-cloud/accounting/
2. Click **"Start Free Trial"**
3. Fill in business details:
   - Business name
   - Industry
   - Number of employees
   - **Country:** South Africa
4. Complete registration
5. Verify your email

**Step 3.2: Extend Trial for Development**

1. Log in to your Sage account
2. Follow the guide: https://developer.sage.com/accounting/quick-start/extend-your-sage-business-cloud-accounting-trial/
3. Request trial extension (usually granted for 6-12 months for developers)

**Step 3.3: Set Up Test Data**

1. Create test customers:
   - Acme Corp (Pty) Ltd
   - Beta Trading CC
2. Create test products/services:
   - Professional Services (R150/hour)
   - Consulting (R200/hour)
3. Set up ledger accounts (if not auto-created)

---

#### 4. Backend Setup

**Step 4.1: Clone and Install**

```bash
cd sage-agent-starter/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -e .
```

**Step 4.2: Configure Environment Variables**

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Update `.env` with your values:**

```bash
# FastAPI
APP_ENV=dev
APP_SECRET=your-random-secret-key-here-change-this

# OAuth (SBCA v3.1)
SAGE_CLIENT_ID=your-client-id-from-step-2
SAGE_CLIENT_SECRET=your-client-secret-from-step-2
SAGE_REDIRECT_URI=http://localhost:8777/auth/callback

# Region / base
SAGE_BASE_URL=https://api.accounting.sage.com/v3.1

# Storage (SQLite for starter)
DATABASE_URL=sqlite:///./sage_agent.sqlite3
```

**Step 4.3: Initialize Database**

```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or let SQLModel auto-create tables on first run
python -c "from app.db import init_db; init_db()"
```

**Step 4.4: Start Backend Server**

```bash
uvicorn app.main:app --reload --port 8777
```

**Verify backend is running:**
```bash
curl http://localhost:8777/healthz
# Should return: {"status":"ok"}
```

---

#### 5. Frontend Setup

**Step 5.1: Install Dependencies**

```bash
cd ../frontend

npm install
```

**Step 5.2: Start Development Server**

```bash
npm run dev
```

**Verify frontend is running:**
- Open browser to http://localhost:8081
- You should see the Sage Agent UI

---

#### 6. Test OAuth Flow

**Step 6.1: Initiate Connection**

1. Click **"Connect Sage (OAuth)"** button
2. You'll be redirected to Sage login page
3. Log in with your Sage trial account credentials
4. Authorize the application
5. You'll be redirected back to business selection page

**Step 6.2: Select Business**

1. Choose your test business from the list
2. Click to select
3. You'll be redirected to the main app

**Step 6.3: Verify Connection**

```bash
# Check connection in database
sqlite3 sage_agent.sqlite3
SELECT * FROM connection;
```

You should see your connection with:
- `access_token` (encrypted)
- `refresh_token` (encrypted)
- `business_id` (Sage business ID)
- `status` = "active"

---

#### 7. Initialize South African Defaults

**Step 7.1: Call Initialization Endpoint**

```bash
curl -X POST http://localhost:8777/api/settings/initialize-za-defaults
```

**Step 7.2: Verify Settings**

```bash
curl http://localhost:8777/api/settings/workspace
```

You should see:
```json
{
  "invoice_default_currency": "ZAR",
  "invoice_default_tax_rate": "ZA_STANDARD",
  "invoice_default_payment_terms_days": 30,
  "vat_rates": {...},
  "payment_terms": {...}
}
```

---

#### 8. Test Invoice Creation

**Step 8.1: Get a Contact ID**

```bash
curl http://localhost:8777/api/sage/contacts
```

Copy a contact ID from the response.

**Step 8.2: Create Test Invoice**

```bash
curl -X POST http://localhost:8777/api/sage/sales_invoices \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "your-contact-id-here",
    "reference": "TEST-001",
    "date": "2025-10-10",
    "due_date": "2025-11-09",
    "line_items": [
      {
        "description": "Test Service",
        "quantity": 1,
        "unit_price": 100.00,
        "tax_rate_id": "ZA_STANDARD",
        "ledger_account_id": "your-ledger-account-id"
      }
    ]
  }'
```

**Step 8.3: Verify in Sage**

1. Log in to your Sage account
2. Navigate to **Sales** → **Invoices**
3. You should see your test invoice

---

## Security Considerations

### 1. Token Encryption and Storage

**Current State:** ❌ Tokens stored in plaintext in SQLite

**Required Implementation:**

**File:** `backend/app/crypto.py` (NEW FILE)

```python
from cryptography.fernet import Fernet
from .settings import get_settings
import base64

class TokenEncryption:
    """Encrypt/decrypt OAuth tokens"""

    def __init__(self):
        settings = get_settings()
        # In production, use environment variable or KMS
        key = base64.urlsafe_b64encode(settings.app_secret.encode().ljust(32)[:32])
        self.cipher = Fernet(key)

    def encrypt(self, token: str) -> str:
        """Encrypt a token"""
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()

# Usage in oauth.py and sage_v31.py
crypto = TokenEncryption()

# When storing:
conn.access_token = crypto.encrypt(tok.get("access_token"))
conn.refresh_token = crypto.encrypt(tok.get("refresh_token"))

# When retrieving:
access_token = crypto.decrypt(conn.access_token)
```

**Production Recommendations:**
- Use AWS KMS, Azure Key Vault, or Google Cloud KMS
- Store only encrypted token references in database
- Rotate encryption keys regularly
- Use separate encryption keys per environment

---

### 2. CORS Configuration

**Current State:** ⚠️ Allow all origins (`allow_origins=["*"]`)

**Production Configuration:**

**File:** `backend/app/main.py`

```python
# Development
if s.app_env == "dev":
    origins = ["http://localhost:8081", "http://localhost:3000"]
else:
    # Production - specify your domains
    origins = [
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

---

### 3. API Rate Limiting

**Implementation:**

**File:** `backend/app/rate_limit.py` (NEW FILE)

```python
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def check_rate_limit(self, identifier: str):
        """Check if request is within rate limit"""

        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > minute_ago
        ]

        # Check limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        self.requests[identifier].append(now)

# Usage in main.py
rate_limiter = RateLimiter(requests_per_minute=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Use tenant_id or IP as identifier
    identifier = request.client.host
    await rate_limiter.check_rate_limit(identifier)
    response = await call_next(request)
    return response
```

**Production:** Use Redis-based rate limiting (e.g., `slowapi` library)

---

### 4. Input Validation

**Implementation:** Use Pydantic models for all request bodies

**Example:**

```python
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import date

class InvoiceLineItem(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(..., gt=0, le=10000)
    unit_price: float = Field(..., ge=0, le=1000000)
    tax_rate_id: str = Field(default="ZA_STANDARD")
    ledger_account_id: str = Field(..., min_length=1)

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

class CreateInvoiceRequest(BaseModel):
    contact_id: str = Field(..., min_length=1)
    reference: str = Field(..., min_length=1, max_length=50)
    date: date
    due_date: date
    line_items: List[InvoiceLineItem] = Field(..., min_items=1, max_items=100)
    notes: str = Field(default="", max_length=5000)

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'date' in values and v < values['date']:
            raise ValueError('Due date must be after invoice date')
        return v
```

---

### 5. SQL Injection Prevention

**Current State:** ✅ Using SQLModel ORM (safe from SQL injection)

**Best Practices:**
- Always use ORM methods
- Never concatenate SQL strings
- Use parameterized queries if raw SQL is needed

---

### 6. XSS Prevention

**Frontend:**
- React automatically escapes values in JSX
- Never use `dangerouslySetInnerHTML` with user input
- Sanitize any HTML content before rendering

---

### 7. CSRF Protection

**Implementation:**

```python
from itsdangerous import URLSafeTimedSerializer

def generate_csrf_token():
    s = URLSafeTimedSerializer(get_settings().app_secret)
    return s.dumps("csrf-token")

def validate_csrf_token(token: str, max_age: int = 3600):
    s = URLSafeTimedSerializer(get_settings().app_secret)
    try:
        s.loads(token, max_age=max_age)
        return True
    except:
        return False
```

---

## Deployment Strategy

### Production Deployment Checklist

#### 1. Environment Preparation

**Infrastructure Requirements:**
- [ ] Web server (e.g., AWS EC2, DigitalOcean Droplet, Azure VM)
- [ ] PostgreSQL database (replace SQLite)
- [ ] Redis for caching and rate limiting
- [ ] SSL certificate (Let's Encrypt or commercial)
- [ ] Domain name configured
- [ ] Firewall rules configured

**Environment Variables (Production):**

```bash
# Application
APP_ENV=production
APP_SECRET=<generate-strong-random-secret-256-bits>

# OAuth
SAGE_CLIENT_ID=<production-client-id>
SAGE_CLIENT_SECRET=<production-client-secret>
SAGE_REDIRECT_URI=https://yourdomain.com/auth/callback
SAGE_BASE_URL=https://api.accounting.sage.com/v3.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sage_agent

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ENCRYPTION_KEY=<kms-key-id-or-strong-key>

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=INFO
```

---

#### 2. Database Migration to PostgreSQL

**Step 2.1: Install PostgreSQL**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb sage_agent
sudo -u postgres createuser sage_user
sudo -u postgres psql -c "ALTER USER sage_user WITH PASSWORD 'strong-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sage_agent TO sage_user;"
```

**Step 2.2: Update Dependencies**

```toml
# pyproject.toml
dependencies = [
    # ... existing dependencies
    "psycopg2-binary>=2.9.9",  # PostgreSQL adapter
]
```

**Step 2.3: Update Database URL**

```python
# .env
DATABASE_URL=postgresql://sage_user:strong-password@localhost:5432/sage_agent
```

**Step 2.4: Run Migrations**

```bash
alembic upgrade head
```

---

#### 3. Backend Deployment

**Option A: Docker Deployment**

**File:** `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application
COPY app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8777

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8777"]
```

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8777:8777"
    environment:
      - DATABASE_URL=postgresql://sage_user:password@db:5432/sage_agent
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ./backend/.env
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=sage_agent
      - POSTGRES_USER=sage_user
      - POSTGRES_PASSWORD=strong-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

**Deploy:**

```bash
docker-compose up -d
```

---

**Option B: Traditional Deployment (systemd)**

**File:** `/etc/systemd/system/sage-agent.service`

```ini
[Unit]
Description=Sage Agent Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sage-agent/backend
Environment="PATH=/var/www/sage-agent/backend/.venv/bin"
EnvironmentFile=/var/www/sage-agent/backend/.env
ExecStart=/var/www/sage-agent/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8777
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable sage-agent
sudo systemctl start sage-agent
sudo systemctl status sage-agent
```

---

#### 4. Frontend Deployment

**Step 4.1: Build for Production**

```bash
cd frontend

# Update API URL in vite.config.js for production
# Remove proxy, use full backend URL

npm run build
```

**Step 4.2: Serve with Nginx**

**File:** `/etc/nginx/sites-available/sage-agent`

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    root /var/www/sage-agent/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8777;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # OAuth endpoints
    location /auth {
        proxy_pass http://localhost:8777;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /healthz {
        proxy_pass http://localhost:8777;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/sage-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

#### 5. SSL Certificate Setup

**Using Let's Encrypt:**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

---

#### 6. Monitoring and Logging

**Step 6.1: Application Logging**

**File:** `backend/app/logging_config.py`

```python
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging(app_env: str = "production"):
    """Configure application logging"""

    # Create logger
    logger = logging.getLogger("sage_agent")
    logger.setLevel(logging.INFO if app_env == "production" else logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (rotating)
    if app_env == "production":
        file_handler = RotatingFileHandler(
            '/var/log/sage-agent/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
```

**Step 6.2: Error Tracking with Sentry**

```bash
pip install sentry-sdk[fastapi]
```

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if s.app_env == "production":
    sentry_sdk.init(
        dsn=s.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=s.app_env
    )
```

**Step 6.3: Health Monitoring**

**File:** `backend/app/health.py`

```python
from fastapi import APIRouter
from sqlmodel import select
from .db import get_session, Tenant
import httpx

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "ok"}

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies"""

    health = {
        "status": "ok",
        "checks": {}
    }

    # Database check
    try:
        with get_session() as session:
            session.exec(select(Tenant).limit(1))
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["checks"]["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    # Sage API check
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("https://api.accounting.sage.com/v3.1/")
            if resp.status_code < 500:
                health["checks"]["sage_api"] = "ok"
            else:
                health["checks"]["sage_api"] = "degraded"
                health["status"] = "degraded"
    except Exception as e:
        health["checks"]["sage_api"] = f"error: {str(e)}"
        health["status"] = "degraded"

    return health
```

---

#### 7. Backup Strategy

**Database Backups:**

```bash
#!/bin/bash
# /usr/local/bin/backup-sage-db.sh

BACKUP_DIR="/var/backups/sage-agent"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sage_agent_$DATE.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U sage_user sage_agent | gzip > $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "sage_agent_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron job:**

```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup-sage-db.sh >> /var/log/sage-agent/backup.log 2>&1
```

---

## Testing Strategy

### 1. Unit Tests

**File:** `backend/tests/test_za_defaults.py`

```python
import pytest
from app.za_defaults import calculate_vat, get_invoice_template, VAT_RATES

def test_calculate_vat_standard():
    """Test VAT calculation with standard rate"""
    result = calculate_vat(1000.00, "ZA_STANDARD")

    assert result["net_amount"] == 1000.00
    assert result["vat_rate"] == 15.0
    assert result["vat_amount"] == 150.00
    assert result["gross_amount"] == 1150.00

def test_calculate_vat_zero():
    """Test VAT calculation with zero rate"""
    result = calculate_vat(1000.00, "ZA_ZERO")

    assert result["net_amount"] == 1000.00
    assert result["vat_rate"] == 0.0
    assert result["vat_amount"] == 0.00
    assert result["gross_amount"] == 1000.00

def test_invoice_template_structure():
    """Test invoice template has correct structure"""
    line_items = [
        {
            "description": "Test Service",
            "quantity": 1,
            "unit_price": 100.00,
            "tax_rate_id": "ZA_STANDARD",
            "ledger_account_id": "acc-123"
        }
    ]

    template = get_invoice_template(
        contact_id="contact-123",
        date="2025-10-10",
        due_date="2025-11-09",
        reference="TEST-001",
        line_items=line_items
    )

    assert template["contact"]["id"] == "contact-123"
    assert template["currency"]["id"] == "ZAR"
    assert len(template["invoice_lines"]) == 1
    assert template["invoice_lines"][0]["tax_rate"]["id"] == "ZA_STANDARD"
```

**Run tests:**

```bash
pytest backend/tests/ -v
```

---

### 2. Integration Tests

**File:** `backend/tests/test_oauth_flow.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_start_redirects():
    """Test OAuth start redirects to Sage"""
    response = client.get("/auth/start", follow_redirects=False)

    assert response.status_code == 307
    assert "sageone.com" in response.headers["location"]
    assert "filter=apiv3.1" in response.headers["location"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

---

### 3. End-to-End Tests

**File:** `frontend/tests/e2e/invoice-creation.spec.js`

```javascript
// Using Playwright or Cypress

describe('Invoice Creation Flow', () => {
  it('should create an invoice successfully', () => {
    // 1. Navigate to invoice creation page
    cy.visit('/invoices/new')

    // 2. Select customer
    cy.get('[data-testid="customer-select"]').click()
    cy.contains('Acme Corp').click()

    // 3. Fill in invoice details
    cy.get('[data-testid="reference-input"]').type('TEST-001')
    cy.get('[data-testid="date-input"]').type('2025-10-10')
    cy.get('[data-testid="due-date-input"]').type('2025-11-09')

    // 4. Add line item
    cy.get('[data-testid="add-line-item"]').click()
    cy.get('[data-testid="description-input"]').type('Test Service')
    cy.get('[data-testid="quantity-input"]').type('1')
    cy.get('[data-testid="unit-price-input"]').type('100')

    // 5. Preview invoice
    cy.get('[data-testid="preview-button"]').click()

    // 6. Verify preview
    cy.contains('R 115.00').should('be.visible') // 100 + 15% VAT

    // 7. Confirm creation
    cy.get('[data-testid="confirm-button"]').click()

    // 8. Verify success
    cy.contains('Invoice created successfully').should('be.visible')
  })
})
```

---

### 4. Manual Testing Checklist

**OAuth Flow:**
- [ ] Click "Connect Sage" redirects to Sage login
- [ ] Sage login accepts valid credentials
- [ ] Authorization page shows correct app name and permissions
- [ ] Callback returns to application successfully
- [ ] Business selection page shows all available businesses
- [ ] Selecting a business activates the connection
- [ ] Connection status shows "active" in settings

**Invoice Creation:**
- [ ] Customer dropdown loads all contacts
- [ ] Date picker works correctly
- [ ] Line items can be added/removed
- [ ] VAT calculation is correct (15%)
- [ ] Preview shows accurate totals
- [ ] Confirm creates invoice in Sage
- [ ] Created invoice appears in Sage UI
- [ ] Audit log records the creation

**Token Refresh:**
- [ ] Wait 5+ minutes after OAuth
- [ ] Make an API call
- [ ] Token is automatically refreshed
- [ ] API call succeeds without re-authentication

**Error Handling:**
- [ ] Invalid customer ID shows error message
- [ ] Network errors are handled gracefully
- [ ] 401 errors trigger token refresh
- [ ] 429 errors show rate limit message
- [ ] Validation errors are user-friendly

---

## Appendices

### Appendix A: Complete File Structure

```
sage-agent-starter/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── settings.py
│   │   ├── db.py
│   │   ├── oauth.py
│   │   ├── token_manager.py          # NEW
│   │   ├── sage_v31.py
│   │   ├── za_defaults.py            # NEW
│   │   ├── audit_service.py          # NEW
│   │   ├── sync_service.py           # NEW
│   │   ├── crypto.py                 # NEW
│   │   ├── rate_limit.py             # NEW
│   │   ├── logging_config.py         # NEW
│   │   ├── health.py                 # NEW
│   │   ├── routes_sage.py
│   │   ├── routes_settings.py
│   │   ├── routes_business.py        # NEW
│   │   └── routes_sync.py            # NEW
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_za_defaults.py       # NEW
│   │   ├── test_oauth_flow.py        # NEW
│   │   └── test_invoice_creation.py  # NEW
│   ├── alembic/
│   │   └── versions/
│   │       └── 001_initial_schema.py # NEW
│   ├── pyproject.toml
│   ├── .env
│   ├── .env.example
│   ├── Dockerfile                     # NEW
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── App.jsx
│   │   │   ├── SelectBusiness.jsx    # NEW
│   │   │   ├── CreateInvoice.jsx     # NEW
│   │   │   ├── Contacts.jsx          # NEW
│   │   │   ├── Settings.jsx          # NEW
│   │   │   └── AuditLogs.jsx         # NEW
│   │   ├── components/
│   │   │   ├── OAuthConnect.jsx      # NEW
│   │   │   └── InvoicePreviewModal.jsx # NEW
│   │   └── main.jsx
│   ├── tests/
│   │   └── e2e/
│   │       └── invoice-creation.spec.js # NEW
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile                     # NEW
│   └── index.html
├── docker-compose.yml                 # NEW
├── SAGE_API_ANALYSIS.md
├── MVP_BLUEPRINT.md
└── README.md
```

---

### Appendix B: Environment-Specific Configurations

**Development (.env.dev):**
```bash
APP_ENV=dev
APP_SECRET=dev-secret-not-for-production
SAGE_CLIENT_ID=dev-client-id
SAGE_CLIENT_SECRET=dev-client-secret
SAGE_REDIRECT_URI=http://localhost:8777/auth/callback
DATABASE_URL=sqlite:///./sage_agent.sqlite3
LOG_LEVEL=DEBUG
```

**Staging (.env.staging):**
```bash
APP_ENV=staging
APP_SECRET=<strong-random-secret>
SAGE_CLIENT_ID=staging-client-id
SAGE_CLIENT_SECRET=staging-client-secret
SAGE_REDIRECT_URI=https://staging.yourdomain.com/auth/callback
DATABASE_URL=postgresql://user:pass@staging-db:5432/sage_agent
LOG_LEVEL=INFO
SENTRY_DSN=<staging-sentry-dsn>
```

**Production (.env.prod):**
```bash
APP_ENV=production
APP_SECRET=<strong-random-secret-from-kms>
SAGE_CLIENT_ID=prod-client-id
SAGE_CLIENT_SECRET=prod-client-secret
SAGE_REDIRECT_URI=https://app.yourdomain.com/auth/callback
DATABASE_URL=postgresql://user:pass@prod-db:5432/sage_agent
REDIS_URL=redis://prod-redis:6379/0
LOG_LEVEL=WARNING
SENTRY_DSN=<production-sentry-dsn>
ENCRYPTION_KEY=<kms-key-id>
```

---

### Appendix C: Quick Reference Commands

**Development:**
```bash
# Start backend
cd backend && uvicorn app.main:app --reload --port 8777

# Start frontend
cd frontend && npm run dev

# Run tests
cd backend && pytest tests/ -v

# Initialize ZA defaults
curl -X POST http://localhost:8777/api/settings/initialize-za-defaults
```

**Production:**
```bash
# Deploy with Docker
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart services
docker-compose restart

# Backup database
docker-compose exec db pg_dump -U sage_user sage_agent > backup.sql

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

## Summary

This MVP Blueprint provides a complete implementation guide for building a production-ready Sage Business Cloud Accounting integration for South African businesses. The roadmap is organized into 5 phases:

1. **Phase 1:** OAuth 2.0 Correction & Token Management (CRITICAL)
2. **Phase 2:** X-Business Context Management (CRITICAL)
3. **Phase 3:** South African Localization (HIGH)
4. **Phase 4:** Audit Logging & Preview/Confirm Pattern (HIGH)
5. **Phase 5:** Incremental Sync Mechanism (MEDIUM)

**Estimated Total Implementation Time:** 10-12 days

**Key Deliverables:**
- ✅ Corrected OAuth 2.0 flow with automatic token refresh
- ✅ Multi-business support with X-Business header management
- ✅ South African defaults (ZAR, 15% VAT, 30-day terms)
- ✅ Complete audit trail for compliance
- ✅ Incremental sync for efficient data synchronization
- ✅ Production-ready deployment configuration
- ✅ Comprehensive testing strategy

**Next Steps:**
1. Review this blueprint with your team
2. Set up development environment following Configuration Guide
3. Begin Phase 1 implementation (OAuth fixes)
4. Test each phase thoroughly before moving to the next
5. Deploy to staging environment for UAT
6. Deploy to production with monitoring

For questions or clarifications, refer to the `SAGE_API_ANALYSIS.md` document for detailed Sage API specifications.

---

**Document End**


