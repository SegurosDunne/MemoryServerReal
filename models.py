from pydantic import BaseModel
from typing import List

class MemoryIn(BaseModel):
    user_id: str
    content: str
    tags: List[str] = []

class Memory(MemoryIn):
    id: str
