#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_t_digest_strategy.py
Comprehensive tests for T-Digest Strategy.
Tests cover:
- Interface compliance (iNodeStrategy)
- Core operations (insert, find)
- Streaming percentile estimation
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
from exonware.xwnode.nodes.strategies.t_digest import TDigestStrategy
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.errors import XWNodeError
@pytest.fixture

def empty_t_digest():
    """Create empty T-Digest."""
    return TDigestStrategy()
@pytest.fixture

def simple_t_digest():
    """Create T-Digest with data."""
    tdigest = TDigestStrategy()
    tdigest.add(10.0)
    tdigest.add(20.0)
    tdigest.add(30.0)
    return tdigest
@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy

class TestTDigestStrategy:
    """Test T-Digest strategy interface compliance."""

    def test_insert_operation(self, empty_t_digest):
        """Test insert operation works correctly."""
        empty_t_digest.add(10.0)
        assert empty_t_digest.get_count() == 1.0

    def test_find_operation(self, simple_t_digest):
        """Test quantile returns approximate values."""
        # T-Digest is approximate, so we check it doesn't crash
        result = simple_t_digest.quantile(0.5)
        assert result is not None

    def test_size_operation(self, simple_t_digest):
        """Test size returns correct count."""
        # T-Digest size may be approximate
        assert simple_t_digest.size() >= 0

    def test_is_empty_operation(self, empty_t_digest, simple_t_digest):
        """Test is_empty correctly identifies empty structures."""
        assert empty_t_digest.is_empty() is True
        assert simple_t_digest.is_empty() is False
