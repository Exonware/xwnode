"""
#exonware/xwnode/tests/0.core/test_circular_buffer_strategy.py

Core tests for CIRCULAR_BUFFER strategy

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
class TestCircularBufferStrategyCore:
    """Core tests for CIRCULAR_BUFFER strategy - Fast, high-value checks"""
    
    def test_create_circular_buffer(self):
        """Test creating circular buffer"""
        buf = XWNode(mode=NodeMode.CIRCULAR_BUFFER, capacity=10)
        assert buf is not None
    
    def test_append_and_get(self):
        """Test append and get operations"""
        buf = XWNode(mode=NodeMode.CIRCULAR_BUFFER, capacity=5)
        strategy = buf._strategy
        
        # Append values
        for i in range(3):
            strategy.append(f'value{i}')
        
        # Get values
        assert strategy.get(0) == 'value0'
        assert strategy.get(1) == 'value1'
        assert strategy.get(2) == 'value2'
    
    def test_overwrite_when_full(self):
        """Test that oldest values are overwritten when buffer is full"""
        buf = XWNode(mode=NodeMode.CIRCULAR_BUFFER, capacity=3)
        strategy = buf._strategy
        
        # Fill buffer
        strategy.append('value0')
        strategy.append('value1')
        strategy.append('value2')
        
        # Add one more (should overwrite value0)
        strategy.append('value3')
        
        # Now oldest is value1
        assert strategy.get(0) == 'value1'
        assert strategy.get(1) == 'value2'
        assert strategy.get(2) == 'value3'
    
    def test_get_recent(self):
        """Test getting recent items"""
        buf = XWNode(mode=NodeMode.CIRCULAR_BUFFER, capacity=10)
        strategy = buf._strategy
        
        for i in range(5):
            strategy.append(f'value{i}')
        
        # Get 3 most recent
        recent = strategy.get_recent(3)
        assert recent == ['value4', 'value3', 'value2']

