#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/contracts.py

Contract Interfaces for XWNode Strategy Pattern - Unified Architecture

This module defines the unified contracts that all node and edge strategies must implement.
Merges facade API (path-based) with strategy API (key-based) for complete interface.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.26
Generation Date: 22-Oct-2025

Version History:
- v0.0.1.29: GUIDELINES Architecture (separated interface/implementation)
- v0.0.1.30: Unified Interfaces (merged iNodeStrategy + INodeStrategy → INodeStrategy)
             Unified Interfaces (merged iEdgeStrategy + IEdgeStrategy → IEdgeStrategy)
             Single source of truth for all contracts
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional, Dict, List, Union, Callable, AsyncIterator
from enum import Enum, Flag
import asyncio

# Import all enums from defs.py to avoid circular references
from .defs import (
    NodeMode, EdgeMode, NodeTrait, EdgeTrait
)
# Note: QueryMode and QueryTrait are in xwquery.defs module


# ==============================================================================
# NODE STRATEGY ENUMS AND OPTIMIZATIONS
# ==============================================================================

# Pre-computed common operations (shared frozenset instance)
NODE_COMMON_OPERATIONS = frozenset([
    "insert", "find", "delete", "size", "is_empty",
    "keys", "values", "items", "to_native"
])

# Global cache for get_supported_operations() conversion
_NODE_OPERATIONS_CACHE: dict[type, list[str]] = {}


class NodeType(Enum):
    """Node strategy type classification with explicit int values."""
    LINEAR = 1    # Array-like, sequential access
    TREE = 2      # Hierarchical, key-based ordering
    GRAPH = 3     # Nodes with relationships
    MATRIX = 4    # 2D grid access
    HYBRID = 5    # Combination of multiple types


# ==============================================================================
# UNIFIED NODE STRATEGY INTERFACE
# ==============================================================================

