import json
from pathlib import Path

DATA_FILE = Path("memories.json")

def _ensure():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")

def _load():
    _ensure()
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except:
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []

def _save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def list_memories(user_id: str):
    return [m for m in _load() if m.get("user_id") == user_id]

def get_memory(user_id: str, mem_id: str):
    for m in _load():
        if m.get("user_id") == user_id and m.get("id") == mem_id:
            return m
    return None

def save_memory(mem: dict):
    data = _load()
    for i, m in enumerate(data):
        if m.get("id") == mem.get("id"):
            data[i] = mem
            _save(data)
            return mem
    data.append(mem)
    _save(data)
    return mem
