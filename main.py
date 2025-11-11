from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

app = FastAPI()

class MemoryIn(BaseModel):
    user_id: str
    content: str
    tags: List[str] = []

class Memory(MemoryIn):
    id: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/memories")
def create_memory(mem: MemoryIn):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                INSERT INTO memories (id, user_id, content, tags)
                VALUES (gen_random_uuid(), :user_id, :content, :tags)
                RETURNING id;
            """),
            {"user_id": mem.user_id, "content": mem.content, "tags": ",".join(mem.tags)}
        )
        new_id = result.fetchone()[0]
        return {"id": new_id, **mem.dict()}


@app.get("/memories/{user_id}")
def list_memories(user_id: str):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, user_id, content, tags FROM memories WHERE user_id=:u"),
            {"u": user_id}
        ).fetchall()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "content": r.content,
                "tags": r.tags.split(",") if r.tags else []
            }
            for r in rows
        ]
