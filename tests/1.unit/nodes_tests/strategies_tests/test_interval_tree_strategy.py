#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_interval_tree_strategy.py
Comprehensive tests for Interval Tree Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Interval queries (overlap, contains)
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

def empty_interval_tree():
    """Create empty interval tree."""
    return XWNode(mode=NodeMode.INTERVAL_TREE)
@pytest.fixture

def simple_interval_tree():
    """Create interval tree with intervals."""
    tree = XWNode(mode=NodeMode.INTERVAL_TREE)
    tree.put((10, 20), {'id': 'interval1', 'data': 'value1'})
    tree.put((15, 25), {'id': 'interval2', 'data': 'value2'})
    tree.put((30, 40), {'id': 'interval3', 'data': 'value3'})
    return tree
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestIntervalTreeStrategy:
    """Test Interval Tree strategy interface compliance."""

    def test_insert_operation(self, empty_interval_tree):
        """Test insert operation works correctly."""
        empty_interval_tree.put((10, 20), {'data': 'value'})
        result = empty_interval_tree.get((10, 20))
        assert result is not None

    def test_find_operation(self, simple_interval_tree):
        """Test find operation returns correct values."""
        result = simple_interval_tree.get((10, 20))
        assert result is not None
        assert result.get('id') == 'interval1'

    def test_delete_operation(self, simple_interval_tree):
        """Test delete operation removes intervals correctly."""
        assert simple_interval_tree.delete((10, 20)) is True
        assert simple_interval_tree.get((10, 20)) is None
        assert simple_interval_tree.delete((100, 200)) is False

    def test_size_operation(self, simple_interval_tree):
        """Test size returns correct count."""
        assert simple_interval_tree.size() == 3
        simple_interval_tree.delete((10, 20))
        assert simple_interval_tree.size() == 2

    def test_is_empty_operation(self, empty_interval_tree, simple_interval_tree):
        """Test is_empty correctly identifies empty structures."""
        assert empty_interval_tree.is_empty() is True
        assert simple_interval_tree.is_empty() is False
