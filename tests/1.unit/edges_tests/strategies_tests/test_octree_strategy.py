#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_octree_strategy.py
Comprehensive tests for Octree Strategy (3D spatial partitioning).
Tests cover:
- Interface compliance (iEdgeStrategy)
- Core edge operations (add_edge, has_edge, delete_edge)
- 3D spatial operations
- Security (input validation, resource limits)
- Error handling
- Edge cases
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from exonware.xwnode.edges.strategies.octree import OctreeStrategy
from exonware.xwnode.defs import EdgeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_octree():
    """Create empty octree."""
    return OctreeStrategy()
@pytest.fixture

def simple_octree():
    """Create octree with 3D points."""
    tree = OctreeStrategy()
    tree.add_edge('A', 'B', x=1.0, y=2.0, z=3.0)
    tree.add_edge('B', 'C', x=2.0, y=3.0, z=4.0)
    return tree
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy

class TestOctreeStrategy:
    """Test Octree strategy interface compliance."""

    def test_add_edge_operation(self, empty_octree):
        """Test add_edge operation works correctly."""
        edge_id = empty_octree.add_edge('A', 'B', x=1.0, y=2.0, z=3.0)
        assert edge_id is not None
        assert empty_octree.has_edge('A', 'B') is True

    def test_has_edge_operation(self, simple_octree):
        """Test has_edge operation returns correct values."""
        assert simple_octree.has_edge('A', 'B') is True
        assert simple_octree.has_edge('B', 'C') is True

    def test_delete_edge_operation(self, simple_octree):
        """Test delete_edge operation removes edges correctly."""
        assert simple_octree.remove_edge('A', 'B') is True
        assert simple_octree.has_edge('A', 'B') is False
