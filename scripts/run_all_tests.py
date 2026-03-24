#!/usr/bin/env python3
"""
#exonware/xwnode/scripts/run_all_tests.py
Run all tests and generate coverage report for xwnode.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import subprocess
import sys
from pathlib import Path


def run_tests_with_coverage():
    """Run all tests with coverage analysis."""
    root_dir = Path(__file__).parent.parent
    print("=" * 60)
    print("XWNode Test Suite Execution with Coverage")
    print("=" * 60)
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=exonware.xwnode",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure (remove for full run)
    ]
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=root_dir)
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("All tests passed!")
        print("Coverage report generated:")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
    else:
        print("Some tests failed. Check output above.")
        print("Coverage report still generated:")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
    print("=" * 60)
    return result.returncode


def run_security_tests():
    """Run security tests."""
    root_dir = Path(__file__).parent.parent
    print("\n" + "=" * 60)
    print("Running Security Tests")
    print("=" * 60)
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/3.advance/test_security.py",
        "-v",
        "--tb=short"
    ]
    result = subprocess.run(cmd, cwd=root_dir)
    return result.returncode


def run_performance_tests():
    """Run performance benchmarks."""
    root_dir = Path(__file__).parent.parent
    print("\n" + "=" * 60)
    print("Running Performance Benchmarks")
    print("=" * 60)
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/3.advance/test_performance.py",
        "benchmarks/20260321-benchmark xwnode consolidated/scripts/test_strategy_performance.py",
        "-v",
        "--tb=short",
        "-m", "xwnode_performance"
    ]
    result = subprocess.run(cmd, cwd=root_dir)
    return result.returncode


def main():
    """Run all test suites."""
    print("XWNode Comprehensive Test Execution")
    print("=" * 60)
    # Run coverage analysis
    coverage_result = run_tests_with_coverage()
    # Run security tests
    security_result = run_security_tests()
    # Run performance tests
    performance_result = run_performance_tests()
    # Summary
    print("\n" + "=" * 60)
    print("Test Execution Summary")
    print("=" * 60)
    print(f"Coverage Tests: {'PASSED' if coverage_result == 0 else 'FAILED'}")
    print(f"Security Tests: {'PASSED' if security_result == 0 else 'FAILED'}")
    print(f"Performance Tests: {'PASSED' if performance_result == 0 else 'FAILED'}")
    print("=" * 60)
    if coverage_result == 0 and security_result == 0 and performance_result == 0:
        print("\nAll test suites passed!")
        return 0
    else:
        print("\nSome test suites failed. Review output above.")
        return 1
if __name__ == "__main__":
    sys.exit(main())
