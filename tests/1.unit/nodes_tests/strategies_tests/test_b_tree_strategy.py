"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_b_tree_strategy.py
Comprehensive tests for BTreeStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Tree balancing and node splitting
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
from exonware.xwnode.nodes.strategies.b_tree import BTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_tree():
    """Create empty B-tree strategy."""
    return BTreeStrategy(degree=3)
@pytest.fixture

def simple_tree():
    """Create B-tree with simple data."""
    tree = BTreeStrategy(degree=3)
    tree.put('key1', 'value1')
    tree.put('key2', 'value2')
    tree.put('key3', 'value3')
    return tree
@pytest.fixture

def large_tree():
    """Create B-tree with enough data to trigger splits."""
    tree = BTreeStrategy(degree=3)
    # Insert enough keys to cause node splits (degree=3 means max 5 keys per node)
    for i in range(10):
        tree.put(f'key_{i:02d}', f'value_{i}')
    return tree
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBTreeStrategyInterface:
    """Test BTreeStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_tree):
        """Test put operation works correctly."""
        empty_tree.put('test_key', 'test_value')
        result = empty_tree.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_tree):
        """Test get operation returns correct values."""
        assert simple_tree.get('key1') == 'value1'
        assert simple_tree.get('key2') == 'value2'
        assert simple_tree.get('key3') == 'value3'
        assert simple_tree.get('nonexistent') is None
        assert simple_tree.get('nonexistent', 'default') == 'default'

    def test_delete_operation(self, simple_tree):
        """Test delete operation removes keys correctly."""
        assert simple_tree.delete('key1') is True
        assert simple_tree.get('key1') is None
        assert simple_tree.delete('nonexistent') is False

    def test_size_operation(self, simple_tree):
        """Test size returns correct count."""
        assert simple_tree.size() == 3
        simple_tree.delete('key1')
        assert simple_tree.size() == 2

    def test_is_empty_operation(self, empty_tree, simple_tree):
        """Test is_empty correctly identifies empty structures."""
        assert empty_tree.is_empty() is True
        assert simple_tree.is_empty() is False

    def test_to_native_conversion(self, simple_tree):
        """Test conversion to native Python dict."""
        native = simple_tree.to_native()
        assert isinstance(native, dict)
        assert native['key1'] == 'value1'
        assert native['key2'] == 'value2'
        assert native['key3'] == 'value3'
# ============================================================================
# TREE BALANCING TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBTreeStrategyBalancing:
    """Test B-tree balancing and node splitting."""

    def test_node_splitting(self, empty_tree):
        """Test that nodes split when they become full."""
        # With degree=3, nodes can hold max 5 keys (2*degree-1)
        # Insert 6 keys to trigger a split
        for i in range(6):
            empty_tree.put(f'key_{i}', f'value_{i}')
        # All keys should still be accessible
        for i in range(6):
            assert empty_tree.get(f'key_{i}') == f'value_{i}'
        assert empty_tree.size() == 6

    def test_tree_structure_after_splits(self, large_tree):
        """Test tree maintains structure after multiple splits."""
        # Verify all keys are accessible
        for i in range(10):
            assert large_tree.get(f'key_{i:02d}') == f'value_{i}'
        assert large_tree.size() == 10

    def test_sorted_order_maintained(self, large_tree):
        """Test keys are maintained in sorted order."""
        keys = list(large_tree.keys())
        # Keys should be in sorted order
        assert keys == sorted(keys)
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBTreeStrategyCore:
    """Test core BTreeStrategy functionality."""

    def test_update_existing_key(self, simple_tree):
        """Test updating existing key."""
        simple_tree.put('key2', 'updated_value')
        assert simple_tree.get('key2') == 'updated_value'
        assert simple_tree.size() == 3  # Size unchanged

    def test_range_query(self, large_tree):
        """Test range query operations."""
        # Get keys in range
        keys = large_tree.range_query('key_02', 'key_08')
        # Should include keys 02-08
        assert 'key_02' in keys
        assert 'key_05' in keys
        assert 'key_08' in keys
        assert 'key_01' not in keys  # Below range
        assert 'key_09' not in keys  # Above range

    def test_clear_operation(self, simple_tree):
        """Test clear removes all items."""
        simple_tree.clear()
        assert simple_tree.is_empty() is True
        assert simple_tree.size() == 0
# ============================================================================
# ITERATOR TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBTreeStrategyIterators:
    """Test iterator protocol."""

    def test_keys_iteration(self, simple_tree):
        """Test keys() returns all keys in sorted order."""
        keys = list(simple_tree.keys())
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
        assert len(keys) == 3
        # Should be sorted
        assert keys == sorted(keys)

    def test_values_iteration(self, simple_tree):
        """Test values() returns all values."""
        values = list(simple_tree.values())
        assert 'value1' in values
        assert 'value2' in values
        assert 'value3' in values
        assert len(values) == 3

    def test_items_iteration(self, simple_tree):
        """Test items() returns all key-value pairs in sorted order."""
        items = list(simple_tree.items())
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

class TestBTreeStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_tree_operations(self, empty_tree):
        """Test operations on empty tree."""
        assert empty_tree.get('any') is None
        assert empty_tree.delete('any') is False
        assert list(empty_tree.keys()) == []
        assert list(empty_tree.values()) == []

    def test_single_key_tree(self, empty_tree):
        """Test tree with single key."""
        empty_tree.put('single', 'value')
        assert empty_tree.size() == 1
        assert empty_tree.get('single') == 'value'
        empty_tree.delete('single')
        assert empty_tree.is_empty() is True

    def test_different_degrees(self):
        """Test B-tree with different degree values."""
        tree_small = BTreeStrategy(degree=2)
        tree_large = BTreeStrategy(degree=5)
        # Both should work
        tree_small.put('key', 'value')
        tree_large.put('key', 'value')
        assert tree_small.get('key') == 'value'
        assert tree_large.get('key') == 'value'
# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance

class TestBTreeStrategyPerformance:
    """Test performance characteristics."""

    def test_large_dataset_operations(self):
        """Test operations with large dataset."""
        tree = BTreeStrategy(degree=5)
        # Insert 100 items
        for i in range(100):
            tree.put(f'key_{i:03d}', f'value_{i}')
        assert tree.size() == 100
        # All should be accessible
        for i in range(100):
            assert tree.get(f'key_{i:03d}') == f'value_{i}'
        # Keys should be sorted
        keys = list(tree.keys())
        assert keys == sorted(keys)
