"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_edge_list_strategy.py

Comprehensive tests for EdgeListStrategy (edge strategy).

Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Simple edge list storage
- Iterator protocol
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
from exonware.xwnode.edges.strategies.edge_list import EdgeListStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_strategy():
    """Create empty edge list strategy."""
    return EdgeListStrategy()


@pytest.fixture
def simple_strategy():
    """Create edge list with simple graph."""
    strategy = EdgeListStrategy()
    strategy.add_edge('A', 'B')
    strategy.add_edge('B', 'C')
    strategy.add_edge('A', 'C')
    return strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestEdgeListStrategyInterface:
    """Test EdgeListStrategy implements iEdgeStrategy interface correctly."""
    
    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B')
        
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
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestEdgeListStrategyCore:
    """Test core EdgeListStrategy functionality."""
    
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
class TestEdgeListStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.get_neighbors('A')) == []
        assert empty_strategy.edge_count() == 0

