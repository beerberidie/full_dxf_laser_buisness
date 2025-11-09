from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    model: str = Field(default="gpt-4.1-mini")
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: Dict[str, Any]

class EmbedReq(BaseModel):
    texts: List[str]
    model: Optional[str] = None

class EmbedRes(BaseModel):
    vectors: List[List[float]]
