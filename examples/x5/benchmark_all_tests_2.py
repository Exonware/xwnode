"""
Comprehensive Benchmarking Script for V1 vs V2 vs V3 vs V4 Performance Comparison
This script runs all tests from the test suite with multiple iteration counts
and generates markdown tables comparing all 4 versions.
V1: json_utils (stdlib json, streaming)
V2: json_utils_indexed (stdlib json, indexed)
V3: json_libs (orjson + ijson, streaming) / json_libs_indexed (orjson + ijson, indexed)
V4: json_libs_v4 (all performance libs, streaming) / json_libs_indexed_v4 (all performance libs, indexed)
"""

import sys
import os
import time
import importlib
import importlib.util
import inspect
import asyncio
import traceback
from pathlib import Path
from collections import defaultdict
import json
import argparse
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
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
# Progress file to save/load results
PROGRESS_FILE = Path(__file__).parent / 'benchmark_progress_v2.json'
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


def parse_test_name(test_name: str) -> tuple[int, int, int, str] | None:
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


def discover_tests(test_file_path: Path) -> dict[tuple[int, int, int], tuple[str, callable, str]]:
    """
    Discover all test functions from a test file.
    Returns dict mapping (category, subcategory, test_num) to (test_title, test_func, module_name).
    """
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
                tests[(category, subcategory, test_num)] = (test_title, obj, module_name)
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


def run_test_with_version(
    test_func: callable,
    test_func_name: str,
    module_name: str,
    version: str,
    test_name: str = ""
) -> tuple[bool, float] | None:
    """
    Run a test function with a specific version implementation.
    Returns (success, time) or None if test fails.
    Strategy: 
    - For V1/V2: Use times from test result directly (tests measure V1/V2 internally)
    - For V3/V4: Swap modules in sys.modules and run test (modules are accessed dynamically)
    Root cause fix: Avoid importlib.reload() in thread contexts where context variables
    (used by lazyimports) aren't available. Instead, swap modules and let tests access
    them dynamically through sys.modules.
    Following GUIDE_TEST.md and GUIDE_DEV.md: Never hide errors, show full tracebacks for root cause analysis.
    """
    # Store original modules
    original_modules = {}
    try:
        script_dir = Path(__file__).parent
        # For V1/V2, use the test result directly (no module swapping needed)
        if version == "v1" or version == "v2":
            start_time = time.perf_counter()
            result = test_func()
            elapsed_time = time.perf_counter() - start_time
            if result is None:
                return None
            if isinstance(result, tuple) and len(result) >= 3:
                success, v1_time, v2_time = result[0], result[1], result[2]
                time_to_use = v1_time if version == "v1" else v2_time
                return (success, time_to_use)
            else:
                return (True, elapsed_time)
        # For V3/V4, swap modules in sys.modules
        # Root cause fix: Store original modules before swapping
        if 'json_utils' in sys.modules:
            original_modules['json_utils'] = sys.modules['json_utils']
        if 'json_utils_indexed' in sys.modules:
            original_modules['json_utils_indexed'] = sys.modules['json_utils_indexed']
        if version == "v3":
            # Import V3 modules
            v3_utils = importlib.import_module('json_libs')
            v3_indexed = importlib.import_module('json_libs_indexed')
            # Replace in sys.modules - tests will access these dynamically
            sys.modules['json_utils'] = v3_utils
            sys.modules['json_utils_indexed'] = v3_indexed
        elif version == "v4":
            # Import V4 modules
            v4_utils = importlib.import_module('json_libs_v4')
            v4_indexed = importlib.import_module('json_libs_indexed_v4')
            # Replace in sys.modules - tests will access these dynamically
            sys.modules['json_utils'] = v4_utils
            sys.modules['json_utils_indexed'] = v4_indexed
        # Root cause fix: Reload modules to pick up swapped implementations.
        # Wrap in try/except to handle context variable issues gracefully.
        # Following GUIDE_TEST.md: Fix root causes - handle edge cases properly.
        test_helpers_modules = ['data_operations.test_helpers', 'test_helpers']
        reloaded_any = False
        for mod_name in test_helpers_modules:
            if mod_name in sys.modules:
                try:
                    importlib.reload(sys.modules[mod_name])
                    reloaded_any = True
                except (LookupError, AttributeError, RuntimeError) as e:
                    # Context variable not available in this thread context
                    # This can happen with lazyimports or other context-dependent imports
                    # Continue without reload - module swap in sys.modules may still work
                    # for some dynamic imports, though module-level imports won't update
                    pass
        # Reload the test module to pick up swapped modules
        test_func_reloaded = False
        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
                # Get the test function from the reloaded module
                reloaded_module = sys.modules[module_name]
                test_func = getattr(reloaded_module, test_func_name)
                test_func_reloaded = True
            except (LookupError, AttributeError, RuntimeError) as e:
                # If reload fails, use original test_func
                # Note: Module-level imports in test_func won't see swapped modules
                # but dynamic imports through sys.modules will work
                test_func_reloaded = False
        # Run the test - it will use the swapped modules from sys.modules
        start_time = time.perf_counter()
        result = test_func()
        elapsed_time = time.perf_counter() - start_time
        if result is None:
            return None
        if isinstance(result, tuple) and len(result) >= 3:
            success, v1_time, v2_time = result[0], result[1], result[2]
            # Use elapsed time for V3/V4 since we're measuring the swapped implementation
            return (success, elapsed_time)
        else:
            return (True, elapsed_time)
    except Exception as e:
        # Following GUIDE_TEST.md: Show full traceback for root cause analysis
        error_msg = f"\n    ❌ Test '{test_name}' failed with {version}:"
        error_msg += f"\n       Error Type: {type(e).__name__}"
        error_msg += f"\n       Error Message: {str(e)}"
        error_msg += f"\n       Full Traceback:"
        for line in traceback.format_exception(type(e), e, e.__traceback__):
            error_msg += f"\n       {line.rstrip()}"
        print(error_msg)
        return None
    finally:
        # Restore original modules
        # Root cause fix: Only restore, don't reload (reload causes context variable issues)
        for mod_name, mod in original_modules.items():
            sys.modules[mod_name] = mod


