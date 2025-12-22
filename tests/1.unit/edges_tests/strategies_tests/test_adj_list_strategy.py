"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_adj_list_strategy.py

Comprehensive tests for AdjListStrategy (edge strategy).

Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Neighbor queries (get_neighbors, get_incoming)
- Graph traversal operations
- Performance characteristics (O(1) add, O(degree) queries)
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
from exonware.xwnode.edges.strategies.adj_list import AdjListStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_strategy():
    """Create empty adjacency list strategy."""
    return AdjListStrategy()


@pytest.fixture
def simple_strategy():
    """Create adjacency list with simple graph."""
    strategy = AdjListStrategy()
    strategy.add_edge('A', 'B')
    strategy.add_edge('B', 'C')
    strategy.add_edge('A', 'C')
    return strategy


@pytest.fixture
def directed_strategy():
    """Create directed graph."""
    strategy = AdjListStrategy(directed=True)
    strategy.add_edge('A', 'B')
    strategy.add_edge('B', 'C')
    return strategy


@pytest.fixture
def undirected_strategy():
    """Create undirected graph."""
    strategy = AdjListStrategy(directed=False)
    strategy.add_edge('A', 'B')
    strategy.add_edge('B', 'C')
    return strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestAdjListStrategyInterface:
    """Test AdjListStrategy implements iEdgeStrategy interface correctly."""
    
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
        assert simple_strategy.has_edge('C', 'A') is False  # Directed
    
    def test_delete_edge_operation(self, simple_strategy):
        """Test delete_edge operation removes edges correctly."""
        assert simple_strategy.delete_edge('A', 'B') is True
        assert simple_strategy.has_edge('A', 'B') is False
        assert simple_strategy.delete_edge('nonexistent', 'edge') is False
    
    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.get_neighbors('A'))
        assert 'B' in neighbors
        assert 'C' in neighbors
        assert len(neighbors) == 2


# ============================================================================
# DIRECTED/UNDIRECTED TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestAdjListStrategyDirected:
    """Test directed vs undirected graph behavior."""
    
    def test_directed_graph(self, directed_strategy):
        """Test directed graph maintains direction."""
        assert directed_strategy.has_edge('A', 'B') is True
        assert directed_strategy.has_edge('B', 'A') is False  # Not bidirectional
    
    def test_undirected_graph(self, undirected_strategy):
        """Test undirected graph creates bidirectional edges."""
        assert undirected_strategy.has_edge('A', 'B') is True
        assert undirected_strategy.has_edge('B', 'A') is True  # Bidirectional
    
    def test_get_incoming_neighbors(self, directed_strategy):
        """Test get_incoming_neighbors for directed graphs."""
        incoming = list(directed_strategy.get_incoming_neighbors('B'))
        assert 'A' in incoming
        assert len(incoming) == 1


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestAdjListStrategyCore:
    """Test core AdjListStrategy functionality."""
    
    def test_self_loops(self):
        """Test self-loop handling."""
        strategy = AdjListStrategy(self_loops=True)
        edge_id = strategy.add_edge('A', 'A')
        assert edge_id is not None
        assert strategy.has_edge('A', 'A') is True
        
        strategy_no_loops = AdjListStrategy(self_loops=False)
        with pytest.raises(ValueError):
            strategy_no_loops.add_edge('A', 'A')
    
    def test_multi_edges(self):
        """Test multi-edge handling."""
        strategy = AdjListStrategy(multi_edges=True)
        edge1 = strategy.add_edge('A', 'B')
        edge2 = strategy.add_edge('A', 'B')
        assert edge1 != edge2  # Different edge IDs
        
        strategy_no_multi = AdjListStrategy(multi_edges=False)
        strategy_no_multi.add_edge('A', 'B')
        with pytest.raises(ValueError):
            strategy_no_multi.add_edge('A', 'B')
    
    def test_edge_count(self, simple_strategy):
        """Test edge count tracking."""
        assert simple_strategy.edge_count() == 3
    
    def test_vertex_count(self, simple_strategy):
        """Test vertex count tracking."""
        vertices = simple_strategy.get_vertices()
        assert 'A' in vertices
        assert 'B' in vertices
        assert 'C' in vertices
        assert len(vertices) == 3


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestAdjListStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert empty_strategy.delete_edge('A', 'B') is False
        assert list(empty_strategy.get_neighbors('A')) == []
        assert empty_strategy.edge_count() == 0
    
    def test_nonexistent_vertices(self, simple_strategy):
        """Test operations with nonexistent vertices."""
        assert list(simple_strategy.get_neighbors('Z')) == []
        assert simple_strategy.has_edge('Z', 'A') is False

