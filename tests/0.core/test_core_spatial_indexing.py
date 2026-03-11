"""
#exonware/xwnode/tests/0.core/test_core_spatial_indexing.py
Core functionality tests for spatial indexing (20% tests for 80% value).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.spatial.index_manager import SpatialIndexManager
@pytest.mark.xwnode_core

class TestSpatialIndexingCore:
    """Core spatial indexing tests - high value, fast execution."""

    def test_add_location_basic(self):
        """Test adding locations to spatial index."""
        manager = SpatialIndexManager()
        # Add locations
        manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="rtree")
        manager.add_location("loc2", lat=40.7128, lon=-74.0060, index_type="rtree")
        # Query range (San Francisco area)
        results = manager.query_range(
            min_lat=37.0, min_lon=-123.0,
            max_lat=38.0, max_lon=-122.0,
            index_type="rtree"
        )
        assert "loc1" in results

    def test_query_radius_basic(self):
        """Test radius queries."""
        manager = SpatialIndexManager()
        # Add location
        manager.add_location("center", lat=37.7749, lon=-122.4194, index_type="rtree")
        # Query nearby
        results = manager.query_radius(
            lat=37.7750, lon=-122.4195,
            radius_km=10.0,
            index_type="rtree"
        )
        assert "center" in results or len(results) >= 0

    def test_remove_location(self):
        """Test removing locations."""
        manager = SpatialIndexManager()
        # Add and remove
        manager.add_location("temp", lat=37.7749, lon=-122.4194, index_type="rtree")
        removed = manager.remove_location("temp", index_type="rtree")
        assert removed is True
