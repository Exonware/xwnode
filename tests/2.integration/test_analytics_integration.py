"""
#exonware/xwnode/tests/2.integration/test_analytics_integration.py
Integration tests for analytics with mocked xwai/xwstorage.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.analytics.integration import AnalyticsIntegration
from exonware.xwnode.common.analytics.structures import AnalyticsDataStructures
@pytest.mark.xwnode_integration

class TestAnalyticsIntegration:
    """Integration tests for analytics."""

    def test_analytics_processing_workflow(self):
        """Test complete analytics processing workflow."""
        integration = AnalyticsIntegration()
        # Get analytics structures
        cms = integration.get_count_min_sketch()
        hll = integration.get_hyperloglog()
        # Process data
        data = ["item1", "item2", "item1", "item3"]
        # Add to Count-Min Sketch
        for item in data:
            cms.put(item, 1)
        # Add to HyperLogLog
        for item in data:
            hll.put(item)
        # Process with custom processor
        def count_unique(items):
            return len(set(items))
        unique_count = integration.process_analytics(data, count_unique)
        assert unique_count == 3

    def test_analytics_storage_integration(self):
        """Test storing analytics data to storage backend."""
        integration = AnalyticsIntegration()
        class MockStorage:
            def __init__(self):
                self.stored_data = []
            def store(self, data):
                self.stored_data.append(data)
        storage = MockStorage()
        analytics_data = {
            "count_min_sketch": {"item1": 5, "item2": 3},
            "hyperloglog": {"cardinality": 100}
        }
        integration.store_analytics(storage, analytics_data)
        assert len(storage.stored_data) == 1
        assert storage.stored_data[0] == analytics_data

    def test_analytics_structures_integration(self):
        """Test integration between analytics structures."""
        structures = AnalyticsDataStructures()
        # Use Count-Min Sketch
        cms = structures.get_count_min_sketch()
        cms.put("event1", 1)
        cms.put("event2", 1)
        # Use HyperLogLog
        hll = structures.get_hyperloglog()
        hll.put("user1")
        hll.put("user2")
        hll.put("user1")  # Duplicate
        # Use GraphBLAS
        graph = structures.get_graphblas()
        graph.add_node("node1", data={})
        graph.add_node("node2", data={})
        graph.add_edge("node1", "node2", edge_type="connects")
        # All structures should work together
        assert cms is not None
        assert hll is not None
        assert graph is not None
