"""
#exonware/xwnode/src/exonware/xwnode/common/graph/event_routing.py
Event routing implementation for BaaS capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.24
Generation Date: 01-Jan-2026
"""

from typing import Any
from collections import defaultdict, deque
from collections.abc import Sequence
from .event_routing_contracts import IEventChannelGraph, IChannelRouter
from ...facades.graph import XWNodeGraph
from ...defs import EdgeMode, NodeMode


class EventChannelGraph:
    """
    Event channel graph using multiplex or adjacency list strategies.
    Provides event graph structures for real-time/WebSocket and Hub/Event Bus.
    Uses existing MultiplexStrategy and AdjacencyListStrategy for graph operations.
    """

    def __init__(self, use_multiplex: bool = True):
        """
        Initialize event channel graph.
        Args:
            use_multiplex: If True, use multiplex graph for multi-layer channels
        """
        # Use XWNodeGraph for complete graph operations (reuses existing facade)
        # Use HASH_MAP for nodes (simpler, no abstract method issues)
        edge_mode = EdgeMode.MULTIPLEX if use_multiplex else EdgeMode.ADJ_LIST
        self._graph = XWNodeGraph(
            node_mode=NodeMode.HASH_MAP,
            edge_mode=edge_mode,
            enable_caching=True,
            enable_indexing=True
        )
        # Channel metadata
        self._channel_metadata: dict[str, dict[str, Any]] = {}
        self._parent_channels: dict[str, str | None] = {}
        self._use_multiplex = use_multiplex

    def add_channel(self, channel: str, parent: str | None = None) -> None:
        """Add a channel to the event graph."""
        if not channel:
            raise ValueError("Channel identifier cannot be empty")
        # Add channel as node (reuse XWNodeGraph.add_node)
        self._graph.add_node(channel, data={'type': 'channel'})
        # Add parent-child relationship (reuse XWNodeGraph.add_edge)
        if parent:
            # Ensure parent exists (reuse XWNodeGraph.get_node)
            if self._graph.get_node(parent) is None:
                self._graph.add_node(parent, data={'type': 'channel'})
            # Add parent-child edge
            self._graph.add_edge(
                source=parent,
                target=channel,
                edge_type="hierarchy"
            )
        self._parent_channels[channel] = parent
        # Initialize metadata
        if channel not in self._channel_metadata:
            self._channel_metadata[channel] = {
                'created_at': None,
                'subscribers': 0,
                'events_routed': 0
            }

    def remove_channel(self, channel: str) -> bool:
        """Remove a channel from the event graph."""
        # Use XWNodeGraph.remove_node which handles edges automatically
        if self._graph.get_node(channel) is None:
            return False
        # Remove node (automatically removes all edges)
        self._graph.remove_node(channel)
        # Cleanup metadata
        self._channel_metadata.pop(channel, None)
        self._parent_channels.pop(channel, None)
        return True

    def get_channels(self, pattern: str | None = None) -> list[str]:
        """Get channels matching pattern."""
        # Get all channels from metadata (channels are tracked in metadata)
        all_channels = set(self._channel_metadata.keys())
        if pattern is None:
            return list(all_channels)
        # Simple pattern matching (supports wildcards)
        if '*' in pattern:
            import fnmatch
            return [ch for ch in all_channels if fnmatch.fnmatch(ch, pattern)]
        # Exact match
        return [ch for ch in all_channels if ch == pattern]

    def route_event(
        self,
        source: str,
        event: Any,
        target_channels: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Route event to target channels."""
        if source not in self._channel_metadata:
            raise ValueError(f"Source channel not found: {source}")
        results: dict[str, Any] = {}
        if target_channels is None:
            # Broadcast to all reachable channels
            target_channels = self._get_reachable_channels(source)
        for target in target_channels:
            if target not in self._channel_metadata:
                results[target] = {'status': 'error', 'message': 'Channel not found'}
                continue
            # Check if path exists
            if self._has_path(source, target):
                results[target] = {
                    'status': 'routed',
                    'event': event,
                    'path': self._get_path(source, target)
                }
                # Update metadata
                if target in self._channel_metadata:
                    self._channel_metadata[target]['events_routed'] += 1
            else:
                results[target] = {'status': 'unreachable', 'message': 'No path found'}
        return results

    def get_channel_topology(self) -> dict[str, list[str]]:
        """Get channel topology (parent-child relationships)."""
        topology: dict[str, list[str]] = defaultdict(list)
        for channel, parent in self._parent_channels.items():
            if parent:
                topology[parent].append(channel)
        return dict(topology)

    def has_channel(self, channel: str) -> bool:
        """Check if channel exists."""
        # Use XWNodeGraph.get_node (reuse existing method)
        return self._graph.get_node(channel) is not None

    def _get_reachable_channels(self, source: str) -> list[str]:
        """Get all channels reachable from source using BFS."""
        if not self.has_channel(source):
            return []
        visited: set[str] = {source}
        queue: deque[str] = deque([source])
        reachable: list[str] = []
        while queue:
            current = queue.popleft()
            if current != source:
                reachable.append(current)
            # Use XWNodeGraph.get_neighbors (reuse existing method)
            neighbors = self._graph.get_neighbors(current, direction='outgoing')
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return reachable

    def _has_path(self, source: str, target: str) -> bool:
        """Check if path exists between channels."""
        if source == target:
            return True
        visited: set[str] = {source}
        queue: deque[str] = deque([source])
        while queue:
            current = queue.popleft()
            # Use XWNodeGraph.get_neighbors (reuse existing method)
            neighbors = self._graph.get_neighbors(current, direction='outgoing')
            for neighbor in neighbors:
                if neighbor == target:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def _get_path(self, source: str, target: str) -> list[str] | None:
        """Get path between channels using BFS."""
        if source == target:
            return [source]
        # BFS with path tracking
        queue: deque[tuple[str, list[str]]] = deque([(source, [source])])
        visited: set[str] = {source}
        while queue:
            current, path = queue.popleft()
            # Use XWNodeGraph.get_neighbors (reuse existing method)
            neighbors = self._graph.get_neighbors(current, direction='outgoing')
            for neighbor in neighbors:
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None


class ChannelRouter:
    """
    Channel router implementation using graph traversal.
    Provides routing algorithms for event propagation across channels.
    """

    def __init__(self, channel_graph: IEventChannelGraph):
        """
        Initialize channel router.
        Args:
            channel_graph: Event channel graph instance
        """
        self._graph = channel_graph

    def route(
        self,
        source: str,
        event: Any,
        target_channels: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Route event from source to target channels."""
        return self._graph.route_event(source, event, target_channels)

    def get_reachable_channels(self, source: str) -> list[str]:
        """Get all channels reachable from source."""
        if hasattr(self._graph, '_get_reachable_channels'):
            return self._graph._get_reachable_channels(source)
        # Fallback: use routing to all channels
        result = self._graph.route_event(source, {}, None)
        return list(result.keys())

    def get_shortest_path(self, source: str, target: str) -> list[str] | None:
        """Get shortest path between channels."""
        if hasattr(self._graph, '_get_path'):
            return self._graph._get_path(source, target)
        # Fallback: check if path exists
        if hasattr(self._graph, '_has_path'):
            if self._graph._has_path(source, target):
                # Simple path (direct connection assumed)
                return [source, target]
        return None
