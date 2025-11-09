from cryptography.fernet import Fernet
from .config import FERNET_KEY

if FERNET_KEY == "CHANGE_ME":
    # WARNING: replace this in production, this is a dev fallback
    _key = Fernet.generate_key()
else:
    _key = FERNET_KEY.encode()

fernet = Fernet(_key)

def enc(s: str) -> str:
    if s is None:
        return ""
    return fernet.encrypt(s.encode()).decode()

def dec(s: str) -> str:
    if not s:
        return ""
    return fernet.decrypt(s.encode()).decode()
