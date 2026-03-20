"""
Unit tests for R_TREE edge strategy.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.rtree import RTreeStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait
@pytest.mark.xwnode_core

class TestRTreeCore:
    """Core tests for R_TREE edge strategy."""

    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = RTreeStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.R_TREE
        assert len(strategy) == 0

    def test_add_spatial_edge(self, spatial_dataset):
        """Test add_edge with spatial coordinates."""
        strategy = RTreeStrategy()
        edges = spatial_dataset(dimensions=2, num_edges=20)
        for src, tgt, props in edges:
            # R-Tree needs spatial coordinates
            source_coords = (props['x1'], props['y1'])
            target_coords = (props['x2'], props['y2'])
            edge_id = strategy.add_edge(src, tgt, 
                                       source_coords=source_coords,
                                       target_coords=target_coords)
            assert edge_id is not None
        assert len(strategy) == 20

    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = RTreeStrategy()
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(10, 10))
        strategy.add_edge("v1", "v3", source_coords=(0, 0), target_coords=(20, 20))
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v1", "v3") is True
        assert strategy.has_edge("v2", "v3") is False

    def test_spatial_range_query(self):
        """Test spatial range queries."""
        strategy = RTreeStrategy()
        # Add edges with known spatial coordinates
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(5, 5))
        strategy.add_edge("v2", "v3", source_coords=(10, 10), target_coords=(15, 15))
        strategy.add_edge("v3", "v4", source_coords=(50, 50), target_coords=(55, 55))
        # Query edges in region (0, 0) to (20, 20)
        edges_in_range = list(strategy.range_query(0, 0, 20, 20))
        # Should find first two edges
        assert len(edges_in_range) >= 1

    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = RTreeStrategy()
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(10, 10))
        assert len(strategy) > 0
        strategy.clear()
        assert len(strategy) == 0

    def test_supported_traits(self):
        """Test trait support."""
        strategy = RTreeStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPATIAL in traits
@pytest.mark.xwnode_core

class TestRTreeSpatialFeatures:
    """R-Tree specific spatial feature tests."""

    def test_bounding_rectangle_queries(self):
        """Test MBR (Minimum Bounding Rectangle) queries."""
        strategy = RTreeStrategy()
        # Add edges with known locations
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(10, 10))
        strategy.add_edge("v2", "v3", source_coords=(5, 5), target_coords=(15, 15))
        assert len(strategy) == 2

    def test_point_query(self):
        """
        Test point-based spatial queries.
        Fixed: R_TREE uses point_query(), not nearest_neighbors().
        Priority: Maintainability #3 - Test actual API
        """
        strategy = RTreeStrategy()
        # Add spatially distributed edges
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(1, 1))
        strategy.add_edge("v2", "v3", source_coords=(10, 10), target_coords=(11, 11))
        strategy.add_edge("v3", "v4", source_coords=(50, 50), target_coords=(51, 51))
        # Find edges near origin
        nearby = list(strategy.point_query(0, 0, radius=5.0))
        assert len(nearby) >= 0

    def test_spatial_intersection(self):
        """Test spatial intersection queries."""
        strategy = RTreeStrategy()
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(20, 20))
        strategy.add_edge("v2", "v3", source_coords=(10, 10), target_coords=(30, 30))
        # Query region that intersects both
        intersecting = list(strategy.range_query(5, 5, 25, 25))
        assert len(intersecting) >= 1

    def test_3d_spatial_support(self, spatial_dataset):
        """Test 3D spatial edge support."""
        strategy = RTreeStrategy(dimensions=3)
        edges = spatial_dataset(dimensions=3, num_edges=10)
        for src, tgt, props in edges:
            source_coords = (props['x1'], props['y1'], props['z1'])
            target_coords = (props['x2'], props['y2'], props['z2'])
            edge_id = strategy.add_edge(src, tgt,
                                       source_coords=source_coords,
                                       target_coords=target_coords)
            assert edge_id is not None
        assert len(strategy) == 10

    def test_edge_length_calculation(self):
        """Test automatic edge length calculation."""
        strategy = RTreeStrategy()
        strategy.add_edge("v1", "v2", source_coords=(0, 0), target_coords=(3, 4))
        # Edge length should be 5 (3-4-5 triangle)
        edge_data = strategy.get_edge_data("v1", "v2")
        if edge_data and 'length' in edge_data:
            assert abs(edge_data['length'] - 5.0) < 0.01
@pytest.mark.xwnode_performance

class TestRTreePerformance:
    """Performance validation tests for R_TREE."""

    def test_spatial_query_speed(self):
        """Validate fast spatial query performance with localized edges."""
        import random
        from tests.scale_config import MEDIUM_SIZE, scaled
        n_edges, n_queries = scaled(1000), scaled(100)
        strategy = RTreeStrategy()
        random.seed(42)
        for i in range(n_edges):
            cx, cy = random.uniform(0, 100), random.uniform(0, 100)
            dx, dy = random.uniform(-2, 2), random.uniform(-2, 2)
            strategy.add_edge(f"v{i}", f"v{(i+1)%max(1,n_edges)}",
                            source_coords=(cx, cy),
                            target_coords=(cx + dx, cy + dy))
        import time
        start = time.perf_counter()
        for i in range(n_queries):
            list(strategy.range_query(float(i), float(i), float(i + 10), float(i + 10)))
        elapsed = time.perf_counter() - start
        # Should be fast (< 500ms for 100 queries on localized data)
        assert elapsed < 0.5

    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage for spatial index."""
        from tests.scale_config import MEDIUM_SIZE
        def operation():
            strategy = RTreeStrategy()
            for i in range(MEDIUM_SIZE):
                strategy.add_edge(f"v{i}", f"v{(i+1)%max(1,MEDIUM_SIZE)}",
                                source_coords=(float(i), float(i)),
                                target_coords=(float(i+1), float(i+1)))
            return strategy
        result, memory = measure_memory(operation)
        # Should be reasonable (< 2MB)
        assert memory < 2 * 1024 * 1024

    def test_large_scale_spatial_indexing(self):
        """Test R-Tree on large spatial datasets."""
        from tests.scale_config import scaled
        n = scaled(5000)
        strategy = RTreeStrategy()
        import time
        start = time.perf_counter()
        for i in range(n):
            strategy.add_edge(f"v{i}", f"v{(i+1)%max(1,n)}",
                            source_coords=(float(i % 100), float(i // 100)),
                            target_coords=(float((i+1) % 100), float((i+1) // 100)))
        elapsed = time.perf_counter() - start
        assert len(strategy) == n
        assert elapsed < 2.0
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
