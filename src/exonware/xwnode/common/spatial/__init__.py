"""
#exonware/xwnode/src/exonware/xwnode/common/spatial/__init__.py
Spatial indexing module for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
Generation Date: 01-Jan-2026
"""

from .contracts import ISpatialIndexManager, IGeofenceIndex
from .index_manager import SpatialIndexManager
from .geofence import GeofenceIndex
__all__ = [
    'ISpatialIndexManager',
    'IGeofenceIndex',
    'SpatialIndexManager',
    'GeofenceIndex',
]
