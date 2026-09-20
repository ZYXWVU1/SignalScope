from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_health_requires_ready_database() -> None:
    with patch("app.main.check_database") as check, TestClient(app) as client:
        response = client.get("/health")
    check.assert_called_once()
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_outage_is_reported_without_leaking_credentials() -> None:
    with patch("app.main.check_database", side_effect=RuntimeError("secret-password")):
        with TestClient(app) as client:
            response = client.get("/health")
            assert client.get("/live").status_code == 200
    assert response.status_code == 503
    assert "secret-password" not in response.text


def test_cors_does_not_allow_unconfigured_origin() -> None:
    with TestClient(app) as client:
        response = client.get("/live", headers={"Origin": "https://untrusted.example"})
    assert "access-control-allow-origin" not in response.headers
