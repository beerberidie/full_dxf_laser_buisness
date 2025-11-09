import base64, hashlib, os, secrets, time

def pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge

def now_utc():
    import datetime as dt
    return dt.datetime.utcnow()

def iso(dt):
    return dt.replace(microsecond=0).isoformat() + "Z"
