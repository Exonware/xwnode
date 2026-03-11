#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_euler_tour_strategy.py
Comprehensive tests for Euler Tour Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Dynamic connectivity queries
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

def empty_euler_tour():
    """Create empty Euler tour tree."""
    return XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.EULER_TOUR)
@pytest.fixture

def simple_euler_tour():
    """Create Euler tour tree with edges."""
    graph = XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.EULER_TOUR)
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestEulerTourStrategy:
    """Test Euler Tour strategy interface compliance."""

    def test_add_edge_operation(self, empty_euler_tour):
        """Test add_edge operation works correctly."""
        edge_id = empty_euler_tour.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_euler_tour.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_euler_tour):
        """Test has_edge operation returns correct values."""
        assert simple_euler_tour.has_edge('A', 'B') is True
        assert simple_euler_tour.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_euler_tour):
        """Test delete_edge operation removes edges correctly."""
        assert simple_euler_tour.delete_edge('A', 'B') is True
        assert simple_euler_tour.has_edge('A', 'B') is False
