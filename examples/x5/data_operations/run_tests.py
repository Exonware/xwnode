#!/usr/bin/env python3
"""
#exonware/xwnode/examples/x5/data_operations/run_tests.py

Main test runner for data operations test suite.
Coordinates all test execution using pytest following GUIDE_TEST.md standards.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --core             # Run only core tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --create           # Run only CREATE tests
    python run_tests.py --read             # Run only READ tests
    python run_tests.py --update           # Run only UPDATE tests
    python run_tests.py --delete           # Run only DELETE tests

Output:
    - Terminal: Colored, formatted output with emojis
    - File: docs/tests/TEST_<timestamp>_SUMMARY.md (Markdown-friendly format)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding


class DualOutput:
    """Capture output for both terminal and Markdown file."""
    
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.terminal_lines = []
        self.markdown_lines = []
    
    def print(self, text: str, markdown_format: str = None):
        """Print to terminal and capture for Markdown."""
        # Terminal output
        print(text)
        self.terminal_lines.append(text)
        
        # Markdown output (use markdown_format if provided, else clean terminal output)
        if markdown_format:
            self.markdown_lines.append(markdown_format)
        else:
            # Clean emoji and special chars for Markdown
            cleaned = text.replace("="*80, "---")
            self.markdown_lines.append(cleaned)
    
    def save(self, metadata: dict = None):
        """Save Markdown output to file."""
        header = f"""# Test Execution Report

**Library:** xwnode
**Component:** examples/x5/data_operations
**Generated:** {datetime.now().strftime("%d-%b-%Y %H:%M:%S")}
**Runner:** Main Test Runner (pytest-based)

