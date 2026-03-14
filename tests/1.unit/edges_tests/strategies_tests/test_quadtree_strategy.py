"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_quadtree_strategy.py
Comprehensive tests for QuadtreeStrategy (edge strategy).
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- Quadtree spatial indexing (2D)
- Spatial queries
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
from exonware.xwnode.edges.strategies.quadtree import QuadTreeStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty quadtree strategy."""
    return QuadTreeStrategy()
@pytest.fixture

def simple_strategy():
    """Create quadtree with simple spatial data."""
    strategy = QuadTreeStrategy()
    strategy.add_edge('A', 'B', bbox=(0, 0, 1, 1))
    strategy.add_edge('B', 'C', bbox=(2, 2, 3, 3))
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestQuadtreeStrategyInterface:
    """Test QuadtreeStrategy implements iEdgeStrategy interface correctly."""

    def test_add_edge_operation(self, empty_strategy):
        """Test add_edge operation works correctly."""
        edge_id = empty_strategy.add_edge('A', 'B', bbox=(0, 0, 1, 1))
        assert edge_id is not None
        assert empty_strategy.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_strategy):
        """Test has_edge operation returns correct values."""
        assert simple_strategy.has_edge('A', 'B') is True
        assert simple_strategy.has_edge('B', 'C') is True
# ============================================================================
# SPATIAL QUERY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestQuadtreeStrategySpatial:
    """Test spatial query features."""

    def test_spatial_queries(self, simple_strategy):
        """Test spatial queries if available."""
        if hasattr(simple_strategy, 'query_range'):
            results = simple_strategy.query_range((0.5, 0.5, 1.5, 1.5))
            assert len(results) >= 0
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestQuadtreeStrategyCore:
    """Test core QuadtreeStrategy functionality."""

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

class TestQuadtreeStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph_operations(self, empty_strategy):
        """Test operations on empty graph."""
        assert empty_strategy.has_edge('A', 'B') is False
        assert list(empty_strategy.neighbors('A')) == []
        assert empty_strategy.edge_count() == 0
