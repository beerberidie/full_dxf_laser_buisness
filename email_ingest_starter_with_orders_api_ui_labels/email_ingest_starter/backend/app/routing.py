
from sqlalchemy.orm import Session
from .models import RoutingRule

def route_for_recipients(db: Session, recipients: list[str]) -> str | None:
    # Simple local-part matching by pattern substring
    if not recipients:
        return None
    rules = db.query(RoutingRule).filter(RoutingRule.enabled==True).all()
    lower_recipients = [r.lower() for r in recipients if r]
    for rl in rules:
        p = rl.pattern.lower()
        if any(p in r for r in lower_recipients):
            return rl.label
    # defaults
    if any("ops@" in r for r in lower_recipients): return "ops"
    if any("sales@" in r for r in lower_recipients): return "sales"
    if any("quotes@" in r for r in lower_recipients): return "quotes"
    return None
