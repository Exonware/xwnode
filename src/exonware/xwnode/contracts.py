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
Version: 0.0.1.31
Generation Date: 24-Oct-2025

Version History:
- v0.0.1.29: GUIDELINES Architecture (separated interface/implementation)
- v0.0.1.30: Unified Interfaces (merged duplicates)
- v0.0.1.28: Clean Separation (facade only, strategies in local folders)
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional, Union, TypeVar
from collections.abc import Callable

# Import enums from defs.py
from .defs import NodeMode, EdgeMode, NodeTrait, EdgeTrait

# Type variables for generic types
# T: Node value type - the type of data stored in nodes (e.g., dict[str, int], User, Any)
# P: Edge property type - the type of values in edge property dictionaries (e.g., str, dict[str, Any], Any)
T = TypeVar('T')  # Value type for nodes
P = TypeVar('P')  # Property type for edges


# ==============================================================================
# NODE FACADE INTERFACE
# ==============================================================================

class INode[T](ABC):
    """
    Node interface with generic type parameter - defines the contract for all node implementations.
    
    Generic type parameter:
        T: The type of the native value returned by to_native() and value property.
           Defaults to Any for backward compatibility with heterogeneous data.
    
    This is the top-level interface that all node classes must implement.
    Follows GUIDELINES_DEV.md naming: INode (interface) → ANode (abstract) → XWNode (concrete).
    
    Examples:
        # Flexible usage (default - Any type)
        node: INode[Any] = XWNode.from_native({"key": "value"})
        
        # Type-safe usage for known structures
        user_data: INode[dict[str, Any]] = XWNode.from_native({"name": "Alice", "age": 30})
        user_list: INode[list[dict[str, Any]]] = XWNode.from_native([{"name": "Alice"}])
    """
    
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['INode[T]']:
        """Get a node by path."""
        pass
    
    @abstractmethod
    def set(self, path: str, value: Any, in_place: bool = True) -> 'INode[T]':
        """Set a value at path."""
        pass
    
    @abstractmethod
    def delete(self, path: str, in_place: bool = True) -> 'INode[T]':
        """Delete a node at path."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        pass
    
    @abstractmethod
    def find(self, path: str, in_place: bool = False) -> Optional['INode[T]']:
        """Find a node by path."""
        pass
    
    @abstractmethod
    def to_native(self) -> T:
        """Convert to native Python object of type T."""
        pass
    
    @abstractmethod
    def copy(self) -> 'INode[T]':
        """Create a deep copy."""
        pass
    
    @abstractmethod
    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        pass
    
    @abstractmethod
    def flatten(self, separator: str = ".") -> dict[str, Any]:
        """Flatten to dictionary."""
        pass
    
    @abstractmethod
    def merge(self, other: 'INode[T]', strategy: str = "replace") -> 'INode[T]':
        """Merge with another node."""
        pass
    
    @abstractmethod
    def diff(self, other: 'INode[T]') -> dict[str, Any]:
        """Get differences with another node."""
        pass
    
    @abstractmethod
    def transform(self, transformer: Callable[[Any], Any]) -> 'INode[T]':
        """Transform using a function."""
        pass
    
    @abstractmethod
    def select(self, *paths: str) -> dict[str, 'INode[T]']:
        """Select multiple paths."""
        pass
    
    # Container methods
    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator['INode[T]']:
        """Iterate over children."""
        pass
    
    @abstractmethod
    def __getitem__(self, key: Union[str, int, slice]) -> 'INode[T]':
        """Get child by key, index, or slice."""
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
    def value(self) -> T:
        """Get the value of this node, typed as T."""
        pass


# ==============================================================================
# EDGE FACADE INTERFACE
# ==============================================================================

class IEdge[P](ABC):
    """
    Edge interface with generic type parameter - defines the contract for all edge implementations.
    
    Generic type parameter:
        P: The type of values in edge property dictionaries.
           Defaults to Any for backward compatibility with mixed property types.
    
    This is the top-level interface that all edge classes must implement.
    Follows GUIDELINES_DEV.md naming: IEdge (interface) → AEdge (abstract) → XWEdge (concrete).
    
    Examples:
        # Flexible usage (default - Any property type)
        edge: IEdge[Any] = XWEdge()
        
        # Type-safe usage for known property structures
        typed_edge: IEdge[str] = XWEdge()  # Properties are dict[str, str]
        complex_edge: IEdge[dict[str, Any]] = XWEdge()  # Nested properties
    """
    
    @abstractmethod
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[dict[str, P]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with typed properties."""
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
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> list[str]:
        """Get neighbors of a node with optional filtering."""
        pass
    
    @abstractmethod
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> list[dict[str, Any]]:
        """Get all edges with metadata."""
        pass
    
    @abstractmethod
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[dict[str, P]]:
        """Get edge data/properties, typed as dict[str, P]."""
        pass
    
    @abstractmethod
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> list[str]:
        """Find shortest path between nodes."""
        pass
    
    @abstractmethod
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> list[list[str]]:
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
    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over edges with full metadata."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def copy(self) -> 'IEdge[P]':
        """Create a deep copy."""
        pass
