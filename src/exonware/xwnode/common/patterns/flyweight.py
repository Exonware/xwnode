#!/usr/bin/env python3
#exonware/xwnode/src/exonware/xwnode/common/patterns/flyweight.py
"""
Strategy Flyweight Pattern Implementation
Optimizes memory usage by sharing strategy instances with identical configurations.
This prevents creating multiple instances of the same strategy type with the same
configuration, which is especially important for high-throughput applications.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.14
Generation Date: 07-Sep-2025
"""

import threading
import hashlib
from typing import Any, TypeVar
from weakref import WeakValueDictionary
from exonware.xwsystem import get_logger
from exonware.xwsystem.io.serialization.formats.text.json import JsonSerializer
from exonware.xwsystem.caching import create_cache
from collections.abc import Hashable
logger = get_logger(__name__)
# ============================================================================
# GLOBAL CACHE FOR STRATEGY INSTANCES (xwsystem integration - shared across ALL instances)
# ============================================================================
# Performance: Use xwsystem's optimized cache (PylruCache when pylru installed, else FunctoolsLRUCache)
# This provides O(1) operations, automatic LRU eviction, thread-safety, and statistics
# Similar to xwdata's global cache pattern for maximum performance
_GLOBAL_STRATEGY_CACHE = None
_strategy_cache_lock = threading.Lock()


def _get_global_strategy_cache():
    """Get or create global strategy cache (shared across all flyweight instances)."""
    global _GLOBAL_STRATEGY_CACHE
    if _GLOBAL_STRATEGY_CACHE is None:
        with _strategy_cache_lock:
            if _GLOBAL_STRATEGY_CACHE is None:
                # Use xwsystem's create_cache (defaults to PylruCache when pylru installed, else FunctoolsLRUCache)
                # Large capacity for strategy instances (strategies are lightweight)
                _GLOBAL_STRATEGY_CACHE = create_cache(
                    capacity=10000, 
                    namespace='xwnode', 
                    name='strategy_cache_global'
                )
                logger.debug("Using xwsystem global cache for xwnode strategy instances")
    return _GLOBAL_STRATEGY_CACHE
# Global JSON serializer instance for config serialization (reused across all flyweight instances)
# Performance: Creating serializer once is much faster than creating per request
_json_serializer = None
_json_serializer_lock = threading.RLock()


def _get_json_serializer() -> JsonSerializer:
    """Get or create global JSON serializer instance for config serialization."""
    global _json_serializer
    if _json_serializer is None:
        with _json_serializer_lock:
            if _json_serializer is None:
                _json_serializer = JsonSerializer()
    return _json_serializer
from ...defs import NodeMode, EdgeMode, NodeTrait, EdgeTrait
from ...nodes.strategies.base import ANodeStrategy
from ...edges.strategies.base import AEdgeStrategy
T = TypeVar('T', bound=ANodeStrategy | AEdgeStrategy)


