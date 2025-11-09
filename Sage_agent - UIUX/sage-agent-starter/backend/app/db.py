from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime

from .settings import get_settings
settings = get_settings()

engine = create_engine(settings.database_url, echo=False)

class Tenant(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    region: str = "ZA"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    email: str
    display_name: Optional[str] = None
    role: str = "Owner"

class Connection(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    provider: str  # 'sbca'
    business_id: Optional[str] = None
    secret_ref: Optional[str] = None  # in real prod: reference to KMS/Vault
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    status: str = "active"

class Setting(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    scope: str  # 'workspace' | 'personal' | 'automation' | 'template' | 'security'
    key: str
    value: str

class AuditLog(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    user_id: Optional[str] = Field(default=None)
    action: str
    target: Optional[str] = None
    request: Optional[str] = None
    response: Optional[str] = None
    status: str = "preview"  # preview|confirmed|success|failure
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SyncCursor(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g., 'contacts', 'sales_invoices'
    tenant_id: str = Field(foreign_key="tenant.id")
    last_ts: Optional[str] = None

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
