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
from pathlib import Path
from exonware.xwsystem.utils.test_runner import TestRunner
if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwnode",
        layer_name="0.core",
        description="Core Tests - Fast, High-Value Checks (20% tests for 80% value)",
        test_dir=Path(__file__).parent
    )
    sys.exit(runner.run())
