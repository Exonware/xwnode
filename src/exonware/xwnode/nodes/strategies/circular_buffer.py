"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/circular_buffer.py
Circular Buffer Strategy Implementation
Fixed-size ring buffer with automatic overwrite of oldest entries.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.21
Generation Date: 27-Oct-2025
"""

from typing import Any
from threading import RLock
from .base import ANodeStrategy
from ...defs import NodeMode


class CircularBufferStrategy(ANodeStrategy):
    """
    Circular Buffer Strategy for Fixed-Size Ring Buffer
    O(1) append (overwrites oldest when full)
    O(1) access by index
    Use cases:
    - Recent query history tracking
    - Sliding window statistics
    - Event logging with size limits
    - Streaming data with fixed memory
    Priority alignment:
    - Performance (#4): O(1) append and access
    - Usability (#2): Simple append/get interface
    - Maintainability (#3): Clean fixed-size buffer implementation
    """

    def __init__(self, mode=None, traits=None, capacity: int = 1000, **kwargs):
        """
        Initialize circular buffer
        Args:
            mode: NodeMode for this strategy (passed to base)
            traits: NodeTrait for this strategy (passed to base)
            capacity: Maximum number of elements
            **kwargs: Additional arguments
        """
        from ...defs import NodeMode, NodeTrait
        # Extract capacity from kwargs if passed by flyweight (overrides default)
        final_capacity = kwargs.pop('capacity', capacity)
        super().__init__(
            mode=mode or NodeMode.CIRCULAR_BUFFER,
            traits=traits or NodeTrait.NONE,
            **kwargs
        )
        self._capacity = final_capacity
        self._buffer: list[Any | None] = [None] * final_capacity
        self._head = 0  # Next write position
        self._size = 0  # Current number of elements
        # Thread safety
        self._lock = RLock()

    def append(self, value: Any) -> None:
        """
        Append value to buffer (O(1))
        Overwrites oldest value when buffer is full
        Args:
            value: Value to append
        """
        with self._lock:
            self._buffer[self._head] = value
            self._head = (self._head + 1) % self._capacity
            if self._size < self._capacity:
                self._size += 1

    def get(self, index: int) -> Any | None:
        """
        Get value at index (O(1))
        Index 0 is the oldest value, index (size-1) is the newest
        Args:
            index: Index (0 to size-1)
        Returns:
            Value at index or None if invalid index
        """
        with self._lock:
            if index < 0 or index >= self._size:
                return None
            # Calculate actual buffer position
            # Oldest item is at (head - size) % capacity
            oldest_pos = (self._head - self._size) % self._capacity
            actual_pos = (oldest_pos + index) % self._capacity
            return self._buffer[actual_pos]

    def get_recent(self, n: int) -> list[Any]:
        """
        Get n most recent items
        Args:
            n: Number of recent items to get
        Returns:
            List of recent items (newest first)
        """
        with self._lock:
            n = min(n, self._size)
            result = []
            for i in range(n):
                # Most recent is at (head - 1)
                pos = (self._head - 1 - i) % self._capacity
                result.append(self._buffer[pos])
            return result

    def get_all(self) -> list[Any]:
        """
        Get all items in order (oldest to newest)
        Returns:
            List of all items
        """
        with self._lock:
            result = []
            for i in range(self._size):
                result.append(self.get(i))
            return result

    def clear(self) -> None:
        """Clear all entries"""
        with self._lock:
            self._buffer = [None] * self._capacity
            self._head = 0
            self._size = 0

    def get_size(self) -> int:
        """Get current number of elements"""
        with self._lock:
            return self._size

    def get_capacity(self) -> int:
        """Get buffer capacity"""
        return self._capacity

    def is_full(self) -> bool:
        """Check if buffer is full"""
        with self._lock:
            return self._size >= self._capacity

    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        with self._lock:
            return self._size == 0
    # ANodeStrategy interface implementation

    def get_mode(self) -> NodeMode:
        """Get the node mode for this strategy"""
        return NodeMode.CIRCULAR_BUFFER

    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported"""
        supported = {
            'append', 'get', 'get_recent', 'get_all',
            'clear', 'size', 'capacity', 'is_full', 'is_empty'
        }
        return operation in supported

    def get_complexity(self, operation: str) -> str:
        """Get time complexity for operation"""
        return "O(1)"  # All operations are O(1)
    # Required abstract methods from ANodeStrategy

    def put(self, key: Any, value: Any = None) -> None:
        """Not applicable for circular buffer - use append() instead"""
        raise NotImplementedError("Use append() for circular buffer operations")

    def delete(self, key: Any) -> bool:
        """Not applicable for circular buffer - use clear() to reset"""
        return False

    def has(self, key: Any) -> bool:
        """Check if index exists"""
        with self._lock:
            return 0 <= key < self._size

    def keys(self):
        """Get iterator over buffer indices"""
        with self._lock:
            return iter(range(self._size))

    def values(self):
        """Get iterator over buffer values"""
        with self._lock:
            # Iterate from oldest to newest
            idx = self._head
            for _ in range(self._size):
                yield self._buffer[idx]
                idx = (idx + 1) % self._capacity

    def items(self):
        """Get iterator over (index, value) pairs"""
        with self._lock:
            for i in range(self._size):
                yield (i, self.get(i))

    def __len__(self) -> int:
        """Get number of elements in buffer"""
        with self._lock:
            return self._size

    def to_native(self) -> Any:
        """Convert circular buffer to native Python list"""
        with self._lock:
            result = []
            idx = self._head
            for _ in range(self._size):
                result.append(self._buffer[idx])
                idx = (idx + 1) % self._capacity
            return result
