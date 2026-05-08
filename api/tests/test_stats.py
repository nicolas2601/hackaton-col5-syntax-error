"""Stats endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import FakeDB


def test_total(client: TestClient, fake_db: FakeDB) -> None:
    fake_db._fetchval_result = 1003902
    res = client.get("/api/v1/stats/total")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1003902
    assert body["snapshot"]


def test_columnas(client: TestClient) -> None:
    res = client.get("/api/v1/stats/columnas")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 84
    assert "Nombre Entidad" in body["columnas"]
    assert "Valor del Contrato" in body["columnas"]


def test_anios(client: TestClient, fake_db: FakeDB) -> None:
    fake_db._fetch_results = [
        {"anio": 2024, "contratos": 412350},
        {"anio": 2025, "contratos": 591552},
    ]
    res = client.get("/api/v1/stats/anios")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 2
    assert body["items"][0]["anio"] == 2024
