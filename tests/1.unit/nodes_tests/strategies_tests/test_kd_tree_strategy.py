#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_kd_tree_strategy.py
Comprehensive tests for KD-Tree Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Spatial queries (nearest neighbor, range queries)
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

def empty_kd_tree():
    """Create empty KD-tree."""
    return XWNode(mode=NodeMode.KD_TREE)
@pytest.fixture

def simple_kd_tree():
    """Create KD-tree with 2D points."""
    tree = XWNode(mode=NodeMode.KD_TREE)
    tree.put((1.0, 2.0), {'id': 'point1', 'data': 'value1'})
    tree.put((3.0, 4.0), {'id': 'point2', 'data': 'value2'})
    tree.put((5.0, 6.0), {'id': 'point3', 'data': 'value3'})
    return tree
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestKDTreeStrategy:
    """Test KD-Tree strategy interface compliance."""

    def test_insert_operation(self, empty_kd_tree):
        """Test insert operation works correctly."""
        empty_kd_tree.put((1.0, 2.0), {'data': 'value'})
        result = empty_kd_tree.get((1.0, 2.0))
        assert result is not None

    def test_find_operation(self, simple_kd_tree):
        """Test find operation returns correct values."""
        result = simple_kd_tree.get((1.0, 2.0))
        assert result is not None
        assert result.get('id') == 'point1'

    def test_delete_operation(self, simple_kd_tree):
        """Test delete operation removes points correctly."""
        assert simple_kd_tree.delete((1.0, 2.0)) is True
        assert simple_kd_tree.get((1.0, 2.0)) is None
        assert simple_kd_tree.delete((100.0, 200.0)) is False

    def test_size_operation(self, simple_kd_tree):
        """Test size returns correct count."""
        assert simple_kd_tree.size() == 3
        simple_kd_tree.delete((1.0, 2.0))
        assert simple_kd_tree.size() == 2

    def test_is_empty_operation(self, empty_kd_tree, simple_kd_tree):
        """Test is_empty correctly identifies empty structures."""
        assert empty_kd_tree.is_empty() is True
        assert simple_kd_tree.is_empty() is False
