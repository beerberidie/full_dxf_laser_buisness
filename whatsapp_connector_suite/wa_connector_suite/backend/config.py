from pydantic import BaseModel, Field
import os

class Settings(BaseModel):
    graph_api_version: str = Field(default=os.getenv("GRAPH_API_VERSION", "v20.0"))
    phone_number_id: str = Field(default=os.getenv("WA_PHONE_NUMBER_ID", ""))
    business_account_id: str = Field(default=os.getenv("WA_BUSINESS_ACCOUNT_ID", ""))
    access_token: str = Field(default=os.getenv("WA_ACCESS_TOKEN", ""))
    app_secret: str = Field(default=os.getenv("WA_APP_SECRET", ""))
    verify_token: str = Field(default=os.getenv("WA_VERIFY_TOKEN", "change-me-verify-token"))

    database_url: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./whatsapp.db"))

    host: str = Field(default=os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default=int(os.getenv("PORT", "8080")))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "info"))

settings = Settings()
