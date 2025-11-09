from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTasks
from typing import List, Optional
import json
from config import settings
from db import init_db, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, desc
from security import verify_xhub_signature
from graph import WhatsAppGraphClient
from schemas import SendText, SendMedia, SendTemplate, MessageOut, ContactOut
from handlers import upsert_contact, record_incoming_message, record_outgoing_message
from models import Message, Contact

app = FastAPI(title="WhatsApp Connector", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_start():
    init_db()

@app.get("/health")
def health():
    return {"ok": True, "version": app.version}

@app.get("/whatsapp/webhook", response_class=PlainTextResponse)
def verify(mode: str = "", challenge: str = "", verify_token: str = ""):
    if mode == "subscribe" and verify_token == settings.verify_token:
        return challenge or "OK"
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/whatsapp/webhook")
async def webhook(request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_xhub_signature(settings.app_secret, body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body.decode("utf-8"))
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", [])
            messages = value.get("messages", [])
            contact_name = (contacts[0].get("profile", {}).get("name") if contacts else None)
            wa_id = (contacts[0].get("wa_id") if contacts else (messages[0].get("from") if messages else None))
            if not wa_id:
                continue
            contact = upsert_contact(db, wa_id=wa_id, display_name=contact_name)

            for msg in messages:
                msg_id = msg.get("id")
                mtype = msg.get("type", "text")
                body_txt = ""
                if mtype == "text":
                    body_txt = msg.get("text", {}).get("body", "")
                elif mtype in {"image","document","audio","video","sticker"}:
                    body_txt = msg.get(mtype, {}).get("id") or msg.get(mtype, {}).get("link") or ""
                else:
                    body_txt = json.dumps(msg)
                record_incoming_message(db, wa_message_id=msg_id, contact=contact, type_=mtype, body=body_txt, raw=msg)
    return JSONResponse({"received": True})

def send_text_reply(to: str, text: str):
    client = WhatsAppGraphClient()
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    client.send(payload)

@app.post("/whatsapp/send")
def send_text(msg: SendText, db: Session = Depends(get_db)):
    client = WhatsAppGraphClient()
    payload = {"messaging_product": "whatsapp", "to": msg.to, "type": "text", "text": msg.text}
    resp = client.send(payload)
    contact = upsert_contact(db, wa_id=msg.to, display_name=None)
    wa_message_id = (resp.get("messages") or [{}])[0].get("id")
    record_outgoing_message(db, wa_message_id=wa_message_id, to_contact=contact, type_="text", body=msg.text.get("body",""), raw=resp)
    return resp

@app.post("/whatsapp/send-media")
def send_media(msg: SendMedia, db: Session = Depends(get_db)):
    client = WhatsAppGraphClient()
    obj = {k:v for k,v in {"id": msg.id, "link": msg.link, "caption": msg.caption}.items() if v is not None}
    payload = {"messaging_product": "whatsapp", "to": msg.to, "type": msg.type, msg.type: obj}
    resp = client.send(payload)
    contact = upsert_contact(db, wa_id=msg.to, display_name=None)
    wa_message_id = (resp.get("messages") or [{}])[0].get("id")
    record_outgoing_message(db, wa_message_id=wa_message_id, to_contact=contact, type_=msg.type, body=json.dumps(obj), raw=resp)
    return resp

@app.post("/whatsapp/send-template")
def send_template(msg: SendTemplate, db: Session = Depends(get_db)):
    client = WhatsAppGraphClient()
    payload = {"messaging_product": "whatsapp", "to": msg.to, "type": "template", "template": {"name": msg.template_name, "language": {"code": msg.language_code}, "components": msg.components or []}}
    resp = client.send(payload)
    contact = upsert_contact(db, wa_id=msg.to, display_name=None)
    wa_message_id = (resp.get("messages") or [{}])[0].get("id")
    record_outgoing_message(db, wa_message_id=wa_message_id, to_contact=contact, type_="template", body=json.dumps(payload["template"]), raw=resp)
    return resp

@app.get("/messages", response_model=List[MessageOut])
def list_messages(db: Session = Depends(get_db), limit: int = Query(50, ge=1, le=500), direction: str = Query("all"), search: Optional[str] = None):
    q = select(Message, Contact).join(Contact, Message.contact_id == Contact.id).order_by(desc(Message.created_at)).limit(limit)
    if direction in ("in", "out"):
        q = q.where(Message.direction == direction)
    if search:
        like = f"%{search}%"
        q = q.where(or_(Message.body.ilike(like), Contact.wa_id.ilike(like), Contact.display_name.ilike(like)))
    rows = db.execute(q).all()
    out = []
    for m, c in rows:
        out.append({
            "id": m.id,
            "wa_message_id": m.wa_message_id,
            "direction": m.direction,
            "type": m.type,
            "status": m.status,
            "body": m.body,
            "created_at": m.created_at.isoformat()+"Z",
            "contact_wa_id": c.wa_id if c else None,
            "contact_name": c.display_name if c else None,
        })
    return out

@app.get("/contacts", response_model=List[ContactOut])
def list_contacts(db: Session = Depends(get_db), search: Optional[str] = None, limit: int = Query(100, ge=1, le=1000)):
    q = select(Contact).order_by(desc(Contact.created_at)).limit(limit)
    if search:
        like = f"%{search}%"
        q = q.where(or_(Contact.wa_id.ilike(like), Contact.display_name.ilike(like)))
    rows = db.execute(q).scalars().all()
    return [{"wa_id": c.wa_id, "display_name": c.display_name} for c in rows]
