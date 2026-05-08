"""Departamentos endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import FakeDB


def test_top_deptos(client: TestClient, fake_db: FakeDB) -> None:
    fake_db._fetch_results = [
        {"nombre": "Bogotá D.C.", "contratos": 250000, "valor_total": 1.5e13},
        {"nombre": "Antioquia", "contratos": 89432, "valor_total": 2.4e13},
    ]
    res = client.get("/api/v1/departamentos/top")
    assert res.status_code == 200
    assert res.json()["count"] == 2


def test_depto_no_existe(client: TestClient, fake_db: FakeDB) -> None:
    fake_db._fetchrow_result = {"contratos": 0, "valor_total": 0}
    res = client.get("/api/v1/departamentos/Atlantida")
    assert res.status_code == 404
