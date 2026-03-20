"""
Tree Facade - XWTree[NT, ET]
Specialized facade for tree data structures with optional edge properties
and type-safe generic parameters.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
Generation Date: 22-Oct-2025
"""

from __future__ import annotations
import logging
from typing import Any, TypeVar
from ..facade import XWNode
from ..common.graph.manager import XWGraphManager
from ..defs import NodeMode, EdgeMode
from . import TREE_MODES
logger = logging.getLogger(__name__)
# Type variables for tree facade
NT = TypeVar('NT')  # Node type - the type of data stored in nodes
ET = TypeVar('ET')  # Edge type - the type of edge properties (optional for trees)


class XWTree[NT, ET](XWNode[dict[str, NT]]):
    """
    Specialized facade for tree data structures with generic type parameters.
    Generic type parameters:
        NT: The type of data stored in nodes (Node Type)
        ET: The type of values in edge property dictionaries (Edge Type) - optional
    Trees are acyclic connected graphs, so this facade extends XWNode with
    tree-specific operations while maintaining the flexibility to add edge
    properties for tree edges (parent-child relationships).
    Example:
        >>> from exonware.xwnode.facades import XWTree
        >>> 
        >>> # Create a tree with typed nodes
        >>> tree: XWTree[str, Any] = XWTree(mode='TRIE')
        >>> 
        >>> # Add nodes
        >>> tree.add_node('root', data='Root Node')
        >>> tree.add_node('child1', data='Child 1')
        >>> 
        >>> # Add parent-child relationship
        >>> tree.add_edge('root', 'child1', edge_type='child')
        >>> 
        >>> # Traverse tree
        >>> children = tree.get_children('root')
    """

    def __init__(
        self,
        data: dict[str, NT] | None = None,
        mode: NodeMode | str = NodeMode.TREE_GRAPH_HYBRID,
        edge_mode: EdgeMode | str = EdgeMode.TREE_GRAPH_BASIC,
        immutable: bool = False,
        enable_caching: bool = True,
        enable_indexing: bool = True,
        **options
    ):
        """
        Initialize XWTree with node and optional edge configuration.
        Args:
            data: Initial tree data dictionary mapping node IDs to node values of type NT
            mode: Tree node storage strategy (default: TREE_GRAPH_HYBRID)
            edge_mode: Edge storage strategy for parent-child relationships (default: TREE_GRAPH_BASIC)
            immutable: If True, enable COW semantics
            enable_caching: Enable LRU query cache for tree operations
            enable_indexing: Enable multi-index for O(1) edge lookups
            **options: Additional configuration options
        """
        # Initialize node storage
        if isinstance(mode, str):
            mode = NodeMode[mode]
        # Initialize the underlying XWNode for tree node storage
        tree_data = data or {}
        super().__init__(data=tree_data, mode=mode, immutable=immutable, **options)
        # Initialize graph manager for parent-child edge operations (optional)
        if isinstance(edge_mode, str):
            edge_mode = EdgeMode[edge_mode]
        self._graph_manager = XWGraphManager(
            edge_mode=edge_mode,
            enable_caching=enable_caching,
            enable_indexing=enable_indexing,
            **options
        )
        self._tree_mode = mode
        self._edge_mode = edge_mode
    # ============================================================================
    # TREE NODE OPERATIONS (delegated to XWNode)
    # ============================================================================

    def add_node(self, node_id: str, data: NT, **options) -> None:
        """
        Add a node to the tree with typed data.
        Args:
            node_id: Unique identifier for the node
            data: Node data of type NT
            **options: Additional node configuration options
        """
        self.put(node_id, data)

    def get_node(self, node_id: str) -> NT | None:
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
        Remove a node from the tree and all its parent-child relationships.
        Args:
            node_id: Node identifier
        Returns:
            True if removed, False if not found
        """
        # Remove all parent-child relationships
        children = self.get_children(node_id)
        for child_id in children:
            self._graph_manager.remove_relationship(node_id, child_id)
        parent = self.get_parent(node_id)
        if parent:
            self._graph_manager.remove_relationship(parent, node_id)
        # Remove the node itself
        return self.delete(node_id) is not None
    # ============================================================================
    # TREE-SPECIFIC EDGE OPERATIONS (parent-child relationships)
    # ============================================================================

    def add_edge(
        self,
        parent: str,
        child: str,
        edge_type: str = "child",
        properties: dict[str, ET] | None = None,
        **options
    ) -> str:
        """
        Add a parent-child edge with typed properties.
        Args:
            parent: Parent node ID
            child: Child node ID
            edge_type: Type of relationship (default: "child")
            properties: Edge properties dictionary with values of type ET
            **options: Additional edge configuration
        Returns:
            Edge/relationship ID
        """
        props_dict = properties or {}
        return self._graph_manager.add_relationship(
            parent, child, edge_type, **props_dict
        )

    def remove_edge(self, parent: str, child: str) -> bool:
        """
        Remove a parent-child edge.
        Args:
            parent: Parent node ID
            child: Child node ID
        Returns:
            True if removed, False if not found
        """
        return self._graph_manager.remove_relationship(parent, child, 'child')

    def get_parent(self, node_id: str) -> str | None:
        """
        Get the parent node ID.
        Args:
            node_id: Node identifier
        Returns:
            Parent node ID, or None if root node
        """
        incoming = self._graph_manager.get_incoming(node_id, 'child')
        if incoming:
            return incoming[0].get('source')  # type: ignore[return-value]
        return None

    def get_children(
        self,
        node_id: str,
        edge_type: str = 'child',
        limit: int | None = None
    ) -> list[str]:
        """
        Get child node IDs.
        Args:
            node_id: Parent node identifier
            edge_type: Edge type filter (default: 'child')
            limit: Optional result limit
        Returns:
            List of child node IDs
        """
        outgoing = self._graph_manager.get_outgoing(node_id, edge_type, limit)
        return [rel.get('target') for rel in outgoing if rel.get('target')]  # type: ignore[misc,return-value]

    def get_siblings(self, node_id: str) -> list[str]:
        """
        Get sibling node IDs (nodes with the same parent).
        Args:
            node_id: Node identifier
        Returns:
            List of sibling node IDs
        """
        parent = self.get_parent(node_id)
        if not parent:
            return []
        siblings = self.get_children(parent)
        return [sib for sib in siblings if sib != node_id]

    def is_root(self, node_id: str) -> bool:
        """
        Check if node is the root (has no parent).
        Args:
            node_id: Node identifier
        Returns:
            True if root, False otherwise
        """
        return self.get_parent(node_id) is None

    def is_leaf(self, node_id: str) -> bool:
        """
        Check if node is a leaf (has no children).
        Args:
            node_id: Node identifier
        Returns:
            True if leaf, False otherwise
        """
        return len(self.get_children(node_id)) == 0

    def get_depth(self, node_id: str) -> int:
        """
        Get the depth of a node in the tree (distance from root).
        Args:
            node_id: Node identifier
        Returns:
            Depth of the node (0 for root)
        """
        depth = 0
        current = node_id
        while True:
            parent = self.get_parent(current)
            if parent is None:
                break
            depth += 1
            current = parent
        return depth

    def get_path_to_root(self, node_id: str) -> list[str]:
        """
        Get the path from node to root.
        Args:
            node_id: Node identifier
        Returns:
            List of node IDs from node to root (inclusive)
        """
        path = [node_id]
        current = node_id
        while True:
            parent = self.get_parent(current)
            if parent is None:
                break
            path.append(parent)
            current = parent
        return path

    def traverse(
        self,
        start_node: str | None = None,
        order: str = 'preorder'
    ) -> list[str]:
        """
        Traverse the tree in specified order.
        Args:
            start_node: Starting node (default: root)
            order: Traversal order ('preorder', 'postorder', 'level')
        Returns:
            List of node IDs in traversal order
        """
        if start_node is None:
            # Find root node
            all_nodes = list(self.to_native().keys())
            roots = [node_id for node_id in all_nodes if self.is_root(node_id)]
            if not roots:
                return []
            start_node = roots[0]
        result = []
        if order == 'preorder':
            result.append(start_node)
            for child in self.get_children(start_node):
                result.extend(self.traverse(child, order))
        elif order == 'postorder':
            for child in self.get_children(start_node):
                result.extend(self.traverse(child, order))
            result.append(start_node)
        elif order == 'level':
            # Level-order (BFS)
            queue = [start_node]
            while queue:
                node = queue.pop(0)
                result.append(node)
                queue.extend(self.get_children(node))
        return result
    # ============================================================================
    # FACTORY METHODS
    # ============================================================================
    @classmethod

    def from_native(
        cls,
        nodes: dict[str, NT],
        edges: list[tuple[str, str, dict[str, ET] | None]] | None = None,
        mode: NodeMode | str = NodeMode.TREE_GRAPH_HYBRID,
        **options
    ) -> XWTree[NT, ET]:
        """
        Create XWTree from native Python data.
        Args:
            nodes: Dictionary mapping node IDs to node data of type NT
            edges: Optional list of parent-child edge tuples (parent, child, properties)
            mode: Tree storage strategy
            **options: Additional configuration options
        Returns:
            XWTree[NT, ET] instance
        """
        tree = cls(data=nodes, mode=mode, **options)
        # Add parent-child edges if provided
        if edges:
            for edge in edges:
                parent, child, properties = edge
                tree.add_edge(parent, child, properties=properties)
        return tree
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def to_native(self) -> dict[str, Any]:
        """
        Convert tree to native Python representation.
        Returns:
            Dictionary with 'nodes' and 'edges' keys
        """
        nodes = super().to_native()
        # Collect all parent-child edges
        edges = []
        for node_id in nodes.keys():
            children = self.get_children(node_id)
            for child_id in children:
                edge_data = self._graph_manager.get_outgoing(node_id, 'child')
                props = {}
                for rel in edge_data:
                    if rel.get('target') == child_id:
                        props = {k: v for k, v in rel.items() 
                               if k not in ('source', 'target', 'relationship_type')}
                        break
                edges.append({
                    'parent': node_id,
                    'child': child_id,
                    'properties': props
                })
        return {
            'nodes': nodes,
            'edges': edges
        }
