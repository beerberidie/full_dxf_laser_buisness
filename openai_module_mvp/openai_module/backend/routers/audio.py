from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from ..deps import get_provider

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/audio/tts")
async def tts(text: str, voice: str="alloy", provider=Depends(get_provider)):
    data = provider.tts(text, voice=voice)
    return Response(content=data, media_type="audio/mpeg")

@router.post("/audio/stt")
async def stt(file: UploadFile = File(...), provider=Depends(get_provider)):
    wav = await file.read()
    text = provider.stt(wav)
    return {"text": text}
