import hashlib
import json
import time
from datetime import UTC, datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import GamingPost, GamingPostMetric


def _number(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).replace(",", "").strip())
    except ValueError:
        return None


def _date(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_public_html(html: str, page_url: str) -> list[dict[str, object]]:
    """Parse only public JSON-LD Article records; no private endpoints or browser automation."""
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, object]] = []
    for node in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(node.string or node.get_text())
        except json.JSONDecodeError:
            continue
        candidates = payload if isinstance(payload, list) else [payload]
        for item in candidates:
            if not isinstance(item, dict) or item.get("@type") not in {
                "Article",
                "NewsArticle",
                "SocialMediaPosting",
            }:
                continue
            title = str(item.get("headline") or item.get("name") or "").strip()
            url = urljoin(page_url, str(item.get("url") or page_url))
            if not title:
                continue
            author = item.get("author")
            if isinstance(author, dict):
                author = author.get("name")
            image = item.get("image")
            if isinstance(image, list):
                image = image[0] if image else None
            records.append(
                {
                    "external_id": url,
                    "title": title,
                    "url": url,
                    "summary": item.get("description"),
                    "author": author,
                    "image_url": image,
                    "published_at": _date(item.get("datePublished")),
                    "game": None,
                    "likes": None,
                    "comments": None,
                    "views": None,
                }
            )
    return records


def gaming_hash(title: str, url: str) -> str:
    return hashlib.sha256(" ".join(f"{title} {url}".lower().split()).encode()).hexdigest()


class XiaoheihePublicProvider:
    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=20, headers={"User-Agent": "SignalScope/1.0"})
        self._owned_client = client is None

    def close(self) -> None:
        if self._owned_client:
            self.client.close()

    def fetch(self) -> list[dict[str, object]]:
        urls = list(settings.xhh_public_post_urls)
        if not urls:
            urls = [settings.xhh_public_feed_url]
        records: list[dict[str, object]] = []
        for index, url in enumerate(urls):
            if index:
                time.sleep(max(settings.xhh_request_delay_seconds, 0))
            response = self.client.get(url)
            response.raise_for_status()
            records.extend(parse_public_html(response.text, str(response.url)))
        return records


def collect_gaming(
    session: Session, provider: XiaoheihePublicProvider | None = None
) -> tuple[int, int]:
    provider = provider or XiaoheihePublicProvider()
    try:
        posts = provider.fetch()
        inserted = 0
        for raw in posts:
            title = str(raw.get("title") or "").strip()
            url = str(raw.get("url") or "").strip()
            if not title or not url:
                continue
            digest = gaming_hash(title, url)
            post = session.scalar(select(GamingPost).where(GamingPost.content_hash == digest))
            if post is None:
                post = GamingPost(
                    external_id=str(raw.get("external_id") or url),
                    source="xiaoheihe",
                    title=title,
                    game=raw.get("game"),
                    author=raw.get("author"),
                    url=url,
                    summary=raw.get("summary"),
                    image_url=raw.get("image_url"),
                    likes=_number(raw.get("likes")),
                    comments=_number(raw.get("comments")),
                    views=_number(raw.get("views")),
                    published_at=raw.get("published_at"),
                    collected_at=datetime.now(UTC),
                    content_hash=digest,
                )
                session.add(post)
                session.flush()
                inserted += 1
            session.add(
                GamingPostMetric(
                    gaming_post_id=post.id,
                    likes=post.likes,
                    comments=post.comments,
                    views=post.views,
                    recorded_at=datetime.now(UTC),
                )
            )
        session.flush()
        return len(posts), inserted
    finally:
        if provider._owned_client:
            provider.close()
