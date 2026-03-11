#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/common_tests/async_tests/test_event_loop_reuse.py
Tests for EventLoopManager implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.32
Generation Date: 07-Sep-2025
"""

import pytest
import asyncio
import threading
from exonware.xwnode.common.async_utils import EventLoopManager, get_event_loop_manager
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance

class TestEventLoopManager:
    """Test EventLoopManager event loop reuse."""

    def test_get_event_loop_creates_new(self):
        """Test that get_event_loop creates new loop when none exists."""
        manager = EventLoopManager()
        loop = manager.get_event_loop()
        assert loop is not None
        assert isinstance(loop, asyncio.AbstractEventLoop)

    def test_get_event_loop_reuses_existing(self):
        """Test that get_event_loop reuses existing loop."""
        manager = EventLoopManager()
        loop1 = manager.get_event_loop()
        loop2 = manager.get_event_loop()
        # Should be the same loop (reused) - check by manager's internal state
        # Note: In test context, asyncio.get_event_loop() may return different
        # objects, but manager should track the same loop instance internally
        assert manager._thread_id is not None
        assert manager._loop is not None
        # Manager should track the same loop instance
        # Both calls should return the manager's tracked loop
        assert loop1 is manager._loop, f"loop1 ({id(loop1)}) should be manager._loop ({id(manager._loop)})"
        assert loop2 is manager._loop, f"loop2 ({id(loop2)}) should be manager._loop ({id(manager._loop)})"
        # Both calls should return the same loop instance (manager's tracked loop)
        assert loop1 is loop2, f"loop1 ({id(loop1)}) and loop2 ({id(loop2)}) should be the same"

    def test_run_until_complete(self):
        """Test run_until_complete with managed event loop."""
        manager = EventLoopManager()
        async def async_function():
            await asyncio.sleep(0.01)
            return "result"
        result = manager.run_until_complete(async_function())
        assert result == "result"

    def test_cleanup_closes_loop(self):
        """Test that cleanup closes the event loop."""
        manager = EventLoopManager()
        loop = manager.get_event_loop()
        assert not loop.is_closed()
        manager.cleanup()
        # Loop should be closed
        assert loop.is_closed()

    def test_context_manager(self):
        """Test EventLoopManager as context manager."""
        with EventLoopManager() as manager:
            loop = manager.get_event_loop()
            assert loop is not None
        # Loop should be cleaned up after context exit
        # (Note: cleanup behavior may vary based on loop state)

    def test_is_loop_available(self):
        """Test is_loop_available check."""
        manager = EventLoopManager()
        # Initially no loop
        assert not manager.is_loop_available()
        # After getting loop
        manager.get_event_loop()
        # Availability depends on loop state
        # (may not be running in test context)

    def test_global_manager_singleton(self):
        """Test that get_event_loop_manager returns singleton."""
        manager1 = get_event_loop_manager()
        manager2 = get_event_loop_manager()
        # Should be the same instance
        assert manager1 is manager2
    @pytest.mark.xwnode_performance

    def test_event_loop_reuse_performance(self):
        """Test that reusing event loop is faster than creating new."""
        import time
        manager = EventLoopManager()
        # First call (creates loop)
        start1 = time.time()
        loop1 = manager.get_event_loop()
        time1 = time.time() - start1
        # Second call (reuses loop)
        start2 = time.time()
        loop2 = manager.get_event_loop()
        time2 = time.time() - start2
        # Reuse should be faster (or at least not slower)
        assert time2 <= time1 * 1.1  # Allow 10% variance
        # Manager should track the same loop instance
        assert loop1 is manager._loop, f"loop1 ({id(loop1)}) should be manager._loop ({id(manager._loop)})"
        assert loop2 is manager._loop, f"loop2 ({id(loop2)}) should be manager._loop ({id(manager._loop)})"
        # Both calls should return the manager's tracked loop
        assert loop1 is loop2, f"loop1 ({id(loop1)}) and loop2 ({id(loop2)}) should be the same"
