"""
#exonware/xwnode/tests/0.core/test_core_cache_management.py
Core functionality tests for cache management (20% tests for 80% value).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.caching.strategy import CacheStrategyManager, CacheMetrics
@pytest.mark.xwnode_core

class TestCacheManagementCore:
    """Core cache management tests - high value, fast execution."""

    def test_get_cache_lru(self):
        """Test getting LRU cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lru", max_size=100)
        # Basic operations
        cache.put("key1", "value1")
        value = cache.get("key1")
        assert value == "value1"

    def test_get_cache_lfu(self):
        """Test getting LFU cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lfu", max_size=100)
        # Basic operations
        cache.put("key1", "value1")
        value = cache.get("key1")
        assert value == "value1"

    def test_get_cache_ttl(self):
        """Test getting TTL cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="ttl", max_size=100, ttl=60)
        # Basic operations
        cache.put("key1", "value1")
        value = cache.get("key1")
        assert value == "value1"

    def test_cache_metrics(self):
        """Test cache metrics."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lru", max_size=100, cache_id="test")
        # Use cache
        cache.put("key1", "value1")
        cache.get("key1")
        cache.get("key2")  # Miss
        # Get metrics
        metrics = CacheMetrics(manager)
        stats = metrics.get_metrics("test")
        assert "test" in stats or len(stats) > 0
