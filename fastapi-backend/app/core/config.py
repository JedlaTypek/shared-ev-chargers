# fastapi-backend/app/core/config.py
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    project_name: str = "Voltuj"
    project_version: str = "0.1.0"
    
    # Databáze
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    postgres_port: int = 5432

    # Redis
    redis_host: str
    redis_port: int = 6379

    # Bezpečnost
    api_key: str
    jwt_secret: str
    access_token_expire_minutes: int = 30
    # Pydantic automaticky parsuje ["*"] na list
    backend_cors_origins: List[str] = []
    algorithm: str = "HS256"

    # Ostatní
    debug: bool
    log_level: str = "info"
    
    # URL pro databázi (asynchronní pro aplikaci)
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.postgres_port}/{self.postgres_db}"

# Inicializace
config = Config()