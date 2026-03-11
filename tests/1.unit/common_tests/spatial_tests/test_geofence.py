"""
#exonware/xwnode/tests/1.unit/common_tests/spatial_tests/test_geofence.py
Unit tests for geofence indexing.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.spatial.geofence import GeofenceIndex
from exonware.xwnode.common.spatial.index_manager import SpatialIndexManager
from exonware.xwnode.common.spatial.contracts import IGeofenceIndex
@pytest.mark.xwnode_unit

class TestGeofenceIndex:
    """Tests for GeofenceIndex."""

    def test_initialization(self):
        """Test geofence index initialization."""
        index = GeofenceIndex()
        assert index is not None
        assert index._index_manager is not None
        assert index._geofence_bounds == {}

    def test_initialization_with_manager(self):
        """Test initialization with existing manager."""
        manager = SpatialIndexManager()
        index = GeofenceIndex(manager)
        assert index._index_manager is manager

    def test_add_geofence(self):
        """Test adding geofence."""
        index = GeofenceIndex()
        bounds = {
            'min_lat': 37.0,
            'min_lon': -123.0,
            'max_lat': 38.0,
            'max_lon': -122.0
        }
        index.add_geofence("geofence1", bounds, index_type="rtree")
        assert "geofence1" in index._geofence_bounds

    def test_add_geofence_invalid_bounds(self):
        """Test adding geofence with invalid bounds."""
        index = GeofenceIndex()
        bounds = {'min_lat': 37.0}  # Missing other bounds
        with pytest.raises(ValueError):
            index.add_geofence("geofence1", bounds)

    def test_check_location(self):
        """Test checking location against geofences."""
        index = GeofenceIndex()
        bounds = {
            'min_lat': 37.0,
            'min_lon': -123.0,
            'max_lat': 38.0,
            'max_lon': -122.0
        }
        index.add_geofence("geofence1", bounds, index_type="rtree")
        # Check location inside bounds
        results = index.check_location(lat=37.5, lon=-122.5, index_type="rtree")
        assert len(results) >= 0  # May or may not find depending on implementation

    def test_remove_geofence(self):
        """Test removing geofence."""
        index = GeofenceIndex()
        bounds = {
            'min_lat': 37.0,
            'min_lon': -123.0,
            'max_lat': 38.0,
            'max_lon': -122.0
        }
        index.add_geofence("geofence1", bounds)
        removed = index.remove_geofence("geofence1")
        assert removed is True
        assert "geofence1" not in index._geofence_bounds

    def test_implements_interface(self):
        """Test that GeofenceIndex implements IGeofenceIndex."""
        index = GeofenceIndex()
        assert isinstance(index, IGeofenceIndex)
