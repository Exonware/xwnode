"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/histogram.py
Histogram Strategy Implementation
Histogram for statistical estimation and selectivity calculation.
Supports both equi-width and equi-depth histogram types.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.18
Generation Date: 27-Oct-2025
"""

from typing import Any
from threading import RLock
import bisect
from .base import ANodeStrategy
from ...defs import NodeMode


class _Bucket:
    """Histogram bucket"""

    def __init__(self, min_val: float, max_val: float, count: int = 0):
        self.min_val = min_val
        self.max_val = max_val
        self.count = count

    def contains(self, value: float) -> bool:
        """Check if value falls in this bucket"""
        return self.min_val <= value < self.max_val

    def overlaps(self, min_val: float, max_val: float) -> bool:
        """Check if range overlaps with this bucket"""
        return not (max_val <= self.min_val or min_val >= self.max_val)


class HistogramStrategy(ANodeStrategy):
    """
    Histogram Strategy for Statistical Estimation
    Supports:
    - Equi-width histograms (equal bucket sizes)
    - Equi-depth histograms (equal frequencies per bucket)
    - Selectivity estimation for range queries
    - Percentile estimation
    - Frequency distribution analysis
    Use cases:
    - Query optimization (selectivity estimation)
    - Data profiling and analysis
    - Statistical summaries
    - Anomaly detection
    Priority alignment:
    - Performance (#4): O(log n) selectivity estimation
    - Usability (#2): Simple add/query interface
    - Extensibility (#5): Support multiple histogram types
    """

    def __init__(
        self,
        mode=None,
        traits=None,
        num_buckets: int = 100,
        histogram_type: str = 'equi-width',
        min_value: float | None = None,
        max_value: float | None = None,
        **kwargs
    ):
        """
        Initialize histogram
        Args:
            num_buckets: Number of buckets
            histogram_type: 'equi-width' or 'equi-depth'
            min_value: Minimum value (auto-detected if None)
            max_value: Maximum value (auto-detected if None)
            mode: NodeMode for this strategy (passed to base)
            traits: NodeTrait for this strategy (passed to base)
            **kwargs: Additional arguments - ignored
        """
        from ...defs import NodeMode, NodeTrait
        # Extract parameters from kwargs if passed by flyweight
        num_buckets = kwargs.pop('num_buckets', num_buckets)
        histogram_type = kwargs.pop('histogram_type', histogram_type)
        min_value = kwargs.pop('min_value', min_value)
        max_value = kwargs.pop('max_value', max_value)
        super().__init__(
            mode=mode or NodeMode.HISTOGRAM,
            traits=traits or NodeTrait.NONE,
            **kwargs
        )
        self._num_buckets = num_buckets
        self._histogram_type = histogram_type
        self._min_value = min_value
        self._max_value = max_value
        # Buckets
        self._buckets: list[_Bucket] = []
        self._total_count = 0
        # Thread safety
        self._lock = RLock()
        # For building histogram (buffer for both types; build() does bucketing)
        self._values: list[float] = []

    def add_value(self, value: float) -> None:
        """
        Add value to histogram
        For both equi-depth and equi-width, values are buffered until build() is called
        Args:
            value: Numeric value to add
        """
        with self._lock:
            self._values.append(value)

    def build(self) -> None:
        """
        Build histogram from collected values
        Must be called after adding all values
        """
        with self._lock:
            if self._histogram_type == 'equi-width':
                self._build_equi_width_buckets()
                self._assign_equi_width_counts()
            else:  # equi-depth
                self._build_equi_depth_buckets()

    def estimate_selectivity(self, min_val: float, max_val: float) -> float:
        """
        Estimate selectivity for range [min_val, max_val]
        Returns fraction of values in range (0.0 to 1.0)
        Args:
            min_val: Range minimum
            max_val: Range maximum
        Returns:
            Estimated selectivity (0.0 to 1.0)
        """
        with self._lock:
            if self._total_count == 0:
                return 0.0
            matching_count = 0
            for bucket in self._buckets:
                if bucket.overlaps(min_val, max_val):
                    # Calculate fraction of bucket that overlaps
                    overlap_min = max(bucket.min_val, min_val)
                    overlap_max = min(bucket.max_val, max_val)
                    overlap_width = overlap_max - overlap_min
                    bucket_width = bucket.max_val - bucket.min_val
                    if bucket_width > 0:
                        fraction = overlap_width / bucket_width
                        matching_count += bucket.count * fraction
                    else:
                        matching_count += bucket.count
            return matching_count / self._total_count

    def get_percentile(self, p: float) -> float | None:
        """
        Get p-th percentile
        Args:
            p: Percentile (0.0 to 1.0), e.g., 0.5 for median
        Returns:
            Estimated percentile value
        """
        with self._lock:
            if self._total_count == 0:
                return None
            target_count = p * self._total_count
            cumulative_count = 0
            for bucket in self._buckets:
                cumulative_count += bucket.count
                if cumulative_count >= target_count:
                    # Interpolate within bucket
                    bucket_fraction = (target_count - (cumulative_count - bucket.count)) / bucket.count
                    return bucket.min_val + bucket_fraction * (bucket.max_val - bucket.min_val)
            return self._max_value

    def get_buckets(self) -> list[tuple[float, float, int]]:
        """
        Get bucket information
        Returns:
            List of (min, max, count) tuples
        """
        with self._lock:
            return [(b.min_val, b.max_val, b.count) for b in self._buckets]

    def get_total_count(self) -> int:
        """Get total number of values added"""
        with self._lock:
            return self._total_count

    def _build_equi_width_buckets(self) -> None:
        """Build equi-width bucket boundaries from buffered values."""
        if not self._values:
            return
        self._min_value = min(self._values)
        self._max_value = max(self._values)
        self._total_count = len(self._values)
        self._buckets = []
        range_width = self._max_value - self._min_value
        if range_width == 0:
            # All values are the same
            self._buckets = [_Bucket(self._min_value, self._min_value + 1, self._total_count)]
            return
        bucket_width = range_width / self._num_buckets
        for i in range(self._num_buckets):
            min_val = self._min_value + i * bucket_width
            max_val = self._min_value + (i + 1) * bucket_width
            self._buckets.append(_Bucket(min_val, max_val, 0))

    def _assign_equi_width_counts(self) -> None:
        """Assign buffered values to equi-width buckets (call after _build_equi_width_buckets)."""
        for value in self._values:
            for bucket in self._buckets:
                if bucket.contains(value):
                    bucket.count += 1
                    break

    def _build_equi_depth_buckets(self) -> None:
        """Build equi-depth histogram (equal frequencies per bucket)"""
        if not self._values:
            return
        # Sort values
        sorted_values = sorted(self._values)
        self._total_count = len(sorted_values)
        values_per_bucket = max(1, self._total_count // self._num_buckets)
        self._buckets = []
        for i in range(0, self._total_count, values_per_bucket):
            bucket_values = sorted_values[i:i + values_per_bucket]
            if bucket_values:
                min_val = bucket_values[0]
                max_val = bucket_values[-1] + 0.001  # Slightly larger for inclusive range
                count = len(bucket_values)
                self._buckets.append(_Bucket(min_val, max_val, count))
        # Set min/max
        if sorted_values:
            self._min_value = sorted_values[0]
            self._max_value = sorted_values[-1]
    # ANodeStrategy interface implementation

    def get_mode(self) -> NodeMode:
        """Get the node mode for this strategy"""
        return NodeMode.HISTOGRAM

    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported"""
        supported = {
            'add_value', 'build', 'estimate_selectivity',
            'get_percentile', 'get_buckets', 'get_total_count'
        }
        return operation in supported

    def get_complexity(self, operation: str) -> str:
        """Get time complexity for operation"""
        complexities = {
            'add_value': 'O(1)' if self._histogram_type == 'equi-depth' else 'O(b)',
            'build': 'O(n log n)' if self._histogram_type == 'equi-depth' else 'O(1)',
            'estimate_selectivity': 'O(b)',
            'get_percentile': 'O(b)',
        }
        return complexities.get(operation, 'O(b)')  # b = number of buckets
    # Required abstract methods from ANodeStrategy

    def put(self, key: Any, value: Any = None) -> None:
        """Not applicable for histogram - use add_value() instead"""
        raise NotImplementedError("Use add_value() for histogram operations")

    def get(self, key: Any, default: Any = None) -> Any:
        """Not applicable for histogram"""
        return default

    def has(self, key: Any) -> bool:
        """Not applicable for histogram"""
        return False

    def delete(self, key: Any) -> bool:
        """Not applicable for histogram"""
        return False

    def keys(self):
        """Get iterator over bucket indices"""
        with self._lock:
            return iter(range(len(self._buckets)))

    def values(self):
        """Get iterator over bucket counts"""
        with self._lock:
            return iter(b.count for b in self._buckets)

    def items(self):
        """Get iterator over (index, bucket_info) pairs"""
        with self._lock:
            return iter((i, (b.min_val, b.max_val, b.count)) for i, b in enumerate(self._buckets))

    def __len__(self) -> int:
        """Get number of buckets"""
        with self._lock:
            return len(self._buckets)

    def to_native(self) -> Any:
        """Convert histogram to native Python dict"""
        with self._lock:
            return {
                'type': self._histogram_type,
                'num_buckets': self._num_buckets,
                'total_count': self._total_count,
                'min_value': self._min_value,
                'max_value': self._max_value,
                'buckets': [(b.min_val, b.max_val, b.count) for b in self._buckets]
            }
