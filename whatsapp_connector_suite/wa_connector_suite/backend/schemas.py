from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class SendText(BaseModel):
    to: str
    type: str = Field(default="text")
    text: Dict[str, Any]

class SendMedia(BaseModel):
    to: str
    type: str
    link: Optional[str] = None
    id: Optional[str] = None
    caption: Optional[str] = None

class SendTemplate(BaseModel):
    to: str
    template_name: str
    language_code: str = "en_US"
    components: Optional[list] = None

class MessageOut(BaseModel):
    id: int
    wa_message_id: Optional[str]
    direction: str
    type: str
    status: str
    body: Optional[str]
    created_at: str
    contact_wa_id: Optional[str]
    contact_name: Optional[str]
    class Config:
        from_attributes = True

class ContactOut(BaseModel):
    wa_id: str
    display_name: Optional[str]
