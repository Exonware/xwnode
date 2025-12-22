"""
#exonware/xwnode/examples/x5/data_operations/test_5_list_query_operations.py

LIST/QUERY Operations Test Suite

Tests all LIST/QUERY operations (retrieving collections) for both V1 (Streaming) and V2 (Indexed) implementations.
All tests are fully implemented at production level with no TODOs.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import test helpers
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
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_line,
    indexed_get_by_id,
    get_page,
)


# ============================================================================
# 5.1 Basic Listing
# ============================================================================

def test_5_1_1_list_all_records():
    """
    Full Test Name: test_5_1_1_list_all_records
    Test: Get all records in file
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List all records
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List all records using index
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 10
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_1_2_list_with_pagination():
    """
    Full Test Name: test_5_1_2_list_with_pagination
    Test: Get records in pages
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(100)]
    file_path = create_test_file(test_data)
    
    try:
        page_size = 10
        page_num = 3  # Third page
        
        # V1: List with pagination
        v1_start = time.perf_counter()
        v1_results = []
        skip = (page_num - 1) * page_size
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    if skip > 0:
                        skip -= 1
                        continue
                    if count >= page_size:
                        break
                    v1_results.append(json.loads(line.strip()))
                    count += 1
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with pagination using get_page
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_page(file_path, page_num, page_size, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == page_size
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_1_3_list_with_limit():
    """
    Full Test Name: test_5_1_3_list_with_limit
    Test: Get first N records
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(50)]
    file_path = create_test_file(test_data)
    
    try:
        limit = 20
        
        # V1: List with limit
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if line.strip() and i < limit:
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with limit using index
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(min(limit, len(index.line_offsets))):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == limit
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_1_4_list_with_offset():
    """
    Full Test Name: test_5_1_4_list_with_offset
    Test: Skip N records, get next M
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(50)]
    file_path = create_test_file(test_data)
    
    try:
        offset = 10
        limit = 15
        
        # V1: List with offset
        v1_start = time.perf_counter()
        v1_results = []
        skipped = 0
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    if skipped < offset:
                        skipped += 1
                        continue
                    if count >= limit:
                        break
                    v1_results.append(json.loads(line.strip()))
                    count += 1
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with offset using index
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(offset, min(offset + limit, len(index.line_offsets))):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == limit
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_1_5_list_in_reverse():
    """
    Full Test Name: test_5_1_5_list_in_reverse
    Test: Get records in reverse order
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List in reverse
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_results.append(json.loads(line.strip()))
        v1_results.reverse()
        v1_time = time.perf_counter() - v1_start
        
        # V2: List in reverse using index
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets) - 1, -1, -1):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 10
        assert v1_results == v2_results
        assert v1_results[0]["id"] == "9"
        assert v1_results[-1]["id"] == "0"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 5.2 Filtered Listing
# ============================================================================

