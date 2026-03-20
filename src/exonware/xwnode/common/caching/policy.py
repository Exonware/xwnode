"""
#exonware/xwnode/src/exonware/xwnode/common/caching/policy.py
xwnode cache policy: ICacheAdapter facades + singleton CacheController over xwsystem.
"""

from __future__ import annotations

import fnmatch
import threading
from contextlib import contextmanager
from typing import Any

from exonware.xwsystem import get_logger
from exonware.xwsystem.caching import TwoTierCache, create_cache
from exonware.xwsystem.caching.base import ACache
from exonware.xwsystem.caching.factory import CacheFactory, CacheType

from ...config import XWNodeConfig, get_config
from .contracts import CacheStats, ICacheAdapter

logger = get_logger(__name__)

_XWNODE_STRATEGY_EXTRAS: frozenset[str] = frozenset(
    {
        "xwsystem",
        "default",
        "auto",
        "two_tier",
        "none",
        "fifo",
    }
)


def list_xwsystem_cache_types() -> list[str]:
    names: set[str] = {ct.value for ct in CacheType}
    for k in CacheFactory._cache_types:
        names.add(k.value if hasattr(k, "value") else str(k).lower())
    names.update(_XWNODE_STRATEGY_EXTRAS)
    return sorted(names)


def cache_strategy_is_allowed(strategy: str) -> bool:
    s = (strategy or "").lower().strip()
    if s in _XWNODE_STRATEGY_EXTRAS:
        return True
    if s in {ct.value for ct in CacheType}:
        return True
    for k in CacheFactory._cache_types:
        key = k.value if hasattr(k, "value") else str(k).lower()
        if key == s:
            return True
    return False


def _acache_stats(cache: ACache, evictions_extra: int = 0) -> CacheStats:
    raw = cache.get_stats()
    max_size = int(raw.get("max_size", raw.get("capacity", getattr(cache, "capacity", 0))))
    return CacheStats(
        hits=int(raw.get("hits", 0)),
        misses=int(raw.get("misses", 0)),
        size=int(raw.get("size", cache.size())),
        max_size=max_size,
        evictions=int(raw.get("evictions", evictions_extra)),
    )


class NoCacheAdapter(ICacheAdapter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._stats = CacheStats()

    def get(self, key: str) -> Any | None:
        self._stats.misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        pass

    def delete(self, key: str) -> bool:
        return False

    def clear(self) -> None:
        pass

    def get_stats(self) -> CacheStats:
        return self._stats

    def invalidate_pattern(self, pattern: str) -> int:
        return 0


class _ACacheAdapterBase(ICacheAdapter):
    __slots__ = ("_cache", "_lock", "_evictions")

    def __init__(self, cache: ACache) -> None:
        self._cache = cache
        self._lock = threading.RLock()
        self._evictions = 0

    def get(self, key: str) -> Any | None:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            cap = self._cache.capacity
            if isinstance(cap, str):
                cap = int(cap)
            if self._cache.size() >= cap:
                self._evictions += 1
            self._cache.put(key, value)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._cache.delete(key)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> CacheStats:
        with self._lock:
            return _acache_stats(self._cache, evictions_extra=self._evictions)

    def invalidate_pattern(self, pattern: str) -> int:
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys() if fnmatch.fnmatch(str(k), pattern)
            ]
            for k in keys_to_delete:
                self._cache.delete(k)
            return len(keys_to_delete)


class XWSystemCacheAdapter(_ACacheAdapterBase):
    __slots__ = ("xwsystem_cache_type",)

    def __init__(
        self, size: int, cache_type: str, namespace: str = "default", **kwargs: Any
    ) -> None:
        self.xwsystem_cache_type = cache_type.lower().strip()
        name = kwargs.pop("name", None)
        if name is None and namespace != "default":
            name = f"{namespace}-{self.xwsystem_cache_type}"
        backend = create_cache(
            capacity=size,
            cache_type=self.xwsystem_cache_type,
            namespace=namespace,
            name=name,
            **kwargs,
        )
        super().__init__(backend)


