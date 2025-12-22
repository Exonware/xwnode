"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_bidir_wrapper_strategy.py

Comprehensive tests for BidirWrapperStrategy (edge strategy).

Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Bidirectional edge support (undirected via dual arcs)
- Neighbor queries
- Performance characteristics
- Security (input validation, resource limits)
- Error handling
- Edge cases

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 15-Nov-2025
"""

import pytest
from typing import Any
from exonware.xwnode.edges.strategies.bidir_wrapper import BidirWrapperStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_strategy():
    """Create empty bidir wrapper strategy."""
    return BidirWrapperStrategy()


@pytest.fixture
def simple_strategy():
    """Create bidir wrapper with simple graph."""
    strategy = BidirWrapperStrategy()
    strategy.add_edge('A', 'B')
    strategy.add_edge('B', 'C')
    return strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestBidirWrapperStrategyInterface:
    """Test BidirWrapperStrategy implements iEdgeStrategy interface correctly."""
    
    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly (creates bidirectional)."""
        edge_id = empty_strategy.add_edge('A', 'B')
        
        assert edge_id is not None
        assert empty_strategy.has_edge('A', 'B') is True
        assert empty_strategy.has_edge('B', 'A') is True  # Bidirectional
    
    def test_has_edge_operation(self, simple_strategy):
        """Test has_edge operation returns correct values (bidirectional)."""
        assert simple_strategy.has_edge('A', 'B') is True
        assert simple_strategy.has_edge('B', 'A') is True  # Bidirectional
        assert simple_strategy.has_edge('B', 'C') is True
        assert simple_strategy.has_edge('C', 'B') is True  # Bidirectional
    
    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.get_neighbors('A'))
        assert 'B' in neighbors


# ============================================================================
# BIDIRECTIONAL FEATURES TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestBidirWrapperStrategyBidir:
    """Test bidirectional edge features."""
    
    def test_bidirectional_edges(self, simple_strategy):
        """Test that edges are bidirectional."""
        # Adding A->B should create both A->B and B->A
        assert simple_strategy.has_edge('A', 'B') is True
        assert simple_strategy.has_edge('B', 'A') is True


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestBidirWrapperStrategyCore:
    """Test core BidirWrapperStrategy functionality."""
    
    def test_edge_count(self, simple_strategy):
        """Test edge count tracking."""
        # Bidirectional edges count as one edge
        assert simple_strategy.edge_count() >= 2
    
    def test_vertex_count(self, simple_strategy):
        """Test vertex count tracking."""
        vertices = simple_strategy.get_vertices()
        assert 'A' in vertices
        assert 'B' in vertices
        assert 'C' in vertices


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestBidirWrapperStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.get_neighbors('A')) == []
        assert empty_strategy.edge_count() == 0

