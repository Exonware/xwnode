"""
#exonware/xwnode/examples/x5/data_operations/run_tests_unified.py
Unified Test Runner
Runs all data operations tests using pytest following GUIDE_TEST.md standards.
Ensures all functionalities work and fixes root causes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import subprocess
from pathlib import Path
# Configure UTF-8 for Windows console (GUIDE_TEST.md requirement)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass


def main():
    """
    Run all tests using pytest following GUIDE_TEST.md standards.
    Following GUIDE_TEST.md:
    - Uses pytest for test execution
    - Stop on first failure (-x, --maxfail=1)
    - Verbose output (-v)
    - Short tracebacks (--tb=short)
    - Never hide warnings or errors
    - Fix root causes, not symptoms
    """
    test_dir = Path(__file__).parent
    print("="*80)
    print("UNIFIED TEST RUNNER - Data Operations Test Suite")
    print("Following GUIDE_TEST.md Standards")
    print("="*80)
    print()
    print("Running all tests with pytest...")
    print("Configuration:")
    print("  - Stop on first failure (-x)")
    print("  - Verbose output (-v)")
    print("  - Short tracebacks (--tb=short)")
    print("  - Strict markers (--strict-markers)")
    print()
    # Run pytest with GUIDE_TEST.md compliant options
    # CRITICAL: Following GUIDE_TEST.md - Never hide problems!
    pytest_args = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "-v",                    # Verbose: show all test details
        "--tb=short",            # Short traceback: concise but informative
        "--strict-markers",      # Enforce marker discipline
        "-x",                    # Stop on FIRST failure (fast feedback)
        "--maxfail=1",           # Same as -x (explicit)
        # FORBIDDEN: Never use these flags (GUIDE_TEST.md):
        # --disable-warnings     # Hides real problems!
        # --maxfail=10           # Continues past failures!
        # --tb=no                # Hides debugging info!
        # -q / --quiet           # Hides important output!
    ]
    try:
        result = subprocess.run(
            pytest_args,
            cwd=test_dir,
            check=False  # Don't raise, we'll handle exit code
        )
        print()
        print("="*80)
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
            print("="*80)
            return 0
        else:
            print("❌ SOME TESTS FAILED!")
            print("="*80)
            print()
            print("Following GUIDE_TEST.md:")
            print("  - Fix root causes, not symptoms")
            print("  - Never rig tests to pass")
            print("  - Never hide errors or warnings")
            print("  - Fix the code, not the test")
            return 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
if __name__ == "__main__":
    sys.exit(main())
