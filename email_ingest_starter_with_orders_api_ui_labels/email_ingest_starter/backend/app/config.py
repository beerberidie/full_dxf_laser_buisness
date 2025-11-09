import os
from dotenv import load_dotenv

load_dotenv()

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
PUBLIC_WEBHOOK_BASE = os.getenv("PUBLIC_WEBHOOK_BASE", APP_BASE_URL)

FERNET_KEY = os.getenv("FERNET_KEY", "CHANGE_ME")

# Google
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", f"{APP_BASE_URL}/auth/gmail/callback")
GMAIL_PUBSUB_VERIFICATION_TOKEN = os.getenv("GMAIL_PUBSUB_VERIFICATION_TOKEN", "dev-token")
GMAIL_PUBSUB_TOPIC = os.getenv("GMAIL_PUBSUB_TOPIC", "")

# Microsoft
MS_CLIENT_ID = os.getenv("MS_CLIENT_ID", "")
MS_TENANT_ID = os.getenv("MS_TENANT_ID", "common")
MS_REDIRECT_URI = os.getenv("MS_REDIRECT_URI", f"{APP_BASE_URL}/auth/m365/callback")
