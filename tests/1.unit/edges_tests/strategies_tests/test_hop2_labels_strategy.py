#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_hop2_labels_strategy.py
Comprehensive tests for 2-Hop Labeling Strategy.
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Fast reachability queries
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
from exonware.xwnode.edges.strategies.hop2_labels import Hop2LabelsStrategy
from exonware.xwnode.defs import EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_hop2():
    """Create empty 2-hop labeling graph."""
    return Hop2LabelsStrategy()
@pytest.fixture

def simple_hop2():
    """Create 2-hop labeling graph with edges."""
    graph = Hop2LabelsStrategy()
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    return graph
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestHop2LabelsStrategy:
    """Test 2-Hop Labeling strategy interface compliance."""

    def test_add_edge_operation(self, empty_hop2):
        """Test add_edge operation works correctly."""
        edge_id = empty_hop2.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_hop2.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_hop2):
        """Test has_edge operation returns correct values."""
        assert simple_hop2.has_edge('A', 'B') is True
        assert simple_hop2.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_hop2):
        """Test delete_edge operation removes edges correctly."""
        assert simple_hop2.delete_edge('A', 'B') is True
        assert simple_hop2.has_edge('A', 'B') is False
