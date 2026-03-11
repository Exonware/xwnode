#!/usr/bin/env python3
"""
#exonware/xwnode/scripts/run_performance_benchmarks.py
Run performance benchmarks for xwnode and validate claims.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run performance benchmarks."""
    root_dir = Path(__file__).parent.parent
    print("=" * 60)
    print("XWNode Performance Benchmark Execution")
    print("=" * 60)
    # Run performance tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/3.advance/test_performance.py",
        "tests/utilities/benchmarks/test_strategy_performance.py",
        "-v",
        "--tb=short",
        "-m", "xwnode_performance",
        "--benchmark-only"  # If using pytest-benchmark
    ]
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=root_dir)
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("Performance benchmarks completed successfully!")
        print("Review output above for performance metrics.")
    else:
        print("Some performance benchmarks failed or had issues.")
        print("Review output above for details.")
    print("=" * 60)
    return result.returncode
if __name__ == "__main__":
    sys.exit(main())
