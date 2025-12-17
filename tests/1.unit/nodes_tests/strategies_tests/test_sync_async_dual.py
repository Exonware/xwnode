#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_sync_async_dual.py

Tests for dual sync/async API implementation.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.32
Generation Date: 07-Sep-2025
"""

import pytest
import asyncio
from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
from exonware.xwnode.defs import NodeMode


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestSyncAsyncDual:
    """Test dual sync/async API implementation."""
    
    def test_sync_methods_are_native(self):
        """Test that sync methods are native (no asyncio.run overhead)."""
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        
        # Sync methods should work directly (no async overhead)
        strategy.insert("key1", "value1")
        value = strategy.find("key1")
        
        assert value == "value1"
    
    @pytest.mark.asyncio
    async def test_async_methods_are_wrappers(self):
        """Test that async methods are lightweight wrappers."""
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        
        # Async methods should work in async context
        await strategy.insert_async("key1", "value1")
        value = await strategy.find_async("key1")
        
        assert value == "value1"
    
    def test_sync_performance_no_overhead(self):
        """Test that sync methods have no asyncio.run overhead."""
        import time
        
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        
        # Sync operations should be fast (no event loop overhead)
        start = time.time()
        for i in range(1000):
            strategy.insert(f"key{i}", f"value{i}")
        sync_time = time.time() - start
        
        # Should be fast (< 10ms for 1000 operations)
        assert sync_time < 0.01
    
    @pytest.mark.asyncio
    async def test_async_performance_lightweight(self):
        """Test that async methods are lightweight wrappers."""
        import time
        
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        
        # Async operations should be fast (lightweight wrappers)
        start = time.time()
        for i in range(1000):
            await strategy.insert_async(f"key{i}", f"value{i}")
        async_time = time.time() - start
        
        # Should be fast (< 50ms for 1000 operations)
        assert async_time < 0.05
    
    def test_sync_async_consistency(self):
        """Test that sync and async methods produce same results."""
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        
        # Sync operations
        strategy.insert("key1", "value1")
        sync_value = strategy.find("key1")
        
        # Async operations (in sync context using asyncio.run)
        async def async_ops():
            await strategy.insert_async("key2", "value2")
            return await strategy.find_async("key2")
        
        async_value = asyncio.run(async_ops())
        
        assert sync_value == "value1"
        assert async_value == "value2"
    
    def test_no_asyncio_run_in_sync_methods(self):
        """Test that sync methods don't use asyncio.run internally."""
        # This test verifies that sync methods are truly native
        # and don't have the 10-20x overhead of asyncio.run()
        
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        
        # Sync methods should be direct calls (no event loop)
        # We can't directly test this, but we verify performance
        import time
        
        start = time.time()
        for i in range(100):
            strategy.insert(f"key{i}", f"value{i}")
        elapsed = time.time() - start
        
        # If asyncio.run() were used, this would be 10-20x slower
        # Direct sync calls should be very fast
        assert elapsed < 0.01  # 10ms for 100 operations

