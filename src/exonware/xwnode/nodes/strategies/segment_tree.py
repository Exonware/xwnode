#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/segment_tree.py
Segment Tree Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.26
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Callable, Iterator
"""
Segment Tree Node Strategy Implementation
This module implements the SEGMENT_TREE strategy for range queries
and updates with O(log n) complexity.
"""
from typing import Any
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class SegmentTreeStrategy(ANodeTreeStrategy):
    """
    Segment Tree strategy for range query operations.
    WHY Segment Tree:
    - Supports arbitrary range queries (sum, min, max, GCD, etc.)
    - O(log n) queries and updates (in optimized implementation)
    - More flexible than Fenwick Tree (supports non-invertible operations)
    - Industry standard for range query problems
    - Handles both point and range updates
    WHY this implementation:
    - Simplified O(n) range query for correctness (not O(log n) tree structure)
    - Supports multiple operations (sum, min, max, etc.)
    - Combiner pattern allows pluggable operations
    - Identity elements enable proper initialization
    - Clear semantics over performance optimization
    Time Complexity (Current Simplified Implementation):
    - Update: O(1) - direct array access
    - Range Query: O(n) - scans range (simplified for correctness)
    - Note: Full O(log n) segment tree requires tree rebuild logic
    Space Complexity: O(n) - simple array storage
    Trade-offs:
    - Advantage: Supports non-invertible operations (min, max, GCD)
    - Advantage: More flexible than Fenwick Tree
    - Limitation: Current implementation is O(n) query (not O(log n))
    - Limitation: Full segment tree is more complex than Fenwick
    - Compared to Fenwick: More flexible, but current impl slower
    - Compared to naive: Same complexity, but extensible
    Best for:
    - Range queries with non-invertible operations (min, max)
    - When operation flexibility is needed
    - Competitive programming (with proper O(log n) impl)
    - When understanding segment tree concepts
    Not recommended for:
    - Prefix sums only (use Fenwick Tree - simpler)
    - When O(log n) is critical (current impl is O(n))
    - Production systems (needs full tree implementation)
    Following eXonware Priorities:
    1. Usability: Clear API for range operations
    2. Maintainability: Simplified for correctness over complexity
    3. Performance: O(1) updates, O(n) queries (acceptable for moderate n)
    4. Extensibility: Easy to swap combiner functions
    5. Security: Input validation, bounds checking
    Implementation Note:
    This is a SIMPLIFIED segment tree using O(n) range queries for CORRECTNESS.
    A full O(log n) segment tree requires proper tree structure with:
    - Recursive tree building
    - Lazy propagation for range updates
    - Complex index calculations
    For production O(log n) performance, this needs enhancement.
    Current implementation prioritizes CORRECTNESS and SIMPLICITY per
    GUIDELINES_DEV.md principle: "prefer simple, maintainable solutions."
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the Segment Tree strategy.
        Time Complexity: O(n) where n is initial_size
        Space Complexity: O(n)
        """
        super().__init__(NodeMode.SEGMENT_TREE, traits, **options)
        self._max_size = options.get('initial_size', 1000)
        self._operation = options.get('operation', 'sum')
        self._identity = self._get_identity(self._operation)
        self._combiner = self._get_combiner(self._operation)
        # Simple array to store values (0-indexed for queries)
        self._data: list[Any] = [self._identity] * self._max_size
        self._values: dict[str, Any] = {}  # Key-value storage for compatibility

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the segment tree strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.INDEXED | NodeTrait.HIERARCHICAL | NodeTrait.STREAMING)

    def _get_identity(self, operation: str) -> Any:
        """Get identity element for the operation."""
        identities = {
            'sum': 0,
            'min': float('inf'),
            'max': float('-inf'),
            'product': 1,
            'gcd': 0,
            'lcm': 1,
            'xor': 0,
            'and': True,
            'or': False
        }
        return identities.get(operation, 0)

    def _get_combiner(self, operation: str) -> Callable[[Any, Any], Any]:
        """Get combiner function for the operation."""
        import math
        combiners = {
            'sum': lambda a, b: a + b,
            'min': lambda a, b: min(a, b),
            'max': lambda a, b: max(a, b),
            'product': lambda a, b: a * b,
            'gcd': lambda a, b: math.gcd(int(a), int(b)),
            'lcm': lambda a, b: abs(int(a) * int(b)) // math.gcd(int(a), int(b)),
            'xor': lambda a, b: a ^ b,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b
        }
        return combiners.get(operation, lambda a, b: a + b)
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """Store a value at the given key."""
        key_str = str(key)
        # Try to convert to index
        try:
            idx = int(key_str)
            if 0 <= idx < self._max_size:
                self.update(idx, value)
        except (ValueError, TypeError):
            pass
        # Always store in values dict
        self._values[key_str] = value

    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        key_str = str(key)
        return self._values.get(key_str, default)

    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return str(key) in self._values

    def remove(self, key: Any) -> bool:
        """Remove value by key."""
        key_str = str(key)
        if key_str not in self._values:
            return False
        # Try to clear from array
        try:
            idx = int(key_str)
            if 0 <= idx < self._max_size:
                self._data[idx] = self._identity
        except (ValueError, TypeError):
            pass
        del self._values[key_str]
        return True

    def delete(self, key: Any) -> bool:
        """Remove value by key (alias for remove)."""
        return self.remove(key)

    def clear(self) -> None:
        """Clear all data."""
        self._data = [self._identity] * self._max_size
        self._values.clear()

    def keys(self) -> Iterator[str]:
        """Get all keys."""
        return iter(self._values.keys())

    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._values.values())

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        return iter(self._values.items())

    def __len__(self) -> int:
        """Get the number of items."""
        return len(self._values)

    def to_native(self) -> dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self._values)
    # ============================================================================
    # ASYNC API - Lightweight wrappers (NO lock overhead, v0.0.1.28b)
    # ============================================================================

    async def insert_async(self, key: Any, value: Any) -> None:
        """Lightweight async wrapper for insert (no lock overhead)."""
        return self.insert(key, value)

    async def find_async(self, key: Any) -> Any | None:
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
        """This can behave like a list."""
        return True
    @property

    def is_dict(self) -> bool:
        """This can behave like a dict."""
        return True
    # ============================================================================
    # SEGMENT TREE SPECIFIC OPERATIONS
    # ============================================================================

    def range_query(self, left: int, right: int) -> Any:
        """
        Query range [left, right] inclusive (0-indexed).
        Uses simple O(n) scan for correctness.
        For true O(log n), segment tree needs proper rebuild after updates.
        """
        if left < 0 or right >= len(self._data) or left > right:
            return self._identity
        result = self._identity
        for i in range(left, right + 1):
            result = self._combiner(result, self._data[i])
        return result

    def update(self, index: int, value: Any) -> None:
        """
        Update value at specific index (0-indexed).
        Simple O(1) update for correctness.
        """
        if index < 0 or index >= self._max_size:
            return
        # Store value
        self._data[index] = value
        # Track in values dict
        key = str(index)
        self._values[key] = value

    def range_update(self, left: int, right: int, value: Any) -> None:
        """Update range [left, right] with value."""
        for i in range(left, right + 1):
            self.update(i, value)

    def get_operation_info(self) -> dict[str, Any]:
        """Get information about the current operation."""
        return {
            'operation': self._operation,
            'identity': self._identity
        }
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'SEGMENT_TREE',
            'backend': 'Array-based segment tree',
            'operation': self._operation,
            'complexity': {
                'point_update': 'O(log n)',
                'range_query': 'O(log n)',
                'range_update': 'O(n log n)',
                'build': 'O(n)'
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        tree_height = 0
        if len(self._values) > 0:
            import math
            tree_height = math.ceil(math.log2(len(self._values)))
        return {
            'size': len(self._values),
            'tree_size': len(self._tree),
            'tree_height': tree_height,
            'operation': self._operation,
            'memory_usage': f"{len(self._tree) * 8 + len(self._values) * 24} bytes (estimated)",
            'utilization': f"{len(self._values) / max(1, len(self._tree) // 4) * 100:.1f}%"
        }

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def find_path(self, start: Any, end: Any) -> list[Any]:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph paths")

    def get_neighbors(self, node: Any) -> list[Any]:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph neighbors")

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse - returns all key-value pairs."""
        return list(self.items())

    def get_min(self) -> Any:
        """Get minimum key."""
        keys = list(self.keys())
        if not keys:
            return None
        return min(keys)

    def get_max(self) -> Any:
        """Get maximum key."""
        keys = list(self.keys())
        if not keys:
            return None
        return max(keys)

    def as_union_find(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support union-find view")

    def as_neural_graph(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support neural graph view")

    def as_flow_network(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support flow network view")

    def as_trie(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support trie view")

    def as_heap(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support heap view")

    def as_skip_list(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support skip list view")
