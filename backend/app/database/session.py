from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

REQUIRED_TABLES = (
    "alembic_version",
    "stock_watchlist",
    "stock_prices",
    "news_articles",
    "gaming_posts",
    "gaming_post_metrics",
    "collector_runs",
)


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
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def session_scope() -> Session:
    return SessionLocal()


def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        if not revision:
            raise RuntimeError("Database migration is not current")
        missing = [
            name
            for name in REQUIRED_TABLES[1:]
            if connection.execute(text("SELECT to_regclass(:name)"), {"name": name}).scalar()
            is None
        ]
        if missing:
            raise RuntimeError(f"Required database tables are missing: {', '.join(missing)}")


def database_table_status() -> dict[str, bool]:
    with engine.connect() as connection:
        return {
            name: connection.execute(text("SELECT to_regclass(:name)"), {"name": name}).scalar()
            is not None
            for name in REQUIRED_TABLES
        }
