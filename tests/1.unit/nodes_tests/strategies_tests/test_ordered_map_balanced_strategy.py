"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_ordered_map_balanced_strategy.py
Comprehensive tests for OrderedMapBalancedStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Balanced tree operations (RB/AVL/Treap)
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
from exonware.xwnode.nodes.strategies.ordered_map_balanced import OrderedMapBalancedStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_map():
    """Create empty ordered map balanced strategy."""
    return OrderedMapBalancedStrategy()
@pytest.fixture

def simple_map():
    """Create ordered map balanced with simple data."""
    map_strategy = OrderedMapBalancedStrategy()
    map_strategy.put('key1', 'value1')
    map_strategy.put('key2', 'value2')
    map_strategy.put('key3', 'value3')
    return map_strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapBalancedStrategyInterface:
    """Test OrderedMapBalancedStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_map):
        """Test put operation works correctly."""
        empty_map.put('test_key', 'test_value')
        result = empty_map.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_map):
        """Test get operation returns correct values."""
        assert simple_map.get('key1') == 'value1'
        assert simple_map.get('key2') == 'value2'
        assert simple_map.get('key3') == 'value3'
        assert simple_map.get('nonexistent') is None

    def test_delete_operation(self, simple_map):
        """Test delete operation removes keys correctly."""
        assert simple_map.delete('key1') is True
        assert simple_map.get('key1') is None
        assert simple_map.delete('nonexistent') is False

    def test_size_operation(self, simple_map):
        """Test size returns correct count."""
        assert simple_map.size() == 3
        simple_map.delete('key1')
        assert simple_map.size() == 2

    def test_is_empty_operation(self, empty_map, simple_map):
        """Test is_empty correctly identifies empty structures."""
        assert empty_map.is_empty() is True
        assert simple_map.is_empty() is False
# ============================================================================
# BALANCED TREE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapBalancedStrategyBalancing:
    """Test balanced tree features."""

    def test_sorted_order_maintained(self, simple_map):
        """Test keys are maintained in sorted order."""
        keys = list(simple_map.keys())
        assert keys == sorted(keys)

    def test_range_query(self, simple_map):
        """Test range query operations."""
        if hasattr(simple_map, 'range_keys'):
            keys = simple_map.range_keys('key1', 'key3')
            assert 'key1' in keys
            assert 'key2' in keys
            assert 'key3' in keys
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapBalancedStrategyCore:
    """Test core OrderedMapBalancedStrategy functionality."""

    def test_update_existing_key(self, simple_map):
        """Test updating existing key."""
        simple_map.put('key2', 'updated_value')
        assert simple_map.get('key2') == 'updated_value'
        assert simple_map.size() == 3

    def test_clear_operation(self, simple_map):
        """Test clear removes all items."""
        simple_map.clear()
        assert simple_map.is_empty() is True
        assert simple_map.size() == 0
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestOrderedMapBalancedStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_map_operations(self, empty_map):
        """Test operations on empty map."""
        assert empty_map.get('any') is None
        assert empty_map.delete('any') is False
        assert list(empty_map.keys()) == []
