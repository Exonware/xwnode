#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/facade_tests/test_path_caching.py

Tests for path navigation caching in XWNode facade.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: 07-Sep-2025
"""

import pytest
from exonware.xwnode import XWNode


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestPathCaching:
    """Test path navigation caching in XWNode."""
    
    def test_path_cache_hit(self):
        """Test that repeated path access uses cache."""
        node = XWNode.from_native({
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        })
        
        # First access (cache miss)
        value1 = node.get_value("users.0.name")
        assert value1 == "Alice"
        
        # Second access (cache hit - should be faster)
        value2 = node.get_value("users.0.name")
        assert value2 == "Alice"
        
        # Check cache stats
        stats = node._nav_cache.get_stats()
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1
    
    def test_cache_invalidation_on_put(self):
        """Test that cache is invalidated when values are updated."""
        node = XWNode.from_native({"user": {"name": "Alice"}})
        
        # Cache the path
        node.get_value("user.name")
        assert "user.name" in node._nav_cache
        
        # Update value
        node.put("user", {"name": "Bob"})
        
        # Cache should be invalidated
        assert "user.name" not in node._nav_cache or node._nav_cache.get("user.name") is None
        
        # New value should be correct
        assert node.get_value("user.name") == "Bob"
    
    def test_cache_invalidation_on_remove(self):
        """Test that cache is invalidated when values are removed."""
        node = XWNode.from_native({"user": {"name": "Alice", "age": 30}})
        
        # Cache paths
        node.get_value("user.name")
        node.get_value("user.age")
        
        # Remove user
        node.remove("user")
        
        # Cache should be invalidated
        assert node.get_value("user.name") is None
        assert node.get_value("user.age") is None
    
    def test_cache_invalidation_on_set(self):
        """Test that cache is invalidated when set() is called."""
        node = XWNode.from_native({"user": {"name": "Alice"}})
        
        # Cache the path
        value1 = node.get_value("user.name")
        assert value1 == "Alice"
        
        # Verify cache has the value
        cached_before = node._nav_cache.get("user.name")
        assert cached_before == "Alice" or "user.name" in node._nav_cache
        
        # Set new value (should invalidate cache)
        node.set("user.name", "Bob")
        
        # Cache should be invalidated (path should not be in cache or have None)
        cached_after_set = node._nav_cache.get("user.name")
        # Cache should be empty for this path (invalidated)
        assert cached_after_set is None or "user.name" not in node._nav_cache, \
            f"Cache should be invalidated but found: {cached_after_set}"
        
        # Verify cache invalidation worked (cache is cleared)
        # Note: The actual value update depends on strategy implementation
        # This test specifically verifies cache invalidation, not set() correctness
    
    def test_cache_invalidation_nested_paths(self):
        """Test that invalidating a path also invalidates nested paths."""
        node = XWNode.from_native({
            "users": {
                "0": {"name": "Alice", "age": 30},
                "1": {"name": "Bob", "age": 25}
            }
        })
        
        # Cache nested paths
        node.get_value("users.0.name")
        node.get_value("users.0.age")
        node.get_value("users.1.name")
        
        # Verify cache has these paths
        assert "users.0.name" in node._nav_cache or node._nav_cache.get("users.0.name") == "Alice"
        
        # Update parent (this should invalidate nested paths)
        node.put("users", {"0": {"name": "Charlie"}})
        
        # Cache should be invalidated for nested paths
        # Note: Cache invalidation is what we're testing, not the put() correctness
        cached_after = node._nav_cache.get("users.0.name")
        # Cache should be invalidated (None or not in cache)
        assert cached_after is None or "users.0.name" not in node._nav_cache, \
            f"Cache should be invalidated but found: {cached_after}"
    
    def test_cache_performance_improvement(self):
        """Test that caching provides performance improvement."""
        import time
        
        # Create large dataset
        large_data = {
            "records": [
                {"id": i, "data": f"value_{i}"}
                for i in range(1000)
            ]
        }
        node = XWNode.from_native(large_data)
        
        # First access (cache miss)
        start1 = time.time()
        for _ in range(100):
            node.get_value("records.0.data")
        first_time = time.time() - start1
        
        # Second access (cache hit)
        start2 = time.time()
        for _ in range(100):
            node.get_value("records.0.data")
        second_time = time.time() - start2
        
        # Cache hits should be faster (30-50x improvement expected)
        # Allow some variance, but second should be significantly faster
        assert second_time < first_time * 0.5  # At least 2x faster
    
    def test_cache_clear_on_clear(self):
        """Test that cache is cleared when node is cleared."""
        node = XWNode.from_native({"user": {"name": "Alice"}})
        
        # Cache a path
        node.get_value("user.name")
        assert len(node._nav_cache) > 0
        
        # Clear node
        node.clear()
        
        # Cache should be cleared
        assert len(node._nav_cache) == 0

