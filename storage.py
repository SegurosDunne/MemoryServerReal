# storage.py
import os
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crear tabla si no existe
with engine.begin() as con:
    con.execute(text("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            tags JSONB NOT NULL DEFAULT '[]'::jsonb
        )
    """))

def list_memories(user_id: str) -> List[Dict[str, Any]]:
    sql = text("SELECT id, user_id, content, tags FROM memories WHERE user_id=:u")
    with engine.begin() as con:
        rows = con.execute(sql, {"u": user_id}).mappings().all()
        return [dict(r) for r in rows]

def get_memory(user_id: str, mem_id: str) -> Optional[Dict[str, Any]]:
    sql = text("""
        SELECT id, user_id, content, tags
        FROM memories
        WHERE user_id=:u AND id=:i
        LIMIT 1
    """)
    with engine.begin() as con:
        r = con.execute(sql, {"u": user_id, "i": mem_id}).mappings().first()
        return dict(r) if r else None

def save_memory(mem: dict) -> dict:
    sql = text("""
        INSERT INTO memories (id, user_id, content, tags)
        VALUES (:id, :user_id, :content, CAST(:tags AS JSONB))
        ON CONFLICT (id) DO UPDATE SET
            user_id=EXCLUDED.user_id,
            content=EXCLUDED.content,
            tags=EXCLUDED.tags
        RETURNING id, user_id, content, tags
    """)
    with engine.begin() as con:
        row = con.execute(sql, {
            "id": mem["id"],
            "user_id": mem["user_id"],
            "content": mem["content"],
            "tags": mem["tags"],
        }).mappings().first()
        return dict(row)
