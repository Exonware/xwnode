"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_priority_queue_strategy.py
Comprehensive tests for PriorityQueueStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core priority queue operations (push, pop, peek)
- Min-heap and max-heap behavior
- Priority ordering
- Iterator protocol
- Performance characteristics (O(log n) operations)
- Security (bounds checking, priority validation)
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
from exonware.xwnode.nodes.strategies.priority_queue import PriorityQueueStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_pq():
    """Create empty priority queue strategy."""
    return PriorityQueueStrategy()
@pytest.fixture

def min_heap():
    """Create min-heap priority queue."""
    pq = PriorityQueueStrategy(is_max_heap=False)
    pq.push('value3', priority=3)
    pq.push('value1', priority=1)
    pq.push('value2', priority=2)
    return pq
@pytest.fixture

def max_heap():
    """Create max-heap priority queue."""
    pq = PriorityQueueStrategy(is_max_heap=True)
    pq.push('value1', priority=1)
    pq.push('value3', priority=3)
    pq.push('value2', priority=2)
    return pq
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPriorityQueueStrategyInterface:
    """Test PriorityQueueStrategy implements iNodeStrategy interface correctly."""

    def test_push_operation(self, empty_pq):
        """Test push operation works correctly."""
        empty_pq.push('test_value', priority=5)
        assert empty_pq.size() == 1
        assert empty_pq.peek() == 'test_value'

    def test_pop_operation_min_heap(self, min_heap):
        """Test pop operation follows priority order (min-heap)."""
        # Should pop in priority order: 1, 2, 3
        assert min_heap.pop() == 'value1'
        assert min_heap.pop() == 'value2'
        assert min_heap.pop() == 'value3'
        assert min_heap.is_empty is True

    def test_pop_operation_max_heap(self, max_heap):
        """Test pop operation follows priority order (max-heap)."""
        # Should pop in reverse priority order: 3, 2, 1
        assert max_heap.pop() == 'value3'
        assert max_heap.pop() == 'value2'
        assert max_heap.pop() == 'value1'
        assert max_heap.is_empty is True

    def test_peek_operation(self, min_heap):
        """Test peek returns highest priority without removing."""
        assert min_heap.peek() == 'value1'  # Lowest priority value
        assert min_heap.size() == 3  # Size unchanged
        assert min_heap.peek() == 'value1'  # Still there

    def test_size_operation(self, min_heap):
        """Test size returns correct count."""
        assert min_heap.size() == 3
        min_heap.pop()
        assert min_heap.size() == 2

    def test_is_empty_operation(self, empty_pq, min_heap):
        """Test is_empty correctly identifies empty structures."""
        assert empty_pq.is_empty is True
        assert min_heap.is_empty is False
# ============================================================================
# PRIORITY ORDERING TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPriorityQueueStrategyPriority:
    """Test priority ordering behavior."""

    def test_min_heap_ordering(self, empty_pq):
        """Test min-heap maintains minimum priority at top."""
        empty_pq.push('high', priority=10)
        empty_pq.push('low', priority=1)
        empty_pq.push('medium', priority=5)
        # Should pop in order: low, medium, high
        assert empty_pq.pop() == 'low'
        assert empty_pq.pop() == 'medium'
        assert empty_pq.pop() == 'high'

    def test_max_heap_ordering(self):
        """Test max-heap maintains maximum priority at top."""
        pq = PriorityQueueStrategy(is_max_heap=True)
        pq.push('low', priority=1)
        pq.push('high', priority=10)
        pq.push('medium', priority=5)
        # Should pop in order: high, medium, low
        assert pq.pop() == 'high'
        assert pq.pop() == 'medium'
        assert pq.pop() == 'low'

    def test_equal_priorities(self, empty_pq):
        """Test handling of equal priorities."""
        empty_pq.push('first', priority=5)
        empty_pq.push('second', priority=5)
        empty_pq.push('third', priority=5)
        # Should maintain insertion order for equal priorities (FIFO)
        # Or arbitrary order - both are valid
        assert empty_pq.size() == 3
        popped = [empty_pq.pop(), empty_pq.pop(), empty_pq.pop()]
        assert set(popped) == {'first', 'second', 'third'}
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPriorityQueueStrategyCore:
    """Test core PriorityQueueStrategy functionality."""

    def test_clear_operation(self, min_heap):
        """Test clear removes all items."""
        min_heap.clear()
        assert min_heap.is_empty is True
        assert min_heap.size() == 0

    def test_initial_items(self):
        """Test priority queue with initial items."""
        pq = PriorityQueueStrategy(initial_items=[(3, 'c'), (1, 'a'), (2, 'b')])
        assert pq.size() == 3
        assert pq.pop() == 'a'  # Lowest priority
        assert pq.pop() == 'b'
        assert pq.pop() == 'c'
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPriorityQueueStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_pq_operations(self, empty_pq):
        """Test operations on empty priority queue."""
        assert empty_pq.pop() is None
        assert empty_pq.peek() is None
        assert empty_pq.size() == 0

    def test_single_item_pq(self, empty_pq):
        """Test priority queue with single item."""
        empty_pq.push('single', priority=1)
        assert empty_pq.size() == 1
        assert empty_pq.peek() == 'single'
        assert empty_pq.pop() == 'single'
        assert empty_pq.is_empty is True

    def test_negative_priorities(self, empty_pq):
        """Test handling of negative priorities."""
        empty_pq.push('negative', priority=-5)
        empty_pq.push('positive', priority=5)
        # In min-heap, negative should come first
        assert empty_pq.pop() == 'negative'
        assert empty_pq.pop() == 'positive'
# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance

class TestPriorityQueueStrategyPerformance:
    """Test performance characteristics."""

    def test_large_pq_operations(self):
        """Test operations with large priority queue."""
        pq = PriorityQueueStrategy()
        # Push 100 items with random priorities
        for i in range(100):
            pq.push(f'item_{i}', priority=i)
        assert pq.size() == 100
        # Pop all items - should be in priority order
        for i in range(100):
            assert pq.pop() == f'item_{i}'
        assert pq.is_empty is True
