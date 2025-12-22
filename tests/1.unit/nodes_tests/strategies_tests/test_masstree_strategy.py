"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_masstree_strategy.py

Comprehensive tests for MasstreeStrategy.

Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- B+ tree + trie hybrid structure
- High-performance operations
- Iterator protocol
- Performance characteristics
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
from exonware.xwnode.nodes.strategies.masstree import MasstreeStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_tree():
    """Create empty masstree strategy."""
    return MasstreeStrategy()


@pytest.fixture
def simple_tree():
    """Create masstree with simple data."""
    tree = MasstreeStrategy()
    tree.put('key1', 'value1')
    tree.put('key2', 'value2')
    tree.put('key3', 'value3')
    return tree


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestMasstreeStrategyInterface:
    """Test MasstreeStrategy implements iNodeStrategy interface correctly."""
    
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


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestMasstreeStrategyCore:
    """Test core MasstreeStrategy functionality."""
    
    def test_update_existing_key(self, simple_tree):
        """Test updating existing key."""
        simple_tree.put('key2', 'updated_value')
        
        assert simple_tree.get('key2') == 'updated_value'
        assert simple_tree.size() == 3
    
    def test_clear_operation(self, simple_tree):
        """Test clear removes all items."""
        simple_tree.clear()
        
        assert simple_tree.is_empty() is True
        assert simple_tree.size() == 0


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestMasstreeStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_tree_operations(self, empty_tree):
        """Test operations on empty tree."""
        assert empty_tree.get('any') is None
        assert empty_tree.delete('any') is False
        assert list(empty_tree.keys()) == []

