from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5}
)


def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        if revision != "0001_foundation":
            raise RuntimeError("Database migration is not current")
