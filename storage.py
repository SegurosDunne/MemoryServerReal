# storage.py  (Postgres con psycopg)
import os
from typing import List, Dict, Any, Optional
import psycopg
from psycopg.rows import dict_row

# Lee la URL de conexión del entorno
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada")

# Conexión única por proceso (pool liviano con psycopg)
# Autocommit ON para operaciones simples
conn = psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)

def _ensure_schema():
    sql = """
    CREATE TABLE IF NOT EXISTS memories (
        id UUID PRIMARY KEY,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT[] NOT NULL DEFAULT '{}',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)

_ensure_schema()

def list_memories(user_id: str) -> List[Dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute("SELECT id, user_id, content, tags FROM memories WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def get_memory(user_id: str, mem_id: str) -> Optional[Dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, user_id, content, tags FROM memories WHERE user_id = %s AND id = %s",
            (user_id, mem_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None

def save_memory(mem: Dict[str, Any]) -> Dict[str, Any]:
    # Si existe -> update; si no -> insert
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM memories WHERE id = %s", (mem["id"],))
        exists = cur.fetchone() is not None

        if exists:
            cur.execute(
                "UPDATE memories SET user_id = %s, content = %s, tags = %s WHERE id = %s",
                (mem["user_id"], mem["content"], mem.get("tags", []), mem["id"]),
            )
        else:
            cur.execute(
                "INSERT INTO memories (id, user_id, content, tags) VALUES (%s, %s, %s, %s)",
                (mem["id"], mem["user_id"], mem["content"], mem.get("tags", [])),
            )
    return mem
