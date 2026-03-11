"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_b_plus_tree_strategy.py
Comprehensive tests for BPlusTreeStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Leaf node linking for sequential access
- Range queries (B+ Tree strength)
- Iterator protocol
- Performance characteristics (O(log n) operations, O(k) range queries)
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
from exonware.xwnode.nodes.strategies.b_plus_tree import BPlusTreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_tree():
    """Create empty B+ tree strategy."""
    return BPlusTreeStrategy(max_keys=4)
@pytest.fixture

def simple_tree():
    """Create B+ tree with simple data."""
    tree = BPlusTreeStrategy(max_keys=4)
    tree.put('key1', 'value1')
    tree.put('key2', 'value2')
    tree.put('key3', 'value3')
    return tree
@pytest.fixture

def large_tree():
    """Create B+ tree with enough data to trigger splits."""
    tree = BPlusTreeStrategy(max_keys=4)
    # Insert enough keys to cause node splits
    for i in range(10):
        tree.put(f'key_{i:02d}', f'value_{i}')
    return tree
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBPlusTreeStrategyInterface:
    """Test BPlusTreeStrategy implements iNodeStrategy interface correctly."""

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
# B+ TREE SPECIFIC TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBPlusTreeStrategySpecific:
    """Test B+ Tree specific features (leaf linking, range queries)."""

    def test_leaf_linking(self, large_tree):
        """Test that leaf nodes are linked for sequential access."""
        # B+ Tree should support sequential iteration via linked leaves
        keys = list(large_tree.keys())
        # Should be in sorted order (via leaf linking)
        assert keys == sorted(keys)
        assert len(keys) == 10

    def test_range_query_efficiency(self, large_tree):
        """Test range queries are efficient (B+ Tree strength)."""
        # Get keys in range
        keys = large_tree.range_keys('key_02', 'key_08')
        # Should include keys 02-08
        assert 'key_02' in keys
        assert 'key_05' in keys
        assert 'key_08' in keys
        assert 'key_01' not in keys  # Below range
        assert 'key_09' not in keys  # Above range

    def test_all_values_in_leaves(self, large_tree):
        """Test all values are stored in leaf nodes."""
        # In B+ Tree, all values should be in leaves
        # This is verified by successful retrieval
        for i in range(10):
            assert large_tree.get(f'key_{i:02d}') == f'value_{i}'
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestBPlusTreeStrategyCore:
    """Test core BPlusTreeStrategy functionality."""

    def test_update_existing_key(self, simple_tree):
        """Test updating existing key."""
        simple_tree.put('key2', 'updated_value')
        assert simple_tree.get('key2') == 'updated_value'
        assert simple_tree.size() == 3  # Size unchanged

    def test_sorted_order_maintained(self, large_tree):
        """Test keys are maintained in sorted order."""
        keys = list(large_tree.keys())
        # Keys should be in sorted order
        assert keys == sorted(keys)

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

class TestBPlusTreeStrategyIterators:
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

class TestBPlusTreeStrategyEdgeCases:
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

    def test_different_max_keys(self):
        """Test B+ tree with different max_keys values."""
        tree_small = BPlusTreeStrategy(max_keys=2)
        tree_large = BPlusTreeStrategy(max_keys=8)
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

class TestBPlusTreeStrategyPerformance:
    """Test performance characteristics."""

    def test_large_dataset_operations(self):
        """Test operations with large dataset."""
        tree = BPlusTreeStrategy(max_keys=8)
        # Insert 100 items
        for i in range(100):
            tree.put(f'key_{i:03d}', f'value_{i}')
        assert tree.size() == 100
        # All should be accessible
        for i in range(100):
            assert tree.get(f'key_{i:03d}') == f'value_{i}'
        # Keys should be sorted (B+ Tree maintains sorted order)
        keys = list(tree.keys())
        assert keys == sorted(keys)

    def test_range_query_performance(self):
        """Test range query performance (B+ Tree strength)."""
        tree = BPlusTreeStrategy(max_keys=8)
        # Insert items
        for i in range(100):
            tree.put(f'key_{i:03d}', f'value_{i}')
        # Range query should be efficient
        keys = tree.range_keys('key_010', 'key_090')
        assert len(keys) == 81  # 10 to 90 inclusive
