"""Pool asyncpg — singleton + lifecycle hooks."""

from __future__ import annotations

import asyncpg
import structlog

from app.config import get_settings

log = structlog.get_logger(__name__)


class Database:
    """Pool asyncpg encapsulado."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Inicializar el pool. Idempotente."""
        if self._pool is not None:
            return

        settings = get_settings()
        log.info(
            "db.connecting",
            min_size=settings.database_pool_min,
            max_size=settings.database_pool_max,
        )

        self._pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.database_pool_min,
            max_size=settings.database_pool_max,
            timeout=settings.database_timeout,
            command_timeout=settings.database_timeout,
            server_settings={
                "application_name": "secop-api",
                "jit": "off",
            },
        )
        log.info("db.connected")

    async def disconnect(self) -> None:
        """Cerrar el pool gracefully."""
        if self._pool is None:
            return
        await self._pool.close()
        self._pool = None
        log.info("db.disconnected")

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database pool no inicializado — llamar connect() primero")
        return self._pool

    async def fetch(self, query: str, *args: object) -> list[asyncpg.Record]:
        """SELECT múltiple."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args: object) -> asyncpg.Record | None:
        """SELECT una fila."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: object) -> object:
        """SELECT escalar."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def ping(self) -> bool:
        """Liveness check."""
        try:
            val = await self.fetchval("SELECT 1")
            return val == 1
        except Exception as exc:  # noqa: BLE001
            log.error("db.ping_failed", error=str(exc))
            return False


# Singleton global — inyectado vía Depends
db = Database()


async def get_db() -> Database:
    """FastAPI dependency."""
    return db
