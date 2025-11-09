from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    wa_id = Column(String(64), unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="contact")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    wa_message_id = Column(String(128), unique=True, index=True, nullable=True)
    direction = Column(String(8))
    type = Column(String(32))
    status = Column(String(32), default="received")
    body = Column(Text, nullable=True)
    raw = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    contact = relationship("Contact", back_populates="messages")
    media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    media = relationship("Media")

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    wa_media_id = Column(String(128), index=True)
    mime_type = Column(String(128))
    sha256 = Column(String(128), nullable=True)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
