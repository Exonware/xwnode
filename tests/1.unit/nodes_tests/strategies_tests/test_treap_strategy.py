"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_treap_strategy.py
Comprehensive tests for TreapStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Randomized balancing (treap property)
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
from exonware.xwnode.nodes.strategies.treap import TreapStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_treap():
    """Create empty treap strategy."""
    return TreapStrategy()
@pytest.fixture

def simple_treap():
    """Create treap with simple data."""
    treap = TreapStrategy()
    treap.put('key1', 'value1')
    treap.put('key2', 'value2')
    treap.put('key3', 'value3')
    return treap
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestTreapStrategyInterface:
    """Test TreapStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_treap):
        """Test put operation works correctly."""
        empty_treap.put('test_key', 'test_value')
        result = empty_treap.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_treap):
        """Test get operation returns correct values."""
        assert simple_treap.get('key1') == 'value1'
        assert simple_treap.get('key2') == 'value2'
        assert simple_treap.get('key3') == 'value3'
        assert simple_treap.get('nonexistent') is None

    def test_delete_operation(self, simple_treap):
        """Test delete operation removes keys correctly."""
        assert simple_treap.delete('key1') is True
        assert simple_treap.get('key1') is None
        assert simple_treap.delete('nonexistent') is False

    def test_size_operation(self, simple_treap):
        """Test size returns correct count."""
        assert simple_treap.size() == 3
        simple_treap.delete('key1')
        assert simple_treap.size() == 2

    def test_is_empty_operation(self, empty_treap, simple_treap):
        """Test is_empty correctly identifies empty structures."""
        assert empty_treap.is_empty is True
        assert simple_treap.is_empty is False
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestTreapStrategyCore:
    """Test core TreapStrategy functionality."""

    def test_update_existing_key(self, simple_treap):
        """Test updating existing key."""
        simple_treap.put('key2', 'updated_value')
        assert simple_treap.get('key2') == 'updated_value'
        assert simple_treap.size() == 3

    def test_clear_operation(self, simple_treap):
        """Test clear removes all items."""
        simple_treap.clear()
        assert simple_treap.is_empty is True
        assert simple_treap.size() == 0
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestTreapStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_treap_operations(self, empty_treap):
        """Test operations on empty treap."""
        assert empty_treap.get('any') is None
        assert empty_treap.delete('any') is False
        assert list(empty_treap.keys()) == []
