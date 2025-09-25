"""
Strategy System for xNode

This package implements the strategy system, providing:
- 28 Node Modes (comprehensive data structure coverage)
- 16 Edge Modes (complete graph support)
- 12 Traits (cross-cutting capabilities)
- Lazy materialization and AUTO mode selection
- Strategy registry and advisor system
- 100% backward compatibility with existing xNode
"""

from .types import (
    NodeMode, EdgeMode, NodeTrait, EdgeTrait,
    AUTO, LEGACY, HASH_MAP, ORDERED_MAP, ORDERED_MAP_BALANCED,
    ARRAY_LIST, LINKED_LIST, TRIE, RADIX_TRIE, PATRICIA,
    HEAP, SET_HASH, SET_TREE, BLOOM_FILTER, CUCKOO_HASH,
    BITMAP, BITSET_DYNAMIC, ROARING_BITMAP, B_TREE, B_PLUS_TREE,
    LSM_TREE, PERSISTENT_TREE, COW_TREE, UNION_FIND, SEGMENT_TREE, FENWICK_TREE,
    SUFFIX_ARRAY, AHO_CORASICK, COUNT_MIN_SKETCH, HYPERLOGLOG,
    ADJ_LIST, DYNAMIC_ADJ_LIST, ADJ_MATRIX, BLOCK_ADJ_MATRIX,
    CSR, CSC, COO, BIDIR_WRAPPER, TEMPORAL_EDGESET,
    HYPEREDGE_SET, EDGE_PROPERTY_STORE, R_TREE, QUADTREE, OCTREE
)

from .registry import StrategyRegistry, get_registry, register_node_strategy, register_edge_strategy
from .advisor import StrategyAdvisor, get_advisor
from .manager import StrategyManager

__all__ = [
    # Types and Enums
    'NodeMode', 'EdgeMode', 'NodeTrait', 'EdgeTrait',
    
    # Node Modes
    'AUTO', 'LEGACY', 'HASH_MAP', 'ORDERED_MAP', 'ORDERED_MAP_BALANCED',
    'ARRAY_LIST', 'LINKED_LIST', 'TRIE', 'RADIX_TRIE', 'PATRICIA',
    'HEAP', 'SET_HASH', 'SET_TREE', 'BLOOM_FILTER', 'CUCKOO_HASH',
    'BITMAP', 'BITSET_DYNAMIC', 'ROARING_BITMAP', 'B_TREE', 'B_PLUS_TREE',
    'LSM_TREE', 'PERSISTENT_TREE', 'COW_TREE', 'UNION_FIND', 'SEGMENT_TREE', 'FENWICK_TREE',
    'SUFFIX_ARRAY', 'AHO_CORASICK', 'COUNT_MIN_SKETCH', 'HYPERLOGLOG',
    
    # Edge Modes
    'ADJ_LIST', 'DYNAMIC_ADJ_LIST', 'ADJ_MATRIX', 'BLOCK_ADJ_MATRIX',
    'CSR', 'CSC', 'COO', 'BIDIR_WRAPPER', 'TEMPORAL_EDGESET',
    'HYPEREDGE_SET', 'EDGE_PROPERTY_STORE', 'R_TREE', 'QUADTREE', 'OCTREE',
    
    # Core Components
    'StrategyRegistry', 'StrategyAdvisor', 'StrategyManager',
    'get_registry', 'get_advisor', 'register_node_strategy', 'register_edge_strategy',
]
