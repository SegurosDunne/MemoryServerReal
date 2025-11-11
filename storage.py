import os
from typing import List, Optional
from sqlalchemy import (
    create_engine, String, Text, Column, DateTime
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL no está configurada")

# Engine y sesión
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class MemoryRow(Base):
    __tablename__ = "memories"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# Crear tabla si no existe
Base.metadata.create_all(bind=engine)

# ============ API de almacenamiento ============

def list_memories(user_id: str) -> List[dict]:
    with SessionLocal() as s:
        rows = s.query(MemoryRow).filter(MemoryRow.user_id == user_id).order_by(MemoryRow.created_at.desc()).all()
        return [
            {"id": r.id, "user_id": r.user_id, "content": r.content, "tags": r.tags}
            for r in rows
        ]

def get_memory(user_id: str, mem_id: str) -> Optional[dict]:
    with SessionLocal() as s:
        r = (s.query(MemoryRow)
               .filter(MemoryRow.user_id == user_id, MemoryRow.id == mem_id)
               .one_or_none())
        if not r:
            return None
        return {"id": r.id, "user_id": r.user_id, "content": r.content, "tags": r.tags}

def save_memory(mem: dict) -> dict:
    with SessionLocal() as s:
        r = s.query(MemoryRow).get(mem["id"])
        if r:
            r.user_id = mem["user_id"]
            r.content = mem["content"]
            r.tags = mem.get("tags", [])
        else:
            r = MemoryRow(
                id=mem["id"],
                user_id=mem["user_id"],
                content=mem["content"],
                tags=mem.get("tags", []),
            )
            s.add(r)
        s.commit()
        return {"id": r.id, "user_id": r.user_id, "content": r.content, "tags": r.tags}
