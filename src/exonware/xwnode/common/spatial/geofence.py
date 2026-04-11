"""
#exonware/xwnode/src/exonware/xwnode/common/spatial/geofence.py
Geofence index implementation for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.24
Generation Date: 01-Jan-2026
"""

from .contracts import IGeofenceIndex
from .index_manager import SpatialIndexManager


class GeofenceIndex:
    """
    Geofence index for geofencing operations.
    Uses spatial indices for efficient geofence queries.
    """

    def __init__(self, index_manager: SpatialIndexManager | None = None):
        """
        Initialize geofence index.
        Args:
            index_manager: Optional spatial index manager (creates new if None)
        """
        self._index_manager = index_manager or SpatialIndexManager()
        self._geofence_bounds: dict[str, dict[str, float]] = {}

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
        min_lat = bounds.get('min_lat')
        min_lon = bounds.get('min_lon')
        max_lat = bounds.get('max_lat')
        max_lon = bounds.get('max_lon')
        if None in (min_lat, min_lon, max_lat, max_lon):
            raise ValueError("Bounds must contain min_lat, min_lon, max_lat, max_lon")
        # Store bounds
        self._geofence_bounds[id] = bounds
        # Add center point to spatial index for quick lookup
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        # Use geofence ID with prefix
        self._index_manager.add_location(
            f"geofence_{id}",
            center_lat,
            center_lon,
            index_type
        )

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
        results: list[str] = []
        # Query nearby geofences (using radius query)
        # Use a small radius to get candidates, then check bounds
        candidates = self._index_manager.query_radius(
            lat, lon, 10.0, index_type  # 10km radius for candidates
        )
        # Check each geofence bounds
        for candidate_id in candidates:
            if candidate_id.startswith("geofence_"):
                geofence_id = candidate_id.replace("geofence_", "")
                if geofence_id in self._geofence_bounds:
                    bounds = self._geofence_bounds[geofence_id]
                    if (bounds['min_lat'] <= lat <= bounds['max_lat'] and
                        bounds['min_lon'] <= lon <= bounds['max_lon']):
                        results.append(geofence_id)
        return results

    def remove_geofence(self, id: str, index_type: str | None = None) -> bool:
        """Remove geofence from index."""
        removed = False
        if id in self._geofence_bounds:
            self._geofence_bounds.pop(id)
            removed = True
        # Remove from spatial index
        if self._index_manager.remove_location(f"geofence_{id}", index_type):
            removed = True
        return removed
