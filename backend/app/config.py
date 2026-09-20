from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    database_url: str = (
        "postgresql+psycopg://signalscope:local-development-only@localhost:5432/signalscope"
    )
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
