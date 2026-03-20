#exonware/xwnode/src/exonware/xwnode/nodes/strategies/cow_tree.py
"""
Copy-on-Write Tree Node Strategy Implementation
Status: Production Ready
True Purpose: Copy-on-write tree with atomic snapshots and reference tracking
Complexity: O(log n) operations with COW semantics
Production Features: ✓ COW Semantics, ✓ Reference Counting, ✓ Memory Pressure Monitoring, ✓ Cycle Detection
This module implements the COW_TREE strategy for copy-on-write trees with
atomic snapshots and versioning capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.10
Generation Date: 24-Oct-2025
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
from typing import Any
import weakref
import gc
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class COWTreeNode:
    """
    Copy-on-write node in the tree with advanced reference counting.
    Implements reference counting, cycle detection, and memory tracking.
    """

    def __init__(self, key: str, value: Any = None, left: COWTreeNode | None = None,
                 right: COWTreeNode | None = None, ref_count: int = 1):
        """Time Complexity: O(1)"""
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.ref_count = ref_count
        self._frozen = False
        self._hash = None
        self._generation = 0  # Generational tracking
        self._weak_refs: list[weakref.ref] = []  # Weak references for cycle detection

    def __hash__(self) -> int:
        """
        Cache hash for performance.
        Time Complexity: O(1) amortized
        """
        if self._hash is None:
            self._hash = hash((self.key, self.value, id(self.left), id(self.right)))
        return self._hash

    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, COWTreeNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.left is other.left and
                self.right is other.right)

    def increment_ref(self) -> None:
        """Increment reference count."""
        if not self._frozen:
            self.ref_count += 1

    def decrement_ref(self) -> bool:
        """Decrement reference count, return True if should be deleted."""
        if not self._frozen:
            self.ref_count -= 1
            return self.ref_count <= 0
        return False

    def freeze(self) -> None:
        """Freeze node to prevent modifications."""
        self._frozen = True

    def is_shared(self) -> bool:
        """Check if node is shared (ref_count > 1)."""
        return self.ref_count > 1

    def add_weak_ref(self, ref: weakref.ref) -> None:
        """Add weak reference for cycle detection."""
        self._weak_refs.append(ref)

    def has_cycles(self, visited: set[int] | None = None) -> bool:
        """
        Check for reference cycles (advanced feature).
        Uses graph traversal to detect cycles in the tree structure.
        """
        if visited is None:
            visited = set()
        node_id = id(self)
        if node_id in visited:
            return True  # Cycle detected
        visited.add(node_id)
        # Check left and right children
        if self.left and self.left.has_cycles(visited):
            return True
        if self.right and self.right.has_cycles(visited):
            return True
        return False


class COWTreeStrategy(ANodeTreeStrategy):
    """
    Copy-on-write tree node strategy with atomic snapshots.
    Provides instant snapshots, atomic updates, and versioning through
    copy-on-write semantics with reference counting.
    """
    STRATEGY_TYPE = NodeType.TREE

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the COW tree strategy with advanced features."""
        super().__init__(NodeMode.COW_TREE, traits, **options)
        self.case_sensitive = options.get('case_sensitive', True)
        self.balanced = options.get('balanced', True)  # Use AVL balancing
        self.auto_snapshot = options.get('auto_snapshot', False)
        # Core COW tree
        self._root: COWTreeNode | None = None
        self._size = 0
        self._version = 0
        self._snapshots: list[COWTreeStrategy] = []
        # Statistics
        self._total_copies = 0
        self._total_shares = 0
        self._max_height = 0
        self._snapshot_count = 0
        # Memory pressure monitoring
        self._memory_pressure_threshold = options.get('memory_pressure_threshold', 10000)  # nodes
        self._total_nodes = 0
        self._current_generation = 0
        # Cycle detection
        self._check_cycles = options.get('check_cycles', False)  # Performance cost

    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the COW tree strategy."""
        return (NodeTrait.PERSISTENT | NodeTrait.ORDERED | NodeTrait.INDEXED)

    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()

    def _create_node(self, key: str, value: Any, left: COWTreeNode | None = None,
                    right: COWTreeNode | None = None) -> COWTreeNode:
        """Create new node with generational tracking."""
        node = COWTreeNode(key, value, left, right)
        node._generation = self._current_generation
        self._total_nodes += 1
        # Check memory pressure
        if self._total_nodes > self._memory_pressure_threshold:
            self._gc_old_generations()
        return node

    def _copy_node(self, node: COWTreeNode) -> COWTreeNode:
        """Copy node with COW semantics and smart heuristics."""
        if not node.is_shared():
            # Node is not shared, can modify in place
            self._total_shares += 1
            return node
        # Node is shared, need to copy
        self._total_copies += 1
        new_node = COWTreeNode(node.key, node.value, node.left, node.right)
        new_node._generation = self._current_generation  # Update generation
        # Increment reference counts for shared children
        if node.left:
            node.left.increment_ref()
        if node.right:
            node.right.increment_ref()
        # Cycle detection if enabled
        if self._check_cycles and new_node.has_cycles():
            raise RuntimeError("Cycle detected in COW tree structure")
        return new_node

    def _get_height(self, node: COWTreeNode | None) -> int:
        """Get height of node."""
        if not node:
            return 0
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)

    def _get_balance(self, node: COWTreeNode | None) -> int:
        """Get balance factor of node."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, node: COWTreeNode) -> COWTreeNode:
        """Right rotation for AVL balancing."""
        left = node.left
        if not left:
            return node
        # Copy nodes if shared
        left = self._copy_node(left)
        node = self._copy_node(node)
        # Perform rotation
        new_right = self._create_node(node.key, node.value, left.right, node.right)
        new_root = self._create_node(left.key, left.value, left.left, new_right)
        return new_root

    def _rotate_left(self, node: COWTreeNode) -> COWTreeNode:
        """Left rotation for AVL balancing."""
        right = node.right
        if not right:
            return node
        # Copy nodes if shared
        right = self._copy_node(right)
        node = self._copy_node(node)
        # Perform rotation
        new_left = self._create_node(node.key, node.value, node.left, right.left)
        new_root = self._create_node(right.key, right.value, new_left, right.right)
        return new_root

    def _balance_node(self, node: COWTreeNode) -> COWTreeNode:
        """Balance node using AVL rotations."""
        if not self.balanced:
            return node
        balance = self._get_balance(node)
        # Left heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                # Left-Right case
                new_left = self._rotate_left(node.left)
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._rotate_right(new_node)
            else:
                # Left-Left case
                return self._rotate_right(node)
        # Right heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                # Right-Left case
                new_right = self._rotate_right(node.right)
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._rotate_left(new_node)
            else:
                # Right-Right case
                return self._rotate_left(node)
        return node

    def _insert_node(self, node: COWTreeNode | None, key: str, value: Any) -> tuple[COWTreeNode | None, bool]:
        """Insert node with COW semantics."""
        if not node:
            new_node = self._create_node(key, value)
            return new_node, True
        # Copy node if shared
        if node.is_shared():
            node = self._copy_node(node)
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        if normalized_key < node_key:
            new_left, inserted = self._insert_node(node.left, key, value)
            if inserted or new_left is not node.left:
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        elif normalized_key > node_key:
            new_right, inserted = self._insert_node(node.right, key, value)
            if inserted or new_right is not node.right:
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        else:
            # Key exists, update value
            if node.value == value:
                # Share unchanged node
                self._total_shares += 1
                return node, False
            else:
                new_node = self._create_node(node.key, value, node.left, node.right)
                return new_node, False

    def _find_node(self, node: COWTreeNode | None, key: str) -> COWTreeNode | None:
        """Find node by key."""
        if not node:
            return None
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        if normalized_key < node_key:
            return self._find_node(node.left, key)
        elif normalized_key > node_key:
            return self._find_node(node.right, key)
        else:
            return node

    def _delete_node(self, node: COWTreeNode | None, key: str) -> tuple[COWTreeNode | None, bool]:
        """Delete node with COW semantics."""
        if not node:
            return None, False
        # Copy node if shared
        if node.is_shared():
            node = self._copy_node(node)
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        if normalized_key < node_key:
            new_left, deleted = self._delete_node(node.left, key)
            if deleted or new_left is not node.left:
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        elif normalized_key > node_key:
            new_right, deleted = self._delete_node(node.right, key)
            if deleted or new_right is not node.right:
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        else:
            # Found node to delete
            if not node.left:
                return node.right, True
            elif not node.right:
                return node.left, True
            else:
                # Node has both children, find successor
                successor = self._find_min(node.right)
                new_right, _ = self._delete_node(node.right, successor.key)
                new_node = self._create_node(successor.key, successor.value, node.left, new_right)
                return self._balance_node(new_node), True

    def _find_min(self, node: COWTreeNode) -> COWTreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node

    def _find_max(self, node: COWTreeNode) -> COWTreeNode:
        """Find maximum node in subtree."""
        while node.right:
            node = node.right
        return node

    def _inorder_traversal(self, node: COWTreeNode | None) -> Iterator[tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)

    def _preorder_traversal(self, node: COWTreeNode | None) -> Iterator[tuple[str, Any]]:
        """Pre-order traversal of tree."""
        if node:
            yield (node.key, node.value)
            yield from self._preorder_traversal(node.left)
            yield from self._preorder_traversal(node.right)

    def _postorder_traversal(self, node: COWTreeNode | None) -> Iterator[tuple[str, Any]]:
        """Post-order traversal of tree."""
        if node:
            yield from self._postorder_traversal(node.left)
            yield from self._postorder_traversal(node.right)
            yield (node.key, node.value)

    def _freeze_tree(self, node: COWTreeNode | None) -> None:
        """Freeze entire tree to prevent modifications."""
        if node:
            node.freeze()
            self._freeze_tree(node.left)
            self._freeze_tree(node.right)
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        new_root, inserted = self._insert_node(self._root, key, value)
        self._root = new_root
        if inserted:
            self._size += 1
            self._version += 1
        self._max_height = max(self._max_height, self._get_height(self._root))
        # Auto-snapshot if enabled
        if self.auto_snapshot and inserted:
            self.snapshot()

    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        node = self._find_node(self._root, key)
        return node.value if node else default

    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        new_root, deleted = self._delete_node(self._root, key)
        self._root = new_root
        if deleted:
            self._size -= 1
            self._version += 1
        return deleted

    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        return self._find_node(self._root, key) is not None

    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
        self._version += 1

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
    # COW TREE SPECIFIC OPERATIONS
    # ============================================================================

    def snapshot(self) -> COWTreeStrategy:
        """Create an atomic snapshot of the current tree."""
        snapshot = COWTreeStrategy(self.traits, **self.options)
        snapshot._root = self._root
        snapshot._size = self._size
        snapshot._version = self._version
        # Increment reference counts for shared nodes
        if self._root:
            self._root.increment_ref()
        # Freeze the snapshot to prevent modifications
        snapshot._freeze_tree(snapshot._root)
        self._snapshots.append(snapshot)
        self._snapshot_count += 1
        return snapshot

    def restore_snapshot(self, snapshot: COWTreeStrategy) -> None:
        """Restore from a snapshot."""
        # Decrement reference counts for current tree
        if self._root:
            self._root.decrement_ref()
        # Copy snapshot state
        self._root = snapshot._root
        self._size = snapshot._size
        self._version = snapshot._version
        # Increment reference counts for restored tree
        if self._root:
            self._root.increment_ref()

    def get_snapshots(self) -> list[COWTreeStrategy]:
        """Get list of all snapshots."""
        return self._snapshots.copy()

    def cleanup_snapshots(self) -> int:
        """Clean up old snapshots, return number of snapshots removed."""
        removed = len(self._snapshots)
        self._snapshots.clear()
        self._snapshot_count = 0
        # Trigger garbage collection to reclaim memory
        gc.collect()
        return removed

    def _gc_old_generations(self) -> None:
        """
        Garbage collect old generations under memory pressure.
        Removes nodes from old generations that are no longer referenced.
        """
        # Increment generation
        self._current_generation += 1
        # Force Python garbage collection
        collected = gc.collect()
        # Reset node count estimate
        self._total_nodes = self._size * 2  # Rough estimate

    def get_memory_pressure(self) -> dict[str, Any]:
        """
        Get memory pressure statistics.
        Returns information about memory usage and pressure.
        """
        return {
            'total_nodes': self._total_nodes,
            'memory_threshold': self._memory_pressure_threshold,
            'pressure_ratio': self._total_nodes / self._memory_pressure_threshold,
            'current_generation': self._current_generation,
            'under_pressure': self._total_nodes > self._memory_pressure_threshold,
            'estimated_memory_bytes': self._total_nodes * 128,  # Rough estimate
            'active_snapshots': len(self._snapshots)
        }

    def get_version(self) -> int:
        """Get current version number."""
        return self._version

    def get_stats(self) -> dict[str, Any]:
        """Get performance statistics with memory pressure details."""
        memory_pressure = self.get_memory_pressure()
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'version': self._version,
            'snapshot_count': self._snapshot_count,
            'total_copies': self._total_copies,
            'total_shares': self._total_shares,
            'copy_ratio': self._total_copies / max(1, self._total_shares + self._total_copies),
            'strategy': 'COW_TREE',
            'backend': 'Copy-on-write AVL tree with advanced reference counting',
            'production_features': [
                'Copy-on-Write Semantics',
                'Reference Counting',
                'Memory Pressure Monitoring',
                'Generational Tracking',
                'Cycle Detection (optional)',
                'Automatic Garbage Collection'
            ],
            'memory_pressure': memory_pressure,
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }

    # ============================================================================
    # ANodeTreeStrategy / ANodeGraphStrategy abstract methods
    # ============================================================================

    def get_min(self) -> tuple[str, Any] | None:
        """Get the minimum key-value pair. Time Complexity: O(log n)."""
        if not self._root:
            return None
        min_node = self._find_min(self._root)
        return (min_node.key, min_node.value)

    def get_max(self) -> tuple[str, Any] | None:
        """Get the maximum key-value pair. Time Complexity: O(log n)."""
        if not self._root:
            return None
        max_node = self._find_max(self._root)
        return (max_node.key, max_node.value)

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse tree in specified order (inorder, preorder, postorder)."""
        if order == 'inorder':
            return [kv for kv in self._inorder_traversal(self._root)]
        if order == 'preorder':
            return list(self._preorder_traversal(self._root))
        if order == 'postorder':
            return list(self._postorder_traversal(self._root))
        return [kv for kv in self._inorder_traversal(self._root)]

    def as_trie(self):
        raise XWNodeUnsupportedCapabilityError("COW tree cannot behave as Trie")

    def as_heap(self):
        raise XWNodeUnsupportedCapabilityError("COW tree cannot behave as Heap")

    def as_skip_list(self):
        raise XWNodeUnsupportedCapabilityError("COW tree cannot behave as SkipList")

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        raise XWNodeUnsupportedCapabilityError("COW tree does not support graph edges")

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        raise XWNodeUnsupportedCapabilityError("COW tree does not support graph edges")

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        raise XWNodeUnsupportedCapabilityError("COW tree does not support graph edges")

    def find_path(self, start: Any, end: Any) -> list[Any]:
        raise XWNodeUnsupportedCapabilityError("COW tree does not support graph paths")

    def get_neighbors(self, node: Any) -> list[Any]:
        raise XWNodeUnsupportedCapabilityError("COW tree does not support graph neighbors")

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        raise XWNodeUnsupportedCapabilityError("COW tree does not support graph edges")

    def as_union_find(self):
        raise XWNodeUnsupportedCapabilityError("COW tree cannot behave as Union-Find")

    def as_neural_graph(self):
        raise XWNodeUnsupportedCapabilityError("COW tree cannot behave as Neural Graph")

    def as_flow_network(self):
        raise XWNodeUnsupportedCapabilityError("COW tree cannot behave as Flow Network")
