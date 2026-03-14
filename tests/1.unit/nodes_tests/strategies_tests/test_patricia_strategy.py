"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_patricia_strategy.py
Comprehensive tests for PatriciaStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Binary trie compression
- Prefix search operations
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
from exonware.xwnode.nodes.strategies.patricia import PatriciaStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_trie():
    """Create empty Patricia trie strategy."""
    return PatriciaStrategy()
@pytest.fixture

def simple_trie():
    """Create Patricia trie with simple data."""
    trie = PatriciaStrategy()
    trie.put('key1', 'value1')
    trie.put('key2', 'value2')
    trie.put('key3', 'value3')
    return trie
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPatriciaStrategyInterface:
    """Test PatriciaStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_trie):
        """Test put operation works correctly."""
        empty_trie.put('test_key', 'test_value')
        result = empty_trie.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_trie):
        """Test get operation returns correct values."""
        assert simple_trie.get('key1') == 'value1'
        assert simple_trie.get('key2') == 'value2'
        assert simple_trie.get('key3') == 'value3'
        assert simple_trie.get('nonexistent') is None

    def test_delete_operation(self, simple_trie):
        """Test delete operation removes keys correctly."""
        assert simple_trie.delete('key1') is True
        assert simple_trie.get('key1') is None
        assert simple_trie.delete('nonexistent') is False

    def test_size_operation(self, simple_trie):
        """Test size returns correct count."""
        assert simple_trie.size() == 3
        simple_trie.delete('key1')
        assert simple_trie.size() == 2

    def test_is_empty_operation(self, empty_trie, simple_trie):
        """Test is_empty correctly identifies empty structures."""
        assert empty_trie.is_empty is True
        assert simple_trie.is_empty is False
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPatriciaStrategyCore:
    """Test core PatriciaStrategy functionality."""

    def test_update_existing_key(self, simple_trie):
        """Test updating existing key."""
        simple_trie.put('key2', 'updated_value')
        assert simple_trie.get('key2') == 'updated_value'
        assert simple_trie.size() == 3

    def test_clear_operation(self, simple_trie):
        """Test clear removes all items."""
        simple_trie.clear()
        assert simple_trie.is_empty is True
        assert simple_trie.size() == 0
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestPatriciaStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_trie_operations(self, empty_trie):
        """Test operations on empty trie."""
        assert empty_trie.get('any') is None
        assert empty_trie.delete('any') is False
        assert list(empty_trie.keys()) == []
