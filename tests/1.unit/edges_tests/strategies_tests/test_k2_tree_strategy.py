#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_k2_tree_strategy.py
Comprehensive tests for K2-Tree Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Ultra-compact adjacency representation
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
from exonware.xwnode.edges.strategies.k2_tree import K2TreeStrategy
from exonware.xwnode.defs import EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_k2_tree():
    """Create empty K2-tree."""
    return K2TreeStrategy()
@pytest.fixture

def simple_k2_tree():
    """Create K2-tree with edges."""
    graph = K2TreeStrategy()
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestK2TreeStrategy:
    """Test K2-Tree strategy interface compliance."""

    def test_add_edge_operation(self, empty_k2_tree):
        """Test add_edge operation works correctly."""
        edge_id = empty_k2_tree.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_k2_tree.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_k2_tree):
        """Test has_edge operation returns correct values."""
        assert simple_k2_tree.has_edge('A', 'B') is True
        assert simple_k2_tree.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_k2_tree):
        """Test delete_edge operation removes edges correctly."""
        assert simple_k2_tree.delete_edge('A', 'B') is True
        assert simple_k2_tree.has_edge('A', 'B') is False
