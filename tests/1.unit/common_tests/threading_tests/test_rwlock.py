#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/common_tests/threading_tests/test_rwlock.py
Tests for AsyncRWLock implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.31
Generation Date: 07-Sep-2025
"""

import pytest
import asyncio
import time
from exonware.xwnode.common.threading import AsyncRWLock
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance

class TestAsyncRWLock:
    """Test AsyncRWLock read-write lock implementation."""
    @pytest.mark.asyncio

    async def test_read_lock_allows_concurrent_reads(self):
        """Test that multiple readers can hold the lock simultaneously."""
        rwlock = AsyncRWLock()
        results = []
        async def read_operation(id: int):
            async with rwlock.read_lock():
                results.append(f"reader_{id}")
                await asyncio.sleep(0.01)  # Simulate read operation
                results.append(f"reader_{id}_done")
        # Start multiple concurrent readers
        await asyncio.gather(
            read_operation(1),
            read_operation(2),
            read_operation(3)
        )
        # All readers should have executed concurrently
        # (not strictly sequential)
        assert len(results) == 6
        assert "reader_1" in results
        assert "reader_2" in results
        assert "reader_3" in results
    @pytest.mark.asyncio

    async def test_write_lock_exclusive(self):
        """Test that write lock is exclusive (blocks all operations)."""
        rwlock = AsyncRWLock()
        results = []
        async def write_operation(id: int):
            async with rwlock.write_lock():
                results.append(f"writer_{id}_start")
                await asyncio.sleep(0.01)
                results.append(f"writer_{id}_end")
        # Start multiple writers
        await asyncio.gather(
            write_operation(1),
            write_operation(2)
        )
        # Writers should execute sequentially (exclusive)
        assert len(results) == 4
        # First writer should complete before second starts
        writer1_start_idx = results.index("writer_1_start")
        writer1_end_idx = results.index("writer_1_end")
        writer2_start_idx = results.index("writer_2_start")
        assert writer1_end_idx < writer2_start_idx
    @pytest.mark.asyncio

    async def test_write_blocks_reads(self):
        """Test that write lock blocks concurrent reads."""
        rwlock = AsyncRWLock()
        results = []
        async def write_operation():
            async with rwlock.write_lock():
                results.append("write_start")
                await asyncio.sleep(0.05)
                results.append("write_end")
        async def read_operation(id: int):
            async with rwlock.read_lock():
                results.append(f"read_{id}")
        # Start write, then reads
        write_task = asyncio.create_task(write_operation())
        await asyncio.sleep(0.01)  # Let write start
        # Start reads (should wait for write)
        read_tasks = [asyncio.create_task(read_operation(i)) for i in range(3)]
        await asyncio.gather(write_task, *read_tasks)
        # Write should complete before reads
        write_end_idx = results.index("write_end")
        read_indices = [results.index(f"read_{i}") for i in range(3)]
        assert all(idx > write_end_idx for idx in read_indices)
    @pytest.mark.asyncio

    async def test_read_does_not_block_reads(self):
        """Test that reads don't block other reads."""
        rwlock = AsyncRWLock()
        start_times = []
        end_times = []
        async def read_operation(id: int):
            async with rwlock.read_lock():
                start_times.append((id, time.time()))
                await asyncio.sleep(0.01)
                end_times.append((id, time.time()))
        # Start multiple concurrent reads
        await asyncio.gather(
            read_operation(1),
            read_operation(2),
            read_operation(3)
        )
        # All reads should start before any completes
        # (indicating concurrency)
        max_start = max(t for _, t in start_times)
        min_end = min(t for _, t in end_times)
        # Reads should overlap (concurrent execution)
        assert max_start < min_end
    @pytest.mark.asyncio

    async def test_manual_lock_acquire_release(self):
        """Test manual lock acquisition and release."""
        rwlock = AsyncRWLock()
        await rwlock.acquire_read()
        stats = rwlock.get_stats()
        assert stats['readers'] == 1
        await rwlock.release_read()
        stats = rwlock.get_stats()
        assert stats['readers'] == 0
        await rwlock.acquire_write()
        stats = rwlock.get_stats()
        assert stats['writer_active'] is True
        await rwlock.release_write()
        stats = rwlock.get_stats()
        assert stats['writer_active'] is False
    @pytest.mark.asyncio

    async def test_get_stats(self):
        """Test lock statistics reporting."""
        rwlock = AsyncRWLock()
        stats = rwlock.get_stats()
        assert stats['readers'] == 0
        assert stats['writers_waiting'] == 0
        assert stats['writer_active'] is False
        async with rwlock.read_lock():
            stats = rwlock.get_stats()
            assert stats['readers'] == 1
        async with rwlock.write_lock():
            stats = rwlock.get_stats()
            assert stats['writer_active'] is True
            assert stats['readers'] == 0
    @pytest.mark.xwnode_performance
    @pytest.mark.asyncio

    async def test_concurrent_read_performance(self):
        """Test that concurrent reads are faster than sequential."""
        rwlock = AsyncRWLock()
        data = {"value": 42}
        async def read_operation():
            async with rwlock.read_lock():
                return data["value"]
        # Concurrent reads
        start = time.time()
        results = await asyncio.gather(*[read_operation() for _ in range(100)])
        concurrent_time = time.time() - start
        # All should succeed
        assert all(r == 42 for r in results)
        # Concurrent should be fast (all execute simultaneously)
        assert concurrent_time < 0.1  # Should complete quickly
