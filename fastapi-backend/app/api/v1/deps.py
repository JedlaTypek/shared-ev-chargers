from typing import AsyncGenerator
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.schema import AsyncSessionLocal, User
from app.core.config import config

from app.services.charger_service import ChargerService
from app.services.connector_service import ConnectorService
from app.services.transaction_service import TransactionService

# 1. STRIKTNÍ SCHÉMA (pro zamčené endpointy)
# Říká swaggeru: "Token získáš na této URL".
# Pokud token chybí, FastAPI samo vyhodí chybu (protože auto_error=True je default).
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token"
)

# 2. VOLITELNÉ SCHÉMA (pro smíšené endpointy)
# auto_error=False zajistí, že když token chybí, FastAPI vrátí None místo chyby.
reusable_oauth2_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token",
    auto_error=False
)

# --- DATABÁZE & REDIS ---

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    r = redis.Redis(
        host=config.redis_host, 
        port=config.redis_port, 
        decode_responses=True
    )
    try:
        yield r
    finally:
        await r.close()

# --- AUTENTIZACE ---

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    STRIKTNÍ VERZE:
    Použij toto u endpointů, které vyžadují přihlášení (např. GET /users/me).
    Pokud je token neplatný nebo chybí, vyhodí 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Dekódování JWT tokenu
        payload = jwt.decode(
            token, 
            config.secret_key, 
            algorithms=[config.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Vyhledání uživatele v DB
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    # Volitelně: kontrola, zda je uživatel aktivní
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: str | None = Depends(reusable_oauth2_optional)
) -> User | None:
    """
    VOLITELNÁ VERZE:
    Použij toto u endpointů, kam může i nepřihlášený (např. Registrace).
    Pokud je token platný, vrátí User objekt (jako admin).
    Pokud token chybí nebo je neplatný, vrátí None (a ty s tím musíš v kódu počítat).
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, 
            config.secret_key, 
            algorithms=[config.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        # Pokud je token poškozený, prostě ho ignorujeme a tváříme se jako anonym
        return None

    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    return user


async def verify_api_key(x_api_key: str = Header(...)):
    """
    Ověří, zda požadavek obsahuje správný API Key v hlavičce 'x-api-key'.
    FastAPI automaticky převede 'X-API-Key' z hlavičky na proměnnou 'x_api_key'.
    """
    if x_api_key != config.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return True

def get_connector_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> ConnectorService:
    return ConnectorService(session=db, redis=redis)

def get_charger_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> ChargerService:
    return ChargerService(session=db, redis=redis)

def get_transaction_service(
    db: AsyncSession = Depends(get_db)
) -> TransactionService:
    return TransactionService(session=db)