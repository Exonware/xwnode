#!/usr/bin/env python3
"""
#exonware/xwnode/tests/0.core/runner.py
Core test runner for xwnode
Auto-discovers and runs core tests with colored output and Markdown logging.
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

from exonware.xwsystem.console.cli import ensure_utf8_console

ensure_utf8_console()

from exonware.xwsystem.utils.test_runner import TestRunner


def main() -> int:
    """Run core tests."""
    os.chdir(_PKG_ROOT)
    runner = TestRunner(
        library_name="xwnode",
        layer_name="0.core",
        description="Core Tests - Fast, High-Value Checks (20% tests for 80% value)",
        test_dir=Path(__file__).parent,
        pytest_cwd=_PKG_ROOT,
        markers=["xwnode_core"],
    )
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
