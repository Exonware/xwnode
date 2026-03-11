"""
#exonware/xwnode/examples/x5/data_operations/test_4_delete_operations.py
DELETE Operations Test Suite
Tests all DELETE operations (removing data) for both V1 (Streaming) and V2 (Indexed) implementations.
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
from pathlib import Path
from typing import Any
# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    delete_record_by_id_v1,
    delete_record_by_id_v2,
    delete_record_by_line_v1,
    delete_record_by_line_v2,
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
    stream_update,
    JsonRecordNotFound,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_id,
    indexed_get_by_line,
)
# ============================================================================
# 4.1 Single Record Deletion
# ============================================================================


def test_4_1_1_delete_by_id():
    """
    Full Test Name: test_4_1_1_delete_by_id
    Test: Remove record by unique identifier
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete by ID
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "2", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        assert all(r["id"] != "2" for r in v1_remaining)
        assert v1_deleted
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete by ID and rebuild index
        v2_start = time.perf_counter()
        v2_deleted = delete_record_by_id_v2(file_path, "2", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        assert all(r["id"] != "2" for r in v2_remaining)
        assert v2_deleted
        # Verify record is gone
        try:
            indexed_get_by_id(file_path, "2", id_field="id", index=index)
            assert False, "Record should not exist"
        except JsonRecordNotFound:
            pass
        assert v1_deleted == v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_1_2_delete_by_line_number():
    """
    Full Test Name: test_4_1_2_delete_by_line_number
    Test: Remove record by position
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete by line number (0-indexed, line 1 = Bob)
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_line_v1(file_path, 1)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        assert v1_remaining[0]["id"] == "1"
        assert v1_remaining[1]["id"] == "3"
        assert v1_deleted
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete by line number and rebuild index
        v2_start = time.perf_counter()
        v2_deleted = delete_record_by_line_v2(file_path, 1)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        assert v2_remaining[0]["id"] == "1"
        assert v2_remaining[1]["id"] == "3"
        assert v2_deleted
        assert v1_deleted == v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_1_3_delete_first_matching():
    """
    Full Test Name: test_4_1_3_delete_first_matching
    Test: Delete first record matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "admin"},
        {"id": "3", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Delete first matching (read all, delete first, write back)
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        first_admin = None
        for i, record in enumerate(records):
            if is_admin(record):
                first_admin = record
                # Delete by ID
                delete_record_by_id_v1(file_path, record["id"], id_field="id")
                break
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        admin_count = sum(1 for r in v1_remaining if is_admin(r))
        assert admin_count == 1  # One admin should remain
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete first matching using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        for i in range(len(index.line_offsets)):
            record = indexed_get_by_line(file_path, i, index=index)
            if is_admin(record):
                delete_record_by_id_v2(file_path, record["id"], id_field="id")
                break
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        admin_count_v2 = sum(1 for r in v2_remaining if is_admin(r))
        assert admin_count_v2 == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_1_4_delete_with_confirmation():
    """
    Full Test Name: test_4_1_4_delete_with_confirmation
    Test: Delete only if condition verified
    """
    test_data = [
        {"id": "1", "name": "Alice", "status": "active"},
        {"id": "2", "name": "Bob", "status": "inactive"}
    ]
    file_path = create_test_file(test_data)
    try:
        def can_delete(obj):
            return obj.get("status") == "inactive"
        # V1: Delete with confirmation
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        deleted_count = 0
        for record in records:
            if can_delete(record):
                if delete_record_by_id_v1(file_path, record["id"], id_field="id"):
                    deleted_count += 1
                    break  # Delete first matching
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "1"
        assert deleted_count == 1
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with confirmation using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        deleted_count_v2 = 0
        for i in range(len(index.line_offsets)):
            record = indexed_get_by_line(file_path, i, index=index)
            if can_delete(record):
                if delete_record_by_id_v2(file_path, record["id"], id_field="id"):
                    deleted_count_v2 += 1
                    break
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "1"
        assert deleted_count_v2 == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 4.2 Multiple Record Deletion
# ============================================================================


def test_4_2_1_delete_all_matching():
    """
    Full Test Name: test_4_2_1_delete_all_matching
    Test: Remove all records matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "admin"},
        {"id": "3", "role": "user"},
        {"id": "4", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Delete all matching
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, is_admin)
        deleted_count = 0
        for record in records:
            if delete_record_by_id_v1(file_path, record["id"], id_field="id"):
                deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["role"] == "user"
        assert deleted_count == 3
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete all matching using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, is_admin, index=index)
        deleted_count_v2 = 0
        for record in records_v2:
            if delete_record_by_id_v2(file_path, record["id"], id_field="id"):
                deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["role"] == "user"
        assert deleted_count_v2 == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_2_2_delete_by_id_list():
    """
    Full Test Name: test_4_2_2_delete_by_id_list
    Test: Remove multiple records by list of IDs
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
        {"id": "4", "name": "David"}
    ]
    file_path = create_test_file(test_data)
    try:
        id_list = ["2", "4"]
        # V1: Delete by ID list
        v1_start = time.perf_counter()
        deleted_count = 0
        for record_id in id_list:
            if delete_record_by_id_v1(file_path, record_id, id_field="id"):
                deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        assert all(r["id"] not in id_list for r in v1_remaining)
        assert deleted_count == 2
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete by ID list using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        deleted_count_v2 = 0
        for record_id in id_list:
            if delete_record_by_id_v2(file_path, record_id, id_field="id"):
                deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        assert all(r["id"] not in id_list for r in v2_remaining)
        assert deleted_count_v2 == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_2_3_delete_by_line_range():
    """
    Full Test Name: test_4_2_3_delete_by_line_range
    Test: Remove records from line N to M
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
        start_line = 1
        end_line = 3  # Delete lines 1 and 2 (0-indexed)
        # V1: Delete by line range (delete in reverse to maintain indices)
        v1_start = time.perf_counter()
        deleted_count = 0
        for line_num in range(end_line - 1, start_line - 1, -1):  # Reverse order
            if delete_record_by_line_v1(file_path, line_num):
                deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 3
        assert v1_remaining[0]["id"] == "1"
        assert v1_remaining[1]["id"] == "4"
        assert deleted_count == 2
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete by line range using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        deleted_count_v2 = 0
        for line_num in range(end_line - 1, start_line - 1, -1):  # Reverse order
            if delete_record_by_line_v2(file_path, line_num):
                deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 3
        assert v2_remaining[0]["id"] == "1"
        assert v2_remaining[1]["id"] == "4"
        assert deleted_count_v2 == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_2_4_delete_with_limit():
    """
    Full Test Name: test_4_2_4_delete_with_limit
    Test: Delete first N matching records
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "admin"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        limit = 2
        # V1: Delete with limit
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, is_admin)
        deleted_count = 0
        for record in records[:limit]:
            if delete_record_by_id_v1(file_path, record["id"], id_field="id"):
                deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2  # 2 admins deleted, 1 admin + 1 user remain
        admin_count = sum(1 for r in v1_remaining if is_admin(r))
        assert admin_count == 1
        assert deleted_count == limit
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with limit using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, is_admin, index=index)
        deleted_count_v2 = 0
        for record in records_v2[:limit]:
            if delete_record_by_id_v2(file_path, record["id"], id_field="id"):
                deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        admin_count_v2 = sum(1 for r in v2_remaining if is_admin(r))
        assert admin_count_v2 == 1
        assert deleted_count_v2 == limit
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_2_5_bulk_delete():
    """
    Full Test Name: test_4_2_5_bulk_delete
    Test: Delete large number of records efficiently
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(20)]
    file_path = create_test_file(test_data)
    try:
        ids_to_delete = [str(i) for i in range(5, 15)]  # Delete 10 records
        # V1: Bulk delete
        v1_start = time.perf_counter()
        deleted_count = 0
        for record_id in ids_to_delete:
            if delete_record_by_id_v1(file_path, record_id, id_field="id"):
                deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 10  # 20 - 10 = 10
        assert all(r["id"] not in ids_to_delete for r in v1_remaining)
        assert deleted_count == 10
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk delete using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        deleted_count_v2 = 0
        for record_id in ids_to_delete:
            if delete_record_by_id_v2(file_path, record_id, id_field="id"):
                deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 10
        assert all(r["id"] not in ids_to_delete for r in v2_remaining)
        assert deleted_count_v2 == 10
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 4.3 Conditional Deletion
# ============================================================================


def test_4_3_1_delete_if_exists():
    """
    Full Test Name: test_4_3_1_delete_if_exists
    Test: Delete only if record exists
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete if exists
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_not_found = delete_record_by_id_v1(file_path, "999", id_field="id")  # Non-existent
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "2"
        assert v1_deleted == True
        assert v1_not_found == False
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete if exists using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_not_found = delete_record_by_id_v2(file_path, "999", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "2"
        assert v2_deleted == True
        assert v2_not_found == False
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_3_2_delete_if_matches():
    """
    Full Test Name: test_4_3_2_delete_if_matches
    Test: Delete only if condition is met
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob", "age": 25},
        {"id": "3", "name": "Charlie", "age": 35}
    ]
    file_path = create_test_file(test_data)
    try:
        def should_delete(obj):
            return obj.get("age", 0) >= 30
        # V1: Delete if matches
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        deleted_count = 0
        for record in records:
            if should_delete(record):
                if delete_record_by_id_v1(file_path, record["id"], id_field="id"):
                    deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "2"
        assert deleted_count == 2
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete if matches using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        deleted_count_v2 = 0
        for record in records_v2:
            if should_delete(record):
                if delete_record_by_id_v2(file_path, record["id"], id_field="id"):
                    deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "2"
        assert deleted_count_v2 == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_3_3_delete_with_cascade():
    """
    Full Test Name: test_4_3_3_delete_with_cascade
    Test: Delete record and related records
    """
    test_data = [
        {"id": "1", "name": "Alice", "parent_id": None},
        {"id": "2", "name": "Bob", "parent_id": "1"},
        {"id": "3", "name": "Charlie", "parent_id": "1"},
        {"id": "4", "name": "David", "parent_id": None}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with cascade (delete parent and children)
        v1_start = time.perf_counter()
        parent_id = "1"
        # First delete children
        records = get_all_matching_v1(file_path, lambda x: x.get("parent_id") == parent_id)
        for record in records:
            delete_record_by_id_v1(file_path, record["id"], id_field="id")
        # Then delete parent
        delete_record_by_id_v1(file_path, parent_id, id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "4"
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with cascade using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        # First delete children
        records_v2 = get_all_matching_v2(file_path, lambda x: x.get("parent_id") == parent_id, index=index)
        for record in records_v2:
            delete_record_by_id_v2(file_path, record["id"], id_field="id")
        # Then delete parent
        delete_record_by_id_v2(file_path, parent_id, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "4"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_3_4_soft_delete():
    """
    Full Test Name: test_4_3_4_soft_delete
    Test: Mark as deleted without removing (add deleted flag)
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        def soft_delete(obj):
            obj["deleted"] = True
            obj["deleted_at"] = "2024-01-01"
            return obj
        # V1: Soft delete
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), soft_delete)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["deleted"] == True
        assert v1_result["deleted_at"] == "2024-01-01"
        assert v1_result["name"] == "Alice"
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Soft delete and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), soft_delete)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["deleted"] == True
        assert v2_result["deleted_at"] == "2024-01-01"
        assert v2_result["name"] == "Alice"
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_3_5_hard_delete():
    """
    Full Test Name: test_4_3_5_hard_delete
    Test: Permanently remove from file
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Hard delete (permanent removal)
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "2"
        # Verify record is completely gone
        try:
            stream_read(file_path, match_by_id("id", "1"))
            assert False, "Record should not exist"
        except JsonRecordNotFound:
            pass
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Hard delete using index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "2"
        # Verify record is completely gone
        try:
            indexed_get_by_id(file_path, "1", id_field="id", index=index)
            assert False, "Record should not exist"
        except JsonRecordNotFound:
            pass
        assert v1_deleted == v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 4.4 Field Deletion
# ============================================================================


def test_4_4_1_delete_field():
    """
    Full Test Name: test_4_4_1_delete_field
    Test: Remove specific field from record
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        def remove_field(obj):
            if "age" in obj:
                del obj["age"]
            return obj
        # V1: Delete field
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), remove_field)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert "age" not in v1_result
        assert "name" in v1_result
        assert v1_result["id"] == "1"
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete field and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), remove_field)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert "age" not in v2_result
        assert "name" in v2_result
        assert v2_result["id"] == "1"
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_4_2_delete_nested_field():
    """
    Full Test Name: test_4_4_2_delete_nested_field
    Test: Remove nested field from record
    """
    test_data = [{"id": "1", "user": {"name": "Alice", "age": 30}}]
    file_path = create_test_file(test_data)
    try:
        def remove_nested_field(obj):
            if "user" in obj and "age" in obj["user"]:
                del obj["user"]["age"]
            return obj
        # V1: Delete nested field
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), remove_nested_field)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert "age" not in v1_result["user"]
        assert "name" in v1_result["user"]
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete nested field and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), remove_nested_field)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert "age" not in v2_result["user"]
        assert "name" in v2_result["user"]
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_4_3_delete_array_element():
    """
    Full Test Name: test_4_4_3_delete_array_element
    Test: Remove element from array
    """
    test_data = [{"id": "1", "tags": ["a", "b", "c"]}]
    file_path = create_test_file(test_data)
    try:
        def remove_array_element(obj):
            if "b" in obj.get("tags", []):
                obj["tags"].remove("b")
            return obj
        # V1: Delete array element
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), remove_array_element)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "c"]
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete array element and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), remove_array_element)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["a", "c"]
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_4_4_delete_multiple_fields():
    """
    Full Test Name: test_4_4_4_delete_multiple_fields
    Test: Remove several fields at once
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30, "email": "alice@example.com"}]
    file_path = create_test_file(test_data)
    try:
        def remove_multiple_fields(obj):
            for field in ["age", "email"]:
                if field in obj:
                    del obj[field]
            return obj
        # V1: Delete multiple fields
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), remove_multiple_fields)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert "age" not in v1_result
        assert "email" not in v1_result
        assert "name" in v1_result
        assert v1_result["id"] == "1"
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete multiple fields and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), remove_multiple_fields)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert "age" not in v2_result
        assert "email" not in v2_result
        assert "name" in v2_result
        assert v2_result["id"] == "1"
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_4_5_clear_record():
    """
    Full Test Name: test_4_4_5_clear_record
    Test: Remove all fields, keep empty record
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        def clear_record(obj):
            return {"id": obj["id"]}  # Keep only ID
        # V1: Clear record
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), clear_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result == {"id": "1"}
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Clear record and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), clear_record)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result == {"id": "1"}
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 4.5 Edge Cases
# ============================================================================


