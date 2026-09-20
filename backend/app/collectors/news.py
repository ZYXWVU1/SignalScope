import hashlib
import re
from datetime import UTC, datetime
from typing import cast

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import NewsArticle

CATEGORIES: dict[str, tuple[str, ...]] = {
    "AI": ("artificial intelligence", "machine learning", "llm", "openai", "anthropic"),
    "Hardware": ("hardware", "laptop", "smartphone", "device", "computer"),
    "Cybersecurity": ("cybersecurity", "security breach", "malware", "ransomware"),
    "Cloud": ("cloud computing", "aws", "azure", "google cloud", "data center"),
    "Semiconductors": ("nvidia", "amd", "intel", "gpu", "chip", "semiconductor"),
    "Startups": ("startup", "venture capital", "funding", "series a", "series b"),
    "Developer": ("programming", "developer", "software development", "github", "api"),
    "Consumer Tech": ("apple", "google", "microsoft", "consumer tech", "gaming console"),
}


class NewsApiProvider:
    endpoint = "https://newsapi.org/v2/everything"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=20, headers={"User-Agent": "SignalScope/1.0"})
        self._owned_client = client is None

    def close(self) -> None:
        if self._owned_client:
            self.client.close()

    def fetch_articles(self) -> list[dict[str, object]]:
        if not settings.news_api_key:
            raise RuntimeError("NEWS_API_KEY is not configured")
        response = self.client.get(
            self.endpoint,
            params={
                "q": (
                    "(technology OR artificial intelligence OR cybersecurity OR "
                    "semiconductor OR software)"
                ),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100,
                "apiKey": settings.news_api_key,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "ok":
            raise RuntimeError(str(payload.get("message", "NewsAPI request failed")))
        articles = payload.get("articles", [])
        return cast(list[dict[str, object]], articles) if isinstance(articles, list) else []


def classify_article(title: str, description: str | None) -> str | None:
    text = f"{title} {description or ''}".lower()
    for category, keywords in CATEGORIES.items():
        if any(re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text) for keyword in keywords):
            return category
    return None


def article_hash(title: str, source: str, url: str) -> str:
    value = " ".join(f"{title} {source} {url}".lower().split())
    return hashlib.sha256(value.encode()).hexdigest()


def parse_published_at(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def collect_news(session: Session, provider: NewsApiProvider | None = None) -> tuple[int, int]:
    provider = provider or NewsApiProvider()
    try:
        articles = provider.fetch_articles()
        inserted = 0
        for raw in articles:
            title = str(raw.get("title") or "").strip()
            url = str(raw.get("url") or "").strip()
            if not title or not url:
                continue
            source_value = raw.get("source")
            source_raw: dict[str, object] = source_value if isinstance(source_value, dict) else {}
            source = str(source_raw.get("name") or "Unknown")
            description = str(raw.get("description")) if raw.get("description") else None
            category = classify_article(title, description)
            if category is None:
                continue
            digest = article_hash(title, source, url)
            if session.scalar(select(NewsArticle.id).where(NewsArticle.content_hash == digest)):
                continue
            session.add(
                NewsArticle(
                    external_id=str(raw.get("url")),
                    source=source,
                    title=title,
                    description=description,
                    url=url,
                    image_url=str(raw.get("urlToImage")) if raw.get("urlToImage") else None,
                    author=str(raw.get("author")) if raw.get("author") else None,
                    category=category,
                    published_at=parse_published_at(raw.get("publishedAt")),
                    collected_at=datetime.now(UTC),
                    content_hash=digest,
                )
            )
            inserted += 1
        session.flush()
        return len(articles), inserted
    finally:
        if provider._owned_client:
            provider.close()
