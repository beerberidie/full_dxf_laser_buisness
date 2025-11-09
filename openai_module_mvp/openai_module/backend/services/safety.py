import re
from typing import Sequence, Dict, Any

PII_REGEX = re.compile(r"\b(\d{13}|\+?\d{10,})\b")

def redact(text: str) -> str:
    return PII_REGEX.sub("[REDACTED]", text)

def guard_text(messages: Sequence[Dict[str, Any]]):
    for m in messages:
        if isinstance(m.get("content"), str):
            m["content"] = redact(m["content"])
