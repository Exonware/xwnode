"""
#exonware/xwnode/src/exonware/xwnode/facades/baas.py
BaaS facade for xwnode BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.25
Generation Date: 01-Jan-2026
"""

from typing import Any
from collections.abc import Sequence
# Event routing
from ..common.graph.event_routing import EventChannelGraph, ChannelRouter
from ..common.graph.event_routing_contracts import IEventChannelGraph, IChannelRouter
# Analytics
from ..common.analytics.structures import AnalyticsDataStructures
from ..common.analytics.integration import AnalyticsIntegration
from ..common.analytics.contracts import IAnalyticsIntegration, IAnalyticsStructures
# Spatial
from ..common.spatial.index_manager import SpatialIndexManager
from ..common.spatial.geofence import GeofenceIndex
from ..common.spatial.contracts import ISpatialIndexManager, IGeofenceIndex
# Caching
from ..common.caching.strategy import CacheStrategyManager, CacheMetrics
from ..common.caching.contracts import ICacheStrategyManager, ICacheMetrics, ICacheAdapter


class XWNodeBaaSFacade:
    """
    BaaS facade for xwnode BaaS platform capabilities.
    Provides convenience methods for:
    - Analytics (Count-Min Sketch, HyperLogLog, GraphBLAS)
    - Event routing (channel graphs, routing)
    - Spatial indexing (R-tree, Quadtree, geofencing)
    - Cache management (LRU, LFU, FIFO, TTL strategies)
    All features are optional and can be used independently.
    """

    def __init__(self):
        """Initialize BaaS facade."""
        # Lazy initialization - only create when needed
        self._event_graph: EventChannelGraph | None = None
        self._channel_router: ChannelRouter | None = None
        self._analytics_structures: AnalyticsDataStructures | None = None
        self._analytics_integration: AnalyticsIntegration | None = None
        self._spatial_manager: SpatialIndexManager | None = None
        self._geofence_index: GeofenceIndex | None = None
        self._cache_manager: CacheStrategyManager | None = None
        self._cache_metrics: CacheMetrics | None = None
    # ============================================================================
    # EVENT ROUTING
    # ============================================================================

    def get_event_graph(self, use_multiplex: bool = True) -> IEventChannelGraph:
        """
        Get event channel graph instance.
        Args:
            use_multiplex: If True, use multiplex graph for multi-layer channels
        Returns:
            Event channel graph instance
        """
        if self._event_graph is None:
            self._event_graph = EventChannelGraph(use_multiplex=use_multiplex)
        return self._event_graph

    def get_channel_router(
        self,
        event_graph: IEventChannelGraph | None = None
    ) -> IChannelRouter:
        """
        Get channel router instance.
        Args:
            event_graph: Optional event graph (creates new if None)
        Returns:
            Channel router instance
        """
        if self._channel_router is None:
            graph = event_graph or self.get_event_graph()
            self._channel_router = ChannelRouter(graph)
        return self._channel_router

    def add_event_channel(self, channel: str, parent: str | None = None) -> None:
        """Add event channel to graph."""
        graph = self.get_event_graph()
        graph.add_channel(channel, parent)

    def route_event(
        self,
        source: str,
        event: Any,
        target_channels: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Route event to target channels."""
        router = self.get_channel_router()
        return router.route(source, event, target_channels)
    # ============================================================================
    # ANALYTICS
    # ============================================================================

    def get_analytics_structures(self) -> IAnalyticsStructures:
        """Get analytics data structures facade."""
        if self._analytics_structures is None:
            self._analytics_structures = AnalyticsDataStructures()
        return self._analytics_structures

    def get_analytics_integration(self) -> IAnalyticsIntegration:
        """Get analytics integration instance."""
        if self._analytics_integration is None:
            self._analytics_integration = AnalyticsIntegration()
        return self._analytics_integration

    def get_count_min_sketch(self, epsilon: float = 0.01, delta: float = 0.01) -> Any:
        """Get Count-Min Sketch instance for frequency estimation."""
        structures = self.get_analytics_structures()
        return structures.get_count_min_sketch(epsilon=epsilon, delta=delta)

    def get_hyperloglog(self, precision: int = 14) -> Any:
        """Get HyperLogLog instance for cardinality estimation."""
        structures = self.get_analytics_structures()
        return structures.get_hyperloglog(precision=precision)

    def get_graphblas(self) -> Any:
        """Get GraphBLAS instance for graph analytics."""
        structures = self.get_analytics_structures()
        return structures.get_graphblas()
    # ============================================================================
    # SPATIAL INDEXING
    # ============================================================================

    def get_spatial_manager(self) -> ISpatialIndexManager:
        """Get spatial index manager instance."""
        if self._spatial_manager is None:
            self._spatial_manager = SpatialIndexManager()
        return self._spatial_manager

    def get_geofence_index(
        self,
        spatial_manager: ISpatialIndexManager | None = None
    ) -> IGeofenceIndex:
        """Get geofence index instance."""
        if self._geofence_index is None:
            manager = spatial_manager or self.get_spatial_manager()
            self._geofence_index = GeofenceIndex(manager)
        return self._geofence_index

    def add_location(
        self,
        id: str,
        lat: float,
        lon: float,
        index_type: str = "rtree"
    ) -> None:
        """Add location to spatial index."""
        manager = self.get_spatial_manager()
        manager.add_location(id, lat, lon, index_type)

    def query_locations_in_range(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        index_type: str = "rtree"
    ) -> list[str]:
        """Query locations in range."""
        manager = self.get_spatial_manager()
        return manager.query_range(min_lat, min_lon, max_lat, max_lon, index_type)

    def query_locations_in_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        index_type: str = "rtree"
    ) -> list[str]:
        """Query locations within radius."""
        manager = self.get_spatial_manager()
        return manager.query_radius(lat, lon, radius_km, index_type)
    # ============================================================================
    # CACHE MANAGEMENT
    # ============================================================================

    def get_cache_manager(self) -> ICacheStrategyManager:
        """Get cache strategy manager instance."""
        if self._cache_manager is None:
            self._cache_manager = CacheStrategyManager()
        return self._cache_manager

    def get_cache_metrics(
        self,
        cache_manager: ICacheStrategyManager | None = None
    ) -> ICacheMetrics:
        """Get cache metrics instance."""
        if self._cache_metrics is None:
            manager = cache_manager or self.get_cache_manager()
            if isinstance(manager, CacheStrategyManager):
                self._cache_metrics = CacheMetrics(manager)
            else:
                raise ValueError("Cache manager must be CacheStrategyManager instance")
        return self._cache_metrics

    def get_cache(
        self,
        strategy: str = "lru",
        max_size: int = 1000,
        cache_id: str | None = None,
        **options
    ) -> ICacheAdapter:
        """Get cache instance with specified strategy."""
        manager = self.get_cache_manager()
        return manager.get_cache(strategy=strategy, max_size=max_size, cache_id=cache_id, **options)

    def get_cache_metrics_data(
        self,
        cache_id: str | None = None
    ) -> dict[str, Any]:
        """Get cache metrics data."""
        metrics = self.get_cache_metrics()
        return metrics.get_metrics(cache_id)
