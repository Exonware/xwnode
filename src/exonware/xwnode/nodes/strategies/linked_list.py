#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/linked_list.py
Linked List Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.16
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
"""
Linked List Node Strategy Implementation
This module implements the LINKED_LIST strategy for efficient
insertions and deletions with sequential access patterns.
"""
from typing import Any
from .base import ANodeLinearStrategy
from ...defs import NodeMode, NodeTrait
from .contracts import NodeType


class ListNode:
    """Node in the doubly linked list."""

    def __init__(self, key: str, value: Any):
        """Time Complexity: O(1)"""
        self.key = key
        self.value = value
        self.prev: ListNode | None = None
        self.next: ListNode | None = None


class LinkedListStrategy(ANodeLinearStrategy):
    """
    Linked List node strategy for efficient insertions and deletions.
    Provides O(1) insertions/deletions at known positions with
    sequential access patterns optimized for iteration.
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.LINEAR

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the Linked List strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.LINKED_LIST, traits, **options)
        self.doubly_linked = options.get('doubly_linked', True)
        # Doubly linked list with sentinel nodes
        self._head = ListNode("_head", None)
        self._tail = ListNode("_tail", None)
        self._head.next = self._tail
        self._tail.prev = self._head
        # Map for O(1) key lookup
        self._key_to_node: dict[str, ListNode] = {}
        self._size = 0

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the linked list strategy.
        Time Complexity: O(1)
        """
        return NodeTrait.ORDERED | NodeTrait.DOUBLE_ENDED | NodeTrait.FAST_INSERT | NodeTrait.FAST_DELETE

    def _insert_after(self, prev_node: ListNode, key: str, value: Any) -> ListNode:
        """
        Insert node after given node.
        Time Complexity: O(1)
        """
        new_node = ListNode(key, value)
        next_node = prev_node.next
        new_node.prev = prev_node
        new_node.next = next_node
        prev_node.next = new_node
        next_node.prev = new_node
        return new_node

    def _remove_node(self, node: ListNode) -> None:
        """
        Remove node from list.
        Time Complexity: O(1)
        """
        prev_node = node.prev
        next_node = node.next
        if prev_node:
            prev_node.next = next_node
        if next_node:
            next_node.prev = prev_node

    def _get_node_at_index(self, index: int) -> ListNode | None:
        """
        Get node at specific index.
        Time Complexity: O(n)
        """
        if index < 0 or index >= self._size:
            return None
        current = self._head.next
        for i in range(index):
            if current == self._tail:
                return None
            current = current.next
        return current if current != self._tail else None
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """
        Add key-value pair to linked list.
        Time Complexity: O(1)
        """
        key_str = str(key)
        if key_str in self._key_to_node:
            # Update existing
            self._key_to_node[key_str].value = value
        else:
            # Insert new at end
            new_node = self._insert_after(self._tail.prev, key_str, value)
            self._key_to_node[key_str] = new_node
            self._size += 1

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get value by key.
        Time Complexity: O(1) with key lookup, O(n) without
        """
        key_str = str(key)
        if key_str in self._key_to_node:
            return self._key_to_node[key_str].value
        return default

    def has(self, key: Any) -> bool:
        """
        Check if key exists.
        Time Complexity: O(1)
        """
        return str(key) in self._key_to_node

    def remove(self, key: Any) -> bool:
        """
        Remove key from list.
        Time Complexity: O(1)
        """
        key_str = str(key)
        if key_str in self._key_to_node:
            node = self._key_to_node[key_str]
            self._remove_node(node)
            del self._key_to_node[key_str]
            self._size -= 1
            return True
        return False

    def delete(self, key: Any) -> bool:
        """
        Remove key from list (alias for remove).
        Time Complexity: O(1)
        """
        return self.remove(key)

    def clear(self) -> None:
        """
        Clear all data.
        Time Complexity: O(n)
        """
        self._head.next = self._tail
        self._tail.prev = self._head
        self._key_to_node.clear()
        self._size = 0

    def keys(self) -> Iterator[str]:
        """
        Get all keys in order.
        Time Complexity: O(n)
        """
        current = self._head.next
        while current != self._tail:
            yield current.key
            current = current.next

    def values(self) -> Iterator[Any]:
        """
        Get all values in order.
        Time Complexity: O(n)
        """
        current = self._head.next
        while current != self._tail:
            yield current.value
            current = current.next

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Get all key-value pairs in order.
        Time Complexity: O(n)
        """
        current = self._head.next
        while current != self._tail:
            yield (current.key, current.value)
            current = current.next

    def get_at(self, index: int) -> Any:
        """Get value at zero-based index, or None when out of bounds."""
        if index < 0 or index >= self._size:
            return None
        current_index = 0
        current = self._head.next
        while current != self._tail:
            if current_index == index:
                return current.value
            current_index += 1
            current = current.next
        return None

    def __len__(self) -> int:
        """
        Get number of items.
        Time Complexity: O(1)
        """
        return self._size

    def to_native(self) -> dict[str, Any]:
        """
        Convert to native Python dict preserving linked-list order.
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
        This is a list strategy.
        Time Complexity: O(1)
        """
        return True
    @property

    def is_dict(self) -> bool:
        """
        This also behaves like a dict.
        Time Complexity: O(1)
        """
        return True
    # ============================================================================
    # LINKED LIST SPECIFIC OPERATIONS
    # ============================================================================

    def append(self, value: Any) -> str:
        """
        Append value to end of list.
        Time Complexity: O(1)
        """
        key = str(self._size)
        self.put(key, value)
        return key

    def prepend(self, value: Any) -> str:
        """
        Prepend value to beginning of list.
        Time Complexity: O(1)
        """
        key = f"prepend_{self._size}"
        new_node = self._insert_after(self._head, key, value)
        self._key_to_node[key] = new_node
        self._size += 1
        return key

    def insert_at(self, index: int, value: Any) -> str:
        """
        Insert value at specific index.
        Time Complexity: O(n)
        """
        if index < 0 or index > self._size:
            raise IndexError(f"Index {index} out of range")
        if index == 0:
            return self.prepend(value)
        elif index == self._size:
            return self.append(value)
        # Find insertion point
        prev_node = self._get_node_at_index(index - 1)
        if not prev_node:
            raise IndexError(f"Cannot find insertion point at index {index}")
        key = f"insert_{index}_{self._size}"
        new_node = self._insert_after(prev_node, key, value)
        self._key_to_node[key] = new_node
        self._size += 1
        return key

    def insert(self, index: int, value: Any) -> None:
        """
        Insert value at index.
        Time Complexity: O(n)
        """
        self.insert_at(index, value)

    def push_back(self, value: Any) -> None:
        """
        Add element to back.
        Time Complexity: O(1)
        """
        self.append(value)

    def push_front(self, value: Any) -> None:
        """
        Add element to front.
        Time Complexity: O(1)
        """
        self.prepend(value)

    def pop_back(self) -> Any:
        """
        Remove and return element from back.
        Time Complexity: O(1)
        """
        return self.pop()

    def pop_front(self) -> Any:
        """
        Remove and return element from front.
        Time Complexity: O(1)
        """
        return self.popleft()

    def pop(self) -> Any:
        """
        Remove and return last element.
        Time Complexity: O(1)
        """
        if self._size == 0:
            raise IndexError("pop from empty list")
        last_node = self._tail.prev
        value = last_node.value
        self._remove_node(last_node)
        del self._key_to_node[last_node.key]
        self._size -= 1
        return value

    def popleft(self) -> Any:
        """
        Remove and return first element.
        Time Complexity: O(1)
        """
        if self._size == 0:
            raise IndexError("popleft from empty list")
        first_node = self._head.next
        value = first_node.value
        self._remove_node(first_node)
        del self._key_to_node[first_node.key]
        self._size -= 1
        return value

    def first(self) -> Any:
        """Get first element without removing."""
        if self._size == 0:
            return None
        return self._head.next.value

    def last(self) -> Any:
        """Get last element without removing."""
        if self._size == 0:
            return None
        return self._tail.prev.value

    def reverse(self) -> None:
        """Reverse the list in place."""
        if self._size <= 1:
            return
        current = self._head.next
        while current != self._tail:
            current.prev, current.next = current.next, current.prev
            current = current.prev
        self._head.next, self._tail.prev = self._tail.prev, self._head.next
        self._head.next.prev = self._head
        self._tail.prev.next = self._tail

    def get_at_index(self, index: int) -> Any:
        """Get value at specific index."""
        node = self._get_node_at_index(index)
        if not node:
            raise IndexError(f"Index {index} out of range")
        return node.value

    def set_at_index(self, index: int, value: Any) -> None:
        """Set value at specific index."""
        node = self._get_node_at_index(index)
        if not node:
            raise IndexError(f"Index {index} out of range")
        node.value = value

    def find_index(self, value: Any) -> int:
        """Find index of first occurrence of value."""
        current = self._head.next
        index = 0
        while current != self._tail:
            if current.value == value:
                return index
            current = current.next
            index += 1
        return -1

    def remove_value(self, value: Any) -> bool:
        """Remove first occurrence of value."""
        current = self._head.next
        while current != self._tail:
            if current.value == value:
                self._remove_node(current)
                del self._key_to_node[current.key]
                self._size -= 1
                return True
            current = current.next
        return False

    def count_value(self, value: Any) -> int:
        """Count occurrences of value."""
        count = 0
        current = self._head.next
        while current != self._tail:
            if current.value == value:
                count += 1
            current = current.next
        return count

    def to_array(self) -> list[Any]:
        """Convert to array representation."""
        return list(self.values())

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive linked list statistics."""
        return {
            'size': self._size,
            'doubly_linked': self.doubly_linked,
            'first_value': self.first(),
            'last_value': self.last(),
            'memory_overhead': self._size * 24,  # Estimated
            'access_pattern': 'Sequential'
        }
    @property

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'LINKED_LIST',
            'backend': 'Doubly linked list with sentinel nodes',
            'doubly_linked': self.doubly_linked,
            'complexity': {
                'insert': 'O(1) at known position, O(n) at index',
                'delete': 'O(1) at known position, O(n) at index',
                'search': 'O(n)',
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
            'first_value': str(stats['first_value']) if stats['first_value'] is not None else 'None',
            'last_value': str(stats['last_value']) if stats['last_value'] is not None else 'None',
            'doubly_linked': stats['doubly_linked'],
            'memory_overhead': f"{stats['memory_overhead']} bytes",
            'access_pattern': stats['access_pattern']
        }
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeLinearStrategy)
    # ============================================================================

    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        return self  # LinkedListStrategy is already a linked list

    def as_stack(self):
        """Provide Stack behavioral view."""
        raise NotImplementedError(
            "LinkedList cannot behave as Stack - use StackStrategy for LIFO operations"
        )

    def as_queue(self):
        """Provide Queue behavioral view."""
        raise NotImplementedError(
            "LinkedList cannot behave as Queue - use QueueStrategy for FIFO operations"
        )

    def as_deque(self):
        """Provide Deque behavioral view."""
        raise NotImplementedError(
            "LinkedList cannot behave as Deque - use DequeStrategy for double-ended queue operations"
        )
