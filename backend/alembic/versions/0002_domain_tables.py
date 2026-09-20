"""Add stock, technology news, gaming, metrics, and collector run tables."""

import sqlalchemy as sa

from alembic import op

revision = "0002_domain_tables"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stock_watchlist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(16), nullable=False, unique=True),
        sa.Column("company_name", sa.String(255)),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stock_watchlist_symbol", "stock_watchlist", ["symbol"], unique=False)
    op.create_index("ix_stock_watchlist_enabled", "stock_watchlist", ["enabled"], unique=False)
    op.create_table(
        "stock_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("price", sa.Numeric(18, 6), nullable=False),
        sa.Column("open", sa.Numeric(18, 6)),
        sa.Column("high", sa.Numeric(18, 6)),
        sa.Column("low", sa.Numeric(18, 6)),
        sa.Column("previous_close", sa.Numeric(18, 6)),
        sa.Column("change", sa.Numeric(18, 6)),
        sa.Column("change_percent", sa.Numeric(12, 6)),
        sa.Column("volume", sa.BigInteger()),
        sa.Column("market_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_source", sa.String(64), nullable=False, server_default="alpha_vantage"),
        sa.Column("data_freshness", sa.String(32), nullable=False, server_default="delayed"),
        sa.UniqueConstraint("symbol", "market_timestamp", name="uq_stock_snapshot"),
    )
    op.create_index("ix_stock_prices_symbol", "stock_prices", ["symbol"], unique=False)
    op.create_index(
        "ix_stock_prices_market_timestamp", "stock_prices", ["market_timestamp"], unique=False
    )
    op.create_index(
        "ix_stock_prices_symbol_timestamp",
        "stock_prices",
        ["symbol", "market_timestamp"],
        unique=False,
    )
    op.create_table(
        "news_articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(255)),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("image_url", sa.String(2048)),
        sa.Column("author", sa.String(255)),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
    )
    op.create_index("ix_news_articles_category", "news_articles", ["category"], unique=False)
    op.create_index(
        "ix_news_articles_published_at", "news_articles", ["published_at"], unique=False
    )
    op.create_table(
        "gaming_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(255)),
        sa.Column("source", sa.String(64), nullable=False, server_default="xiaoheihe"),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("game", sa.String(255)),
        sa.Column("author", sa.String(255)),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("image_url", sa.String(2048)),
        sa.Column("likes", sa.Integer()),
        sa.Column("comments", sa.Integer()),
        sa.Column("views", sa.Integer()),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
    )
    op.create_index("ix_gaming_posts_game", "gaming_posts", ["game"], unique=False)
    op.create_index("ix_gaming_posts_published_at", "gaming_posts", ["published_at"], unique=False)
    op.create_table(
        "gaming_post_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gaming_post_id", sa.Integer(), nullable=False),
        sa.Column("likes", sa.Integer()),
        sa.Column("comments", sa.Integer()),
        sa.Column("views", sa.Integer()),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_gaming_post_metrics_gaming_post_id",
        "gaming_post_metrics",
        ["gaming_post_id"],
        unique=False,
    )
    op.create_table(
        "collector_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("collector", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("items_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
    )
    op.create_index("ix_collector_runs_collector", "collector_runs", ["collector"], unique=False)
    op.create_index("ix_collector_runs_status", "collector_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_table("collector_runs")
    op.drop_table("gaming_post_metrics")
    op.drop_table("gaming_posts")
    op.drop_table("news_articles")
    op.drop_table("stock_prices")
    op.drop_table("stock_watchlist")
