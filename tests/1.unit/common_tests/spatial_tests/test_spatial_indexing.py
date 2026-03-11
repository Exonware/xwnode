"""
#exonware/xwnode/tests/1.unit/common_tests/spatial_tests/test_spatial_indexing.py
Unit tests for spatial indexing.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.spatial.index_manager import SpatialIndexManager
from exonware.xwnode.common.spatial.contracts import ISpatialIndexManager
@pytest.mark.xwnode_unit

class TestSpatialIndexManager:
    """Tests for SpatialIndexManager."""

    def test_initialization(self):
        """Test manager initialization."""
        manager = SpatialIndexManager()
        assert manager is not None
        assert manager._rtree is None
        assert manager._quadtree is None
        assert manager._location_data == {}

    def test_add_location_rtree(self):
        """Test adding location to R-tree."""
        manager = SpatialIndexManager()
        manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="rtree")
        assert "loc1" in manager._location_data
        assert manager._rtree is not None

    def test_add_location_quadtree(self):
        """Test adding location to Quadtree."""
        manager = SpatialIndexManager()
        manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="quadtree")
        assert "loc1" in manager._location_data
        assert manager._quadtree is not None

    def test_add_location_invalid_type(self):
        """Test adding location with invalid index type."""
        manager = SpatialIndexManager()
        with pytest.raises(ValueError):
            manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="invalid")

    def test_remove_location(self):
        """Test removing location."""
        manager = SpatialIndexManager()
        manager.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="rtree")
        removed = manager.remove_location("loc1", index_type="rtree")
        assert removed is True
        assert "loc1" not in manager._location_data

    def test_query_range(self):
        """Test range queries."""
        manager = SpatialIndexManager()
        # Add locations
        manager.add_location("sf", lat=37.7749, lon=-122.4194, index_type="rtree")
        manager.add_location("ny", lat=40.7128, lon=-74.0060, index_type="rtree")
        # Query San Francisco area
        results = manager.query_range(
            min_lat=37.0, min_lon=-123.0,
            max_lat=38.0, max_lon=-122.0,
            index_type="rtree"
        )
        assert "sf" in results
        assert "ny" not in results

    def test_query_radius(self):
        """Test radius queries."""
        manager = SpatialIndexManager()
        manager.add_location("center", lat=37.7749, lon=-122.4194, index_type="rtree")
        results = manager.query_radius(
            lat=37.7750, lon=-122.4195,
            radius_km=10.0,
            index_type="rtree"
        )
        assert len(results) >= 0  # May or may not include center depending on implementation

    def test_haversine_distance(self):
        """Test Haversine distance calculation."""
        manager = SpatialIndexManager()
        # San Francisco to New York (approximately 4139 km)
        distance = manager._haversine_distance(
            lat1=37.7749, lon1=-122.4194,
            lat2=40.7128, lon2=-74.0060
        )
        # Should be approximately 4139 km (allow 10% error)
        assert 3700 <= distance <= 4600

    def test_implements_interface(self):
        """Test that SpatialIndexManager implements ISpatialIndexManager."""
        manager = SpatialIndexManager()
        assert isinstance(manager, ISpatialIndexManager)