class XWSystemDefaultCacheAdapter(_ACacheAdapterBase):
    __slots__ = ("xwsystem_cache_type",)

    def __init__(self, size: int, namespace: str = "default", **kwargs: Any) -> None:
        self.xwsystem_cache_type = "default"
        name = kwargs.pop("name", None)
        if name is None and namespace != "default":
            name = f"{namespace}-xwsystem-default"
        backend = create_cache(
            capacity=size,
            cache_type=None,
            namespace=namespace,
            name=name,
            **kwargs,
        )
        super().__init__(backend)


class LRUCacheAdapter(_ACacheAdapterBase):
    __slots__ = ("xwsystem_cache_type",)

    def __init__(self, size: int, namespace: str = "default", **kwargs: Any) -> None:
        self.xwsystem_cache_type = "lru"
        name = kwargs.pop("name", None)
        if name is None and namespace != "default":
            name = f"{namespace}-LRU"
        super().__init__(
            create_cache(
                capacity=size,
                cache_type="lru",
                namespace=namespace,
                name=name,
                **kwargs,
            )
        )


class LFUCacheAdapter(_ACacheAdapterBase):
    __slots__ = ("xwsystem_cache_type",)

    def __init__(self, size: int, namespace: str = "default", **kwargs: Any) -> None:
        self.xwsystem_cache_type = "lfu"
        name = kwargs.pop("name", None)
        if name is None and namespace != "default":
            name = f"{namespace}-LFU"
        super().__init__(
            create_cache(
                capacity=size,
                cache_type="lfu",
                namespace=namespace,
                name=name,
                **kwargs,
            )
        )


class TTLCacheAdapter(_ACacheAdapterBase):
    __slots__ = ("xwsystem_cache_type",)

    def __init__(
        self,
        size: int,
        ttl: int = 300,
        namespace: str = "default",
        **kwargs: Any,
    ) -> None:
        self.xwsystem_cache_type = "ttl"
        name = kwargs.pop("name", None)
        if name is None and namespace != "default":
            name = f"{namespace}-TTL"
        super().__init__(
            create_cache(
                capacity=size,
                cache_type="ttl",
                ttl=float(ttl),
                namespace=namespace,
                name=name or "ttl_cache",
                **kwargs,
            )
        )


class TwoTierCacheAdapter(ICacheAdapter):
    __slots__ = (
        "_cache",
        "_lock",
        "_evictions",
        "_memory_cap",
        "_disk_cap",
        "xwsystem_cache_type",
    )

    def __init__(
        self,
        size: int,
        disk_size: int = 10000,
        disk_cache_dir: str | None = None,
        namespace: str = "default",
        **kwargs: Any,
    ) -> None:
        self.xwsystem_cache_type = "two_tier"
        kwargs.pop("name", None)
        self._memory_cap = int(size)
        self._disk_cap = int(disk_size)
        self._cache = TwoTierCache(
            namespace=namespace,
            memory_size=self._memory_cap,
            disk_size=self._disk_cap,
            disk_cache_dir=disk_cache_dir,
        )
        self._lock = threading.RLock()
        self._evictions = 0

    def get(self, key: str) -> Any | None:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache.put(key, value)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._cache.delete(key)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> CacheStats:
        with self._lock:
            d = self._cache.get_stats()
            hits = int(d["memory_hits"]) + int(d["disk_hits"])
            misses = int(d["misses"])
            return CacheStats(
                hits=hits,
                misses=misses,
                size=int(d["memory_size"]) + int(d["disk_size"]),
                max_size=self._memory_cap + self._disk_cap,
                evictions=self._evictions,
            )

    def invalidate_pattern(self, pattern: str) -> int:
        with self._lock:
            count = 0
            mem = self._cache.memory_cache
            try:
                key_iter = mem.keys()
            except Exception:
                key_iter = []
            for k in key_iter:
                if fnmatch.fnmatch(str(k), pattern):
                    if self._cache.delete(k):
                        count += 1
            return count