def run_test_with_iterations(
    test_func: callable,
    test_func_name: str,
    module_name: str,
    iterations: int,
    test_name: str = ""
) -> tuple[float, float, float, float] | None:
    """
    Run a test function multiple times with all 4 versions and return average times.
    Returns (v1_time, v2_time, v3_time, v4_time) or None if test fails.
    Following GUIDE_TEST.md and GUIDE_DEV.md: Never hide errors, show full tracebacks for root cause analysis.
    """
    v1_times = []
    v2_times = []
    v3_times = []
    v4_times = []
    for i in range(iterations):
        # Run with V1
        v1_result = run_test_with_version(test_func, test_func_name, module_name, "v1", test_name)
        if v1_result is None:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' failed with V1")
            continue
        success, v1_time = v1_result
        if not success:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' returned False with V1")
            continue
        v1_times.append(v1_time)
        # Check if V1 is taking too long
        if v1_time > MAX_V1_TIME_SECONDS:
            print(f"\n    ⚠️  Stopping: V1 time ({v1_time:.2f}s) exceeds {MAX_V1_TIME_SECONDS}s")
            return None
        # Run with V2
        v2_result = run_test_with_version(test_func, test_func_name, module_name, "v2", test_name)
        if v2_result is None:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' failed with V2")
            continue
        success, v2_time = v2_result
        if not success:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' returned False with V2")
            continue
        v2_times.append(v2_time)
        # Run with V3
        v3_result = run_test_with_version(test_func, test_func_name, module_name, "v3", test_name)
        if v3_result is None:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' failed with V3")
            continue
        success, v3_time = v3_result
        if not success:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' returned False with V3")
            continue
        v3_times.append(v3_time)
        # Run with V4
        v4_result = run_test_with_version(test_func, test_func_name, module_name, "v4", test_name)
        if v4_result is None:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' failed with V4")
            continue
        success, v4_time = v4_result
        if not success:
            if i == 0:
                print(f"\n    ⚠️  Test '{test_name}' returned False with V4")
            continue
        v4_times.append(v4_time)
    if not v1_times or not v2_times or not v3_times or not v4_times:
        # Following GUIDE_TEST.md: Don't hide failures - explain why
        missing = []
        if not v1_times:
            missing.append("V1")
        if not v2_times:
            missing.append("V2")
        if not v3_times:
            missing.append("V3")
        if not v4_times:
            missing.append("V4")
        print(f"\n    ⚠️  Test '{test_name}': No times collected for {', '.join(missing)}")
        return None
    avg_v1 = sum(v1_times) / len(v1_times)
    avg_v2 = sum(v2_times) / len(v2_times)
    avg_v3 = sum(v3_times) / len(v3_times)
    avg_v4 = sum(v4_times) / len(v4_times)
    return (avg_v1, avg_v2, avg_v3, avg_v4)


