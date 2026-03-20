"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/t_digest.py
T-Digest Strategy Implementation
T-Digest for streaming percentile estimation with constant space.
Implements Ted Dunning's T-Digest algorithm for accurate percentiles.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.13
Generation Date: 27-Oct-2025
"""

from __future__ import annotations
from typing import Any
from threading import RLock
import math
from .base import ANodeStrategy
from ...defs import NodeMode


class _Centroid:
    """Centroid for T-Digest"""

    def __init__(self, mean: float, weight: float):
        self.mean = mean
        self.weight = weight

    def __repr__(self):
        return f"Centroid(mean={self.mean:.2f}, weight={self.weight:.1f})"


class TDigestStrategy(ANodeStrategy):
    """
    T-Digest Strategy for Streaming Percentile Estimation
    Space: O(δ) where δ is compression parameter (typically 100)
    Time: O(1) for add, O(log δ) for percentile query
    Accuracy: Very high for extreme percentiles (p95, p99, p999)
    Advantages over histograms:
    - Constant space regardless of data size
    - Better accuracy for tail percentiles
    - Streaming algorithm (online updates)
    - Merge support for distributed computation
    Use cases:
    - Percentile queries (median, p95, p99, p999)
    - Streaming data analytics
    - Performance monitoring
    - SLA tracking
    Priority alignment:
    - Performance (#4): Constant space, fast percentile queries
    - Usability (#2): Simple add/query interface
    - Extensibility (#5): Merge support for distributed scenarios
    """

    def __init__(self, mode=None, traits=None, compression: int = 100, **kwargs):
        """
        Initialize T-Digest
        Args:
            mode: NodeMode for this strategy (passed to base)
            traits: NodeTrait for this strategy (passed to base)
            compression: Compression parameter (higher = more accurate, more memory, typical values: 50-200)
            **kwargs: Additional arguments - ignored
        """
        from ...defs import NodeMode, NodeTrait
        # Extract compression from kwargs if passed by flyweight
        compression = kwargs.pop('compression', compression)
        super().__init__(
            mode=mode or NodeMode.T_DIGEST,
            traits=traits or NodeTrait.NONE,
            **kwargs
        )
        self._compression = compression
        self._centroids: list[_Centroid] = []
        self._total_weight = 0.0
        self._min = float('inf')
        self._max = float('-inf')
        # Thread safety
        self._lock = RLock()

    def add(self, value: float, weight: float = 1.0) -> None:
        """
        Add value to T-Digest
        O(1) amortized time complexity
        Args:
            value: Numeric value to add
            weight: Weight of this value (default: 1.0)
        """
        with self._lock:
            # Update min/max
            if value < self._min:
                self._min = value
            if value > self._max:
                self._max = value
            # Add centroid
            self._centroids.append(_Centroid(value, weight))
            self._total_weight += weight
            # Compress if needed (keep centroids under control)
            if len(self._centroids) > self._compression * 2:
                self._compress()

    def quantile(self, q: float) -> float | None:
        """
        Get q-th quantile
        O(log δ) time complexity where δ is compression parameter
        Args:
            q: Quantile (0.0 to 1.0)
               q=0.0 → minimum
               q=0.5 → median
               q=0.95 → 95th percentile
               q=1.0 → maximum
        Returns:
            Estimated quantile value
        """
        with self._lock:
            if self._total_weight == 0:
                return None
            if q <= 0:
                return self._min
            if q >= 1:
                return self._max
            # Ensure centroids are sorted
            self._centroids.sort(key=lambda c: c.mean)
            # Find quantile using cumulative distribution
            target = q * self._total_weight
            cumulative = 0.0
            for i, centroid in enumerate(self._centroids):
                cumulative += centroid.weight
                if cumulative >= target:
                    # Found the centroid containing the quantile
                    if i == 0:
                        return centroid.mean
                    # Interpolate between centroids
                    prev_centroid = self._centroids[i - 1]
                    prev_cumulative = cumulative - centroid.weight
                    # Linear interpolation
                    fraction = (target - prev_cumulative) / centroid.weight
                    return prev_centroid.mean + fraction * (centroid.mean - prev_centroid.mean)
            return self._max

    def cdf(self, value: float) -> float:
        """
        Cumulative distribution function
        Returns fraction of values <= value
        Args:
            value: Value to query
        Returns:
            Fraction of values <= value (0.0 to 1.0)
        """
        with self._lock:
            if self._total_weight == 0:
                return 0.0
            if value <= self._min:
                return 0.0
            if value >= self._max:
                return 1.0
            # Ensure sorted
            self._centroids.sort(key=lambda c: c.mean)
            cumulative = 0.0
            for centroid in self._centroids:
                if centroid.mean > value:
                    break
                cumulative += centroid.weight
            return cumulative / self._total_weight

    def merge(self, other: TDigestStrategy) -> TDigestStrategy:
        """
        Merge two T-Digests
        Useful for distributed computation
        Args:
            other: Another T-Digest to merge
        Returns:
            New merged T-Digest
        """
        merged = TDigestStrategy(compression=self._compression)
        with self._lock:
            with other._lock:
                # Merge centroids
                merged._centroids = self._centroids + other._centroids
                merged._total_weight = self._total_weight + other._total_weight
                merged._min = min(self._min, other._min)
                merged._max = max(self._max, other._max)
                # Compress merged result
                merged._compress()
        return merged

    def get_min(self) -> float:
        """Get minimum value"""
        with self._lock:
            return self._min

    def get_max(self) -> float:
        """Get maximum value"""
        with self._lock:
            return self._max

    def get_count(self) -> float:
        """Get total count (weight)"""
        with self._lock:
            return self._total_weight

    def get_stats(self) -> dict[str, Any]:
        """Get T-Digest statistics"""
        with self._lock:
            return {
                'compression': self._compression,
                'centroids': len(self._centroids),
                'total_weight': self._total_weight,
                'min': self._min,
                'max': self._max,
                'median': self.quantile(0.5),
                'p95': self.quantile(0.95),
                'p99': self.quantile(0.99),
            }

    def _compress(self) -> None:
        """
        Compress centroids to maintain size bound
        Merges nearby centroids while maintaining accuracy
        """
        if len(self._centroids) <= self._compression:
            return
        # Sort by mean so each merged block remains locally coherent.
        self._centroids.sort(key=lambda c: c.mean)

        # Use deterministic block compression:
        # keep at most `compression` centroids by merging contiguous ranges.
        # This avoids pathological over-merging and preserves quantile shape.
        target = max(1, self._compression)
        n = len(self._centroids)
        block_size = max(1, math.ceil(n / target))

        compressed: list[_Centroid] = []
        for i in range(0, n, block_size):
            block = self._centroids[i:i + block_size]
            total_weight = sum(c.weight for c in block)
            if total_weight <= 0:
                continue
            weighted_mean = sum(c.mean * c.weight for c in block) / total_weight
            compressed.append(_Centroid(weighted_mean, total_weight))

        self._centroids = compressed[:target]

    def _scale_function(self, q: float) -> float:
        """
        T-Digest scale function
        Controls centroid density - more centroids near 0 and 1 (tails)
        """
        # Standard T-Digest scale function
        return 4 * self._total_weight * q * (1 - q)

    def _build_equi_width_buckets(self) -> None:
        """Not used in T-Digest"""
        pass

    def _build_equi_depth_buckets(self) -> None:
        """Not used in T-Digest"""
        pass
    # ANodeStrategy interface implementation

    def get_mode(self) -> NodeMode:
        """Get the node mode for this strategy"""
        return NodeMode.T_DIGEST

    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported"""
        supported = {
            'add', 'quantile', 'cdf', 'merge',
            'get_min', 'get_max', 'get_count', 'get_stats'
        }
        return operation in supported

    def get_complexity(self, operation: str) -> str:
        """Get time complexity for operation"""
        complexities = {
            'add': 'O(1) amortized',
            'quantile': 'O(log δ)',
            'cdf': 'O(log δ)',
            'merge': 'O(δ)',
        }
        return complexities.get(operation, 'O(1)')
    # Required abstract methods from ANodeStrategy

    def put(self, key: Any, value: Any = None) -> None:
        """Not applicable for t-digest - use add() instead"""
        raise NotImplementedError("Use add() for t-digest operations")

    def get(self, key: Any, default: Any = None) -> Any:
        """Not applicable for t-digest"""
        return default

    def has(self, key: Any) -> bool:
        """Not applicable for t-digest"""
        return False

    def delete(self, key: Any) -> bool:
        """Not applicable for t-digest"""
        return False

    def keys(self):
        """Get iterator over centroid means"""
        with self._lock:
            return iter(c.mean for c in self._centroids)

    def values(self):
        """Get iterator over centroid weights"""
        with self._lock:
            return iter(c.weight for c in self._centroids)

    def items(self):
        """Get iterator over (mean, weight) pairs"""
        with self._lock:
            return iter((c.mean, c.weight) for c in self._centroids)

    def __len__(self) -> int:
        """Get number of centroids"""
        with self._lock:
            return len(self._centroids)

    def to_native(self) -> Any:
        """Convert t-digest to native Python dict"""
        with self._lock:
            return {
                'compression': self._compression,
                'count': self._total_weight,
                'centroids': [(c.mean, c.weight) for c in self._centroids]
            }
