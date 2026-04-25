"""
#exonware/xwnode/src/exonware/xwnode/common/caching/contracts.py
xwnode cache contracts (thin surface over exonware.xwsystem.caching engines).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.26
"""

from typing import Any, Protocol, runtime_checkable
from dataclasses import dataclass


@dataclass
class CacheStats:
    """Statistics for cache performance."""

    hits: int = 0
    misses: int = 0
    size: int = 0
    max_size: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": self.size,
            "max_size": self.max_size,
            "evictions": self.evictions,
            "hit_rate": self.hit_rate,
            "total_requests": self.total_requests,
        }


@runtime_checkable
class ICacheAdapter(Protocol):
    """Unified get/put cache API wrapping xwsystem.caching backends."""

    def get(self, key: str) -> Any | None: ...
    def put(self, key: str, value: Any) -> None: ...
    def delete(self, key: str) -> bool: ...
    def clear(self) -> None: ...
    def get_stats(self) -> CacheStats: ...
    def invalidate_pattern(self, pattern: str) -> int: ...

    def contains(self, key: str) -> bool:
        return self.get(key) is not None

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def put_many(self, items: dict[str, Any]) -> None:
        for key, value in items.items():
            self.put(key, value)


@runtime_checkable
class ICacheFactory(Protocol):
    def create_cache(
        self, component: str, size: int, **options: Any
    ) -> ICacheAdapter: ...


@runtime_checkable
class ICacheStrategyManager(Protocol):
    def get_cache(
        self, strategy: str = "lru", max_size: int = 1000, **options: Any
    ) -> ICacheAdapter: ...

    def switch_strategy(
        self, cache_id: str, new_strategy: str, **options: Any
    ) -> ICacheAdapter: ...


@runtime_checkable
class ICacheMetrics(Protocol):
    def get_metrics(self, cache_id: str | None = None) -> dict[str, Any]: ...
    def reset_metrics(self, cache_id: str | None = None) -> None: ...
