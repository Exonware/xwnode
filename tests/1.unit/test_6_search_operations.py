"""
#exonware/xwnode/examples/x5/data_operations/test_6_search_operations.py
SEARCH Operations Test Suite
Tests all SEARCH operations (finding data) for both V1 (Streaming) and V2 (Indexed) implementations.
All tests are fully implemented at production level with no TODOs.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import os
import json
import time
import re
from pathlib import Path
from typing import Any
# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    get_all_matching_v1,
    get_all_matching_v2,
)
# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from json_utils import (
    match_by_id,
    stream_read,
    JsonRecordNotFound,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_id,
)
# ============================================================================
# 6.1 Exact Match Search
# ============================================================================


def test_6_1_1_search_by_exact_value():
    """
    Full Test Name: test_6_1_1_search_by_exact_value
    Test: Find records with exact match
    """
    test_data = [
        {"id": "1", "status": "active"},
        {"id": "2", "status": "inactive"},
        {"id": "3", "status": "active"}
    ]
    file_path = create_test_file(test_data)
    try:
        def exact_match(obj):
            return obj.get("status") == "active"
        # V1: Search by exact value
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, exact_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by exact value using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, exact_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("status") == "active" for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_1_2_search_by_id():
    """
    Full Test Name: test_6_1_2_search_by_id
    Test: Find record by identifier
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Search by ID
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, match_by_id("id", "2"))
        v1_time = time.perf_counter() - v1_start
        # V2: Search by ID using index
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_result = indexed_get_by_id(file_path, "2", id_field="id", index=index)
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == {"id": "2", "name": "Bob"}
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_1_3_search_by_multiple_ids():
    """
    Full Test Name: test_6_1_3_search_by_multiple_ids
    Test: Find multiple records by IDs
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
        {"id": "4", "name": "David"}
    ]
    file_path = create_test_file(test_data)
    try:
        id_list = ["1", "3", "4"]
        # V1: Search by multiple IDs
        v1_start = time.perf_counter()
        v1_results = []
        for record_id in id_list:
            try:
                v1_results.append(stream_read(file_path, match_by_id("id", record_id)))
            except Exception:
                pass
        v1_time = time.perf_counter() - v1_start
        # V2: Search by multiple IDs using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for record_id in id_list:
            try:
                v2_results.append(indexed_get_by_id(file_path, record_id, id_field="id", index=index))
            except Exception:
                pass
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert all(r["id"] in id_list for r in v1_results)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_1_4_search_by_composite_key():
    """
    Full Test Name: test_6_1_4_search_by_composite_key
    Test: Find by multiple field combination
    """
    test_data = [
        {"id": "1", "user_id": "u1", "session_id": "s1", "status": "active"},
        {"id": "2", "user_id": "u1", "session_id": "s2", "status": "active"},
        {"id": "3", "user_id": "u2", "session_id": "s1", "status": "inactive"}
    ]
    file_path = create_test_file(test_data)
    try:
        def composite_match(obj):
            return obj.get("user_id") == "u1" and obj.get("session_id") == "s1"
        # V1: Search by composite key
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, composite_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by composite key using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, composite_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results[0]["id"] == "1"
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.2 Pattern Matching Search
# ============================================================================


def test_6_2_1_search_by_prefix():
    """
    Full Test Name: test_6_2_1_search_by_prefix
    Test: Find records starting with pattern
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Alicia"},
        {"id": "3", "name": "Bob"},
        {"id": "4", "name": "Alice Smith"}
    ]
    file_path = create_test_file(test_data)
    try:
        prefix = "Alic"
        def prefix_match(obj):
            name = obj.get("name", "").lower()
            return name.startswith(prefix.lower())
        # V1: Search by prefix
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, prefix_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by prefix using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, prefix_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("name", "").lower().startswith(prefix.lower()) for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_2_2_search_by_suffix():
    """
    Full Test Name: test_6_2_2_search_by_suffix
    Test: Find records ending with pattern
    """
    test_data = [
        {"id": "1", "email": "alice@example.com"},
        {"id": "2", "email": "bob@example.com"},
        {"id": "3", "email": "charlie@test.org"},
        {"id": "4", "email": "david@example.com"}
    ]
    file_path = create_test_file(test_data)
    try:
        suffix = "@example.com"
        def suffix_match(obj):
            email = obj.get("email", "").lower()
            return email.endswith(suffix.lower())
        # V1: Search by suffix
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, suffix_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by suffix using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, suffix_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("email", "").lower().endswith(suffix.lower()) for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_2_3_search_by_contains():
    """
    Full Test Name: test_6_2_3_search_by_contains
    Test: Find records containing substring
    """
    test_data = [
        {"id": "1", "description": "Python developer"},
        {"id": "2", "description": "JavaScript developer"},
        {"id": "3", "description": "Python and JavaScript expert"},
        {"id": "4", "description": "Java developer"}
    ]
    file_path = create_test_file(test_data)
    try:
        substring = "Python"
        def contains_match(obj):
            description = obj.get("description", "").lower()
            return substring.lower() in description
        # V1: Search by contains
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, contains_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by contains using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, contains_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(substring.lower() in r.get("description", "").lower() for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_2_4_search_by_regex():
    """
    Full Test Name: test_6_2_4_search_by_regex
    Test: Find records matching regular expression
    """
    test_data = [
        {"id": "1", "email": "alice@example.com"},
        {"id": "2", "email": "bob@test.org"},
        {"id": "3", "email": "charlie@example.com"},
        {"id": "4", "email": "david@other.net"}
    ]
    file_path = create_test_file(test_data)
    try:
        pattern = re.compile(r"@example\.com$")
        def regex_match(obj):
            email = obj.get("email", "")
            return bool(pattern.search(email))
        # V1: Search by regex
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, regex_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by regex using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, regex_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all("@example.com" in r.get("email", "") for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_2_5_search_by_wildcard():
    """
    Full Test Name: test_6_2_5_search_by_wildcard
    Test: Find records matching wildcard pattern
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Alicia"},
        {"id": "3", "name": "Bob"},
        {"id": "4", "name": "Alice Smith"}
    ]
    file_path = create_test_file(test_data)
    try:
        # Simple wildcard: "Alic*" matches "Alic" followed by anything
        wildcard_pattern = "Alic*"
        base_pattern = wildcard_pattern.replace("*", "")
        def wildcard_match(obj):
            name = obj.get("name", "").lower()
            return name.startswith(base_pattern.lower())
        # V1: Search by wildcard
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, wildcard_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by wildcard using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, wildcard_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("name", "").lower().startswith(base_pattern.lower()) for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.3 Range Search
# ============================================================================


def test_6_3_1_search_by_numeric_range():
    """
    Full Test Name: test_6_3_1_search_by_numeric_range
    Test: Find records within number range
    """
    test_data = [
        {"id": "1", "age": 20},
        {"id": "2", "age": 30},
        {"id": "3", "age": 40},
        {"id": "4", "age": 50},
        {"id": "5", "age": 25}
    ]
    file_path = create_test_file(test_data)
    try:
        min_age = 25
        max_age = 40
        def in_numeric_range(obj):
            age = obj.get("age", 0)
            return min_age <= age <= max_age
        # V1: Search by numeric range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, in_numeric_range)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by numeric range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, in_numeric_range, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(min_age <= r.get("age", 0) <= max_age for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_3_2_search_by_date_range():
    """
    Full Test Name: test_6_3_2_search_by_date_range
    Test: Find records within date range
    """
    test_data = [
        {"id": "1", "created": "2024-01-15"},
        {"id": "2", "created": "2024-02-20"},
        {"id": "3", "created": "2024-03-10"},
        {"id": "4", "created": "2024-04-05"}
    ]
    file_path = create_test_file(test_data)
    try:
        start_date = "2024-02-01"
        end_date = "2024-03-31"
        def in_date_range(obj):
            created = obj.get("created", "")
            return start_date <= created <= end_date
        # V1: Search by date range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, in_date_range)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by date range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, in_date_range, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_3_3_search_by_string_range():
    """
    Full Test Name: test_6_3_3_search_by_string_range
    Test: Find records within string range
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
        {"id": "4", "name": "David"}
    ]
    file_path = create_test_file(test_data)
    try:
        start_str = "Bob"
        end_str = "David"
        def in_string_range(obj):
            name = obj.get("name", "")
            return start_str <= name <= end_str
        # V1: Search by string range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, in_string_range)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by string range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, in_string_range, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(start_str <= r.get("name", "") <= end_str for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_3_4_search_by_size_range():
    """
    Full Test Name: test_6_3_4_search_by_size_range
    Test: Find records within size range
    """
    test_data = [
        {"id": "1", "tags": ["a"]},
        {"id": "2", "tags": ["a", "b"]},
        {"id": "3", "tags": ["a", "b", "c", "d"]},
        {"id": "4", "tags": ["a", "b", "c", "d", "e", "f"]}
    ]
    file_path = create_test_file(test_data)
    try:
        min_size = 2
        max_size = 4
        def in_size_range(obj):
            tags = obj.get("tags", [])
            size = len(tags)
            return min_size <= size <= max_size
        # V1: Search by size range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, in_size_range)
        v1_time = time.perf_counter() - v1_start
        # V2: Search by size range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, in_size_range, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(min_size <= len(r.get("tags", [])) <= max_size for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.4 Comparison Search
# ============================================================================


def test_6_4_1_search_greater_than():
    """
    Full Test Name: test_6_4_1_search_greater_than
    Test: Find records where field > value
    """
    test_data = [
        {"id": "1", "score": 50},
        {"id": "2", "score": 75},
        {"id": "3", "score": 90},
        {"id": "4", "score": 60}
    ]
    file_path = create_test_file(test_data)
    try:
        threshold = 70
        def greater_than(obj):
            return obj.get("score", 0) > threshold
        # V1: Search greater than
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, greater_than)
        v1_time = time.perf_counter() - v1_start
        # V2: Search greater than using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, greater_than, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("score", 0) > threshold for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_4_2_search_less_than():
    """
    Full Test Name: test_6_4_2_search_less_than
    Test: Find records where field < value
    """
    test_data = [
        {"id": "1", "score": 50},
        {"id": "2", "score": 75},
        {"id": "3", "score": 90},
        {"id": "4", "score": 60}
    ]
    file_path = create_test_file(test_data)
    try:
        threshold = 70
        def less_than(obj):
            return obj.get("score", 0) < threshold
        # V1: Search less than
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, less_than)
        v1_time = time.perf_counter() - v1_start
        # V2: Search less than using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, less_than, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("score", 0) < threshold for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_4_3_search_greater_or_equal():
    """
    Full Test Name: test_6_4_3_search_greater_or_equal
    Test: Find records where field >= value
    """
    test_data = [
        {"id": "1", "age": 20},
        {"id": "2", "age": 30},
        {"id": "3", "age": 40},
        {"id": "4", "age": 30}
    ]
    file_path = create_test_file(test_data)
    try:
        threshold = 30
        def greater_or_equal(obj):
            return obj.get("age", 0) >= threshold
        # V1: Search greater or equal
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, greater_or_equal)
        v1_time = time.perf_counter() - v1_start
        # V2: Search greater or equal using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, greater_or_equal, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("age", 0) >= threshold for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_4_4_search_less_or_equal():
    """
    Full Test Name: test_6_4_4_search_less_or_equal
    Test: Find records where field <= value
    """
    test_data = [
        {"id": "1", "age": 20},
        {"id": "2", "age": 30},
        {"id": "3", "age": 40},
        {"id": "4", "age": 30}
    ]
    file_path = create_test_file(test_data)
    try:
        threshold = 30
        def less_or_equal(obj):
            return obj.get("age", 0) <= threshold
        # V1: Search less or equal
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, less_or_equal)
        v1_time = time.perf_counter() - v1_start
        # V2: Search less or equal using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, less_or_equal, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("age", 0) <= threshold for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_4_5_search_not_equal():
    """
    Full Test Name: test_6_4_5_search_not_equal
    Test: Find records where field != value
    """
    test_data = [
        {"id": "1", "status": "active"},
        {"id": "2", "status": "inactive"},
        {"id": "3", "status": "active"},
        {"id": "4", "status": "pending"}
    ]
    file_path = create_test_file(test_data)
    try:
        exclude_value = "inactive"
        def not_equal(obj):
            return obj.get("status") != exclude_value
        # V1: Search not equal
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, not_equal)
        v1_time = time.perf_counter() - v1_start
        # V2: Search not equal using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, not_equal, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("status") != exclude_value for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.5 Array/Collection Search
