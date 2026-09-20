from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class StockWatchlist(Base):
    __tablename__ = "stock_watchlist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    company_name: Mapped[str | None] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class StockPrice(Base):
    __tablename__ = "stock_prices"
    __table_args__ = (
        UniqueConstraint("symbol", "market_timestamp", name="uq_stock_snapshot"),
        Index("ix_stock_prices_symbol_timestamp", "symbol", "market_timestamp"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    open: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    high: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    low: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    previous_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    change: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    change_percent: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    market_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_source: Mapped[str] = mapped_column(String(64), default="alpha_vantage", nullable=False)
    data_freshness: Mapped[str] = mapped_column(String(32), default="delayed", nullable=False)


class NewsArticle(Base):
    __tablename__ = "news_articles"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_news_content_hash"),
        Index("ix_news_published_at", "published_at"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(2048))
    author: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class GamingPost(Base):
    __tablename__ = "gaming_posts"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_gaming_content_hash"),
        Index("ix_gaming_published_at", "published_at"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="xiaoheihe")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    game: Mapped[str | None] = mapped_column(String(255), index=True)
    author: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(2048))
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class GamingPostMetric(Base):
    __tablename__ = "gaming_post_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaming_post_id: Mapped[int] = mapped_column(Integer, index=True)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CollectorRun(Base):
    __tablename__ = "collector_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collector: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(16), index=True)
    items_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
