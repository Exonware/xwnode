"""
Comprehensive Benchmarking Script for V1 vs V2 Performance Comparison
This script runs all tests from the test suite with multiple iteration counts
and generates markdown tables organized by the structure in RECOMMENDATIONS.md
"""

import sys
import os
import time
import importlib
import importlib.util
import inspect
import asyncio
import traceback
import shutil
import threading
from pathlib import Path
from typing import Optional, Any
from collections import defaultdict
import json
import argparse
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        import ctypes
        # Set Windows console code page to UTF-8 (65001)
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8 code page
            kernel32.SetConsoleCP(65001)  # UTF-8 code page for input too
        except Exception:
            # Fallback: try chcp command
            try:
                import subprocess
                subprocess.run(['chcp', '65001'], shell=True, capture_output=True, check=False)
            except Exception:
                pass
        # Configure stdout/stderr streams
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding
# Default test iteration counts - can be overridden via CLI for modular benchmarking
# Following GUIDE_TEST.md: Provide fast feedback options without hiding tests.
DEFAULT_ITERATION_COUNTS = [1, 10, 50, 100, 200, 500, 1000]
DEFAULT_BULK_OPERATIONS_ITERATIONS = [1]
# These globals are used by helper functions; they will be set in main()
ITERATION_COUNTS = DEFAULT_ITERATION_COUNTS
BULK_OPERATIONS_ITERATIONS = DEFAULT_BULK_OPERATIONS_ITERATIONS
MAX_V1_TIME_SECONDS = 20.0
# Dataset configuration
DATASET_FILE = None
SHARED_TEST_FILE_V1 = None  # Single shared file for V1 for entire benchmark
SHARED_TEST_FILE_V2 = None  # Single shared file for V2 for entire benchmark
# Thread lock for file restoration (prevents race conditions in parallel tests)
FILE_RESTORE_LOCK = threading.Lock()
# Progress file to save/load results
PROGRESS_FILE = Path(__file__).parent / 'benchmark_progress.json'
# Test files to process
TEST_FILES = [
    'test_1_create_operations',
    'test_2_read_operations',
    'test_3_update_operations',
    'test_4_delete_operations',
    'test_5_list_query_operations',
    'test_6_search_operations',
    'test_7_bulk_operations',
    'test_8_transaction_operations',
    'test_9_index_operations',
    'test_10_validation_operations',
    'test_11_aggregation_operations',
    'test_12_file_operations',
    'test_13_concurrency_operations',
    'test_14_async_operations',
    'test_15_utility_operations',
    'test_16_monitoring_operations',
]
# Map test numbers to category names from RECOMMENDATIONS.md
CATEGORY_NAMES = {
    1: "CREATE Operations",
    2: "READ Operations",
    3: "UPDATE Operations",
    4: "DELETE Operations",
    5: "LIST/QUERY Operations",
    6: "SEARCH Operations",
    7: "BULK Operations",
    8: "TRANSACTION Operations",
    9: "INDEX Operations",
    10: "VALIDATION Operations",
    11: "AGGREGATION Operations",
    12: "FILE Operations",
    13: "CONCURRENCY Operations",
    14: "ASYNC Operations",
    15: "UTILITY Operations",
    16: "MONITORING Operations",
}
SUBCATEGORY_NAMES = {
    1: {
        1: "Single Record Creation",
        2: "Bulk Creation",
        3: "Conditional Creation",
        4: "Edge Cases",
    },
    2: {
        1: "Single Record Retrieval",
        2: "Multiple Record Retrieval",
        3: "Query Operations",
        4: "Search Operations",
        5: "Sorting Operations",
        6: "Aggregation Operations",
        7: "Streaming Operations",
        8: "Edge Cases and Error Handling",
    },
    3: {
        1: "Single Property Updates",
        2: "Multiple Property Updates",
        3: "Conditional Updates",
        4: "Incremental Updates",
        5: "Transformative Updates",
        6: "Edge Cases",
    },
    4: {
        1: "Single Record Deletion",
        2: "Multiple Record Deletion",
        3: "Conditional Deletion",
        4: "Partial Deletion",
        5: "Edge Cases",
    },
    5: {
        1: "Basic Listing",
        2: "Filtered Listing",
        3: "Sorted Listing",
        4: "Projected Listing",
        5: "Edge Cases",
    },
    6: {
        1: "Exact Match Search",
        2: "Pattern Matching Search",
        3: "Range Search",
        4: "Comparison Search",
        5: "Array/Collection Search",
        6: "Nested Search",
        7: "Full-Text Search",
        8: "Edge Cases",
    },
    7: {
        1: "Bulk Read",
        2: "Bulk Write",
        3: "Bulk Operations with Conditions",
        4: "Edge Cases",
    },
    8: {
        1: "Transaction Types",
        2: "Transactional Operations",
    },
    9: {
        1: "Index Creation",
        2: "Index Maintenance",
        3: "Index Usage",
    },
    10: {
        1: "Schema Validation",
        2: "Data Validation",
    },
    11: {
        1: "Counting",
        2: "Mathematical Aggregations",
        3: "Grouping",
    },
    12: {
        1: "File Management",
        2: "File Information",
    },
    13: {
        1: "Locking",
        2: "Concurrent Access",
    },
    14: {
        1: "Async Read",
        2: "Async Write",
    },
    15: {
        1: "Data Transformation",
        2: "Data Export/Import",
        3: "Data Migration",
    },
    16: {
        1: "Performance Monitoring",
        2: "Health Monitoring",
    },
}


