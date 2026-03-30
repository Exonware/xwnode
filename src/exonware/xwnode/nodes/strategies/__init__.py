"""
Node Strategies Package
This package contains all node strategy implementations organized by type:
- Linear strategies (arrays, lists, stacks, queues)
- Tree strategies (tries, heaps, BSTs)
- Graph strategies (union-find, neural graphs)
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.18
Generation Date: January 2, 2025
"""

from .base import ANodeStrategy, ANodeLinearStrategy, ANodeTreeStrategy, ANodeGraphStrategy
# Linear strategies
from .array_list import ArrayListStrategy
from .linked_list import LinkedListStrategy
# Tree strategies
from .trie import TrieStrategy
from .heap import HeapStrategy
from .aho_corasick import AhoCorasickStrategy
from .ast import ASTStrategy
# Graph strategies
from .hash_map import HashMapStrategy
from .union_find import UnionFindStrategy
# Advanced specialized strategies
from .veb_tree import VebTreeStrategy
from .dawg import DawgStrategy
from .hopscotch_hash import HopscotchHashStrategy
from .interval_tree import IntervalTreeStrategy
from .kd_tree import KdTreeStrategy
from .rope import RopeStrategy
from .crdt_map import CRDTMapStrategy
from .bloomier_filter import BloomierFilterStrategy
# Query optimization strategies (NEW - v0.0.1.28)
from .lru_cache import LRUCacheStrategy
from .histogram import HistogramStrategy
from .t_digest import TDigestStrategy
from .range_map import RangeMapStrategy
from .circular_buffer import CircularBufferStrategy
__all__ = [
    # Base classes
    'ANodeStrategy',
    'ANodeLinearStrategy', 
    'ANodeTreeStrategy',
    'ANodeGraphStrategy',
    # Linear strategies
    'ArrayListStrategy',
    'LinkedListStrategy',
    # Tree strategies
    'TrieStrategy',
    'HeapStrategy',
    'AhoCorasickStrategy',
    'ASTStrategy',
    # Graph strategies
    'HashMapStrategy',
    'UnionFindStrategy',
    # Advanced specialized strategies
    'VebTreeStrategy',
    'DawgStrategy',
    'HopscotchHashStrategy',
    'IntervalTreeStrategy',
    'KdTreeStrategy',
    'RopeStrategy',
    'CRDTMapStrategy',
    'BloomierFilterStrategy',
    # Query optimization strategies (NEW - v0.0.1.28)
    'LRUCacheStrategy',
    'HistogramStrategy',
    'TDigestStrategy',
    'RangeMapStrategy',
    'CircularBufferStrategy',
]
