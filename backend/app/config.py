from pathlib import Path
from urllib.parse import urlsplit

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", extra="ignore", hide_input_in_errors=True
    )
    database_url: SecretStr
    cors_origins: list[str] = []
    frontend_url: str = ""

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value().strip())
            if url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"}:
                raise ValueError
            if not url.host or not url.database or not url.username:
                raise ValueError
            if url.query.get("sslmode", "require") not in {"require", "verify-ca", "verify-full"}:
                raise ValueError
        except (ArgumentError, ValueError):
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL URL with a host, database, user, and TLS"
            ) from None
        url = url.set(drivername="postgresql+psycopg")
        if "sslmode" not in url.query:
            url = url.update_query_dict({"sslmode": "require"})
        return SecretStr(url.render_as_string(hide_password=False))

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, origins: list[str]) -> list[str]:
        return list(dict.fromkeys(cls.validate_origin(origin) for origin in origins))

    @field_validator("frontend_url")
    @classmethod
    def validate_frontend_url(cls, origin: str) -> str:
        return cls.validate_origin(origin) if origin else ""

    @staticmethod
    def validate_origin(origin: str) -> str:
        parts = urlsplit(origin.strip())
        if (
            parts.scheme not in {"http", "https"}
            or not parts.hostname
            or "*" in parts.netloc
            or parts.username is not None
            or parts.password is not None
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
        ):
            raise ValueError("Frontend origins must be explicit HTTP(S) origins without paths")
        return f"{parts.scheme}://{parts.netloc}"

    @property
    def allowed_origins(self) -> list[str]:
        return list(
            dict.fromkeys([*self.cors_origins, *([self.frontend_url] if self.frontend_url else [])])
        )


settings = Settings()
