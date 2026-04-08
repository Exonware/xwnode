#!/usr/bin/env python3
"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/runner.py
Test runner for edge strategies module
Auto-discovers and runs all 16 edge strategy tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import os
from pathlib import Path

def _package_root() -> Path:
    """Folder with pyproject.toml + src/ (any tests/**/runner.py depth)."""
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / "pyproject.toml").is_file() and (p / "src").is_dir():
            return p
        p = p.parent
    raise RuntimeError("Could not locate package root from " + str(Path(__file__)))


_PKG_ROOT = _package_root()

from exonware.xwsystem.utils.test_runner import TestRunner
if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwnode",
        layer_name="1.unit.edges.strategies",
        description="Unit Tests - Edge Strategies (16 strategies: ADJ_LIST, R_TREE, NEURAL_GRAPH, etc.)",
        test_dir=Path(__file__).parent,
        pytest_cwd=_PKG_ROOT,
        markers=["xwnode_unit", "xwnode_edge_strategy"]
    )
    sys.exit(runner.run())
