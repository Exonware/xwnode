"""
#exonware/xwnode/src/exonware/xwnode/common/analytics/structures.py
Analytics data structures facade for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.21
Generation Date: 01-Jan-2026
"""

from typing import Any
from .contracts import IAnalyticsStructures
from ...facade import XWNode
from ...facades.graph import XWNodeGraph
from ...defs import NodeMode, EdgeMode


class AnalyticsDataStructures:
    """
    Analytics data structures facade.
    Wraps Count-Min Sketch, HyperLogLog, and GraphBLAS for analytics operations.
    Provides unified interface for analytics data structures.
    """

    def __init__(self):
        """Initialize analytics data structures."""
        self._count_min_sketch: XWNode | None = None
        self._hyperloglog: XWNode | None = None
        # Use XWNodeGraph with GRAPHBLAS edge mode (reuse existing facade)
        self._graphblas: XWNodeGraph | None = None

    def get_count_min_sketch(
        self,
        epsilon: float = 0.01,
        delta: float = 0.01
    ) -> XWNode:
        """
        Get Count-Min Sketch instance for frequency estimation.
        Args:
            epsilon: Error bound (default: 0.01 = 1%)
            delta: Confidence level (default: 0.01 = 99%)
        Returns:
            XWNode with COUNT_MIN_SKETCH mode
        """
        if self._count_min_sketch is None:
            self._count_min_sketch = XWNode(
                mode=NodeMode.COUNT_MIN_SKETCH,
                epsilon=epsilon,
                delta=delta
            )
        return self._count_min_sketch

    def get_hyperloglog(self, precision: int = 14) -> XWNode:
        """
        Get HyperLogLog instance for cardinality estimation.
        Args:
            precision: Precision parameter (default: 14)
        Returns:
            XWNode with HYPERLOGLOG mode
        """
        if self._hyperloglog is None:
            self._hyperloglog = XWNode(
                mode=NodeMode.HYPERLOGLOG,
                precision=precision
            )
        return self._hyperloglog

    def get_graphblas(self) -> XWNodeGraph:
        """
        Get GraphBLAS instance for graph analytics.
        Returns:
            XWNodeGraph with GRAPHBLAS edge mode (reuses existing facade)
        """
        if self._graphblas is None:
            self._graphblas = XWNodeGraph(
                node_mode=NodeMode.HASH_MAP,
                edge_mode=EdgeMode.GRAPHBLAS,
                enable_caching=True,
                enable_indexing=True
            )
        return self._graphblas

    def reset(self) -> None:
        """Reset all analytics structures."""
        self._count_min_sketch = None
        self._hyperloglog = None
        self._graphblas = None
