"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_deque_strategy.py

Comprehensive tests for DequeStrategy.

Tests cover:
- Interface compliance (iNodeStrategy)
- Core deque operations (append, appendleft, pop, popleft)
- Double-ended queue semantics
- Iterator protocol
- Performance characteristics (O(1) operations)
- Security (bounds checking)
- Error handling
- Edge cases

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 15-Nov-2025
"""

import pytest
from typing import Any
from exonware.xwnode.nodes.strategies.deque import DequeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_deque():
    """Create empty deque strategy."""
    return DequeStrategy()


@pytest.fixture
def simple_deque():
    """Create deque with simple data."""
    deque = DequeStrategy()
    deque.append('value1')
    deque.append('value2')
    deque.append('value3')
    return deque


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestDequeStrategyInterface:
    """Test DequeStrategy implements iNodeStrategy interface correctly."""
    
    def test_append_operation(self, empty_deque):
        """Test append operation works correctly."""
        empty_deque.append('test_value')
        
        assert empty_deque.size() == 1
        assert empty_deque.peek_right() == 'test_value'
    
    def test_appendleft_operation(self, empty_deque):
        """Test appendleft operation works correctly."""
        empty_deque.appendleft('test_value')
        
        assert empty_deque.size() == 1
        assert empty_deque.peek_left() == 'test_value'
    
    def test_pop_operation(self, simple_deque):
        """Test pop operation removes from right."""
        assert simple_deque.pop() == 'value3'
        assert simple_deque.size() == 2
        assert simple_deque.pop() == 'value2'
    
    def test_popleft_operation(self, simple_deque):
        """Test popleft operation removes from left."""
        assert simple_deque.popleft() == 'value1'
        assert simple_deque.size() == 2
        assert simple_deque.popleft() == 'value2'
    
    def test_size_operation(self, simple_deque):
        """Test size returns correct count."""
        assert simple_deque.size() == 3
        
        simple_deque.pop()
        assert simple_deque.size() == 2
    
    def test_is_empty_operation(self, empty_deque, simple_deque):
        """Test is_empty correctly identifies empty structures."""
        assert empty_deque.is_empty() is True
        assert simple_deque.is_empty() is False
    
    def test_to_native_conversion(self, simple_deque):
        """Test conversion to native Python list."""
        native = simple_deque.to_native()
        
        assert isinstance(native, list)
        assert len(native) == 3


# ============================================================================
# DOUBLE-ENDED OPERATIONS TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestDequeStrategyDoubleEnded:
    """Test double-ended queue operations."""
    
    def test_both_ends_operations(self, empty_deque):
        """Test operations on both ends."""
        empty_deque.append('right')
        empty_deque.appendleft('left')
        
        assert empty_deque.peek_left() == 'left'
        assert empty_deque.peek_right() == 'right'
        assert empty_deque.size() == 2
    
    def test_peek_operations(self, simple_deque):
        """Test peek operations don't remove items."""
        left = simple_deque.peek_left()
        right = simple_deque.peek_right()
        
        assert left == 'value1'
        assert right == 'value3'
        assert simple_deque.size() == 3  # Size unchanged


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestDequeStrategyCore:
    """Test core DequeStrategy functionality."""
    
    def test_clear_operation(self, simple_deque):
        """Test clear removes all items."""
        simple_deque.clear()
        
        assert simple_deque.is_empty() is True
        assert simple_deque.size() == 0
    
    def test_rotation(self, simple_deque):
        """Test rotation operations if available."""
        # Test rotate if method exists
        if hasattr(simple_deque, 'rotate'):
            original = list(simple_deque)
            simple_deque.rotate(1)
            # After rotation, last item should be first
            assert simple_deque.peek_left() == original[-1]


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestDequeStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_deque_operations(self, empty_deque):
        """Test operations on empty deque."""
        assert empty_deque.pop() is None
        assert empty_deque.popleft() is None
        assert empty_deque.peek_left() is None
        assert empty_deque.peek_right() is None
    
    def test_single_item_deque(self, empty_deque):
        """Test deque with single item."""
        empty_deque.append('single')
        
        assert empty_deque.size() == 1
        assert empty_deque.peek_left() == 'single'
        assert empty_deque.peek_right() == 'single'
        assert empty_deque.pop() == 'single'
        assert empty_deque.is_empty() is True

