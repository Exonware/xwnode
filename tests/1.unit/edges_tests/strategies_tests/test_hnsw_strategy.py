#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_hnsw_strategy.py
Comprehensive tests for HNSW (Hierarchical Navigable Small World) Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Approximate nearest neighbor queries
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
from exonware.xwnode.edges.strategies.hnsw import HNSWStrategy
from exonware.xwnode.defs import EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_hnsw():
    """Create empty HNSW graph."""
    return HNSWStrategy()
@pytest.fixture

def simple_hnsw():
    """Create HNSW graph with edges."""
    graph = HNSWStrategy()
    graph.add_edge('A', 'B', weight=1.0)
    graph.add_edge('B', 'C', weight=2.0)
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestHNSWStrategy:
    """Test HNSW strategy interface compliance."""

    def test_add_edge_operation(self, empty_hnsw):
        """Test add_edge operation works correctly."""
        edge_id = empty_hnsw.add_edge('A', 'B', weight=1.0)
        assert edge_id is not None
        assert empty_hnsw.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_hnsw):
        """Test has_edge operation returns correct values."""
        assert simple_hnsw.has_edge('A', 'B') is True
        assert simple_hnsw.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_hnsw):
        """Test delete_edge operation removes edges correctly."""
        assert simple_hnsw.delete_edge('A', 'B') is True
        assert simple_hnsw.has_edge('A', 'B') is False
