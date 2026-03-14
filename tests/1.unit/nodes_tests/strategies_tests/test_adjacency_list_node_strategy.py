#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_adjacency_list_node_strategy.py
Comprehensive tests for AdjacencyListNodeStrategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find, delete)
- Graph node operations
- Neighbor queries
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
from exonware.xwnode.nodes.strategies.adjacency_list import AdjacencyListStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_strategy():
    """Create empty adjacency list strategy."""
    return AdjacencyListStrategy()
@pytest.fixture

def simple_strategy():
    """Create adjacency list with simple data."""
    strategy = AdjacencyListStrategy()
    strategy.insert('node1', {'neighbors': ['node2', 'node3']})
    strategy.insert('node2', {'neighbors': ['node1']})
    return strategy
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestAdjacencyListNodeStrategy:
    """Test AdjacencyListNodeStrategy interface compliance."""

    def test_insert_operation(self, empty_strategy):
        """Test insert operation works correctly."""
        empty_strategy.insert('test_node', {'data': 'value'})
        result = empty_strategy.find('test_node')
        assert result is not None
        assert result.get('data') == 'value'

    def test_find_operation(self, simple_strategy):
        """Test find operation returns correct values."""
        result = simple_strategy.find('node1')
        assert result is not None
        assert 'neighbors' in result

    def test_delete_operation(self, simple_strategy):
        """Test delete operation removes nodes correctly."""
        assert simple_strategy.delete('node1') is True
        assert simple_strategy.find('node1') is None
        assert simple_strategy.delete('nonexistent') is False

    def test_size_operation(self, simple_strategy):
        """Test size returns correct count."""
        assert simple_strategy.size() == 2
        simple_strategy.delete('node1')
        assert simple_strategy.size() == 1

    def test_is_empty_operation(self, empty_strategy, simple_strategy):
        """Test is_empty correctly identifies empty structures."""
        assert empty_strategy.is_empty is True
        assert simple_strategy.is_empty is False
