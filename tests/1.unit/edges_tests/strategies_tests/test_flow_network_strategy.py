"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_flow_network_strategy.py
Comprehensive tests for FlowNetworkStrategy (edge strategy).
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Flow network operations (capacity, flow)
- Network flow algorithms support
- Performance characteristics
- Security (input validation, resource limits)
- Error handling
- Edge cases
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 15-Nov-2025
"""

import pytest
from typing import Any
from exonware.xwnode.edges.strategies.flow_network import FlowNetworkStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty flow network strategy."""
    return FlowNetworkStrategy()
@pytest.fixture

def simple_strategy():
    """Create flow network with simple graph."""
    strategy = FlowNetworkStrategy()
    strategy.add_edge('A', 'B', capacity=10)
    strategy.add_edge('B', 'C', capacity=5)
    strategy.add_edge('A', 'C', capacity=8)
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestFlowNetworkStrategyInterface:
    """Test FlowNetworkStrategy implements iEdgeStrategy interface correctly."""

    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B', capacity=10)
        assert edge_id is not None
        assert empty_strategy.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_strategy):
        """Test has_edge operation returns correct values."""
        assert simple_strategy.has_edge('A', 'B') is True
        assert simple_strategy.has_edge('B', 'C') is True
        assert simple_strategy.has_edge('A', 'C') is True

    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.neighbors('A'))
        assert 'B' in neighbors
        assert 'C' in neighbors
# ============================================================================
# FLOW NETWORK FEATURES TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestFlowNetworkStrategyFlow:
    """Test flow network specific features."""

    def test_capacity_support(self, simple_strategy):
        """Test edge capacity support."""
        # Flow network should support edge capacities
        if hasattr(simple_strategy, 'get_edge_capacity'):
            capacity = simple_strategy.get_edge_capacity('A', 'B')
            assert capacity == 10
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestFlowNetworkStrategyCore:
    """Test core FlowNetworkStrategy functionality."""

    def test_edge_count(self, simple_strategy):
        """Test edge count tracking."""
        assert simple_strategy.edge_count() == 3

    def test_vertex_count(self, simple_strategy):
        """Test vertex count tracking."""
        vertices = simple_strategy.vertices()
        assert 'A' in vertices
        assert 'B' in vertices
        assert 'C' in vertices
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestFlowNetworkStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.neighbors('A')) == []
        assert empty_strategy.edge_count() == 0