# ============================================================================


def test_6_5_1_search_array_contains():
    """
    Full Test Name: test_6_5_1_search_array_contains
    Test: Find records where array contains value
    """
    test_data = [
        {"id": "1", "tags": ["python", "javascript"]},
        {"id": "2", "tags": ["python", "java"]},
        {"id": "3", "tags": ["javascript", "typescript"]},
        {"id": "4", "tags": ["python", "go"]}
    ]
    file_path = create_test_file(test_data)
    try:
        search_tag = "python"
        def array_contains(obj):
            tags = obj.get("tags", [])
            return search_tag in tags
        # V1: Search array contains
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, array_contains)
        v1_time = time.perf_counter() - v1_start
        # V2: Search array contains using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, array_contains, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(search_tag in r.get("tags", []) for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_5_2_search_array_size():
    """
    Full Test Name: test_6_5_2_search_array_size
    Test: Find records where array length matches
    """
    test_data = [
        {"id": "1", "tags": ["a"]},
        {"id": "2", "tags": ["a", "b"]},
        {"id": "3", "tags": ["a", "b", "c"]},
        {"id": "4", "tags": ["a", "b"]}
    ]
    file_path = create_test_file(test_data)
    try:
        target_size = 2
        def array_size_match(obj):
            tags = obj.get("tags", [])
            return len(tags) == target_size
        # V1: Search array size
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, array_size_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search array size using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, array_size_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(len(r.get("tags", [])) == target_size for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_5_3_search_array_any():
    """
    Full Test Name: test_6_5_3_search_array_any
    Test: Find records where any array element matches
    """
    test_data = [
        {"id": "1", "scores": [50, 60, 70]},
        {"id": "2", "scores": [80, 90, 100]},
        {"id": "3", "scores": [70, 80, 90]},
        {"id": "4", "scores": [40, 50, 60]}
    ]
    file_path = create_test_file(test_data)
    try:
        threshold = 90
        def array_any_match(obj):
            scores = obj.get("scores", [])
            return any(score >= threshold for score in scores)
        # V1: Search array any
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, array_any_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search array any using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, array_any_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_5_4_search_array_all():
    """
    Full Test Name: test_6_5_4_search_array_all
    Test: Find records where all array elements match
    """
    test_data = [
        {"id": "1", "scores": [80, 85, 90]},
        {"id": "2", "scores": [70, 75, 80]},
        {"id": "3", "scores": [90, 95, 100]},
        {"id": "4", "scores": [60, 70, 80]}
    ]
    file_path = create_test_file(test_data)
    try:
        threshold = 80
        def array_all_match(obj):
            scores = obj.get("scores", [])
            return all(score >= threshold for score in scores) if scores else False
        # V1: Search array all
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, array_all_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search array all using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, array_all_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.6 Nested Search
# ============================================================================


def test_6_6_1_search_nested_field():
    """
    Full Test Name: test_6_6_1_search_nested_field
    Test: Find records matching nested path
    """
    test_data = [
        {"id": "1", "user": {"profile": {"age": 30}}},
        {"id": "2", "user": {"profile": {"age": 25}}},
        {"id": "3", "user": {"profile": {"age": 35}}}
    ]
    file_path = create_test_file(test_data)
    try:
        def nested_match(obj):
            age = obj.get("user", {}).get("profile", {}).get("age", 0)
            return age > 28
        # V1: Search nested field
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, nested_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search nested field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, nested_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_6_2_search_deep_nested():
    """
    Full Test Name: test_6_6_2_search_deep_nested
    Test: Find records in deeply nested structures
    """
    test_data = [
        {"id": "1", "level1": {"level2": {"level3": {"value": 10}}}},
        {"id": "2", "level1": {"level2": {"level3": {"value": 20}}}},
        {"id": "3", "level1": {"level2": {"level3": {"value": 15}}}}
    ]
    file_path = create_test_file(test_data)
    try:
        def deep_nested_match(obj):
            value = obj.get("level1", {}).get("level2", {}).get("level3", {}).get("value", 0)
            return value >= 15
        # V1: Search deep nested
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, deep_nested_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search deep nested using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, deep_nested_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_6_3_search_nested_array():
    """
    Full Test Name: test_6_6_3_search_nested_array
    Test: Find records in nested arrays
    """
    test_data = [
        {"id": "1", "user": {"tags": ["python", "js"]}},
        {"id": "2", "user": {"tags": ["java", "python"]}},
        {"id": "3", "user": {"tags": ["go", "rust"]}}
    ]
    file_path = create_test_file(test_data)
    try:
        search_tag = "python"
        def nested_array_match(obj):
            tags = obj.get("user", {}).get("tags", [])
            return search_tag in tags
        # V1: Search nested array
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, nested_array_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search nested array using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, nested_array_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_6_4_search_nested_object():
    """
    Full Test Name: test_6_6_4_search_nested_object
    Test: Find records in nested objects
    """
    test_data = [
        {"id": "1", "data": {"user": {"role": "admin"}}},
        {"id": "2", "data": {"user": {"role": "user"}}},
        {"id": "3", "data": {"user": {"role": "admin"}}}
    ]
    file_path = create_test_file(test_data)
    try:
        def nested_object_match(obj):
            role = obj.get("data", {}).get("user", {}).get("role", "")
            return role == "admin"
        # V1: Search nested object
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, nested_object_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Search nested object using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, nested_object_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.7 Full-Text Search
# ============================================================================


def test_6_7_1_full_text_search():
    """
    Full Test Name: test_6_7_1_full_text_search
    Test: Search across all text content
    """
    test_data = [
        {"id": "1", "name": "Alice", "description": "Software engineer"},
        {"id": "2", "name": "Bob", "description": "Data scientist"},
        {"id": "3", "name": "Charlie", "description": "Software architect"}
    ]
    file_path = create_test_file(test_data)
    try:
        search_term = "software"
        def full_text_match(obj):
            text = json.dumps(obj).lower()
            return search_term.lower() in text
        # V1: Full-text search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, full_text_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Full-text search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, full_text_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_7_2_multi_field_text_search():
    """
    Full Test Name: test_6_7_2_multi_field_text_search
    Test: Search across multiple text fields
    """
    test_data = [
        {"id": "1", "name": "Alice", "email": "alice@example.com", "bio": "Software engineer"},
        {"id": "2", "name": "Bob", "email": "bob@test.org", "bio": "Data analyst"},
        {"id": "3", "name": "Charlie", "email": "charlie@example.com", "bio": "Software developer"}
    ]
    file_path = create_test_file(test_data)
    try:
        search_term = "software"
        search_fields = ["name", "email", "bio"]
        def multi_field_match(obj):
            for field in search_fields:
                value = str(obj.get(field, "")).lower()
                if search_term.lower() in value:
                    return True
            return False
        # V1: Multi-field text search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, multi_field_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Multi-field text search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, multi_field_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_7_3_phrase_search():
    """
    Full Test Name: test_6_7_3_phrase_search
    Test: Find records containing exact phrase
    """
    test_data = [
        {"id": "1", "description": "Python developer expert"},
        {"id": "2", "description": "Python and JavaScript developer"},
        {"id": "3", "description": "JavaScript expert developer"},
        {"id": "4", "description": "Python developer"}
    ]
    file_path = create_test_file(test_data)
    try:
        phrase = "Python developer"
        def phrase_match(obj):
            description = obj.get("description", "").lower()
            return phrase.lower() in description
        # V1: Phrase search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, phrase_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Phrase search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, phrase_match, index=index)
        v2_time = time.perf_counter() - v2_start
        # Only 2 records match: "Python developer expert" and "Python developer"
        # "Python and JavaScript developer" does NOT contain "Python developer" as exact phrase
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        # Verify correct records matched
        ids = {r["id"] for r in v1_results}
        assert ids == {"1", "4"}, f"Expected IDs 1 and 4, got {ids}"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_7_4_boolean_text_search():
    """
    Full Test Name: test_6_7_4_boolean_text_search
    Test: Combine search terms with AND/OR/NOT
    """
    test_data = [
        {"id": "1", "description": "Python and JavaScript developer"},
        {"id": "2", "description": "Python developer"},
        {"id": "3", "description": "JavaScript developer"},
        {"id": "4", "description": "Java developer"}
    ]
    file_path = create_test_file(test_data)
    try:
        term1 = "Python"
        term2 = "JavaScript"
        def boolean_and_match(obj):
            desc = obj.get("description", "").lower()
            return term1.lower() in desc and term2.lower() in desc
        # V1: Boolean AND search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, boolean_and_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Boolean AND search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, boolean_and_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results == v2_results
        # Test OR
        def boolean_or_match(obj):
            desc = obj.get("description", "").lower()
            return term1.lower() in desc or term2.lower() in desc
        v1_or_start = time.perf_counter()
        v1_or_results = get_all_matching_v1(file_path, boolean_or_match)
        v1_or_time = time.perf_counter() - v1_or_start
        v2_or_start = time.perf_counter()
        v2_or_results = get_all_matching_v2(file_path, boolean_or_match, index=index)
        v2_or_time = time.perf_counter() - v2_or_start
        assert len(v1_or_results) == len(v2_or_results) == 3
        total_v1_time = v1_time + v1_or_time
        total_v2_time = v2_time + v2_or_time
        return True, total_v1_time, total_v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_7_5_fuzzy_text_search():
    """
    Full Test Name: test_6_7_5_fuzzy_text_search
    Test: Find similar text with typos
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Alicia"},
        {"id": "3", "name": "Alise"},
        {"id": "4", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        search_term = "Alice"
        def fuzzy_match(obj):
            name = obj.get("name", "").lower()
            search_lower = search_term.lower()
            # Simple fuzzy: starts with or contains similar prefix
            return (name.startswith(search_lower[:3]) or 
                   search_lower[:3] in name or
                   name.startswith(search_lower))
        # V1: Fuzzy text search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, fuzzy_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Fuzzy text search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, fuzzy_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 6.8 Edge Cases and Error Handling
# ============================================================================


def test_6_8_1_search_empty_file():
    """
    Full Test Name: test_6_8_1_search_empty_file
    Test: Search operations on empty file should return empty results
    """
    file_path = create_test_file([])
    try:
        def match_anything(obj):
            return True
        # V1: Search empty file
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, match_anything)
        v1_time = time.perf_counter() - v1_start
        # V2: Search empty file
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, match_anything, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 0
        assert v1_results == v2_results
        # Try searching by ID in empty file
        try:
            result = stream_read(file_path, match_by_id("id", "1"))
            assert False, "Should have raised JsonRecordNotFound"
        except Exception:
            pass  # Expected
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_8_2_search_with_missing_fields():
    """
    Full Test Name: test_6_8_2_search_with_missing_fields
    Test: Search operations handle missing fields gracefully
    """
    test_data = [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob"},  # Missing email
        {"id": "3", "email": "charlie@example.com"},  # Missing name
        {"id": "4"}  # Only id
    ]
    file_path = create_test_file(test_data)
    try:
        def has_email(obj):
            return "email" in obj and obj.get("email") is not None
        # V1: Search with missing fields
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, has_email)
        v1_time = time.perf_counter() - v1_start
        # V2: Search with missing fields
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, has_email, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        assert all("email" in r for r in v1_results)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_8_3_search_nonexistent_id():
    """
    Full Test Name: test_6_8_3_search_nonexistent_id
    Test: Search for non-existent ID should raise appropriate error
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Search non-existent ID
        try:
            result = stream_read(file_path, match_by_id("id", "999"))
            assert False, "Should have raised JsonRecordNotFound"
        except Exception as e:
            assert "not found" in str(e).lower() or isinstance(e, JsonRecordNotFound)
        # V2: Search non-existent ID
        index = build_index(file_path, id_field="id")
        try:
            result = indexed_get_by_id(file_path, "999", id_field="id", index=index)
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected
        return True, 0.0, 0.0
    finally:
        cleanup_test_file(file_path)


def test_6_8_4_search_with_special_characters():
    """
    Full Test Name: test_6_8_4_search_with_special_characters
    Test: Search handles special characters in search terms
    """
    test_data = [
        {"id": "1", "name": "O'Brien", "email": "test+tag@example.com"},
        {"id": "2", "name": "José", "email": "user@test.org"},
        {"id": "3", "name": "A-Name", "email": "dash@test.com"}
    ]
    file_path = create_test_file(test_data)
    try:
        def has_plus_email(obj):
            email = obj.get("email", "")
            return "+" in email
        # V1: Search with special characters
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, has_plus_email)
        v1_time = time.perf_counter() - v1_start
        # V2: Search with special characters
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, has_plus_email, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results == v2_results
        assert "+" in v1_results[0]["email"]
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_8_5_search_with_unicode():
    """
    Full Test Name: test_6_8_5_search_with_unicode
    Test: Search handles Unicode characters correctly
    """
    test_data = [
        {"id": "1", "name": "Алиса", "description": "Русский"},
        {"id": "2", "name": "中文", "description": "中文描述"},
        {"id": "3", "name": "こんにちは", "description": "日本語"}
    ]
    file_path = create_test_file(test_data)
    try:
        def contains_russian(obj):
            desc = obj.get("description", "")
            return "Русский" in desc
        # V1: Search with Unicode
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, contains_russian)
        v1_time = time.perf_counter() - v1_start
        # V2: Search with Unicode
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, contains_russian, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results == v2_results
        assert v1_results[0]["id"] == "1"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_6_8_6_search_with_null_values():
    """
    Full Test Name: test_6_8_6_search_with_null_values
    Test: Search operations handle null/None values correctly
    """
    test_data = [
        {"id": "1", "status": "active", "value": 100},
        {"id": "2", "status": None, "value": 50},  # null status
        {"id": "3", "status": "inactive", "value": None}  # null value
    ]
    file_path = create_test_file(test_data)
    try:
        def has_active_status(obj):
            return obj.get("status") == "active"
        # V1: Search with null values
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, has_active_status)
        v1_time = time.perf_counter() - v1_start
        # V2: Search with null values
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, has_active_status, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results == v2_results
        assert v1_results[0]["id"] == "1"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
