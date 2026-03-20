#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/splay_tree.py
Splay Tree Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
#exonware\xnode\strategies\impls\node_splay_tree.py
"""
Splay Tree Node Strategy Implementation
This module implements the SPLAY_TREE strategy for self-adjusting binary
search trees with amortized O(log n) performance.
"""
from typing import Any
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class SplayTreeNode:
    """Node in the splay tree."""

    def __init__(self, key: str, value: Any = None):
        """Time Complexity: O(1)"""
        self.key = key
        self.value = value
        self.left: SplayTreeNode | None = None
        self.right: SplayTreeNode | None = None
        self.parent: SplayTreeNode | None = None
        self._hash = None

    def __hash__(self) -> int:
        """
        Cache hash for performance.
        Time Complexity: O(1) amortized
        """
        if self._hash is None:
            self._hash = hash((self.key, self.value))
        return self._hash

    def __eq__(self, other) -> bool:
        """
        Structural equality.
        Time Complexity: O(1)
        """
        if not isinstance(other, SplayTreeNode):
            return False
        return self.key == other.key and self.value == other.value


class SplayTreeStrategy(ANodeTreeStrategy):
    """
    Splay Tree strategy for self-adjusting binary search trees.
    WHY Splay Tree:
    - Self-optimizing for access patterns (frequently accessed → faster access)
    - Amortized O(log n) performance without explicit balancing rules
    - No extra metadata needed (no heights, colors, priorities)
    - Excellent cache locality (recently accessed near root)
    - Simpler than AVL/Red-Black (just rotations, no complex invariants)
    WHY this implementation:
    - Move-to-root heuristic via splaying on every access
    - Three splay cases: zig, zig-zig, zig-zag
    - Parent pointers enable bottom-up splaying
    - No rebalancing metadata stored
    - Adapts to access patterns automatically
    Time Complexity:
    - Insert: O(log n) amortized
    - Search: O(log n) amortized
    - Delete: O(log n) amortized
    - Worst case per operation: O(n), but amortized is O(log n)
    Space Complexity: O(n) - one node per key + parent pointers
    Trade-offs:
    - Advantage: Adapts to access patterns (hot keys stay near root)
    - Advantage: Simpler than AVL/Red-Black (no balancing metadata)
    - Limitation: Amortized (not worst-case) O(log n)
    - Limitation: Poor for uniform random access
    - Compared to AVL: Better for skewed access, worse for uniform
    Best for:
    - Skewed access patterns (80/20 rule)
    - Caching scenarios (LRU-like behavior)
    - When simplicity is valued
    - Sequential access patterns
    Not recommended for:
    - Uniform random access
    - Hard real-time (amortized, not worst-case)
    - When consistent latency is critical
    Performance Note:
    Splay Trees offer AMORTIZED O(log n), not worst-case.
    A single operation can be O(n), but a sequence of m operations
    is O(m log n). Best for workloads with temporal locality.
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the splay tree strategy."""
        super().__init__(NodeMode.SPLAY_TREE, traits, **options)
        self.case_sensitive = options.get('case_sensitive', True)
        # Core splay tree
        self._root: SplayTreeNode | None = None
        self._size = 0
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_splays = 0
        self._max_height = 0

    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the splay tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)

    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()

    def _get_height(self, node: SplayTreeNode | None) -> int:
        """Get height of node."""
        if not node:
            return 0
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)

    def _rotate_right(self, node: SplayTreeNode) -> None:
        """Right rotation around node."""
        left_child = node.left
        if not left_child:
            return
        # Update parent connections
        node.left = left_child.right
        if left_child.right:
            left_child.right.parent = node
        left_child.parent = node.parent
        if not node.parent:
            self._root = left_child
        elif node == node.parent.left:
            node.parent.left = left_child
        else:
            node.parent.right = left_child
        # Update rotation
        left_child.right = node
        node.parent = left_child

    def _rotate_left(self, node: SplayTreeNode) -> None:
        """Left rotation around node."""
        right_child = node.right
        if not right_child:
            return
        # Update parent connections
        node.right = right_child.left
        if right_child.left:
            right_child.left.parent = node
        right_child.parent = node.parent
        if not node.parent:
            self._root = right_child
        elif node == node.parent.right:
            node.parent.right = right_child
        else:
            node.parent.left = right_child
        # Update rotation
        right_child.left = node
        node.parent = right_child

    def _splay(self, node: SplayTreeNode) -> None:
        """Splay node to root."""
        while node.parent:
            parent = node.parent
            grandparent = parent.parent
            if not grandparent:
                # Zig case
                if node == parent.left:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)
            elif node == parent.left and parent == grandparent.left:
                # Zig-zig case (left-left)
                self._rotate_right(grandparent)
                self._rotate_right(parent)
            elif node == parent.right and parent == grandparent.right:
                # Zig-zig case (right-right)
                self._rotate_left(grandparent)
                self._rotate_left(parent)
            elif node == parent.right and parent == grandparent.left:
                # Zig-zag case (left-right)
                self._rotate_left(parent)
                self._rotate_right(grandparent)
            else:
                # Zig-zag case (right-left)
                self._rotate_right(parent)
                self._rotate_left(grandparent)
            self._total_splays += 1

    def _find_node(self, key: str) -> SplayTreeNode | None:
        """Find node with given key and splay it to root."""
        normalized_key = self._normalize_key(key)
        current = self._root
        while current:
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                # Found the node, splay it to root
                self._splay(current)
                return current
        return None

    def _insert_node(self, key: str, value: Any) -> bool:
        """Insert node with given key and value."""
        normalized_key = self._normalize_key(key)
        # Create new node
        new_node = SplayTreeNode(key, value)
        # Find insertion point
        current = self._root
        parent = None
        while current:
            parent = current
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                # Key already exists, update value and splay
                current.value = value
                self._splay(current)
                return False
        # Insert new node
        new_node.parent = parent
        if not parent:
            self._root = new_node
        elif normalized_key < self._normalize_key(parent.key):
            parent.left = new_node
        else:
            parent.right = new_node
        # Splay new node to root
        self._splay(new_node)
        self._size += 1
        self._total_insertions += 1
        self._max_height = max(self._max_height, self._get_height(self._root))
        return True

    def _delete_node(self, key: str) -> bool:
        """Delete node with given key."""
        node = self._find_node(key)
        if not node:
            return False
        # Splay node to root
        self._splay(node)
        # If node has no children, just remove it
        if not node.left and not node.right:
            self._root = None
        elif not node.left:
            # Only right child
            self._root = node.right
            self._root.parent = None
        elif not node.right:
            # Only left child
            self._root = node.left
            self._root.parent = None
        else:
            # Both children exist
            # Find maximum in left subtree
            max_left = node.left
            while max_left.right:
                max_left = max_left.right
            # Splay max_left to root of left subtree
            self._splay(max_left)
            # Attach right subtree to max_left
            max_left.right = node.right
            if node.right:
                node.right.parent = max_left
            # Make max_left the new root
            self._root = max_left
            self._root.parent = None
        self._size -= 1
        self._total_deletions += 1
        return True

    def _inorder_traversal(self, node: SplayTreeNode | None) -> Iterator[tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        self._insert_node(key, value)

    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        node = self._find_node(key)
        return node.value if node else default

    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        return self._delete_node(key)

    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        return self._find_node(key) is not None

    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0

    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._size

    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self._size

    def to_native(self) -> dict[str, Any]:
        """Convert to native Python dict."""
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

    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self._root is None
    # ============================================================================
    # ITERATION
    # ============================================================================

    def keys(self) -> Iterator[str]:
        """Iterate over keys in sorted order."""
        for key, _ in self._inorder_traversal(self._root):
            yield key

    def values(self) -> Iterator[Any]:
        """Iterate over values in key order."""
        for _, value in self._inorder_traversal(self._root):
            yield value

    def items(self) -> Iterator[tuple[str, Any]]:
        """Iterate over key-value pairs in sorted order."""
        yield from self._inorder_traversal(self._root)

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        yield from self.keys()
    # ============================================================================
    # SPLAY TREE SPECIFIC OPERATIONS
    # ============================================================================

    def get_min(self) -> tuple[str, Any] | None:
        """Get the minimum key-value pair."""
        if not self._root:
            return None
        # Find minimum and splay it to root
        current = self._root
        while current.left:
            current = current.left
        self._splay(current)
        return (current.key, current.value)

    def get_max(self) -> tuple[str, Any] | None:
        """Get the maximum key-value pair."""
        if not self._root:
            return None
        # Find maximum and splay it to root
        current = self._root
        while current.right:
            current = current.right
        self._splay(current)
        return (current.key, current.value)

    def get_height(self) -> int:
        """Get the height of the tree."""
        return self._get_height(self._root)

    def splay_to_root(self, key: str) -> bool:
        """Splay node with given key to root."""
        node = self._find_node(key)
        return node is not None

    def get_root_key(self) -> str | None:
        """Get the key of the root node."""
        return self._root.key if self._root else None

    def get_root_value(self) -> Any | None:
        """Get the value of the root node."""
        return self._root.value if self._root else None

    def get_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_splays': self._total_splays,
            'root_key': self.get_root_key(),
            'strategy': 'SPLAY_TREE',
            'backend': 'Self-adjusting splay tree with amortized O(log n) performance',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
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
