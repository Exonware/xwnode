"""
Graph Facade - XWNodeGraph[NT, ET]
Specialized facade for graph data structures combining node and edge operations
with type-safe generic parameters.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
Generation Date: 22-Oct-2025
"""

from __future__ import annotations
import logging
from typing import Any, Optional, TypeVar
from ..facade import XWNode
from ..base import ANode
from ..common.graph.manager import XWGraphManager
from ..defs import NodeMode, EdgeMode
from . import GRAPH_MODES, GRAPH_EDGE_MODES
logger = logging.getLogger(__name__)
# Type variables for graph facade
NT = TypeVar('NT')  # Node type - the type of data stored in nodes
ET = TypeVar('ET')  # Edge type - the type of edge properties/dictionary values


class XWNodeGraph[NT, ET](XWNode[dict[str, NT]]):
    """
    Specialized facade for graph data structures with generic type parameters.
    Generic type parameters:
        NT: The type of data stored in nodes (Node Type)
        ET: The type of values in edge property dictionaries (Edge Type)
    This facade combines node operations (from XWNode) with graph-specific
    edge operations (via XWGraphManager) to provide a unified, type-safe API
    for working with graphs.
    Example:
        >>> from exonware.xwnode.facades import XWNodeGraph
        >>> 
        >>> # Create a graph with typed nodes and edges
        >>> graph: XWNodeGraph[str, float] = XWNodeGraph()
        >>> 
        >>> # Add nodes with string data
        >>> graph.add_node('alice', data='Alice Smith')
        >>> graph.add_node('bob', data='Bob Jones')
        >>> 
        >>> # Add edges with float weights
        >>> graph.add_edge('alice', 'bob', edge_type='follows', weight=1.5)
        >>> 
        >>> # Get neighbors
        >>> neighbors = graph.get_outgoing('alice', 'follows')
    """

    def __init__(
        self,
        data: Optional[dict[str, NT]] = None,
        node_mode: NodeMode | str = NodeMode.ADJACENCY_LIST,
        edge_mode: EdgeMode | str = EdgeMode.ADJ_LIST,
        immutable: bool = False,
        enable_caching: bool = True,
        enable_indexing: bool = True,
        isolation_key: Optional[str] = None,
        **options
    ):
        """
        Initialize XWNodeGraph with node and edge configuration.
        Args:
            data: Initial node data dictionary mapping node IDs to node values of type NT
            node_mode: Node storage strategy (default: ADJACENCY_LIST)
            edge_mode: Edge storage strategy (default: ADJ_LIST)
            immutable: If True, enable COW semantics
            enable_caching: Enable LRU query cache for graph operations
            enable_indexing: Enable multi-index for O(1) edge lookups
            isolation_key: Optional tenant/context ID for isolation
            **options: Additional configuration options
        """
        # Initialize node storage
        if isinstance(node_mode, str):
            node_mode = NodeMode[node_mode]
        # Initialize the underlying XWNode for node storage
        node_data = data or {}
        super().__init__(data=node_data, mode=node_mode, immutable=immutable, **options)
        # Initialize graph manager for edge operations
        if isinstance(edge_mode, str):
            edge_mode = EdgeMode[edge_mode]
        self._graph_manager = XWGraphManager(
            edge_mode=edge_mode,
            enable_caching=enable_caching,
            enable_indexing=enable_indexing,
            isolation_key=isolation_key,
            **options
        )
        self._node_mode = node_mode
        self._edge_mode = edge_mode
    # ============================================================================
    # NODE OPERATIONS (delegated to XWNode)
    # ============================================================================

    def add_node(self, node_id: str, data: NT, **options) -> None:
        """
        Add a node to the graph with typed data.
        Args:
            node_id: Unique identifier for the node
            data: Node data of type NT
            **options: Additional node configuration options
        """
        self.put(node_id, data)

    def get_node(self, node_id: str) -> Optional[NT]:
        """
        Get node data by ID.
        Args:
            node_id: Node identifier
        Returns:
            Node data of type NT, or None if not found
        """
        node = self.get(node_id)
        return node.value if node else None  # type: ignore[return-value]

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node and all its edges from the graph.
        Args:
            node_id: Node identifier
        Returns:
            True if removed, False if not found
        """
        # Remove all outgoing relationships
        outgoing = self._graph_manager.get_outgoing(node_id)
        for rel in outgoing:
            self._graph_manager.remove_relationship(node_id, rel.get('target'))
        # Remove all incoming relationships
        incoming = self._graph_manager.get_incoming(node_id)
        for rel in incoming:
            self._graph_manager.remove_relationship(rel.get('source'), node_id)
        # Remove the node itself
        return self.delete(node_id) is not None
    # ============================================================================
    # EDGE OPERATIONS (delegated to XWGraphManager)
    # ============================================================================

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str = "default",
        weight: float = 1.0,
        properties: Optional[dict[str, ET]] = None,
        **options
    ) -> str:
        """
        Add an edge between nodes with typed properties.
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Type of edge/relationship
            weight: Edge weight (default: 1.0)
            properties: Edge properties dictionary with values of type ET
            **options: Additional edge configuration
        Returns:
            Edge/relationship ID
        """
        # Convert properties to dict for XWGraphManager (it expects **kwargs)
        props_dict = properties or {}
        props_dict['weight'] = weight
        return self._graph_manager.add_relationship(
            source, target, edge_type, **props_dict
        )

    def remove_edge(
        self,
        source: str,
        target: str,
        edge_type: Optional[str] = None
    ) -> bool:
        """
        Remove an edge between nodes.
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Optional edge type filter
        Returns:
            True if removed, False if not found
        """
        return self._graph_manager.remove_relationship(source, target, edge_type)

    def has_edge(
        self,
        source: str,
        target: str,
        edge_type: Optional[str] = None
    ) -> bool:
        """
        Check if an edge exists between nodes.
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Optional edge type filter
        Returns:
            True if edge exists, False otherwise
        """
        return self._graph_manager.has_relationship(source, target, edge_type)

    def get_outgoing(
        self,
        node_id: str,
        edge_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """
        Get outgoing edges/relationships from a node.
        Args:
            node_id: Node identifier
            edge_type: Optional edge type filter
            limit: Optional result limit
        Returns:
            List of relationship dictionaries with edge metadata
        """
        return self._graph_manager.get_outgoing(node_id, edge_type, limit)

    def get_incoming(
        self,
        node_id: str,
        edge_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """
        Get incoming edges/relationships to a node.
        Args:
            node_id: Node identifier
            edge_type: Optional edge type filter
            limit: Optional result limit
        Returns:
            List of relationship dictionaries with edge metadata
        """
        return self._graph_manager.get_incoming(node_id, edge_type, limit)

    def get_neighbors(
        self,
        node_id: str,
        edge_type: Optional[str] = None,
        direction: str = "both"
    ) -> list[str]:
        """
        Get neighbor node IDs.
        Args:
            node_id: Node identifier
            edge_type: Optional edge type filter
            direction: 'outgoing', 'incoming', or 'both'
        Returns:
            List of neighbor node IDs
        """
        neighbors = set()
        if direction in ('outgoing', 'both'):
            outgoing = self.get_outgoing(node_id, edge_type)
            for rel in outgoing:
                neighbors.add(rel.get('target'))
        if direction in ('incoming', 'both'):
            incoming = self.get_incoming(node_id, edge_type)
            for rel in incoming:
                neighbors.add(rel.get('source'))
        return list(neighbors)

    def get_edge_data(
        self,
        source: str,
        target: str,
        edge_type: Optional[str] = None
    ) -> Optional[dict[str, ET]]:
        """
        Get edge data/properties.
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Optional edge type filter
        Returns:
            Edge properties dictionary with values of type ET, or None if not found
        """
        outgoing = self.get_outgoing(source, edge_type)
        for rel in outgoing:
            if rel.get('target') == target:
                # Remove internal fields and return properties
                props = {k: v for k, v in rel.items() 
                        if k not in ('source', 'target', 'relationship_type')}
                return props  # type: ignore[return-value]
        return None
    # ============================================================================
    # FACTORY METHODS
    # ============================================================================
    @classmethod

    def from_native(
        cls,
        nodes: dict[str, NT],
        edges: Optional[list[tuple[str, str, str, Optional[dict[str, ET]]]]] = None,
        node_mode: NodeMode | str = NodeMode.ADJACENCY_LIST,
        edge_mode: EdgeMode | str = EdgeMode.ADJ_LIST,
        **options
    ) -> XWNodeGraph[NT, ET]:
        """
        Create XWNodeGraph from native Python data.
        Args:
            nodes: Dictionary mapping node IDs to node data of type NT
            edges: Optional list of edge tuples (source, target, edge_type, properties)
            node_mode: Node storage strategy
            edge_mode: Edge storage strategy
            **options: Additional configuration options
        Returns:
            XWNodeGraph[NT, ET] instance
        """
        graph = cls(data=nodes, node_mode=node_mode, edge_mode=edge_mode, **options)
        # Add edges if provided
        if edges:
            for edge in edges:
                source, target, edge_type, properties = edge
                graph.add_edge(source, target, edge_type, properties=properties)
        return graph
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def to_native(self) -> dict[str, Any]:
        """
        Convert graph to native Python representation.
        Returns:
            Dictionary with 'nodes' and 'edges' keys
        """
        nodes = super().to_native()
        # Collect all edges
        edges = []
        for node_id in nodes.keys():
            outgoing = self.get_outgoing(node_id)
            for rel in outgoing:
                edges.append({
                    'source': node_id,
                    'target': rel.get('target'),
                    'type': rel.get('relationship_type', 'default'),
                    'properties': {k: v for k, v in rel.items() 
                                  if k not in ('source', 'target', 'relationship_type')}
                })
        return {
            'nodes': nodes,
            'edges': edges
        }
