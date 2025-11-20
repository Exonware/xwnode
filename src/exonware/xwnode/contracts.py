#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/contracts.py

Facade Interfaces for XWNode - Clean Architecture

This module defines ONLY facade interfaces for XWNode and XWEdge.
Strategy interfaces are in their respective strategy folders:
- Node strategy interfaces: nodes/strategies/contracts.py
- Edge strategy interfaces: edges/strategies/contracts.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.30
Generation Date: 24-Oct-2025

Version History:
- v0.0.1.29: GUIDELINES Architecture (separated interface/implementation)
- v0.0.1.30: Unified Interfaces (merged duplicates)
- v0.0.1.28: Clean Separation (facade only, strategies in local folders)
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional, Dict, List, Union, Callable

# Import enums from defs.py
from .defs import NodeMode, EdgeMode, NodeTrait, EdgeTrait


# ==============================================================================
# NODE FACADE INTERFACE
# ==============================================================================

class INode(ABC):
    """
    Node interface - defines the contract for all node implementations.
    
    This is the top-level interface that all node classes must implement.
    Follows GUIDELINES_DEV.md naming: INode (interface) → ANode (abstract) → XWNode (concrete).
    """
    
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['INode']:
        """Get a node by path."""
        pass
    
    @abstractmethod
    def set(self, path: str, value: Any, in_place: bool = True) -> 'INode':
        """Set a value at path."""
        pass
    
    @abstractmethod
    def delete(self, path: str, in_place: bool = True) -> 'INode':
        """Delete a node at path."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        pass
    
    @abstractmethod
    def find(self, path: str, in_place: bool = False) -> Optional['INode']:
        """Find a node by path."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def copy(self) -> 'INode':
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
    def merge(self, other: 'INode', strategy: str = "replace") -> 'INode':
        """Merge with another node."""
        pass
    
    @abstractmethod
    def diff(self, other: 'INode') -> Dict[str, Any]:
        """Get differences with another node."""
        pass
    
    @abstractmethod
    def transform(self, transformer: callable) -> 'INode':
        """Transform using a function."""
        pass
    
    @abstractmethod
    def select(self, *paths: str) -> Dict[str, 'INode']:
        """Select multiple paths."""
        pass
    
    # Container methods
    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator['INode']:
        """Iterate over children."""
        pass
    
    @abstractmethod
    def __getitem__(self, key: Union[str, int]) -> 'INode':
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


# ==============================================================================
# EDGE FACADE INTERFACE
# ==============================================================================

class IEdge(ABC):
    """
    Edge interface - defines the contract for all edge implementations.
    
    This is the top-level interface that all edge classes must implement.
    Follows GUIDELINES_DEV.md naming: IEdge (interface) → AEdge (abstract) → XWEdge (concrete).
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
    def copy(self) -> 'IEdge':
        """Create a deep copy."""
        pass
