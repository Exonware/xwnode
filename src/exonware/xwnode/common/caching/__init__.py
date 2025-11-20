"""
#exonware/xwnode/src/exonware/xwnode/common/caching/__init__.py

Cache system for xwnode components.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.30
Generation Date: November 4, 2025
"""

from .controller import CacheController, get_cache_controller, reset_cache_controller
from .contracts import ICacheAdapter, CacheStats, ICacheFactory
from .adapters import (
    LRUCacheAdapter,
    LFUCacheAdapter,
    TTLCacheAdapter,
    TwoTierCacheAdapter,
    NoCacheAdapter
)
from .telemetry import (
    CacheTelemetryCollector,
    CachePerformanceMetric,
    CacheComparisonReport,
    get_telemetry_collector,
    reset_telemetry
)

__all__ = [
    # Controller
    'CacheController',
    'get_cache_controller',
    'reset_cache_controller',
    
    # Contracts
    'ICacheAdapter',
    'ICacheFactory',
    'CacheStats',
    
    # Adapters
    'LRUCacheAdapter',
    'LFUCacheAdapter',
    'TTLCacheAdapter',
    'TwoTierCacheAdapter',
    'NoCacheAdapter',
    
    # Telemetry
    'CacheTelemetryCollector',
    'CachePerformanceMetric',
    'CacheComparisonReport',
    'get_telemetry_collector',
    'reset_telemetry',
]