class INodeStrategy(ABC):
    """
    UNIFIED node strategy interface - merges facade and strategy APIs.
    
    This interface combines:
    1. Facade API (path-based): put/get for XWNode facade compatibility
    2. Strategy API (key-based): insert/find for direct strategy operations
    3. Async-first: All operations have async versions
    4. Optimizations: __slots__, caching, thread-safety
    
    Following GUIDELINES_DEV.md Priorities:
    1. Security: Thread-safe with immutable data, atomic operations
    2. Usability: Dual API (path + key based), sync + async
    3. Maintainability: Clean interface, well-documented
    4. Performance: O(1) frozenset lookups, cached conversions, __slots__
    5. Extensibility: Auto-optimizing subclasses via __init_subclass__
    """
    
    # Memory optimization: no __dict__ overhead
    __slots__ = ()
    
    # Strategy type classification (immutable, thread-safe)
    STRATEGY_TYPE: NodeType = NodeType.TREE  # Default
    
    # Supported operations (immutable frozenset, thread-safe, O(1) lookups)
    SUPPORTED_OPERATIONS: frozenset[str] = frozenset()  # Empty = supports all
    
    def __init_subclass__(cls, **kwargs):
        """
        Auto-optimize subclasses at definition time.
        
        - Auto-converts list/set/tuple to frozenset for SUPPORTED_OPERATIONS
        - Pre-caches operations list for O(1) get_supported_operations()
        - Validates subclass configuration
        """
        super().__init_subclass__(**kwargs)
        
        # Auto-convert SUPPORTED_OPERATIONS to frozenset if needed
        if hasattr(cls, 'SUPPORTED_OPERATIONS'):
            ops = cls.SUPPORTED_OPERATIONS
            if not isinstance(ops, frozenset):
                if isinstance(ops, (list, set, tuple)):
                    cls.SUPPORTED_OPERATIONS = frozenset(ops)
        
        # Pre-cache operations list for O(1) retrieval
        if cls not in _NODE_OPERATIONS_CACHE:
            _NODE_OPERATIONS_CACHE[cls] = list(cls.SUPPORTED_OPERATIONS)
    
    # =========================================================================
    # STRATEGY API (Key-based operations - Primary for concrete strategies)
    # =========================================================================
    
    @abstractmethod
    async def insert_async(self, key: Any, value: Any) -> None:
        """Async insert operation (primary strategy API)."""
        pass
    
    @abstractmethod
    def insert(self, key: Any, value: Any) -> None:
        """Sync insert operation (wraps async)."""
        pass
    
    @abstractmethod
    async def find_async(self, key: Any) -> Optional[Any]:
        """Async find operation (primary strategy API)."""
        pass
    
    @abstractmethod
    def find(self, key: Any) -> Optional[Any]:
        """Sync find operation (wraps async)."""
        pass
    
    @abstractmethod
    async def delete_async(self, key: Any) -> bool:
        """Async delete operation (primary strategy API)."""
        pass
    
    @abstractmethod
    async def size_async(self) -> int:
        """Async size check."""
        pass
    
    @abstractmethod
    async def is_empty_async(self) -> bool:
        """Async empty check."""
        pass
    
    @abstractmethod
    async def to_native_async(self) -> Any:
        """Async convert to native Python object."""
        pass
    
    @abstractmethod
    def keys_async(self) -> AsyncIterator[Any]:
        """Async iterator over keys."""
        pass
    
    @abstractmethod
    def values_async(self) -> AsyncIterator[Any]:
        """Async iterator over values."""
        pass
    
    @abstractmethod
    def items_async(self) -> AsyncIterator[tuple[Any, Any]]:
        """Async iterator over key-value pairs."""
        pass
    
    # =========================================================================
    # FACADE API (Path-based operations - For XWNode facade compatibility)
    # =========================================================================
    
    @abstractmethod
    def create_from_data(self, data: Any) -> 'INodeStrategy':
        """Create a new strategy instance from data."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object (sync version)."""
        pass
    
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['INodeStrategy']:
        """Get a child node by path (facade API)."""
        pass
    
    @abstractmethod
    def put(self, path: str, value: Any) -> 'INodeStrategy':
        """Set a value at path (facade API)."""
        pass
    
    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete a node at path (facade API)."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists (facade API)."""
        pass
    
    @abstractmethod
    def keys(self) -> Iterator[Any]:
        """Get keys iterator (sync version)."""
        pass
    
    @abstractmethod
    def values(self) -> Iterator[Any]:
        """Get values iterator (sync version)."""
        pass
    
    @abstractmethod
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get items iterator (sync version)."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator['INodeStrategy']:
        """Iterate over children."""
        pass
    
    @abstractmethod
    def __getitem__(self, key: Union[str, int]) -> 'INodeStrategy':
        """Get child by key or index."""
        pass
    
    @abstractmethod
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        pass
    
    @abstractmethod
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        pass
    
    # Type checking properties
    @property
    @abstractmethod
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        pass
    
    @property
    @abstractmethod
    def is_list(self) -> bool:
        """Check if this is a list node."""
        pass
    
    @property
    @abstractmethod
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        pass
    
    @property
    @abstractmethod
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        pass
    
    @property
    @abstractmethod
    def is_object(self) -> bool:
        """Check if this is an object node."""
        pass
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Get the type of this node."""
        pass
    
    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the value of this node."""
        pass
    
    # =========================================================================
    # CLASS METHODS (Thread-safe - operate on immutable class data)
    # =========================================================================
    
    @classmethod
    def supports_operation(cls, operation: str) -> bool:
        """
        Check if this strategy supports a specific operation.
        
        Performance: O(1) - frozenset lookup
        Thread-Safety: Immutable data, no locks needed
        """
        if not cls.SUPPORTED_OPERATIONS:
            return True  # Empty = supports all
        return operation in cls.SUPPORTED_OPERATIONS
    
    @classmethod
    def get_supported_operations(cls) -> list[str]:
        """
        Get list of supported operations.
        
        Performance: O(1) - cached result
        Thread-Safety: Immutable cached data, no locks needed
        """
        # Return cached list (pre-computed in __init_subclass__)
        if cls in _NODE_OPERATIONS_CACHE:
            return _NODE_OPERATIONS_CACHE[cls]
        # Fallback for dynamically created classes
        return list(cls.SUPPORTED_OPERATIONS)
    
    # Optional properties with default implementations
    @property
    def uri(self) -> Optional[str]:
        """Get URI (for reference/object nodes)."""
        return None
    
    @property
    def reference_type(self) -> Optional[str]:
        """Get reference type (for reference nodes)."""
        return None
    
    @property
    def object_type(self) -> Optional[str]:
        """Get object type (for object nodes)."""
        return None
    
    @property
    def mime_type(self) -> Optional[str]:
        """Get MIME type (for object nodes)."""
        return None
    
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata (for reference/object nodes)."""
        return None
    
    # Strategy information
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass
    
    @property
    @abstractmethod
    def supported_traits(self) -> List[NodeTrait]:
        """Get supported traits for this strategy."""
        pass
    
    @abstractmethod
    def get_mode(self) -> NodeMode:
        """
        Get the strategy mode (NodeMode enum).
        
        Returns:
            NodeMode enum value for this strategy
        """
        pass
    
    @abstractmethod
    def get_traits(self) -> NodeTrait:
        """
        Get the strategy traits (NodeTrait flags).
        
        Returns:
            NodeTrait flags for this strategy
        """
        pass


# ==============================================================================
# BACKWARD COMPATIBILITY (Revert to v0.0.1.28 naming)
# ==============================================================================
iNodeStrategy = INodeStrategy


# ==============================================================================
# EDGE STRATEGY ENUMS AND OPTIMIZATIONS
# ==============================================================================

# Pre-computed common edge operations
EDGE_COMMON_OPERATIONS = frozenset([
    "add_edge", "remove_edge", "has_edge", "get_edge",
    "get_neighbors", "get_edges"
])

# Global cache for edge operations
_EDGE_OPERATIONS_CACHE: dict[type, list[str]] = {}


class EdgeType(Enum):
    """Edge strategy type classification with explicit int values."""
    LINEAR = 1    # Sequential connections
    TREE = 2      # Hierarchical connections
    GRAPH = 3     # Network connections
    MATRIX = 4    # Grid-based connections
    SPATIAL = 5   # Spatial index connections
    HYBRID = 6    # Combination of multiple types


# ==============================================================================
# UNIFIED EDGE STRATEGY INTERFACE
# ==============================================================================

class IEdgeStrategy(ABC):
    """
    UNIFIED edge strategy interface - merges facade and strategy APIs.
    
    This interface combines:
    1. Graph operations: add_edge/remove_edge for direct strategy use
    2. Async-first: All operations have async versions
    3. Optimizations: __slots__, caching, thread-safety
    
    All edge strategies must implement this interface to ensure
    compatibility with the XWNode graph operations, including advanced
    features like edge types, weights, properties, and graph algorithms.
    """
    
    # Memory optimization
    __slots__ = ()
    
    # Strategy type classification
    STRATEGY_TYPE: EdgeType = EdgeType.GRAPH  # Default
    
    # Supported operations
    SUPPORTED_OPERATIONS: frozenset[str] = frozenset()  # Empty = supports all
    
    def __init_subclass__(cls, **kwargs):
        """Auto-optimize edge strategy subclasses."""
        super().__init_subclass__(**kwargs)
        
        # Auto-convert SUPPORTED_OPERATIONS to frozenset
        if hasattr(cls, 'SUPPORTED_OPERATIONS'):
            ops = cls.SUPPORTED_OPERATIONS
            if not isinstance(ops, frozenset):
                if isinstance(ops, (list, set, tuple)):
                    cls.SUPPORTED_OPERATIONS = frozenset(ops)
        
        # Pre-cache operations list
        if cls not in _EDGE_OPERATIONS_CACHE:
            _EDGE_OPERATIONS_CACHE[cls] = list(cls.SUPPORTED_OPERATIONS)
    
    # =========================================================================
    # ASYNC API (Primary)
    # =========================================================================
    
    @abstractmethod
    async def add_edge_async(self, source: str, target: str, edge_type: str = "default",
                            weight: float = 1.0, **properties) -> None:
        """Async add edge operation."""
        pass
    
    @abstractmethod
    async def remove_edge_async(self, source: str, target: str, edge_type: str = "default") -> bool:
        """Async remove edge operation."""
        pass
    
    @abstractmethod
    async def has_edge_async(self, source: str, target: str, edge_type: str = "default") -> bool:
        """Async check if edge exists."""
        pass
    
    # =========================================================================
    # SYNC API (Wraps async)
    # =========================================================================
    
    @abstractmethod
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with advanced properties."""
        pass
    
    @abstractmethod
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove an edge between source and target."""
        pass
    
    @abstractmethod
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> List[str]:
        """Get neighbors of a node with optional filtering."""
        pass
    
    @abstractmethod
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        """Get all edges with metadata."""
        pass
    
    @abstractmethod
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get edge data/properties."""
        pass
    
    @abstractmethod
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> List[str]:
        """Find shortest path between nodes."""
        pass
    
    @abstractmethod
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> List[List[str]]:
        """Find cycles in the graph."""
        pass
    
    @abstractmethod
    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: Optional[str] = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        pass
    
    @abstractmethod
    def is_connected(self, source: str, target: str, edge_type: Optional[str] = None) -> bool:
        """Check if nodes are connected."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get number of edges."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over edges with full metadata."""
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass
    
    @property
    @abstractmethod
    def supported_traits(self) -> List[EdgeTrait]:
        """Get supported traits for this strategy."""
        pass
    
    @abstractmethod
    def get_mode(self) -> EdgeMode:
        """
        Get the strategy mode (EdgeMode enum).
        
        Returns:
            EdgeMode enum value for this strategy
        """
        pass
    
    @abstractmethod
    def get_traits(self) -> EdgeTrait:
        """
        Get the strategy traits (EdgeTrait flags).
        
        Returns:
            EdgeTrait flags for this strategy
        """
        pass


