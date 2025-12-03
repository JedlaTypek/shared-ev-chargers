# app/api/deps.py
from typing import Generator
from app.db.schema import SessionLocal

# Tato funkce je nyní veřejná a sdílená pro celou aplikaci
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()