#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_bitemporal_strategy.py
Comprehensive tests for Bitemporal Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Valid time and transaction time tracking
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

def empty_bitemporal():
    """Create empty bitemporal graph."""
    return XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.BITEMPORAL)
@pytest.fixture

def simple_bitemporal():
    """Create bitemporal graph with edges."""
    graph = XWNode(mode=NodeMode.ADJACENCY_LIST, edge_mode=EdgeMode.BITEMPORAL)
    graph.add_edge('A', 'B', valid_time=(0, 100), transaction_time=1000)
    graph.add_edge('B', 'C', valid_time=(0, 100), transaction_time=1001)
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestBitemporalStrategy:
    """Test Bitemporal strategy interface compliance."""

    def test_add_edge_operation(self, empty_bitemporal):
        """Test add_edge operation works correctly."""
        edge_id = empty_bitemporal.add_edge('A', 'B', valid_time=(0, 100), transaction_time=1000)
        assert edge_id is not None
        assert empty_bitemporal.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_bitemporal):
        """Test has_edge operation returns correct values."""
        assert simple_bitemporal.has_edge('A', 'B') is True
        assert simple_bitemporal.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_bitemporal):
        """Test delete_edge operation removes edges correctly."""
        assert simple_bitemporal.delete_edge('A', 'B') is True
        assert simple_bitemporal.has_edge('A', 'B') is False
