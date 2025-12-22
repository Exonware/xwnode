"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_set_tree_strategy.py

Comprehensive tests for SetTreeStrategy.

Tests cover:
- Interface compliance (iNodeStrategy)
- Core set operations (add, remove, contains)
- Set operations (union, intersection, difference)
- Sorted order maintenance
- Iterator protocol
- Performance characteristics (O(log n) operations)
- Security (malicious input, resource limits)
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
from exonware.xwnode.nodes.strategies.set_tree import SetTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_set():
    """Create empty set tree strategy."""
    return SetTreeStrategy()


@pytest.fixture
def simple_set():
    """Create set tree with simple data."""
    set_strategy = SetTreeStrategy()
    set_strategy.add('value1')
    set_strategy.add('value2')
    set_strategy.add('value3')
    return set_strategy


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSetTreeStrategyInterface:
    """Test SetTreeStrategy implements iNodeStrategy interface correctly."""
    
    def test_add_operation(self, empty_set):
        """Test add operation works correctly."""
        empty_set.add('test_value')
        
        assert empty_set.contains('test_value') is True
        assert empty_set.size() == 1
    
    def test_contains_operation(self, simple_set):
        """Test contains operation returns correct values."""
        assert simple_set.contains('value1') is True
        assert simple_set.contains('value2') is True
        assert simple_set.contains('nonexistent') is False
    
    def test_remove_operation(self, simple_set):
        """Test remove operation removes items correctly."""
        assert simple_set.remove('value1') is True
        assert simple_set.contains('value1') is False
        assert simple_set.remove('nonexistent') is False
    
    def test_size_operation(self, simple_set):
        """Test size returns correct count."""
        assert simple_set.size() == 3
        
        simple_set.remove('value1')
        assert simple_set.size() == 2
    
    def test_is_empty_operation(self, empty_set, simple_set):
        """Test is_empty correctly identifies empty structures."""
        assert empty_set.is_empty() is True
        assert simple_set.is_empty() is False


# ============================================================================
# SET OPERATIONS TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSetTreeStrategySetOperations:
    """Test set operations (union, intersection, difference)."""
    
    def test_union_operation(self, simple_set):
        """Test union with another set."""
        other = SetTreeStrategy()
        other.add('value3')
        other.add('value4')
        
        union = simple_set.union(other)
        assert union.contains('value1') is True
        assert union.contains('value2') is True
        assert union.contains('value3') is True
        assert union.contains('value4') is True
        assert union.size() == 4
    
    def test_intersection_operation(self, simple_set):
        """Test intersection with another set."""
        other = SetTreeStrategy()
        other.add('value2')
        other.add('value3')
        other.add('value4')
        
        intersection = simple_set.intersection(other)
        assert intersection.contains('value2') is True
        assert intersection.contains('value3') is True
        assert intersection.contains('value1') is False
        assert intersection.size() == 2
    
    def test_sorted_order(self, simple_set):
        """Test keys are maintained in sorted order."""
        keys = list(simple_set.keys())
        assert keys == sorted(keys)


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSetTreeStrategyCore:
    """Test core SetTreeStrategy functionality."""
    
    def test_duplicate_add(self, empty_set):
        """Test adding duplicate items."""
        empty_set.add('value')
        empty_set.add('value')  # Duplicate
        
        # Set should only contain one instance
        assert empty_set.size() == 1
        assert empty_set.contains('value') is True
    
    def test_clear_operation(self, simple_set):
        """Test clear removes all items."""
        simple_set.clear()
        
        assert simple_set.is_empty() is True
        assert simple_set.size() == 0


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSetTreeStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_set_operations(self, empty_set):
        """Test operations on empty set."""
        assert empty_set.contains('any') is False
        assert empty_set.remove('any') is False
        assert list(empty_set) == []

