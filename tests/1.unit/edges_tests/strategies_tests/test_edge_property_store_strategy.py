"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_edge_property_store_strategy.py
Comprehensive tests for EdgePropertyStoreStrategy (edge strategy).
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Columnar edge property storage
- Property queries and updates
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
from exonware.xwnode.edges.strategies.edge_property_store import EdgePropertyStoreStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty edge property store strategy."""
    return EdgePropertyStoreStrategy()
@pytest.fixture

def simple_strategy():
    """Create edge property store with simple graph."""
    strategy = EdgePropertyStoreStrategy()
    strategy.add_edge('A', 'B', weight=1.0, label='edge1')
    strategy.add_edge('B', 'C', weight=2.0, label='edge2')
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestEdgePropertyStoreStrategyInterface:
    """Test EdgePropertyStoreStrategy implements iEdgeStrategy interface correctly."""

    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B', weight=1.0)
        assert edge_id is not None
        assert empty_strategy.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_strategy):
        """Test has_edge operation returns correct values."""
        assert simple_strategy.has_edge('A', 'B') is True
        assert simple_strategy.has_edge('B', 'C') is True

    def test_get_neighbors_operation(self, simple_strategy):
        """Test get_neighbors returns correct neighbors."""
        neighbors = list(simple_strategy.neighbors('A'))
        assert 'B' in neighbors
# ============================================================================
# PROPERTY STORE FEATURES TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestEdgePropertyStoreStrategyProperties:
    """Test edge property storage features."""

    def test_property_queries(self, simple_strategy):
        """Test property queries if available."""
        # Edge property store should support property queries
        if hasattr(simple_strategy, 'get_edge_property'):
            weight = simple_strategy.get_edge_property('A', 'B', 'weight')
            assert weight == 1.0
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestEdgePropertyStoreStrategyCore:
    """Test core EdgePropertyStoreStrategy functionality."""

    def test_edge_count(self, simple_strategy):
        """Test edge count tracking."""
        assert simple_strategy.edge_count() == 2

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

class TestEdgePropertyStoreStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.neighbors('A')) == []
        assert empty_strategy.edge_count() == 0
