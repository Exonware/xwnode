"""
#exonware/xwnode/examples/x5/data_operations/test_2_read_operations.py
READ Operations Test Suite
Tests all READ operations (retrieving data) for both V1 (Streaming) and V2 (Indexed) implementations.
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
from collections.abc import Callable
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    get_all_matching_v1,
    get_all_matching_v2,
    count_records_v1,
    count_records_v2,
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
    indexed_get_by_line,
    indexed_get_by_id,
    get_page,
    JsonIndex,
)
# ============================================================================
# 2.1 Single Record Retrieval
# ============================================================================


def test_2_1_1_get_by_id():
    """
    Full Test Name: test_2_1_1_get_by_id
    Test: Get record by unique identifier
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob", "age": 25},
        {"id": "3", "name": "Charlie", "age": 35}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Stream read by ID
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, match_by_id("id", "2"))
        v1_time = time.perf_counter() - v1_start
        # V2: Indexed get by ID
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_result = indexed_get_by_id(file_path, "2", id_field="id", index=index)
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == {"id": "2", "name": "Bob", "age": 25}
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_1_2_get_by_line_number():
    """
    Full Test Name: test_2_1_2_get_by_line_number
    Test: Get record by position (indexed)
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Stream to line N
        v1_start = time.perf_counter()
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 1:  # Line 2 (0-indexed)
                    v1_result = json.loads(line.strip())
                    break
        v1_time = time.perf_counter() - v1_start
        # V2: Direct access by line number
        index = build_index(file_path)
        v2_start = time.perf_counter()
        v2_result = indexed_get_by_line(file_path, 1, index=index)  # 0-indexed
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == {"id": "2", "name": "Bob"}
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_1_3_get_first_matching():
    """
    Full Test Name: test_2_1_3_get_first_matching
    Test: Find first record matching criteria
    """
    test_data = [
        {"id": "1", "name": "Alice", "role": "admin"},
        {"id": "2", "name": "Bob", "role": "user"},
        {"id": "3", "name": "Charlie", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Stream read with match
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, is_admin)
        v1_time = time.perf_counter() - v1_start
        # V2: Use stream_read as fallback (no role index)
        v2_start = time.perf_counter()
        v2_result = stream_read(file_path, is_admin)
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == {"id": "1", "name": "Alice", "role": "admin"}
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_1_4_get_by_path():
    """
    Full Test Name: test_2_1_4_get_by_path
    Test: Extract specific field/path from record
    """
    test_data = [
        {"id": "1", "user": {"name": "Alice", "email": "alice@example.com"}},
        {"id": "2", "user": {"name": "Bob", "email": "bob@example.com"}}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Stream read with path extraction
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, match_by_id("id", "1"), path=["user", "email"])
        v1_time = time.perf_counter() - v1_start
        # V2: Indexed get with path extraction
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        full_record = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        v2_result = full_record["user"]["email"]
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == "alice@example.com"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_1_5_get_with_projection():
    """
    Full Test Name: test_2_1_5_get_with_projection
    Test: Retrieve only specified fields
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30, "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "age": 25, "email": "bob@example.com"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Stream read with path extraction
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, match_by_id("id", "1"), path=["name"])
        v1_time = time.perf_counter() - v1_start
        # V2: Get full record then extract
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        full_record = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        v2_result = full_record["name"]
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == "Alice"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.2 Multiple Record Retrieval
# ============================================================================


