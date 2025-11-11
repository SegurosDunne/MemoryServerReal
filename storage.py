import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_memory(mem):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO memories (id, user_id, content, tags)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            content = EXCLUDED.content,
            tags = EXCLUDED.tags
        RETURNING *;
    """, (mem["id"], mem["user_id"], mem["content"], ",".join(mem["tags"])))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row

def list_memories(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM memories WHERE user_id=%s;", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_memory(user_id, mem_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM memories WHERE user_id=%s AND id=%s;",
        (user_id, mem_id)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row
