#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/common_tests/caching_tests/test_path_cache.py
Tests for PathNavigationCache implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: 07-Sep-2025
"""

import pytest
from exonware.xwnode.common.caching.path_nav import PathNavigationCache
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance

class TestPathNavigationCache:
    """Test PathNavigationCache LRU cache implementation."""

    def test_cache_get_put(self):
        """Test basic cache get and put operations."""
        cache = PathNavigationCache(max_size=10)
        # Put value
        cache.put("users.0.name", "Alice")
        # Get value
        value = cache.get("users.0.name")
        assert value == "Alice"
        # Miss
        assert cache.get("missing") is None

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        cache = PathNavigationCache(max_size=10)
        # First access (miss)
        cache.get("path1")
        # Put and get (hit)
        cache.put("path1", "value1")
        cache.get("path1")
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = PathNavigationCache(max_size=3)
        # Fill cache
        cache.put("path1", "value1")
        cache.put("path2", "value2")
        cache.put("path3", "value3")
        assert len(cache) == 3
        # Add one more (should evict least recently used)
        cache.put("path4", "value4")
        assert len(cache) == 3
        # path1 should be evicted (least recently used)
        assert cache.get("path1") is None
        # path4 should be present
        assert cache.get("path4") == "value4"

    def test_cache_invalidate_specific_path(self):
        """Test invalidating a specific path."""
        cache = PathNavigationCache(max_size=10)
        cache.put("users.0.name", "Alice")
        cache.put("users.0.age", 30)
        cache.put("users.1.name", "Bob")
        # Invalidate specific path
        invalidated = cache.invalidate("users.0.name")
        assert invalidated == 1
        assert cache.get("users.0.name") is None
        assert cache.get("users.0.age") == 30  # Still cached
        assert cache.get("users.1.name") == "Bob"  # Still cached

    def test_cache_invalidate_nested_paths(self):
        """Test that invalidating a path also invalidates nested paths."""
        cache = PathNavigationCache(max_size=10)
        cache.put("users.0.name", "Alice")
        cache.put("users.0.age", 30)
        cache.put("users.1.name", "Bob")
        # Invalidate parent path
        invalidated = cache.invalidate("users.0")
        assert invalidated == 2  # Both users.0.name and users.0.age
        assert cache.get("users.0.name") is None
        assert cache.get("users.0.age") is None
        assert cache.get("users.1.name") == "Bob"  # Not affected

    def test_cache_clear(self):
        """Test clearing all cache entries."""
        cache = PathNavigationCache(max_size=10)
        cache.put("path1", "value1")
        cache.put("path2", "value2")
        assert len(cache) == 2
        cache.clear()
        assert len(cache) == 0
        assert cache.get("path1") is None
        assert cache.get("path2") is None

    def test_cache_dict_like_access(self):
        """Test dict-like access (__getitem__, __setitem__, __contains__)."""
        cache = PathNavigationCache(max_size=10)
        # Set item
        cache["path1"] = "value1"
        # Check contains
        assert "path1" in cache
        assert "missing" not in cache
        # Get item
        assert cache["path1"] == "value1"
        # Delete item
        del cache["path1"]
        assert "path1" not in cache

    def test_cache_stats_tracking(self):
        """Test cache statistics tracking."""
        cache = PathNavigationCache(max_size=10)
        # Miss
        cache.get("path1")
        # Put and hit
        cache.put("path1", "value1")
        cache.get("path1")
        cache.get("path1")  # Another hit
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['size'] == 1
        assert stats['max_size'] == 10

    def test_cache_reset_stats(self):
        """Test resetting cache statistics."""
        cache = PathNavigationCache(max_size=10)
        cache.put("path1", "value1")
        cache.get("path1")
        cache.get("path2")  # Miss
        stats_before = cache.get_stats()
        assert stats_before['hits'] > 0
        assert stats_before['misses'] > 0
        cache.reset_stats()
        stats_after = cache.get_stats()
        assert stats_after['hits'] == 0
        assert stats_after['misses'] == 0
        assert stats_after['size'] == stats_before['size']  # Entries preserved
    @pytest.mark.xwnode_performance

    def test_cache_performance(self):
        """Test cache performance (30-50x faster on hits)."""
        cache = PathNavigationCache(max_size=100)
        # Warm up cache
        for i in range(50):
            cache.put(f"path{i}", f"value{i}")
        import time
        # Measure cache hit performance
        start = time.time()
        for _ in range(1000):
            cache.get("path0")
        cache_time = time.time() - start
        # Cache hits should be very fast (< 1ms for 1000 hits)
        assert cache_time < 0.01  # 10ms for 1000 operations = 0.01ms per operation
