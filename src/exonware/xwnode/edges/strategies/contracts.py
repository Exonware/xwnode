#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/edges/strategies/contracts.py

Edge Strategy Contracts

This module defines contracts and enums for edge strategies.
Moved from root contracts.py to follow GUIDELINES_DEV.md structure.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.30
Generation Date: 24-Oct-2025
"""

from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Optional, Iterator, Dict, List

# Import EdgeMode and EdgeTrait from defs
from ...defs import EdgeMode, EdgeTrait


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
# EDGE STRATEGY INTERFACE
# ==============================================================================

class IEdgeStrategy(ABC):
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


# Backward compatibility alias
iEdgeStrategy = IEdgeStrategy