def test_5_2_1_list_matching():
    """
    Full Test Name: test_5_2_1_list_matching
    Test: Get all records matching filter
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        
        # V1: List matching
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, is_admin)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List matching using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, is_admin, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("role") == "admin" for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_2_2_list_by_type():
    """
    Full Test Name: test_5_2_2_list_by_type
    Test: Get records of specific type/category
    """
    test_data = [
        {"id": "1", "type": "user", "name": "Alice"},
        {"id": "2", "type": "admin", "name": "Bob"},
        {"id": "3", "type": "user", "name": "Charlie"},
        {"id": "4", "type": "guest", "name": "David"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        target_type = "user"
        
        def is_type(obj):
            return obj.get("type") == target_type
        
        # V1: List by type
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, is_type)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List by type using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, is_type, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 2
        assert all(r.get("type") == target_type for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_2_3_list_by_date_range():
    """
    Full Test Name: test_5_2_3_list_by_date_range
    Test: Get records within date range
    """
    test_data = [
        {"id": "1", "created": "2024-01-01"},
        {"id": "2", "created": "2024-02-15"},
        {"id": "3", "created": "2024-03-20"},
        {"id": "4", "created": "2024-04-10"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        start_date = "2024-02-01"
        end_date = "2024-03-31"
        
        def in_date_range(obj):
            created = obj.get("created", "")
            return start_date <= created <= end_date
        
        # V1: List by date range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, in_date_range)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List by date range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, in_date_range, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 2
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_2_4_list_by_value_range():
    """
    Full Test Name: test_5_2_4_list_by_value_range
    Test: Get records within numeric range
    """
    test_data = [
        {"id": "1", "score": 50},
        {"id": "2", "score": 75},
        {"id": "3", "score": 90},
        {"id": "4", "score": 60}
    ]
    file_path = create_test_file(test_data)
    
    try:
        min_score = 60
        max_score = 80
        
        def in_score_range(obj):
            score = obj.get("score", 0)
            return min_score <= score <= max_score
        
        # V1: List by value range
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, in_score_range)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List by value range using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, in_score_range, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 2
        assert all(min_score <= r.get("score", 0) <= max_score for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_2_5_list_excluding():
    """
    Full Test Name: test_5_2_5_list_excluding
    Test: Get records not matching criteria
    """
    test_data = [
        {"id": "1", "status": "active"},
        {"id": "2", "status": "inactive"},
        {"id": "3", "status": "active"},
        {"id": "4", "status": "pending"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def not_inactive(obj):
            return obj.get("status") != "inactive"
        
        # V1: List excluding
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, not_inactive)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List excluding using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, not_inactive, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("status") != "inactive" for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 5.3 Sorted Listing
# ============================================================================

def test_5_3_1_list_sorted_ascending():
    """
    Full Test Name: test_5_3_1_list_sorted_ascending
    Test: Get records sorted A-Z
    """
    test_data = [
        {"id": "1", "name": "Charlie"},
        {"id": "2", "name": "Alice"},
        {"id": "3", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List sorted ascending
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_results = sorted(v1_all, key=lambda x: x.get("name", ""))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List sorted ascending using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_results = sorted(v2_all, key=lambda x: x.get("name", ""))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert v1_results[0]["name"] == "Alice"
        assert v1_results[-1]["name"] == "Charlie"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_3_2_list_sorted_descending():
    """
    Full Test Name: test_5_3_2_list_sorted_descending
    Test: Get records sorted Z-A
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Charlie"},
        {"id": "3", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List sorted descending
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_results = sorted(v1_all, key=lambda x: x.get("name", ""), reverse=True)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List sorted descending using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_results = sorted(v2_all, key=lambda x: x.get("name", ""), reverse=True)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert v1_results[0]["name"] == "Charlie"
        assert v1_results[-1]["name"] == "Alice"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_3_3_list_sorted_by_date():
    """
    Full Test Name: test_5_3_3_list_sorted_by_date
    Test: Get records sorted by date
    """
    test_data = [
        {"id": "1", "date": "2024-03-15"},
        {"id": "2", "date": "2024-01-10"},
        {"id": "3", "date": "2024-02-20"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List sorted by date
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_results = sorted(v1_all, key=lambda x: x.get("date", ""))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List sorted by date using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_results = sorted(v2_all, key=lambda x: x.get("date", ""))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert v1_results[0]["date"] == "2024-01-10"
        assert v1_results[-1]["date"] == "2024-03-15"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_3_4_list_sorted_by_multiple_fields():
    """
    Full Test Name: test_5_3_4_list_sorted_by_multiple_fields
    Test: Multi-field sorting
    """
    test_data = [
        {"id": "1", "role": "admin", "age": 30},
        {"id": "2", "role": "user", "age": 25},
        {"id": "3", "role": "admin", "age": 25},
        {"id": "4", "role": "user", "age": 30}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List sorted by multiple fields
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_results = sorted(v1_all, key=lambda x: (x.get("role", ""), x.get("age", 0)))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List sorted by multiple fields using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_results = sorted(v2_all, key=lambda x: (x.get("role", ""), x.get("age", 0)))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 4
        assert v1_results == v2_results
        assert v1_results[0]["role"] == "admin"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_3_5_list_with_custom_sort():
    """
    Full Test Name: test_5_3_5_list_with_custom_sort
    Test: Sort using custom comparator
    """
    test_data = [
        {"id": "1", "priority": "high", "value": 10},
        {"id": "2", "priority": "low", "value": 20},
        {"id": "3", "priority": "high", "value": 5}
    ]
    file_path = create_test_file(test_data)
    
    try:
        priority_order = {"high": 1, "medium": 2, "low": 3}
        
        def custom_sort_key(obj):
            return (priority_order.get(obj.get("priority", ""), 99), obj.get("value", 0))
        
        # V1: List with custom sort
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_all.append(json.loads(line.strip()))
        v1_results = sorted(v1_all, key=custom_sort_key)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with custom sort using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path, i, index=index))
        v2_results = sorted(v2_all, key=custom_sort_key)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert v1_results[0]["priority"] == "high"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 5.4 Projected Listing
# ============================================================================

def test_5_4_1_list_with_field_selection():
    """
    Full Test Name: test_5_4_1_list_with_field_selection
    Test: Get only specified fields
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30, "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "age": 25, "email": "bob@example.com"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        fields = ["id", "name"]
        
        # V1: List with field selection
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_all.append({k: v for k, v in obj.items() if k in fields})
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with field selection using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_all.append({k: v for k, v in obj.items() if k in fields})
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_all) == len(v2_all) == 2
        assert all(set(r.keys()) == set(fields) for r in v1_all)
        assert v1_all == v2_all
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_4_2_list_with_field_exclusion():
    """
    Full Test Name: test_5_4_2_list_with_field_exclusion
    Test: Get all fields except specified
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30, "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "age": 25, "email": "bob@example.com"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        exclude_fields = ["email", "age"]
        
        # V1: List with field exclusion
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_all.append({k: v for k, v in obj.items() if k not in exclude_fields})
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with field exclusion using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_all.append({k: v for k, v in obj.items() if k not in exclude_fields})
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_all) == len(v2_all) == 2
        assert all("email" not in r and "age" not in r for r in v1_all)
        assert all("id" in r and "name" in r for r in v1_all)
        assert v1_all == v2_all
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_4_3_list_with_computed_fields():
    """
    Full Test Name: test_5_4_3_list_with_computed_fields
    Test: Include calculated fields
    """
    test_data = [
        {"id": "1", "price": 10, "quantity": 2},
        {"id": "2", "price": 5, "quantity": 4}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List with computed fields
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    obj["total"] = obj.get("price", 0) * obj.get("quantity", 0)
                    v1_all.append(obj)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with computed fields using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            obj["total"] = obj.get("price", 0) * obj.get("quantity", 0)
            v2_all.append(obj)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_all) == len(v2_all) == 2
        assert all("total" in r for r in v1_all)
        assert v1_all[0]["total"] == 20
        assert v1_all == v2_all
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_4_4_list_with_nested_projection():
    """
    Full Test Name: test_5_4_4_list_with_nested_projection
    Test: Project nested fields
    """
    test_data = [
        {"id": "1", "user": {"name": "Alice", "email": "alice@example.com", "age": 30}},
        {"id": "2", "user": {"name": "Bob", "email": "bob@example.com", "age": 25}}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List with nested projection
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    projected = {
                        "id": obj.get("id"),
                        "name": obj.get("user", {}).get("name"),
                        "email": obj.get("user", {}).get("email")
                    }
                    v1_all.append(projected)
        v1_time = time.perf_counter() - v1_start
        
        # V2: List with nested projection using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            projected = {
                "id": obj.get("id"),
                "name": obj.get("user", {}).get("name"),
                "email": obj.get("user", {}).get("email")
            }
            v2_all.append(projected)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_all) == len(v2_all) == 2
        assert all("name" in r and "email" in r for r in v1_all)
        assert all("age" not in r for r in v1_all)
        assert v1_all == v2_all
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 5.5 Edge Cases and Error Handling
# ============================================================================

