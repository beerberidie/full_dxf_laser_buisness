import base64, json, datetime as dt, httpx
from typing import Callable, Any, Dict, List
from sqlalchemy.orm import Session
from ..models import Mailbox, Email
from ..security import dec
from ..config import GMAIL_PUBSUB_TOPIC
from ..email_normalizer import NormalizedEmail, normalize_gmail_message

def start_gmail_watch(db: Session, mailbox_id: int):
    mb = db.query(Mailbox).get(mailbox_id)
    if not mb or mb.provider != "gmail":
        return {"error": "Mailbox not found or not gmail"}
    access_token = dec(mb.access_token_enc)
    body = {"topicName": GMAIL_PUBSUB_TOPIC}
    r = httpx.post("https://gmail.googleapis.com/gmail/v1/users/me/watch",
                   headers={"Authorization": f"Bearer {access_token}"}, json=body)
    return r.json()

def ensure_gmail_watch(db: Session, mailbox_id: int):
    # simplistic: call watch; in production track historyId and re-watch on errors/expiration
    start_gmail_watch(db, mailbox_id)

async def gmail_webhook_handler(body: Dict[str, Any], background, db: Session, analyzer: Callable):
    # Pub/Sub message container
    msg = body.get("message", {})
    data_b64 = msg.get("data")
    if not data_b64:
        return
    data = json.loads(base64.b64decode(data_b64).decode())
    # Contains historyId and email address
    # Minimal: directly list latest messages (for demo)
    email_address = data.get("emailAddress")
    mb = db.query(Mailbox).filter(Mailbox.provider=="gmail", Mailbox.address==email_address).first()
    if not mb:
        return
    access_token = dec(mb.access_token_enc)

    # Fetch last 5 messages (demo-friendly). In production use users.history.list with historyId.
    async with httpx.AsyncClient() as hc:
        r = await hc.get("https://gmail.googleapis.com/gmail/v1/users/me/messages",
                         headers={"Authorization": f"Bearer {access_token}"}, params={"maxResults": 5})
        lst = r.json().get("messages", [])
        for m in lst:
            mg = await hc.get(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}",
                              headers={"Authorization": f"Bearer {access_token}"}, params={"format":"full"})
            mj = mg.json()
            norm = normalize_gmail_message(mj)
            background.add_task(analyzer, db, norm)

def discover_gmail_address(access_token: str) -> str:
    # helper to get the gmail address; not used in this demo path
    return ""


def build_mime_reply(to_email: str, subject: str, in_reply_to: str, body_html: str):
    from email.mime.text import MIMEText
    import email.utils
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject
    msg = MIMEText(body_html, "html")
    msg["To"] = to_email
    msg["Subject"] = subject
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to
    msg["Date"] = email.utils.formatdate(localtime=True)
    return msg

def create_gmail_draft(access_token: str, to_email: str, subject: str, in_reply_to: str, body_html: str):
    mime = build_mime_reply(to_email, subject, in_reply_to, body_html)
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    import httpx
    r = httpx.post("https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                   headers={"Authorization": f"Bearer {access_token}",
                            "Content-Type":"application/json"},
                   json={"message":{"raw": raw}})
    return r.json()


def _gmail_find_label_id(access_token: str, name: str):
    import httpx
    r = httpx.get("https://gmail.googleapis.com/gmail/v1/users/me/labels",
                  headers={"Authorization": f"Bearer {access_token}"})
    if r.status_code != 200:
        return None
    for lb in r.json().get("labels", []):
        if lb.get("name","").lower() == name.lower():
            return lb.get("id")
    return None

def _gmail_ensure_label(access_token: str, name: str):
    lid = _gmail_find_label_id(access_token, name)
    if lid:
        return lid
    import httpx
    r = httpx.post("https://gmail.googleapis.com/gmail/v1/users/me/labels",
                   headers={"Authorization": f"Bearer {access_token}", "Content-Type":"application/json"},
                   json={"name": name, "labelListVisibility":"labelShow", "messageListVisibility":"show"})
    if r.status_code >= 300:
        return None
    return r.json().get("id")

def gmail_apply_label(access_token: str, message_id: str, label_name: str):
    lid = _gmail_ensure_label(access_token, label_name)
    if not lid:
        return {"error":"label ensure failed"}
    import httpx
    r = httpx.post(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify",
                   headers={"Authorization": f"Bearer {access_token}", "Content-Type":"application/json"},
                   json={"addLabelIds":[lid]})
    try:
        return r.json()
    except Exception:
        return {"status": r.status_code}
