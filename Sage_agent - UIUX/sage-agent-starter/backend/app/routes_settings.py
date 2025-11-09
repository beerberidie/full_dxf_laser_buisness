from fastapi import APIRouter, Depends
from .db import get_session, Setting
from sqlmodel import select
import uuid, json

router = APIRouter(prefix="/api/settings", tags=["settings"])

def _tenant_id() -> str:
    return "demo-tenant"

@router.get("/{scope}")
def get_settings(scope: str, session=Depends(get_session)):
    rows = session.exec(select(Setting).where(Setting.tenant_id==_tenant_id(), Setting.scope==scope)).all()
    out = {}
    for r in rows:
        out[r.key] = json.loads(r.value)
    return out

@router.put("/{scope}/{key}")
def put_setting(scope: str, key: str, value: dict, session=Depends(get_session)):
    row = session.exec(select(Setting).where(Setting.tenant_id==_tenant_id(), Setting.scope==scope, Setting.key==key)).first()
    if not row:
        row = Setting(id=str(uuid.uuid4()), tenant_id=_tenant_id(), scope=scope, key=key, value=json.dumps(value))
        session.add(row)
    else:
        row.value = json.dumps(value)
    session.commit()
    return {"ok": True}
