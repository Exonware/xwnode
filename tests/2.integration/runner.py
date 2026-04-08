#!/usr/bin/env python3
"""
#exonware/xwnode/tests/2.integration/runner.py
Integration test runner for xwnode
Auto-discovers and runs integration tests with colored output and Markdown logging.
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
        layer_name="2.integration",
        description="Integration Tests - Cross-Module Scenarios",
        test_dir=Path(__file__).parent,
        pytest_cwd=_PKG_ROOT,
    )
    sys.exit(runner.run())
