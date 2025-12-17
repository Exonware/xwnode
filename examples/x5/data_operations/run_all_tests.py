"""
#exonware/xwnode/examples/x5/data_operations/run_all_tests.py

Main Test Runner

Runs all data operations test suites and reports results.
Tests both V1 (Streaming) and V2 (Indexed) implementations.

Following GUIDE_TEST.md standards:
- Uses pytest for test execution
- Proper error handling
- Root cause fixing
- No rigged tests

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import subprocess
import time
import inspect
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Configure UTF-8 for Windows console (GUIDE_TEST.md requirement)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Import all test modules
import test_1_create_operations
import test_2_read_operations
import test_3_update_operations
import test_4_delete_operations
import test_5_list_query_operations
import test_6_search_operations
import test_7_bulk_operations
import test_8_transaction_operations
import test_9_index_operations
import test_10_validation_operations
import test_11_aggregation_operations
import test_12_file_operations
import test_13_concurrency_operations
import test_14_async_operations
import test_15_utility_operations
import test_16_monitoring_operations


def get_test_functions(module) -> List[Tuple[Any, str]]:
    """Get all test functions from a module."""
    tests = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and name.startswith('test_'):
            tests.append((obj, name))
    return sorted(tests, key=lambda x: x[1])


def run_test(test_func, test_name: str) -> Tuple[bool, float, float, str]:
    """Run a single test and return (success, v1_time, v2_time, error_msg)."""
    try:
        start_time = time.perf_counter()
        result = test_func()
        elapsed = time.perf_counter() - start_time
        
        if isinstance(result, tuple) and len(result) >= 3:
            success, v1_time, v2_time = result[0], result[1], result[2]
            if success:
                return True, v1_time, v2_time, ""
            else:
                return False, v1_time, v2_time, "Test returned False"
        else:
            return False, 0.0, 0.0, f"Invalid return value: {result}"
    except AssertionError as e:
        return False, 0.0, 0.0, f"Assertion failed: {str(e)}"
    except Exception as e:
        return False, 0.0, 0.0, f"Exception: {type(e).__name__}: {str(e)}"


def run_test_suite(module, suite_name: str) -> Dict[str, Any]:
    """Run all tests in a test suite."""
    print(f"\n{'='*80}")
    print(f"{suite_name}")
    print(f"{'='*80}")
    
    tests = get_test_functions(module)
    results = {
        'suite_name': suite_name,
        'total': len(tests),
        'passed': 0,
        'failed': 0,
        'total_v1_time': 0.0,
        'total_v2_time': 0.0,
        'tests': []
    }
    
    for test_func, test_name in tests:
        print(f"\nRunning {test_name}...", end=" ", flush=True)
        success, v1_time, v2_time, error = run_test(test_func, test_name)
        
        results['tests'].append({
            'name': test_name,
            'success': success,
            'v1_time': v1_time,
            'v2_time': v2_time,
            'error': error
        })
        
        if success:
            results['passed'] += 1
            results['total_v1_time'] += v1_time
            results['total_v2_time'] += v2_time
            print(f"✓ (V1: {v1_time*1000:.2f}ms, V2: {v2_time*1000:.2f}ms)")
        else:
            results['failed'] += 1
            print(f"✗ {error}")
    
    return results


def print_summary(all_results: List[Dict[str, Any]]):
    """Print summary of all test results."""
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_v1_time = 0.0
    total_v2_time = 0.0
    
    for result in all_results:
        suite_name = result['suite_name']
        total = result['total']
        passed = result['passed']
        failed = result['failed']
        v1_time = result['total_v1_time']
        v2_time = result['total_v2_time']
        
        total_tests += total
        total_passed += passed
        total_failed += failed
        total_v1_time += v1_time
        total_v2_time += v2_time
        
        status = "✓" if failed == 0 else "✗"
        print(f"\n{status} {suite_name}:")
        print(f"  Total: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  V1 Total Time: {v1_time*1000:.2f}ms")
        print(f"  V2 Total Time: {v2_time*1000:.2f}ms")
        if v1_time > 0 and v2_time > 0:
            speedup = v1_time / v2_time if v2_time > 0 else 0
            print(f"  Speedup: {speedup:.2f}x")
    
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    print(f"\nTotal V1 Time: {total_v1_time*1000:.2f}ms")
    print(f"Total V2 Time: {total_v2_time*1000:.2f}ms")
    if total_v1_time > 0 and total_v2_time > 0:
        overall_speedup = total_v1_time / total_v2_time if total_v2_time > 0 else 0
        print(f"Overall Speedup: {overall_speedup:.2f}x")
    
    if total_failed > 0:
        print(f"\n{'='*80}")
        print("FAILED TESTS")
        print(f"{'='*80}")
        for result in all_results:
            for test in result['tests']:
                if not test['success']:
                    print(f"\n✗ {test['name']}")
                    print(f"  Error: {test['error']}")
    
    return total_failed == 0


def main():
    """Run all test suites."""
    print("="*80)
    print("DATA OPERATIONS TEST SUITE")
    print("Testing V1 (Streaming) vs V2 (Indexed) JSON Utils")
    print("="*80)
    
    all_results = []
    
    # Run CREATE tests
    try:
        result = run_test_suite(test_1_create_operations, "CREATE Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run CREATE tests: {e}")
        all_results.append({
            'suite_name': 'CREATE Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run READ tests
    try:
        result = run_test_suite(test_2_read_operations, "READ Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run READ tests: {e}")
        all_results.append({
            'suite_name': 'READ Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run UPDATE tests
    try:
        result = run_test_suite(test_3_update_operations, "UPDATE Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run UPDATE tests: {e}")
        all_results.append({
            'suite_name': 'UPDATE Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run DELETE tests
    try:
        result = run_test_suite(test_4_delete_operations, "DELETE Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run DELETE tests: {e}")
        all_results.append({
            'suite_name': 'DELETE Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run LIST/QUERY tests
    try:
        result = run_test_suite(test_5_list_query_operations, "LIST/QUERY Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run LIST/QUERY tests: {e}")
        all_results.append({
            'suite_name': 'LIST/QUERY Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run SEARCH tests
    try:
        result = run_test_suite(test_6_search_operations, "SEARCH Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run SEARCH tests: {e}")
        all_results.append({
            'suite_name': 'SEARCH Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run BULK tests
    try:
        result = run_test_suite(test_7_bulk_operations, "BULK Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run BULK tests: {e}")
        all_results.append({
            'suite_name': 'BULK Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run TRANSACTION tests
    try:
        result = run_test_suite(test_8_transaction_operations, "TRANSACTION Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run TRANSACTION tests: {e}")
        all_results.append({
            'suite_name': 'TRANSACTION Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run INDEX tests
    try:
        result = run_test_suite(test_9_index_operations, "INDEX Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run INDEX tests: {e}")
        all_results.append({
            'suite_name': 'INDEX Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run VALIDATION tests
    try:
        result = run_test_suite(test_10_validation_operations, "VALIDATION Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run VALIDATION tests: {e}")
        all_results.append({
            'suite_name': 'VALIDATION Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run AGGREGATION tests
    try:
        result = run_test_suite(test_11_aggregation_operations, "AGGREGATION Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run AGGREGATION tests: {e}")
        all_results.append({
            'suite_name': 'AGGREGATION Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run FILE tests
    try:
        result = run_test_suite(test_12_file_operations, "FILE Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run FILE tests: {e}")
        all_results.append({
            'suite_name': 'FILE Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run CONCURRENCY tests
    try:
        result = run_test_suite(test_13_concurrency_operations, "CONCURRENCY Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run CONCURRENCY tests: {e}")
        all_results.append({
            'suite_name': 'CONCURRENCY Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run ASYNC tests
    try:
        result = run_test_suite(test_14_async_operations, "ASYNC Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run ASYNC tests: {e}")
        all_results.append({
            'suite_name': 'ASYNC Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run UTILITY tests
    try:
        result = run_test_suite(test_15_utility_operations, "UTILITY Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run UTILITY tests: {e}")
        all_results.append({
            'suite_name': 'UTILITY Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Run MONITORING tests
    try:
        result = run_test_suite(test_16_monitoring_operations, "MONITORING Operations")
        all_results.append(result)
    except Exception as e:
        print(f"\n✗ Failed to run MONITORING tests: {e}")
        all_results.append({
            'suite_name': 'MONITORING Operations',
            'total': 0,
            'passed': 0,
            'failed': 1,
            'total_v1_time': 0.0,
            'total_v2_time': 0.0,
            'tests': []
        })
    
    # Print summary
    success = print_summary(all_results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

