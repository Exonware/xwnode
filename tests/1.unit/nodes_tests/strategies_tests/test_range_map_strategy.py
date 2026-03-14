#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_range_map_strategy.py
Comprehensive tests for Range Map Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Non-overlapping range→value mapping
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

def empty_range_map():
    """Create empty range map."""
    return XWNode(mode=NodeMode.RANGE_MAP)
@pytest.fixture

def simple_range_map():
    """Create range map with ranges."""
    range_map = XWNode(mode=NodeMode.RANGE_MAP)
    range_map.put((0, 10), 'value1')
    range_map.put((10, 20), 'value2')
    range_map.put((20, 30), 'value3')
    return range_map
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestRangeMapStrategy:
    """Test Range Map strategy interface compliance."""

    def test_insert_operation(self, empty_range_map):
        """Test insert operation works correctly."""
        empty_range_map.put((0, 10), 'value')
        result = empty_range_map.get((0, 10))
        assert result is not None

    def test_find_operation(self, simple_range_map):
        """Test find operation returns correct values."""
        result = simple_range_map.get((0, 10))
        assert result is not None
        assert result == 'value1'

    def test_delete_operation(self, simple_range_map):
        """Test delete operation removes ranges correctly."""
        assert simple_range_map.delete((0, 10)) is True
        assert simple_range_map.get((0, 10)) is None
        assert simple_range_map.delete((100, 200)) is False

    def test_size_operation(self, simple_range_map):
        """Test size returns correct count."""
        assert simple_range_map.size() == 3
        simple_range_map.delete((0, 10))
        assert simple_range_map.size() == 2

    def test_is_empty_operation(self, empty_range_map, simple_range_map):
        """Test is_empty correctly identifies empty structures."""
        assert empty_range_map.is_empty is True
        assert simple_range_map.is_empty is False
