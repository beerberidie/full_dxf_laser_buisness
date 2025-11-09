# Minimal placeholder for pgvector ops.
# In production, use SQLAlchemy vector extension and proper migrations.
from typing import List, Any

def search(session, query_vec: list[float], k: int = 5) -> List[Any]:
    # Placeholder: implement with embedding <-> operator where available.
    return []
