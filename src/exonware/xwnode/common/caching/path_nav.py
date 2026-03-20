#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/caching/path_nav.py
Path navigation result cache (xwnode-specific); backend is exonware.xwsystem.caching.create_cache.
"""

import threading
from typing import Any

from exonware.xwsystem import get_logger
from exonware.xwsystem.caching import create_cache

logger = get_logger(__name__)


class PathNavigationCache:
    """
    Cache for XWNode dotted-path lookup results.
    Uses xwsystem create_cache (default LRU engine) with prefix invalidation.
    """

    def __init__(self, max_size: int = 512) -> None:
        self._max_size = max_size
        self._cache = create_cache(
            capacity=max_size,
            namespace="xwnode",
            name="path_navigation_cache",
        )
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }

    def get(self, path: str) -> Any | None:
        with self._lock:
            value = self._cache.get(path)
            if value is not None:
                self._stats["hits"] += 1
                logger.debug("Path cache hit: %s", path)
                return value
            self._stats["misses"] += 1
            return None

    def put(self, path: str, value: Any) -> None:
        with self._lock:
            was_full = self._cache.is_full()
            key_existed = self._cache.get(path) is not None
            self._cache.put(path, value)
            if was_full and not key_existed and self._cache.size() >= self._max_size:
                cache_stats = self._cache.get_stats()
                xwsystem_evictions = cache_stats.get("evictions", 0)
                if xwsystem_evictions > 0:
                    self._stats["evictions"] = max(
                        self._stats["evictions"], xwsystem_evictions
                    )

    def invalidate(self, path: str | None = None) -> int:
        with self._lock:
            if path is None:
                count = self._cache.size()
                self._cache.clear()
                self._stats["invalidations"] += count
                return count
            invalidated = 0
            paths_to_remove = []
            for cached_path in self._cache.keys():
                if cached_path == path or cached_path.startswith(path + "."):
                    paths_to_remove.append(cached_path)
            for p in paths_to_remove:
                if self._cache.delete(p):
                    invalidated += 1
            self._stats["invalidations"] += invalidated
            return invalidated

    def clear(self) -> None:
        with self._lock:
            count = self._cache.size()
            self._cache.clear()
            self._stats["invalidations"] += count

    def __contains__(self, path: str) -> bool:
        with self._lock:
            return self._cache.get(path) is not None

    def __getitem__(self, path: str) -> Any:
        value = self.get(path)
        if value is None:
            raise KeyError(path)
        return value

    def __setitem__(self, path: str, value: Any) -> None:
        self.put(path, value)

    def __delitem__(self, path: str) -> None:
        with self._lock:
            if not self._cache.delete(path):
                raise KeyError(path)
            self._stats["invalidations"] += 1

    def __len__(self) -> int:
        with self._lock:
            return self._cache.size()

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests if total_requests > 0 else 0.0
            )
            cache_stats = self._cache.get_stats()
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": cache_stats.get("evictions", self._stats["evictions"]),
                "invalidations": self._stats["invalidations"],
                "size": self._cache.size(),
                "max_size": self._max_size,
                "hit_rate": hit_rate,
                "xwsystem_cache_stats": cache_stats,
            }

    def reset_stats(self) -> None:
        with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "invalidations": 0,
            }
