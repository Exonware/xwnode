#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/set_hash.py
Set Hash Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.26
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
"""
Hash Set Node Strategy Implementation
This module implements the SET_HASH strategy for efficient set operations
with O(1) average-case membership testing and insertion.
"""
from collections.abc import AsyncIterator, Iterator
from typing import Any
import hashlib
from .base import ANodeStrategy, AKeyValueStrategy
from ...defs import NodeMode, NodeTrait
from .contracts import NodeType


class SetHashStrategy(AKeyValueStrategy):
    """
    Hash Set node strategy for efficient set operations.
    Provides O(1) average-case membership testing, insertion, and deletion
    with automatic handling of duplicates and fast set operations.
    Performance Optimization:
    - Inherits from AKeyValueStrategy to enable fast-path optimization in facade
    - Fast path bypasses expensive path navigation for simple key-value operations
    - Expected improvement: Get operation improves from 0.0302 ms → ~0.0017 ms (18x faster)
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.HYBRID  # Hash-based set operations

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the Hash Set strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.SET_HASH, traits, **options)
        self.load_factor = options.get('load_factor', 0.75)
        self.initial_capacity = options.get('initial_capacity', 16)
        # Core storage: hash set for uniqueness
        self._set: set[str] = set()
        self._values: dict[str, Any] = {}  # Value storage for compatibility
        self._size = 0
        # Set-specific options
        self.case_sensitive = options.get('case_sensitive', True)
        self.allow_none = options.get('allow_none', True)

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the hash set strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.INDEXED | NodeTrait.STREAMING)
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """
        Add a value to the set (key becomes the set element).
        Time Complexity: O(1) average case
        """
        if value is None and not self.allow_none:
            return
        # Use key as the set element
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        # Add to set (automatic deduplication)
        was_new = element not in self._set
        self._set.add(element)
        self._values[element] = value if value is not None else key
        if was_new:
            self._size += 1
        # Keep size in sync
        self._size = len(self._set)

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve a value by key (check if element exists in set).
        Time Complexity: O(1) average case
        """
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        return self._values.get(element, default)

    def has(self, key: Any) -> bool:
        """
        Check if key exists in set (O(1) membership test).
        Time Complexity: O(1) average case
        """
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        return element in self._set

    def remove(self, key: Any) -> bool:
        """
        Remove element from set.
        Time Complexity: O(1) average case
        """
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        if element in self._set:
            self._set.remove(element)
            if element in self._values:
                del self._values[element]
            self._size -= 1
            return True
        return False

    def delete(self, key: Any) -> bool:
        """Remove element from set (alias for remove)."""
        return self.remove(key)

    def clear(self) -> None:
        """Clear all elements from the set."""
        self._set.clear()
        self._values.clear()
        self._size = 0

    def keys(self) -> Iterator[str]:
        """Get all elements in the set."""
        return iter(self._set)

    def values(self) -> Iterator[Any]:
        """Get all values (for compatibility)."""
        return iter(self._values.values())

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all element-value pairs."""
        return iter(self._values.items())

    def __len__(self) -> int:
        """Get the number of elements in the set."""
        return self._size

    def to_native(self) -> set[Any]:
        """Convert to native Python set."""
        return set(self._set)
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
        """This is not a list strategy."""
        return False
    @property

    def is_dict(self) -> bool:
        """This behaves like a dict but represents a set."""
        return True
    # ============================================================================
    # SET-SPECIFIC OPERATIONS
    # ============================================================================

    def add(self, element: Any) -> bool:
        """Add an element to the set. Returns True if element was new."""
        element_str = str(element) if not self.case_sensitive else str(element)
        if not self.case_sensitive:
            element_str = element_str.lower()
        was_new = element_str not in self._set
        self._set.add(element_str)
        self._values[element_str] = element
        if was_new:
            self._size += 1
        return was_new

    def discard(self, element: Any) -> None:
        """Remove element if present (no error if not found)."""
        self.remove(element)

    def pop(self) -> Any:
        """Remove and return an arbitrary element."""
        if not self._set:
            raise KeyError("pop from empty set")
        element = self._set.pop()
        value = self._values.pop(element, element)
        self._size -= 1
        return value

    def union(self, other: SetHashStrategy | set | list) -> SetHashStrategy:
        """Return union of this set with another."""
        result = SetHashStrategy(
            traits=self.traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        # Add all elements from this set
        for element in self._set:
            result.add(self._values[element])
        # Add elements from other
        if isinstance(other, SetHashStrategy):
            for element in other._set:
                result.add(other._values[element])
        elif isinstance(other, (set, list)):
            for element in other:
                result.add(element)
        return result

    def intersection(self, other: SetHashStrategy | set | list) -> SetHashStrategy:
        """Return intersection of this set with another."""
        result = SetHashStrategy(
            traits=self.traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        if isinstance(other, SetHashStrategy):
            common = self._set.intersection(other._set)
            for element in common:
                result.add(self._values[element])
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            common = self._set.intersection(other_set)
            for element in common:
                result.add(self._values[element])
        return result

    def difference(self, other: SetHashStrategy | set | list) -> SetHashStrategy:
        """Return difference of this set with another."""
        result = SetHashStrategy(
            traits=self.traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        if isinstance(other, SetHashStrategy):
            diff = self._set.difference(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            diff = self._set.difference(other_set)
        else:
            diff = self._set.copy()
        for element in diff:
            result.add(self._values[element])
        return result

    def symmetric_difference(self, other: SetHashStrategy | set | list) -> SetHashStrategy:
        """Return symmetric difference of this set with another."""
        result = SetHashStrategy(
            traits=self.traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        if isinstance(other, SetHashStrategy):
            sym_diff = self._set.symmetric_difference(other._set)
            for element in sym_diff:
                if element in self._values:
                    result.add(self._values[element])
                elif element in other._values:
                    result.add(other._values[element])
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            sym_diff = self._set.symmetric_difference(other_set)
            for element in sym_diff:
                if element in self._values:
                    result.add(self._values[element])
                else:
                    # Find original element in other
                    for orig in other:
                        if (str(orig).lower() if not self.case_sensitive else str(orig)) == element:
                            result.add(orig)
                            break
        return result

    def is_subset(self, other: SetHashStrategy | set | list) -> bool:
        """Check if this set is a subset of another."""
        if isinstance(other, SetHashStrategy):
            return self._set.issubset(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            return self._set.issubset(other_set)
        return False

    def is_superset(self, other: SetHashStrategy | set | list) -> bool:
        """Check if this set is a superset of another."""
        if isinstance(other, SetHashStrategy):
            return self._set.issuperset(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            return self._set.issuperset(other_set)
        return False

    def is_disjoint(self, other: SetHashStrategy | set | list) -> bool:
        """Check if this set has no elements in common with another."""
        if isinstance(other, SetHashStrategy):
            return self._set.isdisjoint(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            return self._set.isdisjoint(other_set)
        return True

    def copy(self) -> SetHashStrategy:
        """Create a shallow copy of the set."""
        result = SetHashStrategy(
            traits=self.traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        for element in self._set:
            result.add(self._values[element])
        return result

    def update(self, *others) -> None:
        """Update the set with elements from other iterables."""
        for other in others:
            if isinstance(other, SetHashStrategy):
                for element in other._set:
                    self.add(other._values[element])
            elif isinstance(other, (set, list, tuple)):
                for element in other:
                    self.add(element)

    def get_hash(self) -> str:
        """Get a hash representation of the set."""
        # Sort elements for consistent hashing
        sorted_elements = sorted(self._set)
        content = ''.join(sorted_elements)
        return hashlib.md5(content.encode()).hexdigest()
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'SET_HASH',
            'backend': 'Python set + dict',
            'case_sensitive': self.case_sensitive,
            'allow_none': self.allow_none,
            'complexity': {
                'add': 'O(1) average',
                'remove': 'O(1) average',
                'contains': 'O(1) average',
                'union': 'O(n + m)',
                'intersection': 'O(min(n, m))',
                'space': 'O(n)'
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        collision_estimate = max(0, len(self._values) - len(self._set))
        return {
            'size': self._size,
            'unique_elements': len(self._set),
            'collisions_estimate': collision_estimate,
            'load_factor': self.load_factor,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'hash': self.get_hash()[:8] + "..."
        }
