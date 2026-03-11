"""
#exonware/xwnode/tests/0.core/test_t_digest_strategy.py
Core tests for T_DIGEST strategy
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.28
Generation Date: 27-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode, NodeMode
@pytest.mark.xwnode_core
@pytest.mark.xwnode_node_strategy

class TestTDigestStrategyCore:
    """Core tests for T_DIGEST strategy - Fast, high-value checks"""

    def test_create_t_digest(self):
        """Test creating T-Digest"""
        tdigest = XWNode(mode=NodeMode.T_DIGEST, compression=100)
        assert tdigest is not None

    def test_add_values_and_query_median(self):
        """Test adding values and querying median"""
        tdigest = XWNode(mode=NodeMode.T_DIGEST, compression=100)
        strategy = tdigest._strategy
        # Add values 1 to 100
        for i in range(1, 101):
            strategy.add(float(i))
        # Median should be around 50
        median = strategy.quantile(0.5)
        assert 45 < median < 55  # Allow some tolerance

    def test_percentiles(self):
        """Test percentile queries"""
        tdigest = XWNode(mode=NodeMode.T_DIGEST, compression=100)
        strategy = tdigest._strategy
        # Add 1000 values
        for i in range(1000):
            strategy.add(float(i))
        # Test percentiles
        p95 = strategy.quantile(0.95)
        p99 = strategy.quantile(0.99)
        assert 940 < p95 < 960
        assert 985 < p99 < 995