def create_adapter_for_strategy(
    strategy: str,
    size: int,
    *,
    namespace: str = "default",
    default_ttl: float | int | None = None,
    default_disk_size: int | None = None,
    default_disk_cache_dir: str | None = None,
    **kwargs: Any,
) -> ICacheAdapter:
    s = (strategy or "xwsystem").lower().strip()
    if not cache_strategy_is_allowed(s):
        raise ValueError(
            f"Unknown cache strategy {strategy!r}. "
            f"Use list_xwsystem_cache_types() or xwnode aliases {sorted(_XWNODE_STRATEGY_EXTRAS)}."
        )
    disk_dir = kwargs.pop("disk_dir", None)
    if "disk_cache_dir" not in kwargs and disk_dir is not None:
        kwargs["disk_cache_dir"] = disk_dir
    if s == "none":
        return NoCacheAdapter()
    if s in ("xwsystem", "default", "auto"):
        return XWSystemDefaultCacheAdapter(size, namespace=namespace, **kwargs)
    if s == "two_tier":
        ds = kwargs.pop("disk_size", None)
        if ds is None:
            ds = default_disk_size if default_disk_size is not None else 10000
        ddir = kwargs.pop("disk_cache_dir", None)
        if ddir is None:
            ddir = default_disk_cache_dir
        return TwoTierCacheAdapter(
            size,
            disk_size=int(ds),
            disk_cache_dir=ddir,
            namespace=namespace,
            **kwargs,
        )
    if s == "fifo":
        return LRUCacheAdapter(size, namespace=namespace, **kwargs)
    if s == "lru":
        return LRUCacheAdapter(size, namespace=namespace, **kwargs)
    if s == "lfu":
        return LFUCacheAdapter(size, namespace=namespace, **kwargs)
    if s == "ttl":
        ttl = kwargs.pop("ttl", default_ttl)
        if ttl is None:
            ttl = 300
        return TTLCacheAdapter(size, ttl=int(ttl), namespace=namespace, **kwargs)
    if s == "secure_ttl" and default_ttl is not None:
        kwargs.setdefault("ttl", float(default_ttl))
    return XWSystemCacheAdapter(size, s, namespace=namespace, **kwargs)


