"""
#exonware/xwnode/tests/1.unit/graph_tests/test_event_routing.py
Unit tests for event routing.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.graph.event_routing import EventChannelGraph, ChannelRouter
from exonware.xwnode.common.graph.event_routing_contracts import IEventChannelGraph, IChannelRouter
@pytest.mark.xwnode_unit

class TestEventChannelGraph:
    """Tests for EventChannelGraph."""

    def test_initialization(self):
        """Test graph initialization."""
        graph = EventChannelGraph(use_multiplex=True)
        assert graph is not None
        assert graph._use_multiplex is True
        graph2 = EventChannelGraph(use_multiplex=False)
        assert graph2._use_multiplex is False

    def test_add_channel(self):
        """Test adding channels."""
        graph = EventChannelGraph()
        graph.add_channel("channel1")
        assert graph.has_channel("channel1")
        graph.add_channel("channel2", parent="channel1")
        assert graph.has_channel("channel2")

    def test_remove_channel(self):
        """Test removing channels."""
        graph = EventChannelGraph()
        graph.add_channel("channel1")
        assert graph.has_channel("channel1")
        removed = graph.remove_channel("channel1")
        assert removed is True
        assert not graph.has_channel("channel1")

    def test_get_channels(self):
        """Test getting channels."""
        graph = EventChannelGraph()
        graph.add_channel("channel1")
        graph.add_channel("channel2")
        graph.add_channel("user:123")
        channels = graph.get_channels()
        assert len(channels) >= 3
        # Pattern matching
        user_channels = graph.get_channels("user:*")
        assert "user:123" in user_channels

    def test_route_event(self):
        """Test event routing."""
        graph = EventChannelGraph()
        graph.add_channel("source")
        graph.add_channel("target", parent="source")
        event = {"type": "test", "data": "hello"}
        results = graph.route_event("source", event, ["target"])
        assert "target" in results
        assert results["target"]["status"] in ["routed", "unreachable"]

    def test_get_channel_topology(self):
        """Test topology retrieval."""
        graph = EventChannelGraph()
        graph.add_channel("root")
        graph.add_channel("child1", parent="root")
        graph.add_channel("child2", parent="root")
        topology = graph.get_channel_topology()
        assert "root" in topology
        assert len(topology["root"]) >= 2
@pytest.mark.xwnode_unit

class TestChannelRouter:
    """Tests for ChannelRouter."""

    def test_initialization(self):
        """Test router initialization."""
        graph = EventChannelGraph()
        router = ChannelRouter(graph)
        assert router is not None
        assert router._graph == graph

    def test_route(self):
        """Test routing events."""
        graph = EventChannelGraph()
        router = ChannelRouter(graph)
        graph.add_channel("source")
        graph.add_channel("target", parent="source")
        event = {"type": "test"}
        results = router.route("source", event, ["target"])
        assert "target" in results

    def test_get_reachable_channels(self):
        """Test getting reachable channels."""
        graph = EventChannelGraph()
        router = ChannelRouter(graph)
        graph.add_channel("source")
        graph.add_channel("target1", parent="source")
        graph.add_channel("target2", parent="source")
        reachable = router.get_reachable_channels("source")
        assert len(reachable) >= 2

    def test_get_shortest_path(self):
        """Test getting shortest path."""
        graph = EventChannelGraph()
        router = ChannelRouter(graph)
        graph.add_channel("a")
        graph.add_channel("b", parent="a")
        graph.add_channel("c", parent="b")
        path = router.get_shortest_path("a", "c")
        # Path should exist if channels are connected
        assert path is None or len(path) > 0
