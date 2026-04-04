"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/range_map.py
Range Map Strategy Implementation
Non-overlapping range→value mapping with O(log n) lookups.
Simpler than INTERVAL_TREE when ranges don't overlap.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.21
Generation Date: 27-Oct-2025
"""

from typing import Any
from threading import RLock
import bisect
from .base import ANodeStrategy
from ...defs import NodeMode


class _Range:
    """Non-overlapping range with associated value"""

    def __init__(self, start: float, end: float, value: Any):
        self.start = start
        self.end = end
        self.value = value

    def contains(self, point: float) -> bool:
        """Check if point is in range [start, end)"""
        return self.start <= point < self.end

    def __repr__(self):
        return f"Range([{self.start}, {self.end}), value={self.value})"


class RangeMapStrategy(ANodeStrategy):
    """
    Range Map Strategy for Non-Overlapping Range Queries
    Maps non-overlapping ranges to values with O(log n) lookup using binary search.
    Simpler than INTERVAL_TREE when ranges are guaranteed not to overlap.
    Use cases:
    - Cost model range mappings (row count → cost factor)
    - Category mappings (age groups, price tiers)
    - Piecewise functions
    - Configuration ranges
    Priority alignment:
    - Performance (#4): O(log n) lookups with binary search
    - Usability (#2): Simple put/get interface
    - Maintainability (#3): Cleaner than custom range logic
    """

    def __init__(self, mode=None, traits=None, **kwargs):
        """
        Initialize range map
        Args:
            mode: NodeMode for this strategy (passed to base)
            traits: NodeTrait for this strategy (passed to base)
            **kwargs: Additional arguments - ignored
        """
        from ...defs import NodeMode, NodeTrait
        super().__init__(
            mode=mode or NodeMode.RANGE_MAP,
            traits=traits or NodeTrait.NONE,
            **kwargs
        )
        # Sorted list of ranges for binary search
        self._ranges: list[_Range] = []
        # Thread safety
        self._lock = RLock()

    def put(self, start: float, end: float, value: Any) -> None:
        """
        Add range with associated value
        Maintains sorted order for binary search
        Assumes ranges don't overlap (undefined behavior if they do)
        Args:
            start: Range start (inclusive)
            end: Range end (exclusive)
            value: Value to associate with this range
        """
        with self._lock:
            if start >= end:
                raise ValueError(f"Invalid range: start ({start}) must be < end ({end})")
            new_range = _Range(start, end, value)
            # Insert in sorted order (by start value)
            if not self._ranges:
                self._ranges.append(new_range)
            else:
                # Find insertion point
                insert_pos = bisect.bisect_left([r.start for r in self._ranges], start)
                self._ranges.insert(insert_pos, new_range)

    def get(self, point: float) -> Any | None:
        """
        Get value for point
        O(log n) lookup using binary search
        Args:
            point: Point to query
        Returns:
            Value associated with range containing point, or None
        """
        with self._lock:
            if not self._ranges:
                return None
            # Binary search for range containing point
            left, right = 0, len(self._ranges)
            while left < right:
                mid = (left + right) // 2
                range_obj = self._ranges[mid]
                if range_obj.contains(point):
                    return range_obj.value
                elif point < range_obj.start:
                    right = mid
                else:
                    left = mid + 1
            return None

    def get_range_for_point(self, point: float) -> tuple[float, float, Any] | None:
        """
        Get complete range information for point
        Args:
            point: Point to query
        Returns:
            (start, end, value) tuple or None
        """
        with self._lock:
            if not self._ranges:
                return None
            left, right = 0, len(self._ranges)
            while left < right:
                mid = (left + right) // 2
                range_obj = self._ranges[mid]
                if range_obj.contains(point):
                    return (range_obj.start, range_obj.end, range_obj.value)
                elif point < range_obj.start:
                    right = mid
                else:
                    left = mid + 1
            return None

    def get_all_ranges(self) -> list[tuple[float, float, Any]]:
        """
        Get all ranges
        Returns:
            List of (start, end, value) tuples
        """
        with self._lock:
            return [(r.start, r.end, r.value) for r in self._ranges]

    def delete(self, start: float, end: float) -> bool:
        """
        Delete range
        Args:
            start: Range start
            end: Range end
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            for i, range_obj in enumerate(self._ranges):
                if range_obj.start == start and range_obj.end == end:
                    del self._ranges[i]
                    return True
            return False

    def clear(self) -> None:
        """Clear all ranges"""
        with self._lock:
            self._ranges.clear()

    def get_size(self) -> int:
        """Get number of ranges"""
        with self._lock:
            return len(self._ranges)
    # ANodeStrategy interface implementation

    def get_mode(self) -> NodeMode:
        """Get the node mode for this strategy"""
        return NodeMode.RANGE_MAP

    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported"""
        supported = {
            'put', 'get', 'get_range_for_point',
            'get_all_ranges', 'delete', 'clear', 'size'
        }
        return operation in supported

    def get_complexity(self, operation: str) -> str:
        """Get time complexity for operation"""
        complexities = {
            'put': 'O(log n)',
            'get': 'O(log n)',
            'get_range_for_point': 'O(log n)',
            'delete': 'O(n)',
            'clear': 'O(1)',
        }
        return complexities.get(operation, 'O(log n)')
    # Required abstract methods from ANodeStrategy

    def has(self, key: Any) -> bool:
        """Check if range exists"""
        with self._lock:
            return key in self._ranges

    def keys(self):
        """Get iterator over range start values"""
        with self._lock:
            return iter(r.start for r in self._ranges)

    def values(self):
        """Get iterator over range values"""
        with self._lock:
            return iter(r.value for r in self._ranges)

    def items(self):
        """Get iterator over ((start, end), value) pairs"""
        with self._lock:
            return iter(((r.start, r.end), r.value) for r in self._ranges)

    def __len__(self) -> int:
        """Get number of ranges"""
        with self._lock:
            return len(self._ranges)

    def to_native(self) -> Any:
        """Convert range map to native Python dict"""
        with self._lock:
            return {
                'ranges': [(r.start, r.end, r.value) for r in self._ranges]
            }
