"""
#exonware/xwnode/src/exonware/xwnode/common/caching/adapters.py

Cache adapters wrapping xwsystem.caching implementations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.30
Generation Date: November 4, 2025
"""

import fnmatch
import threading
from typing import Any, Optional, List, Dict

from exonware.xwsystem import get_logger
from exonware.xwsystem.caching import (
    LRUCache,
    LFUCache,
    TTLCache,
    TwoTierCache
)

from .contracts import ICacheAdapter, CacheStats

logger = get_logger(__name__)


class NoCacheAdapter(ICacheAdapter):
    """No-op cache adapter that disables caching."""
    
    def __init__(self, *args, **kwargs):
        """Initialize no-cache adapter."""
        self._stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """Always returns None (cache miss)."""
        self._stats.misses += 1
        return None
    
    def put(self, key: str, value: Any) -> None:
        """No-op."""
        pass
    
    def delete(self, key: str) -> bool:
        """Always returns False."""
        return False
    
    def clear(self) -> None:
        """No-op."""
        pass
    
    def get_stats(self) -> CacheStats:
        """Return empty stats."""
        return self._stats
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Always returns 0."""
        return 0


class LRUCacheAdapter(ICacheAdapter):
    """
    Adapter for xwsystem.caching.LRUCache.
    
    Provides O(1) get/put with automatic LRU eviction.
    """
    
    def __init__(self, size: int, namespace: str = "default", **kwargs):
        """
        Initialize LRU cache adapter.
        
        Args:
            size: Maximum cache size
            namespace: Cache namespace
            **kwargs: Additional options
        """
        self._cache = LRUCache(size=size, namespace=namespace)
        self._lock = threading.RLock()
        self._evictions = 0
        logger.debug(f"Initialized LRUCacheAdapter: size={size}, namespace={namespace}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from LRU cache."""
        with self._lock:
            return self._cache.get(key)
    
    def put(self, key: str, value: Any) -> None:
        """Store value in LRU cache."""
        with self._lock:
            # Track evictions if cache is full
            if len(self._cache) >= self._cache._max_size:
                self._evictions += 1
            self._cache.put(key, value)
    
    def delete(self, key: str) -> bool:
        """Delete value from LRU cache."""
        with self._lock:
            return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear LRU cache."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            cache_stats = self._cache.get_stats()
            return CacheStats(
                hits=cache_stats['hits'],
                misses=cache_stats['misses'],
                size=cache_stats['size'],
                max_size=cache_stats['max_size'],
                evictions=self._evictions
            )
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern."""
        with self._lock:
            keys_to_delete = [
                k for k in self._cache._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in keys_to_delete:
                self._cache.delete(key)
            return len(keys_to_delete)


class LFUCacheAdapter(ICacheAdapter):
    """
    Adapter for xwsystem.caching.LFUCache.
    
    Provides O(1) get/put with frequency-based eviction.
    """
    
    def __init__(self, size: int, namespace: str = "default", **kwargs):
        """
        Initialize LFU cache adapter.
        
        Args:
            size: Maximum cache size
            namespace: Cache namespace
            **kwargs: Additional options
        """
        self._cache = LFUCache(size=size, namespace=namespace)
        self._lock = threading.RLock()
        self._evictions = 0
        logger.debug(f"Initialized LFUCacheAdapter: size={size}, namespace={namespace}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from LFU cache."""
        with self._lock:
            return self._cache.get(key)
    
    def put(self, key: str, value: Any) -> None:
        """Store value in LFU cache."""
        with self._lock:
            # Track evictions if cache is full
            if len(self._cache) >= self._cache._max_size:
                self._evictions += 1
            self._cache.put(key, value)
    
    def delete(self, key: str) -> bool:
        """Delete value from LFU cache."""
        with self._lock:
            return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear LFU cache."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            cache_stats = self._cache.get_stats()
            return CacheStats(
                hits=cache_stats['hits'],
                misses=cache_stats['misses'],
                size=cache_stats['size'],
                max_size=cache_stats['max_size'],
                evictions=self._evictions
            )
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern."""
        with self._lock:
            keys_to_delete = [
                k for k in self._cache._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in keys_to_delete:
                self._cache.delete(key)
            return len(keys_to_delete)


class TTLCacheAdapter(ICacheAdapter):
    """
    Adapter for xwsystem.caching.TTLCache.
    
    Provides time-based expiration for cached entries.
    """
    
    def __init__(self, size: int, ttl: int = 300, namespace: str = "default", **kwargs):
        """
        Initialize TTL cache adapter.
        
        Args:
            size: Maximum cache size
            ttl: Time-to-live in seconds
            namespace: Cache namespace
            **kwargs: Additional options
        """
        self._cache = TTLCache(size=size, ttl=ttl, namespace=namespace)
        self._lock = threading.RLock()
        self._evictions = 0
        logger.debug(f"Initialized TTLCacheAdapter: size={size}, ttl={ttl}, namespace={namespace}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from TTL cache."""
        with self._lock:
            return self._cache.get(key)
    
    def put(self, key: str, value: Any) -> None:
        """Store value in TTL cache."""
        with self._lock:
            # Track evictions if cache is full
            if len(self._cache) >= self._cache._max_size:
                self._evictions += 1
            self._cache.put(key, value)
    
    def delete(self, key: str) -> bool:
        """Delete value from TTL cache."""
        with self._lock:
            return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear TTL cache."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            cache_stats = self._cache.get_stats()
            return CacheStats(
                hits=cache_stats['hits'],
                misses=cache_stats['misses'],
                size=cache_stats['size'],
                max_size=cache_stats['max_size'],
                evictions=self._evictions
            )
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern."""
        with self._lock:
            keys_to_delete = [
                k for k in self._cache._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in keys_to_delete:
                self._cache.delete(key)
            return len(keys_to_delete)


class TwoTierCacheAdapter(ICacheAdapter):
    """
    Adapter for xwsystem.caching.TwoTierCache.
    
    Provides memory + disk caching for large datasets.
    """
    
    def __init__(
        self,
        size: int,
        disk_size: int = 10000,
        disk_cache_dir: Optional[str] = None,
        namespace: str = "default",
        **kwargs
    ):
        """
        Initialize two-tier cache adapter.
        
        Args:
            size: Memory cache size
            disk_size: Disk cache size
            disk_cache_dir: Disk cache directory
            namespace: Cache namespace
            **kwargs: Additional options
        """
        self._cache = TwoTierCache(
            namespace=namespace,
            memory_size=size,
            disk_size=disk_size,
            disk_cache_dir=disk_cache_dir
        )
        self._lock = threading.RLock()
        self._evictions = 0
        logger.debug(f"Initialized TwoTierCacheAdapter: memory_size={size}, "
                    f"disk_size={disk_size}, namespace={namespace}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from two-tier cache."""
        with self._lock:
            return self._cache.get(key)
    
    def put(self, key: str, value: Any) -> None:
        """Store value in two-tier cache."""
        with self._lock:
            self._cache.put(key, value)
    
    def delete(self, key: str) -> bool:
        """Delete value from two-tier cache."""
        with self._lock:
            return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear two-tier cache."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            cache_stats = self._cache.get_stats()
            return CacheStats(
                hits=cache_stats['memory_hits'] + cache_stats['disk_hits'],
                misses=cache_stats['misses'],
                size=cache_stats['memory_size'] + cache_stats['disk_size'],
                max_size=self._cache._memory_size + self._cache._disk_size,
                evictions=self._evictions
            )
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern."""
        with self._lock:
            count = 0
            # Invalidate from memory cache
            memory_keys = [
                k for k in self._cache._memory_cache._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in memory_keys:
                self._cache.delete(key)
                count += 1
            return count

