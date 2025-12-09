from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    project_name: str = "Shared EV Chargers"
    project_version: str = "0.1.0"
    
    debug: bool = False

    # Postgres
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379

    # JWT secret
    secret_key: str

    # --- CORS CONFIGURATION ---
    # Defaultně prázdný seznam. Pydantic si ho načte z BACKEND_CORS_ORIGINS v .env
    backend_cors_origins: List[str] = []

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        # Pokud je v .env řetězec s čárkami (např. "http://a.com,http://b.com")
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        # Pokud je to list nebo JSON string (např. '["http://a.com"]')
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    class Config:
        env_file = ".env"

config = Config()