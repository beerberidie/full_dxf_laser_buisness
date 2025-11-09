from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends
from ..deps import get_provider

router = APIRouter(prefix="/ai", tags=["ai"])

jobs: dict[str, dict] = {}

def _download(u: str) -> bytes:
    # Placeholder: replace with real downloader
    return u.encode("utf-8")

def _persist(vecs):
    # Placeholder: store vectors
    pass

@router.post("/batch/embed")
async def batch_embed(urls: list[str], bg: BackgroundTasks, provider=Depends(get_provider)):
    job_id = uuid4().hex
    jobs[job_id] = {"status":"pending"}
    def work():
        texts = [ _download(u).decode("utf-8", errors="ignore") for u in urls ]
        vecs = provider.embeddings(texts, model="text-embedding-3-small")
        _persist(vecs)
        jobs[job_id] = {"status":"done"}
    bg.add_task(work)
    return {"job_id": job_id}

@router.get("/batch/status/{job_id}")
async def batch_status(job_id: str):
    return jobs.get(job_id, {"status":"unknown"})
