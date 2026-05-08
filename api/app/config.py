"""Application settings — pydantic-settings con cache LRU."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings cargados desde .env / environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────
    app_name: str = Field(default="SECOP API")
    app_version: str = Field(default="0.1.0")
    app_env: str = Field(default="production")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # ── Server ────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=4)

    # ── Database ──────────────────────────────────────────
    database_url: str = Field(
        default="postgres://postgres:CHANGEME@localhost:5432/secop"
    )
    database_pool_min: int = Field(default=2)
    database_pool_max: int = Field(default=20)
    database_timeout: int = Field(default=30)

    # ── CORS ──────────────────────────────────────────────
    cors_origins: str = Field(
        default="https://panel.tikno.pro,http://localhost:3000"
    )

    # ── Rate limit ────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=100)

    # ── Cache ─────────────────────────────────────────────
    cache_ttl_seconds: int = Field(default=300)

    # ── Snapshot metadata ─────────────────────────────────
    data_snapshot_date: str = Field(default="2026-05-06")
    data_total_rows: int = Field(default=1_003_902)
    data_total_columns: int = Field(default=84)
    data_table_name: str = Field(default="contratos_2025")

    @property
    def cors_origin_list(self) -> list[str]:
        """Convertir CSV string a lista trimmed."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Singleton de settings."""
    return Settings()
