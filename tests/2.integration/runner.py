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
from pathlib import Path
from exonware.xwsystem.utils.test_runner import TestRunner
if __name__ == "__main__":
    runner = TestRunner(
        library_name="xwnode",
        layer_name="2.integration",
        description="Integration Tests - Cross-Module Scenarios",
        test_dir=Path(__file__).parent
    )
    sys.exit(runner.run())
