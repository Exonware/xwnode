"""
#exonware/xwnode/src/exonware/xwnode/common/caching/contracts.py
Cache adapter interface and contracts.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.1
Generation Date: November 4, 2025
"""

from typing import Any, Optional, Protocol, runtime_checkable
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
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    @property

    def total_requests(self) -> int:
        """Total cache requests."""
        return self.hits + self.misses

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': self.size,
            'max_size': self.max_size,
            'evictions': self.evictions,
            'hit_rate': self.hit_rate,
            'total_requests': self.total_requests
        }
@runtime_checkable

class ICacheAdapter(Protocol):
    """
    Adapter interface for cache implementations.
    Provides a unified interface for different cache strategies,
    wrapping xwsystem.caching implementations.
    """

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        Args:
            key: Cache key
        Returns:
            Cached value or None if not found
        """
        ...

    def put(self, key: str, value: Any) -> None:
        """
        Store value in cache.
        Args:
            key: Cache key
            value: Value to cache
        """
        ...

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        Args:
            key: Cache key
        Returns:
            True if deleted, False if not found
        """
        ...

    def clear(self) -> None:
        """Clear all cached entries."""
        ...

    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.
        Returns:
            CacheStats object with performance metrics
        """
        ...

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        Args:
            pattern: Pattern to match (e.g., "user:*")
        Returns:
            Number of entries invalidated
        """
        ...

    def contains(self, key: str) -> bool:
        """
        Check if key exists in cache.
        Args:
            key: Cache key
        Returns:
            True if key exists
        """
        return self.get(key) is not None

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """
        Get multiple values from cache.
        Args:
            keys: List of cache keys
        Returns:
            Dictionary of key-value pairs for found entries
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def put_many(self, items: dict[str, Any]) -> None:
        """
        Store multiple values in cache.
        Args:
            items: Dictionary of key-value pairs to cache
        """
        for key, value in items.items():
            self.put(key, value)
@runtime_checkable

class ICacheFactory(Protocol):
    """Factory interface for creating cache adapters."""

    def create_cache(
        self,
        component: str,
        size: int,
        **options
    ) -> ICacheAdapter:
        """
        Create a cache adapter instance.
        Args:
            component: Component name (e.g., "graph", "traversal")
            size: Maximum cache size
            **options: Additional cache-specific options
        Returns:
            Cache adapter instance
        """
        ...
@runtime_checkable

class ICacheStrategyManager(Protocol):
    """
    Interface for cache strategy manager.
    Provides management for multiple cache strategies (LRU, LFU, FIFO, TTL).
    """

    def get_cache(
        self,
        strategy: str = "lru",
        max_size: int = 1000,
        **options
    ) -> ICacheAdapter:
        """
        Get cache instance with specified strategy.
        Args:
            strategy: Cache strategy ("lru", "lfu", "fifo", "ttl")
            max_size: Maximum cache size
            **options: Additional strategy-specific options
        Returns:
            Cache adapter instance
        """
        ...

    def switch_strategy(
        self,
        cache_id: str,
        new_strategy: str,
        **options
    ) -> ICacheAdapter:
        """
        Switch cache to new strategy.
        Args:
            cache_id: Cache identifier
            new_strategy: New strategy name
            **options: Additional options
        Returns:
            New cache adapter instance
        """
        ...
@runtime_checkable

class ICacheMetrics(Protocol):
    """
    Interface for cache metrics.
    Provides cache performance metrics (hit/miss ratios, eviction rates).
    """

    def get_metrics(self, cache_id: Optional[str] = None) -> dict[str, Any]:
        """
        Get cache metrics.
        Args:
            cache_id: Optional cache identifier (None = all caches)
        Returns:
            Dictionary with cache metrics
        """
        ...

    def reset_metrics(self, cache_id: Optional[str] = None) -> None:
        """
        Reset cache metrics.
        Args:
            cache_id: Optional cache identifier (None = reset all)
        """
        ...
