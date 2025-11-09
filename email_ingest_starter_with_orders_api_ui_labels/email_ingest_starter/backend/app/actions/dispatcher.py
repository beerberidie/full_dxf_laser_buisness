
from ..providers.gmail import create_gmail_draft, gmail_apply_label
from ..providers.m365 import create_draft_reply_m365, m365_apply_category
from ..security import dec
from ..models import Mailbox

from ..models import Order, OrderItem, OutboundDraft
from ..routing import route_for_recipients
import re

import httpx

import json, asyncio
from sqlalchemy.orm import Session
from ..models import Email

async def run_action(db: Session, email: Email, action):
    atype = action.type if hasattr(action, "type") else action.get("type")
    data = action.data if hasattr(action, "data") else action.get("data", {})
    if atype == "UPSERT_CONTACT":
        # TODO: implement
        pass
    elif atype == "CREATE_ORDER":
        # Persist order + items
        # Determine route by 'to' recipients of original email
        try:
            import json as _json
            recipients = _json.loads(email.to_addrs or "[]")
        except Exception:
            recipients = []
        route_label = route_for_recipients(db, recipients)
        order = Order(
            mailbox_id=email.mailbox_id,
            email_id=email.id,
            client_name=data.get("client_name"),
            po_number=data.get("po") or data.get("po_number"),
            due_date=data.get("due_date"),
            route_label=route_label
        )
        db.add(order); db.commit(); db.refresh(order)

        # Items
        items = data.get("items") or []
        for it in items:
            desc = it.get("desc") or it.get("description") or ""
            qty = int(it.get("qty") or it.get("quantity") or 1)
            mat, th = _parse_material_thickness(desc)
            oi = OrderItem(order_id=order.id, description=desc, quantity=qty,
                           material=it.get("material") or mat, thickness=it.get("thickness") or th)
            db.add(oi)
        db.commit()

    elif atype == "DRAFT_REPLY":
        # TODO: implement: create draft with provider API
        pass
    else:
        # Unknown action: log
        print(f"[actions] Unknown action: {atype}")
    await asyncio.sleep(0)  # yield


def _parse_material_thickness(desc: str):
    material = None
    thickness = None
    # crude patterns like 'MS plate 3mm', 'SS 1.2mm', 'galv 0.8'
    m = re.search(r'\b(ms|mild steel|ss|stainless|galv|galvanized|alum|aluminium|aluminum)\b', desc, re.I)
    if m:
        material = m.group(1).lower()
    t = re.search(r'(\d+(?:\.\d+)?)\s*mm\b', desc, re.I)
    if t:
        thickness = t.group(1) + "mm"
    return material, thickness
