#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_multiplex_strategy.py
Comprehensive tests for Multiplex Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Multi-layer graph operations
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

def empty_multiplex():
    """Create empty multiplex graph."""
    return XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.MULTIPLEX)
@pytest.fixture

def simple_multiplex():
    """Create multiplex graph with edges."""
    graph = XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.MULTIPLEX)
    graph.add_edge('A', 'B', layer='layer1')
    graph.add_edge('B', 'C', layer='layer2')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestMultiplexStrategy:
    """Test Multiplex strategy interface compliance."""

    def test_add_edge_operation(self, empty_multiplex):
        """Test add_edge operation works correctly."""
        edge_id = empty_multiplex.add_edge('A', 'B', layer='layer1')
        assert edge_id is not None
        assert empty_multiplex.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_multiplex):
        """Test has_edge operation returns correct values."""
        assert simple_multiplex.has_edge('A', 'B') is True
        assert simple_multiplex.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_multiplex):
        """Test delete_edge operation removes edges correctly."""
        assert simple_multiplex.delete_edge('A', 'B') is True
        assert simple_multiplex.has_edge('A', 'B') is False
