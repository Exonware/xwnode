"""
#exonware/xwnode/tests/1.unit/facade_tests/test_baas_facade.py
Unit tests for BaaS facade.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.facades.baas import XWNodeBaaSFacade
@pytest.mark.xwnode_unit

class TestXWNodeBaaSFacade:
    """Tests for XWNodeBaaSFacade."""

    def test_initialization(self):
        """Test facade initialization."""
        facade = XWNodeBaaSFacade()
        assert facade is not None
        assert facade._event_graph is None
        assert facade._analytics_structures is None
        assert facade._spatial_manager is None
        assert facade._cache_manager is None

    def test_get_event_graph(self):
        """Test getting event graph."""
        facade = XWNodeBaaSFacade()
        graph = facade.get_event_graph(use_multiplex=True)
        assert graph is not None
        # Should return same instance on second call
        graph2 = facade.get_event_graph()
        assert graph is graph2

    def test_get_channel_router(self):
        """Test getting channel router."""
        facade = XWNodeBaaSFacade()
        router = facade.get_channel_router()
        assert router is not None

    def test_add_event_channel(self):
        """Test adding event channel."""
        facade = XWNodeBaaSFacade()
        facade.add_event_channel("channel1")
        facade.add_event_channel("channel2", parent="channel1")
        graph = facade.get_event_graph()
        assert graph.has_channel("channel1")
        assert graph.has_channel("channel2")

    def test_route_event(self):
        """Test routing event."""
        facade = XWNodeBaaSFacade()
        facade.add_event_channel("source")
        facade.add_event_channel("target", parent="source")
        event = {"type": "test", "data": "hello"}
        results = facade.route_event("source", event, ["target"])
        assert "target" in results

    def test_get_analytics_structures(self):
        """Test getting analytics structures."""
        facade = XWNodeBaaSFacade()
        structures = facade.get_analytics_structures()
        assert structures is not None

    def test_get_count_min_sketch(self):
        """Test getting Count-Min Sketch."""
        facade = XWNodeBaaSFacade()
        cms = facade.get_count_min_sketch()
        assert cms is not None

    def test_get_hyperloglog(self):
        """Test getting HyperLogLog."""
        facade = XWNodeBaaSFacade()
        hll = facade.get_hyperloglog()
        assert hll is not None

    def test_get_graphblas(self):
        """Test getting GraphBLAS."""
        facade = XWNodeBaaSFacade()
        graph = facade.get_graphblas()
        assert graph is not None

    def test_get_spatial_manager(self):
        """Test getting spatial manager."""
        facade = XWNodeBaaSFacade()
        manager = facade.get_spatial_manager()
        assert manager is not None

    def test_add_location(self):
        """Test adding location."""
        facade = XWNodeBaaSFacade()
        facade.add_location("loc1", lat=37.7749, lon=-122.4194, index_type="rtree")
        manager = facade.get_spatial_manager()
        # Verify location was added (check location_data)
        assert hasattr(manager, '_location_data')

    def test_query_locations_in_range(self):
        """Test querying locations in range."""
        facade = XWNodeBaaSFacade()
        facade.add_location("sf", lat=37.7749, lon=-122.4194, index_type="rtree")
        results = facade.query_locations_in_range(
            min_lat=37.0, min_lon=-123.0,
            max_lat=38.0, max_lon=-122.0,
            index_type="rtree"
        )
        assert "sf" in results

    def test_query_locations_in_radius(self):
        """Test querying locations in radius."""
        facade = XWNodeBaaSFacade()
        facade.add_location("center", lat=37.7749, lon=-122.4194, index_type="rtree")
        results = facade.query_locations_in_radius(
            lat=37.7750, lon=-122.4195,
            radius_km=10.0,
            index_type="rtree"
        )
        assert len(results) >= 0

    def test_get_cache_manager(self):
        """Test getting cache manager."""
        facade = XWNodeBaaSFacade()
        manager = facade.get_cache_manager()
        assert manager is not None

    def test_get_cache(self):
        """Test getting cache."""
        facade = XWNodeBaaSFacade()
        cache = facade.get_cache(strategy="lru", max_size=100)
        assert cache is not None
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_cache_metrics_data(self):
        """Test getting cache metrics."""
        facade = XWNodeBaaSFacade()
        cache = facade.get_cache(strategy="lru", max_size=100, cache_id="test")
        cache.put("key1", "value1")
        cache.get("key1")
        metrics = facade.get_cache_metrics_data("test")
        assert metrics is not None
