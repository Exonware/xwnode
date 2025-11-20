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
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.30
Generation Date: 24-Oct-2025
"""

import threading
import copy
from abc import ABC
from typing import Any, Iterator, Union, Optional, List, Dict, Callable, TYPE_CHECKING
from collections import OrderedDict

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
    """Thread-safe path parser with caching."""
    
    def __init__(self, max_cache_size: int = 1024):
        self._cache = OrderedDict()
        self._max_cache_size = max_cache_size
        self._lock = threading.RLock()
    
    def parse(self, path: str) -> List[str]:
        """Parse a path string into parts."""
        with self._lock:
            if path in self._cache:
                record_cache_hit()
                return self._cache[path]
            
            record_cache_miss()
            parts = self._parse_path(path)
            
            # Cache the result
            if len(self._cache) >= self._max_cache_size:
                self._cache.popitem(last=False)
            self._cache[path] = parts
            
            return parts
    
    def _parse_path(self, path: str) -> List[str]:
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
    """Global cache for path lookups."""
    
    def __init__(self, max_size: int = 512):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._lock = threading.RLock()
        self._stats = {'hits': 0, 'misses': 0}
    
    def get(self, node_id: int, path: str) -> Optional[Any]:
        """Get cached result for node and path."""
        key = (node_id, path)
        with self._lock:
            if key in self._cache:
                self._stats['hits'] += 1
                return self._cache[key]
            self._stats['misses'] += 1
            return None
    
    def put(self, node_id: int, path: str, result: Any):
        """Cache result for node and path."""
        key = (node_id, path)
        with self._lock:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = result
    
    def clear(self):
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            return self._stats.copy()


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

class ANode(INode):
    """
    Abstract base class for all node implementations.
    
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
    def from_native(cls, data: Any) -> 'ANode':
        """Create ANode from native data."""
        # For now, we'll use a simple hash map strategy
        # In the full implementation, this would use the strategy manager
        from .common.utils.simple import SimpleNodeStrategy
        strategy = SimpleNodeStrategy.create_from_data(data)
        return cls(strategy)

    def get(self, path: str, default: Any = None) -> Optional['ANode']:
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
    
    def set(self, path: str, value: Any, in_place: bool = True) -> 'ANode':
        """Set a value at path."""
        new_strategy = self._strategy.put(path, value)
        if in_place:
            self._strategy = new_strategy
            return self
        else:
            return ANode(new_strategy)
    
    def delete(self, path: str, in_place: bool = True) -> 'ANode':
        """Delete a node at path."""
        success = self._strategy.delete(path)
        return self
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self._strategy.exists(path)
    
    def find(self, path: str, in_place: bool = False) -> Optional['ANode']:
        """Find a node by path."""
        return self.get(path)
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        return self._strategy.to_native()
    
    def copy(self) -> 'ANode':
        """Create a deep copy."""
        return ANode(self._strategy.create_from_data(self._strategy.to_native()))
    
    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        if path == ".":
            return len(self._strategy)
        node = self.get(path)
        return len(node._strategy) if node else 0
    
    def flatten(self, separator: str = ".") -> Dict[str, Any]:
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
    
    def merge(self, other: 'ANode', strategy: str = "replace") -> 'ANode':
        """Merge with another node."""
        # Simple implementation - just replace
        return ANode(self._strategy.create_from_data(other.to_native()))
    
    def diff(self, other: 'ANode') -> Dict[str, Any]:
        """Get differences with another node."""
        return {"changed": True}  # Simple implementation
    
    def transform(self, transformer: callable) -> 'ANode':
        """Transform using a function."""
        transformed_data = transformer(self.to_native())
        return ANode(self._strategy.create_from_data(transformed_data))
    
    def select(self, *paths: str) -> Dict[str, 'ANode']:
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
    
    def __iter__(self) -> Iterator['ANode']:
        """Iterate over children."""
        for child_strategy in self._strategy:
            yield ANode(child_strategy)
    
    def __getitem__(self, key: Union[str, int]) -> 'ANode':
        """Get child by key or index."""
        child_strategy = self._strategy[key]
        return ANode(child_strategy)
    
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        self._strategy[key] = value
    
    def __contains__(self, key: Union[str, int]) -> bool:
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
    def value(self) -> Any:
        """Get the value of this node."""
        return self._strategy.value


# ==============================================================================
# EDGE FACADE BASE CLASS
# ==============================================================================

class AEdge(IEdge):
    """
    Abstract base class for all edge implementations.
    
    Follows GUIDELINES_DEV.md naming: IEdge → AEdge → XWEdge
    Delegates to edge strategies for actual graph storage.
    """
    
    def __init__(self, strategy: iEdgeStrategy):
        self._strategy = strategy
    
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with advanced properties."""
        return self._strategy.add_edge(source, target, edge_type, weight, properties, is_bidirectional, edge_id)
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove an edge between source and target."""
        return self._strategy.remove_edge(source, target, edge_id)
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        return self._strategy.has_edge(source, target)
    
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> List[str]:
        """Get neighbors of a node with optional filtering."""
        return self._strategy.get_neighbors(node, edge_type, direction)
    
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        """Get all edges with metadata."""
        return self._strategy.get_edges(edge_type, direction)
    
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get edge data/properties."""
        return self._strategy.get_edge_data(source, target, edge_id)
    
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> List[str]:
        """Find shortest path between nodes."""
        return self._strategy.shortest_path(source, target, edge_type)
    
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> List[List[str]]:
        """Find cycles in the graph."""
        return self._strategy.find_cycles(start_node, edge_type, max_depth)
    
    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: Optional[str] = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        return self._strategy.traverse_graph(start_node, strategy, max_depth, edge_type)
    
    def is_connected(self, source: str, target: str, edge_type: Optional[str] = None) -> bool:
        """Check if nodes are connected."""
        return self._strategy.is_connected(source, target, edge_type)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return len(self._strategy)
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over edges with full metadata."""
        return iter(self._strategy)
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        return self._strategy.to_native()
    
    def copy(self) -> 'AEdge':
        """Create a deep copy."""
        return AEdge(copy.deepcopy(self._strategy))


# ==============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ==============================================================================

# Old class names (deprecated - use ANode, AEdge)
XWNodeBase = ANode
aEdge = AEdge

# Query classes removed - belong in xwquery project
# If needed, import from xwquery instead of xwnode

