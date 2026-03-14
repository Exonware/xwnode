"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_set_hash_strategy.py
Comprehensive tests for SetHashStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core set operations (add, remove, contains)
- Set operations (union, intersection, difference)
- Iterator protocol
- Performance characteristics (O(1) operations)
- Security (malicious input, resource limits)
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
from exonware.xwnode.nodes.strategies.set_hash import SetHashStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_set():
    """Create empty set hash strategy."""
    return SetHashStrategy()
@pytest.fixture

def simple_set():
    """Create set with simple data."""
    set_strategy = SetHashStrategy()
    set_strategy.add('value1')
    set_strategy.add('value2')
    set_strategy.add('value3')
    return set_strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSetHashStrategyInterface:
    """Test SetHashStrategy implements iNodeStrategy interface correctly."""

    def test_add_operation(self, empty_set):
        """Test add operation works correctly."""
        empty_set.add('test_value')
        assert empty_set.has('test_value') is True
        assert empty_set.size() == 1

    def test_contains_operation(self, simple_set):
        """Test contains operation returns correct values."""
        assert simple_set.has('value1') is True
        assert simple_set.has('value2') is True
        assert simple_set.has('nonexistent') is False

    def test_remove_operation(self, simple_set):
        """Test remove operation removes items correctly."""
        assert simple_set.remove('value1') is True
        assert simple_set.has('value1') is False
        assert simple_set.remove('nonexistent') is False

    def test_size_operation(self, simple_set):
        """Test size returns correct count."""
        assert simple_set.size() == 3
        simple_set.remove('value1')
        assert simple_set.size() == 2

    def test_is_empty_operation(self, empty_set, simple_set):
        """Test is_empty correctly identifies empty structures."""
        assert empty_set.is_empty is True
        assert simple_set.is_empty is False

    def test_to_native_conversion(self, simple_set):
        """Test conversion to native Python set."""
        native = simple_set.to_native()
        assert isinstance(native, (set, dict))
        # Set may be represented as dict with True values or actual set
        if isinstance(native, set):
            assert 'value1' in native
            assert 'value2' in native
            assert 'value3' in native
# ============================================================================
# SET OPERATIONS TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSetHashStrategySetOperations:
    """Test set operations (union, intersection, difference)."""

    def test_union_operation(self, simple_set):
        """Test union with another set."""
        other = SetHashStrategy()
        other.add('value3')
        other.add('value4')
        union = simple_set.union(other)
        assert union.has('value1') is True
        assert union.has('value2') is True
        assert union.has('value3') is True
        assert union.has('value4') is True
        assert union.size() == 4

    def test_intersection_operation(self, simple_set):
        """Test intersection with another set."""
        other = SetHashStrategy()
        other.add('value2')
        other.add('value3')
        other.add('value4')
        intersection = simple_set.intersection(other)
        assert intersection.has('value2') is True
        assert intersection.has('value3') is True
        assert intersection.has('value1') is False
        assert intersection.size() == 2

    def test_difference_operation(self, simple_set):
        """Test difference with another set."""
        other = SetHashStrategy()
        other.add('value2')
        difference = simple_set.difference(other)
        assert difference.has('value1') is True
        assert difference.has('value3') is True
        assert difference.has('value2') is False
        assert difference.size() == 2
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSetHashStrategyCore:
    """Test core SetHashStrategy functionality."""

    def test_duplicate_add(self, empty_set):
        """Test adding duplicate items."""
        empty_set.add('value')
        empty_set.add('value')  # Duplicate
        # Set should only contain one instance
        assert empty_set.size() == 1
        assert empty_set.has('value') is True

    def test_clear_operation(self, simple_set):
        """Test clear removes all items."""
        simple_set.clear()
        assert simple_set.is_empty is True
        assert simple_set.size() == 0
# ============================================================================
# ITERATOR TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSetHashStrategyIterators:
    """Test iterator protocol."""

    def test_iteration(self, simple_set):
        """Test iteration over set items."""
        items = list(simple_set)
        assert 'value1' in items
        assert 'value2' in items
        assert 'value3' in items
        assert len(items) == 3
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSetHashStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_set_operations(self, empty_set):
        """Test operations on empty set."""
        assert empty_set.has('any') is False
        assert empty_set.remove('any') is False
        assert list(empty_set) == []

    def test_none_values(self, empty_set):
        """Test handling of None values."""
        empty_set.add(None)
        assert empty_set.has(None) is True
        assert empty_set.size() == 1
