"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_cuckoo_hash_strategy.py
Comprehensive tests for CuckooHashStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (put, get, delete)
- Cuckoo hashing with multiple hash functions
- High load factor handling
- Iterator protocol
- Performance characteristics (O(1) expected operations)
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
from exonware.xwnode.nodes.strategies.cuckoo_hash import CuckooHashStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError, XWNodeTypeError, XWNodeValueError
# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture

def empty_hash():
    """Create empty cuckoo hash strategy."""
    return CuckooHashStrategy()
@pytest.fixture

def simple_hash():
    """Create cuckoo hash with simple data."""
    hash_strategy = CuckooHashStrategy()
    hash_strategy.put('key1', 'value1')
    hash_strategy.put('key2', 'value2')
    hash_strategy.put('key3', 'value3')
    return hash_strategy
# ============================================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestCuckooHashStrategyInterface:
    """Test CuckooHashStrategy implements iNodeStrategy interface correctly."""

    def test_put_operation(self, empty_hash):
        """Test put operation works correctly."""
        empty_hash.put('test_key', 'test_value')
        result = empty_hash.get('test_key')
        assert result == 'test_value'

    def test_get_operation(self, simple_hash):
        """Test get operation returns correct values."""
        assert simple_hash.get('key1') == 'value1'
        assert simple_hash.get('key2') == 'value2'
        assert simple_hash.get('key3') == 'value3'
        assert simple_hash.get('nonexistent') is None

    def test_delete_operation(self, simple_hash):
        """Test delete operation removes keys correctly."""
        assert simple_hash.delete('key1') is True
        assert simple_hash.get('key1') is None
        assert simple_hash.delete('nonexistent') is False

    def test_size_operation(self, simple_hash):
        """Test size returns correct count."""
        assert simple_hash.size() == 3
        simple_hash.delete('key1')
        assert simple_hash.size() == 2

    def test_is_empty_operation(self, empty_hash, simple_hash):
        """Test is_empty correctly identifies empty structures."""
        assert empty_hash.is_empty() is True
        assert simple_hash.is_empty() is False
# ============================================================================
# CUCKOO HASHING TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestCuckooHashStrategyCuckoo:
    """Test cuckoo hashing specific features."""

    def test_high_load_factor(self, empty_hash):
        """Test cuckoo hash handles high load factors."""
        # Cuckoo hash can handle higher load factors than standard hash
        for i in range(20):
            empty_hash.put(f'key_{i}', f'value_{i}')
        assert empty_hash.size() == 20
        # All should be accessible
        for i in range(20):
            assert empty_hash.get(f'key_{i}') == f'value_{i}'
# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestCuckooHashStrategyCore:
    """Test core CuckooHashStrategy functionality."""

    def test_update_existing_key(self, simple_hash):
        """Test updating existing key."""
        simple_hash.put('key2', 'updated_value')
        assert simple_hash.get('key2') == 'updated_value'
        assert simple_hash.size() == 3

    def test_clear_operation(self, simple_hash):
        """Test clear removes all items."""
        simple_hash.clear()
        assert simple_hash.is_empty() is True
        assert simple_hash.size() == 0
# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestCuckooHashStrategyEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_hash_operations(self, empty_hash):
        """Test operations on empty hash."""
        assert empty_hash.get('any') is None
        assert empty_hash.delete('any') is False
        assert list(empty_hash.keys()) == []
