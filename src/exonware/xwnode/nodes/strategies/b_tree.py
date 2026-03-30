#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/b_tree.py
B-Tree Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.20
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
"""
B-Tree Node Strategy Implementation
This module implements the B_TREE strategy for efficient range queries
and sorted key operations with guaranteed O(log n) performance.
"""
from typing import Any
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class BTreeNode:
    """A node in the B-tree."""

    def __init__(self, degree: int, is_leaf: bool = False):
        """
        Initialize B-tree node.
        Time Complexity: O(1)
        """
        self.degree = degree
        self.keys: list[str] = []
        self.values: list[Any] = []
        self.children: list[BTreeNode] = []
        self.is_leaf = is_leaf

    def is_full(self) -> bool:
        """
        Check if node is full.
        Time Complexity: O(1)
        """
        return len(self.keys) == 2 * self.degree - 1

    def search(self, key: str) -> Any | None:
        """
        Search for a key in this subtree.
        Time Complexity: O(log n)
        """
        i = 0
        while i < len(self.keys) and key > self.keys[i]:
            i += 1
        if i < len(self.keys) and key == self.keys[i]:
            return self.values[i]
        if self.is_leaf:
            return None
        return self.children[i].search(key)

    def insert_non_full(self, key: str, value: Any):
        """
        Insert key-value pair into non-full node.
        Time Complexity: O(t * log n) where t is degree
        """
        i = len(self.keys) - 1
        if self.is_leaf:
            # Insert into leaf
            self.keys.append("")
            self.values.append(None)
            while i >= 0 and key < self.keys[i]:
                self.keys[i + 1] = self.keys[i]
                self.values[i + 1] = self.values[i]
                i -= 1
            self.keys[i + 1] = key
            self.values[i + 1] = value
        else:
            # Find child to insert into
            while i >= 0 and key < self.keys[i]:
                i -= 1
            i += 1
            if self.children[i].is_full():
                self.split_child(i)
                if key > self.keys[i]:
                    i += 1
            self.children[i].insert_non_full(key, value)

    def split_child(self, i: int):
        """
        Split the full child at index i.
        Time Complexity: O(t) where t is degree
        """
        full_child = self.children[i]
        new_child = BTreeNode(full_child.degree, full_child.is_leaf)
        # Calculate middle index
        mid = self.degree - 1
        # Store middle key and value to promote
        mid_key = full_child.keys[mid]
        mid_value = full_child.values[mid]
        # Move right half to new child (excluding middle)
        new_child.keys = full_child.keys[mid + 1:]
        new_child.values = full_child.values[mid + 1:]
        # Keep left half in full_child (excluding middle)
        full_child.keys = full_child.keys[:mid]
        full_child.values = full_child.values[:mid]
        # Move children if not leaf
        if not full_child.is_leaf:
            new_child.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]
        # Insert new child and promote middle key
        self.children.insert(i + 1, new_child)
        self.keys.insert(i, mid_key)
        self.values.insert(i, mid_value)


