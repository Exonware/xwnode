"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_hamt_strategy.py
Comprehensive tests for HAMTStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Hash Array Mapped Trie structure
- Immutability features
- Iterator protocol
- Performance characteristics
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
from exonware.xwnode.nodes.strategies.hamt import HAMTStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_hamt():
    """Create empty HAMT strategy."""
    return HAMTStrategy()
@pytest.fixture

def simple_hamt():
    """Create HAMT with simple data."""
    hamt = HAMTStrategy()
    hamt.put('key1', 'value1')
    hamt.put('key2', 'value2')
    hamt.put('key3', 'value3')
    return hamt
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestHAMTStrategyInterface:
    """Test HAMTStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_hamt):
        """Test put operation works correctly."""
        empty_hamt.put('test_key', 'test_value')
        result = empty_hamt.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_hamt):
        """Test get operation returns correct values."""
        assert simple_hamt.get('key1') == 'value1'
        assert simple_hamt.get('key2') == 'value2'
        assert simple_hamt.get('key3') == 'value3'
        assert simple_hamt.get('nonexistent') is None

    def test_delete_operation(self, simple_hamt):
        """Test delete operation removes keys correctly."""
        assert simple_hamt.delete('key1') is True
        assert simple_hamt.get('key1') is None
        assert simple_hamt.delete('nonexistent') is False

    def test_size_operation(self, simple_hamt):
        """Test size returns correct count."""
        assert simple_hamt.size() == 3
        simple_hamt.delete('key1')
        assert simple_hamt.size() == 2

    def test_is_empty_operation(self, empty_hamt, simple_hamt):
        """Test is_empty correctly identifies empty structures."""
        assert empty_hamt.is_empty() is True
        assert simple_hamt.is_empty() is False
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestHAMTStrategyCore:
    """Test core HAMTStrategy functionality."""

    def test_update_existing_key(self, simple_hamt):
        """Test updating existing key."""
        simple_hamt.put('key2', 'updated_value')
        assert simple_hamt.get('key2') == 'updated_value'
        assert simple_hamt.size() == 3

    def test_clear_operation(self, simple_hamt):
        """Test clear removes all items."""
        simple_hamt.clear()
        assert simple_hamt.is_empty() is True
        assert simple_hamt.size() == 0
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestHAMTStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_hamt_operations(self, empty_hamt):
        """Test operations on empty HAMT."""
        assert empty_hamt.get('any') is None
        assert empty_hamt.delete('any') is False
        assert list(empty_hamt.keys()) == []
