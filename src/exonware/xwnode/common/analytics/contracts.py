"""
#exonware/xwnode/src/exonware/xwnode/common/analytics/contracts.py
Analytics integration contracts for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.19
Generation Date: 01-Jan-2026
"""

from typing import Any, Protocol, runtime_checkable
from collections.abc import Sequence
from collections.abc import Callable
@runtime_checkable

class IAnalyticsStructures(Protocol):
    """
    Interface for analytics data structures.
    Provides access to Count-Min Sketch, HyperLogLog, and GraphBLAS.
    """

    def get_count_min_sketch(
        self,
        epsilon: float = 0.01,
        delta: float = 0.01
    ) -> Any:
        """
        Get Count-Min Sketch instance for frequency estimation.
        Args:
            epsilon: Error bound (default: 0.01 = 1%)
            delta: Confidence level (default: 0.01 = 99%)
        Returns:
            Count-Min Sketch instance
        """
        ...

    def get_hyperloglog(self, precision: int = 14) -> Any:
        """
        Get HyperLogLog instance for cardinality estimation.
        Args:
            precision: Precision parameter (default: 14)
        Returns:
            HyperLogLog instance
        """
        ...

    def get_graphblas(self) -> Any:
        """
        Get GraphBLAS instance for graph analytics.
        Returns:
            GraphBLAS instance
        """
        ...
@runtime_checkable

class IAnalyticsIntegration(Protocol):
    """
    Interface for analytics integration with xwai and xwstorage.
    Provides integration points for analytics processing and storage.
    """

    def process_analytics(
        self,
        data: Any,
        processor: Callable[[Any], Any]
    ) -> Any:
        """
        Process analytics data using processor function.
        Args:
            data: Analytics data to process
            processor: Processing function
        Returns:
            Processed analytics data
        """
        ...

    def store_analytics(
        self,
        storage: Any,
        data: Any
    ) -> None:
        """
        Store analytics data to storage backend.
        Args:
            storage: Storage backend instance
            data: Analytics data to store
        """
        ...

    def get_count_min_sketch(self) -> Any:
        """Get Count-Min Sketch instance."""
        ...

    def get_hyperloglog(self) -> Any:
        """Get HyperLogLog instance."""
        ...

    def get_graphblas(self) -> Any:
        """Get GraphBLAS instance."""
        ...
