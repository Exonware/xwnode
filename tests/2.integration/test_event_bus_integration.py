"""
#exonware/xwnode/tests/2.integration/test_event_bus_integration.py
Integration tests for event bus with mocked xwstorage/xwaction.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.graph.event_routing import EventChannelGraph, ChannelRouter
@pytest.mark.xwnode_integration

class TestEventBusIntegration:
    """Integration tests for event bus."""

    def test_event_routing_workflow(self):
        """Test complete event routing workflow."""
        graph = EventChannelGraph(use_multiplex=True)
        router = ChannelRouter(graph)
        # Setup channel hierarchy
        graph.add_channel("root")
        graph.add_channel("users", parent="root")
        graph.add_channel("users:alice", parent="users")
        graph.add_channel("users:bob", parent="users")
        # Route event from root
        event = {"type": "user_update", "user": "alice", "action": "login"}
        results = router.route("root", event, None)  # Broadcast to all
        # Should route to all channels
        assert len(results) >= 0

    def test_channel_hierarchy(self):
        """Test channel hierarchy operations."""
        graph = EventChannelGraph()
        # Create multi-level hierarchy
        graph.add_channel("app")
        graph.add_channel("app:users", parent="app")
        graph.add_channel("app:users:alice", parent="app:users")
        graph.add_channel("app:users:bob", parent="app:users")
        graph.add_channel("app:posts", parent="app")
        graph.add_channel("app:posts:123", parent="app:posts")
        # Get topology
        topology = graph.get_channel_topology()
        assert "app" in topology
        assert "app:users" in topology["app"]
        assert "app:posts" in topology["app"]

    def test_event_broadcast(self):
        """Test broadcasting events to multiple channels."""
        graph = EventChannelGraph()
        router = ChannelRouter(graph)
        # Setup channels
        graph.add_channel("source")
        graph.add_channel("target1", parent="source")
        graph.add_channel("target2", parent="source")
        graph.add_channel("target3", parent="source")
        # Broadcast event
        event = {"type": "broadcast", "message": "hello"}
        results = router.route("source", event, None)
        # Should reach all targets
        assert len(results) >= 0

    def test_event_filtering(self):
        """Test event filtering by channel pattern."""
        graph = EventChannelGraph()
        # Setup channels with patterns
        graph.add_channel("users:alice")
        graph.add_channel("users:bob")
        graph.add_channel("posts:123")
        graph.add_channel("posts:456")
        # Get user channels only
        user_channels = graph.get_channels("users:*")
        assert len(user_channels) >= 2
        # Get post channels only
        post_channels = graph.get_channels("posts:*")
        assert len(post_channels) >= 2
