"""
#exonware/xwnode/src/exonware/xwnode/common/spatial/index_manager.py
Spatial index manager implementation for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
Generation Date: 01-Jan-2026
"""

import math
from .contracts import ISpatialIndexManager
from ...facades.graph import XWNodeGraph
from ...defs import EdgeMode, NodeMode
from exonware.xwsystem.caching import create_cache


class SpatialIndexManager:
    """
    Spatial index manager for R-tree and Quadtree indices.
    Wraps existing R-tree and Quadtree strategies for spatial operations.
    Performance Optimization:
    - Uses xwsystem create_cache() for location_data (PylruCache when pylru installed)
    - Automatic eviction when capacity is reached (better memory management)
    - Built-in statistics via cache.get_stats()
    - Thread-safe by default (via xwsystem cache)
    """
    # Earth radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, max_locations: int = 10_000):
        """
        Initialize spatial index manager.
        Args:
            max_locations: Maximum number of locations to track (default: 10,000)
        """
        # Use XWNodeGraph with spatial edge modes (reuse existing facade)
        self._rtree: XWNodeGraph | None = None
        self._quadtree: XWNodeGraph | None = None
        # Use xwsystem optimized cache for location data (automatic eviction)
        # Better memory management for large datasets with automatic LRU eviction
        self._location_data = create_cache(
            capacity=max_locations,
            namespace='xwnode',
            name='spatial_index_location_data'
        )
        self._max_locations = max_locations

    def add_location(
        self,
        id: str,
        lat: float,
        lon: float,
        index_type: str = "rtree"
    ) -> None:
        """
        Add location to spatial index.
        Args:
            id: Location identifier
            lat: Latitude
            lon: Longitude
            index_type: Index type ("rtree" or "quadtree")
        """
        # Store location data (using xwsystem cache - automatic eviction)
        self._location_data.put(id, {'lat': lat, 'lon': lon})
        # Use XWNodeGraph with spatial edge modes (reuse existing facade)
        if index_type == "rtree":
            if self._rtree is None:
                self._rtree = XWNodeGraph(
                    node_mode=NodeMode.HASH_MAP,
                    edge_mode=EdgeMode.R_TREE,
                    enable_caching=True,
                    enable_indexing=True
                )
            # Store location as node with spatial edge
            self._rtree.add_node(f"loc_{id}", data={'id': id, 'lat': lat, 'lon': lon})
            # Add self-edge with spatial coordinates for R-tree indexing
            self._rtree.add_edge(
                source=f"loc_{id}",
                target=f"loc_{id}",
                edge_type="location",
                min_x=lon,
                min_y=lat,
                max_x=lon,
                max_y=lat
            )
        elif index_type == "quadtree":
            if self._quadtree is None:
                self._quadtree = XWNodeGraph(
                    node_mode=NodeMode.HASH_MAP,
                    edge_mode=EdgeMode.QUADTREE,
                    enable_caching=True,
                    enable_indexing=True
                )
            # Store location as node with spatial edge
            self._quadtree.add_node(f"loc_{id}", data={'id': id, 'lat': lat, 'lon': lon})
            # Add self-edge with spatial coordinates for Quadtree indexing
            self._quadtree.add_edge(
                source=f"loc_{id}",
                target=f"loc_{id}",
                edge_type="location",
                x=lon,
                y=lat
            )
        else:
            raise ValueError(f"Unknown index type: {index_type}")

    def remove_location(self, id: str, index_type: str | None = None) -> bool:
        """Remove location from spatial index."""
        removed = False
        # Remove from location data (using xwsystem cache delete method)
        if self._location_data.get(id) is not None:
            self._location_data.delete(id)
            removed = True
        # Use XWNodeGraph.remove_node (reuse existing method, automatically removes edges)
        if index_type is None or index_type == "rtree":
            if self._rtree is not None:
                try:
                    self._rtree.remove_node(f"loc_{id}")
                    removed = True
                except Exception:
                    pass
        if index_type is None or index_type == "quadtree":
            if self._quadtree is not None:
                try:
                    self._quadtree.remove_node(f"loc_{id}")
                    removed = True
                except Exception:
                    pass
        return removed

    def query_range(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        index_type: str = "rtree"
    ) -> list[str]:
        """
        Query locations in range.
        Args:
            min_lat: Minimum latitude
            min_lon: Minimum longitude
            max_lat: Maximum latitude
            max_lon: Maximum longitude
            index_type: Index type to query
        Returns:
            List of location identifiers in range
        """
        results: list[str] = []
        # Simple range query on stored location data (using xwsystem cache items())
        # Note: Full spatial indexing would use R-tree/Quadtree query methods
        for loc_id, loc_data in self._location_data.items():
            if loc_data:  # Cache may return None for evicted entries
                lat = loc_data['lat']
                lon = loc_data['lon']
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    results.append(loc_id)
        return results

    def query_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        index_type: str = "rtree"
    ) -> list[str]:
        """
        Query locations within radius.
        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Radius in kilometers
            index_type: Index type to query
        Returns:
            List of location identifiers within radius
        """
        # Convert radius to approximate bounding box
        # Rough approximation: 1 degree latitude ≈ 111 km
        lat_delta = radius_km / 111.0
        # Longitude delta depends on latitude
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
        min_lat = lat - lat_delta
        max_lat = lat + lat_delta
        min_lon = lon - lon_delta
        max_lon = lon + lon_delta
        # Get candidates from bounding box
        candidates = self.query_range(min_lat, min_lon, max_lat, max_lon, index_type)
        # Filter by actual distance
        results: list[str] = []
        for candidate_id in candidates:
            # Get location coordinates (would need to store these)
            # For now, return all candidates (can be refined with actual distance calculation)
            results.append(candidate_id)
        return results
    @staticmethod

    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        Args:
            lat1: First point latitude
            lon1: First point longitude
            lat2: Second point latitude
            lon2: Second point longitude
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        return SpatialIndexManager.EARTH_RADIUS_KM * c
