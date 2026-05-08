"""Pytest fixtures — mock DB para tests rápidos sin Postgres."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import Database, get_db
from app.main import app


class FakeDB(Database):
    """Database mockeado — devuelve fixtures predecibles."""

    def __init__(self) -> None:
        self._pool = MagicMock()
        self._fetch_results: list[Any] = []
        self._fetchrow_result: Any = None
        self._fetchval_result: Any = 0
        self.fetch = AsyncMock(side_effect=self._fetch)
        self.fetchrow = AsyncMock(side_effect=self._fetchrow)
        self.fetchval = AsyncMock(side_effect=self._fetchval)
        self.ping = AsyncMock(return_value=True)
        self.connect = AsyncMock()
        self.disconnect = AsyncMock()

    async def _fetch(self, *_: Any, **__: Any) -> list[Any]:
        return self._fetch_results

    async def _fetchrow(self, *_: Any, **__: Any) -> Any:
        return self._fetchrow_result

    async def _fetchval(self, *_: Any, **__: Any) -> Any:
        return self._fetchval_result


@pytest.fixture
def fake_db() -> FakeDB:
    return FakeDB()


@pytest.fixture
def client(fake_db: FakeDB) -> TestClient:
    """TestClient con DB mockeada."""
    app.dependency_overrides[get_db] = lambda: fake_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
