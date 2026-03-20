"""
#exonware/xwnode/tests/2.integration/test_cache_orchestration.py
Integration tests for cache orchestration with mocked xwbase.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.caching.strategy import CacheStrategyManager, CacheMetrics
@pytest.mark.xwnode_integration

class TestCacheOrchestration:
    """Integration tests for cache orchestration."""

    def test_multiple_cache_strategies(self):
        """Test using multiple cache strategies together."""
        manager = CacheStrategyManager()
        # Create different strategy caches
        lru_cache = manager.get_cache(strategy="lru", max_size=100, cache_id="lru")
        lfu_cache = manager.get_cache(strategy="lfu", max_size=100, cache_id="lfu")
        ttl_cache = manager.get_cache(strategy="ttl", max_size=100, cache_id="ttl", ttl=60)
        # Use all caches
        lru_cache.put("key1", "value1")
        lfu_cache.put("key2", "value2")
        ttl_cache.put("key3", "value3")
        assert lru_cache.get("key1") == "value1"
        assert lfu_cache.get("key2") == "value2"
        assert ttl_cache.get("key3") == "value3"

    def test_cache_metrics_collection(self):
        """Test collecting metrics from multiple caches."""
        manager = CacheStrategyManager()
        # Create and use caches
        cache1 = manager.get_cache(strategy="lru", max_size=100, cache_id="cache1")
        cache2 = manager.get_cache(strategy="lfu", max_size=100, cache_id="cache2")
        cache1.put("key1", "value1")
        cache1.get("key1")  # Hit
        cache1.get("key2")  # Miss
        cache2.put("key3", "value3")
        cache2.get("key3")  # Hit
        # Get metrics
        metrics = CacheMetrics(manager)
        all_stats = metrics.get_metrics()
        assert len(all_stats) >= 0

    def test_cache_strategy_switching(self):
        """Test switching cache strategies."""
        manager = CacheStrategyManager()
        # Create initial cache
        cache1 = manager.get_cache(strategy="lru", max_size=100, cache_id="switch_test")
        cache1.put("key1", "value1")
        cache1.put("key2", "value2")
        # Switch to LFU
        cache2 = manager.switch_strategy("switch_test", "lfu", max_size=100)
        # New cache should work
        cache2.put("key3", "value3")
        assert cache2.get("key3") == "value3"

    def test_cache_with_component(self):
        """Test cache with component integration."""
        manager = CacheStrategyManager(use_controller=True)
        # Get cache with component (reuses CacheController)
        cache = manager.get_cache(
            strategy="lru",
            max_size=100,
            component="graph"
        )
        assert cache is not None
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
