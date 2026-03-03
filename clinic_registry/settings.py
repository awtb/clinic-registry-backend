import os

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_driver: str = "postgresql+asyncpg"
    db_sync_driver: str = "postgresql+psycopg2"

    jwt_secret_key: str
    jwt_access_token_expiration_minutes: int = 30
    jwt_refresh_token_expiration_minutes: int = 80
    serving_host: str = "0.0.0.0"
    serving_port: int = 8000
    serving_workers_count: int = 1

    logging_lvl: str = "INFO"
    logging_fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    cors_allow_origins: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_credentials: bool = True

    model_config = SettingsConfigDict(
        extra="ignore", env_ignore_empty=True, env_file=".env"
    )


def get_settings(env_file: str | None = None) -> Settings:
    target_env_file = env_file or os.getenv("SETTINGS_ENV_FILE", ".env")
    return Settings(_env_file=target_env_file)  # type: ignore[call-arg]
