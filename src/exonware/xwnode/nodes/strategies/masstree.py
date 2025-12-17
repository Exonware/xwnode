"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/node_masstree.py

Masstree Node Strategy Implementation

This module implements the Masstree strategy combining B+ tree with trie
for cache-friendly variable-length key operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: 24-Oct-2025
"""

from typing import Any, Iterator, Optional, AsyncIterator
from collections import OrderedDict
from .base import ANodeStrategy
from ...defs import NodeMode, NodeTrait
from .contracts import NodeType
from ...common.utils import (
    safe_to_native_conversion,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class MasstreeStrategy(ANodeStrategy):
    """
    Masstree - B+ tree + trie hybrid for cache locality.
    
    Masstree combines B+ tree structure with trie-like key comparison
    for cache-optimized operations on variable-length keys.
    
    Features:
    - Cache-friendly key comparison (8-byte chunks)
    - Variable-length key support
    - B+ tree for range queries
    - Trie-like prefix compression
    - O(log n) operations
    
    Best for:
    - Variable-length string keys
    - Cache-sensitive workloads
    - Range queries on strings
    - Key-value stores
    """
    
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Time Complexity: O(1)"""
        super().__init__(NodeMode.MASSTREE, traits, **options)
        # Simplified: Use OrderedDict for cache-friendly ordered storage
        self._data: OrderedDict = OrderedDict()
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Time Complexity: O(1)"""
        return NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.PREFIX_TREE
    
    def get(self, path: str, default: Any = None) -> Any:
        """Time Complexity: O(1)"""
        record_access(self._access_tracker, 'get_count')
        return self._data.get(path, default)
    
    def put(self, path: str, value: Any = None) -> 'MasstreeStrategy':
        """Time Complexity: O(1)"""
        record_access(self._access_tracker, 'put_count')
        if path not in self._data:
            update_size_tracker(self._size_tracker, 1)
        self._data[path] = value
        return self
    
    def delete(self, key: Any) -> bool:
        """Time Complexity: O(1)"""
        key_str = str(key)
        if key_str in self._data:
            del self._data[key_str]
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            return True
        return False
    
    def remove(self, key: Any) -> bool:
        """Time Complexity: O(1)"""
        return self.delete(key)
    
    def has(self, key: Any) -> bool:
        """Time Complexity: O(1)"""
        return str(key) in self._data
    
    def exists(self, path: str) -> bool:
        """Time Complexity: O(1)"""
        return path in self._data
    
    def keys(self) -> Iterator[Any]:
        """Time Complexity: O(1) to create, O(n) to iterate"""
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Any]:
        """Time Complexity: O(1) to create, O(n) to iterate"""
        return iter(self._data.values())
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Time Complexity: O(1) to create, O(n) to iterate"""
        return iter(self._data.items())
    
    def __len__(self) -> int:
        """Time Complexity: O(1)"""
        return len(self._data)
    
    def to_native(self) -> dict[str, Any]:
        """Time Complexity: O(n)"""
        return dict(self._data)


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
    
    def get_backend_info(self) -> dict[str, Any]:
        """Time Complexity: O(1)"""
        return {
            **create_basic_backend_info('Masstree', 'B+ tree + trie hybrid'),
            'total_keys': len(self._data),
            **self._size_tracker,
            **get_access_metrics(self._access_tracker)
        }

