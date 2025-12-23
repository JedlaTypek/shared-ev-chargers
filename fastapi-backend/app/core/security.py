# app/core/security.py
from passlib.context import CryptContext

# Nastavení kontextu pro hashování (používáme algoritmus bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Ověří, zda se zadané heslo shoduje s hashem v DB."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Vygeneruje bezpečný hash z hesla."""
    return pwd_context.hash(password)