def parse_test_name(test_name: str) -> Optional[tuple[int, int, int, str]]:
    """
    Parse test name like 'test_1_1_1_append_single_record' 
    Returns (category, subcategory, test_num, test_title) or None
    """
    if not test_name.startswith('test_'):
        return None
    parts = test_name.split('_')
    if len(parts) < 4:
        return None
    try:
        category = int(parts[1])
        subcategory = int(parts[2])
        test_num = int(parts[3])
        title = '_'.join(parts[4:]) if len(parts) > 4 else 'unknown'
        return (category, subcategory, test_num, title)
    except (ValueError, IndexError):
        return None


def get_test_title(test_func) -> str:
    """Extract test title from docstring or function name."""
    if test_func.__doc__:
        doc_lines = test_func.__doc__.strip().split('\n')
        for line in doc_lines:
            if 'Test:' in line:
                return line.split('Test:')[1].strip()
    # Fallback to function name
    name = test_func.__name__
    if name.startswith('test_'):
        parts = name.split('_')
        if len(parts) >= 4:
            return ' '.join(parts[4:]).replace('_', ' ').title()
    return name


def discover_tests(test_file_path: Path) -> dict[tuple[int, int, int], tuple[str, callable]]:
    """Discover all test functions from a test file."""
    tests = {}
    # Import the test module
    module_name = test_file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, test_file_path)
    if spec is None or spec.loader is None:
        return tests
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Warning: Could not load {test_file_path}: {e}")
        return tests
    # Find all test functions
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if name.startswith('test_'):
            parsed = parse_test_name(name)
            if parsed:
                category, subcategory, test_num, title = parsed
                test_title = get_test_title(obj)
                tests[(category, subcategory, test_num)] = (test_title, obj)
    return tests


def is_bulk_operation(test_title: str, test_name: str = "") -> bool:
    """Check if a test is a bulk operation based on title or name."""
    bulk_keywords = ['bulk', 'batch']
    check_text = (test_title + " " + test_name).lower()
    return any(keyword in check_text for keyword in bulk_keywords)


def get_iteration_counts_for_test(category: int, test_title: str = "", test_name: str = "") -> list[int]:
    """Get iteration counts based on category and test type. Bulk operations use only 1 iteration."""
    # Check if it's a bulk operation by name/title (regardless of category)
    if is_bulk_operation(test_title, test_name):
        return BULK_OPERATIONS_ITERATIONS
    # Category 7 is all bulk operations
    if category == 7:  # BULK Operations category
        return BULK_OPERATIONS_ITERATIONS
    return ITERATION_COUNTS


