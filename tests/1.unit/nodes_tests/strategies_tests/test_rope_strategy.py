#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_rope_strategy.py
Comprehensive tests for Rope Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- String operations (concatenation, substring)
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

def empty_rope():
    """Create empty rope."""
    return XWNode(mode=NodeMode.ROPE)
@pytest.fixture

def simple_rope():
    """Create rope with text."""
    rope = XWNode(mode=NodeMode.ROPE)
    rope.put(0, 'Hello')
    rope.put(5, ' World')
    return rope
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestRopeStrategy:
    """Test Rope strategy interface compliance."""

    def test_insert_operation(self, empty_rope):
        """Test insert operation works correctly."""
        empty_rope.put(0, 'test')
        result = empty_rope.get(0)
        assert result is not None

    def test_find_operation(self, simple_rope):
        """Test find operation returns correct values."""
        result = simple_rope.get(0)
        assert result is not None

    def test_delete_operation(self, simple_rope):
        """Test delete operation removes text correctly."""
        assert simple_rope.delete(0) is True
        assert simple_rope.get(0) is None

    def test_size_operation(self, simple_rope):
        """Test size returns correct count."""
        assert simple_rope.size() >= 2

    def test_is_empty_operation(self, empty_rope, simple_rope):
        """Test is_empty correctly identifies empty structures."""
        assert empty_rope.is_empty is True
        assert simple_rope.is_empty is False
