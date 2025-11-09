from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)

class Mailbox(Base):
    __tablename__ = "mailboxes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String, nullable=False)  # 'gmail' | 'm365'
    address = Column(String, nullable=False)
    provider_account_id = Column(String, nullable=True)

    access_token_enc = Column(Text, nullable=True)
    refresh_token_enc = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    status = Column(String, default="connected")
    last_seen_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="mailboxes")
    subscriptions = relationship("Subscription", backref="mailbox")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    provider = Column(String, nullable=False)
    sub_id = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String, default="active")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    email_id = Column(Integer, ForeignKey("emails.id"))
    client_name = Column(String, nullable=True)
    po_number = Column(String, nullable=True)
    due_date = Column(String, nullable=True)  # ISO date
    route_label = Column(String, nullable=True)  # ops|sales|quotes
    created_at = Column(DateTime, server_default=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    description = Column(Text, nullable=False)
    quantity = Column(Integer, default=1)
    material = Column(String, nullable=True)
    thickness = Column(String, nullable=True)

class OutboundDraft(Base):
    __tablename__ = "outbound_drafts"
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    provider = Column(String, nullable=False)  # gmail|m365
    provider_draft_id = Column(String, nullable=True)  # Gmail draft.id or Graph message.id
    to_email = Column(String, nullable=True)
    subject = Column(Text, nullable=True)
    status = Column(String, default="draft")  # draft|sent|failed
    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class RoutingRule(Base):
    __tablename__ = "routing_rules"
    id = Column(Integer, primary_key=True)
    pattern = Column(String, nullable=False)   # e.g., 'ops@', 'sales@', 'quotes@'
    label = Column(String, nullable=False)     # ops|sales|quotes
    enabled = Column(Boolean, default=True)

class Email(Base):

    __tablename__ = "emails"
    id = Column(Integer, primary_key=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    provider_msg_id = Column(String, nullable=False)
    thread_key = Column(String, nullable=True)

    from_addr = Column(String, nullable=True)
    to_addrs = Column(Text, nullable=True)
    cc_addrs = Column(Text, nullable=True)
    subject = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    html = Column(Text, nullable=True)
    received_at = Column(DateTime, server_default=func.now())
    raw_json = Column(Text, nullable=True)

    mailbox = relationship("Mailbox", backref="emails")

class AIInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    classification = Column(String, nullable=True)
    intents_json = Column(Text, nullable=True)
    entities_json = Column(Text, nullable=True)
    actions_json = Column(Text, nullable=True)
    confidence = Column(String, nullable=True)

    email = relationship("Email", backref="ai_insight")