def run_test_with_iterations(test_func: callable, iterations: int, test_name: str = "") -> Optional[tuple[float, float]]:
    """
    Run a test function multiple times and return average (v1_time, v2_time).
    Returns None if test fails or V1 exceeds MAX_V1_TIME_SECONDS.
    When using large datasets: Uses ONE shared file for the entire benchmark run.
    Following GUIDE_TEST.md and GUIDE_DEV.md: Never hide errors, show full tracebacks for root cause analysis.
    """
    # If using large dataset, patch create_test_file() to return the shared file
    # Import test_helpers before entering executor to avoid context variable issues
    original_create_test_file = None
    patched_helpers = False
    if SHARED_TEST_FILE_V1 and SHARED_TEST_FILE_V2:
        # Import before executor to preserve context variables
        from data_operations import test_helpers
        # Store original function
        original_create_test_file = test_helpers.create_test_file
        # Track call count per thread to alternate between V1 and V2 files
        # Root cause fix: Tests call create_test_file() twice (V1 and V2), and they need separate files
        # Solution: Use thread-local counter to alternate between V1 and V2 files
        file_call_counter = threading.local()
        if not hasattr(file_call_counter, 'count'):
            file_call_counter.count = 0
        def create_shared_test_file(data: list[dict[str, Any]]) -> str:
            """
            Return the shared large dataset file for testing.
            All tests use the same file - it has as many records as possible (100MB+).
            NOTE: The 'data' parameter is ignored when using large datasets.
            Root cause fix: Tests call create_test_file() twice (once for V1, once for V2).
            We alternate between SHARED_TEST_FILE_V1 and SHARED_TEST_FILE_V2 to ensure
            V1 and V2 operations don't interfere with each other.
            Uses thread-safe locking to prevent race conditions in parallel execution.
            """
            # Increment call counter (thread-local)
            file_call_counter.count += 1
            is_v1_call = (file_call_counter.count % 2 == 1)
            # Determine which file to use and restore
            target_file = SHARED_TEST_FILE_V1 if is_v1_call else SHARED_TEST_FILE_V2
            # Restore the target file from the original dataset
            # This ensures each test starts with a clean file
            with FILE_RESTORE_LOCK:
                if DATASET_FILE and os.path.exists(DATASET_FILE):
                    if os.path.exists(target_file):
                        shutil.copy2(DATASET_FILE, target_file)
                    # Clean up index files for the target file
                    for idx_file in [target_file + '.idx.json', target_file + '.ids.json']:
                        if os.path.exists(idx_file):
                            os.remove(idx_file)
            # Return the appropriate file (V1 or V2)
            return target_file
        # Patch the function in the module
        test_helpers.create_test_file = create_shared_test_file
        patched_helpers = True
        # Also patch in sys.modules if the module is already loaded
        if 'data_operations.test_helpers' in sys.modules:
            sys.modules['data_operations.test_helpers'].create_test_file = create_shared_test_file
        if 'test_helpers' in sys.modules:
            sys.modules['test_helpers'].create_test_file = create_shared_test_file
        # CRITICAL: Also patch any modules that imported create_test_file directly
        # Tests import it at module level, so we need to patch it in those modules too
        for module_name in list(sys.modules.keys()):
            if 'test_' in module_name and hasattr(sys.modules[module_name], 'create_test_file'):
                sys.modules[module_name].create_test_file = create_shared_test_file
    try:
        v1_times = []
        v2_times = []
        # Store original file sizes for restoration
        original_size_v1 = None
        original_size_v2 = None
        if SHARED_TEST_FILE_V1 and os.path.exists(SHARED_TEST_FILE_V1):
            original_size_v1 = os.path.getsize(SHARED_TEST_FILE_V1)
        if SHARED_TEST_FILE_V2 and os.path.exists(SHARED_TEST_FILE_V2):
            original_size_v2 = os.path.getsize(SHARED_TEST_FILE_V2)
        for i in range(iterations):
            # Reset the call counter for this test iteration
            # This ensures each test starts with V1 file on first call, V2 file on second call
            if SHARED_TEST_FILE_V1 and SHARED_TEST_FILE_V2:
                # Access thread-local counter and reset it
                if hasattr(file_call_counter, 'count'):
                    file_call_counter.count = 0
            # Note: File restoration now happens inside create_shared_test_file()
            # which is called every time create_test_file() is invoked in the test.
            # This ensures both V1 and V2 operations start with a clean file.
            try:
                result = test_func()
                if result is None:
                    # Following GUIDE_TEST.md: Don't silently skip - log why
                    if i == 0:  # Only print on first iteration to avoid spam
                        print(f"\n    ⚠️  Test '{test_name}' returned None - check test implementation")
                    continue
                if isinstance(result, tuple) and len(result) >= 3:
                    success, v1_time, v2_time = result[0], result[1], result[2]
                    if success:
                        v1_times.append(v1_time)
                        v2_times.append(v2_time)
                        # Check if V1 is taking too long
                        if v1_time > MAX_V1_TIME_SECONDS:
                            print(f"\n    ⚠️  Stopping: V1 time ({v1_time:.2f}s) exceeds {MAX_V1_TIME_SECONDS}s")
                            return None
                    else:
                        # Test reported failure - need to see why
                        if i == 0:  # Only print on first iteration
                            print(f"\n    ⚠️  Test '{test_name}' reported failure (success=False)")
                else:
                    # Test doesn't return timing info in expected format
                    if i == 0:  # Only print on first iteration
                        print(f"\n    ⚠️  Test '{test_name}' returned unexpected format: {type(result)}")
                        print(f"       Expected: tuple(success, v1_time, v2_time), Got: {result}")
                    continue
            except Exception as e:
                # Following GUIDE_TEST.md: Show full traceback for root cause analysis
                error_msg = f"\n    ❌ Test '{test_name}' failed on iteration {i+1}:"
                error_msg += f"\n       Error Type: {type(e).__name__}"
                error_msg += f"\n       Error Message: {str(e)}"
                error_msg += f"\n       Full Traceback:"
                for line in traceback.format_exception(type(e), e, e.__traceback__):
                    error_msg += f"\n       {line.rstrip()}"
                print(error_msg)
                # Restore files even on error
                if SHARED_TEST_FILE_V1 and SHARED_TEST_FILE_V2 and DATASET_FILE and os.path.exists(DATASET_FILE):
                    shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V1)
                    shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V2)
                return None
        if not v1_times or not v2_times:
            # Following GUIDE_TEST.md: Don't hide failures - explain why
            if not v1_times and not v2_times:
                print(f"\n    ⚠️  Test '{test_name}': No successful iterations completed")
            elif not v1_times:
                print(f"\n    ⚠️  Test '{test_name}': No V1 times collected")
            elif not v2_times:
                print(f"\n    ⚠️  Test '{test_name}': No V2 times collected")
            return None
        avg_v1 = sum(v1_times) / len(v1_times)
        avg_v2 = sum(v2_times) / len(v2_times)
        return (avg_v1, avg_v2)
    finally:
        # Restore original create_test_file if we patched it
        if patched_helpers and original_create_test_file:
            from data_operations import test_helpers
            test_helpers.create_test_file = original_create_test_file
            if 'data_operations.test_helpers' in sys.modules:
                sys.modules['data_operations.test_helpers'].create_test_file = original_create_test_file
            if 'test_helpers' in sys.modules:
                sys.modules['test_helpers'].create_test_file = original_create_test_file


