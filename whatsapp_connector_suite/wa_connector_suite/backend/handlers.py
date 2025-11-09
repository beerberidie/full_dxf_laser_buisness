from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from models import Contact, Message, Media

def upsert_contact(db: Session, wa_id: str, display_name: Optional[str]) -> Contact:
    c = db.query(Contact).filter(Contact.wa_id == wa_id).one_or_none()
    if not c:
        c = Contact(wa_id=wa_id, display_name=display_name)
        db.add(c)
        db.commit()
        db.refresh(c)
    elif display_name and c.display_name != display_name:
        c.display_name = display_name
        db.commit()
    return c

def record_incoming_message(db: Session, wa_message_id: str, contact: Contact, type_: str, body: str, raw: Dict[str, Any]) -> Message:
    m = Message(wa_message_id=wa_message_id, direction="in", type=type_, body=body, raw=raw, contact=contact, status="received")
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def record_outgoing_message(db: Session, wa_message_id: str, to_contact: Contact, type_: str, body: str, raw: Dict[str, Any]) -> Message:
    m = Message(wa_message_id=wa_message_id, direction="out", type=type_, body=body, raw=raw, contact=to_contact, status="sent")
    db.add(m)
    db.commit()
    db.refresh(m)
    return m
