from fastapi import FastAPI, HTTPException
from uuid import uuid4
from models import MemoryIn, Memory
import storage

app = FastAPI(title="Memory Server", version="1.0.0")

@app.get("/health")
def health():
    return {"ok": True, "docs": "/docs"}

@app.post("/memories", response_model=Memory)
def create_memory(payload: MemoryIn):
    mem = Memory(id=str(uuid4()), **payload.model_dump())
    return storage.save_memory(mem.model_dump())

@app.get("/memories/{user_id}", response_model=list[Memory])
def list_memories(user_id: str):
    return [Memory(**m) for m in storage.list_memories(user_id)]

@app.get("/memories/{user_id}/{mem_id}", response_model=Memory)
def get_memory(user_id: str, mem_id: str):
    m = storage.get_memory(user_id, mem_id)
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    return Memory(**m)
