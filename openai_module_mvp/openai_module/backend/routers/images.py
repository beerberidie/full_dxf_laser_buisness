from fastapi import APIRouter, Depends
from fastapi.responses import Response
from ..deps import get_provider

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/images")
async def image_generate(prompt: str, size: str="1024x1024", provider=Depends(get_provider)):
    png = provider.image(prompt, size=size)
    return Response(content=png, media_type="image/png")
