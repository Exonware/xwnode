"""
#exonware/xwnode/src/exonware/xwnode/common/caching/__init__.py
xwnode caching: minimal policy + path navigation on top of ``exonware.xwsystem.caching``.

Import from ``exonware.xwnode.common.caching``.
"""

from .contracts import (
    CacheStats,
    ICacheAdapter,
    ICacheFactory,
    ICacheMetrics,
    ICacheStrategyManager,
)
from .path_nav import PathNavigationCache
from .policy import (
    CacheController,
    LFUCacheAdapter,
    LRUCacheAdapter,
    NoCacheAdapter,
    TTLCacheAdapter,
    TwoTierCacheAdapter,
    XWSystemCacheAdapter,
    XWSystemDefaultCacheAdapter,
    cache_strategy_is_allowed,
    create_adapter_for_strategy,
    get_cache_controller,
    list_xwsystem_cache_types,
    reset_cache_controller,
)
from .strategy import CacheMetrics, CacheStrategyManager
from .telemetry import (
    CacheComparisonReport,
    CachePerformanceMetric,
    CacheTelemetryCollector,
    get_telemetry_collector,
    reset_telemetry,
)

__all__ = [
    "CacheController",
    "get_cache_controller",
    "reset_cache_controller",
    "ICacheAdapter",
    "ICacheFactory",
    "ICacheMetrics",
    "ICacheStrategyManager",
    "CacheStats",
    "LRUCacheAdapter",
    "LFUCacheAdapter",
    "TTLCacheAdapter",
    "TwoTierCacheAdapter",
    "NoCacheAdapter",
    "XWSystemDefaultCacheAdapter",
    "XWSystemCacheAdapter",
    "cache_strategy_is_allowed",
    "create_adapter_for_strategy",
    "list_xwsystem_cache_types",
    "CacheTelemetryCollector",
    "CachePerformanceMetric",
    "CacheComparisonReport",
    "get_telemetry_collector",
    "reset_telemetry",
    "PathNavigationCache",
    "CacheStrategyManager",
    "CacheMetrics",
]
