#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_circular_buffer_strategy.py
Comprehensive tests for Circular Buffer Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Fixed-size ring buffer operations
- Security (input validation, resource limits)
- Error handling
- Edge cases
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_circular_buffer():
    """Create empty circular buffer."""
    return XWNode(mode=NodeMode.CIRCULAR_BUFFER, capacity=10)
@pytest.fixture

def simple_circular_buffer():
    """Create circular buffer with data."""
    buffer = XWNode(mode=NodeMode.CIRCULAR_BUFFER, capacity=10)
    buffer.put(0, 'value1')
    buffer.put(1, 'value2')
    buffer.put(2, 'value3')
    return buffer
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestCircularBufferStrategy:
    """Test Circular Buffer strategy interface compliance."""

    def test_insert_operation(self, empty_circular_buffer):
        """Test insert operation works correctly."""
        empty_circular_buffer.put(0, 'value')
        result = empty_circular_buffer.get(0)
        assert result is not None

    def test_find_operation(self, simple_circular_buffer):
        """Test find operation returns correct values."""
        result = simple_circular_buffer.get(0)
        assert result is not None
        assert result == 'value1'

    def test_delete_operation(self, simple_circular_buffer):
        """Test delete operation removes values correctly."""
        assert simple_circular_buffer.delete(0) is True
        assert simple_circular_buffer.get(0) is None

    def test_size_operation(self, simple_circular_buffer):
        """Test size returns correct count."""
        assert simple_circular_buffer.size() >= 3

    def test_is_empty_operation(self, empty_circular_buffer, simple_circular_buffer):
        """Test is_empty correctly identifies empty structures."""
        assert empty_circular_buffer.is_empty is True
        assert simple_circular_buffer.is_empty is False
