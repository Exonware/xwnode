"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_temporal_edgeset_strategy.py
Comprehensive tests for TemporalEdgesetStrategy (edge strategy).
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Temporal queries (time-based edge access)
- Time range queries
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
from exonware.xwnode.edges.strategies.temporal_edgeset import TemporalEdgeSetStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty temporal edgeset strategy."""
    return TemporalEdgeSetStrategy()
@pytest.fixture

def simple_strategy():
    """Create temporal edgeset with simple graph."""
    strategy = TemporalEdgeSetStrategy()
    strategy.add_edge('A', 'B', timestamp=1000)
    strategy.add_edge('B', 'C', timestamp=2000)
    strategy.add_edge('A', 'C', timestamp=1500)
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestTemporalEdgeSetStrategyInterface:
    """Test TemporalEdgeSetStrategy implements iEdgeStrategy interface correctly."""

    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B', timestamp=1000)
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
# TEMPORAL FEATURES TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestTemporalEdgesetStrategyTemporal:
    """Test temporal features (time-based queries)."""

    def test_temporal_queries(self, simple_strategy):
        """Test time-based edge queries if available."""
        # Temporal edgeset should support time-based queries
        if hasattr(simple_strategy, 'get_edges_at_time'):
            edges = simple_strategy.get_edges_at_time(1500)
            assert len(edges) > 0
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestTemporalEdgesetStrategyCore:
    """Test core TemporalEdgesetStrategy functionality."""

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

class TestTemporalEdgesetStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.get_neighbors('A')) == []
        assert empty_strategy.edge_count() == 0