def generate_markdown_tables(results: Dict) -> str:
    """Generate markdown tables from benchmark results."""
    output = []
    output.append("# V1 vs V2 Performance Benchmark Results")
    output.append(f"*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*")
    output.append("")
    output.append("## Summary Table: Last Time V1 Beat V2")
    output.append("")
    # Summary table
    # Root cause fix: Ensure all keys are int for consistent sorting
    # Following GUIDE_TEST.md - Fix root causes, handle type consistency
    summary_rows = []
    for category in sorted(results.keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
        for subcategory in sorted(results[category].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
            for test_num in sorted(results[category][subcategory].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
                test_data = results[category][subcategory][test_num]
                test_title = test_data['title']
                last_v1_win = test_data.get('last_v1_win', None)
                if last_v1_win is not None:
                    summary_rows.append(
                        f"| {category}.{subcategory}.{test_num} {test_title} | {last_v1_win} |"
                    )
    if summary_rows:
        output.append("| TEST | Last Time V1 Beat V2 |")
        output.append("|------|---------------------|")
        output.extend(summary_rows)
        output.append("")
    # Detailed tables by category
    # Root cause fix: Ensure all keys are int for consistent sorting
    # Following GUIDE_TEST.md - Fix root causes, handle type consistency
    for category in sorted(results.keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
        cat_name = CATEGORY_NAMES.get(category, f"Category {category}")
        output.append("")
        output.append(f"## {category}. {cat_name}")
        output.append("")
        for subcategory in sorted(results[category].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
            subcat_name = SUBCATEGORY_NAMES.get(category, {}).get(subcategory, f"Subcategory {subcategory}")
            output.append(f"### {category}.{subcategory} {subcat_name}")
            output.append("")
            # Collect all unique iteration counts used in this subcategory
            # Root cause fix: Ensure iteration counts are unique and properly typed
            # Following GUIDE_TEST.md - Fix root causes, handle data consistency
            all_iterations = set()
            for test_num, test_data in results[category][subcategory].items():
                # Normalize iteration counts to int to avoid duplicates (int vs str)
                for iter_key in test_data.get('results', {}).keys():
                    # Convert to int for consistency, then back to original for display
                    normalized = int(iter_key) if isinstance(iter_key, (int, str)) else iter_key
                    all_iterations.add(normalized)
            # Sort iteration counts and convert back to consistent type
            iteration_counts = sorted(all_iterations) if all_iterations else ITERATION_COUNTS
            # Create table header
            # Root cause fix: Ensure header separator matches number of columns
            # Following GUIDE_TEST.md - Fix root causes, ensure table formatting is correct
            header = "| Test | Title |"
            separator = "|------|-------|"
            for iters in iteration_counts:
                header += f" V1 ({iters}) | V2 ({iters}) |"
                separator += "---------|---------|"
            output.append(header)
            output.append(separator)
            # Add rows for each test
            for test_num in sorted(results[category][subcategory].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
                test_data = results[category][subcategory][test_num]
                test_title = test_data['title']
                row = f"| {category}.{subcategory}.{test_num} | {test_title} |"
                # Root cause fix: Match iteration counts by converting keys to int for lookup
                # Following GUIDE_TEST.md - Fix root causes, handle type consistency
                test_results = test_data.get('results', {})
                for iters in iteration_counts:
                    # Try to find matching result - check both int and str versions
                    result = None
                    if iters in test_results:
                        result = test_results[iters]
                    else:
                        # Try string version
                        str_iters = str(iters)
                        if str_iters in test_results:
                            result = test_results[str_iters]
                        else:
                            # Try int version if iters is str
                            try:
                                int_iters = int(iters) if isinstance(iters, str) else iters
                                if int_iters in test_results:
                                    result = test_results[int_iters]
                            except (ValueError, TypeError):
                                pass
                    if result is not None:
                        v1_time, v2_time = result
                        row += f" {v1_time:.4f}s | {v2_time:.4f}s |"
                    else:
                        row += " N/A | N/A |"
                output.append(row)
            output.append("")
    return "\n".join(output)


def load_progress() -> Dict:
    """Load progress from file if it exists."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert back to nested defaultdict structure
                results = defaultdict(lambda: defaultdict(dict))
                for cat, subcats in data.items():
                    for subcat, tests in subcats.items():
                        for test_num, test_data in tests.items():
                            results[int(cat)][int(subcat)][int(test_num)] = test_data
                return results
        except Exception as e:
            print(f"Warning: Could not load progress: {e}")
    return defaultdict(lambda: defaultdict(dict))


def save_progress(results: Dict):
    """Save progress to file."""
    try:
        # Convert defaultdict to regular dict for JSON serialization
        data = {}
        for cat, subcats in results.items():
            data[str(cat)] = {}
            for subcat, tests in subcats.items():
                data[str(cat)][str(subcat)] = {}
                for test_num, test_data in tests.items():
                    data[str(cat)][str(subcat)][str(test_num)] = test_data
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save progress: {e}")
async def run_test_group_async(
    category: int,
    category_tests: list[tuple[tuple[int, int, int], tuple[str, callable]]],
    results: Dict,
    total_tests: int,
    test_counter: dict[str, int],
    counter_lock: asyncio.Lock,
    progress_lock: asyncio.Lock
) -> Dict:
    """
    Run all tests for a category asynchronously.
    Following GUIDE_TEST.md: Fix root causes, proper error handling.
    """
    category_results = defaultdict(dict)
    for (cat, subcat, test_num), (test_title, test_func) in sorted(category_tests):
        async with counter_lock:
            test_counter['current'] += 1
            current_test = test_counter['current']
        # Get iteration counts for this specific test (checks if it's a bulk operation by name/title)
        test_name = test_func.__name__ if hasattr(test_func, '__name__') else ""
        iteration_counts = get_iteration_counts_for_test(cat, test_title, test_name)
        # Skip if already completed
        if (cat in results and 
            subcat in results[cat] and 
            test_num in results[cat][subcat] and
            len(results[cat][subcat][test_num].get('results', {})) == len(iteration_counts)):
            print(f"[{current_test}/{total_tests}] ⏭️  Skipping {cat}.{subcat}.{test_num} - {test_title} (already completed)")
            continue
        print(f"[{current_test}/{total_tests}] Running {cat}.{subcat}.{test_num} - {test_title}")
        test_results = results[cat][subcat][test_num].get('results', {}) if (
            cat in results and 
            subcat in results[cat] and 
            test_num in results[cat][subcat]
        ) else {}
        last_v1_win = results[cat][subcat][test_num].get('last_v1_win', None) if (
            cat in results and 
            subcat in results[cat] and 
            test_num in results[cat][subcat]
        ) else None
        for iterations in iteration_counts:
            # Root cause fix: Normalize iteration count for consistent lookup
            # Following GUIDE_TEST.md - Fix root causes, ensure data consistency
            normalized_iterations = int(iterations) if isinstance(iterations, (int, str)) else iterations
            # Skip if already done - check both normalized and original forms
            if normalized_iterations in test_results or iterations in test_results:
                continue
            print(f"  🔄 Running with {iterations} iteration(s)...", end=" ", flush=True)
            # Run test in thread pool to avoid blocking
            # Root cause fix: Use asyncio.to_thread() (Python 3.9+) instead of run_in_executor()
            # to preserve context variables needed by lazyimports.
            try:
                if hasattr(asyncio, 'to_thread'):
                    result = await asyncio.to_thread(
                        run_test_with_iterations, 
                        test_func, 
                        iterations,
                        f"{cat}.{subcat}.{test_num} - {test_title}"  # Pass test name for better error messages
                    )
                else:
                    # Fallback for Python < 3.9: use run_in_executor (may have context variable issues)
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, 
                        run_test_with_iterations, 
                        test_func, 
                        iterations,
                        f"{cat}.{subcat}.{test_num} - {test_title}"  # Pass test name for better error messages
                    )
            except Exception as e:
                # Following GUIDE_TEST.md: Fix root causes, show full tracebacks - don't hide errors
                print(f"\n    ❌ Execution Error for {cat}.{subcat}.{test_num} - {test_title}:")
                print(f"       Error Type: {type(e).__name__}")
                print(f"       Error Message: {str(e)}")
                print(f"       Full Traceback:")
                for line in traceback.format_exception(type(e), e, e.__traceback__):
                    print(f"       {line.rstrip()}")
                print(f"\n    ⚠️  Root cause analysis needed - test execution failed")
                result = None
            if result is None:
                # Following GUIDE_TEST.md: Don't use generic failure messages - be specific
                print("❌ Failed or stopped (see error details above)")
                break
            v1_time, v2_time = result
            # Root cause fix: Normalize iteration count to int for consistent storage
            # Following GUIDE_TEST.md - Fix root causes, ensure data consistency
            normalized_iterations = int(iterations) if isinstance(iterations, (int, str)) else iterations
            test_results[normalized_iterations] = (v1_time, v2_time)
            # Track last time V1 was faster
            if v1_time < v2_time:
                last_v1_win = iterations
            winner = "V1" if v1_time < v2_time else "V2"
            # Root cause fix: Prevent division by zero when times are 0
            # Following GUIDE_TEST.md - Fix root causes, handle all edge cases properly
            if v1_time == 0 or v2_time == 0:
                # If either time is 0, use a fallback calculation
                if v1_time == 0 and v2_time == 0:
                    speedup = 1.0  # Both are 0, no speedup
                    speedup_str = f"{speedup:.2f}x faster"
                elif v1_time == 0:
                    speedup_str = "instant"  # V1 is instant
                else:
                    speedup_str = "instant"  # V2 is instant
            else:
                speedup = max(v1_time, v2_time) / min(v1_time, v2_time)
                speedup_str = f"{speedup:.2f}x faster"
            print(f"✓ {winner} wins ({speedup_str})")
            # Save progress after each iteration (thread-safe)
            category_results[subcat][test_num] = {
                'title': test_title,
                'results': test_results,
                'last_v1_win': last_v1_win
            }
            # Update main results
            results[cat][subcat][test_num] = category_results[subcat][test_num]
            async with progress_lock:
                save_progress(results)
        print()
    return category_results
async def run_all_test_groups_async(
    all_tests: dict[tuple[int, int, int], tuple[str, callable]],
    results: Dict,
    total_tests: int
) -> Dict:
    """
    Run all 16 test groups in parallel (async).
    Following GUIDE_TEST.md: Proper async execution with error handling.
    """
    # Group tests by category
    tests_by_category = defaultdict(list)
    for (category, subcategory, test_num), (test_title, test_func) in all_tests.items():
        tests_by_category[category].append(((category, subcategory, test_num), (test_title, test_func)))
    # Shared counter for test numbering (thread-safe)
    test_counter = {'current': 0}
    counter_lock = asyncio.Lock()
    progress_lock = asyncio.Lock()
    # For large datasets, run tests sequentially to avoid file conflicts
    # For default datasets, run in parallel for speed
    use_parallel = not (SHARED_TEST_FILE_V1 and SHARED_TEST_FILE_V2)
    if use_parallel:
        print("🚀 Running all 16 test groups in parallel (async)...\n")
    else:
        print("🚀 Running all 16 test groups sequentially (large dataset mode)...\n")
    category_results = {}
    categories = sorted(tests_by_category.keys())
    if use_parallel:
        # Create all tasks and run in parallel
        tasks = []
        for category in categories:
            category_tests = tests_by_category[category]
            task = run_test_group_async(
                category,
                category_tests,
                results,
                total_tests,
                test_counter,
                counter_lock,
                progress_lock
            )
            tasks.append((category, task))
        # Wait for all tasks to complete in parallel
        for category, task in tasks:
            try:
                cat_results = await task
                category_results[category] = cat_results
            except Exception as e:
                # Following GUIDE_TEST.md: Fix root causes, don't hide errors
                print(f"❌ Category {category} failed: {e}")
                print(f"  ⚠️  Root cause analysis needed - check test file for issues")
                # Continue with other categories
    else:
        # Run categories sequentially for large datasets (one at a time)
        for category in categories:
            category_tests = tests_by_category[category]
            try:
                cat_results = await run_test_group_async(
                    category,
                    category_tests,
                    results,
                    total_tests,
                    test_counter,
                    counter_lock,
                    progress_lock
                )
                category_results[category] = cat_results
            except Exception as e:
                # Following GUIDE_TEST.md: Fix root causes, don't hide errors
                print(f"❌ Category {category} failed: {e}")
                print(f"  ⚠️  Root cause analysis needed - check test file for issues")
                # Continue with other categories
            continue
    return results


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for modular benchmarking configuration.
    Following GUIDE_TEST.md: Provide flexible, explicit configuration instead of
    ad-hoc flags or hidden behaviour.
    """
    parser = argparse.ArgumentParser(
        description="Comprehensive V1 vs V2 benchmarking for xwnode examples/x5",
    )
    parser.add_argument(
        "--iterations",
        type=str,
        default=None,
        help=(
            "Comma-separated iteration counts for standard tests "
            "(default: 1,10,50,100,200,500,1000). "
            "Example: --iterations 1 to run a quick smoke benchmark."
        ),
    )
    parser.add_argument(
        "--bulk-iterations",
        type=str,
        default=None,
        help=(
            "Comma-separated iteration counts for bulk operations (category 7). "
            "Default: 1. Example: --bulk-iterations 1"
        ),
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["default", "100mb"],
        default="default",
        help=(
            "Dataset to use for benchmarking: "
            "default (small test files created per test), "
            "100mb (uses database_100mb.jsonl with numbered copies). "
            "Default: default"
        ),
    )
    # NOTE: Future extension point – we can add a --version-set flag to choose
    # between different implementation sets (e.g., V1/V2 vs V3/V4) without
    # changing the test suite contracts.
    return parser.parse_args(argv)


def configure_iteration_counts(args: argparse.Namespace) -> None:
    """
    Configure global iteration counts from CLI arguments.
    Root cause friendly: all configuration is explicit and easy to override
    when running quick or full benchmarks.
    """
    global ITERATION_COUNTS, BULK_OPERATIONS_ITERATIONS
    # Standard tests
    if args.iterations:
        try:
            ITERATION_COUNTS = [
                int(x.strip())
                for x in args.iterations.split(",")
                if x.strip()
            ]
        except ValueError as e:
            print(f"❌ Invalid --iterations value '{args.iterations}': {e}")
            print("   Expected comma-separated integers, e.g. --iterations 1 or --iterations 1,10,100")
            sys.exit(1)
    else:
        ITERATION_COUNTS = DEFAULT_ITERATION_COUNTS
    # Bulk operations (category 7)
    if args.bulk_iterations:
        try:
            BULK_OPERATIONS_ITERATIONS = [
                int(x.strip())
                for x in args.bulk_iterations.split(",")
                if x.strip()
            ]
        except ValueError as e:
            print(f"❌ Invalid --bulk-iterations value '{args.bulk_iterations}': {e}")
            print("   Expected comma-separated integers, e.g. --bulk-iterations 1")
            sys.exit(1)
    else:
        BULK_OPERATIONS_ITERATIONS = DEFAULT_BULK_OPERATIONS_ITERATIONS


def configure_dataset(dataset_option: str) -> None:
    """
    Configure dataset file based on option.
    Creates ONE shared file for the entire benchmark run.
    """
    global DATASET_FILE, SHARED_TEST_FILE_V1, SHARED_TEST_FILE_V2
    if dataset_option == "100mb":
        script_dir = Path(__file__).parent
        data_dir = script_dir / 'data'
        dataset_path = data_dir / 'database_100mb.jsonl'
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {dataset_path}\n"
                f"  Expected at: {dataset_path.absolute()}\n"
                f"  Solution: Ensure database_100mb.jsonl exists in {data_dir}"
            )
        DATASET_FILE = str(dataset_path)
        # Create ONE shared file for V1 and ONE for V2 for the entire benchmark
        base_name = dataset_path.stem  # database_100mb
        SHARED_TEST_FILE_V1 = str(data_dir / f"{base_name}_tested_v1.jsonl")
        SHARED_TEST_FILE_V2 = str(data_dir / f"{base_name}_tested_v2.jsonl")
        # Copy the large file once at the start
        source_size = os.path.getsize(DATASET_FILE)
        source_size_mb = source_size / (1024 * 1024)
        print(f"  📋 Creating shared test files ({source_size_mb:.1f} MB each)...", end=" ", flush=True)
        shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V1)
        shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V2)
        # Verify copies
        if not os.path.exists(SHARED_TEST_FILE_V1) or os.path.getsize(SHARED_TEST_FILE_V1) != source_size:
            raise RuntimeError(f"Failed to create shared test file: {SHARED_TEST_FILE_V1}")
        if not os.path.exists(SHARED_TEST_FILE_V2) or os.path.getsize(SHARED_TEST_FILE_V2) != source_size:
            raise RuntimeError(f"Failed to create shared test file: {SHARED_TEST_FILE_V2}")
        print("✅", flush=True)
    else:
        DATASET_FILE = None
        SHARED_TEST_FILE_V1 = None
        SHARED_TEST_FILE_V2 = None


def main(argv: Optional[list[str]] = None):
    """Main benchmarking function."""
    # Parse CLI arguments and configure iteration strategy
    args = parse_args(argv)
    configure_iteration_counts(args)
    # Configure dataset
    try:
        configure_dataset(args.dataset)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    # Get test directory
    script_dir = Path(__file__).parent
    test_dir = script_dir / 'data_operations'
    if not test_dir.exists():
        print(f"❌ Error: Test directory not found: {test_dir}")
        print(f"  ⚠️  Root cause: Test directory path is incorrect")
        return 1
    print("=" * 80)
    print("V1 vs V2 Comprehensive Benchmarking")
    print("=" * 80)
    print()
    print("Dataset configuration:")
    if DATASET_FILE and SHARED_TEST_FILE_V1:
        file_size_mb = os.path.getsize(DATASET_FILE) / (1024 * 1024)  # MB
        file_size_gb = file_size_mb / 1024  # GB
        if file_size_gb >= 1.0:
            size_str = f"{file_size_gb:.2f} GB"
        else:
            size_str = f"{file_size_mb:.2f} MB"
        print(f"  ✅ Using large dataset: {DATASET_FILE}")
        print(f"  📊 File size: {size_str}")
        print(f"  🔢 Mode: ONE shared file for entire benchmark (all tests use same file)")
        print(f"  📁 Shared files: {os.path.basename(SHARED_TEST_FILE_V1)}, {os.path.basename(SHARED_TEST_FILE_V2)}")
    else:
        print(f"  📝 Using: Default (small test files created per test)")
    print()
    print("Iteration configuration:")
    print(f"  Standard tests iterations: {ITERATION_COUNTS}")
    print(f"  Bulk operations iterations (category 7): {BULK_OPERATIONS_ITERATIONS}")
    print()
    # Load existing progress
    results = load_progress()
    if results:
        print(f"📂 Loaded existing progress from {PROGRESS_FILE}")
        print()
    # Discover all tests
    all_tests = {}
    for test_file in TEST_FILES:
        test_path = test_dir / f"{test_file}.py"
        if test_path.exists():
            print(f"📂 Discovering tests in {test_file}.py...")
            try:
                tests = discover_tests(test_path)
                all_tests.update(tests)
                print(f"  ✓ Found {len(tests)} tests")
            except Exception as e:
                # Following GUIDE_TEST.md: Fix root causes, don't hide errors
                print(f"  ❌ Error discovering tests: {e}")
                print(f"  ⚠️  Root cause analysis needed - check test file for import/syntax errors")
        else:
            print(f"  ⚠️  File not found: {test_path}")
    print(f"\n📊 Total tests discovered: {len(all_tests)}\n")
    if not all_tests:
        print("❌ No tests discovered. Check test files and paths.")
        return 1
    # Run benchmarks asynchronously
    total_tests = len(all_tests)
    try:
        # Run async
        results = asyncio.run(run_all_test_groups_async(all_tests, results, total_tests))
    except Exception as e:
        # Following GUIDE_TEST.md: Fix root causes, don't hide errors
        print(f"\n❌ Benchmark execution failed: {e}")
        print(f"  ⚠️  Root cause analysis needed")
        import traceback
        traceback.print_exc()
        return 1
    # Generate markdown output
    print("\n" + "=" * 80)
    print("Generating markdown report...")
    print("=" * 80)
    try:
        markdown = generate_markdown_tables(results)
        # Save to file
        output_file = script_dir / 'BENCHMARK_RESULTS.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n✅ Benchmark complete! Results saved to: {output_file}")
        print(f"   Total tests run: {total_tests}")
        print(f"   Results file: {output_file.absolute()}")
        # Clean up progress file
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
            print(f"   Progress file cleaned up")
        # Clean up shared test files if they were created
        if SHARED_TEST_FILE_V1 and os.path.exists(SHARED_TEST_FILE_V1):
            try:
                os.remove(SHARED_TEST_FILE_V1)
                if os.path.exists(SHARED_TEST_FILE_V1 + '.idx.json'):
                    os.remove(SHARED_TEST_FILE_V1 + '.idx.json')
                if os.path.exists(SHARED_TEST_FILE_V1 + '.ids.json'):
                    os.remove(SHARED_TEST_FILE_V1 + '.ids.json')
            except Exception:
                pass
        if SHARED_TEST_FILE_V2 and os.path.exists(SHARED_TEST_FILE_V2):
            try:
                os.remove(SHARED_TEST_FILE_V2)
                if os.path.exists(SHARED_TEST_FILE_V2 + '.idx.json'):
                    os.remove(SHARED_TEST_FILE_V2 + '.idx.json')
                if os.path.exists(SHARED_TEST_FILE_V2 + '.ids.json'):
                    os.remove(SHARED_TEST_FILE_V2 + '.ids.json')
            except Exception:
                pass
        return 0
    except Exception as e:
        # Following GUIDE_TEST.md: Fix root causes, don't hide errors
        print(f"\n❌ Error generating report: {e}")
        print(f"  ⚠️  Root cause analysis needed")
        import traceback
        traceback.print_exc()
        return 1
if __name__ == '__main__':
    # Pass sys.argv[1:] explicitly so tests can call main([]) if needed
    sys.exit(main(sys.argv[1:]))