# Backward compatibility
iEdgeStrategy = IEdgeStrategy


class iEdge(ABC):
    """
    Abstract interface for edge facade.
    
    This defines the public interface for edge operations with advanced features
    including edge types, weights, properties, and graph algorithms.
    """
    
    @abstractmethod
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with advanced properties."""
        pass
    
    @abstractmethod
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove an edge between source and target."""
        pass
    
    @abstractmethod
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> List[str]:
        """Get neighbors of a node with optional filtering."""
        pass
    
    @abstractmethod
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        """Get all edges with metadata."""
        pass
    
    @abstractmethod
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get edge data/properties."""
        pass
    
    @abstractmethod
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> List[str]:
        """Find shortest path between nodes."""
        pass
    
    @abstractmethod
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> List[List[str]]:
        """Find cycles in the graph."""
        pass
    
    @abstractmethod
    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: Optional[str] = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        pass
    
    @abstractmethod
    def is_connected(self, source: str, target: str, edge_type: Optional[str] = None) -> bool:
        """Check if nodes are connected."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get number of edges."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over edges with full metadata."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def copy(self) -> 'iEdge':
        """Create a deep copy."""
        pass


class iNodeFacade(ABC):
    """
    Abstract interface for the XWNode facade.
    
    This defines the public interface that XWNode must implement.
    """
    
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['iNodeFacade']:
        """Get a node by path."""
        pass
    
    @abstractmethod
    def set(self, path: str, value: Any, in_place: bool = True) -> 'iNodeFacade':
        """Set a value at path."""
        pass
    
    @abstractmethod
    def delete(self, path: str, in_place: bool = True) -> 'iNodeFacade':
        """Delete a node at path."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        pass
    
    @abstractmethod
    def find(self, path: str, in_place: bool = False) -> Optional['iNodeFacade']:
        """Find a node by path."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def copy(self) -> 'iNodeFacade':
        """Create a deep copy."""
        pass
    
    @abstractmethod
    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        pass
    
    @abstractmethod
    def flatten(self, separator: str = ".") -> Dict[str, Any]:
        """Flatten to dictionary."""
        pass
    
    @abstractmethod
    def merge(self, other: 'iNodeFacade', strategy: str = "replace") -> 'iNodeFacade':
        """Merge with another node."""
        pass
    
    @abstractmethod
    def diff(self, other: 'iNodeFacade') -> Dict[str, Any]:
        """Get differences with another node."""
        pass
    
    @abstractmethod
    def transform(self, transformer: callable) -> 'iNodeFacade':
        """Transform using a function."""
        pass
    
    @abstractmethod
    def select(self, *paths: str) -> Dict[str, 'iNodeFacade']:
        """Select multiple paths."""
        pass
    
    # Container methods
    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator['iNodeFacade']:
        """Iterate over children."""
        pass
    
    @abstractmethod
    def __getitem__(self, key: Union[str, int]) -> 'iNodeFacade':
        """Get child by key or index."""
        pass
    
    @abstractmethod
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        pass
    
    @abstractmethod
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        pass
    
    # Type checking properties
    @property
    @abstractmethod
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        pass
    
    @property
    @abstractmethod
    def is_list(self) -> bool:
        """Check if this is a list node."""
        pass
    
    @property
    @abstractmethod
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        pass
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Get the type of this node."""
        pass
    
    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the value of this node."""
        pass

