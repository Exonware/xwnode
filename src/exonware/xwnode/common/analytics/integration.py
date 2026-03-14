"""
#exonware/xwnode/src/exonware/xwnode/common/analytics/integration.py
Analytics integration implementation for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: 01-Jan-2026
"""

from typing import Any
from .contracts import IAnalyticsIntegration
from .structures import AnalyticsDataStructures


from collections.abc import Callable
class AnalyticsIntegration:
    """
    Analytics integration with xwai and xwstorage.
    Provides integration interfaces for analytics processing and storage.
    """

    def __init__(self):
        """Initialize analytics integration."""
        self._structures = AnalyticsDataStructures()

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
        return processor(data)

    def store_analytics(
        self,
        storage: Any,
        data: Any
    ) -> None:
        """
        Store analytics data to storage backend.
        Args:
            storage: Storage backend instance (must have store method)
            data: Analytics data to store
        """
        if hasattr(storage, 'store'):
            storage.store(data)
        elif hasattr(storage, 'put'):
            storage.put(data)
        else:
            raise ValueError("Storage backend must have 'store' or 'put' method")

    def get_count_min_sketch(self) -> Any:
        """Get Count-Min Sketch instance."""
        return self._structures.get_count_min_sketch()

    def get_hyperloglog(self) -> Any:
        """Get HyperLogLog instance."""
        return self._structures.get_hyperloglog()

    def get_graphblas(self) -> Any:
        """Get GraphBLAS instance."""
        return self._structures.get_graphblas()
