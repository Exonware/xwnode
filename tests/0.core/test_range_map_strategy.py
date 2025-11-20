"""
#exonware/xwnode/tests/0.core/test_range_map_strategy.py

Core tests for RANGE_MAP strategy

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
class TestRangeMapStrategyCore:
    """Core tests for RANGE_MAP strategy - Fast, high-value checks"""
    
    def test_create_range_map(self):
        """Test creating range map"""
        rmap = XWNode(mode=NodeMode.RANGE_MAP)
        assert rmap is not None
    
    def test_put_and_get(self):
        """Test basic put and get operations"""
        rmap = XWNode(mode=NodeMode.RANGE_MAP)
        strategy = rmap._strategy
        
        strategy.put(0, 100, 'small')
        strategy.put(100, 1000, 'medium')
        strategy.put(1000, 10000, 'large')
        
        assert strategy.get(50) == 'small'
        assert strategy.get(500) == 'medium'
        assert strategy.get(5000) == 'large'
    
    def test_binary_search_performance(self):
        """Test O(log n) lookups with many ranges"""
        rmap = XWNode(mode=NodeMode.RANGE_MAP)
        strategy = rmap._strategy
        
        # Add 100 ranges
        for i in range(100):
            strategy.put(i * 100, (i + 1) * 100, f'range_{i}')
        
        # Should still be fast (O(log n))
        result = strategy.get(5050)
        assert result == 'range_50'

