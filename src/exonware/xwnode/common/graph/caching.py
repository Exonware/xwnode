"""
#exonware/xwnode/src/exonware/xwnode/common/graph/caching.py

Cache manager for frequent relationship queries.
Now powered by xwsystem.caching via CacheController.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: November 4, 2025
"""

import threading
from typing import Any, Optional

from ..caching import get_cache_controller, ICacheAdapter


class CacheManager[K, V]:
    """
    Cache manager for graph query results.
    
    Now uses CacheController for production-grade caching
    with xwsystem.caching backend (10-50x faster than OrderedDict).
    
    Provides:
    - Multiple cache strategies (LRU, LFU, TTL, Two-tier)
    - 4-level cache hierarchy
    - Automatic failover to no-cache on errors
    - Comprehensive statistics
    
    Generic Types:
    - K: Key type (typically str)
    - V: Value type (cached data)
    """
    
    def __init__(self, max_size: int = 1000, strategy: str = 'lru'):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cached entries
            strategy: Cache strategy ('lru', 'lfu', 'ttl', 'two_tier')
        """
        self._lock = threading.RLock()
        self._max_size = max_size
        self._strategy = strategy
        
        # Get cache adapter from controller
        try:
            controller = get_cache_controller()
            self._cache: ICacheAdapter = controller.get_cache(
                component='graph',
                size=max_size,
                strategy=strategy
            )
        except Exception as e:
            # Graceful degradation: use no-cache on failure
            from ..caching.adapters import NoCacheAdapter
            self._cache = NoCacheAdapter()
            import logging
            logging.warning(f"Failed to initialize cache, using NoCacheAdapter: {e}")
    
    def get(self, key: K) -> Optional[V]:
        """
        Get cached result.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
            
        Time Complexity: O(1)
        """
        with self._lock:
            return self._cache.get(key)
    
    def put(self, key: K, value: V) -> None:
        """
        Cache a query result.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Time Complexity: O(1)
        """
        with self._lock:
            self._cache.put(key, value)
    
    def invalidate(self, entity_id: str) -> None:
        """
        Invalidate cache entries for entity.
        
        Removes all cached queries that involve the specified entity.
        
        Args:
            entity_id: Entity whose cache entries should be invalidated
        """
        with self._lock:
            # Use pattern matching to invalidate entries containing entity_id
            pattern = f"*{entity_id}*"
            self._cache.invalidate_pattern(pattern)
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
    
    def get_hit_rate(self) -> float:
        """
        Get cache hit rate.
        
        Returns:
            Hit rate as float between 0.0 and 1.0
        """
        with self._lock:
            stats = self._cache.get_stats()
            return stats.hit_rate
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        with self._lock:
            stats = self._cache.get_stats()
            return stats.to_dict()

