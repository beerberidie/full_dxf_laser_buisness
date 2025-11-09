
import datetime as dt
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import Subscription, Mailbox
from .providers.m365 import renew_m365_subscription, ensure_m365_subscription
from .providers.gmail import ensure_gmail_watch

EXPIRY_BUFFER_HOURS = 12  # renew if expiring within this window

def renew_everything_job():
    db: Session = SessionLocal()
    try:
        # Microsoft 365: renew or create
        subs = db.query(Subscription).filter(Subscription.provider=="m365").all()
        now = dt.datetime.utcnow()
        for s in subs:
            if not s.expires_at or (s.expires_at - now).total_seconds() < EXPIRY_BUFFER_HOURS*3600:
                try:
                    renew_m365_subscription(db, s.id)
                except Exception as e:
                    print("[renew m365] failed:", e)

        # Also ensure every M365 mailbox has at least one active subscription
        mbs = db.query(Mailbox).filter(Mailbox.provider=="m365").all()
        for mb in mbs:
            # if no active sub, create one
            active = [s for s in mb.subscriptions if s.status=="active"]
            if not active:
                try:
                    import asyncio
                    asyncio.get_event_loop().create_task(ensure_m365_subscription(db, mb.id))
                except Exception as e:
                    print("[ensure m365] failed:", e)

        # Gmail: simply ensure watch called (idempotent if already active)
        for mb in db.query(Mailbox).filter(Mailbox.provider=="gmail").all():
            try:
                ensure_gmail_watch(db, mb.id)
            except Exception as e:
                print("[ensure gmail watch] failed:", e)

    finally:
        db.close()
