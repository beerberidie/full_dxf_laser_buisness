# Universal OpenAI Module – MVP

Drop-in module providing a FastAPI backend, React/TypeScript frontend client, and provider adapters for OpenAI (and Azure OpenAI placeholder).

## Quickstart

```bash
# 1) Infra (Postgres + pgvector + MinIO)
docker compose -f infra/docker-compose.yml up -d

# 2) Python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn openai_module.backend.app:app --reload
```

Then import the frontend client and <AIChatBox /> into your React app.
