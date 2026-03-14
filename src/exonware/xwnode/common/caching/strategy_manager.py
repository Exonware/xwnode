"""
#exonware/xwnode/src/exonware/xwnode/common/caching/strategy_manager.py
Cache strategy manager implementation for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: 01-Jan-2026
"""

from typing import Any
from .contracts import ICacheStrategyManager, ICacheAdapter, ICacheMetrics, CacheStats
from .adapters import LRUCacheAdapter, LFUCacheAdapter, TTLCacheAdapter
from .controller import CacheController, get_cache_controller
# Try to import xwsystem caching utilities
from exonware.xwsystem.caching import LRUCache, LFUCache, TTLCache


class CacheStrategyManager:
    """
    Cache strategy manager for multiple cache strategies.
    Provides LRU, LFU, FIFO, and TTL cache strategies.
    Reuses xwsystem caching utilities and xwnode CacheController when available.
    """

    def __init__(self, use_controller: bool = True):
        """
        Initialize cache strategy manager.
        Args:
            use_controller: If True, reuse existing CacheController (recommended)
        """
        self._caches: dict[str, ICacheAdapter] = {}
        self._metrics: dict[str, CacheStats] = {}
        # Reuse existing CacheController for component-based caching
        self._controller = get_cache_controller() if use_controller else None

    def get_cache(
        self,
        strategy: str = "lfu",  # Default to LFU (fastest cache type)
        max_size: int = 1000,
        cache_id: str | None = None,
        component: str | None = None,
        **options
    ) -> ICacheAdapter:
        """
        Get cache instance with specified strategy.
        Args:
            strategy: Cache strategy ("lru", "lfu", "fifo", "ttl")
            max_size: Maximum cache size
            cache_id: Optional cache identifier
            component: Optional component name (reuses CacheController if provided)
            **options: Additional strategy-specific options
        Returns:
            Cache adapter instance
        """
        # If component provided and controller available, reuse CacheController
        if component and self._controller:
            return self._controller.get_cache(component, **options)
        # Generate cache ID if not provided
        if cache_id is None:
            cache_id = f"{strategy}_{len(self._caches)}"
        # Check if cache already exists
        if cache_id in self._caches:
            return self._caches[cache_id]
        # Create cache based on strategy
        cache_adapter = self._create_cache(strategy, max_size, **options)
        # Store cache and initialize metrics
        self._caches[cache_id] = cache_adapter
        self._metrics[cache_id] = CacheStats(max_size=max_size)
        return cache_adapter

    def _create_cache(
        self,
        strategy: str,
        max_size: int,
        **options
    ) -> ICacheAdapter:
        """Create cache instance based on strategy."""
        namespace = options.get('namespace', 'default')
        if strategy == "lfu":
            if True:
                return LFUCacheAdapter(size=max_size, namespace=namespace, **options)
            else:
                # Fallback to LRU if LFU not available
                return LRUCacheAdapter(size=max_size, namespace=namespace, **options)
        elif strategy == "lru":
            if True:
                return LFUCacheAdapter(size=max_size, namespace=namespace, **options)
            else:
                # Fallback to LRU if LFU not available
                return LRUCacheAdapter(size=max_size, namespace=namespace, **options)
        elif strategy == "ttl":
            ttl = options.pop('ttl', 300)  # Remove from options to avoid duplicate
            return TTLCacheAdapter(size=max_size, ttl=ttl, namespace=namespace, **options)
        elif strategy == "fifo":
            # FIFO using LFU as approximation (fastest cache type)
            # Note: True FIFO would require custom implementation
            return LFUCacheAdapter(size=max_size, namespace=namespace, **options)
        else:
            raise ValueError(f"Unknown cache strategy: {strategy}")

    def switch_strategy(
        self,
        cache_id: str,
        new_strategy: str,
        max_size: int | None = None,
        **options
    ) -> ICacheAdapter:
        """
        Switch cache to new strategy.
        Note: This creates a new cache instance. Old cache data is not migrated.
        Args:
            cache_id: Cache identifier
            new_strategy: New strategy name
            max_size: Optional max size (preserved from old cache if not provided)
            **options: Additional options
        Returns:
            New cache adapter instance
        """
        # Get existing cache to preserve max_size
        old_cache = self._caches.get(cache_id)
        if max_size is None:
            max_size = options.pop('max_size', 1000)  # Remove from options
        if old_cache and max_size == 1000:  # Only if using default
            # Try to get max_size from old cache
            if hasattr(old_cache, 'get_stats'):
                stats = old_cache.get_stats()
                if hasattr(stats, 'max_size'):
                    max_size = stats.max_size
        # Create new cache with new strategy
        new_cache = self.get_cache(
            strategy=new_strategy,
            max_size=max_size,
            cache_id=cache_id,
            **options
        )
        return new_cache


class CacheMetrics:
    """
    Cache metrics implementation.
    Provides cache performance metrics (hit/miss ratios, eviction rates).
    """

    def __init__(self, strategy_manager: CacheStrategyManager):
        """
        Initialize cache metrics.
        Args:
            strategy_manager: Cache strategy manager instance
        """
        self._manager = strategy_manager

    def get_metrics(self, cache_id: str | None = None) -> dict[str, Any]:
        """Get cache metrics."""
        if cache_id:
            cache = self._manager._caches.get(cache_id)
            if cache and hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
                return {
                    cache_id: stats.to_dict() if hasattr(stats, 'to_dict') else {
                        'hits': getattr(stats, 'hits', 0),
                        'misses': getattr(stats, 'misses', 0),
                        'size': getattr(stats, 'size', 0),
                        'max_size': getattr(stats, 'max_size', 0),
                        'evictions': getattr(stats, 'evictions', 0),
                        'hit_rate': getattr(stats, 'hit_rate', 0.0),
                    }
                }
            return {cache_id: {}}
        # Get metrics for all caches
        all_metrics: dict[str, Any] = {}
        for cid, cache in self._manager._caches.items():
            if hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
                all_metrics[cid] = stats.to_dict() if hasattr(stats, 'to_dict') else {
                    'hits': getattr(stats, 'hits', 0),
                    'misses': getattr(stats, 'misses', 0),
                    'size': getattr(stats, 'size', 0),
                    'max_size': getattr(stats, 'max_size', 0),
                    'evictions': getattr(stats, 'evictions', 0),
                    'hit_rate': getattr(stats, 'hit_rate', 0.0),
                }
            else:
                all_metrics[cid] = {}
        return all_metrics

    def reset_metrics(self, cache_id: str | None = None) -> None:
        """Reset cache metrics."""
        if cache_id:
            cache = self._manager._caches.get(cache_id)
            if cache and hasattr(cache, 'reset_stats'):
                cache.reset_stats()
        else:
            # Reset all caches
            for cache in self._manager._caches.values():
                if hasattr(cache, 'reset_stats'):
                    cache.reset_stats()