---
"""
        content = header + "\n".join(self.markdown_lines) + "\n"
        self.output_file.write_text(content, encoding='utf-8')


def run_pytest_tests(test_dir: Path, test_pattern: str = None, markers: list = None, output: DualOutput = None) -> int:
    """
    Run pytest tests with GUIDE_TEST.md compliant options.
    
    Following GUIDE_TEST.md:
    - Stop on first failure (-x, --maxfail=1)
    - Verbose output (-v)
    - Short tracebacks (--tb=short)
    - Strict markers (--strict-markers)
    - Never hide warnings or errors
    """
    # Build pytest command following GUIDE_TEST.md
    pytest_args = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "-v",                    # Verbose: show all test details
        "-s",                      # Don't capture output (fixes Windows file handling issue)
        "--tb=short",              # Short traceback: concise but informative
        "--strict-markers",        # Enforce marker discipline
        "-x",                      # Stop on FIRST failure (fast feedback)
        "--maxfail=1",             # Same as -x (explicit)
    ]
    
    # Add test pattern if specified
    if test_pattern:
        pytest_args.append(test_pattern)
    
    # Add markers if specified
    if markers:
        marker_expr = " or ".join(markers)
        pytest_args.extend(["-m", marker_expr])
    
    # FORBIDDEN flags (GUIDE_TEST.md) - NEVER use these:
    # --disable-warnings     # Hides real problems!
    # --maxfail=10           # Continues past failures!
    # --tb=no                # Hides debugging info!
    # -q / --quiet           # Hides important output!
    
    try:
        result = subprocess.run(
            pytest_args,
            cwd=test_dir,
            capture_output=False,  # Show output in real-time
            text=True
        )
        return result.returncode
    except Exception as e:
        if output:
            output.print(f"❌ Error running pytest: {e}", f"**Error:** {e}")
        return 1


def main():
    """Main test runner function following GUIDE_TEST.md."""
    # Setup
    test_dir = Path(__file__).parent
    reports_dir = test_dir.parent.parent.parent / "docs" / "tests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = reports_dir / f"TEST_{timestamp}_DATA_OPERATIONS.md"
    output = DualOutput(output_file)
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(test_dir.parent))
    sys.path.insert(0, str(test_dir))
    
    # Header
    header = "="*80
    output.print(header, "# Data Operations Test Execution Report")
    output.print("Data Operations Test Runner", 
                 f"**Component:** xwnode/examples/x5/data_operations")
    output.print("Main Test Runner - pytest-based execution following GUIDE_TEST.md", "")
    output.print(header, "---")
    
    # Parse arguments
    args = sys.argv[1:]
    
    # Determine which tests to run
    exit_code = 0
    
    if "--core" in args:
        # Run core tests (high-value, fast)
        output.print("\n🚀 Running: Core Tests (High-Value, Fast)", 
                    "\n## Running Core Tests")
        exit_code = run_pytest_tests(test_dir, markers=["xwnode_core"], output=output)
    
    elif "--unit" in args:
        # Run unit tests
        output.print("\n🚀 Running: Unit Tests", "\n## Running Unit Tests")
        exit_code = run_pytest_tests(test_dir, markers=["xwnode_unit"], output=output)
    
    elif "--integration" in args:
        # Run integration tests
        output.print("\n🚀 Running: Integration Tests", "\n## Running Integration Tests")
        exit_code = run_pytest_tests(test_dir, markers=["xwnode_integration"], output=output)
    
    elif "--create" in args:
        # Run CREATE tests
        output.print("\n🚀 Running: CREATE Operations Tests", "\n## Running CREATE Tests")
        exit_code = run_pytest_tests(test_dir, test_pattern="test_1_create_operations.py", output=output)
    
    elif "--read" in args:
        # Run READ tests
        output.print("\n🚀 Running: READ Operations Tests", "\n## Running READ Tests")
        exit_code = run_pytest_tests(test_dir, test_pattern="test_2_read_operations.py", output=output)
    
    elif "--update" in args:
        # Run UPDATE tests
        output.print("\n🚀 Running: UPDATE Operations Tests", "\n## Running UPDATE Tests")
        exit_code = run_pytest_tests(test_dir, test_pattern="test_3_update_operations.py", output=output)
    
    elif "--delete" in args:
        # Run DELETE tests
        output.print("\n🚀 Running: DELETE Operations Tests", "\n## Running DELETE Tests")
        exit_code = run_pytest_tests(test_dir, test_pattern="test_4_delete_operations.py", output=output)
    
    else:
        # Run ALL tests
        output.print("\n🚀 Running: ALL Tests", "\n## Running All Tests")
        output.print("Following GUIDE_TEST.md standards:", "")
        output.print("  - Stop on first failure (-x)", "")
        output.print("  - Verbose output (-v)", "")
        output.print("  - Short tracebacks (--tb=short)", "")
        output.print("  - Never hide warnings or errors", "")
        output.print("", "")
        
        exit_code = run_pytest_tests(test_dir, output=output)
    
    # Print summary
    summary_header = f"\n{'='*80}"
    output.print(summary_header, f"\n---\n\n## 📈 Test Execution Summary")
    output.print("📈 TEST EXECUTION SUMMARY", "")
    output.print(f"{'='*80}", "")
    
    # Final status
    if exit_code == 0:
        final_msg = "\n✅ ALL TESTS PASSED!"
        output.print(final_msg, f"\n### {final_msg}")
        output.print("", "")
        output.print("Following GUIDE_TEST.md:", "")
        output.print("  ✅ All tests passed", "")
        output.print("  ✅ No errors hidden", "")
        output.print("  ✅ Root causes fixed", "")
    else:
        final_msg = "\n❌ SOME TESTS FAILED!"
        output.print(final_msg, f"\n### {final_msg}")
        output.print("", "")
        output.print("Following GUIDE_TEST.md:", "")
        output.print("  ⚠️ Fix root causes, not symptoms", "")
        output.print("  ⚠️ Never rig tests to pass", "")
        output.print("  ⚠️ Never hide errors or warnings", "")
        output.print("  ⚠️ Fix the code, not the test", "")
    
    # Save output
    output.save()
    print(f"\n💾 Test results saved to: {output_file}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
