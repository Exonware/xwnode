#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/contracts.py
Facade Interfaces for XWNode - Clean Architecture
This module defines ONLY facade interfaces for XWNode and XWEdge.
Strategy interfaces are in their respective strategy folders:
- Node strategy interfaces: nodes/strategies/contracts.py
- Edge strategy interfaces: edges/strategies/contracts.py
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.16
Generation Date: 24-Oct-2025
Version History:
- v0.0.1.29: GUIDELINES Architecture (separated interface/implementation)
- v0.0.1.30: Unified Interfaces (merged duplicates)
- v0.0.1.28: Clean Separation (facade only, strategies in local folders)
"""

from __future__ import annotations
from collections.abc import Iterator
from typing import Protocol, runtime_checkable
from typing import Any, TypeVar
from collections.abc import Callable
from enum import Enum, IntFlag, auto
# Import enums from defs.py
from .defs import NodeMode, EdgeMode, NodeTrait, EdgeTrait
# Type variables for generic types
# T: Node value type - the type of data stored in nodes (e.g., dict[str, int], User, Any)
# P: Edge property type - the type of values in edge property dictionaries (e.g., str, dict[str, Any], Any)
T = TypeVar('T')  # Value type for nodes
P = TypeVar('P')  # Property type for edges

# ==============================================================================
# QUERY COMPATIBILITY TYPES (legacy xwquery imports)
# ==============================================================================
class QueryMode(str, Enum):
    """Compatibility enum for query strategy mode selection."""
    AUTO = "AUTO"
    SQL = "SQL"
    XPATH = "XPATH"
    XQUERY = "XQUERY"
    XML_QUERY = "XML_QUERY"
    SPARQL = "SPARQL"
    PROMQL = "PROMQL"
    PIG = "PIG"
    PARTIQL = "PARTIQL"
    N1QL = "N1QL"
    MQL = "MQL"
    LOGQL = "LOGQL"
    LINQ = "LINQ"
    KQL = "KQL"
    JSON_QUERY = "JSON_QUERY"
    JSONIQ = "JSONIQ"
    JQ = "JQ"
    JMESPATH = "JMESPATH"
    HQL = "HQL"
    HIVEQL = "HIVEQL"
    GREMLIN = "GREMLIN"
    GRAPHQL = "GRAPHQL"
    GQL = "GQL"
    FLUX = "FLUX"
    EQL = "EQL"
    ELASTIC_DSL = "ELASTIC_DSL"
    DATALOG = "DATALOG"
    CYPHER = "CYPHER"
    CQL = "CQL"


class QueryTrait(IntFlag):
    """Compatibility bitflags for query capabilities."""
    NONE = 0
    STRUCTURED = auto()
    ANALYTICAL = auto()
    BATCH = auto()
    DOCUMENT = auto()
    GRAPH = auto()
    TEMPORAL = auto()
    STREAMING = auto()
    SEARCH = auto()
    TIME_SERIES = auto()
    UNSTRUCTURED = auto()
    TRANSACTIONAL = auto()


@runtime_checkable
class iQuery(Protocol):
    """Legacy query protocol compatibility alias."""
    def execute(self, query: str, **kwargs: Any) -> Any:
        ...


@runtime_checkable
class iQueryResult(Protocol):
    """Legacy query result protocol compatibility alias."""
    def to_native(self) -> Any:
        ...


@runtime_checkable
class IQueryStrategy(Protocol):
    """Legacy query strategy protocol compatibility alias."""
    def execute(self, query: str, **kwargs: Any) -> Any:
        ...

    def validate_query(self, query: str) -> bool:
        ...
# ==============================================================================
# NODE FACADE INTERFACE
# ==============================================================================
@runtime_checkable

class INode[T](Protocol):
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

    def get(self, path: str, default: Any = None) -> INode[T] | None:
        """Get a node by path."""
        ...

    def set(self, path: str, value: Any, in_place: bool = True) -> INode[T]:
        """Set a value at path."""
        ...

    def delete(self, path: str, in_place: bool = True) -> INode[T]:
        """Delete a node at path."""
        ...

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        ...

    def find(self, path: str, in_place: bool = False) -> INode[T] | None:
        """Find a node by path."""
        ...

    def to_native(self) -> T:
        """Convert to native Python object of type T."""
        ...

    def copy(self) -> INode[T]:
        """Create a deep copy."""
        ...

    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        ...

    def flatten(self, separator: str = ".") -> dict[str, Any]:
        """Flatten to dictionary."""
        ...

    def merge(self, other: INode[T], strategy: str = "replace") -> INode[T]:
        """Merge with another node."""
        ...

    def diff(self, other: INode[T]) -> dict[str, Any]:
        """Get differences with another node."""
        ...

    def transform(self, transformer: Callable[[Any], Any]) -> INode[T]:
        """Transform using a function."""
        ...

    def select(self, *paths: str) -> dict[str, INode[T]]:
        """Select multiple paths."""
        ...
    # Container methods

    def __len__(self) -> int:
        """Get length."""
        ...

    def __iter__(self) -> Iterator['INode[T]']:
        """Iterate over children."""
        ...

    def __getitem__(self, key: str | int | slice) -> INode[T]:
        """Get child by key, index, or slice."""
        ...

    def __setitem__(self, key: str | int, value: Any) -> None:
        """Set child by key or index."""
        ...

    def __contains__(self, key: str | int) -> bool:
        """Check if key exists."""
        ...
    # Type checking properties
    @property

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        ...
    @property

    def is_list(self) -> bool:
        """Check if this is a list node."""
        ...
    @property

    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        ...
    @property

    def type(self) -> str:
        """Get the type of this node."""
        ...
    @property

    def value(self) -> T:
        """Get the value of this node, typed as T."""
        ...
# ==============================================================================
# EDGE FACADE INTERFACE
# ==============================================================================
@runtime_checkable

class IEdge[P](Protocol):
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

    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: dict[str, P] | None = None,
                 is_bidirectional: bool = False, edge_id: str | None = None) -> str:
        """Add an edge between source and target with typed properties."""
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

    def get_edge_data(self, source: str, target: str, edge_id: str | None = None) -> dict[str, P] | None:
        """Get edge data/properties, typed as dict[str, P]."""
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

    def to_native(self) -> Any:
        """Convert to native Python object."""
        ...

    def copy(self) -> IEdge[P]:
        """Create a deep copy."""
        ...
