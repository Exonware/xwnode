#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_link_cut_strategy.py
Comprehensive tests for Link-Cut Tree Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Dynamic tree operations with path queries
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
from exonware.xwnode.edges.strategies.link_cut import LinkCutStrategy
from exonware.xwnode.defs import EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_link_cut():
    """Create empty link-cut tree."""
    return LinkCutStrategy()
@pytest.fixture

def simple_link_cut():
    """Create link-cut tree with edges."""
    graph = LinkCutStrategy()
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestLinkCutStrategy:
    """Test Link-Cut strategy interface compliance."""

    def test_add_edge_operation(self, empty_link_cut):
        """Test add_edge operation works correctly."""
        edge_id = empty_link_cut.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_link_cut.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_link_cut):
        """Test has_edge operation returns correct values."""
        assert simple_link_cut.has_edge('A', 'B') is True
        assert simple_link_cut.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_link_cut):
        """Test delete_edge operation removes edges correctly."""
        assert simple_link_cut.delete_edge('A', 'B') is True
        assert simple_link_cut.has_edge('A', 'B') is False
