import os, httpx, json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Mailbox, User
from ..security import enc, dec
from ..config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GMAIL_PUBSUB_TOPIC
from ..utils import pkce_pair, now_utc
from ..providers.gmail import discover_gmail_address, ensure_gmail_watch

gmail_oauth_routes = APIRouter()

# In production, store verifier/state in a server-side session or cache (redis). Minimal demo here:
_STATE = {}
_VERIFIER = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@gmail_oauth_routes.get("/auth/gmail/start")
def gmail_start():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(500, "GOOGLE_CLIENT_ID not set")
    verifier, challenge = pkce_pair()
    state = os.urandom(16).hex()
    _STATE[state] = True
    _VERIFIER[state] = verifier

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send",
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    qs = "&".join(f"{k}={httpx.QueryParams({k:v})[k]}" for k,v in params.items())
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{qs}")

@gmail_oauth_routes.get("/auth/gmail/callback")
async def gmail_callback(code: str, state: str, db: Session = Depends(get_db)):
    if state not in _STATE:
        raise HTTPException(400, "Bad state")
    verifier = _VERIFIER[state]

    token_url = "https://oauth2.googleapis.com/token"
    async with httpx.AsyncClient() as hc:
        r = await hc.post(token_url, data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI
        })
    if r.status_code != 200:
        raise HTTPException(400, f"Token exchange failed: {r.text}")
    tok = r.json()

    # Fetch userinfo
    async with httpx.AsyncClient() as hc:
        ui = await hc.get("https://www.googleapis.com/oauth2/v3/userinfo",
                          headers={"Authorization": f"Bearer {tok['access_token']}"})
    if ui.status_code != 200:
        raise HTTPException(400, f"userinfo failed: {ui.text}")
    uij = ui.json()
    address = uij.get("email")

    mb = Mailbox(
        user_id=None, provider="gmail", address=address,
        provider_account_id=uij.get("sub"),
        access_token_enc=enc(tok["access_token"]),
        refresh_token_enc=enc(tok.get("refresh_token","")),
        status="connected"
    )
    db.add(mb)
    db.commit()
    db.refresh(mb)

    # Start watch
    ensure_gmail_watch(db, mb.id)

    return RedirectResponse("/connected.html")
