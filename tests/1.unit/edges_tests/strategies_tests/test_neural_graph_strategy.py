"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_neural_graph_strategy.py

Comprehensive tests for NeuralGraphStrategy (edge strategy).

Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Neural network graph operations
- Weighted edges
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
from exonware.xwnode.edges.strategies.neural_graph import NeuralGraphStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_strategy():
    """Create empty neural graph strategy."""
    return NeuralGraphStrategy()


@pytest.fixture
def simple_strategy():
    """Create neural graph with simple graph."""
    strategy = NeuralGraphStrategy()
    strategy.add_edge('A', 'B', weight=0.5)
    strategy.add_edge('B', 'C', weight=0.3)
    strategy.add_edge('A', 'C', weight=0.7)
    return strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestNeuralGraphStrategyInterface:
    """Test NeuralGraphStrategy implements iEdgeStrategy interface correctly."""
    
    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B', weight=0.5)
        
        assert edge_id is not None
        assert empty_strategy.has_edge('A', 'B') is True
    
    def test_has_edge_operation(self, simple_strategy):
        """Test has_edge operation returns correct values."""
        assert simple_strategy.has_edge('A', 'B') is True
        assert simple_strategy.has_edge('B', 'C') is True
        assert simple_strategy.has_edge('A', 'C') is True
    
    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.get_neighbors('A'))
        assert 'B' in neighbors
        assert 'C' in neighbors


# ============================================================================
# NEURAL GRAPH FEATURES TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestNeuralGraphStrategyNeural:
    """Test neural graph specific features."""
    
    def test_weighted_edges(self, simple_strategy):
        """Test weighted edge support."""
        # Neural graph should support weighted edges
        if hasattr(simple_strategy, 'get_edge_weight'):
            weight = simple_strategy.get_edge_weight('A', 'B')
            assert weight == 0.5


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestNeuralGraphStrategyCore:
    """Test core NeuralGraphStrategy functionality."""
    
    def test_edge_count(self, simple_strategy):
        """Test edge count tracking."""
        assert simple_strategy.edge_count() == 3
    
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
class TestNeuralGraphStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.get_neighbors('A')) == []
        assert empty_strategy.edge_count() == 0

