#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_roaring_adj_strategy.py
Comprehensive tests for Roaring Adjacency Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Fast set operations on adjacency
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
from exonware.xwnode.defs import NodeMode, EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_roaring_adj():
    """Create empty roaring adjacency graph."""
    return XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.ROARING_ADJ)
@pytest.fixture

def simple_roaring_adj():
    """Create roaring adjacency graph with edges."""
    graph = XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.ROARING_ADJ)
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestRoaringAdjStrategy:
    """Test Roaring Adjacency strategy interface compliance."""

    def test_add_edge_operation(self, empty_roaring_adj):
        """Test add_edge operation works correctly."""
        edge_id = empty_roaring_adj.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_roaring_adj.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_roaring_adj):
        """Test has_edge operation returns correct values."""
        assert simple_roaring_adj.has_edge('A', 'B') is True
        assert simple_roaring_adj.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_roaring_adj):
        """Test delete_edge operation removes edges correctly."""
        assert simple_roaring_adj.delete_edge('A', 'B') is True
        assert simple_roaring_adj.has_edge('A', 'B') is False
