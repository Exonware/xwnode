"""
Array List Node Strategy Implementation

This module implements the ARRAY_LIST strategy for sequential data
with fast indexed access.
"""

from typing import Any, Iterator, List, Union, Dict
from .base import ANodeLinearStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class ArrayListStrategy(ANodeLinearStrategy):
    """
    Array List node strategy for sequential data with O(1) indexed access.
    
    Uses Python's built-in list for optimal performance with indexed operations.
    
    # Strategy type classification
    STRATEGY_TYPE = NodeType.LINEAR
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the array list strategy.
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.ARRAY_LIST, traits, **options)
        self._data: List[Any] = []
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the array list strategy.
        
        Time Complexity: O(1)
        """
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """
        Store a value at index (key must be numeric).
        
        Time Complexity: O(1) if within capacity, O(n) if needs extension
        Space Complexity: O(n) if extending array
        """
        try:
            index = int(key)
        except (ValueError, TypeError):
            raise TypeError(f"Array list requires numeric indices, got {type(key).__name__}")
        
        # Extend list if necessary
        while len(self._data) <= index:
            self._data.append(None)
            
        if self._data[index] is None:
            self._size += 1
        self._data[index] = value
    
    def find(self, key: Any) -> Any:
        """
        Retrieve a value by index.
        
        Time Complexity: O(1)
        """
        try:
            index = int(key)
            if 0 <= index < len(self._data):
                value = self._data[index]
                return value if value is not None else None
            return None
        except (ValueError, TypeError):
            return None
    
    def delete(self, key: Any) -> bool:
        """
        Remove value at index.
        
        Time Complexity: O(1)
        """
        try:
            index = int(key)
            if 0 <= index < len(self._data) and self._data[index] is not None:
                self._data[index] = None
                self._size -= 1
                return True
            return False
        except (ValueError, TypeError):
            return False
    
    def size(self) -> int:
        """
        Get the number of non-None items.
        
        Time Complexity: O(1)
        """
        return self._size
    
    def is_empty(self) -> bool:
        """
        Check if structure is empty.
        
        Time Complexity: O(1)
        """
        return self._size == 0
    
    def to_native(self) -> List[Any]:
        """
        Convert to native Python list.
        
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        # Return only non-None values in order
        return [value for value in self._data if value is not None]
    
    def __len__(self) -> int:
        """
        Get the number of items.
        
        Time Complexity: O(1)
        """
        return len(self._data)
    
    def has(self, key: Any) -> bool:
        """
        Check if value exists in array.
        
        Time Complexity: O(n) - linear search
        """
        return key in self._data
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get value by index or search for value.
        
        Time Complexity: O(1) for index, O(n) for value search
        """
        try:
            index = int(key)
            if 0 <= index < len(self._data):
                return self._data[index]
        except (ValueError, TypeError):
            if key in self._data:
                return key
        return default
    
    def put(self, key: Any, value: Any = None) -> None:
        """
        Append value to array.
        
        Time Complexity: O(1) amortized, O(n) if needs extension
        """
        self.insert(key, value if value is not None else key)
    
    def keys(self) -> Iterator[Any]:
        """
        Get all indices.
        
        Time Complexity: O(1) to create iterator, O(n) to iterate all
        """
        return iter(range(len(self._data)))
    
    def values(self) -> Iterator[Any]:
        """
        Get all values.
        
        Time Complexity: O(1) to create iterator, O(n) to iterate all
        """
        return iter(self._data)
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """
        Get all items as (index, value) pairs.
        
        Time Complexity: O(1) to create iterator, O(n) to iterate all
        """
        return enumerate(self._data)
    
    # ============================================================================
    # LINEAR STRATEGY METHODS
    # ============================================================================
    
    def push_front(self, value: Any) -> None:
        """
        Add element to front.
        
        Time Complexity: O(n) - shifts all elements
        """
        self._data.insert(0, value)
        self._size += 1
    
    def push_back(self, value: Any) -> None:
        """
        Add element to back.
        
        Time Complexity: O(1) amortized
        """
        self._data.append(value)
        self._size += 1
    
    def pop_front(self) -> Any:
        """
        Remove element from front.
        
        Time Complexity: O(n) - shifts all elements
        """
        if not self._data:
            raise IndexError("pop from empty list")
        value = self._data.pop(0)
        self._size -= 1
        return value
    
    def pop_back(self) -> Any:
        """
        Remove element from back.
        
        Time Complexity: O(1)
        """
        if not self._data:
            raise IndexError("pop from empty list")
        value = self._data.pop()
        self._size -= 1
        return value
    
    def get_at_index(self, index: int) -> Any:
        """
        Get element at index.
        
        Time Complexity: O(1)
        """
        if 0 <= index < len(self._data):
            return self._data[index]
        raise IndexError("list index out of range")
    
    def set_at_index(self, index: int, value: Any) -> None:
        """
        Set element at index.
        
        Time Complexity: O(1)
        """
        if 0 <= index < len(self._data):
            self._data[index] = value
        else:
            raise IndexError("list index out of range")
    
    # ============================================================================
    # AUTO-3 Phase 1 methods
    # ============================================================================
    
    def as_linked_list(self):
        """
        Provide LinkedList behavioral view.
        
        Time Complexity: O(1)
        """
        # TODO: Implement LinkedList view
        return self
    
    def as_stack(self):
        """
        Provide Stack behavioral view.
        
        Time Complexity: O(1)
        """
        # TODO: Implement Stack view
        return self
    
    def as_queue(self):
        """
        Provide Queue behavioral view.
        
        Time Complexity: O(1)
        """
        # TODO: Implement Queue view
        return self
    
    def as_deque(self):
        """
        Provide Deque behavioral view.
        
        Time Complexity: O(1)
        """
        # TODO: Implement Deque view
        return self
    
    # ============================================================================
    # ARRAY-SPECIFIC OPERATIONS
    # ============================================================================
    
    def append(self, value: Any) -> None:
        """
        Append a value to the end.
        
        Time Complexity: O(1) amortized
        """
        self._data.append(value)
        self._size += 1
    
    def insert_at(self, index: int, value: Any) -> None:
        """
        Insert a value at the specified index.
        
        Time Complexity: O(n) - shifts elements after index
        """
        self._data.insert(index, value)
        self._size += 1
    
    def pop_at(self, index: int = -1) -> Any:
        """
        Remove and return value at index.
        
        Time Complexity: O(1) for end, O(n) for middle/start
        """
        if not self._data:
            raise IndexError("pop from empty list")
        value = self._data.pop(index)
        if value is not None:
            self._size -= 1
        return value
    
    def extend(self, values: List[Any]) -> None:
        """
        Extend with multiple values.
        
        Time Complexity: O(k) where k is len(values)
        """
        self._data.extend(values)
        self._size += len(values)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """
        Get backend implementation info.
        
        Time Complexity: O(1)
        """
        return {
            'strategy': 'ARRAY_LIST',
            'backend': 'Python list',
            'complexity': {
                'get': 'O(1)',
                'put': 'O(1) amortized',
                'append': 'O(1) amortized',
                'insert': 'O(n)',
                'pop': 'O(1) end, O(n) middle'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Time Complexity: O(1)
        """
        return {
            'size': self._size,
            'capacity': len(self._data),
            'memory_usage': f"{len(self._data) * 8} bytes (estimated)",
            'utilization': f"{(self._size / max(1, len(self._data))) * 100:.1f}%"
        }
