"""
#exonware/xwnode/tests/0.core/test_histogram_strategy.py

Core tests for HISTOGRAM strategy

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.28
Generation Date: 27-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode, NodeMode


@pytest.mark.xwnode_core
@pytest.mark.xwnode_node_strategy
class TestHistogramStrategyCore:
    """Core tests for HISTOGRAM strategy - Fast, high-value checks"""
    
    def test_create_histogram(self):
        """Test creating histogram"""
        hist = XWNode(mode=NodeMode.HISTOGRAM, num_buckets=10)
        assert hist is not None
    
    def test_add_values_and_build(self):
        """Test adding values and building histogram"""
        hist = XWNode(mode=NodeMode.HISTOGRAM, num_buckets=10, histogram_type='equi-width')
        strategy = hist._strategy
        
        # Add values
        for value in [10, 20, 30, 40, 50]:
            strategy.add_value(value)
        
        strategy.build()
        
        # Should have buckets now
        buckets = strategy.get_buckets()
        assert len(buckets) > 0
    
    def test_selectivity_estimation(self):
        """Test selectivity estimation"""
        hist = XWNode(mode=NodeMode.HISTOGRAM, num_buckets=10, histogram_type='equi-width')
        strategy = hist._strategy
        
        # Add 100 values from 0 to 99
        for i in range(100):
            strategy.add_value(float(i))
        
        strategy.build()
        
        # Estimate selectivity for range [0, 50) - should be ~0.5
        selectivity = strategy.estimate_selectivity(0, 50)
        assert 0.4 < selectivity < 0.6  # Allow some tolerance

