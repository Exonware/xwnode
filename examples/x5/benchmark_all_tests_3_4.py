"""
Comprehensive Benchmarking Script for V3 vs V4 Performance Comparison
This script runs all tests from the test suite with multiple iteration counts
and generates markdown tables comparing V3 (orjson + ijson) vs V4 (all performance libs).
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
MAX_V3_TIME_SECONDS = 20.0
# Dataset configuration
DATASET_FILE = None
SHARED_TEST_FILE_V3 = None  # Single shared file for V3 for entire benchmark
SHARED_TEST_FILE_V4 = None  # Single shared file for V4 for entire benchmark
# Thread lock for file restoration (prevents race conditions in parallel tests)
FILE_RESTORE_LOCK = threading.Lock()
# Progress file to save/load results
PROGRESS_FILE = Path(__file__).parent / 'benchmark_progress_3_4.json'
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


def safe_restore_file(target_file: str, source_file: str, max_retries: int = 10) -> bool:
    """
    Safely restore a file from source, handling Windows file locking.
    Root cause fix: Windows file locking prevents file operations when files are open.
    This function adds retry logic with exponential backoff and forces file handle closure.
    Following GUIDE_TEST.md: Fix root causes - proper error handling with retries.
    Returns:
        True if restoration succeeded, False otherwise
    """
    if not source_file or not os.path.exists(source_file):
        return False
    # Force garbage collection to close any lingering file handles
    import gc
    gc.collect()
    # Initial delay to allow file handles to close (Windows-specific)
    if sys.platform == "win32":
        time.sleep(0.2)  # 200ms initial delay for Windows
    retry_delay = 0.2  # 200ms base delay
    for attempt in range(max_retries):
        try:
            # Try to remove existing file first (if it exists and is not locked)
            if os.path.exists(target_file):
                try:
                    # On Windows, try to remove read-only flag first
                    if sys.platform == "win32":
                        try:
                            os.chmod(target_file, 0o666)
                        except (PermissionError, OSError):
                            pass  # Ignore chmod errors, try remove anyway
                    # Try to remove the file
                    os.remove(target_file)
                except (PermissionError, OSError):
                    # File might be locked, wait and retry
                    if attempt < max_retries - 1:
                        # Exponential backoff with longer delays
                        wait_time = retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        # Force GC again before retry
                        gc.collect()
                        continue
                    # Last attempt: try to copy over it anyway (Windows allows this sometimes)
                    pass
            # Copy the source file to target
            shutil.copy2(source_file, target_file)
            # Verify the copy succeeded
            if not os.path.exists(target_file):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                return False
            # Clean up index files for the target file (with retry)
            for idx_file in [target_file + '.idx.json', target_file + '.ids.json']:
                if os.path.exists(idx_file):
                    try:
                        if sys.platform == "win32":
                            try:
                                os.chmod(idx_file, 0o666)
                            except (PermissionError, OSError):
                                pass
                        os.remove(idx_file)
                    except (PermissionError, OSError):
                        # Index file locked, continue anyway (not critical)
                        pass
            # Success
            return True
        except (PermissionError, OSError) as e:
            if attempt < max_retries - 1:
                # Wait before retry (exponential backoff)
                wait_time = retry_delay * (2 ** attempt)
                time.sleep(wait_time)
                # Force GC again before retry
                gc.collect()
                continue
            else:
                # Last attempt failed - return False
                return False
    return False


def run_test_with_iterations(test_func: callable, iterations: int, test_name: str = "") -> Optional[tuple[float, float]]:
    """
    Run a test function multiple times and return average (v3_time, v4_time).
    Returns None if test fails or V3 exceeds MAX_V3_TIME_SECONDS.
    When using large datasets: Uses ONE shared file for the entire benchmark run.
    Root cause fix: Swaps json_utils/json_utils_indexed modules to V3/V4 implementations
    before running tests. Tests access modules dynamically through sys.modules.
    Following GUIDE_TEST.md and GUIDE_DEV.md: Never hide errors, show full tracebacks for root cause analysis.
    """
    # Store original modules for restoration
    original_modules = {}
    if 'json_utils' in sys.modules:
        original_modules['json_utils'] = sys.modules['json_utils']
    if 'json_utils_indexed' in sys.modules:
        original_modules['json_utils_indexed'] = sys.modules['json_utils_indexed']
    # Import V3 and V4 modules
    v3_utils = importlib.import_module('json_libs')
    v3_indexed = importlib.import_module('json_libs_indexed')
    v4_utils = importlib.import_module('json_libs_v4')
    v4_indexed = importlib.import_module('json_libs_indexed_v4')
    # If using large dataset, patch create_test_file() to return the shared file
    # Import test_helpers before entering executor to avoid context variable issues
    original_create_test_file = None
    patched_helpers = False
    # Track call count per thread to alternate between V3 and V4 files
    # Root cause fix: Tests call create_test_file() twice (V3 and V4), and they need separate files
    # Solution: Use thread-local counter to alternate between V3 and V4 files
    # IMPORTANT: Counter must be defined outside the if block so it persists across V3/V4 runs
    file_call_counter = threading.local()
    create_shared_test_file = None  # Will be defined in the if block below
    if SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4:
        # Import before executor to preserve context variables
        from data_operations import test_helpers
        # Store original function
        original_create_test_file = test_helpers.create_test_file
        def create_shared_test_file(data: list[dict[str, Any]]) -> str:
            """
            Return the shared large dataset file for testing.
            All tests use the same file - it has as many records as possible (100MB+).
            NOTE: The 'data' parameter is ignored when using large datasets.
            Root cause fix: Tests call create_test_file() twice (once for V3, once for V4).
            We alternate between SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4 to ensure
            V3 and V4 operations don't interfere with each other.
            IMPORTANT: File restoration happens at the START of each iteration (before tests run),
            NOT here. This prevents Windows file locking issues where files are restored while open.
            Uses thread-safe locking to prevent race conditions in parallel execution.
            """
            # Initialize counter if not exists (thread-local)
            if not hasattr(file_call_counter, 'count'):
                file_call_counter.count = 0
            # Increment call counter (thread-local)
            # This counter persists across V3 and V4 runs within the same iteration
            file_call_counter.count += 1
            is_v3_call = (file_call_counter.count % 2 == 1)
            # Determine which file to use (DO NOT restore here - files might be open)
            # File restoration happens at the start of each iteration, before tests run
            target_file = SHARED_TEST_FILE_V3 if is_v3_call else SHARED_TEST_FILE_V4
            # Ensure file exists (should have been created at start of iteration)
            # If it doesn't exist, create it from the source dataset (one-time creation)
            if not os.path.exists(target_file) and DATASET_FILE and os.path.exists(DATASET_FILE):
                # File doesn't exist - create it (only happens on first call)
                with FILE_RESTORE_LOCK:
                    try:
                        shutil.copy2(DATASET_FILE, target_file)
                    except (PermissionError, OSError) as e:
                        # If we can't create it, raise a clear error
                        raise RuntimeError(
                            f"Failed to create test file {target_file} from {DATASET_FILE}. "
                            f"Windows file locking issue: {e}. "
                            f"Ensure the source file is accessible."
                        ) from e
            # Return the appropriate file (V3 or V4)
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
        v3_times = []
        v4_times = []
        # Store original file sizes for restoration
        original_size_v3 = None
        original_size_v4 = None
        if SHARED_TEST_FILE_V3 and os.path.exists(SHARED_TEST_FILE_V3):
            original_size_v3 = os.path.getsize(SHARED_TEST_FILE_V3)
        if SHARED_TEST_FILE_V4 and os.path.exists(SHARED_TEST_FILE_V4):
            original_size_v4 = os.path.getsize(SHARED_TEST_FILE_V4)
        for i in range(iterations):
            # Reset the call counter for this test iteration
            # This ensures each test iteration starts fresh: V3 file on first call, V4 file on second call
            if SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4:
                # Initialize/reset thread-local counter at start of each iteration
                # This ensures V3 gets file on first call (count=1, odd), V4 gets file on second call (count=2, even)
                if not hasattr(file_call_counter, 'count'):
                    file_call_counter.count = 0
                else:
                    file_call_counter.count = 0
                # Restore files at the START of each iteration (before tests run)
                # Root cause fix: Windows file locking - restore files when they're guaranteed to be closed
                # This prevents PermissionError and file corruption issues
                with FILE_RESTORE_LOCK:
                    if DATASET_FILE and os.path.exists(DATASET_FILE):
                        # Restore both files using safe_restore_file helper
                        for target_file in [SHARED_TEST_FILE_V3, SHARED_TEST_FILE_V4]:
                            if not safe_restore_file(target_file, DATASET_FILE):
                                # Following GUIDE_TEST.md: Don't hide errors - log warning
                                print(f"\n    ⚠️  Warning: Failed to restore {target_file} - file may be in use")
                                print(f"       Continuing anyway - test may fail if file is corrupted")
            # Run test twice: once with V3 modules, once with V4 modules
            # Tests return (success, v1_time, v2_time) where both times are from the same run
            # When modules are swapped, both V1 and V2 operations use the swapped version
            # First run: V3 (both V1 and V2 operations use V3)
            # Counter starts at 0, so first call to create_test_file() will increment to 1 (odd) → returns V3 file
            # Restore V3 file before running test (ensure clean state)
            # Root cause fix: Only restore if file doesn't exist or is corrupted
            # Files are already restored at start of iteration, so this is a safety check
            if SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4 and DATASET_FILE and os.path.exists(DATASET_FILE):
                # Only restore if file doesn't exist or is significantly different in size (corrupted)
                should_restore = False
                if not os.path.exists(SHARED_TEST_FILE_V3):
                    should_restore = True
                elif os.path.getsize(SHARED_TEST_FILE_V3) != os.path.getsize(DATASET_FILE):
                    should_restore = True
                if should_restore:
                    with FILE_RESTORE_LOCK:
                        safe_restore_file(SHARED_TEST_FILE_V3, DATASET_FILE)
            sys.modules['json_utils'] = v3_utils
            sys.modules['json_utils_indexed'] = v3_indexed
            # Try to reload test_helpers to pick up swapped modules
            try:
                if 'data_operations.test_helpers' in sys.modules:
                    importlib.reload(sys.modules['data_operations.test_helpers'])
                    # Re-patch create_test_file after reload to ensure counter persists
                    if patched_helpers and create_shared_test_file is not None:
                        from data_operations import test_helpers
                        test_helpers.create_test_file = create_shared_test_file
                        if 'data_operations.test_helpers' in sys.modules:
                            sys.modules['data_operations.test_helpers'].create_test_file = create_shared_test_file
            except (LookupError, AttributeError, RuntimeError):
                pass  # Context variable issues - continue anyway
            try:
                result_v3 = test_func()
                # Force garbage collection after V3 test to close file handles
                # Root cause fix: Windows file locking - ensure handles are closed
                if sys.platform == "win32":
                    import gc
                    gc.collect()
                    time.sleep(0.1)  # Small delay for Windows
                if result_v3 is None:
                    if i == 0:
                        print(f"\n    ⚠️  Test '{test_name}' returned None for V3 - check test implementation")
                    continue
                if isinstance(result_v3, tuple) and len(result_v3) >= 3:
                    success_v3, v1_time, v2_time = result_v3[0], result_v3[1], result_v3[2]
                    # Use v1_time (streaming) for V3 comparison
                    v3_time = v1_time if success_v3 else None
                else:
                    if i == 0:
                        print(f"\n    ⚠️  Test '{test_name}' returned unexpected format for V3: {type(result_v3)}")
                    continue
            except Exception as e:
                # Following GUIDE_TEST.md: Show full traceback for root cause analysis
                error_msg = f"\n    ❌ Test '{test_name}' failed for V3 on iteration {i+1}:"
                error_msg += f"\n       Error Type: {type(e).__name__}"
                error_msg += f"\n       Error Message: {str(e)}"
                error_msg += f"\n       Full Traceback:"
                for line in traceback.format_exception(type(e), e, e.__traceback__):
                    error_msg += f"\n       {line.rstrip()}"
                print(error_msg)
                v3_time = None
            # Second run: V4 (both V1 and V2 operations use V4)
            # Counter is now 1 from V3 run, so first call to create_test_file() will increment to 2 (even) → returns V4 file
            # Add a small delay to ensure V3 file handles are closed before V4 starts
            # Root cause fix: Windows file locking - allow time for file handles to close
            if sys.platform == "win32":
                import gc
                gc.collect()  # Force garbage collection to close file handles
                time.sleep(0.1)  # 100ms delay for Windows
            # Restore V4 file before running test (ensure clean state)
            # Root cause fix: Only restore if file doesn't exist or is corrupted
            if SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4 and DATASET_FILE and os.path.exists(DATASET_FILE):
                # Only restore if file doesn't exist or is significantly different in size (corrupted)
                should_restore = False
                if not os.path.exists(SHARED_TEST_FILE_V4):
                    should_restore = True
                elif os.path.getsize(SHARED_TEST_FILE_V4) != os.path.getsize(DATASET_FILE):
                    should_restore = True
                if should_restore:
                    with FILE_RESTORE_LOCK:
                        safe_restore_file(SHARED_TEST_FILE_V4, DATASET_FILE)
            sys.modules['json_utils'] = v4_utils
            sys.modules['json_utils_indexed'] = v4_indexed
            # Try to reload test_helpers to pick up swapped modules
            try:
                if 'data_operations.test_helpers' in sys.modules:
                    importlib.reload(sys.modules['data_operations.test_helpers'])
                    # Re-patch create_test_file after reload to ensure counter persists
                    if patched_helpers and create_shared_test_file is not None:
                        from data_operations import test_helpers
                        test_helpers.create_test_file = create_shared_test_file
                        if 'data_operations.test_helpers' in sys.modules:
                            sys.modules['data_operations.test_helpers'].create_test_file = create_shared_test_file
            except (LookupError, AttributeError, RuntimeError):
                pass  # Context variable issues - continue anyway
            try:
                result_v4 = test_func()
                # Force garbage collection after V4 test to close file handles
                # Root cause fix: Windows file locking - ensure handles are closed
                if sys.platform == "win32":
                    import gc
                    gc.collect()
                    time.sleep(0.1)  # Small delay for Windows
                if result_v4 is None:
                    if i == 0:
                        print(f"\n    ⚠️  Test '{test_name}' returned None for V4 - check test implementation")
                    continue
                if isinstance(result_v4, tuple) and len(result_v4) >= 3:
                    success_v4, v1_time, v2_time = result_v4[0], result_v4[1], result_v4[2]
                    # Use v1_time (streaming) for V4 comparison to match V3
                    v4_time = v1_time if success_v4 else None
                else:
                    if i == 0:
                        print(f"\n    ⚠️  Test '{test_name}' returned unexpected format for V4: {type(result_v4)}")
                    continue
            except Exception as e:
                # Following GUIDE_TEST.md: Show full traceback for root cause analysis
                error_msg = f"\n    ❌ Test '{test_name}' failed for V4 on iteration {i+1}:"
                error_msg += f"\n       Error Type: {type(e).__name__}"
                error_msg += f"\n       Error Message: {str(e)}"
                error_msg += f"\n       Full Traceback:"
                for line in traceback.format_exception(type(e), e, e.__traceback__):
                    error_msg += f"\n       {line.rstrip()}"
                print(error_msg)
                v4_time = None
            # Only record if both succeeded
            if v3_time is not None and v4_time is not None:
                v3_times.append(v3_time)
                v4_times.append(v4_time)
                # Check if V3 is taking too long
                if v3_time > MAX_V3_TIME_SECONDS:
                    print(f"\n    ⚠️  Stopping: V3 time ({v3_time:.2f}s) exceeds {MAX_V3_TIME_SECONDS}s")
                    return None
            else:
                # Restore files even on error
                if SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4 and DATASET_FILE and os.path.exists(DATASET_FILE):
                    shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V3)
                    shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V4)
                if i == 0:
                    print(f"\n    ⚠️  Test '{test_name}': One or both versions failed on iteration {i+1}")
        if not v3_times or not v4_times:
            # Following GUIDE_TEST.md: Don't hide failures - explain why
            if not v3_times and not v4_times:
                print(f"\n    ⚠️  Test '{test_name}': No successful iterations completed")
            elif not v3_times:
                print(f"\n    ⚠️  Test '{test_name}': No V3 times collected")
            elif not v4_times:
                print(f"\n    ⚠️  Test '{test_name}': No V4 times collected")
            return None
        avg_v3 = sum(v3_times) / len(v3_times)
        avg_v4 = sum(v4_times) / len(v4_times)
        return (avg_v3, avg_v4)
    finally:
        # Restore original modules
        if 'json_utils' in original_modules:
            sys.modules['json_utils'] = original_modules['json_utils']
        if 'json_utils_indexed' in original_modules:
            sys.modules['json_utils_indexed'] = original_modules['json_utils_indexed']
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
    output.append("# V3 vs V4 Performance Benchmark Results")
    output.append(f"*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*")
    output.append("")
    output.append("## Summary Table: Last Time V3 Beat V4")
    output.append("")
    # Summary table
    summary_rows = []
    for category in sorted(results.keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
        for subcategory in sorted(results[category].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
            for test_num in sorted(results[category][subcategory].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
                test_data = results[category][subcategory][test_num]
                test_title = test_data['title']
                last_v3_win = test_data.get('last_v3_win', None)
                if last_v3_win is not None:
                    summary_rows.append(
                        f"| {category}.{subcategory}.{test_num} {test_title} | {last_v3_win} |"
                    )
    if summary_rows:
        output.append("| TEST | Last Time V3 Beat V4 |")
        output.append("|------|---------------------|")
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
            # Create table header
            header = "| Test | Title |"
            separator = "|------|-------|"
            for iters in iteration_counts:
                header += f" V3 ({iters}) | V4 ({iters}) |"
                separator += "---------|---------|"
            output.append(header)
            output.append(separator)
            # Add rows for each test
            for test_num in sorted(results[category][subcategory].keys(), key=lambda x: int(x) if isinstance(x, (int, str)) else x):
                test_data = results[category][subcategory][test_num]
                test_title = test_data['title']
                row = f"| {category}.{subcategory}.{test_num} | {test_title} |"
                test_results = test_data.get('results', {})
                for iters in iteration_counts:
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
                    if result is not None:
                        v3_time, v4_time = result
                        row += f" {v3_time:.4f}s | {v4_time:.4f}s |"
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
        last_v3_win = results[cat][subcat][test_num].get('last_v3_win', None) if (
            cat in results and 
            subcat in results[cat] and 
            test_num in results[cat][subcat]
        ) else None
        for iterations in iteration_counts:
            normalized_iterations = int(iterations) if isinstance(iterations, (int, str)) else iterations
            if normalized_iterations in test_results or iterations in test_results:
                continue
            print(f"  🔄 Running with {iterations} iteration(s)...", end=" ", flush=True)
            try:
                if hasattr(asyncio, 'to_thread'):
                    result = await asyncio.to_thread(
                        run_test_with_iterations, 
                        test_func, 
                        iterations,
                        f"{cat}.{subcat}.{test_num} - {test_title}"
                    )
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, 
                        run_test_with_iterations, 
                        test_func, 
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
                result = None
            if result is None:
                print("❌ Failed or stopped (see error details above)")
                break
            v3_time, v4_time = result
            normalized_iterations = int(iterations) if isinstance(iterations, (int, str)) else iterations
            test_results[normalized_iterations] = (v3_time, v4_time)
            # Track last time V3 was faster
            if v3_time < v4_time:
                last_v3_win = iterations
            winner = "V3" if v3_time < v4_time else "V4"
            if v3_time == 0 or v4_time == 0:
                if v3_time == 0 and v4_time == 0:
                    speedup = 1.0
                    speedup_str = f"{speedup:.2f}x faster"
                elif v3_time == 0:
                    speedup_str = "instant"
                else:
                    speedup_str = "instant"
            else:
                speedup = max(v3_time, v4_time) / min(v3_time, v4_time)
                speedup_str = f"{speedup:.2f}x faster"
            print(f"✓ {winner} wins ({speedup_str})")
            category_results[subcat][test_num] = {
                'title': test_title,
                'results': test_results,
                'last_v3_win': last_v3_win
            }
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
    Run all 16 test groups sequentially for large datasets.
    Following GUIDE_TEST.md: Proper async execution with error handling.
    """
    # Group tests by category
    tests_by_category = defaultdict(list)
    for (category, subcategory, test_num), (test_title, test_func) in all_tests.items():
        tests_by_category[category].append(((category, subcategory, test_num), (test_title, test_func)))
    test_counter = {'current': 0}
    counter_lock = asyncio.Lock()
    progress_lock = asyncio.Lock()
    # For large datasets, run tests sequentially to avoid file conflicts
    use_parallel = not (SHARED_TEST_FILE_V3 and SHARED_TEST_FILE_V4)
    if use_parallel:
        print("🚀 Running all 16 test groups in parallel (async)...\n")
    else:
        print("🚀 Running all 16 test groups sequentially (large dataset mode)...\n")
    category_results = {}
    categories = sorted(tests_by_category.keys())
    if use_parallel:
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
        for category, task in tasks:
            try:
                cat_results = await task
                category_results[category] = cat_results
            except Exception as e:
                print(f"❌ Category {category} failed: {e}")
    else:
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
                print(f"❌ Category {category} failed: {e}")
    return results


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for modular benchmarking configuration."""
    parser = argparse.ArgumentParser(
        description="Comprehensive V3 vs V4 benchmarking for xwnode examples/x5",
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
    return parser.parse_args(argv)


def configure_iteration_counts(args: argparse.Namespace) -> None:
    """Configure global iteration counts from CLI arguments."""
    global ITERATION_COUNTS, BULK_OPERATIONS_ITERATIONS
    if args.iterations:
        try:
            ITERATION_COUNTS = [
                int(x.strip())
                for x in args.iterations.split(",")
                if x.strip()
            ]
        except ValueError as e:
            print(f"❌ Invalid --iterations value '{args.iterations}': {e}")
            sys.exit(1)
    else:
        ITERATION_COUNTS = DEFAULT_ITERATION_COUNTS
    if args.bulk_iterations:
        try:
            BULK_OPERATIONS_ITERATIONS = [
                int(x.strip())
                for x in args.bulk_iterations.split(",")
                if x.strip()
            ]
        except ValueError as e:
            print(f"❌ Invalid --bulk-iterations value '{args.bulk_iterations}': {e}")
            sys.exit(1)
    else:
        BULK_OPERATIONS_ITERATIONS = DEFAULT_BULK_OPERATIONS_ITERATIONS


def configure_dataset(dataset_option: str) -> None:
    """Configure dataset file based on option. Creates ONE shared file for the entire benchmark run."""
    global DATASET_FILE, SHARED_TEST_FILE_V3, SHARED_TEST_FILE_V4
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
        base_name = dataset_path.stem
        SHARED_TEST_FILE_V3 = str(data_dir / f"{base_name}_tested_v3.jsonl")
        SHARED_TEST_FILE_V4 = str(data_dir / f"{base_name}_tested_v4.jsonl")
        source_size = os.path.getsize(DATASET_FILE)
        source_size_mb = source_size / (1024 * 1024)
        print(f"  📋 Creating shared test files ({source_size_mb:.1f} MB each)...", end=" ", flush=True)
        shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V3)
        shutil.copy2(DATASET_FILE, SHARED_TEST_FILE_V4)
        if not os.path.exists(SHARED_TEST_FILE_V3) or os.path.getsize(SHARED_TEST_FILE_V3) != source_size:
            raise RuntimeError(f"Failed to create shared test file: {SHARED_TEST_FILE_V3}")
        if not os.path.exists(SHARED_TEST_FILE_V4) or os.path.getsize(SHARED_TEST_FILE_V4) != source_size:
            raise RuntimeError(f"Failed to create shared test file: {SHARED_TEST_FILE_V4}")
        print("✅", flush=True)
    else:
        DATASET_FILE = None
        SHARED_TEST_FILE_V3 = None
        SHARED_TEST_FILE_V4 = None


def main(argv: Optional[list[str]] = None):
    """Main benchmarking function."""
    args = parse_args(argv)
    configure_iteration_counts(args)
    try:
        configure_dataset(args.dataset)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    script_dir = Path(__file__).parent
    test_dir = script_dir / 'data_operations'
    if not test_dir.exists():
        print(f"❌ Error: Test directory not found: {test_dir}")
        return 1
    print("=" * 80)
    print("V3 vs V4 Comprehensive Benchmarking")
    print("=" * 80)
    print()
    print("Dataset configuration:")
    if DATASET_FILE and SHARED_TEST_FILE_V3:
        file_size_mb = os.path.getsize(DATASET_FILE) / (1024 * 1024)
        file_size_gb = file_size_mb / 1024
        if file_size_gb >= 1.0:
            size_str = f"{file_size_gb:.2f} GB"
        else:
            size_str = f"{file_size_mb:.2f} MB"
        print(f"  ✅ Using large dataset: {DATASET_FILE}")
        print(f"  📊 File size: {size_str}")
        print(f"  🔢 Mode: ONE shared file for entire benchmark (all tests use same file)")
        print(f"  📁 Shared files: {os.path.basename(SHARED_TEST_FILE_V3)}, {os.path.basename(SHARED_TEST_FILE_V4)}")
    else:
        print(f"  📝 Using: Default (small test files created per test)")
    print()
    print("Iteration configuration:")
    print(f"  Standard tests iterations: {ITERATION_COUNTS}")
    print(f"  Bulk operations iterations (category 7): {BULK_OPERATIONS_ITERATIONS}")
    print()
    results = load_progress()
    if results:
        print(f"📂 Loaded existing progress from {PROGRESS_FILE}")
        print()
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
        else:
            print(f"  ⚠️  File not found: {test_path}")
    print(f"\n📊 Total tests discovered: {len(all_tests)}\n")
    if not all_tests:
        print("❌ No tests discovered. Check test files and paths.")
        return 1
    total_tests = len(all_tests)
    try:
        results = asyncio.run(run_all_test_groups_async(all_tests, results, total_tests))
    except Exception as e:
        print(f"\n❌ Benchmark execution failed: {e}")
        traceback.print_exc()
        return 1
    print("\n" + "=" * 80)
    print("Generating markdown report...")
    print("=" * 80)
    try:
        markdown = generate_markdown_tables(results)
        output_file = script_dir / 'BENCHMARK_RESULTS_3_4.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n✅ Benchmark complete! Results saved to: {output_file}")
        print(f"   Total tests run: {total_tests}")
        print(f"   Results file: {output_file.absolute()}")
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
            print(f"   Progress file cleaned up")
        if SHARED_TEST_FILE_V3 and os.path.exists(SHARED_TEST_FILE_V3):
            try:
                os.remove(SHARED_TEST_FILE_V3)
                if os.path.exists(SHARED_TEST_FILE_V3 + '.idx.json'):
                    os.remove(SHARED_TEST_FILE_V3 + '.idx.json')
                if os.path.exists(SHARED_TEST_FILE_V3 + '.ids.json'):
                    os.remove(SHARED_TEST_FILE_V3 + '.ids.json')
            except Exception:
                pass
        if SHARED_TEST_FILE_V4 and os.path.exists(SHARED_TEST_FILE_V4):
            try:
                os.remove(SHARED_TEST_FILE_V4)
                if os.path.exists(SHARED_TEST_FILE_V4 + '.idx.json'):
                    os.remove(SHARED_TEST_FILE_V4 + '.idx.json')
                if os.path.exists(SHARED_TEST_FILE_V4 + '.ids.json'):
                    os.remove(SHARED_TEST_FILE_V4 + '.ids.json')
            except Exception:
                pass
        return 0
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        traceback.print_exc()
        return 1
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
