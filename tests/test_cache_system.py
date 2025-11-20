"""
Test suite for xwnode cache system.

Tests the 4-level cache hierarchy, adapters, and telemetry.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.29
Generation Date: November 4, 2025
"""

import pytest
import time
from unittest.mock import Mock, patch

from exonware.xwnode.common.caching import (
    CacheController,
    get_cache_controller,
    reset_cache_controller,
    LRUCacheAdapter,
    LFUCacheAdapter,
    TTLCacheAdapter,
    TwoTierCacheAdapter,
    NoCacheAdapter,
    get_telemetry_collector,
    reset_telemetry
)
from exonware.xwnode.config import XWNodeConfig


class TestCacheAdapters:
    """Test cache adapter implementations."""
    
    def test_lru_cache_adapter(self):
        """Test LRU cache adapter basic operations."""
        cache = LRUCacheAdapter(size=3, namespace="test")
        
        # Test put and get
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        
        # Test LRU eviction
        cache.put("key4", "value4")
        assert cache.get("key1") is None  # Evicted (least recently used)
        assert cache.get("key2") == "value2"
    
    def test_lfu_cache_adapter(self):
        """Test LFU cache adapter."""
        cache = LFUCacheAdapter(size=3, namespace="test")
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Access key1 multiple times to increase frequency
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")
        
        # Add new key (should evict least frequently used)
        cache.put("key4", "value4")
        
        # key1 should still be there (high frequency)
        assert cache.get("key1") == "value1"
    
    def test_ttl_cache_adapter(self):
        """Test TTL cache adapter."""
        cache = TTLCacheAdapter(size=10, ttl=1, namespace="test")
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for TTL expiration
        time.sleep(1.1)
        assert cache.get("key1") is None  # Expired
    
    def test_no_cache_adapter(self):
        """Test no-cache adapter (always returns None)."""
        cache = NoCacheAdapter()
        
        cache.put("key1", "value1")
        assert cache.get("key1") is None
        
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 1
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = LRUCacheAdapter(size=10, namespace="test")
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Hit
        cache.get("key1")
        
        # Miss
        cache.get("key3")
        
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate == 0.5
        assert stats.size == 2
    
    def test_pattern_invalidation(self):
        """Test pattern-based cache invalidation."""
        cache = LRUCacheAdapter(size=10, namespace="test")
        
        cache.put("user:123:profile", "data1")
        cache.put("user:123:settings", "data2")
        cache.put("user:456:profile", "data3")
        
        # Invalidate all entries for user:123
        count = cache.invalidate_pattern("user:123:*")
        assert count == 2
        
        assert cache.get("user:123:profile") is None
        assert cache.get("user:123:settings") is None
        assert cache.get("user:456:profile") == "data3"


class TestCacheController:
    """Test cache controller and 4-level hierarchy."""
    
    def setup_method(self):
        """Reset cache controller before each test."""
        reset_cache_controller()
    
    def test_controller_initialization(self):
        """Test cache controller initialization."""
        controller = get_cache_controller()
        assert controller is not None
    
    def test_get_cache_with_strategy(self):
        """Test getting cache with different strategies."""
        controller = get_cache_controller()
        
        # LRU cache
        lru_cache = controller.get_cache('test', strategy='lru', size=100)
        assert isinstance(lru_cache, LRUCacheAdapter)
        
        # LFU cache
        lfu_cache = controller.get_cache('test2', strategy='lfu', size=100)
        assert isinstance(lfu_cache, LFUCacheAdapter)
    
    def test_flyweight_pattern(self):
        """Test cache instance sharing via Flyweight pattern."""
        controller = get_cache_controller()
        
        # Get cache twice with same config
        cache1 = controller.get_cache('test', strategy='lru', size=100)
        cache2 = controller.get_cache('test', strategy='lru', size=100)
        
        # Should be same instance (Flyweight)
        assert cache1 is cache2
    
    def test_component_config(self):
        """Test component-specific configuration."""
        controller = get_cache_controller()
        
        # Set component config
        controller.set_component_config(
            component='graph',
            enabled=True,
            strategy='lfu',
            size=2000
        )
        
        # Get cache should use component config
        cache = controller.get_cache('graph')
        assert isinstance(cache, LFUCacheAdapter)
    
    def test_runtime_override(self):
        """Test runtime configuration override."""
        controller = get_cache_controller()
        
        controller.set_component_config(
            component='graph',
            strategy='lru',
            size=1000
        )
        
        # Use runtime override
        with controller.runtime_override('graph', strategy='lfu'):
            cache = controller.get_cache('graph')
            # Inside context, should use LFU
            assert isinstance(cache, LFUCacheAdapter)
        
        # Outside context, should revert to LRU
        cache = controller.get_cache('graph')
        assert isinstance(cache, LRUCacheAdapter)
    
    def test_disable_caching(self):
        """Test disabling caching."""
        controller = get_cache_controller()
        
        controller.set_component_config('graph', enabled=False)
        
        cache = controller.get_cache('graph')
        assert isinstance(cache, NoCacheAdapter)
    
    def test_cache_stats_collection(self):
        """Test collecting stats from all caches."""
        controller = get_cache_controller()
        
        cache1 = controller.get_cache('test1', strategy='lru', size=100)
        cache2 = controller.get_cache('test2', strategy='lfu', size=100)
        
        cache1.put("key1", "value1")
        cache2.put("key2", "value2")
        
        all_stats = controller.get_all_stats()
        assert len(all_stats) >= 2
    
    def test_clear_operations(self):
        """Test clearing caches."""
        controller = get_cache_controller()
        
        cache1 = controller.get_cache('test1', strategy='lru', size=100)
        cache2 = controller.get_cache('test2', strategy='lru', size=100)
        
        cache1.put("key1", "value1")
        cache2.put("key2", "value2")
        
        # Clear specific component
        controller.clear_component('test1')
        assert cache1.get("key1") is None
        assert cache2.get("key2") == "value2"
        
        # Clear all
        controller.clear_all()
        assert cache2.get("key2") is None
    
    def test_health_report(self):
        """Test cache health reporting."""
        controller = get_cache_controller()
        
        cache = controller.get_cache('graph', strategy='lru', size=10)
        
        # Add some data
        for i in range(5):
            cache.put(f"key{i}", f"value{i}")
        
        # Generate hits and misses
        for i in range(5):
            cache.get(f"key{i}")  # Hits
        for i in range(5, 10):
            cache.get(f"key{i}")  # Misses
        
        health = controller.get_health_report()
        assert 'total_caches' in health
        assert 'components' in health
        assert 'warnings' in health
        assert 'recommendations' in health


