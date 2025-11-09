from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_provider, settings
from ..models.schemas import ChatRequest, ChatResponse
from ..services.safety import guard_text

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, provider=Depends(get_provider)):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages are required")
    guard_text(req.messages)
    resp = provider.chat(
        messages=req.messages,
        model=req.model or settings.default_model,
        tools=req.tools,
        response_format=req.response_format,
        stream=False,
    )
    content = resp.choices[0].message
    return ChatResponse(message=content)

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
from ..deps import get_provider, settings
from ..models.schemas import ChatRequest

router = APIRouter(prefix="/ai", tags=["ai"])

def sse(event: str, data: str) -> bytes:
    return f"event: {event}\ndata: {data}\n\n".encode()

@router.post("/stream")
async def chat_stream(req: ChatRequest, provider=Depends(get_provider)):
    stream = provider.chat(messages=req.messages, model=req.model or settings.default_model, tools=req.tools, stream=True)
    def gen():
        for chunk in stream:
            ch = getattr(chunk, "choices", None)
            if ch and len(ch) and hasattr(ch[0], "delta") and ch[0].delta:
                yield sse("token", json.dumps(ch[0].delta.model_dump()))
        yield sse("done", "{}")
    return StreamingResponse(gen(), media_type="text/event-stream")
