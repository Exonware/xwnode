#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/set_tree.py
Set Tree Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
"""
Tree Set Node Strategy Implementation
This module implements the SET_TREE strategy for ordered set operations
using a balanced binary search tree with efficient range queries.
"""
from collections.abc import AsyncIterator, Iterator
from typing import Any
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class TreeNode:
    """Node in the balanced binary search tree."""

    def __init__(self, key: str, value: Any = None):
        """Time Complexity: O(1)"""
        self.key = key
        self.value = value
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None
        self.height = 1
        self.size = 1  # Size of subtree


class SetTreeStrategy(ANodeTreeStrategy):
    """
    Tree Set node strategy for ordered set operations.
    Provides efficient ordered set operations with logarithmic complexity
    for insertions, delet
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
ions, and range queries.
    """

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the Tree Set strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.SET_TREE, traits, **options)
        self.allow_duplicates = options.get('allow_duplicates', False)
        self.case_sensitive = options.get('case_sensitive', True)
        # Core AVL tree
        self._root: TreeNode | None = None
        self._size = 0
        # Key-value mapping for compatibility
        self._values: dict[str, Any] = {}

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the tree set strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)

    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()

    def _get_height(self, node: TreeNode | None) -> int:
        """Get height of node."""
        return node.height if node else 0

    def _get_size(self, node: TreeNode | None) -> int:
        """Get size of subtree."""
        return node.size if node else 0

    def _update_node(self, node: TreeNode) -> None:
        """Update height and size of node."""
        node.height = max(self._get_height(node.left), self._get_height(node.right)) + 1
        node.size = self._get_size(node.left) + self._get_size(node.right) + 1

    def _get_balance(self, node: TreeNode | None) -> int:
        """Get balance factor of node."""
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _rotate_right(self, y: TreeNode) -> TreeNode:
        """Right rotation for AVL balancing."""
        x = y.left
        t2 = x.right
        # Perform rotation
        x.right = y
        y.left = t2
        # Update heights and sizes
        self._update_node(y)
        self._update_node(x)
        return x

    def _rotate_left(self, x: TreeNode) -> TreeNode:
        """Left rotation for AVL balancing."""
        y = x.right
        t2 = y.left
        # Perform rotation
        y.left = x
        x.right = t2
        # Update heights and sizes
        self._update_node(x)
        self._update_node(y)
        return y

    def _insert_node(self, node: TreeNode | None, key: str, value: Any) -> TreeNode:
        """Insert node with AVL balancing."""
        # Standard BST insertion
        if not node:
            return TreeNode(key, value)
        if key < node.key:
            node.left = self._insert_node(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_node(node.right, key, value)
        else:
            # Key exists
            if self.allow_duplicates:
                # Insert as right child for duplicates
                node.right = self._insert_node(node.right, key, value)
            else:
                # Update value
                node.value = value
                return node
        # Update height and size
        self._update_node(node)
        # Get balance factor
        balance = self._get_balance(node)
        # Left heavy
        if balance > 1:
            if key < node.left.key:
                # Left-Left case
                return self._rotate_right(node)
            else:
                # Left-Right case
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        # Right heavy
        if balance < -1:
            if key > node.right.key:
                # Right-Right case
                return self._rotate_left(node)
            else:
                # Right-Left case
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
        return node

    def _find_min(self, node: TreeNode) -> TreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node

    def _delete_node(self, node: TreeNode | None, key: str) -> TreeNode | None:
        """Delete node with AVL balancing."""
        if not node:
            return node
        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            # Node to delete found
            if not node.left or not node.right:
                # Node with only one child or no child
                temp = node.left if node.left else node.right
                if not temp:
                    # No child case
                    temp = node
                    node = None
                else:
                    # One child case
                    node = temp
            else:
                # Node with two children
                temp = self._find_min(node.right)
                node.key = temp.key
                node.value = temp.value
                node.right = self._delete_node(node.right, temp.key)
        if not node:
            return node
        # Update height and size
        self._update_node(node)
        # Get balance factor
        balance = self._get_balance(node)
        # Left heavy
        if balance > 1:
            if self._get_balance(node.left) >= 0:
                return self._rotate_right(node)
            else:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        # Right heavy
        if balance < -1:
            if self._get_balance(node.right) <= 0:
                return self._rotate_left(node)
            else:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
        return node

    def _search_node(self, node: TreeNode | None, key: str) -> TreeNode | None:
        """Search for node with given key."""
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._search_node(node.left, key)
        else:
            return self._search_node(node.right, key)

    def _inorder_traversal(self, node: TreeNode | None, result: list[tuple[str, Any]]) -> None:
        """Inorder traversal to get sorted keys."""
        if node:
            self._inorder_traversal(node.left, result)
            result.append((node.key, node.value))
            self._inorder_traversal(node.right, result)
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """Add key to tree set."""
        key_str = self._normalize_key(str(key))
        old_size = self._get_size(self._root)
        self._root = self._insert_node(self._root, key_str, value)
        new_size = self._get_size(self._root)
        if new_size > old_size:
            self._size += 1
        self._values[key_str] = value if value is not None else True

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        if key_str == "sorted_keys":
            return self.get_sorted_keys()
        elif key_str == "tree_info":
            return {
                'height': self._get_height(self._root),
                'size': self._size,
                'balanced': self.is_balanced()
            }
        normalized_key = self._normalize_key(key_str)
        node = self._search_node(self._root, normalized_key)
        return node.value if node else default

    def has(self, key: Any) -> bool:
        """Check if key exists in set."""
        key_str = self._normalize_key(str(key))
        return self._search_node(self._root, key_str) is not None

    def remove(self, key: Any) -> bool:
        """Remove key from set."""
        key_str = self._normalize_key(str(key))
        if not self._search_node(self._root, key_str):
            return False
        self._root = self._delete_node(self._root, key_str)
        self._size -= 1
        self._values.pop(key_str, None)
        return True

    def delete(self, key: Any) -> bool:
        """Remove key from set (alias for remove)."""
        return self.remove(key)

    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
        self._values.clear()

    def keys(self) -> Iterator[str]:
        """Get all keys in sorted order."""
        result = []
        self._inorder_traversal(self._root, result)
        for key, _ in result:
            yield key

    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        result = []
        self._inorder_traversal(self._root, result)
        for _, value in result:
            yield value

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        result = []
        self._inorder_traversal(self._root, result)
        for key, value in result:
            yield (key, value)

    def __len__(self) -> int:
        """Get number of elements in set."""
        return self._size

    def to_native(self) -> list[str]:
        """Convert to native Python sorted list."""
        return list(self.keys())
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
        """This can behave like a list for ordered access."""
        return True
    @property

    def is_dict(self) -> bool:
        """This behaves like a dict."""
        return True
    # ============================================================================
    # SET-SPECIFIC OPERATIONS
    # ============================================================================

    def add(self, key: str) -> bool:
        """Add element to set. Returns True if element was new."""
        old_size = self._size
        self.put(key)
        return self._size > old_size

    def discard(self, key: str) -> None:
        """Remove element if present (no error if not found)."""
        self.remove(key)

    def get_sorted_keys(self) -> list[str]:
        """Get all keys in sorted order."""
        return list(self.keys())

    def get_range(self, start_key: str, end_key: str, inclusive: bool = True) -> list[str]:
        """Get keys in range [start_key, end_key]."""
        result = []
        start_norm = self._normalize_key(start_key)
        end_norm = self._normalize_key(end_key)
        for key in self.keys():
            if inclusive:
                if start_norm <= key <= end_norm:
                    result.append(key)
            else:
                if start_norm < key < end_norm:
                    result.append(key)
        return result

    def lower_bound(self, key: str) -> str | None:
        """Find first key >= given key."""
        norm_key = self._normalize_key(key)
        for k in self.keys():
            if k >= norm_key:
                return k
        return None

    def upper_bound(self, key: str) -> str | None:
        """Find first key > given key."""
        norm_key = self._normalize_key(key)
        for k in self.keys():
            if k > norm_key:
                return k
        return None

    def floor(self, key: str) -> str | None:
        """Find largest key <= given key."""
        norm_key = self._normalize_key(key)
        result = None
        for k in self.keys():
            if k <= norm_key:
                result = k
            else:
                break
        return result

    def ceiling(self, key: str) -> str | None:
        """Find smallest key >= given key."""
        return self.lower_bound(key)

    def first(self) -> str | None:
        """Get first (smallest) key."""
        if self._root:
            node = self._root
            while node.left:
                node = node.left
            return node.key
        return None

    def last(self) -> str | None:
        """Get last (largest) key."""
        if self._root:
            node = self._root
            while node.right:
                node = node.right
            return node.key
        return None

    def is_balanced(self) -> bool:
        """Check if tree is balanced."""
        def _check_balance(node: TreeNode | None) -> bool:
            if not node:
                return True
            balance = self._get_balance(node)
            if abs(balance) > 1:
                return False
            return _check_balance(node.left) and _check_balance(node.right)
        return _check_balance(self._root)

    def get_tree_statistics(self) -> dict[str, Any]:
        """Get comprehensive tree statistics."""
        if not self._root:
            return {'size': 0, 'height': 0, 'balanced': True}
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'balanced': self.is_balanced(),
            'first_key': self.first(),
            'last_key': self.last(),
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates
        }
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'SET_TREE',
            'backend': 'AVL balanced binary search tree',
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates,
            'complexity': {
                'insert': 'O(log n)',
                'delete': 'O(log n)',
                'search': 'O(log n)',
                'range_query': 'O(log n + k)',  # k = result size
                'traversal': 'O(n)',
                'space': 'O(n)'
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_tree_statistics()
        return {
            'size': stats['size'],
            'height': stats['height'],
            'balanced': stats['balanced'],
            'first_key': stats.get('first_key', 'None'),
            'last_key': stats.get('last_key', 'None'),
            'memory_usage': f"{self._size * 80} bytes (estimated)"
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
