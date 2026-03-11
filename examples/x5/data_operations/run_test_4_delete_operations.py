#!/usr/bin/env python3
"""
Test runner for test_4_delete_operations.py
Runs all tests with edge case handling and proper error reporting.
"""

import sys
import traceback
from pathlib import Path
# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass
# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
# Import test module
from test_4_delete_operations import (
    test_4_1_1_delete_by_id,
    test_4_1_2_delete_by_line_number,
    test_4_1_3_delete_first_matching,
    test_4_1_4_delete_with_confirmation,
    test_4_2_1_delete_all_matching,
    test_4_2_2_delete_by_id_list,
    test_4_2_3_delete_by_line_range,
    test_4_2_4_delete_with_limit,
    test_4_2_5_bulk_delete,
    test_4_3_1_delete_if_exists,
    test_4_3_2_delete_if_matches,
    test_4_3_3_delete_with_cascade,
    test_4_3_4_soft_delete,
    test_4_3_5_hard_delete,
    test_4_4_1_delete_field,
    test_4_4_2_delete_nested_field,
    test_4_4_3_delete_array_element,
    test_4_4_4_delete_multiple_fields,
    test_4_4_5_clear_record,
    # Edge case tests
    test_4_5_1_delete_from_empty_file,
    test_4_5_2_delete_nonexistent_id,
    test_4_5_3_delete_invalid_line_number,
    test_4_5_4_delete_with_missing_id_field,
    test_4_5_5_delete_with_duplicate_ids,
    test_4_5_6_delete_with_null_id,
    test_4_5_7_delete_with_unicode_ids,
    test_4_5_8_delete_last_record,
    test_4_5_9_delete_first_record,
    test_4_5_10_delete_all_records,
    test_4_5_11_delete_with_special_characters,
    test_4_5_12_delete_with_very_large_id,
)

def run_test(test_func, test_name):
    """Run a single test and report results."""
    print(f"\n{'='*80}")
    print(f"Running: {test_name}")
    print(f"{'='*80}")
    try:
        result = test_func()
        if isinstance(result, tuple) and len(result) == 3:
            success, v1_time, v2_time = result
            if success:
                print(f"✅ PASSED - V1: {v1_time*1000:.2f}ms, V2: {v2_time*1000:.2f}ms")
                return True
            else:
                print(f"❌ FAILED - Test returned False")
                return False
        else:
            print(f"✅ PASSED - Result: {result}")
            return True
    except AssertionError as e:
        print(f"❌ ASSERTION FAILED: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("="*80)
    print("DELETE Operations Test Suite")
    print("="*80)
    tests = [
        (test_4_1_1_delete_by_id, "test_4_1_1_delete_by_id"),
        (test_4_1_2_delete_by_line_number, "test_4_1_2_delete_by_line_number"),
        (test_4_1_3_delete_first_matching, "test_4_1_3_delete_first_matching"),
        (test_4_1_4_delete_with_confirmation, "test_4_1_4_delete_with_confirmation"),
        (test_4_2_1_delete_all_matching, "test_4_2_1_delete_all_matching"),
        (test_4_2_2_delete_by_id_list, "test_4_2_2_delete_by_id_list"),
        (test_4_2_3_delete_by_line_range, "test_4_2_3_delete_by_line_range"),
        (test_4_2_4_delete_with_limit, "test_4_2_4_delete_with_limit"),
        (test_4_2_5_bulk_delete, "test_4_2_5_bulk_delete"),
        (test_4_3_1_delete_if_exists, "test_4_3_1_delete_if_exists"),
        (test_4_3_2_delete_if_matches, "test_4_3_2_delete_if_matches"),
        (test_4_3_3_delete_with_cascade, "test_4_3_3_delete_with_cascade"),
        (test_4_3_4_soft_delete, "test_4_3_4_soft_delete"),
        (test_4_3_5_hard_delete, "test_4_3_5_hard_delete"),
        (test_4_4_1_delete_field, "test_4_4_1_delete_field"),
        (test_4_4_2_delete_nested_field, "test_4_4_2_delete_nested_field"),
        (test_4_4_3_delete_array_element, "test_4_4_3_delete_array_element"),
        (test_4_4_4_delete_multiple_fields, "test_4_4_4_delete_multiple_fields"),
        (test_4_4_5_clear_record, "test_4_4_5_clear_record"),
        # Edge case tests
        (test_4_5_1_delete_from_empty_file, "test_4_5_1_delete_from_empty_file"),
        (test_4_5_2_delete_nonexistent_id, "test_4_5_2_delete_nonexistent_id"),
        (test_4_5_3_delete_invalid_line_number, "test_4_5_3_delete_invalid_line_number"),
        (test_4_5_4_delete_with_missing_id_field, "test_4_5_4_delete_with_missing_id_field"),
        (test_4_5_5_delete_with_duplicate_ids, "test_4_5_5_delete_with_duplicate_ids"),
        (test_4_5_6_delete_with_null_id, "test_4_5_6_delete_with_null_id"),
        (test_4_5_7_delete_with_unicode_ids, "test_4_5_7_delete_with_unicode_ids"),
        (test_4_5_8_delete_last_record, "test_4_5_8_delete_last_record"),
        (test_4_5_9_delete_first_record, "test_4_5_9_delete_first_record"),
        (test_4_5_10_delete_all_records, "test_4_5_10_delete_all_records"),
        (test_4_5_11_delete_with_special_characters, "test_4_5_11_delete_with_special_characters"),
        (test_4_5_12_delete_with_very_large_id, "test_4_5_12_delete_with_very_large_id"),
    ]
    results = []
    for test_func, test_name in tests:
        result = run_test(test_func, test_name)
        results.append((test_name, result))
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
    if failed > 0:
        print(f"\n❌ {failed} test(s) failed. See errors above.")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed!")
        sys.exit(0)
if __name__ == "__main__":
    main()
