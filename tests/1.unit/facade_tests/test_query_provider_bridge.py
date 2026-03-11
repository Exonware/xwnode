#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/facade_tests/test_query_provider_bridge.py
Tests for XWNode.query() bridge via xwsystem.query registry.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 28-Dec-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwsystem.query import (
    QueryProviderNotRegisteredError,
    get_query_provider_registry,
    reset_query_provider_registry,
)
from exonware.xwsystem.query.contracts import IQueryProvider


class DummyQueryProvider(IQueryProvider):
    provider_id = "dummy"

    def execute(self, query: str, data, *, format: str | None = None, auto_detect: bool = True, **opts):
        # For this test, validate we get the node instance and return stable shape.
        return {"query": query, "format": format, "node_type": type(data).__name__}
@pytest.mark.xwnode_unit

class TestXWNodeQueryBridge:

    def teardown_method(self):
        reset_query_provider_registry()

    def test_query_raises_when_no_provider(self):
        node = XWNode.from_native({"users": []})
        with pytest.raises(QueryProviderNotRegisteredError):
            node.query("SELECT * FROM users")

    def test_query_delegates_to_registered_provider(self):
        registry = get_query_provider_registry()
        registry.register(DummyQueryProvider())
        node = XWNode.from_native({"users": [{"id": 1}]})
        result = node.query("SELECT * FROM users", format="sql")
        assert result["query"] == "SELECT * FROM users"
        assert result["format"] == "sql"
        assert result["node_type"] == "XWNode"
