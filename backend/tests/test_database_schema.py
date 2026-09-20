from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_database_health_reports_table_status_without_credentials() -> None:
    with (
        patch("app.main.check_database"),
        patch(
            "app.main.database_table_status",
            return_value={"alembic_version": True, "stock_watchlist": True},
        ),
    ):
        with TestClient(app) as client:
            response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "tables": {"alembic_version": True, "stock_watchlist": True},
    }
