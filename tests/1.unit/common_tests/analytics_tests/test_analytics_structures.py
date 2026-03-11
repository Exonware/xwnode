"""
#exonware/xwnode/tests/1.unit/common_tests/analytics_tests/test_analytics_structures.py
Unit tests for analytics structures.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.analytics.structures import AnalyticsDataStructures
from exonware.xwnode.common.analytics.contracts import IAnalyticsStructures
@pytest.mark.xwnode_unit

class TestAnalyticsDataStructures:
    """Tests for AnalyticsDataStructures."""

    def test_initialization(self):
        """Test structures initialization."""
        structures = AnalyticsDataStructures()
        assert structures is not None
        assert structures._count_min_sketch is None
        assert structures._hyperloglog is None
        assert structures._graphblas is None

    def test_get_count_min_sketch(self):
        """Test getting Count-Min Sketch."""
        structures = AnalyticsDataStructures()
        cms = structures.get_count_min_sketch(epsilon=0.01, delta=0.01)
        assert cms is not None
        # Verify it's the same instance on second call
        cms2 = structures.get_count_min_sketch()
        assert cms is cms2

    def test_get_hyperloglog(self):
        """Test getting HyperLogLog."""
        structures = AnalyticsDataStructures()
        hll = structures.get_hyperloglog(precision=14)
        assert hll is not None
        # Verify it's the same instance on second call
        hll2 = structures.get_hyperloglog()
        assert hll is hll2

    def test_get_graphblas(self):
        """Test getting GraphBLAS."""
        structures = AnalyticsDataStructures()
        graph = structures.get_graphblas()
        assert graph is not None
        # Verify it's the same instance on second call
        graph2 = structures.get_graphblas()
        assert graph is graph2

    def test_reset(self):
        """Test resetting structures."""
        structures = AnalyticsDataStructures()
        # Create instances
        structures.get_count_min_sketch()
        structures.get_hyperloglog()
        structures.get_graphblas()
        # Reset
        structures.reset()
        assert structures._count_min_sketch is None
        assert structures._hyperloglog is None
        assert structures._graphblas is None

    def test_implements_interface(self):
        """Test that AnalyticsDataStructures implements IAnalyticsStructures."""
        structures = AnalyticsDataStructures()
        assert isinstance(structures, IAnalyticsStructures)
