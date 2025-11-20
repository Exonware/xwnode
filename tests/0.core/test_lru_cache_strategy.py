"""
#exonware/xwnode/tests/0.core/test_lru_cache_strategy.py

Core tests for LRU_CACHE strategy

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.28
Generation Date: 27-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode, NodeMode


@pytest.mark.xwnode_core
@pytest.mark.xwnode_node_strategy
class TestLRUCacheStrategyCore:
    """Core tests for LRU_CACHE strategy - Fast, high-value checks"""
    
    def test_create_lru_cache(self):
        """Test creating LRU cache"""
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=10)
        assert cache is not None
    
    def test_put_and_get(self):
        """Test basic put and get operations"""
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=10)
        
        # Access strategy directly for strategy-specific operations
        strategy = cache._strategy
        strategy.put('key1', 'value1')
        result = strategy.get('key1')
        
        assert result == 'value1'
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=3)
        strategy = cache._strategy
        
        # Fill cache
        strategy.put('key1', 'value1')
        strategy.put('key2', 'value2')
        strategy.put('key3', 'value3')
        
        # Add one more (should evict key1)
        strategy.put('key4', 'value4')
        
        # key1 should be evicted
        assert strategy.get('key1') is None
        # Others should still exist
        assert strategy.get('key2') == 'value2'
        assert strategy.get('key3') == 'value3'
        assert strategy.get('key4') == 'value4'
    
    def test_statistics_tracking(self):
        """Test hit/miss statistics"""
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=10)
        strategy = cache._strategy
        
        strategy.put('key1', 'value1')
        
        # Hit
        strategy.get('key1')
        # Miss
        strategy.get('key2')
        
        stats = strategy.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5

