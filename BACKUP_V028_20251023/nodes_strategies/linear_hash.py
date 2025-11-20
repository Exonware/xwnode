"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/node_linear_hash.py

Linear Hash Node Strategy Implementation

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.26
Generation Date: 11-Oct-2025
"""

from typing import Any, Iterator, Dict
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


class LinearHashStrategy(ANodeStrategy):
    """
    Linear Hash - Linear dynamic hashing without directory.
    
    Time Complexity: O(1) for get/put/delete operations
    """
    
    STRATEGY_TYPE = NodeType.TREE
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Time Complexity: O(1)"""
        super().__init__(NodeMode.LINEAR_HASH, traits, **options)
        self._data: Dict[str, Any] = {}
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Time Complexity: O(1)"""
        return NodeTrait.INDEXED
    
    def get(self, path: str, default: Any = None) -> Any:
        """Time Complexity: O(1)"""
        record_access(self._access_tracker, 'get_count')
        return self._data.get(path, default)
    
    def put(self, path: str, value: Any = None) -> 'LinearHashStrategy':
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
    
    def to_native(self) -> Dict[str, Any]:
        """Time Complexity: O(n)"""
        return dict(self._data)
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Time Complexity: O(1)"""
        return {
            **create_basic_backend_info('Linear Hash', 'Linear dynamic hashing'),
            'total_keys': len(self._data),
            **self._size_tracker,
            **get_access_metrics(self._access_tracker)
        }

