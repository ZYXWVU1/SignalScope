from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url.get_secret_value(),
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    pool_timeout=5,
    pool_recycle=1800,
    connect_args={"connect_timeout": 5, "options": "-c statement_timeout=10000"},
)


def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        if revision != "0001_foundation":
            raise RuntimeError("Database migration is not current")
