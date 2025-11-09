from fastapi import FastAPI, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .db import init_db, SessionLocal
from sqlalchemy.orm import Session
from . import models
from .config import PUBLIC_WEBHOOK_BASE
from .providers.gmail import gmail_webhook_handler, start_gmail_watch
from .providers.m365 import m365_webhook_handler, ensure_m365_subscription
from .oauth.google import gmail_oauth_routes
from .oauth.microsoft import m365_oauth_routes
from .ai.engine import analyze_email_and_dispatch
from .email_normalizer import NormalizedEmail
import asyncio
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .scheduler import renew_everything_job
scheduler = AsyncIOScheduler()


app = FastAPI(title="Email Ingest Starter")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    init_db()

# start APScheduler for renewals
try:
    scheduler.add_job(renew_everything_job, IntervalTrigger(minutes=30))
    scheduler.start()
except Exception as e:
    print("[scheduler] start failed:", e)

# Mount OAuth routes
app.include_router(gmail_oauth_routes, prefix="")
app.include_router(m365_oauth_routes, prefix="")

# Health
@app.get("/healthz")
def health():
    return {"ok": True}

# List connected mailboxes
@app.get("/mailboxes")
def list_mailboxes(db: Session = Depends(get_db)):
    mailboxes = db.query(models.Mailbox).all()
    return [{"id": mb.id, "provider": mb.provider, "address": mb.address, "status": mb.status} for mb in mailboxes]

# Serve connected.html for OAuth callback success page
@app.get("/connected.html")
def connected_page():
    connected_file = Path(__file__).parent.parent / "connected.html"
    if connected_file.exists():
        return FileResponse(connected_file)
    return {"message": "✅ Mailbox connected! You can close this tab and return to the app."}

# Manual: start Gmail watch for a mailbox id
@app.post("/gmail/watch/{mailbox_id}")
def gmail_watch(mailbox_id: int, db: Session = Depends(get_db)):
    return start_gmail_watch(db, mailbox_id)

