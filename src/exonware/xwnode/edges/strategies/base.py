#!/usr/bin/env python3
"""
Edge Strategy Base Classes
This module defines the abstract base classes for all edge strategy implementations:
- AEdgeStrategy: Base strategy for all edge implementations
- ALinearEdgeStrategy: Linear edge capabilities (sequential connections)
- ATreeEdgeStrategy: Tree edge capabilities (hierarchical connections)
- AGraphEdgeStrategy: Graph edge capabilities (network connections)
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: January 2, 2025
"""

from abc import ABC, abstractmethod
from typing import Any
from .contracts import IEdgeStrategy
from ...errors import XWNodeTypeError, XWNodeValueError


class AEdgeStrategy(IEdgeStrategy):
    """Base strategy for all edge implementations - extends iEdgeStrategy interface."""

    def __init__(self, **options):
        """Initialize edge strategy."""
        self._options = options
        self._mode = options.get('mode', 'AUTO')
        self._traits = options.get('traits', None)
    @abstractmethod

    def add_edge(self, from_node: Any, to_node: Any, **kwargs) -> None:
        """Add edge between nodes."""
        pass
    @abstractmethod

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes."""
        pass
    @abstractmethod

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists."""
        pass
    @abstractmethod

    def get_edge_count(self) -> int:
        """Get total number of edges."""
        pass
    @abstractmethod

    def get_vertex_count(self) -> int:
        """Get total number of vertices."""
        pass

    def get_mode(self) -> str:
        """Get strategy mode."""
        return self._mode

    def get_traits(self):
        """Get strategy traits."""
        return self._traits


class ALinearEdgeStrategy(AEdgeStrategy):
    """Linear edge capabilities (sequential connections)."""
    @abstractmethod

    def get_next(self, node: Any) -> Any | None:
        """Get next node in sequence."""
        pass
    @abstractmethod

    def get_previous(self, node: Any) -> Any | None:
        """Get previous node in sequence."""
        pass
    @abstractmethod

    def get_first(self) -> Any | None:
        """Get first node in sequence."""
        pass
    @abstractmethod

    def get_last(self) -> Any | None:
        """Get last node in sequence."""
        pass
    @abstractmethod

    def insert_after(self, node: Any, new_node: Any) -> None:
        """Insert new node after specified node."""
        pass
    @abstractmethod

    def insert_before(self, node: Any, new_node: Any) -> None:
        """Insert new node before specified node."""
        pass


class ATreeEdgeStrategy(AEdgeStrategy):
    """Tree edge capabilities (hierarchical connections)."""
    @abstractmethod

    def get_parent(self, node: Any) -> Any | None:
        """Get parent node."""
        pass
    @abstractmethod

    def get_children(self, node: Any) -> list[Any]:
        """Get child nodes."""
        pass
    @abstractmethod

    def get_siblings(self, node: Any) -> list[Any]:
        """Get sibling nodes."""
        pass
    @abstractmethod

    def get_root(self) -> Any | None:
        """Get root node."""
        pass
    @abstractmethod

    def get_leaves(self) -> list[Any]:
        """Get leaf nodes."""
        pass
    @abstractmethod

    def get_depth(self, node: Any) -> int:
        """Get depth of node."""
        pass
    @abstractmethod

    def get_height(self) -> int:
        """Get height of tree."""
        pass
    @abstractmethod

    def is_ancestor(self, ancestor: Any, descendant: Any) -> bool:
        """Check if one node is ancestor of another."""
        pass


class AGraphEdgeStrategy(AEdgeStrategy):
    """Graph edge capabilities (network connections)."""
    @abstractmethod

    def get_neighbors(self, node: Any) -> list[Any]:
        """Get all neighboring nodes."""
        pass
    @abstractmethod

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight."""
        pass
    @abstractmethod

    def set_edge_weight(self, from_node: Any, to_node: Any, weight: float) -> None:
        """Set edge weight."""
        pass
    @abstractmethod

    def find_shortest_path(self, start: Any, end: Any) -> list[Any]:
        """Find shortest path between nodes."""
        pass
    @abstractmethod

    def find_all_paths(self, start: Any, end: Any) -> list[list[Any]]:
        """Find all paths between nodes."""
        pass
    @abstractmethod

    def get_connected_components(self) -> list[list[Any]]:
        """Get all connected components."""
        pass
    @abstractmethod

    def is_connected(self, start: Any, end: Any) -> bool:
        """Check if two nodes are connected."""
        pass
    @abstractmethod

    def get_degree(self, node: Any) -> int:
        """Get degree of node."""
        pass
    @abstractmethod

    def is_cyclic(self) -> bool:
        """Check if graph contains cycles."""
        pass
