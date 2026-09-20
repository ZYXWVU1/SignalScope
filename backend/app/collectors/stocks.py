import re
from datetime import UTC, datetime
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import StockPrice, StockWatchlist

SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,15}$")


class AlphaVantageProvider:
    endpoint = "https://www.alphavantage.co/query"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=15, headers={"User-Agent": "SignalScope/1.0"})
        self._owned_client = client is None

    def close(self) -> None:
        if self._owned_client:
            self.client.close()

    def get_quote(self, symbol: str) -> dict[str, str]:
        if not settings.alpha_vantage_api_key:
            raise RuntimeError("ALPHA_VANTAGE_API_KEY is not configured")
        response = self.client.get(
            self.endpoint,
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": settings.alpha_vantage_api_key,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("Note") or payload.get("Information"):
            raise RuntimeError(payload.get("Note") or payload.get("Information"))
        quote = payload.get("Global Quote") or {}
        if not quote.get("05. price"):
            raise RuntimeError(f"Alpha Vantage returned no quote for {symbol}")
        return quote

    def search_symbols(self, query: str) -> list[dict[str, str]]:
        if not settings.alpha_vantage_api_key:
            raise RuntimeError("ALPHA_VANTAGE_API_KEY is not configured")
        response = self.client.get(
            self.endpoint,
            params={
                "function": "SYMBOL_SEARCH",
                "keywords": query,
                "apikey": settings.alpha_vantage_api_key,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return [item for item in payload.get("bestMatches", []) if isinstance(item, dict)]


def parse_quote(
    symbol: str, quote: dict[str, str], collected_at: datetime | None = None
) -> StockPrice:
    market_timestamp = datetime.strptime(quote["07. latest trading day"], "%Y-%m-%d").replace(
        tzinfo=UTC
    )
    return StockPrice(
        symbol=symbol,
        price=Decimal(quote["05. price"]),
        open=Decimal(quote["02. open"]) if quote.get("02. open") else None,
        high=Decimal(quote["03. high"]) if quote.get("03. high") else None,
        low=Decimal(quote["04. low"]) if quote.get("04. low") else None,
        previous_close=Decimal(quote["08. previous close"])
        if quote.get("08. previous close")
        else None,
        change=Decimal(quote["09. change"]) if quote.get("09. change") else None,
        change_percent=Decimal(quote["10. change percent"].rstrip("%"))
        if quote.get("10. change percent")
        else None,
        volume=int(quote["06. volume"]) if quote.get("06. volume") else None,
        market_timestamp=market_timestamp,
        collected_at=collected_at or datetime.now(UTC),
        data_source="alpha_vantage",
        data_freshness="delayed",
    )


def collect_stocks(
    session: Session, provider: AlphaVantageProvider | None = None
) -> tuple[int, int]:
    symbols = [
        row.symbol
        for row in session.scalars(select(StockWatchlist).where(StockWatchlist.enabled)).all()
    ]
    if not symbols:
        return 0, 0
    provider = provider or AlphaVantageProvider()
    inserted = 0
    try:
        for symbol in symbols:
            if not SYMBOL_RE.fullmatch(symbol):
                continue
            quote = provider.get_quote(symbol)
            snapshot = parse_quote(symbol, quote)
            duplicate = session.scalar(
                select(StockPrice.id).where(
                    StockPrice.symbol == symbol,
                    StockPrice.market_timestamp == snapshot.market_timestamp,
                )
            )
            if duplicate is None:
                session.add(snapshot)
                inserted += 1
        session.flush()
        return len(symbols), inserted
    finally:
        if provider is not None and provider._owned_client:
            provider.close()
