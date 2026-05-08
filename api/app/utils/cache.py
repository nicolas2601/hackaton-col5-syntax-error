"""Cache TTL en memoria — para queries pesadas (Pareto, Top X)."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")

_cache: dict[str, tuple[float, Any]] = {}
_lock = asyncio.Lock()


def ttl_cache(seconds: int = 300) -> Callable:
    """Decorator de cache async con TTL."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            key = f"{func.__module__}.{func.__name__}:{args!r}:{kwargs!r}"
            now = time.monotonic()
            async with _lock:
                cached = _cache.get(key)
                if cached and cached[0] > now:
                    return cached[1]  # type: ignore[no-any-return]
            result = await func(*args, **kwargs)
            async with _lock:
                _cache[key] = (now + seconds, result)
            return result

        return wrapper

    return decorator


def clear_cache() -> None:
    """Wipe del cache — útil en tests / endpoint admin."""
    _cache.clear()