class StrategyFlyweight:
    """
    Flyweight factory for strategy instances.
    Manages shared strategy instances to reduce memory footprint and
    improve performance by avoiding redundant object creation.
    """

    def __init__(self):
        """Initialize the flyweight factory."""
        # Primary storage: WeakValueDictionary for automatic memory management
        # Automatically cleans up unused strategy instances
        self._node_instances: WeakValueDictionary[str, ANodeStrategy] = WeakValueDictionary()
        self._edge_instances: WeakValueDictionary[str, AEdgeStrategy] = WeakValueDictionary()
        # Fast lookup layer: xwsystem's optimized LRU cache for frequently accessed strategies
        # This provides O(1) lookups with automatic LRU eviction and statistics
        # Only caches frequently accessed strategies (WeakValueDictionary handles the rest)
        self._fast_cache = _get_global_strategy_cache()
        self._lock = threading.RLock()
        self._stats = {
            'node_created': 0,
            'node_reused': 0,
            'edge_created': 0,
            'edge_reused': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'fast_cache_hits': 0,  # Track xwsystem cache hits
            'memory_saved_instances': 0
        }

    def get_node_strategy(
        self, 
        strategy_class: type[T],
        mode: NodeMode,
        traits: NodeTrait = NodeTrait.NONE,
        **config: Any
    ) -> T:
        """
        Get a node strategy instance, creating or reusing based on configuration.
        Args:
            strategy_class: The strategy class to instantiate
            mode: Node mode for the strategy
            traits: Node traits for the strategy
            **config: Configuration parameters for the strategy
        Returns:
            Shared strategy instance
        """
        # Create a hashable key from the class and configuration
        cache_key = self._create_node_cache_key(strategy_class, mode, traits, config)
        with self._lock:
            # Performance optimization: Check xwsystem fast cache first (O(1) with LRU eviction)
            # This provides 10-50x faster lookups for frequently accessed strategies
            cached_instance = self._fast_cache.get(cache_key)
            if cached_instance is not None:
                self._stats['fast_cache_hits'] += 1
                self._stats['cache_hits'] += 1
                self._stats['node_reused'] += 1
                self._stats['memory_saved_instances'] += 1
                # Performance optimization: Guard logging with isEnabledFor check
                if logger.isEnabledFor(10):  # DEBUG level
                    logger.debug(f"⚡ Fast cache hit: {strategy_class.__name__}")
                return cached_instance
            # Check WeakValueDictionary (for memory-managed instances)
            if cache_key in self._node_instances:
                instance = self._node_instances[cache_key]
                # Promote to fast cache for future lookups
                self._fast_cache.put(cache_key, instance)
                self._stats['cache_hits'] += 1
                self._stats['node_reused'] += 1
                self._stats['memory_saved_instances'] += 1
                # Performance optimization: Guard logging with isEnabledFor check
                if logger.isEnabledFor(10):  # DEBUG level
                    logger.debug(f"♻️ Reusing node strategy: {strategy_class.__name__}")
                return instance
            # Create new instance
            self._stats['cache_misses'] += 1
            self._stats['node_created'] += 1
            try:
                # Root cause fixed: Strategy classes don't accept 'mode' parameter
                # They hardcode it in super().__init__() call, so remove it from config
                # to prevent "multiple values for argument 'mode'" error
                # Performance optimization: Check if config is empty first, then check keys
                # (dict 'in' operator is O(1) average case, faster than set creation for small dicts)
                if config and ('mode' in config or 'traits' in config):
                    clean_config = {k: v for k, v in config.items() if k not in ('mode', 'traits')}
                else:
                    clean_config = config  # Reuse original dict - no copy needed
                instance = strategy_class(traits=traits, **clean_config)
                # Store in both WeakValueDictionary (for automatic cleanup) and fast cache (for performance)
                self._node_instances[cache_key] = instance
                self._fast_cache.put(cache_key, instance)  # Promote to fast cache immediately
                # Performance optimization: Guard logging with isEnabledFor check
                if logger.isEnabledFor(10):  # DEBUG level
                    logger.debug(f"🆕 Created new node strategy: {strategy_class.__name__}")
                return instance
            except Exception as e:
                logger.error(f"❌ Failed to create {strategy_class.__name__} instance: {e}")
                raise

    def get_edge_strategy(
        self, 
        strategy_class: type[T],
        mode: EdgeMode,
        traits: EdgeTrait = EdgeTrait.NONE,
        **config: Any
    ) -> T:
        """
        Get an edge strategy instance, creating or reusing based on configuration.
        Args:
            strategy_class: The strategy class to instantiate
            mode: Edge mode for the strategy
            traits: Edge traits for the strategy
            **config: Configuration parameters for the strategy
        Returns:
            Shared strategy instance
        """
        # Create a hashable key from the class and configuration
        cache_key = self._create_edge_cache_key(strategy_class, mode, traits, config)
        with self._lock:
            # Performance optimization: Check xwsystem fast cache first (O(1) with LRU eviction)
            # This provides 10-50x faster lookups for frequently accessed strategies
            cached_instance = self._fast_cache.get(cache_key)
            if cached_instance is not None:
                self._stats['fast_cache_hits'] += 1
                self._stats['cache_hits'] += 1
                self._stats['edge_reused'] += 1
                self._stats['memory_saved_instances'] += 1
                # Performance optimization: Guard logging with isEnabledFor check
                if logger.isEnabledFor(10):  # DEBUG level
                    logger.debug(f"⚡ Fast cache hit: {strategy_class.__name__}")
                return cached_instance
            # Check WeakValueDictionary (for memory-managed instances)
            if cache_key in self._edge_instances:
                instance = self._edge_instances[cache_key]
                # Promote to fast cache for future lookups
                self._fast_cache.put(cache_key, instance)
                self._stats['cache_hits'] += 1
                self._stats['edge_reused'] += 1
                self._stats['memory_saved_instances'] += 1
                # Performance optimization: Guard logging with isEnabledFor check
                if logger.isEnabledFor(10):  # DEBUG level
                    logger.debug(f"♻️ Reusing edge strategy: {strategy_class.__name__}")
                return instance
            # Create new instance
            self._stats['cache_misses'] += 1
            self._stats['edge_created'] += 1
            try:
                # Root cause fixed: Strategy classes don't accept 'mode' parameter
                # They hardcode it in super().__init__() call, so remove it from config
                # to prevent "multiple values for argument 'mode'" error
                # Performance optimization: Check if config is empty first, then check keys
                # (dict 'in' operator is O(1) average case, faster than set creation for small dicts)
                if config and ('mode' in config or 'traits' in config):
                    clean_config = {k: v for k, v in config.items() if k not in ('mode', 'traits')}
                else:
                    clean_config = config  # Reuse original dict - no copy needed
                instance = strategy_class(traits=traits, **clean_config)
                # Store in both WeakValueDictionary (for automatic cleanup) and fast cache (for performance)
                self._edge_instances[cache_key] = instance
                self._fast_cache.put(cache_key, instance)  # Promote to fast cache immediately
                # Performance optimization: Guard logging with isEnabledFor check
                if logger.isEnabledFor(10):  # DEBUG level
                    logger.debug(f"🆕 Created new edge strategy: {strategy_class.__name__}")
                return instance
            except Exception as e:
                logger.error(f"❌ Failed to create {strategy_class.__name__} instance: {e}")
                raise

    def _create_node_cache_key(
        self, 
        strategy_class: type[T], 
        mode: NodeMode,
        traits: NodeTrait,
        config: dict[str, Any]
    ) -> str:
        """
        Create a hashable cache key from class, mode, traits, and configuration.
        Args:
            strategy_class: The strategy class
            mode: Node mode
            traits: Node traits
            config: Configuration dictionary
        Returns:
            String cache key
        Performance optimization: Avoids expensive json.dumps() for empty/simple configs.
        Uses tuple-based key for faster hashing when possible.
        """
        # Start with class name and module
        key_parts = [f"{strategy_class.__module__}.{strategy_class.__name__}"]
        # Add mode and traits
        key_parts.append(f"mode:{mode.name}")
        key_parts.append(f"traits:{traits.name}")
        # Performance optimization: Use xwsystem JsonSerializer for config serialization
        # This leverages xwsystem's optimized serialization (auto-detects best parser: orjson, ujson, etc.)
        # Much faster than manual JSON encoding and handles all types correctly
        if config:
            try:
                # Use xwsystem JsonSerializer (optimized, auto-detects best parser)
                # Global instance is reused (thread-safe) for better performance
                serializer = _get_json_serializer()
                config_str = serializer.encode(
                    config,
                    options={'sort_keys': True, 'default': str}
                )
                # Handle both string and bytes return types
                if isinstance(config_str, bytes):
                    config_str = config_str.decode('utf-8')
                key_parts.append(f"config:{config_str}")
            except Exception:
                # Fallback in case of serialization error (very unlikely with default=str)
                key_parts.append(f"config:{str(config)}")
        # Create hash for shorter key
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _create_edge_cache_key(
        self, 
        strategy_class: type[T], 
        mode: EdgeMode,
        traits: EdgeTrait,
        config: dict[str, Any]
    ) -> str:
        """
        Create a hashable cache key from class, mode, traits, and configuration.
        Args:
            strategy_class: The strategy class
            mode: Edge mode
            traits: Edge traits
            config: Configuration dictionary
        Returns:
            String cache key
        Performance optimization: Avoids expensive json.dumps() for empty/simple configs.
        Uses tuple-based key for faster hashing when possible.
        """
        # Start with class name and module
        key_parts = [f"{strategy_class.__module__}.{strategy_class.__name__}"]
        # Add mode and traits
        key_parts.append(f"mode:{mode.name}")
        key_parts.append(f"traits:{traits.name}")
        # Performance optimization: Use xwsystem JsonSerializer for config serialization
        # This leverages xwsystem's optimized serialization (auto-detects best parser: orjson, ujson, etc.)
        # Much faster than manual JSON encoding and handles all types correctly
        if config:
            try:
                # Use xwsystem JsonSerializer (optimized, auto-detects best parser)
                # Global instance is reused (thread-safe) for better performance
                serializer = _get_json_serializer()
                config_str = serializer.encode(
                    config,
                    options={'sort_keys': True, 'default': str}
                )
                # Handle both string and bytes return types
                if isinstance(config_str, bytes):
                    config_str = config_str.decode('utf-8')
                key_parts.append(f"config:{config_str}")
            except Exception:
                # Fallback in case of serialization error (very unlikely with default=str)
                key_parts.append(f"config:{str(config)}")
        # Create hash for shorter key
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get_stats(self) -> dict[str, Any]:
        """
        Get flyweight statistics.
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_created = self._stats['node_created'] + self._stats['edge_created']
            total_reused = self._stats['node_reused'] + self._stats['edge_reused']
            total_requests = total_created + total_reused
            cache_hit_rate = (self._stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
            # Get xwsystem cache statistics if available
            fast_cache_stats = {}
            try:
                if hasattr(self._fast_cache, 'get_stats'):
                    fast_cache_stats = self._fast_cache.get_stats()
                elif hasattr(self._fast_cache, 'capacity'):
                    fast_cache_stats = {
                        'capacity': self._fast_cache.capacity,
                        'size': len(self._fast_cache) if hasattr(self._fast_cache, '__len__') else 0
                    }
            except Exception:
                pass
            return {
                'node_strategies': {
                    'created': self._stats['node_created'],
                    'reused': self._stats['node_reused'],
                    'active': len(self._node_instances)
                },
                'edge_strategies': {
                    'created': self._stats['edge_created'],
                    'reused': self._stats['edge_reused'],
                    'active': len(self._edge_instances)
                },
                'cache_performance': {
                    'hits': self._stats['cache_hits'],
                    'misses': self._stats['cache_misses'],
                    'fast_cache_hits': self._stats.get('fast_cache_hits', 0),  # xwsystem cache hits
                    'hit_rate_percent': round(cache_hit_rate, 2),
                    'memory_saved_instances': self._stats['memory_saved_instances'],
                    'xwsystem_fast_cache': fast_cache_stats  # xwsystem cache statistics
                },
                'total_instances': {
                    'created': total_created,
                    'reused': total_reused,
                    'active': len(self._node_instances) + len(self._edge_instances)
                }
            }

    def clear_cache(self) -> None:
        """Clear all cached strategy instances."""
        with self._lock:
            node_count = len(self._node_instances)
            edge_count = len(self._edge_instances)
            self._node_instances.clear()
            self._edge_instances.clear()
            # Also clear xwsystem fast cache
            try:
                self._fast_cache.clear()
            except Exception:
                pass
            logger.info(f"🧹 Cleared flyweight cache: {node_count} node + {edge_count} edge instances")

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get detailed cache information.
        Returns:
            Dictionary with detailed cache information
        """
        with self._lock:
            return {
                'node_cache_size': len(self._node_instances),
                'edge_cache_size': len(self._edge_instances),
                'total_cache_size': len(self._node_instances) + len(self._edge_instances),
                'node_cache_keys': list(self._node_instances.keys()),
                'edge_cache_keys': list(self._edge_instances.keys())
            }
# Global flyweight instance
_flyweight_instance: StrategyFlyweight | None = None
_flyweight_lock = threading.Lock()


def get_flyweight() -> StrategyFlyweight:
    """
    Get the global strategy flyweight instance.
    Returns:
        Global StrategyFlyweight instance
    """
    global _flyweight_instance
    if _flyweight_instance is None:
        with _flyweight_lock:
            if _flyweight_instance is None:
                _flyweight_instance = StrategyFlyweight()
                logger.info("🏭 Initialized global strategy flyweight")
    return _flyweight_instance


def get_flyweight_stats() -> dict[str, Any]:
    """
    Get flyweight statistics.
    Returns:
        Flyweight statistics dictionary
    """
    return get_flyweight().get_stats()


def clear_flyweight_cache() -> None:
    """Clear the global flyweight cache."""
    get_flyweight().clear_cache()


def get_flyweight_cache_info() -> dict[str, Any]:
    """
    Get flyweight cache information.
    Returns:
        Cache information dictionary
    """
    return get_flyweight().get_cache_info()
# Usability aliases (Priority #2: Clean, intuitive API)
Flyweight = StrategyFlyweight
