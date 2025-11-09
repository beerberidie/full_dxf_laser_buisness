import json
from sqlalchemy.orm import Session
from .schema import AIResult, Action
from ..models import Email, AIInsight, Mailbox
from ..routing import route_for_recipients
from ..email_normalizer import NormalizedEmail
from ..actions.dispatcher import run_action

# Plug your LLM call here
async def call_model_to_get_json(normalized: NormalizedEmail) -> AIResult:
    # !!! Replace with your model call (local or API) and enforce schema
    pass

import re
from dateutil import parser as dateparser

PO_PATTERNS = [
    r"\bPO(?:\s*#|\s*No\.?|\s*Number\s*:?|\s*:)\s*([A-Z0-9_\-/]+)\b",
    r"\bPurchase\s*Order\s*[:#]?\s*([A-Z0-9_\-/]+)\b"
]

DUE_PATTERNS = [
    r"\b(?:due|deadline|deliver(?:y| by))\s*(?:on|:)?\s*(.+)$",
]

ITEM_LINE_PATTERNS = [
    r"^(?:-\s*)?(\d+)\s*[xX*]?\s*(.+)$",           # '4 x MS plate 3mm'
    r"^(?:-\s*)?Qty\s*[:=]\s*(\d+)\s*(.+)$",      # 'Qty: 3 Brackets 2mm'
]

def extract_po(text):
    for pat in PO_PATTERNS:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def extract_due(text):
    # Try explicit date on same line after keywords or any parseable date
    lines = text.splitlines()
    for ln in lines:
        for pat in DUE_PATTERNS:
            m = re.search(pat, ln, flags=re.IGNORECASE)
            if m:
                cand = m.group(1).strip().rstrip('. ,;')
                try:
                    dt = dateparser.parse(cand, dayfirst=True, fuzzy=True)
                    return dt.date().isoformat()
                except Exception:
                    pass
    # Fallback: any date-looking token
    try:
        dt = dateparser.parse(text, dayfirst=True, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None

def extract_items(text):
    items = []
    for ln in text.splitlines():
        ln = ln.strip()
        for pat in ITEM_LINE_PATTERNS:
            m = re.match(pat, ln, flags=re.IGNORECASE)
            if m:
                qty = int(m.group(1))
                desc = m.group(2).strip()
                items.append({"desc": desc, "qty": qty})
                break
    return items[:20]

async def call_model_to_get_json(normalized: NormalizedEmail) -> AIResult:
    # Minimal heuristic demo:
    subj = (normalized.subject or "").lower()
    txt = (normalized.text or "").lower()

    classification = "order_request" if any(k in subj or k in txt for k in ["order","po","quote","request","rfq"]) else "unknown"
    actions = []
    po = extract_po(normalized.text + "\n" + (normalized.subject or ""))
    due = extract_due(normalized.text)
    items = extract_items(normalized.text)
    entities = {}
    if po: entities["po_number"] = po
    if due: entities["due_date"] = due
    if items: entities["items"] = items

    if classification == "order_request":
        actions = [Action(type="CREATE_ORDER", data={"source":"email","subject": normalized.subject, "po": po, "items": items}).model_dump(),
                   Action(type="DRAFT_REPLY", data={"html": f"<p>Hi {normalized.from_.name or normalized.from_.email},</p><p>Received your request{(' for PO '+po) if po else ''}. We'll send a quote/ETA shortly.</p>"}).model_dump()]

    res = {
        "version":"1.0",
        "summary": f"Auto-classified: {classification}",
        "classification": classification,
        "intents": ["create_order"] if classification=="order_request" else [],
        "entities": entities,
        "actions": actions,
        "confidence": 0.62
    }
    return AIResult(**res)

async def analyze_email_and_dispatch(db: Session, normalized: NormalizedEmail):
    # Persist email
    e = Email(
        mailbox_id=db.query(Mailbox).filter(Mailbox.provider==normalized.provider).first().id if db.query(Mailbox).filter(Mailbox.provider==normalized.provider).first() else None,
        provider_msg_id=normalized.provider_msg_id,
        thread_key=normalized.thread_key,
        from_addr=normalized.from_.email if normalized.from_ else None,
        to_addrs=json.dumps([x.email for x in normalized.to]),
        cc_addrs=json.dumps([x.email for x in normalized.cc]),
        subject=normalized.subject, text=normalized.text, html=normalized.html,
        raw_json=json.dumps(normalized.raw)[:500000]
    )

    db.add(e); db.commit(); db.refresh(e)
    # assign route label
    try:
        import json as _json
        recipients = _json.loads(e.to_addrs or "[]")
    except Exception:
        recipients = []
    e.route_label = route_for_recipients(db, recipients)
    db.add(e); db.commit()

    # AI
    ai = await call_model_to_get_json(normalized)
    insight = AIInsight(email_id=e.id,
                        classification=ai.classification,
                        intents_json=json.dumps(ai.intents),
                        entities_json=json.dumps(ai.entities),
                        actions_json=json.dumps([a.model_dump() if hasattr(a,'model_dump') else a for a in ai.actions]),
                        confidence=str(ai.confidence))
    db.add(insight); db.commit()

    # Dispatch
    for act in ai.actions:
        await run_action(db, e, act)
