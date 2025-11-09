import uuid, logging
log = logging.getLogger("ai")

def request_id(headers: dict) -> str:
    return headers.get("X-Request-ID") or uuid.uuid4().hex
