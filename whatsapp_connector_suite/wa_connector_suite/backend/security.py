import hmac, hashlib
from typing import Optional

def verify_xhub_signature(app_secret: str, body: bytes, signature_header: Optional[str]) -> bool:
    if not app_secret or not signature_header:
        return True
    try:
        algo, sig = signature_header.split("=", 1)
        if algo != "sha256":
            return False
        mac = hmac.new(app_secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
        expected = mac.hexdigest()
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False
