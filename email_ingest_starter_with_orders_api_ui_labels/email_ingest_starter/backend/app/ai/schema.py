from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional

class Action(BaseModel):
    type: str
    data: Dict[str, Any] = {}

class AIResult(BaseModel):
    version: str = "1.0"
    summary: str
    classification: str  # order_request | quote | support | spam | personal | unknown
    intents: List[str] = []
    entities: Dict[str, Any] = {}
    actions: List[Action] = []
    confidence: Optional[float] = 0.7

SCHEMA_EXAMPLE = {
  "version": "1.0",
  "summary": "New order from ACME",
  "classification": "order_request",
  "intents": ["create_order"],
  "entities": {
    "client_name": "ACME Ltd",
    "po_number": "PO-12345",
    "due_date": "2025-10-22",
    "items": [{"desc":"MS plate 3mm", "qty":4}]
  },
  "actions": [
    {"type":"UPSERT_CONTACT","data":{"name":"ACME Ltd","email":"ops@acme.com"}},
    {"type":"CREATE_ORDER","data":{"items":[{"desc":"MS plate 3mm","qty":4}]}},
    {"type":"DRAFT_REPLY","data":{"tone":"professional","key_points":["Quote ETA 24h","Need DXF"]}}
  ]
}
