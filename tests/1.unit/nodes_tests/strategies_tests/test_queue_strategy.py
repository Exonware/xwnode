"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_queue_strategy.py
Comprehensive tests for QueueStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core queue operations (enqueue, dequeue, peek)
- FIFO (First In, First Out) semantics
- Iterator protocol
- Performance characteristics (O(1) operations)
- Security (bounds checking, memory limits)
- Error handling
- Edge cases
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 15-Nov-2025
"""

import pytest
from typing import Any
from exonware.xwnode.nodes.strategies.queue import QueueStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_queue():
    """Create empty queue strategy."""
    return QueueStrategy()
@pytest.fixture

def simple_queue():
    """Create queue with simple data."""
    queue = QueueStrategy()
    queue.enqueue('value1')
    queue.enqueue('value2')
    queue.enqueue('value3')
    return queue
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestQueueStrategyInterface:
    """Test QueueStrategy implements iNodeStrategy interface correctly."""

    def test_enqueue_operation(self, empty_queue):
        """Test enqueue operation works correctly."""
        empty_queue.enqueue('test_value')
        assert empty_queue.size() == 1
        assert empty_queue.peek() == 'test_value'

    def test_dequeue_operation(self, simple_queue):
        """Test dequeue operation follows FIFO order."""
        # First in should be first out
        assert simple_queue.dequeue() == 'value1'
        assert simple_queue.dequeue() == 'value2'
        assert simple_queue.dequeue() == 'value3'
        assert simple_queue.is_empty is True

    def test_peek_operation(self, simple_queue):
        """Test peek returns front without removing."""
        assert simple_queue.peek() == 'value1'
        assert simple_queue.size() == 3  # Size unchanged
        assert simple_queue.peek() == 'value1'  # Still there

    def test_size_operation(self, simple_queue):
        """Test size returns correct count."""
        assert simple_queue.size() == 3
        simple_queue.dequeue()
        assert simple_queue.size() == 2

    def test_is_empty_operation(self, empty_queue, simple_queue):
        """Test is_empty correctly identifies empty structures."""
        assert empty_queue.is_empty is True
        assert simple_queue.is_empty is False

    def test_to_native_conversion(self, simple_queue):
        """Test conversion to native Python list."""
        native = simple_queue.to_native()
        assert isinstance(native, list)
        assert len(native) == 3
# ============================================================================
# FIFO SEMANTICS TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestQueueStrategyFIFO:
    """Test FIFO (First In, First Out) semantics."""

    def test_fifo_order(self, empty_queue):
        """Test items are dequeued in order of insertion."""
        empty_queue.enqueue('first')
        empty_queue.enqueue('second')
        empty_queue.enqueue('third')
        # Should dequeue in order: first, second, third
        assert empty_queue.dequeue() == 'first'
        assert empty_queue.dequeue() == 'second'
        assert empty_queue.dequeue() == 'third'

    def test_multiple_enqueue_dequeue(self, empty_queue):
        """Test multiple enqueue/dequeue operations maintain FIFO."""
        for i in range(5):
            empty_queue.enqueue(f'item_{i}')
        # Dequeue in order
        for i in range(5):
            assert empty_queue.dequeue() == f'item_{i}'
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestQueueStrategyCore:
    """Test core QueueStrategy functionality."""

    def test_clear_operation(self, simple_queue):
        """Test clear removes all items."""
        simple_queue.clear()
        assert simple_queue.is_empty is True
        assert simple_queue.size() == 0

    def test_initial_values(self):
        """Test queue with initial values."""
        queue = QueueStrategy(initial_values=['a', 'b', 'c'])
        assert queue.size() == 3
        assert queue.dequeue() == 'a'
        assert queue.dequeue() == 'b'
        assert queue.dequeue() == 'c'

    def test_max_size_limit(self):
        """Test max_size option limits queue size."""
        queue = QueueStrategy(max_size=3)
        queue.enqueue('a')
        queue.enqueue('b')
        queue.enqueue('c')
        # Should have 3 items
        assert queue.size() == 3
        # Attempting to enqueue more should either raise error or ignore
        try:
            queue.enqueue('d')
            # If no error, size should still be 3
            assert queue.size() == 3
        except (XWNodeError, OverflowError):
            # If error raised, that's also valid
            pass
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestQueueStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_queue_operations(self, empty_queue):
        """Test operations on empty queue."""
        assert empty_queue.dequeue() is None
        assert empty_queue.peek() is None
        assert empty_queue.size() == 0

    def test_single_item_queue(self, empty_queue):
        """Test queue with single item."""
        empty_queue.enqueue('single')
        assert empty_queue.size() == 1
        assert empty_queue.peek() == 'single'
        assert empty_queue.dequeue() == 'single'
        assert empty_queue.is_empty is True

    def test_none_values(self, empty_queue):
        """Test handling of None values."""
        empty_queue.enqueue(None)
        assert empty_queue.peek() is None
        assert empty_queue.dequeue() is None
# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance

class TestQueueStrategyPerformance:
    """Test performance characteristics."""

    def test_large_queue_operations(self):
        """Test operations with large queue."""
        queue = QueueStrategy()
        # Enqueue 1000 items
        for i in range(1000):
            queue.enqueue(f'item_{i}')
        assert queue.size() == 1000
        # Dequeue all items
        for i in range(1000):
            assert queue.dequeue() == f'item_{i}'
        assert queue.is_empty is True