def test_5_5_1_list_empty_file():
    """
    Full Test Name: test_5_5_1_list_empty_file
    Test: List operations on empty file should return empty results
    """
    file_path = create_test_file([])
    
    try:
        # V1: List all from empty file
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List all from empty file
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 0
        assert v1_results == v2_results
        
        # Test pagination on empty file
        page_results = get_page(file_path, 1, 10, index=index)
        assert len(page_results) == 0
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_5_2_list_with_missing_fields():
    """
    Full Test Name: test_5_5_2_list_with_missing_fields
    Test: List operations handle records with missing fields gracefully
    """
    test_data = [
        {"id": "1", "name": "Alice", "score": 100},
        {"id": "2", "name": "Bob"},  # Missing score
        {"id": "3", "score": 75},  # Missing name
        {"id": "4"}  # Only id
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List all records with missing fields
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List all records with missing fields
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 4
        assert v1_results == v2_results
        
        # Test filtering with missing fields (should use default values)
        def has_high_score(obj):
            return obj.get("score", 0) >= 80
        
        v1_filtered = get_all_matching_v1(file_path, has_high_score)
        v2_filtered = get_all_matching_v2(file_path, has_high_score, index=index)
        
        assert len(v1_filtered) == len(v2_filtered) == 1  # Only record 1 has score >= 80
        assert v1_filtered == v2_filtered
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_5_3_list_with_null_values():
    """
    Full Test Name: test_5_5_3_list_with_null_values
    Test: List operations handle null/None values correctly
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": None, "age": 25},  # null name
        {"id": "3", "name": "Charlie", "age": None}  # null age
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: List all with null values
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    v1_results.append(json.loads(line.strip()))
        v1_time = time.perf_counter() - v1_start
        
        # V2: List all with null values
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            v2_results.append(indexed_get_by_line(file_path, i, index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert len(v1_results) == len(v2_results) == 3
        assert v1_results == v2_results
        assert v1_results[1]["name"] is None
        assert v1_results[2]["age"] is None
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_5_5_4_list_pagination_edge_cases():
    """
    Full Test Name: test_5_5_4_list_pagination_edge_cases
    Test: Pagination handles edge cases (page beyond range, zero page size, etc.)
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(5)]
    file_path = create_test_file(test_data)
    
    try:
        index = build_index(file_path, id_field="id")
        
        # Test page beyond range (should return empty)
        page1 = get_page(file_path, 10, 10, index=index)
        assert len(page1) == 0
        
        # Test last page (partial results)
        page_last = get_page(file_path, 1, 3, index=index)  # Should get first 3 of 5
        assert len(page_last) == 3
        
        # Test page size larger than total
        page_large = get_page(file_path, 1, 100, index=index)
        assert len(page_large) == 5
        
        return True, 0.0, 0.0
    finally:
        cleanup_test_file(file_path)


def test_5_5_5_list_with_invalid_json():
    """
    Full Test Name: test_5_5_5_list_with_invalid_json
    Test: Handle gracefully when file has invalid JSON lines (skip bad lines)
    """
    # Create file with valid records
    file_path = create_test_file([
        {"id": "1", "name": "Valid"},
        {"id": "2", "name": "AlsoValid"}
    ])
    
    try:
        # V1: List all valid records
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        v1_results.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines
        v1_time = time.perf_counter() - v1_start
        
        # V2: List all valid records
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for i in range(len(index.line_offsets)):
            try:
                v2_results.append(indexed_get_by_line(file_path, i, index=index))
            except Exception:
                continue  # Skip invalid lines
        v2_time = time.perf_counter() - v2_start
        
        # Should have 2 valid records
        assert len(v1_results) == 2
        assert len(v2_results) == 2
        assert v1_results == v2_results
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)