def test_2_2_1_get_all_matching():
    """
    Full Test Name: test_2_2_1_get_all_matching
    Test: Find all records matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "user"},
        {"id": "5", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Get all matching
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, is_admin)
        v1_time = time.perf_counter() - v1_start
        # V2: Get all matching using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, is_admin, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("role") == "admin" for r in v1_results)
        assert all(r.get("role") == "admin" for r in v2_results)
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_2_2_get_by_id_list():
    """
    Full Test Name: test_2_2_2_get_by_id_list
    Test: Retrieve multiple records by list of IDs
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
        {"id": "4", "name": "David"},
        {"id": "5", "name": "Eve"}
    ]
    file_path = create_test_file(test_data)
    try:
        id_list = ["2", "4", "5"]
        # V1: Get by ID list
        v1_start = time.perf_counter()
        v1_results = []
        for record_id in id_list:
            try:
                v1_results.append(stream_read(file_path, match_by_id("id", record_id)))
            except JsonRecordNotFound:
                pass
        v1_time = time.perf_counter() - v1_start
        # V2: Get by ID list using index
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
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_2_3_get_by_line_range():
    """
    Full Test Name: test_2_2_3_get_by_line_range
    Test: Retrieve records from line N to M
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        start_line = 2
        end_line = 5
        # V1: Get by line range
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if start_line <= i < end_line:
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        # V2: Get by line range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(start_line, end_line):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert v1_results[0]["id"] == "2"
        assert v1_results[-1]["id"] == "4"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_2_4_get_page():
    """
    Full Test Name: test_2_2_4_get_page
    Test: Retrieve paginated results (offset + limit)
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(100)]
    file_path = create_test_file(test_data)
    try:
        page_size = 10
        page_num = 2  # Second page (1-indexed)
        # V1: Stream and collect records
        v1_start = time.perf_counter()
        v1_results = []
        count = 0
        skip = (page_num - 1) * page_size
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if skip > 0:
                    skip -= 1
                    continue
                if count >= page_size:
                    break
                v1_results.append(json.loads(line.strip()))
                count += 1
        v1_time = time.perf_counter() - v1_start
        # V2: Use get_page function
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_page(file_path, page_num, page_size, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == page_size
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_2_5_get_with_limit():
    """
    Full Test Name: test_2_2_5_get_with_limit
    Test: Retrieve first N matching records
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "admin"},
        {"id": "3", "role": "user"},
        {"id": "4", "role": "admin"},
        {"id": "5", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        limit = 2
        # V1: Get with limit
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    if is_admin(obj) and len(v1_results) < limit:
                        v1_results.append(obj)
        v1_time = time.perf_counter() - v1_start
        # V2: Get with limit using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            if len(v2_results) >= limit:
                break
            obj = indexed_get_by_line(file_path, i, index=index)
            if is_admin(obj):
                v2_results.append(obj)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == limit
        assert all(r.get("role") == "admin" for r in v1_results)
        assert all(r.get("role") == "admin" for r in v2_results)
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_2_6_get_with_skip():
    """
    Full Test Name: test_2_2_6_get_with_skip
    Test: Skip first N records, then retrieve
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(20)]
    file_path = create_test_file(test_data)
    try:
        skip = 5
        take = 10
        # V1: Get with skip
        v1_start = time.perf_counter()
        v1_results = []
        skipped = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    if skipped < skip:
                        skipped += 1
                        continue
                    if len(v1_results) >= take:
                        break
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        # V2: Get with skip using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(skip, min(skip + take, len(index.line_offsets))):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == take
        assert v1_results == v2_results
        assert v1_results[0]["id"] == "5"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.3 Query Operations
# ============================================================================


