from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx, time, secrets
from urllib.parse import urlencode
from .settings import get_settings
from .db import get_session, Connection, Tenant
from sqlmodel import select
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

def _tenant_id() -> str:
    # For starter, a fixed demo tenant. Replace with your auth system.
    return "demo-tenant"

@router.get("/start")
async def auth_start():
    """
    Initiate OAuth 2.0 flow with Sage Business Cloud Accounting.
    Correct OAuth URLs as per Sage API documentation.
    """
    s = get_settings()
    # CORRECT Sage OAuth authorize URL for API v3.1
    authorize_url = "https://www.sageone.com/oauth2/auth/central?filter=apiv3.1"
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": s.sage_client_id,
        "redirect_uri": s.sage_redirect_uri,
        "scope": "full_access",
        "state": state,
    }
    logger.info(f"Starting OAuth flow with state: {state}")
    return RedirectResponse(f"{authorize_url}&{urlencode(params)}")

@router.get("/callback")
async def auth_callback(request: Request, code: str, state: str, session=Depends(get_session)):
    """
    OAuth callback handler. Exchanges authorization code for access token.
    Then fetches available businesses for the user to select.
    """
    s = get_settings()
    # CORRECT Sage OAuth token URL
    token_url = "https://oauth.accounting.sage.com/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": s.sage_redirect_uri,
        "client_id": s.sage_client_id,
        "client_secret": s.sage_client_secret,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(token_url, data=data)
            resp.raise_for_status()
            tok = resp.json()

        # Calculate token expiration (access tokens expire in 5 minutes)
        expires_at = datetime.utcnow() + timedelta(seconds=tok.get("expires_in", 300))

        # Store tokens temporarily (without business_id yet)
        tenant_id = _tenant_id()

        # Check if connection already exists
        existing_conn = session.exec(
            select(Connection).where(
                Connection.tenant_id == tenant_id,
                Connection.provider == "sbca"
            )
        ).first()

        if existing_conn:
            # Update existing connection
            existing_conn.access_token = tok.get("access_token")
            existing_conn.refresh_token = tok.get("refresh_token")
            existing_conn.expires_at = expires_at
            existing_conn.status = "pending_business_selection"
            existing_conn.business_id = None  # Clear until business is selected
            session.add(existing_conn)
        else:
            # Create new connection
            conn = Connection(
                id=f"conn-sbca-{secrets.token_urlsafe(8)}",
                tenant_id=tenant_id,
                provider="sbca",
                access_token=tok.get("access_token"),
                refresh_token=tok.get("refresh_token"),
                expires_at=expires_at,
                status="pending_business_selection",
                business_id=None,
            )
            session.add(conn)

        session.commit()

        logger.info(f"OAuth tokens stored successfully for tenant: {tenant_id}")

        # Redirect to business selection page
        return RedirectResponse("/?select_business=true")

    except httpx.HTTPStatusError as e:
        logger.error(f"OAuth token exchange failed: {e.response.text}")
        raise HTTPException(status_code=400, detail=f"OAuth failed: {e.response.text}")
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OAuth error: {str(e)}")

@router.get("/businesses")
async def get_businesses(session=Depends(get_session)):
    """
    Fetch available businesses for the authenticated user.
    This endpoint is called after OAuth to let user select a business.
    """
    s = get_settings()
    tenant_id = _tenant_id()

    conn = session.exec(
        select(Connection).where(
            Connection.tenant_id == tenant_id,
            Connection.provider == "sbca"
        )
    ).first()

    if not conn or not conn.access_token:
        raise HTTPException(status_code=400, detail="Not authenticated. Please complete OAuth flow first.")

    # Fetch businesses from Sage API
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{s.sage_base_url}/businesses",
                headers={
                    "Authorization": f"Bearer {conn.access_token}",
                    "Accept": "application/json"
                }
            )
            resp.raise_for_status()
            businesses = resp.json()

        return {"businesses": businesses.get("$items", [])}

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch businesses: {e.response.text}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch businesses: {e.response.text}")

@router.post("/select-business")
async def select_business(business_id: str, session=Depends(get_session)):
    """
    Set the selected business for the connection.
    This completes the OAuth setup process.
    """
    tenant_id = _tenant_id()

    conn = session.exec(
        select(Connection).where(
            Connection.tenant_id == tenant_id,
            Connection.provider == "sbca"
        )
    ).first()

    if not conn:
        raise HTTPException(status_code=400, detail="No connection found")

    conn.business_id = business_id
    conn.status = "active"
    session.add(conn)
    session.commit()

    logger.info(f"Business {business_id} selected for tenant {tenant_id}")

    return {"status": "success", "business_id": business_id}

@router.get("/status")
async def auth_status(session=Depends(get_session)):
    """
    Check current authentication status.
    """
    tenant_id = _tenant_id()

    conn = session.exec(
        select(Connection).where(
            Connection.tenant_id == tenant_id,
            Connection.provider == "sbca"
        )
    ).first()

    if not conn:
        return {"authenticated": False, "status": "not_connected"}

    return {
        "authenticated": True,
        "status": conn.status,
        "business_id": conn.business_id,
        "expires_at": conn.expires_at.isoformat() if conn.expires_at else None
    }
