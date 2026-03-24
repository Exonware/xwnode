"""
#exonware/xwnode/tests/3.advance/test_usability.py
Usability Excellence Tests - Priority #2
Validates API intuitiveness, documentation, and user experience.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from pathlib import Path
from exonware.xwnode import XWNode


@pytest.mark.xwnode_advance
@pytest.mark.xwnode_usability

class TestUsabilityExcellence:
    """Usability excellence validation - Priority #2."""

    def test_api_intuitiveness(self):
        """Validate intuitive API design."""
        node = XWNode.from_native({"users": [{"name": "Alice"}]})
        assert node.get_value("users.0.name") == "Alice"
        assert node["users"][0]["name"] == "Alice"

    def test_error_messages(self):
        """Validate clear, helpful error messages."""
        with pytest.raises(Exception) as exc_info:
            XWNode.from_native({}, mode="INVALID_MODE")
        assert "INVALID_MODE" in str(exc_info.value)

    def test_documentation_completeness(self):
        """Validate comprehensive documentation."""
        readme = Path(__file__).resolve().parents[2] / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert "XWNode" in content
        assert "Install" in content

    def test_examples_quality(self):
        """Validate clear, practical examples."""
        init_file = Path(__file__).resolve().parents[2] / "src" / "exonware" / "xwnode" / "__init__.py"
        content = init_file.read_text(encoding="utf-8")
        assert "Example:" in content
        assert "from exonware.xwnode import XWNode" in content

    def test_naming_consistency(self):
        """Validate consistent naming conventions."""
        from exonware.xwnode import __all__
        assert "XWNode" in __all__
        assert "XWEdge" in __all__
        assert "XWFactory" in __all__

    def test_api_discoverability(self):
        """Validate easy-to-discover API functionality."""
        public = dir(XWNode)
        assert "from_native" in public
        assert "to_native" in public
        assert "query" in public
