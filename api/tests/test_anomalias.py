"""Anomalías endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.utils.cache import clear_cache
from tests.conftest import FakeDB


def test_top_anomalias_sin_data(client: TestClient, fake_db: FakeDB) -> None:
    clear_cache()
    fake_db._fetchrow_result = {"media": 0.0, "desv": 0.0}
    res = client.get("/api/v1/anomalias/financieras")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 0


def test_validar_no_existe(client: TestClient, fake_db: FakeDB) -> None:
    fake_db._fetchrow_result = None
    res = client.get("/api/v1/anomalias/financieras/validar/CO1.PCCNTR.999999")
    assert res.status_code == 404
