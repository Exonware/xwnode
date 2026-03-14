#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/edges/strategies/contracts.py
Edge Strategy Contracts
This module defines contracts and enums for edge strategies.
Moved from root contracts.py to follow GUIDELINES_DEV.md structure.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
Generation Date: 24-Oct-2025
"""

from enum import Enum
from typing import Any, Protocol, runtime_checkable
# Import EdgeMode and EdgeTrait from defs
from ...defs import EdgeMode, EdgeTrait
# ==============================================================================
# EDGE STRATEGY ENUMS AND OPTIMIZATIONS
# ==============================================================================
# Pre-computed common edge operations
from collections.abc import Iterator
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
# EDGE STRATEGY INTERFACE
# ==============================================================================
@runtime_checkable

class IEdgeStrategy(Protocol):
    """
    Edge strategy interface - defines contract for all edge implementations.
    This interface defines the operations that all edge strategies must implement
    for compatibility with XWNode graph operations, including advanced features
    like edge types, weights, properties, and graph algorithms.
    Following GUIDELINES_DEV.md Priorities:
    1. Security: Thread-safe operations
    2. Usability: Clear interface
    3. Maintainability: Well-documented
    4. Performance: Optimized lookups
    5. Extensibility: Easy to add new strategies
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
    # EDGE OPERATIONS
    # =========================================================================

    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: dict[str, Any] | None = None,
                 is_bidirectional: bool = False, edge_id: str | None = None) -> str:
        """Add an edge between source and target with advanced properties."""
        ...

    def remove_edge(self, source: str, target: str, edge_id: str | None = None) -> bool:
        """Remove an edge between source and target."""
        ...

    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        ...

    def get_neighbors(self, node: str, edge_type: str | None = None, direction: str = "outgoing") -> list[str]:
        """Get neighbors of a node with optional filtering."""
        ...

    def get_edges(self, edge_type: str | None = None, direction: str = "both") -> list[dict[str, Any]]:
        """Get all edges with metadata."""
        ...

    def get_edge_data(self, source: str, target: str, edge_id: str | None = None) -> dict[str, Any] | None:
        """Get edge data/properties."""
        ...

    def shortest_path(self, source: str, target: str, edge_type: str | None = None) -> list[str]:
        """Find shortest path between nodes."""
        ...

    def find_cycles(self, start_node: str, edge_type: str | None = None, max_depth: int = 10) -> list[list[str]]:
        """Find cycles in the graph."""
        ...

    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: str | None = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        ...

    def is_connected(self, source: str, target: str, edge_type: str | None = None) -> bool:
        """Check if nodes are connected."""
        ...

    def __len__(self) -> int:
        """Get number of edges."""
        ...

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over edges with full metadata."""
        ...
    @property

    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        ...
    @property

    def supported_traits(self) -> list[EdgeTrait]:
        """Get supported traits for this strategy."""
        ...

    def get_mode(self) -> EdgeMode:
        """
        Get the strategy mode (EdgeMode enum).
        Returns:
            EdgeMode enum value for this strategy
        """
        ...

    def get_traits(self) -> EdgeTrait:
        """
        Get the strategy traits (EdgeTrait flags).
        Returns:
            EdgeTrait flags for this strategy
        """
        ...