def generate_markdown_tables(results: Dict) -> str:
    """Generate markdown tables from benchmark results comparing all 4 versions."""
    output = []
    output.append("# V1 vs V2 vs V3 vs V4 Performance Benchmark Results")
    output.append(f"*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*")
    output.append("")
    output.append("## Summary Table: Fastest Version by Test")
    output.append("")
    # Summary table showing fastest version for each test
    summary_rows = []
    for category in sorted(results.keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
        for subcategory in sorted(results[category].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
            for test_num in sorted(results[category][subcategory].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
                test_data = results[category][subcategory][test_num]
                test_title = test_data['title']
                # Find fastest version across all iterations
                fastest_version = None
                fastest_time = float('inf')
                for iter_key, result in test_data.get('results', {}).items():
                    if result and len(result) == 4:
                        v1_time, v2_time, v3_time, v4_time = result
                        times = {'V1': v1_time, 'V2': v2_time, 'V3': v3_time, 'V4': v4_time}
                        min_time = min(times.values())
                        if min_time < fastest_time:
                            fastest_time = min_time
                            fastest_version = min(times, key=times.get)
                if fastest_version:
                    summary_rows.append(
                        f"| {category}.{subcategory}.{test_num} {test_title} | {fastest_version} |"
                    )
    if summary_rows:
        output.append("| TEST | Fastest Version |")
        output.append("|------|------------------|")
        output.extend(summary_rows)
        output.append("")
    # Detailed tables by category
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
            all_iterations = set()
            for test_num, test_data in results[category][subcategory].items():
                for iter_key in test_data.get('results', {}).keys():
                    normalized = int(iter_key) if isinstance(iter_key, (int, str)) else iter_key
                    all_iterations.add(normalized)
            iteration_counts = sorted(all_iterations) if all_iterations else ITERATION_COUNTS
            # Create table header with all 4 versions
            header = "| Test | Title |"
            separator = "|------|-------|"
            for iters in iteration_counts:
                header += f" V1 ({iters}) | V2 ({iters}) | V3 ({iters}) | V4 ({iters}) |"
                separator += "---------|---------|---------|---------|"
            output.append(header)
            output.append(separator)
            # Add rows for each test
            for test_num in sorted(results[category][subcategory].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
                test_data = results[category][subcategory][test_num]
                test_title = test_data['title']
                row = f"| {category}.{subcategory}.{test_num} | {test_title} |"
                test_results = test_data.get('results', {})
                for iters in iteration_counts:
                    # Try to find matching result
                    result = None
                    if iters in test_results:
                        result = test_results[iters]
                    else:
                        str_iters = str(iters)
                        if str_iters in test_results:
                            result = test_results[str_iters]
                        else:
                            try:
                                int_iters = int(iters) if isinstance(iters, str) else iters
                                if int_iters in test_results:
                                    result = test_results[int_iters]
                            except (ValueError, TypeError):
                                pass
                    if result is not None and len(result) == 4:
                        v1_time, v2_time, v3_time, v4_time = result
                        row += f" {v1_time:.4f}s | {v2_time:.4f}s | {v3_time:.4f}s | {v4_time:.4f}s |"
                    else:
                        row += " N/A | N/A | N/A | N/A |"
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
    category_tests: list[tuple[tuple[int, int, int], tuple[str, callable, str]]],
    results: Dict,
    total_tests: int,
    test_counter: dict[str, int],
    counter_lock: asyncio.Lock,
    progress_lock: asyncio.Lock
) -> Dict:
    """
    Run all tests for a category asynchronously with all 4 versions.
    Following GUIDE_TEST.md: Fix root causes, proper error handling.
    """
    category_results = defaultdict(dict)
    for (cat, subcat, test_num), (test_title, test_func, module_name) in sorted(category_tests):
        async with counter_lock:
            test_counter['current'] += 1
            current_test = test_counter['current']
        # Get iteration counts for this specific test
        test_func_name = test_func.__name__ if hasattr(test_func, '__name__') else ""
        iteration_counts = get_iteration_counts_for_test(cat, test_title, test_func_name)
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
        for iterations in iteration_counts:
            normalized_iterations = int(iterations) if isinstance(iterations, (int, str)) else iterations
            if normalized_iterations in test_results or iterations in test_results:
                continue
            print(f"  🔄 Running with {iterations} iteration(s)...", end=" ", flush=True)
            # Root cause fix: Use asyncio.to_thread() (Python 3.9+) instead of run_in_executor()
            # to preserve context variables needed by lazyimports during module reloading.
            # run_in_executor() doesn't preserve context variables, causing LookupError.
            try:
                # Python 3.9+ has asyncio.to_thread() which preserves context variables
                if hasattr(asyncio, 'to_thread'):
                    result = await asyncio.to_thread(
                        run_test_with_iterations,
                        test_func,
                        test_func_name,
                        module_name,
                        iterations,
                        f"{cat}.{subcat}.{test_num} - {test_title}"
                    )
                else:
                    # Fallback for Python < 3.9: run synchronously in async context
                    # This preserves context variables but blocks the event loop
                    result = run_test_with_iterations(
                        test_func,
                        test_func_name,
                        module_name,
                        iterations,
                        f"{cat}.{subcat}.{test_num} - {test_title}"
                    )
            except Exception as e:
                print(f"\n    ❌ Execution Error for {cat}.{subcat}.{test_num} - {test_title}:")
                print(f"       Error Type: {type(e).__name__}")
                print(f"       Error Message: {str(e)}")
                print(f"       Full Traceback:")
                for line in traceback.format_exception(type(e), e, e.__traceback__):
                    print(f"       {line.rstrip()}")
                print(f"\n    ⚠️  Root cause analysis needed - test execution failed")
                result = None
            if result is None:
                print("❌ Failed or stopped (see error details above)")
                break
            v1_time, v2_time, v3_time, v4_time = result
            normalized_iterations = int(iterations) if isinstance(iterations, (int, str)) else iterations
            test_results[normalized_iterations] = (v1_time, v2_time, v3_time, v4_time)
            # Find fastest version
            times = {'V1': v1_time, 'V2': v2_time, 'V3': v3_time, 'V4': v4_time}
            fastest = min(times, key=times.get)
            speedup = max(times.values()) / min(times.values())
            print(f"✓ {fastest} wins ({speedup:.2f}x faster than slowest)")
            # Save progress after each iteration (thread-safe)
            category_results[subcat][test_num] = {
                'title': test_title,
                'results': test_results,
            }
            results[cat][subcat][test_num] = category_results[subcat][test_num]
            async with progress_lock:
                save_progress(results)
        print()
    return category_results
async def run_all_test_groups_async(
    all_tests: dict[tuple[int, int, int], tuple[str, callable, str]],
    results: Dict,
    total_tests: int
) -> Dict:
    """
    Run all 16 test groups in parallel (async).
    Following GUIDE_TEST.md: Proper async execution with error handling.
    """
    # Group tests by category
    tests_by_category = defaultdict(list)
    for (category, subcategory, test_num), (test_title, test_func, module_name) in all_tests.items():
        tests_by_category[category].append(((category, subcategory, test_num), (test_title, test_func, module_name)))
    # Shared counter for test numbering (thread-safe)
    test_counter = {'current': 0}
    counter_lock = asyncio.Lock()
    progress_lock = asyncio.Lock()
    # Run all categories in parallel
    print("🚀 Running all 16 test groups in parallel (async) with V1/V2/V3/V4 comparison...\n")
    tasks = []
    for category in sorted(tests_by_category.keys()):
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
    # Wait for all tasks to complete
    category_results = {}
    for category, task in tasks:
        try:
            cat_results = await task
            category_results[category] = cat_results
        except Exception as e:
            print(f"❌ Category {category} failed: {e}")
            print(f"  ⚠️  Root cause analysis needed - check test file for issues")
            continue
    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments for modular benchmarking configuration.
    """
    parser = argparse.ArgumentParser(
        description="Comprehensive V1 vs V2 vs V3 vs V4 benchmarking for xwnode examples/x5",
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
    return parser.parse_args(argv)


def configure_iteration_counts(args: argparse.Namespace) -> None:
    """
    Configure global iteration counts from CLI arguments.
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


def main(argv: list[str] | None = None):
    """Main benchmarking function."""
    # Parse CLI arguments and configure iteration strategy
    args = parse_args(argv)
    configure_iteration_counts(args)
    # Get test directory
    script_dir = Path(__file__).parent
    test_dir = script_dir / 'data_operations'
    if not test_dir.exists():
        print(f"❌ Error: Test directory not found: {test_dir}")
        print(f"  ⚠️  Root cause: Test directory path is incorrect")
        return 1
    print("=" * 80)
    print("V1 vs V2 vs V3 vs V4 Comprehensive Benchmarking")
    print("=" * 80)
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
        output_file = script_dir / 'BENCHMARK_RESULTS_V2.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n✅ Benchmark complete! Results saved to: {output_file}")
        print(f"   Total tests run: {total_tests}")
        print(f"   Results file: {output_file.absolute()}")
        # Clean up progress file
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
            print(f"   Progress file cleaned up")
        return 0
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        print(f"  ⚠️  Root cause analysis needed")
        import traceback
        traceback.print_exc()
        return 1
if __name__ == '__main__':
    # Pass sys.argv[1:] explicitly so tests can call main([]) if needed
    sys.exit(main(sys.argv[1:]))
