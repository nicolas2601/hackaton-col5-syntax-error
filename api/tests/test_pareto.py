"""Pareto endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.utils.cache import clear_cache
from tests.conftest import FakeDB


def test_pareto_quintiles(client: TestClient, fake_db: FakeDB) -> None:
    clear_cache()
    fake_db._fetch_results = [
        {"quintil": 1, "entidades": 1234, "dinero_total": 1.5e13},
        {"quintil": 2, "entidades": 1234, "dinero_total": 3.0e12},
        {"quintil": 3, "entidades": 1234, "dinero_total": 1.5e12},
        {"quintil": 4, "entidades": 1234, "dinero_total": 7.5e11},
        {"quintil": 5, "entidades": 1234, "dinero_total": 2.5e11},
    ]
    res = client.get("/api/v1/pareto/entidades")
    assert res.status_code == 200
    body = res.json()
    assert len(body["quintiles"]) == 5
    # quintil 1 debe concentrar más dinero que el resto
    assert body["quintiles"][0]["pct_dinero"] > body["quintiles"][4]["pct_dinero"]
