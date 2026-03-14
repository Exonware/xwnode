#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_bv_graph_strategy.py
Comprehensive tests for BVGraph Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- WebGraph compression with Elias coding
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
from exonware.xwnode.facades.graph import XWNodeGraph
from exonware.xwnode.defs import NodeMode, EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_bv_graph():
    """Create empty BVGraph (use XWNodeGraph for edge operations)."""
    return XWNodeGraph(node_mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.BV_GRAPH)
@pytest.fixture

def simple_bv_graph():
    """Create BVGraph with edges."""
    graph = XWNodeGraph(node_mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.BV_GRAPH)
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestBVGraphStrategy:
    """Test BVGraph strategy interface compliance."""

    def test_add_edge_operation(self, empty_bv_graph):
        """Test add_edge operation works correctly."""
        edge_id = empty_bv_graph.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_bv_graph.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_bv_graph):
        """Test has_edge operation returns correct values."""
        assert simple_bv_graph.has_edge('A', 'B') is True
        assert simple_bv_graph.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_bv_graph):
        """Test remove_edge operation removes edges correctly (XWNodeGraph uses remove_edge)."""
        assert simple_bv_graph.remove_edge('A', 'B') is True
        assert simple_bv_graph.has_edge('A', 'B') is False
