import logging
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.collectors.stocks import SYMBOL_RE, AlphaVantageProvider
from app.config import settings
from app.database.session import check_database, database_table_status, engine, session_scope
from app.models import CollectorRun, GamingPost, NewsArticle, StockPrice, StockWatchlist

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    engine.dispose()


app = FastAPI(title="SignalScope API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class Health(BaseModel):
    status: Literal["ok"] = "ok"


def require_database() -> None:
    try:
        check_database()
    except Exception:
        logger.warning("Database readiness check failed")
        raise HTTPException(
            status_code=503, detail="Database unavailable or migrations pending"
        ) from None


@app.get("/health", response_model=Health)
def health(_: Annotated[None, Depends(require_database)]) -> Health:
    """Readiness: PostgreSQL must respond and the migration must be applied."""
    return Health()


@app.get("/live", response_model=Health)
def live() -> Health:
    """Process liveness only; does not imply that PostgreSQL is ready."""
    return Health()


@app.get("/health/db")
def database_health(_: Annotated[None, Depends(require_database)]) -> dict[str, object]:
    """Readiness plus non-sensitive required-table status."""
    return {"status": "ok", "tables": database_table_status()}


def get_db() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session


class WatchlistRequest(BaseModel):
    symbol: str
    company_name: str | None = None


def latest_stock_rows(session: Session) -> list[dict[str, object]]:
    latest = (
        select(StockPrice.symbol, func.max(StockPrice.market_timestamp).label("latest"))
        .group_by(StockPrice.symbol)
        .subquery()
    )
    rows = session.execute(
        select(StockWatchlist, StockPrice)
        .outerjoin(latest, latest.c.symbol == StockWatchlist.symbol)
        .outerjoin(
            StockPrice,
            (StockPrice.symbol == latest.c.symbol)
            & (StockPrice.market_timestamp == latest.c.latest),
        )
        .where(StockWatchlist.enabled)
        .order_by(StockWatchlist.symbol)
    ).all()
    return [
        {
            "symbol": watch.symbol,
            "companyName": watch.company_name,
            "price": price.price if price else None,
            "change": price.change if price else None,
            "changePercent": price.change_percent if price else None,
            "marketTimestamp": price.market_timestamp.isoformat() if price else None,
            "dataSource": price.data_source if price else None,
            "dataFreshness": price.data_freshness if price else None,
        }
        for watch, price in rows
    ]


@app.get("/api/watchlist")
def watchlist(session: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    return [
        {
            "symbol": row.symbol,
            "companyName": row.company_name,
            "enabled": row.enabled,
            "createdAt": row.created_at.isoformat(),
        }
        for row in session.scalars(
            select(StockWatchlist).where(StockWatchlist.enabled).order_by(StockWatchlist.symbol)
        ).all()
    ]


@app.post("/api/watchlist", status_code=201)
def add_watchlist(
    payload: WatchlistRequest, session: Annotated[Session, Depends(get_db)]
) -> dict[str, object]:
    symbol = payload.symbol.strip().upper()
    if not SYMBOL_RE.fullmatch(symbol):
        raise HTTPException(status_code=422, detail="Invalid ticker symbol")
    row = session.scalar(select(StockWatchlist).where(StockWatchlist.symbol == symbol))
    if row is None:
        row = StockWatchlist(
            symbol=symbol,
            company_name=payload.company_name,
            enabled=True,
            created_at=datetime.now(UTC),
        )
        session.add(row)
    else:
        row.enabled = True
        if payload.company_name:
            row.company_name = payload.company_name
    session.commit()
    return {"symbol": row.symbol, "companyName": row.company_name, "enabled": row.enabled}


@app.delete("/api/watchlist/{symbol}", status_code=204)
def remove_watchlist(symbol: str, session: Annotated[Session, Depends(get_db)]) -> None:
    symbol = symbol.strip().upper()
    row = session.scalar(select(StockWatchlist).where(StockWatchlist.symbol == symbol))
    if row is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    row.enabled = False
    session.commit()


@app.get("/api/stocks")
def stocks(session: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    return latest_stock_rows(session)


@app.get("/api/stocks/search")
def stock_search(q: str, _: Annotated[None, Depends(require_database)]) -> list[dict[str, str]]:
    query = q.strip()
    if len(query) < 2:
        return []
    provider = AlphaVantageProvider()
    try:
        return [
            {
                "symbol": item.get("1. symbol", ""),
                "companyName": item.get("2. name", ""),
                "type": item.get("3. type", ""),
                "region": item.get("4. region", ""),
            }
            for item in provider.search_symbols(query)
        ]
    finally:
        provider.close()


@app.get("/api/stocks/{symbol}")
def stock_history(
    symbol: str, session: Annotated[Session, Depends(get_db)]
) -> list[dict[str, object]]:
    symbol = symbol.strip().upper()
    if not SYMBOL_RE.fullmatch(symbol):
        raise HTTPException(status_code=422, detail="Invalid ticker symbol")
    return [
        {
            "symbol": row.symbol,
            "price": row.price,
            "changePercent": row.change_percent,
            "marketTimestamp": row.market_timestamp.isoformat(),
            "dataFreshness": row.data_freshness,
        }
        for row in session.scalars(
            select(StockPrice)
            .where(StockPrice.symbol == symbol)
            .order_by(StockPrice.market_timestamp.desc())
            .limit(365)
        ).all()
    ]


@app.get("/api/news")
def news(
    session: Annotated[Session, Depends(get_db)],
    category: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, object]:
    query = select(NewsArticle).order_by(
        desc(NewsArticle.published_at), desc(NewsArticle.collected_at)
    )
    if category and category.lower() != "all":
        query = query.where(NewsArticle.category == category)
    if search:
        query = query.where(NewsArticle.title.ilike(f"%{search.strip()}%"))
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    rows = session.scalars(query.offset(offset).limit(limit)).all()
    return {
        "items": [
            {
                "id": row.id,
                "source": row.source,
                "title": row.title,
                "description": row.description,
                "url": row.url,
                "imageUrl": row.image_url,
                "author": row.author,
                "category": row.category,
                "publishedAt": row.published_at.isoformat() if row.published_at else None,
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/gaming")
def gaming(
    session: Annotated[Session, Depends(get_db)],
    game: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, object]:
    query = select(GamingPost).order_by(
        desc(GamingPost.published_at), desc(GamingPost.collected_at)
    )
    if game:
        query = query.where(GamingPost.game == game)
    if search:
        query = query.where(GamingPost.title.ilike(f"%{search.strip()}%"))
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    rows = session.scalars(query.offset(offset).limit(limit)).all()
    return {
        "items": [
            {
                "id": row.id,
                "source": row.source,
                "title": row.title,
                "game": row.game,
                "author": row.author,
                "url": row.url,
                "summary": row.summary,
                "imageUrl": row.image_url,
                "likes": row.likes,
                "comments": row.comments,
                "views": row.views,
                "publishedAt": row.published_at.isoformat() if row.published_at else None,
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/gaming/trending")
def gaming_trending(session: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    rows = session.execute(
        select(
            GamingPost.game,
            func.count(GamingPost.id),
            func.coalesce(func.sum(GamingPost.likes), 0)
            + func.coalesce(func.sum(GamingPost.comments), 0)
            + func.coalesce(func.sum(GamingPost.views), 0),
        )
        .where(GamingPost.game.is_not(None))
        .group_by(GamingPost.game)
        .order_by(desc(func.count(GamingPost.id)))
        .limit(10)
    ).all()
    return [
        {"game": game, "postCount": count, "interactions": interactions}
        for game, count, interactions in rows
    ]


@app.get("/api/collector-status")
def collector_status(session: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    latest: dict[str, CollectorRun] = {}
    for row in session.scalars(select(CollectorRun).order_by(desc(CollectorRun.started_at))).all():
        latest.setdefault(row.collector, row)
    return [
        {
            "collector": name,
            "status": row.status,
            "itemsFound": row.items_found,
            "itemsInserted": row.items_inserted,
            "startedAt": row.started_at.isoformat(),
            "finishedAt": row.finished_at.isoformat() if row.finished_at else None,
            "error": row.error_message,
        }
        for name, row in latest.items()
    ]


@app.get("/api/dashboard")
def dashboard(session: Annotated[Session, Depends(get_db)]) -> dict[str, object]:
    return {
        "stocks": latest_stock_rows(session),
        "technologyNews": news(limit=5, offset=0, session=session)["items"],
        "gaming": gaming(limit=5, offset=0, session=session)["items"],
        "gamingTrending": gaming_trending(session),
        "collectorStatus": collector_status(session),
    }
