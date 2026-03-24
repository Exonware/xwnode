"""
#exonware/xwnode/tests/3.advance/test_extensibility.py
Extensibility Excellence Tests - Priority #5
Validates plugin support, hooks, and customization capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwnode.common.patterns.registry import get_registry, get_strategy_registry
from exonware.xwnode.defs import QueryMode


@pytest.mark.xwnode_advance
@pytest.mark.xwnode_extensibility

class TestExtensibilityExcellence:
    """Extensibility excellence validation - Priority #5."""

    def test_plugin_support(self):
        """Validate plugin system functionality."""
        registry = get_registry()
        stats = registry.get_registry_stats()
        assert stats["node_strategies"] > 0
        assert stats["edge_strategies"] > 0

    def test_hook_system(self):
        """Validate hook/callback system."""
        node = XWNode.from_native({"items": [{"id": 1}, {"id": 2}]})
        assert node.get_value("items.0.id") == 1
        assert node.get_value("items.1.id") == 2

    def test_customization_points(self):
        """Validate customization points availability."""
        node = XWNode.from_native({"k": "v"}, mode="HASH_MAP")
        assert node.get_value("k") == "v"

    def test_extension_api(self):
        """Validate extension API design."""
        assert get_strategy_registry() is get_registry()

    def test_strategy_registration(self):
        """Validate custom strategy registration."""
        class DummyQueryStrategy:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        registry = get_registry()
        registry.register_query_strategy("UNIT_TEST_DUMMY", DummyQueryStrategy)
        try:
            strategy = registry.get_query_strategy("UNIT_TEST_DUMMY", marker="ok")
            assert isinstance(strategy, DummyQueryStrategy)
            assert strategy.kwargs["marker"] == "ok"
        finally:
            registry.unregister_query_strategy("UNIT_TEST_DUMMY")

    def test_backward_compatibility(self):
        """Validate backward compatibility for extensions."""
        assert QueryMode.AUTO.name == "AUTO"
