from fastapi import FastAPI
from sqlalchemy import create_engine, text
import os

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

@app.get("/health")
def health():
    with engine.connect() as conn:
        r = conn.execute(text("SELECT 1")).scalar()
    return {"ok": True, "db": r}
