from .base import Provider
from typing import Optional, Dict, Any, List
from openai import OpenAI
import base64
from io import BytesIO

class OpenAIProvider(Provider):
    def __init__(self, api_key: str, base_url: Optional[str]=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, messages: List[Dict], *, model: str, tools: Optional[list]=None,
             stream: bool=False, response_format: Optional[dict]=None) -> Any:
        args = {"model": model, "messages": messages}
        if tools: args["tools"] = tools
        if response_format: args["response_format"] = response_format
        if stream:
            return self.client.chat.completions.create(stream=True, **args)
        return self.client.chat.completions.create(**args)

    def embeddings(self, texts: list[str], *, model: str) -> list[list[float]]:
        out = self.client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in out.data]

    def image(self, prompt: str, *, size: str="1024x1024") -> bytes:
        img = self.client.images.generate(model="gpt-image-1", prompt=prompt, size=size)
        return base64.b64decode(img.data[0].b64_json)

    def tts(self, text: str, *, voice: str) -> bytes:
        audio = self.client.audio.speech.create(model="gpt-4o-mini-tts", voice=voice, input=text)
        # The SDK may stream; here we assume full bytes are available
        return audio.read() if hasattr(audio, "read") else bytes(audio)

    def stt(self, wav_bytes: bytes) -> str:
        return self.client.audio.transcriptions.create(model="gpt-4o-transcribe", file=BytesIO(wav_bytes)).text

    def moderate(self, text: str) -> Dict[str, Any]:
        return self.client.moderations.create(model="omni-moderation-latest", input=text).model_dump()
