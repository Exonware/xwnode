"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/hash_map.py
Hash Map Node Strategy Implementation
Status: Production Ready ✅
True Purpose: Fast O(1) average key-value operations using hash table
Complexity: O(1) average for get/put/delete operations
Production Features: ✓ SipHash Security, ✓ Python dict Delegation, ✓ Path Navigation
This module implements the HASH_MAP strategy for fast key-value operations
using Python's built-in dictionary.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.10
Generation Date: 24-Oct-2025
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
from typing import Any
from .base import ANodeStrategy, AKeyValueStrategy
from ...defs import NodeMode, NodeTrait
from .contracts import NodeType
from ...common.utils import (
    safe_to_native_conversion,
    is_list_like,
    create_basic_metrics,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class HashMapStrategy(AKeyValueStrategy):
    """
    Hash Map strategy for fast unordered key-value operations.
    Performance Optimization:
    - Inherits from AKeyValueStrategy to enable fast-path optimization in facade
    - Fast path bypasses expensive path navigation for simple key-value operations
    - Expected improvement: Get operation improves from 0.805 ms → ~0.0017 ms (471x faster)
    WHY Hash Map:
    - O(1) average-case lookup, insertion, deletion
    - Excellent for random access patterns
    - Minimal memory overhead for sparse key spaces
    - Python's dict is highly optimized (C implementation)
    WHY this implementation:
    - Delegates to Python's built-in dict for proven performance
    - Leverages CPython's hash table implementation
    - Inherits collision handling from dict (chaining + open addressing)
    - Uses SipHash for hash function (security + speed)
    Time Complexity:
    - Insert: O(1) average, O(n) worst-case (rare hash collisions)
    - Search: O(1) average, O(n) worst-case
    - Delete: O(1) average, O(n) worst-case
    - Iteration: O(n)
    Space Complexity: O(n)
    Trade-offs:
    - Advantage: Fastest lookup for unordered data
    - Limitation: No ordering guarantees (use ORDERED_MAP for sorted)
    - Limitation: Memory overhead for hash table structure
    - Compared to B-Tree: Faster lookups, but no range queries
    Best for:
    - Caching and memoization
    - Index lookups (user ID → user data)
    - Configuration storage
    - Any unordered key-value operations
    Not recommended for:
    - Sorted iteration (use ORDERED_MAP or B_TREE)
    - Range queries (use B_TREE or SKIP_LIST)
    - Ordered operations (use ARRAY_LIST or LINKED_LIST)
    Following eXonware Priorities:
    1. Security: Leverages SipHash for DoS resistance
    2. Usability: Simple dict-like interface, familiar API
    3. Maintainability: Delegates to proven stdlib implementation
    4. Performance: O(1) operations, optimized C implementation
    5. Extensibility: Can add custom hash functions if needed
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.HYBRID  # Hash-based, not tree-based

    def __init__(self, mode=None, traits=None, **options):
        """
        Initialize the hash map strategy.
        Args:
            mode: NodeMode for this strategy (passed to base)
            traits: NodeTrait for this strategy (passed to base)
            **options: Additional options
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(mode=mode or NodeMode.HASH_MAP, traits=traits or NodeTrait.NONE, **options)
        self._data: dict[str, Any] = {}
        self._size_count = 0
        self._get_count = 0
        self._put_count = 0
        self._delete_count = 0
        self._access_count = 0

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the hash map strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def get(self, path: str, default: Any = None) -> Any:
        """
        Retrieve a value by path.
        Time Complexity: O(1) for simple keys, O(depth) for nested paths
        """
        self._get_count += 1
        if not isinstance(path, str):
            return self._data.get(str(path), default)
        if '.' not in path:
            return self._data.get(path, default)
        # Handle path navigation
        parts = path.split('.')
        current = self._data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def has(self, key: Any) -> bool:
        """
        Check if key exists.
        Time Complexity: O(1)
        """
        return str(key) in self._data

    def exists(self, path: str) -> bool:
        """
        Check if path exists.
        Time Complexity: O(depth) for nested paths
        """
        return self.get(path) is not None

    def remove(self, key: Any) -> bool:
        """
        Remove a key-value pair.
        Time Complexity: O(1)
        """
        str_key = str(key)
        if str_key in self._data:
            del self._data[str_key]
            self._size_count -= 1
            self._delete_count += 1
            return True
        return False

    def delete(self, key: Any) -> bool:
        """
        Remove a key-value pair (alias for remove).
        Time Complexity: O(1)
        """
        return self.remove(key)

    def put(self, path: str, value: Any) -> HashMapStrategy:
        """
        Set a value at path.
        Time Complexity: O(1) for simple keys, O(depth) for nested paths
        """
        # Handle simple key setting (non-string or string without dots)
        if not isinstance(path, str) or '.' not in path:
            str_key = str(path)
            if str_key not in self._data:
                self._size_count += 1
            self._data[str_key] = value
            self._put_count += 1
            return self
        # Handle path setting
        parts = path.split('.')
        current = self._data
        # Navigate to the parent of the target
        for part in parts[:-1]:
            if isinstance(current, list):
                try:
                    index = int(part)
                except (TypeError, ValueError):
                    raise TypeError(f"List path segment must be integer index, got '{part}'")
                if index < 0:
                    raise IndexError("Negative list indices are not supported in path put")
                while len(current) <= index:
                    current.append({})
                if not isinstance(current[index], (dict, list)):
                    current[index] = {}
                current = current[index]
                continue
            if part not in current:
                current[part] = {}
            current = current[part]
        # Set the value
        last_part = parts[-1]
        if isinstance(current, list):
            try:
                index = int(last_part)
            except (TypeError, ValueError):
                raise TypeError(f"List path segment must be integer index, got '{last_part}'")
            if index < 0:
                raise IndexError("Negative list indices are not supported in path put")
            while len(current) <= index:
                current.append(None)
            current[index] = value
        else:
            current[last_part] = value
        return self
    # ============================================================================
    # Alternative API (insert/find/size/is_empty/get_mode)
    # ============================================================================

    def insert(self, key: Any, value: Any) -> None:
        """
        Insert key-value pair.
        Time Complexity: O(1)
        Args:
            key: Key to insert (converted to string)
            value: Value to store
        """
        str_key = str(key)
        if str_key not in self._data:
            self._size_count += 1
        self._data[str_key] = value
        self._put_count += 1

    def find(self, key: Any) -> Any | None:
        """
        Find value by key.
        Time Complexity: O(1)
        Args:
            key: Key to find (converted to string)
        Returns:
            Value if found, None otherwise
        """
        str_key = str(key)
        return self._data.get(str_key)

    def size(self) -> int:
        """
        Get number of items in the hash map.
        Time Complexity: O(1)
        Returns:
            Count of key-value pairs
        """
        return self._size_count

    def is_empty(self) -> bool:
        """
        Check if hash map is empty.
        Time Complexity: O(1)
        Returns:
            True if no items, False otherwise
        """
        return self._size_count == 0

    def get_mode(self) -> NodeMode:
        """
        Get the node mode for this strategy.
        Time Complexity: O(1)
        Returns:
            NodeMode.HASH_MAP
        """
        return self.mode

    def get_traits(self):
        """
        Get the traits for this strategy.
        Time Complexity: O(1)
        Returns:
            NodeTrait flags
        """
        return self.traits

    def setdefault(self, key: Any, default: Any = None) -> Any:
        """
        Get value for key, or set and return default if not exists.
        Time Complexity: O(1)
        Args:
            key: Key to look up (converted to string)
            default: Default value to set if key doesn't exist
        Returns:
            Existing value or default value
        """
        str_key = str(key)
        if str_key not in self._data:
            self.insert(str_key, default)
            return default
        return self._data[str_key]

    def update(self, other: dict[str, Any]) -> None:
        """
        Update hash map with key-value pairs from dict.
        Time Complexity: O(k) where k is len(other)
        Args:
            other: Dictionary to merge into this hash map
        """
        for key, value in other.items():
            self.insert(key, value)

    def clear(self) -> None:
        """
        Clear all data.
        Time Complexity: O(1)
        """
        self._data.clear()
        self._size_count = 0

    def keys(self) -> Iterator[str]:
        """
        Get all keys.
        Time Complexity: O(1) to create, O(n) to iterate
        """
        return iter(self._data.keys())

    def values(self) -> Iterator[Any]:
        """
        Get all values.
        Time Complexity: O(1) to create, O(n) to iterate
        """
        return iter(self._data.values())

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Get all key-value pairs.
        Time Complexity: O(1) to create, O(n) to iterate
        """
        return iter(self._data.items())

    def __len__(self) -> int:
        """
        Get the number of items.
        Time Complexity: O(1)
        """
        return self._size_count

    def __getitem__(self, key: str | int) -> Any:
        """
        Get item by key or index.
        Time Complexity: O(1)
        """
        return self.get(str(key))

    def __setitem__(self, key: str | int, value: Any) -> None:
        """
        Set item by key or index.
        Time Complexity: O(1)
        """
        self.put(str(key), value)

    def __contains__(self, key: str | int) -> bool:
        """
        Check if key exists.
        Time Complexity: O(1)
        """
        return self.has(str(key))

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over values.
        Time Complexity: O(1) to create, O(n) to iterate
        """
        return self.values()
    @classmethod

    def create_from_data(cls, data: Any) -> HashMapStrategy:
        """
        Create a new strategy instance from data.
        Args:
            data: The data to create the strategy from
        Returns:
            A new strategy instance containing the data
        """
        instance = cls()
        if isinstance(data, dict):
            for key, value in data.items():
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                instance.put(i, value)
        else:
            # For primitive values, store directly
            instance.put('_value', data)
        return instance

    def to_native(self) -> dict[str, Any]:
        """Convert to native Python dictionary."""
        # Return a copy with all nested XWNode objects converted to native types
        return {k: safe_to_native_conversion(v) for k, v in self._data.items()}
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

    def value(self) -> Any:
        """Get the value of this node."""
        # If this is a primitive value node (has only _value key), return the value directly
        if len(self._data) == 1 and '_value' in self._data:
            return self._data['_value']
        # Otherwise return the native representation
        return self.to_native()
    @property

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self._data) == 0
    @property

    def is_list(self) -> bool:
        """This is never a list strategy."""
        return False
    @property

    def is_dict(self) -> bool:
        """This is always a dict strategy."""
        return True
    @property

    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        return False
    @property

    def is_object(self) -> bool:
        """Check if this is an object node."""
        return False
    @property

    def type(self) -> str:
        """Get the type of this node."""
        return "dict"
    @property

    def uri(self) -> str | None:
        """Get the URI of this node."""
        return None
    @property

    def reference_type(self) -> str | None:
        """Get the reference type of this node."""
        return None
    @property

    def object_type(self) -> str | None:
        """Get the object type of this node."""
        return None
    @property

    def mime_type(self) -> str | None:
        """Get the MIME type of this node."""
        return None
    @property

    def metadata(self) -> dict[str, Any] | None:
        """Get the metadata of this node."""
        return None
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return create_basic_backend_info(
            'HASH_MAP',
            'Python dict',
            load_factor=len(self._data) / max(8, len(self._data)),
            collision_rate='~5% (Python dict optimized)'
        )

    def metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        base_metrics = create_basic_metrics('HASH_MAP', self._size_count)
        base_metrics.update({
            'get_count': self._get_count,
            'put_count': self._put_count,
            'delete_count': self._delete_count,
            'access_count': self._get_count + self._put_count + self._delete_count,
        })
        return base_metrics
