from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from functools import lru_cache

class Settings(BaseSettings):
    app_env: str = "dev"
    app_secret: str = "dev-secret"

    # OAuth / Sage
    sage_client_id: str = "set-me"
    sage_client_secret: str = "set-me"
    sage_redirect_uri: str = "http://localhost:8777/auth/callback"
    sage_base_url: str = "https://api.accounting.sage.com/v3.1"

    # DB
    database_url: str = "sqlite:///./sage_agent.sqlite3"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