class CacheController:
    """Flyweight component caches; engines from xwsystem CacheFactory."""

    def __init__(self, config: XWNodeConfig | None = None) -> None:
        self._config = config or get_config()
        self._lock = threading.RLock()
        self._cache_instances: dict[str, ICacheAdapter] = {}
        self._component_configs: dict[str, dict[str, Any]] = {}
        self._runtime_overrides: dict[str, dict[str, Any]] = {}
        self._initialize_component_configs()

    def _initialize_component_configs(self) -> None:
        self._component_configs = {
            "graph": {
                "enabled": self._config.enable_graph_caching,
                "strategy": self._config.graph_cache_strategy,
                "size": self._config.graph_cache_size,
            },
            "traversal": {
                "enabled": self._config.enable_traversal_caching,
                "strategy": self._config.traversal_cache_strategy,
                "size": self._config.traversal_cache_size,
            },
            "query": {
                "enabled": self._config.enable_query_caching,
                "strategy": self._config.query_cache_strategy,
                "size": self._config.query_cache_size,
            },
        }

    def get_cache(
        self,
        component: str,
        operation: str | None = None,
        **runtime_options: Any,
    ) -> ICacheAdapter:
        with self._lock:
            if operation and not self._should_cache_operation(component, operation):
                return NoCacheAdapter()
            config = self._get_effective_config(component, runtime_options)
            if not config.get("enabled", True):
                return NoCacheAdapter()
            if not self._config.enable_global_caching:
                return NoCacheAdapter()
            cache_key = self._get_cache_key(component, config)
            if cache_key not in self._cache_instances:
                self._cache_instances[cache_key] = self._create_cache_adapter(
                    component, config
                )
            return self._cache_instances[cache_key]

    def _get_effective_config(
        self, component: str, runtime_options: dict[str, Any]
    ) -> dict[str, Any]:
        config = {
            "enabled": self._config.enable_global_caching,
            "strategy": self._config.global_cache_strategy,
            "size": self._config.global_cache_size,
        }
        if component in self._component_configs:
            config.update(self._component_configs[component])
        if component in self._runtime_overrides:
            config.update(self._runtime_overrides[component])
        config.update(runtime_options)
        return config

    def _should_cache_operation(self, component: str, operation: str) -> bool:
        if operation.startswith("one_time_"):
            return False
        if operation in ("insert", "update", "delete"):
            return False
        return True

    def _get_cache_key(self, component: str, config: dict[str, Any]) -> str:
        strategy = config.get("strategy", "xwsystem")
        size = config.get("size", 1000)
        return f"{component}:{strategy}:{size}"

    def _create_cache_adapter(
        self, component: str, config: dict[str, Any]
    ) -> ICacheAdapter:
        strategy = config.get("strategy", "xwsystem")
        size = config.get("size", 1000)
        namespace = f"xwnode.{component}"
        reserved = frozenset({"enabled", "strategy", "size"})
        passthrough = {k: v for k, v in config.items() if k not in reserved}
        if "disk_dir" in passthrough and "disk_cache_dir" not in passthrough:
            passthrough["disk_cache_dir"] = passthrough.pop("disk_dir")
        try:
            return create_adapter_for_strategy(
                str(strategy),
                int(size),
                namespace=namespace,
                default_ttl=self._config.cache_ttl_seconds,
                default_disk_size=self._config.disk_cache_size,
                default_disk_cache_dir=self._config.disk_cache_dir,
                **passthrough,
            )
        except ValueError as e:
            logger.error("Invalid cache strategy: %s", e)
            return NoCacheAdapter()
        except Exception as e:
            logger.error("Failed to create cache adapter: %s", e)
            return NoCacheAdapter()

    def set_component_config(
        self,
        component: str,
        enabled: bool | None = None,
        strategy: str | None = None,
        size: int | None = None,
        **kwargs: Any,
    ) -> None:
        with self._lock:
            if component not in self._component_configs:
                self._component_configs[component] = {}
            if enabled is not None:
                self._component_configs[component]["enabled"] = enabled
            if strategy is not None:
                self._component_configs[component]["strategy"] = strategy
            if size is not None:
                self._component_configs[component]["size"] = size
            self._component_configs[component].update(kwargs)

    @contextmanager
    def runtime_override(self, component: str, **overrides: Any):
        old_overrides = self._runtime_overrides.get(component, {}).copy()
        try:
            self._runtime_overrides[component] = overrides
            yield
        finally:
            if old_overrides:
                self._runtime_overrides[component] = old_overrides
            else:
                self._runtime_overrides.pop(component, None)

    def get_all_stats(self) -> dict[str, CacheStats]:
        with self._lock:
            return {k: c.get_stats() for k, c in self._cache_instances.items()}

    def get_component_stats(self, component: str) -> CacheStats | None:
        with self._lock:
            for key, cache in self._cache_instances.items():
                if key.startswith(f"{component}:"):
                    return cache.get_stats()
            return None

    def clear_all(self) -> None:
        with self._lock:
            for cache in self._cache_instances.values():
                cache.clear()

    def clear_component(self, component: str) -> None:
        with self._lock:
            for key, cache in list(self._cache_instances.items()):
                if key.startswith(f"{component}:"):
                    cache.clear()

    def invalidate_pattern(self, component: str, pattern: str) -> int:
        with self._lock:
            total = 0
            for key, cache in self._cache_instances.items():
                if key.startswith(f"{component}:"):
                    total += cache.invalidate_pattern(pattern)
            return total

    def get_health_report(self) -> dict[str, Any]:
        with self._lock:
            report: dict[str, Any] = {
                "total_caches": len(self._cache_instances),
                "components": {},
                "warnings": [],
                "recommendations": [],
            }
            for key, cache in self._cache_instances.items():
                comp = key.split(":")[0]
                stats = cache.get_stats()
                report["components"][comp] = stats.to_dict()
                if stats.hit_rate < self._config.cache_hit_threshold:
                    report["warnings"].append(
                        f"{comp}: Low hit rate {stats.hit_rate:.2%}"
                    )
                if stats.max_size and stats.size >= stats.max_size * 0.9:
                    report["warnings"].append(
                        f"{comp}: Cache almost full ({stats.size}/{stats.max_size})"
                    )
            return report


_controller: CacheController | None = None
_controller_lock = threading.Lock()


def get_cache_controller(config: XWNodeConfig | None = None) -> CacheController:
    global _controller
    if _controller is not None:
        return _controller
    with _controller_lock:
        if _controller is None:
            _controller = CacheController(config)
        return _controller


def reset_cache_controller() -> None:
    global _controller
    with _controller_lock:
        if _controller is not None:
            _controller.clear_all()
        _controller = None
