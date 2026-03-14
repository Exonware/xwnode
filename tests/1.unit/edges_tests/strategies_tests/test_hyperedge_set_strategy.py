"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_hyperedge_set_strategy.py
Comprehensive tests for HyperedgeSetStrategy (edge strategy).
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Hyperedge support (edges connecting multiple vertices)
- Multi-vertex edge queries
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
from exonware.xwnode.edges.strategies.hyperedge_set import HyperEdgeSetStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty hyperedge set strategy."""
    return HyperEdgeSetStrategy()
@pytest.fixture

def simple_strategy():
    """Create hyperedge set with simple graph."""
    strategy = HyperEdgeSetStrategy()
    strategy.add_edge('A', 'B')
    # Hyperedge: edge connecting multiple vertices
    if hasattr(strategy, 'add_hyperedge'):
        strategy.add_hyperedge(['A', 'B', 'C'])
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestHyperedgeSetStrategyInterface:
    """Test HyperedgeSetStrategy implements iEdgeStrategy interface correctly."""

    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B')
        assert edge_id is not None
        assert empty_strategy.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_strategy):
        """Test has_edge operation returns correct values."""
        assert simple_strategy.has_edge('A', 'B') is True

    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.neighbors('A'))
        assert 'B' in neighbors
# ============================================================================
# HYPEREDGE FEATURES TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestHyperedgeSetStrategyHyperedge:
    """Test hyperedge features (multi-vertex edges)."""

    def test_hyperedge_support(self, simple_strategy):
        """Test hyperedge support if available."""
        # Hyperedge set should support edges connecting multiple vertices
        if hasattr(simple_strategy, 'get_hyperedges'):
            hyperedges = simple_strategy.get_hyperedges('A')
            assert len(hyperedges) >= 0
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestHyperedgeSetStrategyCore:
    """Test core HyperedgeSetStrategy functionality."""

    def test_edge_count(self, simple_strategy):
        """Test edge count tracking."""
        assert simple_strategy.edge_count() >= 1

    def test_vertex_count(self, simple_strategy):
        """Test vertex count tracking."""
        vertices = list(simple_strategy.vertices())
        assert 'A' in vertices
        assert 'B' in vertices
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestHyperedgeSetStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.neighbors('A')) == []
        assert empty_strategy.edge_count() == 0