# ============================================================================
# QUERY INTERFACES
# ============================================================================
# Note: Query implementation details (QueryMode, QueryTrait) are in xwquery module.
# These are just generic interfaces for query capabilities.


class iQueryResult(ABC):
    """Interface for query results."""
    
    @property
    @abstractmethod
    def nodes(self) -> List['iNodeFacade']:
        """Get result nodes."""
        pass
    
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Get result metadata."""
        pass
    
    @abstractmethod
    def first(self) -> Optional['iNodeFacade']:
        """Get first result."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get result count."""
        pass
    
    @abstractmethod
    def filter(self, predicate: Callable[['iNodeFacade'], bool]) -> 'iQueryResult':
        """Filter results."""
        pass
    
    @abstractmethod
    def limit(self, limit: int) -> 'iQueryResult':
        """Limit results."""
        pass
    
    @abstractmethod
    def offset(self, offset: int) -> 'iQueryResult':
        """Offset results."""
        pass


class iQueryEngine(ABC):
    """Interface for query engines."""
    
    @abstractmethod
    def execute_query(self, query_string: str, context: Dict[str, Any]) -> iQueryResult:
        """Execute query and return results."""
        pass
    
    @abstractmethod
    def parse_query(self, query_string: str) -> Dict[str, Any]:
        """Parse query string into structured format."""
        pass
    
    @abstractmethod
    def validate_query(self, query_string: str) -> bool:
        """Validate query string."""
        pass


