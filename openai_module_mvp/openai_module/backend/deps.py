import os
from .providers.openai_provider import OpenAIProvider
from .providers.azure_openai_provider import AzureOpenAIProvider

class Settings:
    provider = os.getenv("AI_PROVIDER", "openai")
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_url = os.getenv("OPENAI_BASE_URL")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

settings = Settings()
_provider = None

def get_provider():
    global _provider
    if _provider:
        return _provider
    if settings.provider == "azure":
        _provider = AzureOpenAIProvider(api_key=settings.azure_key, endpoint=settings.azure_endpoint)
    else:
        _provider = OpenAIProvider(api_key=settings.openai_key, base_url=settings.openai_url)
    return _provider
