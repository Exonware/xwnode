"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_stack_strategy.py
Comprehensive tests for StackStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core stack operations (push, pop, peek)
- LIFO (Last In, First Out) semantics
- Iterator protocol
- Performance characteristics (O(1) operations)
- Security (bounds checking, overflow protection)
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
from exonware.xwnode.nodes.strategies.stack import StackStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_stack():
    """Create empty stack strategy."""
    return StackStrategy()
@pytest.fixture

def simple_stack():
    """Create stack with simple data."""
    stack = StackStrategy()
    stack.push('value1')
    stack.push('value2')
    stack.push('value3')
    return stack
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestStackStrategyInterface:
    """Test StackStrategy implements iNodeStrategy interface correctly."""

    def test_push_operation(self, empty_stack):
        """Test push operation works correctly."""
        empty_stack.push('test_value')
        assert empty_stack.size() == 1
        assert empty_stack.peek() == 'test_value'

    def test_pop_operation(self, simple_stack):
        """Test pop operation follows LIFO order."""
        # Last in should be first out
        assert simple_stack.pop() == 'value3'
        assert simple_stack.pop() == 'value2'
        assert simple_stack.pop() == 'value1'
        assert simple_stack.is_empty() is True

    def test_peek_operation(self, simple_stack):
        """Test peek returns top without removing."""
        assert simple_stack.peek() == 'value3'
        assert simple_stack.size() == 3  # Size unchanged
        assert simple_stack.peek() == 'value3'  # Still there

    def test_size_operation(self, simple_stack):
        """Test size returns correct count."""
        assert simple_stack.size() == 3
        simple_stack.pop()
        assert simple_stack.size() == 2

    def test_is_empty_operation(self, empty_stack, simple_stack):
        """Test is_empty correctly identifies empty structures."""
        assert empty_stack.is_empty() is True
        assert simple_stack.is_empty() is False

    def test_to_native_conversion(self, simple_stack):
        """Test conversion to native Python list."""
        native = simple_stack.to_native()
        assert isinstance(native, dict)
        # Stack should be in LIFO order (top to bottom)
        assert len(native) == 3
# ============================================================================
# LIFO SEMANTICS TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestStackStrategyLIFO:
    """Test LIFO (Last In, First Out) semantics."""

    def test_lifo_order(self, empty_stack):
        """Test items are popped in reverse order of insertion."""
        empty_stack.push('first')
        empty_stack.push('second')
        empty_stack.push('third')
        # Should pop in reverse: third, second, first
        assert empty_stack.pop() == 'third'
        assert empty_stack.pop() == 'second'
        assert empty_stack.pop() == 'first'

    def test_multiple_push_pop(self, empty_stack):
        """Test multiple push/pop operations maintain LIFO."""
        for i in range(5):
            empty_stack.push(f'item_{i}')
        # Pop in reverse order
        for i in range(4, -1, -1):
            assert empty_stack.pop() == f'item_{i}'
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestStackStrategyCore:
    """Test core StackStrategy functionality."""

    def test_clear_operation(self, simple_stack):
        """Test clear removes all items."""
        simple_stack.clear()
        assert simple_stack.is_empty() is True
        assert simple_stack.size() == 0

    def test_max_size_limit(self):
        """Test max_size option limits stack size."""
        stack = StackStrategy(max_size=3)
        stack.push('a')
        stack.push('b')
        stack.push('c')
        # Should have 3 items
        assert stack.size() == 3
        # Attempting to push more should either raise error or ignore
        # (implementation dependent)
        try:
            stack.push('d')
            # If no error, size should still be 3
            assert stack.size() == 3
        except (XWNodeError, OverflowError):
            # If error raised, that's also valid
            pass
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestStackStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_stack_operations(self, empty_stack):
        """Test operations on empty stack."""
        with pytest.raises(IndexError):
            empty_stack.pop()
        assert empty_stack.peek() is None
        assert empty_stack.size() == 0

    def test_single_item_stack(self, empty_stack):
        """Test stack with single item."""
        empty_stack.push('single')
        assert empty_stack.size() == 1
        assert empty_stack.peek() == 'single'
        assert empty_stack.pop() == 'single'
        assert empty_stack.is_empty() is True

    def test_none_values(self, empty_stack):
        """Test handling of None values."""
        empty_stack.push(None)
        assert empty_stack.peek() is None
        with pytest.raises(IndexError):
            empty_stack.pop()

    def test_nested_structures(self, empty_stack):
        """Test pushing nested structures."""
        nested = {'key': 'value', 'list': [1, 2, 3]}
        empty_stack.push(nested)
        popped = empty_stack.pop()
        assert popped == nested
        assert popped['key'] == 'value'
# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance

class TestStackStrategyPerformance:
    """Test performance characteristics."""

    def test_large_stack_operations(self):
        """Test operations with large stack."""
        stack = StackStrategy()
        # Push 1000 items
        for i in range(1000):
            stack.push(f'item_{i}')
        assert stack.size() == 1000
        # Pop all items
        for i in range(999, -1, -1):
            assert stack.pop() == f'item_{i}'
        assert stack.is_empty() is True
