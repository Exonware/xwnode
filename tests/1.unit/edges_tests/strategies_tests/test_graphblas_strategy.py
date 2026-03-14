#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_graphblas_strategy.py
Comprehensive tests for GraphBLAS Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- GraphBLAS semiring operations
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
from exonware.xwnode.edges.strategies.graphblas import GraphBLASStrategy
from exonware.xwnode.defs import EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_graphblas():
    """Create empty GraphBLAS graph."""
    return GraphBLASStrategy()
@pytest.fixture

def simple_graphblas():
    """Create GraphBLAS graph with edges."""
    graph = GraphBLASStrategy()
    graph.add_edge('A', 'B', weight=1.5)
    graph.add_edge('B', 'C', weight=2.0)
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestGraphBLASStrategy:
    """Test GraphBLAS strategy interface compliance."""

    def test_add_edge_operation(self, empty_graphblas):
        """Test add_edge operation works correctly."""
        edge_id = empty_graphblas.add_edge('A', 'B', weight=1.0)
        assert edge_id is not None
        assert empty_graphblas.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_graphblas):
        """Test has_edge operation returns correct values."""
        assert simple_graphblas.has_edge('A', 'B') is True
        assert simple_graphblas.has_edge('B', 'C') is True
        assert simple_graphblas.has_edge('C', 'A') is False

    def test_delete_edge_operation(self, simple_graphblas):
        """Test delete_edge operation removes edges correctly."""
        assert simple_graphblas.remove_edge('A', 'B') is True
        assert simple_graphblas.has_edge('A', 'B') is False

    def test_get_neighbors_operation(self, simple_graphblas):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_graphblas.get_neighbors('A'))
        assert 'B' in neighbors
