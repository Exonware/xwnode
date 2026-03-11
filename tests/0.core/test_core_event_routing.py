"""
#exonware/xwnode/tests/0.core/test_core_event_routing.py
Core functionality tests for event routing (20% tests for 80% value).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.graph.event_routing import EventChannelGraph, ChannelRouter
@pytest.mark.xwnode_core

class TestEventRoutingCore:
    """Core event routing tests - high value, fast execution."""

    def test_basic_channel_operations(self):
        """Test add and remove channels - fundamental operations."""
        graph = EventChannelGraph()
        # Add channels
        graph.add_channel("channel1")
        graph.add_channel("channel2", parent="channel1")
        # Verify channels exist
        assert graph.has_channel("channel1")
        assert graph.has_channel("channel2")
        # Get channels
        channels = graph.get_channels()
        assert "channel1" in channels
        assert "channel2" in channels

    def test_event_routing_basic(self):
        """Test basic event routing between channels."""
        graph = EventChannelGraph()
        router = ChannelRouter(graph)
        # Setup channels
        graph.add_channel("source")
        graph.add_channel("target", parent="source")
        # Route event
        event = {"type": "test", "data": "hello"}
        results = router.route("source", event, ["target"])
        assert "target" in results
        assert results["target"]["status"] == "routed"
        assert results["target"]["event"] == event

    def test_channel_topology(self):
        """Test channel hierarchy/topology."""
        graph = EventChannelGraph()
        # Create hierarchy
        graph.add_channel("root")
        graph.add_channel("child1", parent="root")
        graph.add_channel("child2", parent="root")
        # Get topology
        topology = graph.get_channel_topology()
        assert "root" in topology
        assert "child1" in topology["root"]
        assert "child2" in topology["root"]