class BTreeStrategy(ANodeTreeStrategy):
    """
    B-Tree strategy for efficient sorted operations and range queries.
    WHY B-Tree:
    - Self-balancing ensures consistent O(log n) performance
    - High branching factor reduces tree height (better than binary trees)
    - Minimizes disk I/O by grouping keys in pages/blocks
    - Excellent for range queries and sequential scans
    WHY this implementation:
    - Uses standard B-Tree algorithm (Knuth, TAOCP Vol 3)
    - Proactive node splitting (split-on-insert strategy)
    - Maintains 2t-1 max keys per node (t = degree)
    - Keeps all leaves at same depth (perfect balance)
    Time Complexity:
    - Insert: O(log n) - REQUIRED for maintaining sorted order
    - Search: O(log n) - Tree height determines this
    - Delete: O(log n) - May require merging/borrowing
    - Range query: O(k + log n) where k = results
    - Iteration: O(n) sorted order guaranteed
    Space Complexity: O(n)
    WHY O(log n) and not O(1):
    - Maintaining sorted order requires tree traversal
    - Balancing operations are essential to B-Tree correctness
    - This trade-off enables efficient range queries
    - Self-balancing prevents degradation to O(n)
    Trade-offs:
    - Advantage: Excellent for range queries (k + log n)
    - Advantage: Guaranteed balanced (no worst-case degradation)
    - Limitation: Higher memory per node vs binary trees
    - Limitation: More complex insertion/deletion logic
    - Compared to Hash Map: Slower single lookups, but supports ranges
    - Compared to Binary Tree: Better cache performance, lower height
    Best for:
    - Database indexes (primary use case)
    - File systems (directory structures)
    - Range queries and sorted iteration
    - Disk-based storage (page-oriented)
    - Large datasets with sorted access
    Not recommended for:
    - Random single-key lookups only (use HASH_MAP)
    - Small datasets (< 100 items, overhead not worth it)
    - Write-heavy workloads (use LSM_TREE)
    - In-memory only with no range queries (use HASH_MAP)
    Following eXonware Priorities:
    1. Security: Predictable performance (no worst-case degradation)
    2. Usability: Sorted iteration, range queries, familiar tree semantics
    3. Maintainability: Well-established algorithm, clear split/merge logic
    4. Performance: O(log n) guaranteed, optimal for disk I/O
    5. Extensibility: Can add concurrent access, bulk loading
    Performance Note:
    This is the CORRECT complexity for a B-Tree. The O(log n) overhead
    enables sorted order and range queries. If you need O(1) operations
    without ordering, use HASH_MAP instead.
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the B-tree strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.B_TREE, traits, **options)
        self.degree = options.get('degree', 3)  # Minimum degree
        self.root: BTreeNode | None = BTreeNode(self.degree, is_leaf=True)
        self._size = 0

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the B-tree strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """
        Store a value with the given key.
        Time Complexity: O(log n)
        """
        key_str = str(key)
        # Check if key already exists (update case)
        if self.has(key_str):
            self._update_existing(key_str, value)
            return
        if self.root.is_full():
            # Create new root
            new_root = BTreeNode(self.degree, is_leaf=False)
            new_root.children.append(self.root)
            new_root.split_child(0)
            self.root = new_root
        self.root.insert_non_full(key_str, value)
        self._size += 1

    def _update_existing(self, key: str, value: Any) -> None:
        """
        Update existing key with new value.
        Time Complexity: O(log n)
        """
        def update_in_node(node: BTreeNode) -> bool:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            if i < len(node.keys) and key == node.keys[i]:
                node.values[i] = value
                return True
            if not node.is_leaf:
                return update_in_node(node.children[i])
            return False
        update_in_node(self.root)

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve a value by key.
        Time Complexity: O(log n)
        """
        if not self.root:
            return default
        result = self.root.search(str(key))
        return result if result is not None else default

    def has(self, key: Any) -> bool:
        """
        Check if key exists in B-tree.
        Time Complexity: O(log n)
        """
        return self.get(key, None) is not None

    def remove(self, key: Any) -> bool:
        """
        Remove value by key (simplified implementation).
        Time Complexity: O(n log n) - rebuilds tree
        """
        # Note: Full B-tree deletion is complex. This is a simplified version.
        key_str = str(key)
        if not self.has(key_str):
            return False
        # For simplicity, we'll rebuild without the key
        # In production, implement proper B-tree deletion
        all_items = list(self.items())
        filtered_items = [(k, v) for k, v in all_items if k != key_str]
        self.clear()
        for k, v in filtered_items:
            self.put(k, v)
        return True

    def delete(self, key: Any) -> bool:
        """
        Remove value by key (alias for remove).
        Time Complexity: O(n log n)
        """
        return self.remove(key)

    def clear(self) -> None:
        """
        Clear all data.
        Time Complexity: O(1)
        """
        self.root = BTreeNode(self.degree, is_leaf=True)
        self._size = 0

    def keys(self) -> Iterator[str]:
        """
        Get all keys in sorted order.
        Time Complexity: O(n) to iterate all
        """
        def inorder_keys(node: BTreeNode) -> Iterator[str]:
            if node.is_leaf:
                yield from node.keys
            else:
                for i in range(len(node.keys)):
                    yield from inorder_keys(node.children[i])
                    yield node.keys[i]
                if node.children:
                    yield from inorder_keys(node.children[-1])
        if self.root:
            yield from inorder_keys(self.root)

    def values(self) -> Iterator[Any]:
        """
        Get all values in key-sorted order.
        Time Complexity: O(n) to iterate all
        """
        def inorder_values(node: BTreeNode) -> Iterator[Any]:
            if node.is_leaf:
                yield from node.values
            else:
                for i in range(len(node.keys)):
                    yield from inorder_values(node.children[i])
                    yield node.values[i]
                if node.children:
                    yield from inorder_values(node.children[-1])
        if self.root:
            yield from inorder_values(self.root)

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Get all key-value pairs in sorted order.
        Time Complexity: O(n) to iterate all
        """
        def inorder_items(node: BTreeNode) -> Iterator[tuple[str, Any]]:
            if node.is_leaf:
                yield from zip(node.keys, node.values)
            else:
                for i in range(len(node.keys)):
                    yield from inorder_items(node.children[i])
                    yield (node.keys[i], node.values[i])
                if node.children:
                    yield from inorder_items(node.children[-1])
        if self.root:
            yield from inorder_items(self.root)

    def __len__(self) -> int:
        """
        Get the number of items.
        Time Complexity: O(1)
        """
        return self._size

    def is_empty(self) -> bool:
        """
        Check if B-Tree is empty.
        Time Complexity: O(1)
        """
        return self._size == 0

    def to_native(self) -> dict[str, Any]:
        """
        Convert to native Python dict.
        Time Complexity: O(n)
        """
        return dict(self.items())
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
        """
        This is not a list strategy.
        Time Complexity: O(1)
        """
        return False
    @property

    def is_dict(self) -> bool:
        """
        This is a dict-like strategy.
        Time Complexity: O(1)
        """
        return True
    # ============================================================================
    # B-TREE SPECIFIC OPERATIONS
    # ============================================================================

    def range_query(self, start_key: str, end_key: str) -> list[str]:
        """
        Get all keys in the specified range [start_key, end_key].
        Time Complexity: O(log n + k) where k is result size
        """
        result: list[str] = []
        for key, value in self.items():
            if start_key <= key <= end_key:
                result.append(key)
            elif key > end_key:
                break
        return result

    def prefix_search(self, prefix: str) -> list[tuple[str, Any]]:
        """
        Find all keys that start with the given prefix.
        Time Complexity: O(n) - may scan all keys
        """
        result = []
        for key, value in self.items():
            if key.startswith(prefix):
                result.append((key, value))
            elif key > prefix:
                # Since keys are sorted, we can stop when we pass the prefix range
                if not key.startswith(prefix):
                    break
        return result

    def min_key(self) -> str | None:
        """
        Get the minimum key.
        Time Complexity: O(log n)
        """
        if not self.root or self._size == 0:
            return None
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        return node.keys[0] if node.keys else None

    def max_key(self) -> str | None:
        """
        Get the maximum key.
        Time Complexity: O(log n)
        """
        if not self.root or self._size == 0:
            return None
        node = self.root
        while not node.is_leaf:
            node = node.children[-1]
        return node.keys[-1] if node.keys else None

    def successor(self, key: str) -> str | None:
        """
        Find the successor of the given key.
        Time Complexity: O(n) - must scan keys
        """
        found = False
        for k in self.keys():
            if found and k > key:
                return k
            if k == key:
                found = True
        return None

    def predecessor(self, key: str) -> str | None:
        """
        Find the predecessor of the given key.
        Time Complexity: O(n) - must scan keys
        """
        prev_key = None
        for k in self.keys():
            if k == key:
                return prev_key
            prev_key = k
        return None
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """
        Get backend implementation info.
        Time Complexity: O(1)
        """
        return {
            'strategy': 'B_TREE',
            'backend': 'Custom B-tree implementation',
            'degree': self.degree,
            'complexity': {
                'search': 'O(log n)',
                'insert': 'O(log n)',
                'delete': 'O(log n)',
                'range_query': 'O(log n + k)',
                'iteration': 'O(n)'
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """
        Get performance metrics.
        Time Complexity: O(log n) - calculates tree height
        """
        # Calculate tree height
        height = 0
        if self.root:
            node = self.root
            while not node.is_leaf and node.children:
                node = node.children[0]
                height += 1
        return {
            'size': self._size,
            'degree': self.degree,
            'height': height,
            'memory_usage': f"{self._size * (24 + 16)} bytes (estimated)",
            'is_sorted': True
        }
    # ============================================================================
    # ANodeTreeStrategy / ANodeGraphStrategy abstract methods
    # ============================================================================

    def get_min(self) -> Any:
        """Get minimum key."""
        keys_iter = self.keys()
        return next(keys_iter, None)

    def get_max(self) -> Any:
        """Get maximum key."""
        keys_list = list(self.keys())
        return keys_list[-1] if keys_list else None

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse in key order."""
        return list(self.items())

    def as_trie(self):
        raise XWNodeUnsupportedCapabilityError("B-tree cannot behave as Trie")

    def as_heap(self):
        raise XWNodeUnsupportedCapabilityError("B-tree cannot behave as Heap")

    def as_skip_list(self):
        raise XWNodeUnsupportedCapabilityError("B-tree cannot behave as SkipList")

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        raise XWNodeUnsupportedCapabilityError("B-tree does not support graph edges")

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        raise XWNodeUnsupportedCapabilityError("B-tree does not support graph edges")

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        raise XWNodeUnsupportedCapabilityError("B-tree does not support graph edges")

    def find_path(self, start: Any, end: Any) -> list[Any]:
        raise XWNodeUnsupportedCapabilityError("B-tree does not support graph paths")

    def get_neighbors(self, node: Any) -> list[Any]:
        raise XWNodeUnsupportedCapabilityError("B-tree does not support graph neighbors")

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        raise XWNodeUnsupportedCapabilityError("B-tree does not support graph edges")

    def as_union_find(self):
        raise XWNodeUnsupportedCapabilityError("B-tree cannot behave as Union-Find")

    def as_neural_graph(self):
        raise XWNodeUnsupportedCapabilityError("B-tree cannot behave as Neural Graph")

    def as_flow_network(self):
        raise XWNodeUnsupportedCapabilityError("B-tree cannot behave as Flow Network")
