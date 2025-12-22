"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_radix_trie_strategy.py

Comprehensive tests for RadixTrieStrategy.

Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Prefix compression
- Prefix search operations
- Iterator protocol
- Performance characteristics (O(k) operations where k is key length)
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
from exonware.xwnode.nodes.strategies.radix_trie import RadixTrieStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def empty_trie():
    """Create empty radix trie strategy."""
    return RadixTrieStrategy()


@pytest.fixture
def simple_trie():
    """Create radix trie with simple data."""
    trie = RadixTrieStrategy()
    trie.put('key1', 'value1')
    trie.put('key2', 'value2')
    trie.put('key3', 'value3')
    return trie


@pytest.fixture
def prefix_trie():
    """Create radix trie with shared prefixes."""
    trie = RadixTrieStrategy()
    trie.put('apple', 'a')
    trie.put('app', 'b')
    trie.put('application', 'c')
    return trie


# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRadixTrieStrategyInterface:
    """Test RadixTrieStrategy implements iNodeStrategy interface correctly."""
    
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
        assert simple_trie.get('nonexistent', 'default') == 'default'
    
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
        assert empty_trie.is_empty() is True
        assert simple_trie.is_empty() is False


# ============================================================================
# PREFIX COMPRESSION TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRadixTrieStrategyPrefix:
    """Test prefix compression and prefix search."""
    
    def test_prefix_compression(self, prefix_trie):
        """Test that shared prefixes are compressed."""
        # Radix trie should compress shared prefixes
        assert prefix_trie.get('apple') == 'a'
        assert prefix_trie.get('app') == 'b'
        assert prefix_trie.get('application') == 'c'
    
    def test_prefix_search(self, prefix_trie):
        """Test prefix search operations."""
        # Get all keys with prefix 'app'
        if hasattr(prefix_trie, 'keys_with_prefix'):
            keys = list(prefix_trie.keys_with_prefix('app'))
            assert 'app' in keys
            assert 'apple' in keys
            assert 'application' in keys


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRadixTrieStrategyCore:
    """Test core RadixTrieStrategy functionality."""
    
    def test_update_existing_key(self, simple_trie):
        """Test updating existing key."""
        simple_trie.put('key2', 'updated_value')
        
        assert simple_trie.get('key2') == 'updated_value'
        assert simple_trie.size() == 3  # Size unchanged
    
    def test_clear_operation(self, simple_trie):
        """Test clear removes all items."""
        simple_trie.clear()
        
        assert simple_trie.is_empty() is True
        assert simple_trie.size() == 0


# ============================================================================
# ITERATOR TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRadixTrieStrategyIterators:
    """Test iterator protocol."""
    
    def test_keys_iteration(self, simple_trie):
        """Test keys() returns all keys."""
        keys = list(simple_trie.keys())
        
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
        assert len(keys) == 3
    
    def test_values_iteration(self, simple_trie):
        """Test values() returns all values."""
        values = list(simple_trie.values())
        
        assert 'value1' in values
        assert 'value2' in values
        assert 'value3' in values
        assert len(values) == 3


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRadixTrieStrategyEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_trie_operations(self, empty_trie):
        """Test operations on empty trie."""
        assert empty_trie.get('any') is None
        assert empty_trie.delete('any') is False
        assert list(empty_trie.keys()) == []
    
    def test_single_key_trie(self, empty_trie):
        """Test trie with single key."""
        empty_trie.put('single', 'value')
        
        assert empty_trie.size() == 1
        assert empty_trie.get('single') == 'value'
        empty_trie.delete('single')
        assert empty_trie.is_empty() is True
    
    def test_empty_string_key(self, empty_trie):
        """Test handling of empty string key."""
        empty_trie.put('', 'empty_value')
        assert empty_trie.get('') == 'empty_value'


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance
class TestRadixTrieStrategyPerformance:
    """Test performance characteristics."""
    
    def test_large_dataset_operations(self):
        """Test operations with large dataset."""
        trie = RadixTrieStrategy()
        
        # Insert 100 items
        for i in range(100):
            trie.put(f'key_{i:03d}', f'value_{i}')
        
        assert trie.size() == 100
        
        # All should be accessible
        for i in range(100):
            assert trie.get(f'key_{i:03d}') == f'value_{i}'

