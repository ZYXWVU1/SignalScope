import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.skipif(os.getenv("RUN_DATABASE_TESTS") != "1", reason="Requires migrated PostgreSQL")
def test_health_with_real_postgresql() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok"}
