import os, httpx, json, datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Mailbox, Subscription
from ..security import enc, dec
from ..config import MS_CLIENT_ID, MS_TENANT_ID, MS_REDIRECT_URI, PUBLIC_WEBHOOK_BASE
from ..utils import pkce_pair, now_utc

m365_oauth_routes = APIRouter()
_STATE = {}
_VERIFIER = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@m365_oauth_routes.get("/auth/m365/start")
def m365_start():
    if not MS_CLIENT_ID:
        raise HTTPException(500, "MS_CLIENT_ID not set")
    verifier, challenge = pkce_pair()
    state = os.urandom(16).hex()
    _STATE[state] = True
    _VERIFIER[state] = verifier

    params = {
        "client_id": MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": MS_REDIRECT_URI,
        "response_mode": "query",
        "scope": "offline_access Mail.Read Mail.Send openid profile email",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    qs = "&".join(f"{k}={httpx.QueryParams({k:v})[k]}" for k,v in params.items())
    return RedirectResponse(f"https://login.microsoftonline.com/{MS_TENANT_ID}/oauth2/v2.0/authorize?{qs}")

@m365_oauth_routes.get("/auth/m365/callback")
async def m365_callback(code: str, state: str, db: Session = Depends(get_db)):
    if state not in _STATE:
        raise HTTPException(400, "Bad state")
    verifier = _VERIFIER[state]

    token_url = f"https://login.microsoftonline.com/{MS_TENANT_ID}/oauth2/v2.0/token"
    async with httpx.AsyncClient() as hc:
        r = await hc.post(token_url, data={
            "client_id": MS_CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": MS_REDIRECT_URI,
            "code_verifier": verifier,
        })
    if r.status_code != 200:
        raise HTTPException(400, f"Token exchange failed: {r.text}")
    tok = r.json()

    # Get profile & mailbox address
    async with httpx.AsyncClient() as hc:
        me = await hc.get("https://graph.microsoft.com/v1.0/me",
                          headers={"Authorization": f"Bearer {tok['access_token']}"})
    if me.status_code != 200:
        raise HTTPException(400, f"Graph /me failed: {me.text}")
    mej = me.json()
    address = mej.get("mail") or mej.get("userPrincipalName")

    from ..models import Mailbox
    mb = Mailbox(
        user_id=None, provider="m365", address=address,
        provider_account_id=mej.get("id"),
        access_token_enc=enc(tok["access_token"]),
        refresh_token_enc=enc(tok.get("refresh_token","")),
        status="connected"
    )
    db.add(mb)
    db.commit()
    db.refresh(mb)

    # Create initial subscription
    await ensure_m365_subscription(db, mb.id)

    return RedirectResponse("/connected.html")
