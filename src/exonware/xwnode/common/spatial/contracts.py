"""
#exonware/xwnode/src/exonware/xwnode/common/spatial/contracts.py
Spatial indexing contracts for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
Generation Date: 01-Jan-2026
"""

from typing import Any, Optional, Protocol, runtime_checkable
from collections.abc import Sequence
@runtime_checkable

class ISpatialIndexManager(Protocol):
    """
    Interface for spatial index manager.
    Provides management for R-tree and Quadtree spatial indices.
    """

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
        ...

    def remove_location(self, id: str, index_type: Optional[str] = None) -> bool:
        """
        Remove location from spatial index.
        Args:
            id: Location identifier
            index_type: Optional index type (None = remove from all)
        Returns:
            True if removed, False if not found
        """
        ...

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
        ...

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
        ...
@runtime_checkable

class IGeofenceIndex(Protocol):
    """
    Interface for geofence index.
    Provides geofencing operations using spatial indices.
    """

    def add_geofence(
        self,
        id: str,
        bounds: dict[str, float],
        index_type: str = "rtree"
    ) -> None:
        """
        Add geofence to index.
        Args:
            id: Geofence identifier
            bounds: Bounding box {min_lat, min_lon, max_lat, max_lon}
            index_type: Index type to use
        """
        ...

    def check_location(
        self,
        lat: float,
        lon: float,
        index_type: str = "rtree"
    ) -> list[str]:
        """
        Check which geofences contain location.
        Args:
            lat: Latitude
            lon: Longitude
            index_type: Index type to query
        Returns:
            List of geofence identifiers containing location
        """
        ...

    def remove_geofence(self, id: str, index_type: Optional[str] = None) -> bool:
        """
        Remove geofence from index.
        Args:
            id: Geofence identifier
            index_type: Optional index type (None = remove from all)
        Returns:
            True if removed, False if not found
        """
        ...
