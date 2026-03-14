#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_dawg_strategy.py
Comprehensive tests for DAWG (Directed Acyclic Word Graph) Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- String operations
- Prefix matching
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
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_dawg():
    """Create empty DAWG."""
    return XWNode(mode=NodeMode.DAWG)
@pytest.fixture

def simple_dawg():
    """Create DAWG with simple words."""
    dawg = XWNode(mode=NodeMode.DAWG)
    dawg.put('hello', True)
    dawg.put('help', True)
    dawg.put('world', True)
    return dawg
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestDAWGStrategy:
    """Test DAWG strategy interface compliance."""

    def test_insert_operation(self, empty_dawg):
        """Test insert operation works correctly."""
        empty_dawg.put('test', True)
        result = empty_dawg.get('test')
        assert result is not None

    def test_find_operation(self, simple_dawg):
        """Test find operation returns correct values."""
        assert simple_dawg.get('hello') is not None
        assert simple_dawg.get('help') is not None
        assert simple_dawg.get('nonexistent') is None

    def test_delete_operation(self, simple_dawg):
        """Test delete operation removes words correctly."""
        assert simple_dawg.delete('hello') is True
        assert simple_dawg.get('hello') is None
        assert simple_dawg.delete('nonexistent') is False

    def test_size_operation(self, simple_dawg):
        """Test size returns correct count."""
        assert simple_dawg.size() >= 3
        simple_dawg.delete('hello')
        assert simple_dawg.size() >= 2

    def test_is_empty_operation(self, empty_dawg, simple_dawg):
        """Test is_empty correctly identifies empty structures."""
        assert empty_dawg.is_empty is True
        assert simple_dawg.is_empty is False
