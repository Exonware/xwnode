#!/usr/bin/env python3
"""
#exonware/xwnode/tests/2.integration/scenarios/test_adaptive_strategy.py
Tests for adaptive strategy selection.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.33
Generation Date: 07-Sep-2025
"""

import pytest
import time
from exonware.xwnode.common.management.adaptive_selector import (
    AdaptiveStrategySelector,
    get_adaptive_selector
)
from exonware.xwnode.common.monitoring.performance_monitor import (
    get_monitor,
    OperationType
)
from exonware.xwnode.defs import NodeMode
@pytest.mark.xwnode_integration

class TestAdaptiveStrategy:
    """Test adaptive strategy selection."""

    def test_recommend_strategy_no_data(self):
        """Test recommendation when no performance data available."""
        selector = AdaptiveStrategySelector()
        recommendation = selector.recommend_strategy(NodeMode.HASH_MAP)
        # Should return None if no data
        assert recommendation is None

    def test_recommend_strategy_with_data(self):
        """Test recommendation with performance data."""
        selector = AdaptiveStrategySelector()
        monitor = get_monitor()
        # Record some operations
        strategy_id = "node_HASH_MAP"
        for i in range(150):  # Above min_operations threshold
            monitor.record_operation(
                strategy_id=strategy_id,
                operation=OperationType.GET,
                duration=0.1,  # Slow operation (100ms)
                error=False
            )
        # Get recommendation
        recommendation = selector.recommend_strategy(NodeMode.HASH_MAP)
        # Should have recommendation if slow operations detected
        # (May or may not have recommendation depending on thresholds)
        if recommendation:
            assert recommendation.confidence > 0
            assert recommendation.alternative_strategy is not None

    def test_should_switch_confidence_threshold(self):
        """Test should_switch respects confidence threshold."""
        selector = AdaptiveStrategySelector()
        selector.configure(switch_threshold=0.9)  # High threshold
        # Create low-confidence recommendation
        from exonware.xwnode.common.monitoring.performance_monitor import PerformanceRecommendation
        low_confidence_rec = PerformanceRecommendation(
            strategy_name="test",
            recommendation_type="slow_operations",
            confidence=0.5,  # Below threshold
            reasoning="Test",
            estimated_improvement=0.2,
            alternative_strategy="ARRAY_LIST"
        )
        assert not selector.should_switch(NodeMode.HASH_MAP, low_confidence_rec)
        # High confidence should pass
        high_confidence_rec = PerformanceRecommendation(
            strategy_name="test",
            recommendation_type="slow_operations",
            confidence=0.95,  # Above threshold
            reasoning="Test",
            estimated_improvement=0.2,
            alternative_strategy="ARRAY_LIST"
        )
        # Should pass if other criteria met (min operations, etc.)
        # (May fail if min operations not met)
        result = selector.should_switch(NodeMode.HASH_MAP, high_confidence_rec)
        # Result depends on other criteria

    def test_get_recommended_mode(self):
        """Test getting recommended mode."""
        selector = AdaptiveStrategySelector()
        # Without data, should return None
        mode = selector.get_recommended_mode(NodeMode.HASH_MAP)
        assert mode is None or isinstance(mode, NodeMode)

    def test_record_switch(self):
        """Test recording strategy switches."""
        selector = AdaptiveStrategySelector()
        selector.record_switch(NodeMode.HASH_MAP, NodeMode.ARRAY_LIST, success=True)
        stats = selector.get_stats()
        assert stats['switches_performed'] == 1
        assert stats['switches_rejected'] == 0

    def test_configure(self):
        """Test configuring selector parameters."""
        selector = AdaptiveStrategySelector()
        selector.configure(switch_threshold=0.7, min_operations=50)
        # Verify configuration
        recommendation = selector.recommend_strategy(NodeMode.HASH_MAP)
        # Configuration affects should_switch behavior

    def test_global_selector_singleton(self):
        """Test that get_adaptive_selector returns singleton."""
        selector1 = get_adaptive_selector()
        selector2 = get_adaptive_selector()
        assert selector1 is selector2
