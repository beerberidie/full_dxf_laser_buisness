import json
from fastapi import APIRouter, Depends
from ..deps import get_provider, settings
from ..models.schemas import ChatRequest

router = APIRouter(prefix="/ai", tags=["ai"])

TOOLS = [{
  "type": "function",
  "function": {
    "name": "lookup_order",
    "description": "Fetch order by ID",
    "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}
  }
}]

def db_lookup(args_json: str):
    try:
        args = json.loads(args_json)
    except Exception:
        args = {}
    order_id = args.get("order_id", "UNKNOWN")
    return {"order_id": order_id, "status": "stubbed", "items": []}

@router.post("/chat-with-tools")
async def chat_with_tools(req: ChatRequest, provider=Depends(get_provider)):
    resp = provider.chat(messages=req.messages, model=req.model or settings.default_model, tools=TOOLS)
    msg = resp.choices[0].message
    tool_calls = getattr(msg, "tool_calls", None)
    if tool_calls:
        results = []
        for call in tool_calls:
            if call.function.name == "lookup_order":
                payload = json.dumps(db_lookup(call.function.arguments))
                results.append({"role":"tool","tool_call_id":call.id,"name":"lookup_order","content": payload})
        final = provider.chat(messages=req.messages + [msg] + results, model=req.model or settings.default_model)
        return final
    return resp