class iQuery(ABC):
    """Interface for query capabilities."""
    
    @abstractmethod
    def query(self, query_string: str, query_type: str = "hybrid", **kwargs) -> iQueryResult:
        """Execute a query."""
        pass
    
    @abstractmethod
    def find_nodes(self, predicate: Callable[['iNodeFacade'], bool], max_results: Optional[int] = None) -> iQueryResult:
        """Find nodes matching predicate."""
        pass
    
    @abstractmethod
    def find_by_path(self, path_pattern: str) -> iQueryResult:
        """Find nodes by path pattern."""
        pass
    
    @abstractmethod
    def find_by_value(self, value: Any, exact_match: bool = True) -> iQueryResult:
        """Find nodes by value."""
        pass
    
    @abstractmethod
    def count_nodes(self, predicate: Optional[Callable[['iNodeFacade'], bool]] = None) -> int:
        """Count nodes matching predicate."""
        pass
    
    @abstractmethod
    def select(self, selector: str, **kwargs) -> List['iNodeFacade']:
        """Select nodes using a selector expression."""
        pass
    
    @abstractmethod
    def filter(self, condition: str, **kwargs) -> List['iNodeFacade']:
        """Filter nodes based on a condition."""
        pass
    
    @abstractmethod
    def where(self, condition: str) -> List['iNodeFacade']:
        """Filter nodes using a where condition."""
        pass
    
    @abstractmethod
    def sort(self, key: str = None, reverse: bool = False) -> List['iNodeFacade']:
        """Sort nodes by a key."""
        pass
    
    @abstractmethod
    def limit(self, count: int) -> List['iNodeFacade']:
        """Limit the number of results."""
        pass
    
    @abstractmethod
    def skip(self, count: int) -> List['iNodeFacade']:
        """Skip a number of results."""
        pass
    
    @abstractmethod
    def first(self) -> Optional['iNodeFacade']:
        """Get the first result."""
        pass
    
    @abstractmethod
    def last(self) -> Optional['iNodeFacade']:
        """Get the last result."""
        pass
    
    @abstractmethod
    def group_by(self, key: str) -> Dict[str, List['iNodeFacade']]:
        """Group nodes by a key."""
        pass
    
    @abstractmethod
    def distinct(self, key: str = None) -> List['iNodeFacade']:
        """Get distinct values."""
        pass
    
    @abstractmethod
    def clear_query_cache(self):
        """Clear the query cache."""
        pass
    
    @abstractmethod
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query execution statistics."""
        pass