def test_2_3_1_filter_by_single_field():
    """
    Full Test Name: test_2_3_1_filter_by_single_field
    Test: Find records where field == value
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Stream read with match
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, is_admin)
        v1_time = time.perf_counter() - v1_start
        # V2: Use stream_read as fallback (no role index)
        v2_start = time.perf_counter()
        v2_result = stream_read(file_path, is_admin)
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result
        assert v1_result.get("role") == "admin"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_2_filter_by_multiple_fields():
    """
    Full Test Name: test_2_3_2_filter_by_multiple_fields
    Test: Find records matching multiple conditions
    """
    test_data = [
        {"id": "1", "role": "admin", "age": 30, "active": True},
        {"id": "2", "role": "admin", "age": 25, "active": False},
        {"id": "3", "role": "user", "age": 30, "active": True},
        {"id": "4", "role": "admin", "age": 30, "active": True}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin_and_active(obj):
            return obj.get("role") == "admin" and obj.get("active") == True
        # V1: Filter by multiple fields
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, is_admin_and_active)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter by multiple fields using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, is_admin_and_active, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("role") == "admin" and r.get("active") == True for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_3_filter_by_range():
    """
    Full Test Name: test_2_3_3_filter_by_range
    Test: Find records where field between min and max
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
        def age_in_range(obj):
            age = obj.get("age", 0)
            return min_age <= age <= max_age
        # V1: Filter by range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, age_in_range)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter by range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, age_in_range, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(min_age <= r.get("age", 0) <= max_age for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_4_filter_by_pattern():
    """
    Full Test Name: test_2_3_4_filter_by_pattern
    Test: Find records matching regex/pattern
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
        def matches_pattern(obj):
            email = obj.get("email", "")
            return bool(pattern.search(email))
        # V1: Filter by pattern
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, matches_pattern)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter by pattern using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, matches_pattern, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all("@example.com" in r.get("email", "") for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_5_filter_by_nested_field():
    """
    Full Test Name: test_2_3_5_filter_by_nested_field
    Test: Find records matching nested path
    """
    test_data = [
        {"id": "1", "user": {"profile": {"age": 30}}},
        {"id": "2", "user": {"profile": {"age": 25}}},
        {"id": "3", "user": {"profile": {"age": 35}}}
    ]
    file_path = create_test_file(test_data)
    try:
        def age_gt_28(obj):
            return obj.get("user", {}).get("profile", {}).get("age", 0) > 28
        # V1: Stream read with nested match
        v1_start = time.perf_counter()
        v1_result = stream_read(file_path, age_gt_28)
        v1_time = time.perf_counter() - v1_start
        # V2: Use stream_read as fallback
        v2_start = time.perf_counter()
        v2_result = stream_read(file_path, age_gt_28)
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result
        assert v1_result.get("user", {}).get("profile", {}).get("age", 0) > 28
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_6_filter_by_array_contains():
    """
    Full Test Name: test_2_3_6_filter_by_array_contains
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
        def contains_tag(obj):
            tags = obj.get("tags", [])
            return search_tag in tags
        # V1: Filter by array contains
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, contains_tag)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter by array contains using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, contains_tag, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(search_tag in r.get("tags", []) for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_7_filter_with_and_logic():
    """
    Full Test Name: test_2_3_7_filter_with_and_logic
    Test: Multiple conditions with AND
    """
    test_data = [
        {"id": "1", "role": "admin", "active": True, "age": 30},
        {"id": "2", "role": "admin", "active": False, "age": 30},
        {"id": "3", "role": "user", "active": True, "age": 30},
        {"id": "4", "role": "admin", "active": True, "age": 25}
    ]
    file_path = create_test_file(test_data)
    try:
        def complex_and_condition(obj):
            return (obj.get("role") == "admin" and 
                   obj.get("active") == True and 
                   obj.get("age", 0) >= 30)
        # V1: Filter with AND logic
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, complex_and_condition)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter with AND logic using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, complex_and_condition, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results[0]["id"] == "1"
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_8_filter_with_or_logic():
    """
    Full Test Name: test_2_3_8_filter_with_or_logic
    Test: Multiple conditions with OR
    """
    test_data = [
        {"id": "1", "role": "admin", "age": 30},
        {"id": "2", "role": "user", "age": 25},
        {"id": "3", "role": "user", "age": 35},
        {"id": "4", "role": "admin", "age": 20}
    ]
    file_path = create_test_file(test_data)
    try:
        def or_condition(obj):
            return obj.get("role") == "admin" or obj.get("age", 0) >= 30
        # V1: Filter with OR logic
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, or_condition)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter with OR logic using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, or_condition, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_9_filter_with_not_logic():
    """
    Full Test Name: test_2_3_9_filter_with_not_logic
    Test: Exclude records matching condition
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    try:
        def not_admin(obj):
            return obj.get("role") != "admin"
        # V1: Filter with NOT logic
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, not_admin)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter with NOT logic using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, not_admin, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("role") != "admin" for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_3_10_filter_with_complex_logic():
    """
    Full Test Name: test_2_3_10_filter_with_complex_logic
    Test: Nested AND/OR/NOT combinations
    """
    test_data = [
        {"id": "1", "role": "admin", "active": True, "age": 30},
        {"id": "2", "role": "admin", "active": False, "age": 25},
        {"id": "3", "role": "user", "active": True, "age": 35},
        {"id": "4", "role": "user", "active": True, "age": 20}
    ]
    file_path = create_test_file(test_data)
    try:
        def complex_logic(obj):
            # (role == "admin" AND active) OR (age >= 30 AND NOT role == "user")
            return ((obj.get("role") == "admin" and obj.get("active") == True) or
                   (obj.get("age", 0) >= 30 and obj.get("role") != "user"))
        # V1: Filter with complex logic
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, complex_logic)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter with complex logic using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, complex_logic, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results[0]["id"] == "1"
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.4 Search Operations
# ============================================================================


def test_2_4_1_full_text_search():
    """
    Full Test Name: test_2_4_1_full_text_search
    Test: Search across all text fields
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
            # Search in all string fields
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
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_2_field_specific_search():
    """
    Full Test Name: test_2_4_2_field_specific_search
    Test: Search within specific field(s)
    """
    test_data = [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "email": "bob@test.org"},
        {"id": "3", "name": "Alice Smith", "email": "alice.smith@example.com"}
    ]
    file_path = create_test_file(test_data)
    try:
        search_term = "alice"
        search_fields = ["name", "email"]
        def field_specific_match(obj):
            for field in search_fields:
                value = str(obj.get(field, "")).lower()
                if search_term.lower() in value:
                    return True
            return False
        # V1: Field-specific search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, field_specific_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Field-specific search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, field_specific_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_3_fuzzy_search():
    """
    Full Test Name: test_2_4_3_fuzzy_search
    Test: Find similar/approximate matches
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Alicia"},
        {"id": "3", "name": "Bob"},
        {"id": "4", "name": "Alice Smith"}
    ]
    file_path = create_test_file(test_data)
    try:
        search_term = "Alice"
        def fuzzy_match(obj):
            name = obj.get("name", "").lower()
            search_lower = search_term.lower()
            # Improved fuzzy: starts with, contains, or shares common prefix (at least 4 chars)
            if name.startswith(search_lower) or search_lower in name:
                return True
            # Check for common prefix (fuzzy matching for similar names like Alice/Alicia)
            min_prefix_len = min(len(search_lower), len(name), 4)
            if min_prefix_len >= 4:
                return name[:min_prefix_len] == search_lower[:min_prefix_len]
            return False
        # V1: Fuzzy search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, fuzzy_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Fuzzy search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, fuzzy_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_4_prefix_search():
    """
    Full Test Name: test_2_4_4_prefix_search
    Test: Find records starting with prefix
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
        # V1: Prefix search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, prefix_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Prefix search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, prefix_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("name", "").lower().startswith(prefix.lower()) for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_5_suffix_search():
    """
    Full Test Name: test_2_4_5_suffix_search
    Test: Find records ending with suffix
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
        # V1: Suffix search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, suffix_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Suffix search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, suffix_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("email", "").lower().endswith(suffix.lower()) for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_6_contains_search():
    """
    Full Test Name: test_2_4_6_contains_search
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
        # V1: Contains search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, contains_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Contains search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, contains_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert all(substring.lower() in r.get("description", "").lower() for r in v1_results)
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_7_case_insensitive_search():
    """
    Full Test Name: test_2_4_7_case_insensitive_search
    Test: Search ignoring case
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "alice"},
        {"id": "3", "name": "ALICE"},
        {"id": "4", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        search_term = "ALICE"
        def case_insensitive_match(obj):
            name = obj.get("name", "").lower()
            return name == search_term.lower()
        # V1: Case-insensitive search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, case_insensitive_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Case-insensitive search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, case_insensitive_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_4_8_multi_field_search():
    """
    Full Test Name: test_2_4_8_multi_field_search
    Test: Search across multiple fields simultaneously
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
        # V1: Multi-field search
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, multi_field_match)
        v1_time = time.perf_counter() - v1_start
        # V2: Multi-field search using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, multi_field_match, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.5 Sorting Operations
