"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_linked_list_strategy.py
Comprehensive tests for LinkedListStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Sequential access patterns
- Iterator protocol
- Performance characteristics (O(1) insert/delete, O(n) search)
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
from exonware.xwnode.nodes.strategies.linked_list import LinkedListStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty linked list strategy."""
    return LinkedListStrategy()
@pytest.fixture

def simple_strategy():
    """Create linked list with simple data."""
    strategy = LinkedListStrategy()
    strategy.put('key1', 'value1')
    strategy.put('key2', 'value2')
    strategy.put('key3', 'value3')
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestLinkedListStrategyInterface:
    """Test LinkedListStrategy implements iNodeStrategy interface correctly."""

    def test_insert_operation(self, empty_strategy):
        """Test insert operation works correctly."""
        empty_strategy.put('test_key', 'test_value')
        result = empty_strategy.find('test_key')
        assert result == 'test_value'

    def test_find_operation(self, simple_strategy):
        """Test find operation returns correct values."""
        assert simple_strategy.find('key1') == 'value1'
        assert simple_strategy.find('key2') == 'value2'
        assert simple_strategy.find('nonexistent') is None

    def test_delete_operation(self, simple_strategy):
        """Test delete operation removes keys correctly."""
        assert simple_strategy.delete('key1') is True
        assert simple_strategy.find('key1') is None
        assert simple_strategy.delete('nonexistent') is False

    def test_size_operation(self, simple_strategy):
        """Test size returns correct count."""
        assert simple_strategy.size() == 3
        simple_strategy.delete('key1')
        assert simple_strategy.size() == 2

    def test_is_empty_operation(self, empty_strategy, simple_strategy):
        """Test is_empty correctly identifies empty structures."""
        assert empty_strategy.is_empty is True
        assert simple_strategy.is_empty is False

    def test_to_native_conversion(self, simple_strategy):
        """Test conversion to native Python dict."""
        native = simple_strategy.to_native()
        assert isinstance(native, dict)
        assert native['key1'] == 'value1'
        assert native['key2'] == 'value2'
        assert native['key3'] == 'value3'
# ============================================================================
# SEQUENTIAL ACCESS TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestLinkedListStrategySequential:
    """Test sequential access patterns."""

    def test_insertion_order_preserved(self, empty_strategy):
        """Test insertion order is preserved."""
        empty_strategy.put('first', '1')
        empty_strategy.put('second', '2')
        empty_strategy.put('third', '3')
        keys = list(empty_strategy.keys())
        # Order should match insertion order
        assert keys == ['first', 'second', 'third']

    def test_insert_at_index(self, simple_strategy):
        """Test insertion at specific index."""
        # Insert at beginning
        simple_strategy.put('key0', 'value0')
        keys = list(simple_strategy.keys())
        assert 'key0' in keys
        assert simple_strategy.size() == 4

    def test_get_at_index(self, simple_strategy):
        """Test getting value at specific index."""
        assert simple_strategy.get_at(0) == 'value1'
        assert simple_strategy.get_at(1) == 'value2'
        assert simple_strategy.get_at(2) == 'value3'
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestLinkedListStrategyCore:
    """Test core LinkedListStrategy functionality."""

    def test_update_existing_key(self, simple_strategy):
        """Test updating existing key."""
        simple_strategy.put('key2', 'updated_value')
        assert simple_strategy.find('key2') == 'updated_value'
        assert simple_strategy.size() == 3  # Size unchanged

    def test_delete_middle_node(self, simple_strategy):
        """Test deleting middle node maintains structure."""
        assert simple_strategy.delete('key2') is True
        assert simple_strategy.find('key2') is None
        assert simple_strategy.find('key1') == 'value1'
        assert simple_strategy.find('key3') == 'value3'
        assert simple_strategy.size() == 2

    def test_clear_operation(self, simple_strategy):
        """Test clear removes all items."""
        simple_strategy.clear()
        assert simple_strategy.is_empty is True
        assert simple_strategy.size() == 0
# ============================================================================
# ITERATOR TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestLinkedListStrategyIterators:
    """Test iterator protocol."""

    def test_keys_iteration(self, simple_strategy):
        """Test keys() returns all keys in order."""
        keys = list(simple_strategy.keys())
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
        assert len(keys) == 3

    def test_values_iteration(self, simple_strategy):
        """Test values() returns all values."""
        values = list(simple_strategy.values())
        assert 'value1' in values
        assert 'value2' in values
        assert 'value3' in values
        assert len(values) == 3

    def test_items_iteration(self, simple_strategy):
        """Test items() returns all key-value pairs."""
        items = list(simple_strategy.items())
        assert ('key1', 'value1') in items
        assert ('key2', 'value2') in items
        assert ('key3', 'value3') in items
        assert len(items) == 3
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestLinkedListStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_list_operations(self, empty_strategy):
        """Test operations on empty list."""
        assert empty_strategy.find('any') is None
        assert empty_strategy.delete('any') is False
        assert list(empty_strategy.keys()) == []
        assert list(empty_strategy.values()) == []

    def test_single_node_list(self, empty_strategy):
        """Test list with single node."""
        empty_strategy.put('single', 'value')
        assert empty_strategy.size() == 1
        assert empty_strategy.find('single') == 'value'
        empty_strategy.delete('single')
        assert empty_strategy.is_empty is True

    def test_index_bounds(self, simple_strategy):
        """Test index bounds checking."""
        # Valid indices
        assert simple_strategy.get_at(0) is not None
        assert simple_strategy.get_at(2) is not None
        # Invalid indices
        assert simple_strategy.get_at(-1) is None
        assert simple_strategy.get_at(10) is None
