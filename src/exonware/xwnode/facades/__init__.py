"""
Specialized Facades Package
This package provides type-safe, specialized facade classes for common
data structure patterns: graphs, trees, and linear structures.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
Generation Date: 22-Oct-2025
"""

from typing import Any
from ..defs import NodeMode, EdgeMode
# ============================================================================
# MODE CONSTANTS FOR CONVENIENCE
# ============================================================================
# Tree mode constants - suitable for tree data structures
TREE_MODES: list[NodeMode] = [
    NodeMode.TRIE,
    NodeMode.RADIX_TRIE,
    NodeMode.PATRICIA,
    NodeMode.B_TREE,
    NodeMode.B_PLUS_TREE,
    NodeMode.AVL_TREE,
    NodeMode.RED_BLACK_TREE,
    NodeMode.TREAP,
    NodeMode.SPLAY_TREE,
    NodeMode.PERSISTENT_TREE,
    NodeMode.COW_TREE,
    NodeMode.ART,
    NodeMode.HAMT,
    NodeMode.MASSTREE,
    NodeMode.INTERVAL_TREE,
    NodeMode.KD_TREE,
    NodeMode.VEB_TREE,
    NodeMode.DAWG,
]
# Graph mode constants - suitable for graph data structures
GRAPH_MODES: list[NodeMode] = [
    NodeMode.ADJACENCY_LIST,
    NodeMode.UNION_FIND,
    NodeMode.TREE_GRAPH_HYBRID,
]
# Graph edge mode constants
GRAPH_EDGE_MODES: list[EdgeMode] = [
    EdgeMode.ADJ_LIST,
    EdgeMode.DYNAMIC_ADJ_LIST,
    EdgeMode.ADJ_MATRIX,
    EdgeMode.BLOCK_ADJ_MATRIX,
    EdgeMode.CSR,
    EdgeMode.CSC,
    EdgeMode.COO,
    EdgeMode.WEIGHTED_GRAPH,
    EdgeMode.BIDIR_WRAPPER,
    EdgeMode.EDGE_PROPERTY_STORE,
    EdgeMode.TREE_GRAPH_BASIC,
]
# Linear mode constants - suitable for queue, stack, deque
LINEAR_MODES: list[NodeMode] = [
    NodeMode.QUEUE,
    NodeMode.STACK,
    NodeMode.DEQUE,
    NodeMode.PRIORITY_QUEUE,
    NodeMode.CIRCULAR_BUFFER,
]
# Export all facade classes
from .graph import XWNodeGraph
from .tree import XWTree
from .linear import XWQueue, XWStack, XWDeque
__all__ = [
    # Mode constants
    'TREE_MODES',
    'GRAPH_MODES',
    'GRAPH_EDGE_MODES',
    'LINEAR_MODES',
    # Facade classes
    'XWNodeGraph',
    'XWTree',
    'XWQueue',
    'XWStack',
    'XWDeque',
]