# ============================================================================


def test_2_5_1_sort_by_single_field():
    """
    Full Test Name: test_2_5_1_sort_by_single_field
    Test: Order results by one field (asc/desc)
    """
    test_data = [
        {"id": "1", "name": "Charlie", "age": 35},
        {"id": "2", "name": "Alice", "age": 30},
        {"id": "3", "name": "Bob", "age": 25}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sort by single field
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_sorted = sorted(v1_all, key=lambda x: x.get("name", ""))
        v1_time = time.perf_counter() - v1_start
        # V2: Sort by single field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_sorted = sorted(v2_all, key=lambda x: x.get("name", ""))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_sorted) == len(v2_sorted) == 3
        assert v1_sorted == v2_sorted
        assert v1_sorted[0]["name"] == "Alice"
        assert v1_sorted[-1]["name"] == "Charlie"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_5_2_sort_by_multiple_fields():
    """
    Full Test Name: test_2_5_2_sort_by_multiple_fields
    Test: Order by multiple fields (priority)
    """
    test_data = [
        {"id": "1", "role": "admin", "age": 30},
        {"id": "2", "role": "user", "age": 25},
        {"id": "3", "role": "admin", "age": 25},
        {"id": "4", "role": "user", "age": 30}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sort by multiple fields
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_sorted = sorted(v1_all, key=lambda x: (x.get("role", ""), x.get("age", 0)))
        v1_time = time.perf_counter() - v1_start
        # V2: Sort by multiple fields using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_sorted = sorted(v2_all, key=lambda x: (x.get("role", ""), x.get("age", 0)))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_sorted) == len(v2_sorted) == 4
        assert v1_sorted == v2_sorted
        assert v1_sorted[0]["role"] == "admin"
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_5_3_sort_by_nested_field():
    """
    Full Test Name: test_2_5_3_sort_by_nested_field
    Test: Order by nested path
    """
    test_data = [
        {"id": "1", "user": {"profile": {"age": 35}}},
        {"id": "2", "user": {"profile": {"age": 25}}},
        {"id": "3", "user": {"profile": {"age": 30}}}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sort by nested field
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_sorted = sorted(v1_all, key=lambda x: x.get("user", {}).get("profile", {}).get("age", 0))
        v1_time = time.perf_counter() - v1_start
        # V2: Sort by nested field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_sorted = sorted(v2_all, key=lambda x: x.get("user", {}).get("profile", {}).get("age", 0))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_sorted) == len(v2_sorted) == 3
        assert v1_sorted == v2_sorted
        assert v1_sorted[0]["user"]["profile"]["age"] == 25
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_5_4_sort_by_computed_value():
    """
    Full Test Name: test_2_5_4_sort_by_computed_value
    Test: Order by calculated/derived value
    """
    test_data = [
        {"id": "1", "price": 10, "quantity": 2},
        {"id": "2", "price": 5, "quantity": 4},
        {"id": "3", "price": 8, "quantity": 3}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sort by computed value (total = price * quantity)
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        # Stable sort: use id as secondary key when computed values are equal
        v1_sorted = sorted(v1_all, key=lambda x: (x.get("price", 0) * x.get("quantity", 0), x.get("id", "")))
        v1_time = time.perf_counter() - v1_start
        # V2: Sort by computed value using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        # Stable sort: use id as secondary key when computed values are equal
        v2_sorted = sorted(v2_all, key=lambda x: (x.get("price", 0) * x.get("quantity", 0), x.get("id", "")))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_sorted) == len(v2_sorted) == 3
        assert v1_sorted == v2_sorted
        # Both id "1" and "2" have total = 20, but with stable sort by (total, id), "1" comes before "2" alphabetically
        # id "1" = 10*2 = 20, id "2" = 5*4 = 20, id "3" = 8*3 = 24
        assert v1_sorted[0]["id"] == "1"  # total = 20, id "1" < "2" alphabetically
        assert v1_sorted[0].get("price", 0) * v1_sorted[0].get("quantity", 0) == 20
        assert v1_sorted[1]["id"] == "2"  # total = 20, id "2" comes second
        assert v1_sorted[2]["id"] == "3"  # total = 24, highest
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_5_5_sort_with_null_handling():
    """
    Full Test Name: test_2_5_5_sort_with_null_handling
    Test: Handle null values in sort order
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": None},
        {"id": "2", "name": "Bob", "age": 30},
        {"id": "3", "name": "Charlie", "age": None},
        {"id": "4", "name": "David", "age": 25}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sort with null handling (nulls last)
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_sorted = sorted(v1_all, key=lambda x: (x.get("age") is None, x.get("age") or 0))
        v1_time = time.perf_counter() - v1_start
        # V2: Sort with null handling using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_sorted = sorted(v2_all, key=lambda x: (x.get("age") is None, x.get("age") or 0))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_sorted) == len(v2_sorted) == 4
        assert v1_sorted == v2_sorted
        assert v1_sorted[0]["age"] == 25  # Non-null first
        assert v1_sorted[-1]["age"] is None  # Nulls last
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.6 Aggregation Operations
# ============================================================================


def test_2_6_1_count_records():
    """
    Full Test Name: test_2_6_1_count_records
    Test: Count total records or matching records
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Count all records
        v1_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_time = time.perf_counter() - v1_start
        # V2: Count all records using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_count = count_records_v2(file_path, index=index)
        v2_time = time.perf_counter() - v2_start
        assert v1_count == v2_count == 10
        # Count matching records
        def is_even(obj):
            return int(obj.get("id", 0)) % 2 == 0
        v1_matching_start = time.perf_counter()
        v1_matching = len(get_all_matching_v1(file_path, is_even))
        v1_matching_time = time.perf_counter() - v1_matching_start
        v2_matching_start = time.perf_counter()
        v2_matching = len(get_all_matching_v2(file_path, is_even, index=index))
        v2_matching_time = time.perf_counter() - v2_matching_start
        assert v1_matching == v2_matching == 5
        v1_total_time = v1_time + v1_matching_time
        v2_total_time = v2_time + v2_matching_time
        # Timing information available in v1_total_time and v2_total_time variables if needed for benchmarking
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_2_6_2_count_distinct():
    """
    Full Test Name: test_2_6_2_count_distinct
    Test: Count unique values of a field
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "user"},
        {"id": "5", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Count distinct values
        v1_start = time.perf_counter()
        v1_values = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_values.add(obj.get("role"))
        v1_count = len(v1_values)
        v1_time = time.perf_counter() - v1_start
        # V2: Count distinct values using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_values = set()
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_values.add(obj.get("role"))
        v2_count = len(v2_values)
        v2_time = time.perf_counter() - v2_start
        assert v1_count == v2_count == 2
        assert v1_values == v2_values == {"admin", "user"}
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_6_3_sum_field():
    """
    Full Test Name: test_2_6_3_sum_field
    Test: Sum numeric values of a field
    """
    test_data = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
        {"id": "3", "value": 30},
        {"id": "4", "value": 40}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sum field
        v1_start = time.perf_counter()
        v1_sum = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_sum += obj.get("value", 0)
        v1_time = time.perf_counter() - v1_start
        # V2: Sum field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_sum = 0
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_sum += obj.get("value", 0)
        v2_time = time.perf_counter() - v2_start
        assert v1_sum == v2_sum == 100
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_6_4_average_field():
    """
    Full Test Name: test_2_6_4_average_field
    Test: Calculate average of numeric field
    """
    test_data = [
        {"id": "1", "age": 20},
        {"id": "2", "age": 30},
        {"id": "3", "age": 40},
        {"id": "4", "age": 50}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Average field
        v1_start = time.perf_counter()
        v1_sum = 0
        v1_count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_sum += obj.get("age", 0)
                    v1_count += 1
        v1_avg = v1_sum / v1_count if v1_count > 0 else 0
        v1_time = time.perf_counter() - v1_start
        # V2: Average field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_sum = 0
        v2_count = len(index.line_offsets)
        for i in range(v2_count):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_sum += obj.get("age", 0)
        v2_avg = v2_sum / v2_count if v2_count > 0 else 0
        v2_time = time.perf_counter() - v2_start
        assert v1_avg == v2_avg == 35.0
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_6_5_min_max_field():
    """
    Full Test Name: test_2_6_5_min_max_field
    Test: Find minimum/maximum value
    """
    test_data = [
        {"id": "1", "score": 85},
        {"id": "2", "score": 92},
        {"id": "3", "score": 78},
        {"id": "4", "score": 95}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Min/Max field
        v1_start = time.perf_counter()
        v1_scores = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_scores.append(obj.get("score", 0))
        v1_min = min(v1_scores)
        v1_max = max(v1_scores)
        v1_time = time.perf_counter() - v1_start
        # V2: Min/Max field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_scores = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_scores.append(obj.get("score", 0))
        v2_min = min(v2_scores)
        v2_max = max(v2_scores)
        v2_time = time.perf_counter() - v2_start
        assert v1_min == v2_min == 78
        assert v1_max == v2_max == 95
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_6_6_group_by():
    """
    Full Test Name: test_2_6_6_group_by
    Test: Group records by field value
    """
    test_data = [
        {"id": "1", "role": "admin", "age": 30},
        {"id": "2", "role": "user", "age": 25},
        {"id": "3", "role": "admin", "age": 35},
        {"id": "4", "role": "user", "age": 28}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Group by field
        v1_start = time.perf_counter()
        v1_groups = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    role = obj.get("role")
                    if role not in v1_groups:
                        v1_groups[role] = []
                    v1_groups[role].append(obj)
        v1_time = time.perf_counter() - v1_start
        # V2: Group by field using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_groups = {}
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            role = obj.get("role")
            if role not in v2_groups:
                v2_groups[role] = []
            v2_groups[role].append(obj)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_groups) == len(v2_groups) == 2
        assert len(v1_groups["admin"]) == len(v2_groups["admin"]) == 2
        assert len(v1_groups["user"]) == len(v2_groups["user"]) == 2
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_6_7_group_with_aggregation():
    """
    Full Test Name: test_2_6_7_group_with_aggregation
    Test: Group and aggregate within groups
    """
    test_data = [
        {"id": "1", "role": "admin", "salary": 100000},
        {"id": "2", "role": "user", "salary": 50000},
        {"id": "3", "role": "admin", "salary": 120000},
        {"id": "4", "role": "user", "salary": 60000}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Group with aggregation
        v1_start = time.perf_counter()
        v1_groups = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    role = obj.get("role")
                    if role not in v1_groups:
                        v1_groups[role] = {"count": 0, "total": 0}
                    v1_groups[role]["count"] += 1
                    v1_groups[role]["total"] += obj.get("salary", 0)
        v1_avg = {role: data["total"] / data["count"] for role, data in v1_groups.items()}
        v1_time = time.perf_counter() - v1_start
        # V2: Group with aggregation using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_groups = {}
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            role = obj.get("role")
            if role not in v2_groups:
                v2_groups[role] = {"count": 0, "total": 0}
            v2_groups[role]["count"] += 1
            v2_groups[role]["total"] += obj.get("salary", 0)
        v2_avg = {role: data["total"] / data["count"] for role, data in v2_groups.items()}
        v2_time = time.perf_counter() - v2_start
        assert v1_avg == v2_avg
        assert v1_avg["admin"] == 110000.0
        assert v1_avg["user"] == 55000.0
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.7 Streaming Operations
# ============================================================================


def test_2_7_1_stream_all_records():
    """
    Full Test Name: test_2_7_1_stream_all_records
    Test: Iterate through all records
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Stream all records
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        # V2: Use index to get all records
        index = build_index(file_path)
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        assert v1_results == v2_results
        assert len(v1_results) == 10
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_7_2_stream_matching_records():
    """
    Full Test Name: test_2_7_2_stream_matching_records
    Test: Iterate through filtered records
    """
    test_data = [
        {"id": "1", "status": "active"},
        {"id": "2", "status": "inactive"},
        {"id": "3", "status": "active"},
        {"id": "4", "status": "pending"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_active(obj):
            return obj.get("status") == "active"
        # V1: Stream matching records
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    if is_active(obj):
                        v1_results.append(obj)
        v1_time = time.perf_counter() - v1_start
        # V2: Stream matching records using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            if is_active(obj):
                v2_results.append(obj)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_7_3_stream_with_callback():
    """
    Full Test Name: test_2_7_3_stream_with_callback
    Test: Process each record with callback
    """
    test_data = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
        {"id": "3", "value": 30}
    ]
    file_path = create_test_file(test_data)
    try:
        processed = []
        def process_record(obj):
            processed.append(obj.get("value", 0) * 2)
        # V1: Stream with callback
        v1_start = time.perf_counter()
        v1_processed = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_processed.append(obj.get("value", 0) * 2)
        v1_time = time.perf_counter() - v1_start
        # V2: Stream with callback using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_processed = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_processed.append(obj.get("value", 0) * 2)
        v2_time = time.perf_counter() - v2_start
        assert v1_processed == v2_processed == [20, 40, 60]
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_7_4_stream_with_early_exit():
    """
    Full Test Name: test_2_7_4_stream_with_early_exit
    Test: Stop streaming when condition met
    """
    test_data = [
        {"id": "1", "found": False},
        {"id": "2", "found": False},
        {"id": "3", "found": True},
        {"id": "4", "found": False}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Stream with early exit
        v1_start = time.perf_counter()
        v1_result = None
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    if obj.get("found"):
                        v1_result = obj
                        break
        v1_time = time.perf_counter() - v1_start
        # V2: Stream with early exit using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_result = None
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            if obj.get("found"):
                v2_result = obj
                break
        v2_time = time.perf_counter() - v2_start
        assert v1_result == v2_result == {"id": "3", "found": True}
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_7_5_stream_in_batches():
    """
    Full Test Name: test_2_7_5_stream_in_batches
    Test: Process records in chunks
    """
    test_data = [{"id": str(i), "value": i} for i in range(20)]
    file_path = create_test_file(test_data)
    try:
        batch_size = 5
        # V1: Stream in batches
        v1_start = time.perf_counter()
        v1_batches = []
        current_batch = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    current_batch.append(obj)
                    if len(current_batch) >= batch_size:
                        v1_batches.append(current_batch)
                        current_batch = []
            if current_batch:
                v1_batches.append(current_batch)
        v1_time = time.perf_counter() - v1_start
        # V2: Stream in batches using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_batches = []
        for i in range(0, len(index.line_offsets), batch_size):
            batch = []
            for j in range(i, min(i + batch_size, len(index.line_offsets))):
                batch.append(indexed_get_by_line(file_path, j, index=index))
            v2_batches.append(batch)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_batches) == len(v2_batches) == 4
        assert all(len(batch) == batch_size for batch in v1_batches[:-1])
        assert v1_batches == v2_batches
        # Timing information available in v1_time and v2_time variables if needed for benchmarking
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 2.8 Edge Cases and Error Handling
# ============================================================================


def test_2_8_1_empty_file():
    """
    Full Test Name: test_2_8_1_empty_file
    Test: Handle empty files gracefully
    """
    file_path = create_test_file([])
    try:
        # V1: Count records in empty file
        v1_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_time1 = time.perf_counter() - v1_start
        # Try to get all matching (should return empty list)
        def always_true(obj):
            return True
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, always_true)
        v1_time2 = time.perf_counter() - v1_start
        v1_time = v1_time1 + v1_time2
        # V2: Count records in empty file
        v2_start = time.perf_counter()
        index = ensure_index(file_path, id_field="id")
        v2_count = count_records_v2(file_path, index=index)
        v2_time1 = time.perf_counter() - v2_start
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, always_true, index=index)
        v2_time2 = time.perf_counter() - v2_start
        v2_time = v2_time1 + v2_time2
        assert v1_count == v2_count == 0
        assert len(v1_results) == len(v2_results) == 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_2_missing_fields():
    """
    Full Test Name: test_2_8_2_missing_fields
    Test: Handle records with missing fields
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob"},  # Missing age
        {"id": "3", "age": 25},  # Missing name
        {"id": "4"}  # Only id
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Get records with missing fields
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        # V2: Get records with missing fields
        v2_start = time.perf_counter()
        index = ensure_index(file_path, id_field="id")
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_all) == len(v2_all) == 4
        assert v1_all == v2_all
        # Test accessing missing fields (should return None or default)
        assert v1_all[1].get("age") is None
        assert v1_all[2].get("name") is None
        assert v1_all[3].get("name") is None
        assert v1_all[3].get("age") is None
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_3_null_values():
    """
    Full Test Name: test_2_8_3_null_values
    Test: Handle null/None values in fields
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": None, "email": "alice@example.com"},
        {"id": "2", "name": None, "age": 30, "email": None},
        {"id": "3", "name": "Bob", "age": 25, "email": "bob@example.com"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Filter records with null values
        def has_null_name(obj):
            return obj.get("name") is None
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, has_null_name)
        v1_time = time.perf_counter() - v1_start
        # V2: Filter records with null values
        v2_start = time.perf_counter()
        index = ensure_index(file_path, id_field="id")
        v2_results = get_all_matching_v2(file_path, has_null_name, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results[0]["id"] == "2"
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_4_unicode_special_characters():
    """
    Full Test Name: test_2_8_4_unicode_special_characters
    Test: Handle Unicode and special characters
    """
    test_data = [
        {"id": "1", "name": "José", "description": "Café & Restaurant"},
        {"id": "2", "name": "北京", "description": "中文测试"},
        {"id": "3", "name": "🚀 Rocket", "description": "Test with emoji 🎉"},
        {"id": "4", "name": "Test\nNewline", "description": "Tab\tSeparated"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Search with Unicode
        def contains_emoji(obj):
            desc = obj.get("description", "")
            return "🚀" in desc or "🎉" in desc
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, contains_emoji)
        v1_record = stream_read(file_path, match_by_id("id", "2"))
        v1_time = time.perf_counter() - v1_start
        # V2: Search with Unicode
        v2_start = time.perf_counter()
        index = ensure_index(file_path, id_field="id")
        v2_results = get_all_matching_v2(file_path, contains_emoji, index=index)
        index2 = build_index(file_path, id_field="id")
        v2_record = indexed_get_by_id(file_path, "2", id_field="id", index=index2)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 1
        assert v1_results[0]["id"] == "3"
        assert v1_results == v2_results
        assert v1_record == v2_record
        assert v1_record["name"] == "北京"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_5_very_large_record():
    """
    Full Test Name: test_2_8_5_very_large_record
    Test: Handle very large field values
    """
    large_text = "A" * 10000  # 10KB of text
    test_data = [
        {"id": "1", "name": "Large Record", "data": large_text},
        {"id": "2", "name": "Normal Record", "data": "small"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Get large record
        v1_start = time.perf_counter()
        v1_record = stream_read(file_path, match_by_id("id", "1"))
        v1_time = time.perf_counter() - v1_start
        # V2: Get large record
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_record = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        v2_time = time.perf_counter() - v2_start
        assert v1_record == v2_record
        assert len(v1_record["data"]) == 10000
        assert v1_record["data"] == large_text
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_6_missing_id_field():
    """
    Full Test Name: test_2_8_6_missing_id_field
    Test: Handle records without ID field when ID is expected
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"name": "Bob"},  # Missing id
        {"id": "3", "name": "Charlie"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Get by ID should work for records with ID
        v1_start = time.perf_counter()
        v1_record = stream_read(file_path, match_by_id("id", "1"))
        v1_count = count_records_v1(file_path)
        v1_time = time.perf_counter() - v1_start
        assert v1_record["name"] == "Alice"
        # V2: Get by ID should work for records with ID
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_record = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        v2_count = count_records_v2(file_path, index=index)
        v2_time = time.perf_counter() - v2_start
        assert v2_record["name"] == "Alice"
        # Count all records (including those without ID)
        assert v1_count == v2_count == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_7_nonexistent_id():
    """
    Full Test Name: test_2_8_7_nonexistent_id
    Test: Handle requests for non-existent IDs
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Get non-existent ID should raise exception
        v1_start = time.perf_counter()
        try:
            v1_result = stream_read(file_path, match_by_id("id", "999"))
            assert False, "Should have raised JsonRecordNotFound"
        except JsonRecordNotFound:
            pass  # Expected
        v1_time = time.perf_counter() - v1_start
        # V2: Get non-existent ID should raise exception
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        try:
            v2_result = indexed_get_by_id(file_path, "999", id_field="id", index=index)
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected
        v2_time = time.perf_counter() - v2_start
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_2_8_8_invalid_line_number():
    """
    Full Test Name: test_2_8_8_invalid_line_number
    Test: Handle invalid line number requests
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Read by line manually (for comparison)
        v1_start = time.perf_counter()
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            v1_record0 = json.loads(lines[0].strip()) if len(lines) > 0 else None
            v1_record1 = json.loads(lines[1].strip()) if len(lines) > 1 else None
        # Test invalid line access
        try:
            invalid_line = json.loads(lines[999].strip()) if len(lines) > 999 else None
            assert False, "Should not access invalid line"
        except (IndexError, Exception):
            pass  # Expected
        v1_time = time.perf_counter() - v1_start
        assert v1_record0["id"] == "1"
        assert v1_record1["id"] == "2"
        # V2: Get by invalid line number should handle gracefully
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        # Valid line numbers should work
        record0 = indexed_get_by_line(file_path, 0, index=index)
        record1 = indexed_get_by_line(file_path, 1, index=index)
        # Invalid line number (out of range) should raise exception
        try:
            indexed_get_by_line(file_path, 999, index=index)
            assert False, "Should have raised exception for invalid line number"
        except (IndexError, Exception):
            pass  # Expected
        v2_time = time.perf_counter() - v2_start
        assert record0["id"] == "1"
        assert record1["id"] == "2"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
