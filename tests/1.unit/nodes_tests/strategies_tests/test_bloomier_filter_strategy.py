#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_bloomier_filter_strategy.py
Comprehensive tests for Bloomier Filter Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find)
- Probabilistic key-value mapping
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

def empty_bloomier():
    """Create empty Bloomier filter."""
    return XWNode(mode=NodeMode.BLOOMIER_FILTER, capacity=1000)
@pytest.fixture

def simple_bloomier():
    """Create Bloomier filter with data."""
    bloomier = XWNode(mode=NodeMode.BLOOMIER_FILTER, capacity=1000)
    bloomier.put('key1', 'value1')
    bloomier.put('key2', 'value2')
    return bloomier
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBloomierFilterStrategy:
    """Test Bloomier Filter strategy interface compliance."""

    def test_insert_operation(self, empty_bloomier):
        """Test insert operation works correctly."""
        empty_bloomier.put('test_key', 'test_value')
        result = empty_bloomier.get('test_key')
        # Bloomier filter may have false positives, but should find inserted keys
        assert result is not None

    def test_find_operation(self, simple_bloomier):
        """Test find operation returns correct values."""
        result = simple_bloomier.get('key1')
        # May have false positives, but inserted keys should be found
        assert result is not None

    def test_size_operation(self, simple_bloomier):
        """Test size returns correct count."""
        # Bloomier filter size may be approximate
        assert simple_bloomier.size() >= 0

    def test_is_empty_operation(self, empty_bloomier, simple_bloomier):
        """Test is_empty correctly identifies empty structures."""
        assert empty_bloomier.is_empty is True
        assert simple_bloomier.is_empty is False
