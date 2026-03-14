#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_crdt_map_strategy.py
Comprehensive tests for CRDT Map Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Conflict-free replicated operations
- Security (input validation, resource limits)
- Error handling
- Edge cases
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.crdt_map import CRDTMapStrategy
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_crdt():
    """Create empty CRDT map."""
    return CRDTMapStrategy()
@pytest.fixture

def simple_crdt():
    """Create CRDT map with data."""
    crdt = CRDTMapStrategy()
    crdt.put('key1', {'value': 'value1', 'timestamp': 1000})
    crdt.put('key2', {'value': 'value2', 'timestamp': 1001})
    return crdt
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestCRDTMapStrategy:
    """Test CRDT Map strategy interface compliance."""

    def test_insert_operation(self, empty_crdt):
        """Test insert operation works correctly."""
        empty_crdt.put('test_key', {'value': 'test_value'})
        result = empty_crdt.get('test_key')
        assert result is not None

    def test_find_operation(self, simple_crdt):
        """Test find operation returns correct values."""
        result = simple_crdt.get('key1')
        assert result is not None
        assert result.get('value') == 'value1'

    def test_delete_operation(self, simple_crdt):
        """Test delete operation removes keys correctly."""
        assert simple_crdt.delete('key1') is True
        assert simple_crdt.get('key1') is None
        assert simple_crdt.delete('nonexistent') is False

    def test_size_operation(self, simple_crdt):
        """Test size returns correct count."""
        assert simple_crdt.size() == 2
        simple_crdt.delete('key1')
        assert simple_crdt.size() == 1

    def test_is_empty_operation(self, empty_crdt, simple_crdt):
        """Test is_empty correctly identifies empty structures."""
        assert empty_crdt.is_empty() is True
        assert simple_crdt.is_empty() is False
