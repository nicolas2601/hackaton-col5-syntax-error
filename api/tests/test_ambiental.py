"""Ambiental endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.utils.cache import clear_cache
from tests.conftest import FakeDB


def test_total_ambiental(client: TestClient, fake_db: FakeDB) -> None:
    clear_cache()
    fake_db._fetchrow_result = {
        "amb_count": 12500,
        "total": 1003902,
        "valor_total": 5.5e12,
    }
    res = client.get("/api/v1/ambiental/total")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 12500
    assert body["pct"] > 0


def test_anticipos(client: TestClient, fake_db: FakeDB) -> None:
    clear_cache()
    fake_db._fetchrow_result = {
        "ant_count": 45000,
        "total": 1003902,
        "total_anticipos": 2.1e12,
    }
    res = client.get("/api/v1/ambiental/anticipos")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 45000
