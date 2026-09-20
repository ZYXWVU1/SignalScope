from datetime import UTC, datetime
from decimal import Decimal

from app.collectors.gaming import parse_public_html
from app.collectors.news import article_hash, classify_article
from app.collectors.stocks import parse_quote


def test_stock_quote_normalization_preserves_delayed_freshness() -> None:
    row = parse_quote(
        "NVDA",
        {
            "05. price": "120.5000",
            "02. open": "119.0000",
            "03. high": "121.0000",
            "04. low": "118.5000",
            "06. volume": "1000",
            "07. latest trading day": "2026-09-20",
            "08. previous close": "119.5000",
            "09. change": "1.0000",
            "10. change percent": "0.84%",
        },
        collected_at=datetime(2026, 9, 20, tzinfo=UTC),
    )
    assert row.symbol == "NVDA"
    assert row.price == Decimal("120.5000")
    assert row.change_percent == Decimal("0.84")
    assert row.data_freshness == "delayed"


def test_news_classification_is_rule_based_and_hash_is_stable() -> None:
    assert classify_article("OpenAI ships a new LLM", "AI tooling") == "AI"
    assert classify_article("Local weather forecast", "No technology") is None
    assert article_hash("A title", "Source", "https://example.com/a") == article_hash(
        " A  title ", "source", "https://example.com/a"
    )


def test_xiaoheihe_parser_accepts_public_json_ld_only() -> None:
    html = """
    <html><script type="application/ld+json">
    {"@type":"Article","headline":"Public game post","url":"/post/123",
     "description":"A public summary","datePublished":"2026-09-20T12:00:00Z",
     "author":{"name":"Display name"},"image":"https://img.example/post.jpg"}
    </script></html>
    """
    records = parse_public_html(html, "https://xiaoheihe.cn/")
    assert records == [
        {
            "external_id": "https://xiaoheihe.cn/post/123",
            "title": "Public game post",
            "url": "https://xiaoheihe.cn/post/123",
            "summary": "A public summary",
            "author": "Display name",
            "image_url": "https://img.example/post.jpg",
            "published_at": datetime(2026, 9, 20, 12, tzinfo=UTC),
            "game": None,
            "likes": None,
            "comments": None,
            "views": None,
        }
    ]


def test_xiaoheihe_parser_does_not_invent_html_records() -> None:
    assert (
        parse_public_html(
            "<html><article>Visible but unstructured</article></html>", "https://xiaoheihe.cn/"
        )
        == []
    )
