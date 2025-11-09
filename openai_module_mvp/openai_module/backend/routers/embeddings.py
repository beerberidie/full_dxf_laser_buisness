from fastapi import APIRouter, Depends
from ..deps import get_provider, settings
from ..models.schemas import EmbedReq, EmbedRes

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/embeddings", response_model=EmbedRes)
async def create_embeddings(req: EmbedReq, provider=Depends(get_provider)):
    model = req.model or "text-embedding-3-small"
    vecs = provider.embeddings(req.texts, model=model)
    return EmbedRes(vectors=vecs)
