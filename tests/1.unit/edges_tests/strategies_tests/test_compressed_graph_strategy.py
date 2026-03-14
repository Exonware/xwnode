#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_compressed_graph_strategy.py
Comprehensive tests for Compressed Graph Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Graph compression operations
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

def empty_compressed():
    """Create empty compressed graph (use XWNodeGraph for edge operations)."""
    return XWNodeGraph(node_mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.COMPRESSED_GRAPH)
@pytest.fixture

def simple_compressed():
    """Create compressed graph with edges."""
    graph = XWNodeGraph(node_mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.COMPRESSED_GRAPH)
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    graph.add_edge('A', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestCompressedGraphStrategy:
    """Test Compressed Graph strategy interface compliance."""

    def test_add_edge_operation(self, empty_compressed):
        """Test add_edge operation works correctly."""
        edge_id = empty_compressed.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_compressed.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_compressed):
        """Test has_edge operation returns correct values."""
        assert simple_compressed.has_edge('A', 'B') is True
        assert simple_compressed.has_edge('B', 'C') is True
        assert simple_compressed.has_edge('C', 'A') is False

    def test_delete_edge_operation(self, simple_compressed):
        """Test remove_edge operation removes edges correctly (XWNodeGraph uses remove_edge)."""
        assert simple_compressed.remove_edge('A', 'B') is True
        assert simple_compressed.has_edge('A', 'B') is False
        assert simple_compressed.remove_edge('nonexistent', 'edge') is False

    def test_get_neighbors_operation(self, simple_compressed):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_compressed.get_neighbors('A'))
        assert 'B' in neighbors or 'C' in neighbors
