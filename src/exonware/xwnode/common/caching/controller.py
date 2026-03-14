"""
#exonware/xwnode/src/exonware/xwnode/common/caching/controller.py
Cache controller implementing 4-level caching hierarchy.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
Generation Date: November 4, 2025
"""

import threading
from typing import Any
from contextlib import contextmanager
from exonware.xwsystem import get_logger
from ...config import get_config, XWNodeConfig
from ...defs import CacheMode
from .contracts import ICacheAdapter, CacheStats
from .adapters import (
    NoCacheAdapter,
    LRUCacheAdapter,
    LFUCacheAdapter,
    TTLCacheAdapter,
    TwoTierCacheAdapter
)
logger = get_logger(__name__)


class CacheController:
    """
    4-level cache hierarchy controller.
    Implements the caching hierarchy:
    Level 1: Global - System-wide defaults
    Level 2: Component - Per-component overrides (graph, traversal, query)
    Level 3: Runtime - Temporary overrides for specific sessions
    Level 4: Operation - Per-operation caching decisions
    Features:
    - Flyweight pattern for cache instance sharing
    - Thread-safe cache management
    - Automatic cache lifecycle management
    - Performance monitoring integration
    - Graceful degradation on cache failures
    """

    def __init__(self, config: XWNodeConfig | None = None):
        """
        Initialize cache controller.
        Args:
            config: XWNode configuration (uses global config if None)
        """
        self._config = config or get_config()
        self._lock = threading.RLock()
        # Cache instance pool (Flyweight pattern)
        self._cache_instances: dict[str, ICacheAdapter] = {}
        # Component-specific configurations
        self._component_configs: dict[str, dict[str, Any]] = {}
        # Runtime overrides (temporary)
        self._runtime_overrides: dict[str, dict[str, Any]] = {}
        # Initialize default component configurations
        self._initialize_component_configs()
        logger.info("CacheController initialized with 4-level hierarchy")

    def _initialize_component_configs(self) -> None:
        """Initialize component-specific cache configurations from config."""
        self._component_configs = {
            'graph': {
                'enabled': self._config.enable_graph_caching,
                'strategy': self._config.graph_cache_strategy,
                'size': self._config.graph_cache_size,
            },
            'traversal': {
                'enabled': self._config.enable_traversal_caching,
                'strategy': self._config.traversal_cache_strategy,
                'size': self._config.traversal_cache_size,
            },
            'query': {
                'enabled': self._config.enable_query_caching,
                'strategy': self._config.query_cache_strategy,
                'size': self._config.query_cache_size,
            }
        }

    def get_cache(
        self,
        component: str,
        operation: str | None = None,
        **runtime_options
    ) -> ICacheAdapter:
        """
        Get cache adapter for component with 4-level hierarchy.
        Level 1: Global config
        Level 2: Component config
        Level 3: Runtime options
        Level 4: Operation-specific decisions
        Args:
            component: Component name (e.g., "graph", "traversal")
            operation: Optional operation name for Level 4 decisions
            **runtime_options: Runtime overrides (Level 3)
        Returns:
            Cache adapter instance (may be shared via Flyweight)
        """
        with self._lock:
            # Level 4: Check if operation should be cached
            if operation and not self._should_cache_operation(component, operation):
                return NoCacheAdapter()
            # Level 3: Apply runtime overrides
            config = self._get_effective_config(component, runtime_options)
            # Level 2: Check component-level enable
            if not config.get('enabled', True):
                return NoCacheAdapter()
            # Level 1: Check global enable
            if not self._config.enable_global_caching:
                return NoCacheAdapter()
            # Create or retrieve cache instance (Flyweight pattern)
            cache_key = self._get_cache_key(component, config)
            if cache_key not in self._cache_instances:
                self._cache_instances[cache_key] = self._create_cache_adapter(
                    component, config
                )
                logger.debug(f"Created new cache instance: {cache_key}")
            else:
                logger.debug(f"Reusing cache instance: {cache_key}")
            return self._cache_instances[cache_key]

    def _get_effective_config(
        self,
        component: str,
        runtime_options: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Compute effective configuration for component.
        Hierarchy: Runtime > Component > Global
        """
        # Start with global defaults
        config = {
            'enabled': self._config.enable_global_caching,
            'strategy': self._config.global_cache_strategy,
            'size': self._config.global_cache_size,
        }
        # Override with component-specific config
        if component in self._component_configs:
            config.update(self._component_configs[component])
        # Apply runtime overrides
        config.update(runtime_options)
        return config

    def _should_cache_operation(self, component: str, operation: str) -> bool:
        """
        Level 4: Determine if specific operation should be cached.
        Can be extended with pattern matching, cost estimation, etc.
        """
        # Default: cache all operations unless explicitly disabled
        # This can be extended with more sophisticated logic
        # Example: Don't cache one-time operations
        if operation.startswith('one_time_'):
            return False
        # Example: Don't cache write operations
        if operation in ['insert', 'update', 'delete']:
            return False
        return True

    def _get_cache_key(self, component: str, config: dict[str, Any]) -> str:
        """Generate unique cache key for Flyweight pattern."""
        strategy = config.get('strategy', 'lru')
        size = config.get('size', 1000)
        return f"{component}:{strategy}:{size}"

    def _create_cache_adapter(
        self,
        component: str,
        config: dict[str, Any]
    ) -> ICacheAdapter:
        """
        Create cache adapter based on strategy.
        Args:
            component: Component name
            config: Cache configuration
        Returns:
            Cache adapter instance
        """
        strategy = config.get('strategy', 'lru')
        size = config.get('size', 1000)
        namespace = f"xwnode.{component}"
        try:
            if strategy == 'none':
                return NoCacheAdapter()
            elif strategy == 'lru':
                # Default to LFU (fastest cache type)
                return LFUCacheAdapter(size=size, namespace=namespace)
            elif strategy == 'lfu':
                return LFUCacheAdapter(size=size, namespace=namespace)
            elif strategy == 'ttl':
                ttl = config.get('ttl', self._config.cache_ttl_seconds)
                return TTLCacheAdapter(size=size, ttl=ttl, namespace=namespace)
            elif strategy == 'two_tier':
                disk_size = config.get('disk_size', self._config.disk_cache_size)
                disk_dir = config.get('disk_dir', self._config.disk_cache_dir)
                return TwoTierCacheAdapter(
                    size=size,
                    disk_size=disk_size,
                    disk_cache_dir=disk_dir,
                    namespace=namespace
                )
            else:
                logger.warning(f"Unknown cache strategy '{strategy}', using LFU (fastest cache type)")
                # Default to LFU (fastest cache type)
                return LFUCacheAdapter(size=size, namespace=namespace)
        except Exception as e:
            logger.error(f"Failed to create cache adapter: {e}, using NoCacheAdapter")
            return NoCacheAdapter()

    def set_component_config(
        self,
        component: str,
        enabled: bool | None = None,
        strategy: str | None = None,
        size: int | None = None,
        **kwargs
    ) -> None:
        """
        Level 2: Set component-specific cache configuration.
        Args:
            component: Component name
            enabled: Enable/disable caching
            strategy: Cache strategy name
            size: Cache size
            **kwargs: Additional options
        """
        with self._lock:
            if component not in self._component_configs:
                self._component_configs[component] = {}
            if enabled is not None:
                self._component_configs[component]['enabled'] = enabled
            if strategy is not None:
                self._component_configs[component]['strategy'] = strategy
            if size is not None:
                self._component_configs[component]['size'] = size
            self._component_configs[component].update(kwargs)
            logger.info(f"Updated component config for '{component}': {self._component_configs[component]}")
    @contextmanager

    def runtime_override(
        self,
        component: str,
        **overrides
    ):
        """
        Level 3: Context manager for temporary runtime overrides.
        Example:
            with controller.runtime_override('graph', strategy='lfu'):
                # Use LFU cache for this block
                cache = controller.get_cache('graph')
        Args:
            component: Component name
            **overrides: Temporary configuration overrides
        """
        # Save current overrides
        old_overrides = self._runtime_overrides.get(component, {}).copy()
        try:
            # Apply new overrides
            self._runtime_overrides[component] = overrides
            logger.debug(f"Applied runtime overrides for '{component}': {overrides}")
            yield
        finally:
            # Restore old overrides
            if old_overrides:
                self._runtime_overrides[component] = old_overrides
            else:
                self._runtime_overrides.pop(component, None)
            logger.debug(f"Restored runtime overrides for '{component}'")

    def get_all_stats(self) -> dict[str, CacheStats]:
        """
        Get statistics for all cache instances.
        Returns:
            Dictionary mapping cache keys to stats
        """
        with self._lock:
            stats = {}
            for key, cache in self._cache_instances.items():
                stats[key] = cache.get_stats()
            return stats

    def get_component_stats(self, component: str) -> CacheStats | None:
        """
        Get statistics for specific component.
        Args:
            component: Component name
        Returns:
            CacheStats if component has cache, None otherwise
        """
        with self._lock:
            for key, cache in self._cache_instances.items():
                if key.startswith(f"{component}:"):
                    return cache.get_stats()
            return None

    def clear_all(self) -> None:
        """Clear all cache instances."""
        with self._lock:
            for cache in self._cache_instances.values():
                cache.clear()
            logger.info("Cleared all cache instances")

    def clear_component(self, component: str) -> None:
        """
        Clear caches for specific component.
        Args:
            component: Component name
        """
        with self._lock:
            for key, cache in list(self._cache_instances.items()):
                if key.startswith(f"{component}:"):
                    cache.clear()
                    logger.info(f"Cleared cache for component '{component}'")

    def invalidate_pattern(self, component: str, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        Args:
            component: Component name
            pattern: Pattern to match (e.g., "user:*")
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            total = 0
            for key, cache in self._cache_instances.items():
                if key.startswith(f"{component}:"):
                    count = cache.invalidate_pattern(pattern)
                    total += count
            if total > 0:
                logger.info(f"Invalidated {total} entries matching '{pattern}' in '{component}'")
            return total

    def get_health_report(self) -> dict[str, Any]:
        """
        Get comprehensive health report for all caches.
        Returns:
            Dictionary with health metrics and recommendations
        """
        with self._lock:
            report = {
                'total_caches': len(self._cache_instances),
                'components': {},
                'warnings': [],
                'recommendations': []
            }
            for key, cache in self._cache_instances.items():
                component = key.split(':')[0]
                stats = cache.get_stats()
                report['components'][component] = stats.to_dict()
                # Check hit rate
                if stats.hit_rate < self._config.cache_hit_threshold:
                    report['warnings'].append(
                        f"{component}: Low hit rate {stats.hit_rate:.2%} (threshold: {self._config.cache_hit_threshold:.2%})"
                    )
                    report['recommendations'].append(
                        f"{component}: Consider increasing cache size or changing strategy"
                    )
                # Check if cache is full
                if stats.size >= stats.max_size * 0.9:
                    report['warnings'].append(
                        f"{component}: Cache almost full ({stats.size}/{stats.max_size})"
                    )
                    report['recommendations'].append(
                        f"{component}: Consider increasing cache size"
                    )
            return report
# Global controller instance (singleton pattern)
_controller: CacheController | None = None
_controller_lock = threading.Lock()


def get_cache_controller(config: XWNodeConfig | None = None) -> CacheController:
    """
    Get global cache controller instance.
    Args:
        config: Optional configuration (uses global if None)
    Returns:
        Cache controller instance
    """
    global _controller
    if _controller is not None:
        return _controller
    with _controller_lock:
        if _controller is None:
            _controller = CacheController(config)
        return _controller


def reset_cache_controller() -> None:
    """Reset global cache controller (mainly for testing)."""
    global _controller
    with _controller_lock:
        if _controller is not None:
            _controller.clear_all()
        _controller = None
        logger.info("Cache controller reset")
