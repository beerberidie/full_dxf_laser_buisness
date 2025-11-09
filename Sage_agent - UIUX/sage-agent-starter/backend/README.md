# Sage Agent Backend

## Quick start
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --port 8777
```

Create `.env` from `.env.example` and set your values.
