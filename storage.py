import psycopg
import os

DB_URL = os.environ["DATABASE_URL"]

def get_conn():
    return psycopg.connect(DB_URL)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT[]
            );
        """)
        conn.commit()

def save_memory(mem):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO memories (id, user_id, content, tags)
            VALUES (%s, %s, %s, %s)
        """, (mem["id"], mem["user_id"], mem["content"], mem["tags"]))
        conn.commit()
        return mem

def list_memories(user_id: str):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, user_id, content, tags FROM memories
            WHERE user_id = %s
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]

def get_memory(user_id: str, mem_id: str):
    with get_conn() as conn:
        row = conn.execute("""
            SELECT id, user_id, content, tags FROM memories
            WHERE user_id = %s AND id = %s
        """, (user_id, mem_id)).fetchone()
        return dict(row) if row else None
