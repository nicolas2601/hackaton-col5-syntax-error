"""Health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["db"] is True
    assert "version" in body
    assert "snapshot" in body


def test_root(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["docs"] == "/docs"
    assert body["health"] == "/health"
