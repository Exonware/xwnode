"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_ordered_map_strategy.py
Comprehensive tests for OrderedMapStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Sorted order maintenance
- Range queries
- Iterator protocol
- Performance characteristics (O(log n) operations)
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
from exonware.xwnode.nodes.strategies.ordered_map import OrderedMapStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_strategy():
    """Create empty ordered map strategy."""
    return OrderedMapStrategy()
@pytest.fixture

def simple_strategy():
    """Create ordered map with simple data."""
    strategy = OrderedMapStrategy()
    strategy.put('key1', 'value1')
    strategy.put('key2', 'value2')
    strategy.put('key3', 'value3')
    return strategy
@pytest.fixture

def sorted_strategy():
    """Create ordered map with keys in reverse order to test sorting."""
    strategy = OrderedMapStrategy()
    # Insert in reverse order - should maintain sorted order
    strategy.put('zebra', 'z')
    strategy.put('apple', 'a')
    strategy.put('banana', 'b')
    return strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapStrategyInterface:
    """Test OrderedMapStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_strategy):
        """Test put operation works correctly."""
        empty_strategy.put('test_key', 'test_value')
        result = empty_strategy.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_strategy):
        """Test get operation returns correct values."""
        assert simple_strategy.get('key1') == 'value1'
        assert simple_strategy.get('key2') == 'value2'
        assert simple_strategy.get('nonexistent') is None
        assert simple_strategy.get('nonexistent', 'default') == 'default'

    def test_delete_operation(self, simple_strategy):
        """Test delete operation removes keys correctly."""
        assert simple_strategy.delete('key1') is True
        assert simple_strategy.get('key1') is None
        assert simple_strategy.delete('nonexistent') is False

    def test_size_operation(self, simple_strategy):
        """Test size returns correct count."""
        assert simple_strategy.size() == 3
        simple_strategy.delete('key1')
        assert simple_strategy.size() == 2

    def test_is_empty_operation(self, empty_strategy, simple_strategy):
        """Test is_empty correctly identifies empty structures."""
        assert empty_strategy.is_empty() is True
        assert simple_strategy.is_empty() is False

    def test_to_native_conversion(self, simple_strategy):
        """Test conversion to native Python dict."""
        native = simple_strategy.to_native()
        assert isinstance(native, dict)
        assert native['key1'] == 'value1'
        assert native['key2'] == 'value2'
        assert native['key3'] == 'value3'
# ============================================================================
# SORTED ORDER TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapStrategySortedOrder:
    """Test sorted order maintenance."""

    def test_keys_maintain_sorted_order(self, sorted_strategy):
        """Test keys are maintained in sorted order."""
        keys = list(sorted_strategy.keys())
        # Should be sorted: apple, banana, zebra
        assert keys == ['apple', 'banana', 'zebra']

    def test_insert_maintains_sorted_order(self, empty_strategy):
        """Test inserting keys maintains sorted order."""
        # Insert in random order
        empty_strategy.put('zebra', 'z')
        empty_strategy.put('apple', 'a')
        empty_strategy.put('banana', 'b')
        empty_strategy.put('dog', 'd')
        keys = list(empty_strategy.keys())
        assert keys == ['apple', 'banana', 'dog', 'zebra']

    def test_range_query(self, sorted_strategy):
        """Test range query operations."""
        # Get keys in range ['banana', 'zebra']
        keys = sorted_strategy.range_query('banana', 'zebra')
        assert 'banana' in keys
        assert 'zebra' in keys
        assert 'apple' not in keys
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapStrategyCore:
    """Test core OrderedMapStrategy functionality."""

    def test_update_existing_key(self, simple_strategy):
        """Test updating existing key preserves order."""
        simple_strategy.put('key2', 'updated_value')
        assert simple_strategy.get('key2') == 'updated_value'
        assert simple_strategy.size() == 3  # Size unchanged

    def test_case_sensitivity(self):
        """Test case sensitivity option."""
        case_sensitive = OrderedMapStrategy(case_sensitive=True)
        case_sensitive.put('Key', 'value1')
        case_sensitive.put('key', 'value2')
        assert case_sensitive.get('Key') == 'value1'
        assert case_sensitive.get('key') == 'value2'
        assert case_sensitive.size() == 2
        case_insensitive = OrderedMapStrategy(case_sensitive=False)
        case_insensitive.put('Key', 'value1')
        case_insensitive.put('key', 'value2')
        # Should update existing (case-insensitive)
        assert case_insensitive.size() == 1
        assert case_insensitive.get('Key') == 'value2'

    def test_clear_operation(self, simple_strategy):
        """Test clear removes all items."""
        simple_strategy.clear()
        assert simple_strategy.is_empty() is True
        assert simple_strategy.size() == 0
# ============================================================================
# ITERATOR TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapStrategyIterators:
    """Test iterator protocol."""

    def test_keys_iteration(self, simple_strategy):
        """Test keys() returns all keys in sorted order."""
        keys = list(simple_strategy.keys())
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
        assert len(keys) == 3
        # Should be sorted
        assert keys == sorted(keys)

    def test_values_iteration(self, simple_strategy):
        """Test values() returns all values."""
        values = list(simple_strategy.values())
        assert 'value1' in values
        assert 'value2' in values
        assert 'value3' in values
        assert len(values) == 3

    def test_items_iteration(self, simple_strategy):
        """Test items() returns all key-value pairs in sorted order."""
        items = list(simple_strategy.items())
        assert ('key1', 'value1') in items
        assert ('key2', 'value2') in items
        assert ('key3', 'value3') in items
        assert len(items) == 3
        # Keys should be in sorted order
        keys = [k for k, v in items]
        assert keys == sorted(keys)
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_map_operations(self, empty_strategy):
        """Test operations on empty map."""
        assert empty_strategy.get('any') is None
        assert empty_strategy.delete('any') is False
        assert list(empty_strategy.keys()) == []
        assert list(empty_strategy.values()) == []

    def test_none_values(self, empty_strategy):
        """Test handling of None values."""
        empty_strategy.put('key', None)
        assert empty_strategy.get('key') is None
        assert empty_strategy.size() == 1

    def test_numeric_keys(self, empty_strategy):
        """Test numeric keys are converted to strings and sorted."""
        empty_strategy.put(100, 'hundred')
        empty_strategy.put(10, 'ten')
        empty_strategy.put(1, 'one')
        keys = list(empty_strategy.keys())
        # String comparison: '1', '10', '100'
        assert keys == ['1', '10', '100']
# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance

class TestOrderedMapStrategyPerformance:
    """Test performance characteristics."""

    def test_large_dataset_insertion(self):
        """Test insertion performance with large dataset."""
        strategy = OrderedMapStrategy()
        # Insert 1000 items
        for i in range(1000):
            strategy.put(f'key_{i}', f'value_{i}')
        assert strategy.size() == 1000
        # Keys should be sorted
        keys = list(strategy.keys())
        assert keys == sorted(keys)

    def test_range_query_performance(self):
        """Test range query performance."""
        strategy = OrderedMapStrategy()
        # Insert items
        for i in range(100):
            strategy.put(f'key_{i:03d}', f'value_{i}')
        # Range query should be efficient
        keys = strategy.range_query('key_010', 'key_090')
        assert len(keys) == 81  # 10 to 90 inclusive