class TestCacheTelemetry:
    """Test cache telemetry and proof-of-superiority."""
    
    def setup_method(self):
        """Reset telemetry before each test."""
        reset_telemetry()
    
    def test_telemetry_recording(self):
        """Test recording cache operations."""
        collector = get_telemetry_collector()
        
        # Record baseline operations
        collector.record_operation('graph', 'get_neighbors', 10.0, cached=False)
        collector.record_operation('graph', 'get_neighbors', 12.0, cached=False)
        
        # Record cached operations
        collector.record_operation('graph', 'get_neighbors', 1.0, cached=True, cache_strategy='lru')
        collector.record_operation('graph', 'get_neighbors', 0.8, cached=True, cache_strategy='lru')
        
        # Get comparison report
        reports = collector.get_comparison_report()
        assert len(reports) > 0
        
        report = reports[0]
        assert report.component == 'graph'
        assert report.operation == 'get_neighbors'
        assert report.baseline_avg_ms > report.cached_avg_ms
        assert report.speedup_factor > 1.0
    
    def test_proof_summary(self):
        """Test proof-of-superiority summary."""
        collector = get_telemetry_collector()
        
        # Record multiple operations with significant speedup
        for _ in range(10):
            collector.record_operation('graph', 'traverse', 50.0, cached=False)
            collector.record_operation('graph', 'traverse', 5.0, cached=True, cache_strategy='lru')
        
        proof = collector.get_proof_summary()
        
        assert proof['status'] == 'success'
        assert 'overall_metrics' in proof
        assert 'best_performer' in proof
        assert 'worst_performer' in proof
        assert 'recommendations' in proof
        
        metrics = proof['overall_metrics']
        assert metrics['avg_speedup_factor'] > 1.0
        assert 0.0 <= metrics['avg_hit_rate'] <= 1.0
    
    def test_comparison_filtering(self):
        """Test filtering comparison reports."""
        collector = get_telemetry_collector()
        
        collector.record_operation('graph', 'op1', 10.0, cached=False)
        collector.record_operation('graph', 'op1', 1.0, cached=True)
        collector.record_operation('traversal', 'op2', 20.0, cached=False)
        collector.record_operation('traversal', 'op2', 2.0, cached=True)
        
        # Filter by component
        reports = collector.get_comparison_report(component='graph')
        assert all(r.component == 'graph' for r in reports)
        
        # Filter by operation
        reports = collector.get_comparison_report(operation='op1')
        assert all(r.operation == 'op1' for r in reports)


class TestFacadeIntegration:
    """Test facade convenience functions."""
    
    def test_facade_cache_stats(self):
        """Test facade cache stats function."""
        from exonware.xwnode.facade import get_cache_stats, configure_cache
        
        # Configure and use cache
        configure_cache('test_component', strategy='lru', size=100)
        controller = get_cache_controller()
        cache = controller.get_cache('test_component')
        
        cache.put("test_key", "test_value")
        cache.get("test_key")
        
        # Get stats via facade
        stats = get_cache_stats()
        assert isinstance(stats, dict)
    
    def test_facade_cache_health(self):
        """Test facade cache health function."""
        from exonware.xwnode.facade import get_cache_health
        
        health = get_cache_health()
        assert 'total_caches' in health
    
    def test_facade_clear_cache(self):
        """Test facade clear cache function."""
        from exonware.xwnode.facade import clear_cache, configure_cache
        
        configure_cache('test_component', strategy='lru', size=100)
        controller = get_cache_controller()
        cache = controller.get_cache('test_component')
        
        cache.put("key", "value")
        clear_cache('test_component')
        
        assert cache.get("key") is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

