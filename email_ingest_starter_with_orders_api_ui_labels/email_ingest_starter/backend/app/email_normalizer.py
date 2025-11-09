from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import base64

class Address(BaseModel):
    name: Optional[str] = ""
    email: str

class Attachment(BaseModel):
    filename: str
    mime: str
    size: int = 0
    downloadRef: str = ""  # provider-specific

class NormalizedEmail(BaseModel):
    provider: str
    provider_msg_id: str
    thread_key: Optional[str] = None
    from_: Address = Field(..., alias="from")
    to: List[Address] = []
    cc: List[Address] = []
    subject: str = ""
    text: str = ""
    html: str = ""
    attachments: List[Attachment] = []
    received_at: Optional[str] = None
    raw: Dict[str, Any] = {}

def _header(headers, name):
    for h in headers:
        if h.get("name","").lower() == name.lower():
            return h.get("value","")
    return ""

def normalize_gmail_message(m: dict) -> NormalizedEmail:
    headers = m.get("payload",{}).get("headers",[])
    msg_id = _header(headers, "Message-Id") or m.get("id","")
    thread_key = _header(headers, "In-Reply-To") or _header(headers, "References") or m.get("threadId","")

    subject = _header(headers, "Subject") or ""
    from_v = _header(headers, "From") or ""
    to_v = _header(headers, "To") or ""
    cc_v = _header(headers, "Cc") or ""

    def parse_addr(s):
        import email.utils
        name, addr = email.utils.parseaddr(s)
        return {"name": name or "", "email": addr or s}

    text = ""
    html = ""
    payload = m.get("payload", {})
    stack = [payload]
    while stack:
        p = stack.pop()
        mime = p.get("mimeType","")
        body = p.get("body",{})
        data = body.get("data")
        if data:
            content = base64.urlsafe_b64decode(data.encode()).decode(errors="ignore")
            if mime.startswith("text/plain"):
                text += content + "\n"
            elif mime.startswith("text/html"):
                html += content
        for part in p.get("parts",[]) or []:
            stack.append(part)

    return NormalizedEmail(
        provider="gmail",
        provider_msg_id=m.get("id",""),
        thread_key=thread_key,
        **{"from": parse_addr(from_v)},
        to=[parse_addr(x.strip()) for x in to_v.split(",") if x.strip()],
        cc=[parse_addr(x.strip()) for x in cc_v.split(",") if x.strip()],
        subject=subject,
        text=text.strip(),
        html=html.strip(),
        attachments=[],  # left for exercise
        received_at=None,
        raw=m
    )

def normalize_m365_message(m: dict) -> NormalizedEmail:
    def to_addr(obj):
        if not obj:
            return None
        return {"name": obj.get("emailAddress",{}).get("name",""),
                "email": obj.get("emailAddress",{}).get("address","")}

    to_list = [to_addr(x) for x in m.get("toRecipients",[]) if to_addr(x)]
    cc_list = [to_addr(x) for x in m.get("ccRecipients",[]) if to_addr(x)]
    from_addr = to_addr(m.get("from"))
    body = m.get("body",{})
    content_type = body.get("contentType","Text")
    content = body.get("content","") or ""
    text = content if content_type == "Text" else ""
    html = content if content_type == "HTML" else ""

    return NormalizedEmail(
        provider="m365",
        provider_msg_id=m.get("id",""),
        thread_key=m.get("conversationId",""),
        **{"from": from_addr},
        to=to_list,
        cc=cc_list,
        subject=m.get("subject",""),
        text=text.strip(),
        html=html.strip(),
        attachments=[],
        received_at=m.get("receivedDateTime",""),
        raw=m
    )