def test_4_5_1_delete_from_empty_file():
    """
    Full Test Name: test_4_5_1_delete_from_empty_file
    Test: Delete from empty file should return False
    """
    file_path = create_test_file([])
    try:
        # V1: Delete from empty file
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        assert v1_deleted == False
        v1_count = count_records_v1(file_path)
        assert v1_count == 0
        # V2: Delete from empty file
        v2_start = time.perf_counter()
        v2_deleted = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        assert v2_deleted == False
        index = ensure_index(file_path, id_field="id")
        v2_count = count_records_v2(file_path, index=index)
        assert v2_count == 0
        assert v1_deleted == v2_deleted == False
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_2_delete_nonexistent_id():
    """
    Full Test Name: test_4_5_2_delete_nonexistent_id
    Test: Delete non-existent ID should return False
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete non-existent ID
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "999", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        assert v1_deleted == False
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "1"
        # V2: Delete non-existent ID
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "999", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        assert v2_deleted == False
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "1"
        assert v1_deleted == v2_deleted == False
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_3_delete_invalid_line_number():
    """
    Full Test Name: test_4_5_3_delete_invalid_line_number
    Test: Delete with invalid line number should return False
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete invalid line number (negative)
        v1_start = time.perf_counter()
        v1_deleted_neg = delete_record_by_line_v1(file_path, -1)
        # Delete invalid line number (too large)
        v1_deleted_large = delete_record_by_line_v1(file_path, 999)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        assert v1_deleted_neg == False
        assert v1_deleted_large == False
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        # V2: Delete invalid line number
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted_neg = delete_record_by_line_v2(file_path, -1)
        v2_deleted_large = delete_record_by_line_v2(file_path, 999)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        assert v2_deleted_neg == False
        assert v2_deleted_large == False
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_4_delete_with_missing_id_field():
    """
    Full Test Name: test_4_5_4_delete_with_missing_id_field
    Test: Delete when ID field is missing from records
    """
    test_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with missing ID field
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - should return False since no records have ID field
        assert v1_deleted == False
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        # V2: Delete with missing ID field
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        assert v2_deleted == False
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        assert v1_deleted == v2_deleted == False
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_5_delete_with_duplicate_ids():
    """
    Full Test Name: test_4_5_5_delete_with_duplicate_ids
    Test: Delete when multiple records have same ID (should delete first match)
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "1", "name": "Alice2"},  # Duplicate ID
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with duplicate IDs (should delete first match)
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - first record with ID "1" should be deleted
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        # Check that one record with ID "1" remains
        ids = [r.get("id") for r in v1_remaining]
        assert "1" in ids
        assert "2" in ids
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with duplicate IDs
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        ids_v2 = [r.get("id") for r in v2_remaining]
        assert "1" in ids_v2
        assert "2" in ids_v2
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_6_delete_with_null_id():
    """
    Full Test Name: test_4_5_6_delete_with_null_id
    Test: Delete when ID field is None/null
    """
    test_data = [
        {"id": None, "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with null ID
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, None, id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "2"
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with null ID
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, None, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "2"
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_7_delete_with_unicode_ids():
    """
    Full Test Name: test_4_5_7_delete_with_unicode_ids
    Test: Delete with Unicode characters in ID
    """
    test_data = [
        {"id": "用户1", "name": "Alice"},
        {"id": "用户2", "name": "Bob"},
        {"id": "🎉🎊", "name": "Charlie"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with Unicode ID
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "用户1", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 2
        assert all(r["id"] != "用户1" for r in v1_remaining)
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with Unicode ID
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "用户1", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 2
        assert all(r["id"] != "用户1" for r in v2_remaining)
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_8_delete_last_record():
    """
    Full Test Name: test_4_5_8_delete_last_record
    Test: Delete the last record in file
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete last record
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "2", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "1"
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete last record
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "2", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "1"
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_9_delete_first_record():
    """
    Full Test Name: test_4_5_9_delete_first_record
    Test: Delete the first record in file
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete first record
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "2"
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete first record
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "2"
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_10_delete_all_records():
    """
    Full Test Name: test_4_5_10_delete_all_records
    Test: Delete all records from file
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete all records
        v1_start = time.perf_counter()
        v1_deleted1 = delete_record_by_id_v1(file_path, "1", id_field="id")
        v1_deleted2 = delete_record_by_id_v1(file_path, "2", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 0
        assert v1_deleted1 == True
        assert v1_deleted2 == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete all records
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted1 = delete_record_by_id_v2(file_path, "1", id_field="id")
        v2_deleted2 = delete_record_by_id_v2(file_path, "2", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 0
        assert v2_deleted1 == True
        assert v2_deleted2 == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_11_delete_with_special_characters():
    """
    Full Test Name: test_4_5_11_delete_with_special_characters
    Test: Delete with special characters in ID
    """
    test_data = [
        {"id": "id-with-dashes", "name": "Alice"},
        {"id": "id_with_underscores", "name": "Bob"},
        {"id": "id.with.dots", "name": "Charlie"},
        {"id": "id@with#special$chars", "name": "David"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with special characters
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, "id-with-dashes", id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 3
        assert all(r["id"] != "id-with-dashes" for r in v1_remaining)
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with special characters
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, "id-with-dashes", id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 3
        assert all(r["id"] != "id-with-dashes" for r in v2_remaining)
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_4_5_12_delete_with_very_large_id():
    """
    Full Test Name: test_4_5_12_delete_with_very_large_id
    Test: Delete with very large ID value
    """
    large_id = "x" * 10000  # 10KB ID
    test_data = [
        {"id": large_id, "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete with very large ID
        v1_start = time.perf_counter()
        v1_deleted = delete_record_by_id_v1(file_path, large_id, id_field="id")
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 1
        assert v1_remaining[0]["id"] == "2"
        assert v1_deleted == True
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Delete with very large ID
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        v2_deleted = delete_record_by_id_v2(file_path, large_id, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 1
        assert v2_remaining[0]["id"] == "2"
        assert v2_deleted == True
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
