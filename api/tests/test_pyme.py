"""PYME endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import FakeDB


def test_pyme_proporcion(client: TestClient, fake_db: FakeDB) -> None:
    fake_db._fetchrow_result = {"pyme": 132479, "total": 1003902}
    res = client.get("/api/v1/pyme/proporcion")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 132479
    assert body["total"] == 1003902
    assert 13.0 < body["pct"] < 14.0