# Manual: fetch and process recent Gmail messages (for testing without webhooks)
@app.post("/gmail/fetch/{mailbox_id}")
async def gmail_fetch_messages(mailbox_id: int, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually fetch and process recent Gmail messages for testing"""
    from .security import dec
    import httpx
    from .email_normalizer import normalize_gmail_message

    mb = db.query(models.Mailbox).get(mailbox_id)
    if not mb or mb.provider != "gmail":
        raise HTTPException(404, "Gmail mailbox not found")

    access_token = dec(mb.access_token_enc)

    # Fetch last 10 messages
    async with httpx.AsyncClient() as hc:
        r = await hc.get("https://gmail.googleapis.com/gmail/v1/users/me/messages",
                        headers={"Authorization": f"Bearer {access_token}"},
                        params={"maxResults": 10})
        if r.status_code != 200:
            raise HTTPException(400, f"Gmail API error: {r.text}")

        lst = r.json().get("messages", [])
        processed = []

        for m in lst:
            # Check if we already processed this message
            existing = db.query(models.Email).filter(
                models.Email.mailbox_id == mailbox_id,
                models.Email.provider_msg_id == m['id']
            ).first()

            if existing:
                continue  # Skip already processed messages

            # Fetch full message
            mg = await hc.get(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}",
                            headers={"Authorization": f"Bearer {access_token}"},
                            params={"format": "full"})
            if mg.status_code == 200:
                mj = mg.json()
                norm = normalize_gmail_message(mj)

                # Process in background
                background.add_task(analyze_email_and_dispatch, db, norm)
                processed.append(m['id'])

    return {"ok": True, "fetched": len(lst), "processed": len(processed), "message_ids": processed}

# Gmail webhook (Pub/Sub push)
@app.post("/gmail/webhook")
async def gmail_webhook(request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    body = await request.json()
    await gmail_webhook_handler(body, background, db, analyze_email_and_dispatch)
    return PlainTextResponse("ok")

# M365 webhook
@app.post("/m365/webhook")
async def m365_webhook(request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    # Graph validation ping (GET) is not used here, only POST notifications
    body = await request.json()
    await m365_webhook_handler(body, background, db, analyze_email_and_dispatch)
    return PlainTextResponse("ok")

# Debug endpoint to process a normalized email (for tests)
@app.post("/mail/process")
async def process_mail(normalized: NormalizedEmail, db: Session = Depends(get_db)):
    await analyze_email_and_dispatch(db, normalized)
    return {"ok": True}


from .models import OutboundDraft, Email, Mailbox, RoutingRule
from .security import dec
import httpx, json

@app.post("/emails/{email_id}/approve_send")
async def approve_send(email_id: int, db: Session = Depends(get_db)):
    od = db.query(OutboundDraft).filter(OutboundDraft.email_id==email_id, OutboundDraft.status=="draft").order_by(OutboundDraft.id.desc()).first()
    if not od:
        raise HTTPException(404, "No draft found to send")
    mb = db.query(Mailbox).get(od.mailbox_id)
    if not mb:
        raise HTTPException(404, "Mailbox not found")
    access_token = dec(mb.access_token_enc)

    if od.provider == "gmail":
        # Send existing draft if ID present; else send raw message
        did = od.provider_draft_id
        if did:
            r = httpx.post("https://gmail.googleapis.com/gmail/v1/users/me/drafts/send",
                           headers={"Authorization": f"Bearer {access_token}", "Content-Type":"application/json"},
                           json={"id": did})
        else:
            # fallback: create and send message (not implemented here for brevity)
            return {"error":"draft id missing"}
        if r.status_code >= 300:
            od.status = "failed"; db.add(od); db.commit()
            raise HTTPException(400, f"Gmail send failed: {r.text}")
        od.status = "sent"; db.add(od); db.commit()
        return {"ok": True}

    elif od.provider == "m365":
        did = od.provider_draft_id
        if not did:
            return {"error":"draft id missing"}
        r = httpx.post(f"https://graph.microsoft.com/v1.0/me/messages/{did}/send",
                       headers={"Authorization": f"Bearer {access_token}"})
        if r.status_code >= 300:
            od.status = "failed"; db.add(od); db.commit()
            raise HTTPException(400, f"Graph send failed: {r.text}")
        od.status = "sent"; db.add(od); db.commit()
        return {"ok": True}

    else:
        raise HTTPException(400, "Unknown provider")

@app.get("/routing_rules")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(RoutingRule).all()
    return [{"id":r.id, "pattern":r.pattern, "label":r.label, "enabled":r.enabled} for r in rules]

@app.post("/routing_rules")
def add_rule(rule: dict, db: Session = Depends(get_db)):
    r = RoutingRule(pattern=rule.get("pattern",""), label=rule.get("label","ops"), enabled=True)
    db.add(r); db.commit(); db.refresh(r)
    return {"id": r.id}

@app.delete("/routing_rules/{rid}")
def del_rule(rid: int, db: Session = Depends(get_db)):
    r = db.query(RoutingRule).get(rid)
    if not r:
        raise HTTPException(404, "not found")
    db.delete(r); db.commit()
    return {"ok": True}


from .models import Order, OrderItem, OutboundDraft

@app.get("/orders")
def list_orders(db: Session = Depends(get_db), limit: int = 50):
    q = db.query(Order).order_by(Order.id.desc()).limit(limit).all()
    out = []
    for o in q:
        items = db.query(OrderItem).filter(OrderItem.order_id==o.id).all()
        draft = db.query(OutboundDraft).filter(OutboundDraft.email_id==o.email_id).order_by(OutboundDraft.id.desc()).first()
        out.append({
            "id": o.id,
            "email_id": o.email_id,
            "mailbox_id": o.mailbox_id,
            "client_name": o.client_name,
            "po_number": o.po_number,
            "due_date": o.due_date,
            "route_label": o.route_label,
            "items": [{"id":it.id,"description":it.description,"quantity":it.quantity,"material":it.material,"thickness":it.thickness} for it in items],
            "draft_status": draft.status if draft else None
        })
    return out

@app.get("/orders/{oid}")
def get_order(oid: int, db: Session = Depends(get_db)):
    o = db.query(Order).get(oid)
    if not o:
        raise HTTPException(404, "not found")
    items = db.query(OrderItem).filter(OrderItem.order_id==o.id).all()
    return {
        "id": o.id, "email_id": o.email_id, "mailbox_id": o.mailbox_id,
        "client_name": o.client_name, "po_number": o.po_number, "due_date": o.due_date,
        "route_label": o.route_label,
        "items": [{"id":it.id,"description":it.description,"quantity":it.quantity,"material":it.material,"thickness":it.thickness} for it in items],
    }
