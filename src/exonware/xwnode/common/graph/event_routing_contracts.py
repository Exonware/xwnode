"""
#exonware/xwnode/src/exonware/xwnode/common/graph/event_routing_contracts.py
Event routing contracts for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 01-Jan-2026
"""

from typing import Any, Protocol, runtime_checkable
from collections.abc import Sequence
@runtime_checkable

class IEventChannelGraph(Protocol):
    """
    Interface for event channel graph structures.
    Provides event routing capabilities for real-time/WebSocket and Hub/Event Bus.
    """

    def add_channel(self, channel: str, parent: str | None = None) -> None:
        """
        Add a channel to the event graph.
        Args:
            channel: Channel identifier
            parent: Optional parent channel for hierarchy
        """
        ...

    def remove_channel(self, channel: str) -> bool:
        """
        Remove a channel from the event graph.
        Args:
            channel: Channel identifier
        Returns:
            True if removed, False if not found
        """
        ...

    def get_channels(self, pattern: str | None = None) -> list[str]:
        """
        Get channels matching pattern.
        Args:
            pattern: Optional pattern to match (e.g., "user:*")
        Returns:
            List of matching channel identifiers
        """
        ...

    def route_event(
        self,
        source: str,
        event: Any,
        target_channels: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """
        Route event to target channels.
        Args:
            source: Source channel identifier
            event: Event data to route
            target_channels: Optional list of target channels (None = all connected)
        Returns:
            Dictionary with routing results per channel
        """
        ...

    def get_channel_topology(self) -> dict[str, list[str]]:
        """
        Get channel topology (parent-child relationships).
        Returns:
            Dictionary mapping channels to their child channels
        """
        ...

    def has_channel(self, channel: str) -> bool:
        """
        Check if channel exists.
        Args:
            channel: Channel identifier
        Returns:
            True if channel exists
        """
        ...
@runtime_checkable

class IChannelRouter(Protocol):
    """
    Interface for channel routing algorithms.
    Provides routing strategies for event propagation across channels.
    """

    def route(
        self,
        source: str,
        event: Any,
        target_channels: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """
        Route event from source to target channels.
        Args:
            source: Source channel identifier
            event: Event data
            target_channels: Optional target channels (None = broadcast)
        Returns:
            Dictionary with routing results
        """
        ...

    def get_reachable_channels(self, source: str) -> list[str]:
        """
        Get all channels reachable from source.
        Args:
            source: Source channel identifier
        Returns:
            List of reachable channel identifiers
        """
        ...

    def get_shortest_path(self, source: str, target: str) -> list[str] | None:
        """
        Get shortest path between channels.
        Args:
            source: Source channel identifier
            target: Target channel identifier
        Returns:
            List of channel identifiers forming path, or None if unreachable
        """
        ...
