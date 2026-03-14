"""
#exonware/xwnode/src/exonware/xwnode/common/graph/contracts.py
Graph manager contracts and enums.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
Generation Date: 11-Oct-2025
"""

from enum import Enum
from typing import Any, Protocol, runtime_checkable


class GraphOptimization(Enum):
    """
    Graph optimization levels for XWGraphManager.
    Controls indexing and caching behavior for performance tuning.
    """
    OFF = 0           # No optimization - fallback to O(n) iteration
    INDEX_ONLY = 1    # Only indexing - O(1) lookups, no caching
    CACHE_ONLY = 2    # Only caching - benefits from repeated queries
    FULL = 3          # Both indexing + caching - maximum performance
    # Aliases for clarity
    DISABLED = 0
    MINIMAL = 1
    MODERATE = 2
    MAXIMUM = 3
@runtime_checkable

class IGraphManager(Protocol):
    """Interface for graph manager implementations."""

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
        **properties
    ) -> str:
        """Add a relationship between entities."""
        ...

    def remove_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str | None = None
    ) -> bool:
        """Remove relationship(s) between entities."""
        ...

    def get_outgoing(
        self,
        entity_id: str,
        relationship_type: str | None = None,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get outgoing relationships for entity."""
        ...

    def get_incoming(
        self,
        entity_id: str,
        relationship_type: str | None = None,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get incoming relationships for entity."""
        ...

    def has_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str | None = None
    ) -> bool:
        """Check if relationship exists."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get graph statistics."""
        ...

    def clear_cache(self) -> None:
        """Clear query cache."""
        ...
