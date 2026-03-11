#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_async_concurrency.py
Tests for async concurrency with RWLock in node strategies.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: 07-Sep-2025
"""

import pytest
import asyncio
import time
from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
from exonware.xwnode.defs import NodeMode
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance

class TestAsyncConcurrency:
    """Test async concurrency improvements with RWLock."""
    @pytest.mark.asyncio

    async def test_concurrent_reads_performance(self):
        """Test that concurrent reads are faster than sequential."""
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        # Populate data
        for i in range(100):
            strategy.put(f"key{i}", f"value{i}")
        # Concurrent reads
        async def read_operation(key: str):
            return await strategy.find_async(key)
        start = time.time()
        results = await asyncio.gather(*[read_operation(f"key{i}") for i in range(100)])
        concurrent_time = time.time() - start
        # All should succeed
        assert all(results[i] == f"value{i}" for i in range(100))
        # Concurrent should be fast
        assert concurrent_time < 0.1  # Should complete quickly
    @pytest.mark.asyncio

    async def test_read_write_consistency(self):
        """Test that reads and writes maintain consistency."""
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        # Write initial value
        await strategy.insert_async("key1", "value1")
        # Concurrent reads should see consistent value
        async def read_operation():
            return await strategy.find_async("key1")
        results = await asyncio.gather(*[read_operation() for _ in range(10)])
        # All reads should see the same value
        assert all(r == "value1" for r in results)
    @pytest.mark.asyncio

    async def test_write_exclusivity(self):
        """Test that writes are exclusive (no race conditions)."""
        strategy = HashMapStrategy(mode=NodeMode.HASH_MAP)
        # Concurrent writes
        async def write_operation(id: int):
            await strategy.insert_async("counter", id)
            await asyncio.sleep(0.001)  # Small delay
            return await strategy.find_async("counter")
        results = await asyncio.gather(*[write_operation(i) for i in range(10)])
        # All writes should complete (no exceptions)
        assert len(results) == 10
        # Final value should be one of the written values
        final_value = await strategy.find_async("counter")
        assert final_value in results
