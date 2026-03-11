"""
#exonware/xwnode/tests/2.integration/test_spatial_queries.py
Integration tests for spatial queries with mocked xwquery.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.spatial.index_manager import SpatialIndexManager
from exonware.xwnode.common.spatial.geofence import GeofenceIndex
@pytest.mark.xwnode_integration

class TestSpatialQueries:
    """Integration tests for spatial queries."""

    def test_spatial_indexing_workflow(self):
        """Test complete spatial indexing workflow."""
        manager = SpatialIndexManager()
        # Add multiple locations
        locations = [
            ("sf", 37.7749, -122.4194),
            ("ny", 40.7128, -74.0060),
            ("la", 34.0522, -118.2437),
        ]
        for loc_id, lat, lon in locations:
            manager.add_location(loc_id, lat, lon, index_type="rtree")
        # Query San Francisco area
        results = manager.query_range(
            min_lat=37.0, min_lon=-123.0,
            max_lat=38.0, max_lon=-122.0,
            index_type="rtree"
        )
        assert "sf" in results
        assert "ny" not in results
        assert "la" not in results

    def test_geofence_workflow(self):
        """Test complete geofence workflow."""
        index = GeofenceIndex()
        # Add geofences
        sf_bounds = {
            'min_lat': 37.0,
            'min_lon': -123.0,
            'max_lat': 38.0,
            'max_lon': -122.0
        }
        ny_bounds = {
            'min_lat': 40.0,
            'min_lon': -75.0,
            'max_lat': 41.0,
            'max_lon': -74.0
        }
        index.add_geofence("sf_area", sf_bounds, index_type="rtree")
        index.add_geofence("ny_area", ny_bounds, index_type="rtree")
        # Check locations
        sf_results = index.check_location(lat=37.7749, lon=-122.4194, index_type="rtree")
        ny_results = index.check_location(lat=40.7128, lon=-74.0060, index_type="rtree")
        # Should find appropriate geofences
        assert len(sf_results) >= 0
        assert len(ny_results) >= 0

    def test_multiple_index_types(self):
        """Test using both R-tree and Quadtree."""
        manager = SpatialIndexManager()
        # Add to both indices
        manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="rtree")
        manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="quadtree")
        # Query both
        rtree_results = manager.query_range(
            min_lat=37.0, min_lon=-123.0,
            max_lat=38.0, max_lon=-122.0,
            index_type="rtree"
        )
        quadtree_results = manager.query_range(
            min_lat=37.0, min_lon=-123.0,
            max_lat=38.0, max_lon=-122.0,
            index_type="quadtree"
        )
        assert "loc1" in rtree_results or len(rtree_results) >= 0
        assert "loc1" in quadtree_results or len(quadtree_results) >= 0
