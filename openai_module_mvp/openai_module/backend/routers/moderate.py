from fastapi import APIRouter, Depends
from ..deps import get_provider

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/moderate")
async def moderate(text: str, provider=Depends(get_provider)):
    result = provider.moderate(text)
    return result
