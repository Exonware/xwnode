#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/ordered_map.py
Ordered Map Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
"""
Ordered Map Node Strategy Implementation
This module implements the ORDERED_MAP strategy for sorted key-value
operations with efficient range queries and ordered iteration.
"""
from typing import Any, Iterator, Optional, AsyncIterator
import bisect
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class OrderedMapStrategy(ANodeTreeStrategy):
    """
    Ordered Map node strategy for sorted key-value operations.
    Maintains keys in sorted order for efficient range queries,
    ordered iteration, and logarithmic search operations.
    Performance Optimization:
    - Added IS_FAST_PATH flag to enable fast-path optimization in facade
    - Fast path bypasses expensive path navigation for simple key-value operations
    - Expected improvement: Get operation could improve from 0.0036 ms → ~0.0017 ms (2x faster)
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
    # Enable fast-path optimization for simple key-value operations
    IS_FAST_PATH = True

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the Ordered Map strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.ORDERED_MAP, traits, **options)
        self.case_sensitive = options.get('case_sensitive', True)
        self.allow_duplicates = options.get('allow_duplicates', False)
        # Core storage: parallel sorted arrays
        self._keys: list[str] = []
        self._values: list[Any] = []
        self._size = 0

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the ordered map strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)

    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()

    def _find_key_position(self, key: str) -> int:
        """Find position where key should be inserted (or exists)."""
        normalized_key = self._normalize_key(key)
        return bisect.bisect_left(self._keys, normalized_key)

    def _insert_at_position(self, position: int, key: str, value: Any) -> None:
        """Insert key-value pair at specific position."""
        normalized_key = self._normalize_key(key)
        self._keys.insert(position, normalized_key)
        self._values.insert(position, value)
        self._size += 1

    def _remove_at_position(self, position: int) -> Any:
        """Remove key-value pair at specific position."""
        if 0 <= position < self._size:
            self._keys.pop(position)
            value = self._values.pop(position)
            self._size -= 1
            return value
        return None
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """Add/update key-value pair in sorted order."""
        key_str = str(key)
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        # Check if key already exists
        if (position < self._size and 
            self._keys[position] == normalized_key):
            if not self.allow_duplicates:
                # Update existing key
                self._values[position] = value
                return
        # Insert new key-value pair
        self._insert_at_position(position, key_str, value)

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        if key_str == "sorted_keys":
            return self._keys.copy()
        elif key_str == "sorted_values":
            return self._values.copy()
        elif key_str == "map_info":
            return {
                'size': self._size,
                'case_sensitive': self.case_sensitive,
                'allow_duplicates': self.allow_duplicates,
                'first_key': self.first_key(),
                'last_key': self.last_key()
            }
        elif key_str.isdigit():
            # Numeric access by index
            index = int(key_str)
            if 0 <= index < self._size:
                return self._values[index]
            return default
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        if (position < self._size and 
            self._keys[position] == normalized_key):
            return self._values[position]
        return default

    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        if key_str in ["sorted_keys", "sorted_values", "map_info"]:
            return True
        elif key_str.isdigit():
            index = int(key_str)
            return 0 <= index < self._size
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        return (position < self._size and 
                self._keys[position] == normalized_key)

    def remove(self, key: Any) -> bool:
        """Remove key from map."""
        key_str = str(key)
        if key_str.isdigit():
            # Remove by index
            index = int(key_str)
            if 0 <= index < self._size:
                self._remove_at_position(index)
                return True
            return False
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        if (position < self._size and 
            self._keys[position] == normalized_key):
            self._remove_at_position(position)
            return True
        return False

    def delete(self, key: Any) -> bool:
        """Remove key from map (alias for remove)."""
        return self.remove(key)

    def clear(self) -> None:
        """Clear all data."""
        self._keys.clear()
        self._values.clear()
        self._size = 0

    def keys(self) -> Iterator[str]:
        """Get all keys in sorted order."""
        for key in self._keys:
            yield key

    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        for value in self._values:
            yield value

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        for key, value in zip(self._keys, self._values):
            yield (key, value)

    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self._size

    def to_native(self) -> dict[str, Any]:
        """Convert to native Python dict (preserves insertion order in Python 3.7+)."""
        return dict(zip(self._keys, self._values))
    # ============================================================================
    # ASYNC API - Lightweight wrappers (NO lock overhead, v0.0.1.28b)
    # ============================================================================

    async def insert_async(self, key: Any, value: Any) -> None:
        """Lightweight async wrapper for insert (no lock overhead)."""
        return self.insert(key, value)

    async def find_async(self, key: Any) -> Optional[Any]:
        """Lightweight async wrapper for find (no lock overhead)."""
        return self.find(key)

    async def delete_async(self, key: Any) -> bool:
        """Lightweight async wrapper for delete (no lock overhead)."""
        return self.delete(key)

    async def size_async(self) -> int:
        """Lightweight async wrapper for size (no lock overhead)."""
        return self.size()

    async def is_empty_async(self) -> bool:
        """Lightweight async wrapper for is_empty (no lock overhead)."""
        return self.is_empty()

    async def to_native_async(self) -> Any:
        """Lightweight async wrapper for to_native (no lock overhead)."""
        return self.to_native()

    async def keys_async(self) -> AsyncIterator[Any]:
        """Lightweight async wrapper for keys (no lock overhead)."""
        for key in self.keys():
            yield key

    async def values_async(self) -> AsyncIterator[Any]:
        """Lightweight async wrapper for values (no lock overhead)."""
        for value in self.values():
            yield value

    async def items_async(self) -> AsyncIterator[tuple[Any, Any]]:
        """Lightweight async wrapper for items (no lock overhead)."""
        for item in self.items():
            yield item
    @property

    def is_list(self) -> bool:
        """This can behave like a list for indexed access."""
        return True
    @property

    def is_dict(self) -> bool:
        """This is a dict-like structure."""
        return True
    # ============================================================================
    # ORDERED MAP SPECIFIC OPERATIONS
    # ============================================================================

    def first_key(self) -> Optional[str]:
        """Get first (smallest) key."""
        return self._keys[0] if self._size > 0 else None

    def last_key(self) -> Optional[str]:
        """Get last (largest) key."""
        return self._keys[-1] if self._size > 0 else None

    def first_value(self) -> Any:
        """Get value of first key."""
        return self._values[0] if self._size > 0 else None

    def last_value(self) -> Any:
        """Get value of last key."""
        return self._values[-1] if self._size > 0 else None

    def get_range(self, start_key: str, end_key: str, inclusive: bool = True) -> list[tuple[str, Any]]:
        """Get key-value pairs in range [start_key, end_key]."""
        start_norm = self._normalize_key(start_key)
        end_norm = self._normalize_key(end_key)
        result = []
        for key, value in zip(self._keys, self._values):
            if inclusive:
                if start_norm <= key <= end_norm:
                    result.append((key, value))
            else:
                if start_norm < key < end_norm:
                    result.append((key, value))
        return result

    def get_keys_range(self, start_key: str, end_key: str, inclusive: bool = True) -> list[str]:
        """Get keys in range."""
        range_items = self.get_range(start_key, end_key, inclusive)
        return [key for key, _ in range_items]

    def get_values_range(self, start_key: str, end_key: str, inclusive: bool = True) -> list[Any]:
        """Get values in key range."""
        range_items = self.get_range(start_key, end_key, inclusive)
        return [value for _, value in range_items]

    def lower_bound(self, key: str) -> Optional[str]:
        """Find first key >= given key."""
        normalized_key = self._normalize_key(key)
        position = bisect.bisect_left(self._keys, normalized_key)
        return self._keys[position] if position < self._size else None

    def upper_bound(self, key: str) -> Optional[str]:
        """Find first key > given key."""
        normalized_key = self._normalize_key(key)
        position = bisect.bisect_right(self._keys, normalized_key)
        return self._keys[position] if position < self._size else None

    def floor(self, key: str) -> Optional[str]:
        """Find largest key <= given key."""
        normalized_key = self._normalize_key(key)
        position = bisect.bisect_right(self._keys, normalized_key) - 1
        return self._keys[position] if position >= 0 else None

    def ceiling(self, key: str) -> Optional[str]:
        """Find smallest key >= given key."""
        return self.lower_bound(key)

    def get_at_index(self, index: int) -> Optional[tuple[str, Any]]:
        """Get key-value pair at specific index."""
        if 0 <= index < self._size:
            return (self._keys[index], self._values[index])
        return None

    def index_of(self, key: str) -> int:
        """Get index of key (-1 if not found)."""
        normalized_key = self._normalize_key(key)
        position = self._find_key_position(key)
        if (position < self._size and 
            self._keys[position] == normalized_key):
            return position
        return -1

    def pop_first(self) -> Optional[tuple[str, Any]]:
        """Remove and return first key-value pair."""
        if self._size > 0:
            key = self._keys[0]
            value = self._remove_at_position(0)
            return (key, value)
        return None

    def pop_last(self) -> Optional[tuple[str, Any]]:
        """Remove and return last key-value pair."""
        if self._size > 0:
            key = self._keys[-1]
            value = self._remove_at_position(self._size - 1)
            return (key, value)
        return None

    def reverse_keys(self) -> Iterator[str]:
        """Get keys in reverse order."""
        for i in range(self._size - 1, -1, -1):
            yield self._keys[i]

    def reverse_values(self) -> Iterator[Any]:
        """Get values in reverse key order."""
        for i in range(self._size - 1, -1, -1):
            yield self._values[i]

    def reverse_items(self) -> Iterator[tuple[str, Any]]:
        """Get key-value pairs in reverse order."""
        for i in range(self._size - 1, -1, -1):
            yield (self._keys[i], self._values[i])

    def find_prefix_keys(self, prefix: str) -> list[str]:
        """Find all keys starting with given prefix."""
        normalized_prefix = self._normalize_key(prefix)
        result = []
        for key in self._keys:
            if key.startswith(normalized_prefix):
                result.append(key)
            elif key > normalized_prefix and not key.startswith(normalized_prefix):
                break  # Keys are sorted, no more matches possible
        return result

    def count_range(self, start_key: str, end_key: str, inclusive: bool = True) -> int:
        """Count keys in range."""
        return len(self.get_keys_range(start_key, end_key, inclusive))

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive ordered map statistics."""
        if self._size == 0:
            return {'size': 0, 'first_key': None, 'last_key': None}
        # Calculate key length statistics
        key_lengths = [len(key) for key in self._keys]
        avg_key_length = sum(key_lengths) / len(key_lengths)
        min_key_length = min(key_lengths)
        max_key_length = max(key_lengths)
        return {
            'size': self._size,
            'first_key': self.first_key(),
            'last_key': self.last_key(),
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates,
            'avg_key_length': avg_key_length,
            'min_key_length': min_key_length,
            'max_key_length': max_key_length,
            'memory_usage': self._size * 50  # Estimated
        }
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ORDERED_MAP',
            'backend': 'Parallel sorted arrays with binary search',
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates,
            'complexity': {
                'put': 'O(n)',  # Due to array insertion
                'get': 'O(log n)',  # Binary search
                'remove': 'O(n)',  # Due to array removal
                'range_query': 'O(log n + k)',  # k = result size
                'iteration': 'O(n)',
                'space': 'O(n)'
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        return {
            'size': stats['size'],
            'first_key': str(stats['first_key']) if stats['first_key'] else 'None',
            'last_key': str(stats['last_key']) if stats['last_key'] else 'None',
            'avg_key_length': f"{stats['avg_key_length']:.1f}" if stats.get('avg_key_length') else '0',
            'case_sensitive': stats['case_sensitive'],
            'memory_usage': f"{stats['memory_usage']} bytes (estimated)"
        }
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeTreeStrategy)
    # ============================================================================

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """
        Traverse keys in specified order.
        For OrderedMap, inorder/preorder/postorder all return keys in sorted order
        since keys are maintained in sorted order.
        """
        return list(self._keys) if self._size > 0 else []

    def get_min(self) -> Any:
        """Get minimum key (first/smallest key)."""
        return self.first_key()

    def get_max(self) -> Any:
        """Get maximum key (last/largest key)."""
        return self.last_key()
    # ============================================================================
    # BEHAVIORAL VIEWS (from ANodeTreeStrategy and ANodeGraphStrategy)
    # ============================================================================

    def as_trie(self):
        """Provide Trie behavioral view."""
        raise NotImplementedError(
            "OrderedMap cannot behave as Trie - use TrieStrategy or RadixTrieStrategy for prefix matching"
        )

    def as_heap(self):
        """Provide Heap behavioral view."""
        raise NotImplementedError(
            "OrderedMap cannot behave as Heap - use HeapStrategy for priority-based operations"
        )

    def as_skip_list(self):
        """Provide SkipList behavioral view."""
        raise NotImplementedError(
            "OrderedMap cannot behave as SkipList - use SkipListStrategy for probabilistic sorted operations"
        )
    # Graph methods (from ANodeGraphStrategy)

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Add edge between nodes (not applicable for OrderedMap)."""
        raise NotImplementedError(
            "OrderedMap does not support graph edges - use graph strategies for edge operations"
        )

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes (not applicable for OrderedMap)."""
        raise NotImplementedError(
            "OrderedMap does not support graph edges"
        )

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists (not applicable for OrderedMap)."""
        raise NotImplementedError(
            "OrderedMap does not support graph edges"
        )

    def find_path(self, start: Any, end: Any) -> list[Any]:
        """Find path between nodes (not applicable for OrderedMap)."""
        raise NotImplementedError(
            "OrderedMap does not support graph paths"
        )

    def get_neighbors(self, node: Any) -> list[Any]:
        """Get neighboring nodes (not applicable for OrderedMap)."""
        raise NotImplementedError(
            "OrderedMap does not support graph neighbors"
        )

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight (not applicable for OrderedMap)."""
        raise NotImplementedError(
            "OrderedMap does not support graph edges"
        )

    def as_union_find(self):
        """Provide Union-Find behavioral view."""
        raise NotImplementedError(
            "OrderedMap cannot behave as Union-Find - use UnionFindStrategy for connectivity operations"
        )

    def as_neural_graph(self):
        """Provide Neural Graph behavioral view."""
        raise NotImplementedError(
            "OrderedMap cannot behave as Neural Graph - use graph strategies for neural operations"
        )

    def as_flow_network(self):
        """Provide Flow Network behavioral view."""
        raise NotImplementedError(
            "OrderedMap cannot behave as Flow Network - use graph strategies for flow operations"
        )
