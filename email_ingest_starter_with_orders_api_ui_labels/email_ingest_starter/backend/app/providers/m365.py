import json, httpx, datetime as dt, secrets
from typing import Callable, Any, Dict
from sqlalchemy.orm import Session
from ..models import Mailbox, Subscription
from ..security import dec
from ..config import PUBLIC_WEBHOOK_BASE
from ..email_normalizer import normalize_m365_message

async def ensure_m365_subscription(db: Session, mailbox_id: int):
    mb = db.query(Mailbox).get(mailbox_id)
    access_token = dec(mb.access_token_enc)
    client_state = secrets.token_urlsafe(16)
    body = {
        "changeType": "created",
        "notificationUrl": f"{PUBLIC_WEBHOOK_BASE}/m365/webhook",
        "resource": "/me/messages",
        "expirationDateTime": (dt.datetime.utcnow() + dt.timedelta(hours=48)).isoformat()+"Z",
        "clientState": client_state,
    }
    async with httpx.AsyncClient() as hc:
        r = await hc.post("https://graph.microsoft.com/v1.0/subscriptions",
                          headers={"Authorization": f"Bearer {access_token}", "Content-Type":"application/json"},
                          json=body)
    if r.status_code >= 300:
        return {"error": r.text}
    sub = r.json()
    s = Subscription(mailbox_id=mailbox_id, provider="m365", sub_id=sub["id"],
                     resource=sub["resource"], expires_at=dt.datetime.fromisoformat(sub["expirationDateTime"].replace("Z","")), status="active")
    db.add(s); db.commit()
    return sub

async def m365_webhook_handler(body: Dict[str, Any], background, db: Session, analyzer: Callable):
    # For each notification, fetch the message and normalize
    for value in body.get("value", []):
        sub_id = value.get("subscriptionId")
        # Find mailbox by subscription
        sub = db.query(Subscription).filter(Subscription.provider=="m365", Subscription.sub_id==sub_id).first()
        if not sub:
            continue
        mb = sub.mailbox
        access_token = dec(mb.access_token_enc)
        msg_id = value.get("resourceData",{}).get("id")
        if not msg_id:
            continue
        async with httpx.AsyncClient() as hc:
            r = await hc.get(f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}",
                             headers={"Authorization": f"Bearer {access_token}"})
            if r.status_code != 200:
                continue
            mj = r.json()
            norm = normalize_m365_message(mj)
            background.add_task(analyzer, db, norm)


async def renew_m365_subscription(db: Session, subscription_id: int):
    sub = db.query(Subscription).get(subscription_id)
    if not sub:
        return {"error":"subscription not found"}
    mb = sub.mailbox
    access_token = dec(mb.access_token_enc)
    async with httpx.AsyncClient() as hc:
        r = await hc.patch(f"https://graph.microsoft.com/v1.0/subscriptions/{sub.sub_id}",
                           headers={"Authorization": f"Bearer {access_token}",
                                    "Content-Type":"application/json"},
                           json={"expirationDateTime": (dt.datetime.utcnow()+dt.timedelta(hours=48)).isoformat()+"Z"})
    if r.status_code >= 300:
        # try to create new if renew failed
        return await ensure_m365_subscription(db, mb.id)
    data = r.json()
    sub.expires_at = dt.datetime.fromisoformat(data["expirationDateTime"].replace("Z",""))
    db.add(sub); db.commit()
    return {"ok": True}

async def create_draft_reply_m365(access_token: str, original_msg: dict, body_html: str):
    import copy
    # Build a draft reply message
    to = original_msg.get("from",{}).get("emailAddress",{}).get("address")
    subject = original_msg.get("subject","")
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject
    msg = {
        "subject": subject,
        "toRecipients": [{"emailAddress":{"address": to}}] if to else [],
        "body": {"contentType":"HTML", "content": body_html}
    }
    async with httpx.AsyncClient() as hc:
        # Create draft
        dr = await hc.post("https://graph.microsoft.com/v1.0/me/messages",
                           headers={"Authorization": f"Bearer {access_token}",
                                    "Content-Type":"application/json"},
                           json=msg)
    return dr.json()


async def m365_apply_category(access_token: str, message_id: str, category: str):
    # Fetch current categories, then union with new
    async with httpx.AsyncClient() as hc:
        r = await hc.get(f"https://graph.microsoft.com/v1.0/me/messages/{message_id}",
                         headers={"Authorization": f"Bearer {access_token}"})
        if r.status_code != 200:
            return {"error": r.text}
        msg = r.json()
        cats = msg.get("categories", []) or []
        if category not in cats:
            cats.append(category)
        pr = await hc.patch(f"https://graph.microsoft.com/v1.0/me/messages/{message_id}",
                            headers={"Authorization": f"Bearer {access_token}", "Content-Type":"application/json"},
                            json={"categories": cats})
        try:
            return pr.json()
        except Exception:
            return {"status": pr.status_code}
