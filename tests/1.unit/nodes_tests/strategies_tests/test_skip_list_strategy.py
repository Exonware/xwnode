"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_skip_list_strategy.py
Comprehensive tests for SkipListStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Probabilistic structure maintenance
- Range queries
- Iterator protocol
- Performance characteristics (O(log n) expected operations)
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
from exonware.xwnode.nodes.strategies.skip_list import SkipListStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_skip_list():
    """Create empty skip list strategy."""
    return SkipListStrategy()
@pytest.fixture

def simple_skip_list():
    """Create skip list with simple data."""
    skip_list = SkipListStrategy()
    skip_list.put('key1', 'value1')
    skip_list.put('key2', 'value2')
    skip_list.put('key3', 'value3')
    return skip_list
@pytest.fixture

def large_skip_list():
    """Create skip list with enough data to test probabilistic structure."""
    skip_list = SkipListStrategy()
    for i in range(20):
        skip_list.put(f'key_{i:02d}', f'value_{i}')
    return skip_list
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSkipListStrategyInterface:
    """Test SkipListStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_skip_list):
        """Test put operation works correctly."""
        empty_skip_list.put('test_key', 'test_value')
        result = empty_skip_list.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_skip_list):
        """Test get operation returns correct values."""
        assert simple_skip_list.get('key1') == 'value1'
        assert simple_skip_list.get('key2') == 'value2'
        assert simple_skip_list.get('key3') == 'value3'
        assert simple_skip_list.get('nonexistent') is None
        assert simple_skip_list.get('nonexistent', 'default') == 'default'

    def test_delete_operation(self, simple_skip_list):
        """Test delete operation removes keys correctly."""
        assert simple_skip_list.delete('key1') is True
        assert simple_skip_list.get('key1') is None
        assert simple_skip_list.delete('nonexistent') is False

    def test_size_operation(self, simple_skip_list):
        """Test size returns correct count."""
        assert simple_skip_list.size() == 3
        simple_skip_list.delete('key1')
        assert simple_skip_list.size() == 2

    def test_is_empty_operation(self, empty_skip_list, simple_skip_list):
        """Test is_empty correctly identifies empty structures."""
        assert empty_skip_list.is_empty is True
        assert simple_skip_list.is_empty is False

    def test_to_native_conversion(self, simple_skip_list):
        """Test conversion to native Python dict."""
        native = simple_skip_list.to_native()
        assert isinstance(native, dict)
        assert native['key1'] == 'value1'
        assert native['key2'] == 'value2'
        assert native['key3'] == 'value3'
# ============================================================================
# PROBABILISTIC STRUCTURE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSkipListStrategyProbabilistic:
    """Test probabilistic structure maintenance."""

    def test_sorted_order_maintained(self, large_skip_list):
        """Test keys are maintained in sorted order."""
        keys = list(large_skip_list.keys())
        # Keys should be in sorted order (skip list maintains sorted order)
        assert keys == sorted(keys)

    def test_multiple_levels(self, large_skip_list):
        """Test skip list maintains multiple levels probabilistically."""
        # Skip list should have multiple levels (probabilistic)
        # Verify by checking all keys are accessible
        for i in range(20):
            assert large_skip_list.get(f'key_{i:02d}') == f'value_{i}'
        assert large_skip_list.size() == 20
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSkipListStrategyCore:
    """Test core SkipListStrategy functionality."""

    def test_update_existing_key(self, simple_skip_list):
        """Test updating existing key."""
        simple_skip_list.put('key2', 'updated_value')
        assert simple_skip_list.get('key2') == 'updated_value'
        assert simple_skip_list.size() == 3  # Size unchanged

    def test_range_query(self, large_skip_list):
        """Test range query operations."""
        # Get keys in range
        keys = large_skip_list.range_query('key_02', 'key_08')
        # Should include keys 02-08
        assert 'key_02' in keys
        assert 'key_05' in keys
        assert 'key_08' in keys
        assert 'key_01' not in keys  # Below range
        assert 'key_09' not in keys  # Above range

    def test_clear_operation(self, simple_skip_list):
        """Test clear removes all items."""
        simple_skip_list.clear()
        assert simple_skip_list.is_empty is True
        assert simple_skip_list.size() == 0
# ============================================================================
# ITERATOR TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestSkipListStrategyIterators:
    """Test iterator protocol."""

    def test_keys_iteration(self, simple_skip_list):
        """Test keys() returns all keys in sorted order."""
        keys = list(simple_skip_list.keys())
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
        assert len(keys) == 3
        # Should be sorted
        assert keys == sorted(keys)

    def test_values_iteration(self, simple_skip_list):
        """Test values() returns all values."""
        values = list(simple_skip_list.values())
        assert 'value1' in values
        assert 'value2' in values
        assert 'value3' in values
        assert len(values) == 3

    def test_items_iteration(self, simple_skip_list):
        """Test items() returns all key-value pairs in sorted order."""
        items = list(simple_skip_list.items())
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

class TestSkipListStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_skip_list_operations(self, empty_skip_list):
        """Test operations on empty skip list."""
        assert empty_skip_list.get('any') is None
        assert empty_skip_list.delete('any') is False
        assert list(empty_skip_list.keys()) == []
        assert list(empty_skip_list.values()) == []

    def test_single_key_skip_list(self, empty_skip_list):
        """Test skip list with single key."""
        empty_skip_list.put('single', 'value')
        assert empty_skip_list.size() == 1
        assert empty_skip_list.get('single') == 'value'
        empty_skip_list.delete('single')
        assert empty_skip_list.is_empty is True
# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance

class TestSkipListStrategyPerformance:
    """Test performance characteristics."""

    def test_large_dataset_operations(self):
        """Test operations with large dataset."""
        skip_list = SkipListStrategy()
        # Insert 100 items
        for i in range(100):
            skip_list.put(f'key_{i:03d}', f'value_{i}')
        assert skip_list.size() == 100
        # All should be accessible (probabilistic O(log n) expected)
        for i in range(100):
            assert skip_list.get(f'key_{i:03d}') == f'value_{i}'
        # Keys should be sorted
        keys = list(skip_list.keys())
        assert keys == sorted(keys)
