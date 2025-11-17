from dataclasses import dataclass
import os
from functools import lru_cache
from typing import Final

from dotenv import load_dotenv

load_dotenv()

_TRUTHY_VALUES: Final = {"1", "true", "yes", "on"}


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in _TRUTHY_VALUES


@dataclass(frozen=True, slots=True)
class Settings:
    PROJECT_NAME: str = "Shared EV Chargers API"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"


@lru_cache
def get_settings() -> Settings:
    defaults = Settings()
    return Settings(
        PROJECT_NAME=os.getenv("PROJECT_NAME", defaults.PROJECT_NAME),
        DEBUG=_to_bool(os.getenv("DEBUG"), defaults.DEBUG),
        DATABASE_URL=os.getenv("DATABASE_URL", defaults.DATABASE_URL),
    )


settings = get_settings()

