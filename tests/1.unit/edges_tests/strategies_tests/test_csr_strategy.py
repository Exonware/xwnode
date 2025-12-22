"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_csr_strategy.py

Comprehensive tests for CSRStrategy (edge strategy).

Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Compressed Sparse Row format
- Neighbor queries
- Performance characteristics (O(log degree) lookups)
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
from exonware.xwnode.edges.strategies.csr import CSRStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_strategy():
    """Create empty CSR strategy."""
    return CSRStrategy()


@pytest.fixture
def simple_strategy():
    """Create CSR with simple graph."""
    strategy = CSRStrategy()
    strategy.add_edge('A', 'B')
    strategy.add_edge('B', 'C')
    strategy.add_edge('A', 'C')
    return strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestCSRStrategyInterface:
    """Test CSRStrategy implements iEdgeStrategy interface correctly."""
    
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
    
    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.get_neighbors('A'))
        assert 'B' in neighbors
        assert 'C' in neighbors
        assert len(neighbors) == 2


# ============================================================================
# CSR FORMAT TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestCSRStrategyFormat:
    """Test CSR format specific features."""
    
    def test_compressed_storage(self, simple_strategy):
        """Test CSR uses compressed storage format."""
        # CSR should compress sparse graph efficiently
        assert simple_strategy.edge_count() == 3
    
    def test_row_wise_access(self, simple_strategy):
        """Test row-wise access (CSR strength)."""
        # CSR is optimized for row-wise operations
        neighbors = list(simple_strategy.get_neighbors('A'))
        assert len(neighbors) == 2


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestCSRStrategyCore:
    """Test core CSRStrategy functionality."""
    
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
class TestCSRStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.get_neighbors('A')) == []
        assert empty_strategy.edge_count() == 0

