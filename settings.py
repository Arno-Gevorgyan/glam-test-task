import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Glam Migration"
    admin_email: str = "admin@admin.com"

    jwt_secret: str = os.getenv('SECRET_KEY', 'sdfHKHBcpNDysdfKneGjrfsdJvOoGnkywTAHeuamfskulSroNaoMJFcliMFgpSa')
    algorithm: str = "HS256"
    jwt_header: str = "Bearer"
    access_token_expire_minutes: int = 36000
    refresh_token_expire_days: int = 30

    db_host: str = os.getenv('DB_HOST') or 'localhost'
    db_port: str = os.getenv('DB_PORT') or 5432
    db_database: str = os.getenv('DB_DATABASE') or 'glam'
    db_username: str = os.getenv('DB_USERNAME') or 'glam_user'
    db_password: str = os.getenv('DB_PASSWORD') or 'postgres'

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_database}"
        )

    @property
    def alembic_db_url(self) -> str:
        return self.db_url.replace("+asyncpg", "")

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
