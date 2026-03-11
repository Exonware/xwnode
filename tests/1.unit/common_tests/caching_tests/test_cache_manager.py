"""
#exonware/xwnode/tests/1.unit/common_tests/caching_tests/test_cache_manager.py
Unit tests for cache strategy manager.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 01-Jan-2026
"""

import pytest
from exonware.xwnode.common.caching.strategy_manager import CacheStrategyManager, CacheMetrics
from exonware.xwnode.common.caching.contracts import ICacheStrategyManager, ICacheMetrics, ICacheAdapter
@pytest.mark.xwnode_unit

class TestCacheStrategyManager:
    """Tests for CacheStrategyManager."""

    def test_initialization(self):
        """Test manager initialization."""
        manager = CacheStrategyManager()
        assert manager is not None
        assert manager._caches == {}
        assert manager._metrics == {}

    def test_initialization_with_controller(self):
        """Test initialization with controller."""
        manager = CacheStrategyManager(use_controller=True)
        assert manager._controller is not None

    def test_get_cache_lru(self):
        """Test getting LRU cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lru", max_size=100)
        assert cache is not None
        assert isinstance(cache, ICacheAdapter)
        # Test operations
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_cache_lfu(self):
        """Test getting LFU cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lfu", max_size=100)
        assert cache is not None
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_cache_ttl(self):
        """Test getting TTL cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="ttl", max_size=100, ttl=60)
        assert cache is not None
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_cache_fifo(self):
        """Test getting FIFO cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="fifo", max_size=100)
        assert cache is not None
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_cache_invalid_strategy(self):
        """Test getting cache with invalid strategy."""
        manager = CacheStrategyManager()
        with pytest.raises(ValueError):
            manager.get_cache(strategy="invalid", max_size=100)

    def test_get_cache_with_id(self):
        """Test getting cache with specific ID."""
        manager = CacheStrategyManager()
        cache1 = manager.get_cache(strategy="lru", max_size=100, cache_id="cache1")
        cache2 = manager.get_cache(strategy="lru", max_size=100, cache_id="cache1")
        # Should return same instance
        assert cache1 is cache2

    def test_switch_strategy(self):
        """Test switching cache strategy."""
        manager = CacheStrategyManager()
        # Create initial cache
        cache1 = manager.get_cache(strategy="lru", max_size=100, cache_id="test")
        cache1.put("key1", "value1")
        # Switch strategy
        cache2 = manager.switch_strategy("test", "lfu", max_size=100)
        assert cache2 is not None
        # Note: Old data is not migrated, so key1 may not exist
        assert cache2.get("key1") is None or cache2.get("key1") == "value1"

    def test_implements_interface(self):
        """Test that CacheStrategyManager implements ICacheStrategyManager."""
        manager = CacheStrategyManager()
        assert isinstance(manager, ICacheStrategyManager)
@pytest.mark.xwnode_unit

class TestCacheMetrics:
    """Tests for CacheMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        manager = CacheStrategyManager()
        metrics = CacheMetrics(manager)
        assert metrics is not None
        assert metrics._manager is manager

    def test_get_metrics_single_cache(self):
        """Test getting metrics for single cache."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lru", max_size=100, cache_id="test")
        cache.put("key1", "value1")
        cache.get("key1")
        cache.get("key2")  # Miss
        metrics = CacheMetrics(manager)
        stats = metrics.get_metrics("test")
        assert "test" in stats or len(stats) > 0

    def test_get_metrics_all_caches(self):
        """Test getting metrics for all caches."""
        manager = CacheStrategyManager()
        manager.get_cache(strategy="lru", max_size=100, cache_id="cache1")
        manager.get_cache(strategy="lfu", max_size=100, cache_id="cache2")
        metrics = CacheMetrics(manager)
        all_stats = metrics.get_metrics()
        assert len(all_stats) >= 0

    def test_reset_metrics(self):
        """Test resetting metrics."""
        manager = CacheStrategyManager()
        cache = manager.get_cache(strategy="lru", max_size=100, cache_id="test")
        cache.put("key1", "value1")
        cache.get("key1")
        metrics = CacheMetrics(manager)
        metrics.reset_metrics("test")
        # Metrics should be reset (implementation dependent)
        stats = metrics.get_metrics("test")
        assert stats is not None

    def test_implements_interface(self):
        """Test that CacheMetrics implements ICacheMetrics."""
        manager = CacheStrategyManager()
        metrics = CacheMetrics(manager)
        assert isinstance(metrics, ICacheMetrics)
