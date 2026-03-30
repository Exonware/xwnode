#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/base.py
Abstract base classes for XWNode - Clean Facade Architecture
This module contains abstract base classes for facade implementations:
- ANode: Abstract node base (INode → ANode → XWNode)
- AEdge: Abstract edge base (IEdge → AEdge → XWEdge)
Strategy base classes are in their respective strategy folders:
- Node strategy bases: nodes/strategies/base.py
- Edge strategy bases: edges/strategies/base.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.20
Generation Date: 24-Oct-2025
"""

from __future__ import annotations
from collections.abc import Iterator
import threading
import copy
from abc import ABC
from typing import Any, TYPE_CHECKING
from collections.abc import Callable
# Core XWNode imports - strategy-agnostic
from .errors import (
    XWNodeTypeError, XWNodePathError, XWNodeSecurityError, XWNodeValueError, XWNodeLimitError
)
from .config import get_config
from .contracts import INode, IEdge
# Strategy interface imports (for type hints only - avoid circular imports)
if TYPE_CHECKING:
    from .nodes.strategies.contracts import INodeStrategy
    from .edges.strategies.contracts import IEdgeStrategy
    iNodeStrategy = INodeStrategy
    iEdgeStrategy = IEdgeStrategy
else:
    # Runtime: use Any to avoid circular imports
    iNodeStrategy = Any
    iEdgeStrategy = Any
# System-level imports - standard imports (no defensive code!)
from exonware.xwsystem.security import get_resource_limits
from exonware.xwsystem.validation import validate_untrusted_data
from exonware.xwsystem.monitoring import create_component_metrics, CircuitBreaker, CircuitBreakerConfig
from exonware.xwsystem.threading import ThreadSafeFactory, create_thread_safe_cache
from exonware.xwsystem import get_logger
logger = get_logger('xwnode.base')
# Metrics setup
_metrics = create_component_metrics('xwnode_base')
measure_operation = _metrics['measure_operation']
record_cache_hit = _metrics['record_cache_hit']
record_cache_miss = _metrics['record_cache_miss']
# Thread-safe cache for path parsing
_path_cache = create_thread_safe_cache(max_size=1024)
# Circuit breaker for strategy operations
_strategy_circuit_breaker = CircuitBreaker(
    name='xwnode_strategy',
    config=CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=30,
        expected_exception=Exception
    )
)
# ==============================================================================
# PATH UTILITIES
# ==============================================================================


class PathParser:
    """
    Thread-safe path parser with caching using xwsystem's optimized cache.
    Performance optimization: Uses xwsystem's create_cache() (defaults to PylruCache when pylru installed, else FunctoolsLRUCache)
    which is 10-50x faster than manual OrderedDict implementation.
    """

    def __init__(self, max_cache_size: int = 1024):
        # Use xwsystem's optimized cache (PylruCache when pylru installed, else FunctoolsLRUCache)
        # This provides 10-50x faster operations than manual OrderedDict
        from exonware.xwsystem.caching import create_cache
        self._cache = create_cache(
            capacity=max_cache_size,
            namespace='xwnode',
            name='path_parser_cache'
        )
        self._max_cache_size = max_cache_size
        self._lock = threading.RLock()  # Still needed for stats tracking if implemented

    def parse(self, path: str) -> list[str]:
        """Parse a path string into parts (O(1) cache lookup with xwsystem cache)."""
        # Check xwsystem cache first (O(1) with automatic LRU eviction)
        cached_parts = self._cache.get(path)
        if cached_parts is not None:
            record_cache_hit()  # Track metrics
            return cached_parts
        # Cache miss - parse path
        record_cache_miss()  # Track metrics
        parts = self._parse_path(path)
        # Cache the result (automatic LRU eviction when full)
        self._cache.put(path, parts)
        return parts

    def _parse_path(self, path: str) -> list[str]:
        """Internal path parsing logic."""
        if not path:
            return []
        parts = []
        current = ""
        in_brackets = False
        in_quotes = False
        quote_char = None
        for char in path:
            if in_quotes:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current += char
            elif char in ['"', "'"]:
                in_quotes = True
                quote_char = char
            elif char == '[':
                if current:
                    parts.append(current)
                    current = ""
                in_brackets = True
                current += char
            elif char == ']':
                current += char
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
        if current:
            parts.append(current)
        return parts

    def clear_cache(self):
        """Clear the path cache."""
        with self._lock:
            self._cache.clear()


class GlobalPathCache:
    """
    Global cache for path lookups using xwsystem's optimized caching.
    Performance optimization: Uses xwsystem's create_cache() (defaults to PylruCache when pylru installed, else FunctoolsLRUCache)
    which is 10-50x faster than manual OrderedDict implementation.
    Benefits:
    - O(1) operations with automatic LRU eviction
    - Thread-safe by default
    - Built-in statistics tracking
    - Configurable via environment variables/settings
    """

    def __init__(self, max_size: int = 512):
        # Use xwsystem's optimized cache (PylruCache when pylru installed, else FunctoolsLRUCache)
        # This provides 10-50x faster operations than manual OrderedDict
        from exonware.xwsystem.caching import create_cache
        self._cache = create_cache(
            capacity=max_size, 
            namespace='xwnode', 
            name='global_path_cache'
        )
        self._max_size = max_size
        # Statistics tracking (xwsystem cache has built-in stats, but we track our own for compatibility)
        self._stats = {'hits': 0, 'misses': 0}
        self._lock = threading.RLock()  # Still need lock for stats updates

    def get(self, node_id: int, path: str) -> Any | None:
        """Get cached result for node and path (O(1) with xwsystem cache)."""
        # Create hashable key (xwsystem cache requires string keys)
        key = f"{node_id}:{path}"
        with self._lock:
            result = self._cache.get(key)
            if result is not None:
                self._stats['hits'] += 1
                return result
            self._stats['misses'] += 1
            return None

    def put(self, node_id: int, path: str, result: Any):
        """Cache result for node and path (O(1) with automatic LRU eviction)."""
        # Create hashable key (xwsystem cache requires string keys)
        key = f"{node_id}:{path}"
        with self._lock:
            # xwsystem cache handles LRU eviction automatically - no manual size management needed
            self._cache.put(key, result)

    def clear(self):
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._stats = {'hits': 0, 'misses': 0}

    def stats(self) -> dict[str, int]:
        """Get cache statistics (includes xwsystem cache stats if available)."""
        with self._lock:
            stats = self._stats.copy()
            # Add xwsystem cache stats if available
            try:
                if hasattr(self._cache, 'get_stats'):
                    xwsystem_stats = self._cache.get_stats()
                    stats.update(xwsystem_stats)
                elif hasattr(self._cache, 'capacity'):
                    stats['capacity'] = self._cache.capacity
                    stats['size'] = len(self._cache) if hasattr(self._cache, '__len__') else 0
            except Exception:
                pass
            return stats
# Global instances
_path_parser = None
_global_path_cache = None


def get_path_parser() -> PathParser:
    """Get the global path parser instance."""
    global _path_parser
    if _path_parser is None:
        _path_parser = PathParser()
    return _path_parser


def get_global_path_cache() -> GlobalPathCache:
    """Get the global path cache instance."""
    global _global_path_cache
    if _global_path_cache is None:
        _global_path_cache = GlobalPathCache()
    return _global_path_cache
# ==============================================================================
# NODE FACADE BASE CLASS
# ==============================================================================


class ANode[T](INode[T]):
    """
    Abstract base class for all node implementations with generic type parameter.
    Generic type parameter:
        T: The type of the native value returned by to_native() and value property.
    Follows GUIDELINES_DEV.md naming: INode → ANode → XWNode
    Provides core node functionality, delegates to node strategies for storage.
    """
    __slots__ = ('_strategy', '_hash_cache', '_type_cache')

    def __init__(self, strategy: iNodeStrategy):
        """Initialize with a strategy implementation."""
        self._strategy = strategy
        self._hash_cache = None
        self._type_cache = None
    @classmethod

    def from_native(cls, data: Any) -> ANode[Any]:
        """Create ANode from native data."""
        # For now, we'll use a simple hash map strategy
        # In the full implementation, this would use the strategy manager
        from .common.utils.simple import SimpleNodeStrategy
        strategy = SimpleNodeStrategy.create_from_data(data)
        return cls(strategy)

    def get(self, path: str, default: Any = None) -> ANode[T] | None:
        """Get a node by path with support for nested navigation."""
        try:
            # Parse the path into parts (e.g., 'users.0.name' -> ['users', '0', 'name'])
            parser = get_path_parser()
            parts = parser.parse(path)
            # If no parts or empty path, return self
            if not parts:
                return self
            # Navigate through the path
            current = self
            for i, part in enumerate(parts):
                if current is None:
                    return None
                # Try to get the next level
                try:
                    # Use find() for single-key access (no path parsing)
                    # Convert string numbers to int for list access
                    key = int(part) if part.isdigit() else part
                    result = current._strategy.find(key)
                    if result is None:
                        return None
                    # Check if result is already a strategy or needs wrapping
                    from .nodes.strategies.base import ANodeStrategy
                    from .nodes.strategies.contracts import INodeStrategy
                    if isinstance(result, (ANodeStrategy, INodeStrategy)):
                        # Already a strategy, wrap in ANode
                        current = ANode(result)
                    else:
                        # Raw value, need to create a strategy from it
                        from .common.utils.simple import SimpleNodeStrategy
                        strategy = SimpleNodeStrategy.create_from_data(result)
                        current = ANode(strategy)
                except Exception as e:
                    # Log the error for debugging
                    import logging
                    logging.debug(f"Error navigating path part {i} ('{part}'): {e}")
                    return None
            return current
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.debug(f"Error in get() for path '{path}': {e}")
            return None

    def set(self, path: str, value: Any, in_place: bool = True) -> ANode[T]:
        """Set a value at path."""
        new_strategy = self._strategy.put(path, value)
        if in_place:
            self._strategy = new_strategy
            return self
        else:
            return ANode(new_strategy)  # type: ignore[return-value]

    def delete(self, path: str, in_place: bool = True) -> ANode[T]:
        """Delete a node at path."""
        success = self._strategy.delete(path)
        return self

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self._strategy.exists(path)

    def find(self, path: str, in_place: bool = False) -> ANode[T] | None:
        """Find a node by path."""
        return self.get(path)

    def to_native(self) -> T:
        """Convert to native Python object of type T."""
        return self._strategy.to_native()  # type: ignore[return-value]

    def copy(self) -> ANode[T]:
        """Create a deep copy."""
        return ANode(self._strategy.create_from_data(self._strategy.to_native()))

    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        if path == ".":
            return len(self._strategy)
        node = self.get(path)
        return len(node._strategy) if node else 0

    def flatten(self, separator: str = ".") -> dict[str, Any]:
        """Flatten to dictionary."""
        result = {}
        def _flatten(node_strategy, prefix=""):
            if node_strategy.is_leaf:
                result[prefix or "root"] = node_strategy.value
            elif node_strategy.is_dict:
                for key in node_strategy.keys():
                    child = node_strategy.get(key)
                    new_prefix = f"{prefix}{separator}{key}" if prefix else key
                    _flatten(child, new_prefix)
            elif node_strategy.is_list:
                for i in range(len(node_strategy)):
                    child = node_strategy.get(str(i))
                    new_prefix = f"{prefix}{separator}{i}" if prefix else str(i)
                    _flatten(child, new_prefix)
        _flatten(self._strategy)
        return result

    def merge(self, other: INode[T], strategy: str = "replace") -> ANode[T]:
        """Merge with another node."""
        # Simple implementation - just replace
        return ANode(self._strategy.create_from_data(other.to_native()))  # type: ignore[return-value]

    def diff(self, other: INode[T]) -> dict[str, Any]:
        """Get differences with another node."""
        return {"changed": True}  # Simple implementation

    def transform(self, transformer: Callable[[Any], Any]) -> ANode[T]:
        """Transform using a function."""
        transformed_data = transformer(self.to_native())
        return ANode(self._strategy.create_from_data(transformed_data))  # type: ignore[return-value]

    def select(self, *paths: str) -> dict[str, ANode[T]]:
        """Select multiple paths."""
        result = {}
        for path in paths:
            node = self.get(path)
            if node:
                result[path] = node
        return result
    # Container methods

    def __len__(self) -> int:
        """Get length."""
        return len(self._strategy)

    def __iter__(self) -> Iterator['ANode[T]']:
        """Iterate over children."""
        for child_strategy in self._strategy:
            yield ANode(child_strategy)  # type: ignore[misc]

    def __getitem__(self, key: str | int | slice) -> ANode[T]:
        """Get child by key, index, or slice."""
        child_strategy = self._strategy[key]
        return ANode(child_strategy)

    def __setitem__(self, key: str | int, value: Any) -> None:
        """Set child by key or index."""
        self._strategy[key] = value

    def __contains__(self, key: str | int) -> bool:
        """Check if key exists."""
        return key in self._strategy
    # Type checking properties
    @property

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self._strategy.is_leaf
    @property

    def is_list(self) -> bool:
        """Check if this is a list node."""
        return self._strategy.is_list
    @property

    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        return self._strategy.is_dict
    @property

    def type(self) -> str:
        """Get the type of this node."""
        return self._strategy.type
    @property

    def value(self) -> T:
        """Get the value of this node, typed as T."""
        return self._strategy.value  # type: ignore[return-value]
# ==============================================================================
# EDGE FACADE BASE CLASS
# ==============================================================================


class AEdge[P](IEdge[P]):
    """
    Abstract base class for all edge implementations with generic type parameter.
    Generic type parameter:
        P: The type of values in edge property dictionaries.
    Follows GUIDELINES_DEV.md naming: IEdge → AEdge → XWEdge
    Delegates to edge strategies for actual graph storage.
    """

    def __init__(self, strategy: iEdgeStrategy):
        self._strategy = strategy

    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: dict[str, P] | None = None,
                 is_bidirectional: bool = False, edge_id: str | None = None) -> str:
        """Add an edge between source and target with typed properties."""
        return self._strategy.add_edge(source, target, edge_type, weight, properties, is_bidirectional, edge_id)  # type: ignore[arg-type]

    def remove_edge(self, source: str, target: str, edge_id: str | None = None) -> bool:
        """Remove an edge between source and target."""
        return self._strategy.remove_edge(source, target, edge_id)

    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        return self._strategy.has_edge(source, target)

    def get_neighbors(self, node: str, edge_type: str | None = None, direction: str = "outgoing") -> list[str]:
        """Get neighbors of a node with optional filtering."""
        return self._strategy.get_neighbors(node, edge_type, direction)

    def get_edges(self, edge_type: str | None = None, direction: str = "both") -> list[dict[str, Any]]:
        """Get all edges with metadata."""
        return self._strategy.get_edges(edge_type, direction)

    def get_edge_data(self, source: str, target: str, edge_id: str | None = None) -> dict[str, P] | None:
        """Get edge data/properties, typed as dict[str, P]."""
        return self._strategy.get_edge_data(source, target, edge_id)  # type: ignore[return-value]

    def shortest_path(self, source: str, target: str, edge_type: str | None = None) -> list[str]:
        """Find shortest path between nodes."""
        return self._strategy.shortest_path(source, target, edge_type)

    def find_cycles(self, start_node: str, edge_type: str | None = None, max_depth: int = 10) -> list[list[str]]:
        """Find cycles in the graph."""
        return self._strategy.find_cycles(start_node, edge_type, max_depth)

    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: str | None = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        return self._strategy.traverse_graph(start_node, strategy, max_depth, edge_type)

    def is_connected(self, source: str, target: str, edge_type: str | None = None) -> bool:
        """Check if nodes are connected."""
        return self._strategy.is_connected(source, target, edge_type)

    def __len__(self) -> int:
        """Get number of edges."""
        return len(self._strategy)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over edges with full metadata."""
        return iter(self._strategy)

    def to_native(self) -> Any:
        """Convert to native Python object."""
        return self._strategy.to_native()

    def copy(self) -> AEdge[P]:
        """Create a deep copy."""
        return AEdge(copy.deepcopy(self._strategy))  # type: ignore[return-value]
# Query classes removed - belong in xwquery project
# If needed, import from xwquery instead of xwnode

# Backward compatibility alias for older xwquery code.
XWNodeBase = ANode
