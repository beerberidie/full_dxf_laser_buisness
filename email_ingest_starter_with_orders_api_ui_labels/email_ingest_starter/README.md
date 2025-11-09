# Email Ingest Starter (FastAPI + React)

Production-lean starter for **Direct API email ingestion**:
- OAuth (PKCE) for **Gmail** & **Microsoft 365**
- Webhooks (Gmail Pub/Sub push; Microsoft Graph Subscriptions)
- Token store (SQLite + Fernet encryption)
- Auto-renew subscriptions (background job)
- Provider parsers (Gmail, Graph) → **shared normalizer**
- AI JSON schema & dispatcher for `UPSERT_CONTACT`, `CREATE_ORDER`, `DRAFT_REPLY`
- Polished React `<MailboxConnect />`

## Quick Start

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in values
uvicorn app.main:app --reload
```

### 2) Frontend (Vite + React + TS)
```bash
cd frontend
npm i
npm run dev
```

### 3) Environment (.env)
Create `backend/.env` with:
```
APP_BASE_URL=http://localhost:8000               # public URL for callbacks/webhooks if using tunneling
FERNET_KEY=REPLACE_WITH_FERNET_KEY               # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Google
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/gmail/callback
GMAIL_PUBSUB_VERIFICATION_TOKEN=replace_me       # optional extra check
GMAIL_PUBSUB_TOPIC=projects/YOURPROJ/topics/YOURTOPIC

# Microsoft
MS_CLIENT_ID=...
MS_TENANT_ID=common                               # or your tenant
MS_REDIRECT_URI=http://localhost:8000/auth/m365/callback

# Webhook externally reachable (use ngrok in dev)
PUBLIC_WEBHOOK_BASE=https://YOUR-NGROK-URL        # e.g. https://abcd1234.ngrok.app
```

> During local dev, use **ngrok** or a tunnel so Gmail/Microsoft can reach your webhooks.

### 4) Notes
- This kit includes a **safe schema-first AI contract** and a stub `ai/engine.py`—plug your model there.
- Subscriptions auto-renew via a background scheduler.
- Gmail push requires configuring Pub/Sub to push to your webhook or polling the Pub/Sub endpoint you expose.

---
