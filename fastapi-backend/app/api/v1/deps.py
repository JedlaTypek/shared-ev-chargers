from typing import AsyncGenerator
import redis.asyncio as redis # ZMĚNA: redis.asyncio
from app.db.schema import AsyncSessionLocal
from app.core.config import config
from sqlalchemy.ext.asyncio import AsyncSession

# PostrgeSQL Async session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Redis Async client
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    # redis.asyncio.Redis má stejné API, ale metody jsou awaitable
    r = redis.Redis(
        host=config.redis_host, 
        port=config.redis_port, 
        decode_responses=True
    )
    try:
        yield r
    finally:
        await r.close() # ZMĚNA: await close