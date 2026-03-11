#!/usr/bin/env python3
"""
Test runner for test_3_update_operations.py
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
from test_3_update_operations import (
    test_3_1_1_update_single_property,
    test_3_1_2_update_nested_property,
    test_3_1_3_update_array_element,
    test_3_1_4_update_with_path,
    test_3_1_5_update_with_default,
    test_3_2_1_update_multiple_properties,
    test_3_2_2_update_50_percent_of_fields,
    test_3_2_3_update_all_fields,
    test_3_2_4_update_with_merge,
    test_3_2_5_update_with_partial_merge,
    test_3_3_1_update_if_exists,
    test_3_3_2_update_if_matches,
    test_3_3_3_update_first_matching,
    test_3_3_4_update_all_matching,
    test_3_3_5_update_with_validation,
    test_3_4_1_increment_numeric_field,
    test_3_4_2_append_to_array,
    test_3_4_3_prepend_to_array,
    test_3_4_4_remove_from_array,
    test_3_4_5_update_array_element,
    test_3_4_6_concatenate_strings,
    test_3_5_1_update_with_transformation,
    test_3_5_2_update_with_calculation,
    test_3_5_3_update_with_reference,
    test_3_5_4_update_with_timestamp,
    test_3_5_5_update_with_versioning,
    test_3_6_1_update_on_empty_file,
    test_3_6_2_update_nonexistent_record,
    test_3_6_3_update_with_null_values,
    test_3_6_4_update_with_unicode_special_characters,
    test_3_6_5_update_with_missing_field,
    test_3_6_6_update_with_invalid_path,
    test_3_6_7_update_with_type_change,
    test_3_6_8_update_with_very_large_value,
    test_3_6_9_update_array_out_of_bounds,
    test_3_6_10_update_empty_array,
    test_3_6_11_update_with_missing_id_field,
    test_3_6_12_update_nested_path_with_type_mismatch,
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
    print("UPDATE Operations Test Suite")
    print("="*80)
    tests = [
        (test_3_1_1_update_single_property, "test_3_1_1_update_single_property"),
        (test_3_1_2_update_nested_property, "test_3_1_2_update_nested_property"),
        (test_3_1_3_update_array_element, "test_3_1_3_update_array_element"),
        (test_3_1_4_update_with_path, "test_3_1_4_update_with_path"),
        (test_3_1_5_update_with_default, "test_3_1_5_update_with_default"),
        (test_3_2_1_update_multiple_properties, "test_3_2_1_update_multiple_properties"),
        (test_3_2_2_update_50_percent_of_fields, "test_3_2_2_update_50_percent_of_fields"),
        (test_3_2_3_update_all_fields, "test_3_2_3_update_all_fields"),
        (test_3_2_4_update_with_merge, "test_3_2_4_update_with_merge"),
        (test_3_2_5_update_with_partial_merge, "test_3_2_5_update_with_partial_merge"),
        (test_3_3_1_update_if_exists, "test_3_3_1_update_if_exists"),
        (test_3_3_2_update_if_matches, "test_3_3_2_update_if_matches"),
        (test_3_3_3_update_first_matching, "test_3_3_3_update_first_matching"),
        (test_3_3_4_update_all_matching, "test_3_3_4_update_all_matching"),
        (test_3_3_5_update_with_validation, "test_3_3_5_update_with_validation"),
        (test_3_4_1_increment_numeric_field, "test_3_4_1_increment_numeric_field"),
        (test_3_4_2_append_to_array, "test_3_4_2_append_to_array"),
        (test_3_4_3_prepend_to_array, "test_3_4_3_prepend_to_array"),
        (test_3_4_4_remove_from_array, "test_3_4_4_remove_from_array"),
        (test_3_4_5_update_array_element, "test_3_4_5_update_array_element"),
        (test_3_4_6_concatenate_strings, "test_3_4_6_concatenate_strings"),
        (test_3_5_1_update_with_transformation, "test_3_5_1_update_with_transformation"),
        (test_3_5_2_update_with_calculation, "test_3_5_2_update_with_calculation"),
        (test_3_5_3_update_with_reference, "test_3_5_3_update_with_reference"),
        (test_3_5_4_update_with_timestamp, "test_3_5_4_update_with_timestamp"),
        (test_3_5_5_update_with_versioning, "test_3_5_5_update_with_versioning"),
        (test_3_6_1_update_on_empty_file, "test_3_6_1_update_on_empty_file"),
        (test_3_6_2_update_nonexistent_record, "test_3_6_2_update_nonexistent_record"),
        (test_3_6_3_update_with_null_values, "test_3_6_3_update_with_null_values"),
        (test_3_6_4_update_with_unicode_special_characters, "test_3_6_4_update_with_unicode_special_characters"),
        (test_3_6_5_update_with_missing_field, "test_3_6_5_update_with_missing_field"),
        (test_3_6_6_update_with_invalid_path, "test_3_6_6_update_with_invalid_path"),
        (test_3_6_7_update_with_type_change, "test_3_6_7_update_with_type_change"),
        (test_3_6_8_update_with_very_large_value, "test_3_6_8_update_with_very_large_value"),
        (test_3_6_9_update_array_out_of_bounds, "test_3_6_9_update_array_out_of_bounds"),
        (test_3_6_10_update_empty_array, "test_3_6_10_update_empty_array"),
        (test_3_6_11_update_with_missing_id_field, "test_3_6_11_update_with_missing_id_field"),
        (test_3_6_12_update_nested_path_with_type_mismatch, "test_3_6_12_update_nested_path_with_type_mismatch"),
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
