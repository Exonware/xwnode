#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/facade_tests/test_direct_navigation.py
Tests for direct navigation bypass in XWNode facade.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: 07-Sep-2025
"""

import pytest
from exonware.xwnode import XWNode
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance

class TestDirectNavigation:
    """Test direct navigation bypass for simple paths."""

    def test_direct_navigation_simple_path(self):
        """Test direct navigation for simple dot-separated paths."""
        # Create large dataset to trigger direct navigation
        large_data = {
            "users": [
                {"name": f"User{i}", "age": 20 + i}
                for i in range(1500)  # > 1000 threshold
            ]
        }
        node = XWNode.from_native(large_data)
        # Should use direct navigation for simple path
        value = node.get_value("users.0.name")
        assert value == "User0"

    def test_direct_navigation_nested_path(self):
        """Test direct navigation for nested paths."""
        large_data = {
            "data": {
                "users": [
                    {"profile": {"name": "Alice", "age": 30}}
                    for _ in range(1500)
                ]
            }
        }
        node = XWNode.from_native(large_data)
        # Should use direct navigation
        value = node.get_value("data.users.0.profile.name")
        assert value == "Alice"

    def test_direct_navigation_list_access(self):
        """Test direct navigation with list indices."""
        large_data = {
            "items": [f"item{i}" for i in range(1500)]
        }
        node = XWNode.from_native(large_data)
        # Should use direct navigation
        value = node.get_value("items.0")
        assert value == "item0"
        value = node.get_value("items.100")
        assert value == "item100"

    def test_direct_navigation_fallback_to_xwnode(self):
        """Test that complex paths fall back to XWNode navigation."""
        # Small dataset (should not use direct navigation)
        small_data = {
            "users": [
                {"name": "Alice"}
            ]
        }
        node = XWNode.from_native(small_data)
        # Should use XWNode navigation (not direct)
        value = node.get_value("users.0.name")
        assert value == "Alice"

    def test_direct_navigation_invalid_path(self):
        """Test direct navigation with invalid path returns default."""
        large_data = {
            "users": [{"name": "Alice"} for _ in range(1500)]
        }
        node = XWNode.from_native(large_data)
        # Invalid path should return default
        value = node.get_value("users.9999.name", default="Not Found")
        assert value == "Not Found"
        value = node.get_value("missing.path", default=None)
        assert value is None

    def test_direct_navigation_performance(self):
        """Test that direct navigation is faster than XWNode navigation."""
        import time
        # Create large dataset
        large_data = {
            "records": [
                {"id": i, "value": f"data_{i}"}
                for i in range(2000)
            ]
        }
        node = XWNode.from_native(large_data)
        # Measure direct navigation (should be fast)
        start = time.time()
        for i in range(100):
            node.get_value(f"records.{i}.value")
        direct_time = time.time() - start
        # Direct navigation should be fast (< 200ms for 100 operations)
        # Allow some variance for system load
        assert direct_time < 0.2, f"Direct navigation took {direct_time:.3f}s, expected < 0.2s"

    def test_direct_navigation_correctness(self):
        """Test that direct navigation returns correct values."""
        large_data = {
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "value": "deep_value"
                        }
                    }
                }
            },
            "list": [
                {"item": f"item_{i}"} for i in range(1500)
            ]
        }
        node = XWNode.from_native(large_data)
        # Deep nested path
        value = node.get_value("nested.level1.level2.level3.value")
        assert value == "deep_value"
        # List access
        value = node.get_value("list.0.item")
        assert value == "item_0"
        value = node.get_value("list.500.item")
        assert value == "item_500"
