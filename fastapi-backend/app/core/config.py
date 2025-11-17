from pydantic_settings import BaseSettings

class Config(BaseSettings):
    app_name: str = "Shared EV Chargers"
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

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    class Config:
        env_file = ".env"

config = Config()
