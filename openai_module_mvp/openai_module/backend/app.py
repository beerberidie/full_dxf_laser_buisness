from fastapi import FastAPI
from .routers import chat, embeddings, images, audio, moderate, batch, tools

app = FastAPI(title="Universal AI Module", version="0.1.0")

app.include_router(chat.router)
app.include_router(embeddings.router)
app.include_router(images.router)
app.include_router(audio.router)
app.include_router(moderate.router)
app.include_router(batch.router)
app.include_router(tools.router)

@app.get("/health")
def health():
    return {"ok": True}
