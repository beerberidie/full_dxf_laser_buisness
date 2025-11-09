from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import get_settings
from .db import init_db
from .oauth import router as oauth_router
from .routes_sage import router as sage_router
from .routes_settings import router as settings_router

init_db()
s = get_settings()
app = FastAPI(title="Sage Agent Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth_router)
app.include_router(sage_router)
app.include_router(settings_router)

@app.get("/healthz")
def health():
    return {"status": "ok"}
