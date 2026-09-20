import pytest
from pydantic import SecretStr, ValidationError
from sqlalchemy.engine import make_url

from app.config import Settings


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError, match="database_url"):
        Settings(_env_file=None)


def test_supabase_uri_preserves_credentials_and_enables_tls() -> None:
    settings = Settings(
        database_url=SecretStr(
            "postgresql://postgres.project:encoded%40password@pooler.example:5432/postgres"
        )
    )
    url = make_url(settings.database_url.get_secret_value())
    assert url.drivername == "postgresql+psycopg"
    assert url.password == "encoded@password"
    assert url.username == "postgres.project"
    assert url.host == "pooler.example"
    assert url.query["sslmode"] == "require"
    assert "encoded" not in repr(settings)


def test_strict_tls_options_are_preserved() -> None:
    settings = Settings(
        database_url=SecretStr(
            "postgres://user:password@db.example/postgres?sslmode=verify-full&sslrootcert=ca.pem"
        )
    )
    url = make_url(settings.database_url.get_secret_value())
    assert url.query["sslmode"] == "verify-full"
    assert url.query["sslrootcert"] == "ca.pem"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "sqlite:///test.db",
        "postgresql://user@/db",
        "postgresql://user:private-value@db.example/db?sslmode=disable",
    ],
)
def test_bad_database_configuration_is_rejected_without_secret_leak(value: str) -> None:
    with pytest.raises(ValidationError) as error:
        Settings(database_url=SecretStr(value))
    assert "private-value" not in str(error.value)


def test_explicit_origins_merge_without_duplicates() -> None:
    settings = Settings(
        cors_origins=["https://app.example/", "https://app.example"],
        frontend_url="https://preview.example/",
    )
    assert settings.allowed_origins == ["https://app.example", "https://preview.example"]


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "https://*.example",
        "https://app.example/path",
        "https://user:password@app.example",
        "https://app.example?key=x",
    ],
)
def test_invalid_cors_origins_are_rejected(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins=[origin])
