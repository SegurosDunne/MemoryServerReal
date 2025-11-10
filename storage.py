import os
import json
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import OperationalError, ProgrammingError

# DATABASE_URL: si existe => Postgres (Render). Si no => SQLite local.
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./memories.db")

# Para URLs de Render con "postgres://", conviene normalizar a "postgresql://"
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DB_URL, pool_pre_ping=True)
Base = declarative_base()

class MemoryRow(Base):
    __tablename__ = "memories"
    id = Column(String(64), primary_key=True)
    user_id = Column(String(128), index=True, nullable=False)
    content = Column(Text, nullable=False)
    # Guardamos tags como JSON serializado (TEXT) para que funcione igual en Postgres y SQLite
    tags = Column(Text, nullable=False, default="[]")

def _ensure_schema():
    try:
        Base.metadata.create_all(engine)
    except (OperationalError, ProgrammingError) as e:
        raise RuntimeError(f"Error creando tablas: {e}")

_ensure_schema()

def list_memories(user_id: str) -> List[Dict[str, Any]]:
    with Session(engine) as s:
        rows = s.query(MemoryRow).filter(MemoryRow.user_id == user_id).all()
        out = []
        for r in rows:
            out.append({
                "id": r.id,
                "user_id": r.user_id,
                "content": r.content,
                "tags": json.loads(r.tags or "[]"),
            })
        return out

def get_memory(user_id: str, mem_id: str) -> Optional[Dict[str, Any]]:
    with Session(engine) as s:
        r = s.query(MemoryRow).filter(
            MemoryRow.user_id == user_id,
            MemoryRow.id == mem_id
        ).first()
        if not r:
            return None
        return {
            "id": r.id,
            "user_id": r.user_id,
            "content": r.content,
            "tags": json.loads(r.tags or "[]"),
        }

def save_memory(mem: Dict[str, Any]) -> Dict[str, Any]:
    with Session(engine) as s:
        existing = s.get(MemoryRow, mem["id"])
        if existing:
            existing.user_id = mem["user_id"]
            existing.content = mem["content"]
            existing.tags = json.dumps(mem.get("tags", []), ensure_ascii=False)
            s.add(existing)
        else:
            row = MemoryRow(
                id=mem["id"],
                user_id=mem["user_id"],
                content=mem["content"],
                tags=json.dumps(mem.get("tags", []), ensure_ascii=False),
            )
            s.add(row)
        s.commit()
        return mem
