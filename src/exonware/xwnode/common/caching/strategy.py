"""
#exonware/xwnode/src/exonware/xwnode/common/caching/strategy.py
BaaS-oriented cache strategy manager (delegates engines to xwsystem via policy).
"""

from typing import Any

from .contracts import CacheStats, ICacheAdapter
from .policy import (
    cache_strategy_is_allowed,
    create_adapter_for_strategy,
    get_cache_controller,
)


class CacheStrategyManager:
    def __init__(self, use_controller: bool = True) -> None:
        self._caches: dict[str, ICacheAdapter] = {}
        self._metrics: dict[str, CacheStats] = {}
        self._controller = get_cache_controller() if use_controller else None

    def get_cache(
        self,
        strategy: str = "lfu",
        max_size: int = 1000,
        cache_id: str | None = None,
        component: str | None = None,
        **options: Any,
    ) -> ICacheAdapter:
        if component and self._controller:
            return self._controller.get_cache(component, **options)
        if cache_id is None:
            cache_id = f"{strategy}_{len(self._caches)}"
        if cache_id in self._caches:
            return self._caches[cache_id]
        cache_adapter = self._create_cache(strategy, max_size, **options)
        self._caches[cache_id] = cache_adapter
        self._metrics[cache_id] = CacheStats(max_size=max_size)
        return cache_adapter

    def _create_cache(
        self, strategy: str, max_size: int, **options: Any
    ) -> ICacheAdapter:
        if not cache_strategy_is_allowed(strategy):
            raise ValueError(f"Unknown cache strategy: {strategy}")
        namespace = options.pop("namespace", "default")
        return create_adapter_for_strategy(
            strategy, max_size, namespace=namespace, **options
        )

    def switch_strategy(
        self,
        cache_id: str,
        new_strategy: str,
        max_size: int | None = None,
        **options: Any,
    ) -> ICacheAdapter:
        old_cache = self._caches.get(cache_id)
        if max_size is None:
            max_size = int(options.pop("max_size", 1000))
        if old_cache and max_size == 1000 and hasattr(old_cache, "get_stats"):
            stats = old_cache.get_stats()
            if hasattr(stats, "max_size"):
                max_size = stats.max_size
        return self.get_cache(
            strategy=new_strategy,
            max_size=max_size,
            cache_id=cache_id,
            **options,
        )


class CacheMetrics:
    def __init__(self, strategy_manager: CacheStrategyManager) -> None:
        self._manager = strategy_manager

    def get_metrics(self, cache_id: str | None = None) -> dict[str, Any]:
        if cache_id:
            cache = self._manager._caches.get(cache_id)
            if cache and hasattr(cache, "get_stats"):
                stats = cache.get_stats()
                return {
                    cache_id: stats.to_dict()
                    if hasattr(stats, "to_dict")
                    else {
                        "hits": getattr(stats, "hits", 0),
                        "misses": getattr(stats, "misses", 0),
                        "size": getattr(stats, "size", 0),
                        "max_size": getattr(stats, "max_size", 0),
                        "evictions": getattr(stats, "evictions", 0),
                        "hit_rate": getattr(stats, "hit_rate", 0.0),
                    }
                }
            return {cache_id: {}}
        all_metrics: dict[str, Any] = {}
        for cid, cache in self._manager._caches.items():
            if hasattr(cache, "get_stats"):
                stats = cache.get_stats()
                all_metrics[cid] = (
                    stats.to_dict()
                    if hasattr(stats, "to_dict")
                    else {
                        "hits": getattr(stats, "hits", 0),
                        "misses": getattr(stats, "misses", 0),
                        "size": getattr(stats, "size", 0),
                        "max_size": getattr(stats, "max_size", 0),
                        "evictions": getattr(stats, "evictions", 0),
                        "hit_rate": getattr(stats, "hit_rate", 0.0),
                    }
                )
            else:
                all_metrics[cid] = {}
        return all_metrics

    def reset_metrics(self, cache_id: str | None = None) -> None:
        if cache_id:
            cache = self._manager._caches.get(cache_id)
            if cache and hasattr(cache, "reset_stats"):
                cache.reset_stats()
        else:
            for cache in self._manager._caches.values():
                if hasattr(cache, "reset_stats"):
                    cache.reset_stats()
