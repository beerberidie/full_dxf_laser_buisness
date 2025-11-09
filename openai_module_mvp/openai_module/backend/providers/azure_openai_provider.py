from .base import Provider
from typing import Optional, Dict, Any, List

# Placeholder for Azure OpenAI parity; adapt to azure-openai sdk if used.
class AzureOpenAIProvider(Provider):
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def chat(self, messages: List[Dict], *, model: str, tools: Optional[list]=None,
             stream: bool=False, response_format: Optional[dict]=None) -> Any:
        raise NotImplementedError("Implement Azure OpenAI client or map to deployments")

    def embeddings(self, texts: list[str], *, model: str) -> list[list[float]]:
        raise NotImplementedError

    def image(self, prompt: str, *, size: str="1024x1024") -> bytes:
        raise NotImplementedError

    def tts(self, text: str, *, voice: str) -> bytes:
        raise NotImplementedError

    def stt(self, wav_bytes: bytes) -> str:
        raise NotImplementedError

    def moderate(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError
