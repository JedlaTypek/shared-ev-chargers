# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from app.core.config import config  # <--- ZMĚNA: importujeme 'config'

# Nastavení kontextu pro hashování (používáme algoritmus bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Ověří, zda se zadané heslo shoduje s hashem v DB."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Vygeneruje bezpečný hash z hesla."""
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # ZMĚNA: config.access_token_expire_minutes (malá písmena podle Config třídy)
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # ZMĚNA: config.secret_key a config.algorithm
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
    return encoded_jwt