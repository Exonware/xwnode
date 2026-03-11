"""
#exonware/xwnode/examples/x5/data_operations/test_7_bulk_operations.py
BULK Operations Test Suite
Tests all BULK operations (batch processing) for both V1 (Streaming) and V2 (Indexed) implementations.
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
import tempfile
import shutil
from pathlib import Path
from typing import Any
# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    append_record_v1,
    append_record_v2,
    bulk_append_v1,
    bulk_append_v2,
    get_all_matching_v1,
    get_all_matching_v2,
    delete_record_by_id_v1,
    delete_record_by_id_v2,
    count_records_v1,
    count_records_v2,
)
# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from json_utils import (
    match_by_id,
    stream_read,
    stream_update,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_line,
    indexed_get_by_id,
)
# ============================================================================
# 7.1 Bulk Read
# ============================================================================


def test_7_1_1_bulk_get_by_ids():
    """
    Full Test Name: test_7_1_1_bulk_get_by_ids
    Test: Retrieve multiple records by ID list
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        id_list = ["1", "3", "5", "7", "9"]
        # V1: Bulk get by IDs
        v1_start = time.perf_counter()
        v1_results = []
        for record_id in id_list:
            try:
                v1_results.append(stream_read(file_path, match_by_id("id", record_id)))
            except Exception:
                pass
        v1_time = time.perf_counter() - v1_start
        # V2: Bulk get by IDs using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for record_id in id_list:
            try:
                v2_results.append(indexed_get_by_id(file_path, record_id, id_field="id", index=index))
            except Exception:
                pass
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 5
        assert v1_results == v2_results
        assert all(r["id"] in id_list for r in v1_results)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_1_2_bulk_get_by_line_numbers():
    """
    Full Test Name: test_7_1_2_bulk_get_by_line_numbers
    Test: Retrieve multiple records by positions
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        line_numbers = [1, 3, 5, 7, 9]
        # V1: Bulk get by line numbers
        v1_start = time.perf_counter()
        v1_results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line_num in line_numbers:
                if line_num < len(lines):
                    v1_results.append(json.loads(lines[line_num].strip()))
        v1_time = time.perf_counter() - v1_start
        # V2: Bulk get by line numbers using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = []
        for line_num in line_numbers:
            if line_num < len(index.line_offsets):
                v2_results.append(indexed_get_by_line(file_path, line_num, index=index))
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 5
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_1_3_bulk_get_matching():
    """
    Full Test Name: test_7_1_3_bulk_get_matching
    Test: Retrieve all matching records
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "admin"},
        {"id": "5", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Bulk get matching
        v1_start = time.perf_counter()
        v1_results = get_all_matching_v1(file_path, is_admin)
        v1_time = time.perf_counter() - v1_start
        # V2: Bulk get matching using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_results = get_all_matching_v2(file_path, is_admin, index=index)
        v2_time = time.perf_counter() - v2_start
        assert len(v1_results) == len(v2_results) == 3
        assert all(r.get("role") == "admin" for r in v1_results)
        assert v1_results == v2_results
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_1_4_bulk_get_with_projection():
    """
    Full Test Name: test_7_1_4_bulk_get_with_projection
    Test: Retrieve multiple records with field selection
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30, "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "age": 25, "email": "bob@example.com"},
        {"id": "3", "name": "Charlie", "age": 35, "email": "charlie@example.com"}
    ]
    file_path = create_test_file(test_data)
    try:
        fields = ["id", "name"]
        # V1: Bulk get with projection
        v1_start = time.perf_counter()
        v1_all = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line.strip())
                    v1_all.append({k: v for k, v in obj.items() if k in fields})
        v1_time = time.perf_counter() - v1_start
        # V2: Bulk get with projection using index
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_all = []
        for i in range(len(index.line_offsets)):
            obj = indexed_get_by_line(file_path, i, index=index)
            v2_all.append({k: v for k, v in obj.items() if k in fields})
        v2_time = time.perf_counter() - v2_start
        assert len(v1_all) == len(v2_all) == 3
        assert all(set(r.keys()) == set(fields) for r in v1_all)
        assert v1_all == v2_all
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 7.2 Bulk Write
# ============================================================================


def test_7_2_1_bulk_insert():
    """
    Full Test Name: test_7_2_1_bulk_insert
    Test: Insert multiple records at once
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        new_records = [
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Charlie"},
            {"id": "4", "name": "David"}
        ]
        # V1: Bulk insert
        v1_start = time.perf_counter()
        v1_count = bulk_append_v1(file_path, new_records)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_all = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_all) == 4
        assert v1_count == 3
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk insert (rebuilds index once)
        v2_start = time.perf_counter()
        v2_count = bulk_append_v2(file_path, new_records)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_all = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_all) == 4
        assert v2_count == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_2_2_bulk_update():
    """
    Full Test Name: test_7_2_2_bulk_update
    Test: Update multiple records at once
    """
    test_data = [
        {"id": "1", "name": "Alice", "status": "pending"},
        {"id": "2", "name": "Bob", "status": "pending"},
        {"id": "3", "name": "Charlie", "status": "pending"}
    ]
    file_path = create_test_file(test_data)
    try:
        def update_status(obj):
            if obj.get("status") == "pending":
                obj["status"] = "active"
            return obj
        # V1: Bulk update
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, lambda x: x.get("status") == "pending", update_status)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_results = get_all_matching_v1(file_path, lambda x: x.get("status") == "active")
        assert len(v1_results) == 3
        assert v1_updated == 3
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk update and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, lambda x: x.get("status") == "pending", update_status)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_results = get_all_matching_v2(file_path, lambda x: x.get("status") == "active", index=index)
        assert len(v2_results) == 3
        assert v2_updated == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_2_3_bulk_upsert():
    """
    Full Test Name: test_7_2_3_bulk_upsert
    Test: Insert or update multiple records
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob", "age": 25}
    ]
    file_path = create_test_file(test_data)
    try:
        records_to_upsert = [
            {"id": "1", "name": "Alicia", "age": 31},  # Update
            {"id": "3", "name": "Charlie", "age": 35},  # Insert
            {"id": "2", "name": "Robert", "age": 26}  # Update
        ]
        def upsert_v1(filepath, records):
            for record in records:
                try:
                    existing = stream_read(filepath, match_by_id("id", record["id"]))
                    def updater(obj):
                        return record
                    stream_update(filepath, match_by_id("id", record["id"]), updater)
                except Exception:
                    append_record_v1(filepath, record)
        # V1: Bulk upsert
        v1_start = time.perf_counter()
        upsert_v1(file_path, records_to_upsert)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_all = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_all) == 3
        assert stream_read(file_path, match_by_id("id", "1"))["name"] == "Alicia"
        assert stream_read(file_path, match_by_id("id", "3"))["name"] == "Charlie"
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk upsert
        def upsert_v2(filepath, records):
            index = ensure_index(filepath, id_field="id")
            for record in records:
                try:
                    indexed_get_by_id(filepath, record["id"], id_field="id", index=index)
                    def updater(obj):
                        return record
                    stream_update(filepath, match_by_id("id", record["id"]), updater)
                    build_index(filepath, id_field="id")
                    index = ensure_index(filepath, id_field="id")
                except Exception:
                    append_record_v2(filepath, record)
                    index = ensure_index(filepath, id_field="id")
        v2_start = time.perf_counter()
        upsert_v2(file_path, records_to_upsert)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_all = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_all) == 3
        assert indexed_get_by_id(file_path, "1", id_field="id", index=index)["name"] == "Alicia"
        assert indexed_get_by_id(file_path, "3", id_field="id", index=index)["name"] == "Charlie"
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_2_4_bulk_delete():
    """
    Full Test Name: test_7_2_4_bulk_delete
    Test: Delete multiple records at once
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        ids_to_delete = ["2", "4", "6", "8"]
        # V1: Bulk delete
        v1_start = time.perf_counter()
        deleted_count = 0
        for record_id in ids_to_delete:
            if delete_record_by_id_v1(file_path, record_id, id_field="id"):
                deleted_count += 1
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_remaining = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_remaining) == 6
        assert deleted_count == 4
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk delete (rebuilds index after each delete)
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        deleted_count_v2 = 0
        for record_id in ids_to_delete:
            if delete_record_by_id_v2(file_path, record_id, id_field="id"):
                deleted_count_v2 += 1
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_remaining = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_remaining) == 6
        assert deleted_count_v2 == 4
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_2_5_bulk_replace():
    """
    Full Test Name: test_7_2_5_bulk_replace
    Test: Replace multiple records
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob", "age": 25},
        {"id": "3", "name": "Charlie", "age": 35}
    ]
    file_path = create_test_file(test_data)
    try:
        replacements = [
            {"id": "1", "name": "Alicia", "age": 31, "new_field": "value1"},
            {"id": "2", "name": "Robert", "age": 26, "new_field": "value2"}
        ]
        def replace_v1(filepath, replacements):
            for replacement in replacements:
                def replacer(obj):
                    return replacement
                stream_update(filepath, match_by_id("id", replacement["id"]), replacer)
        # V1: Bulk replace
        v1_start = time.perf_counter()
        replace_v1(file_path, replacements)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        assert stream_read(file_path, match_by_id("id", "1")) == replacements[0]
        assert stream_read(file_path, match_by_id("id", "2")) == replacements[1]
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk replace and rebuild index
        def replace_v2(filepath, replacements):
            for replacement in replacements:
                def replacer(obj):
                    return replacement
                stream_update(filepath, match_by_id("id", replacement["id"]), replacer)
            build_index(filepath, id_field="id")
        v2_start = time.perf_counter()
        replace_v2(file_path, replacements)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        assert indexed_get_by_id(file_path, "1", id_field="id", index=index) == replacements[0]
        assert indexed_get_by_id(file_path, "2", id_field="id", index=index) == replacements[1]
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 7.3 Bulk Operations with Conditions
# ============================================================================


def test_7_3_1_bulk_update_matching():
    """
    Full Test Name: test_7_3_1_bulk_update_matching
    Test: Update all records matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin", "status": "pending"},
        {"id": "2", "role": "user", "status": "pending"},
        {"id": "3", "role": "admin", "status": "pending"},
        {"id": "4", "role": "admin", "status": "active"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin_pending(obj):
            return obj.get("role") == "admin" and obj.get("status") == "pending"
        def activate(obj):
            obj["status"] = "active"
            return obj
        # V1: Bulk update matching
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, is_admin_pending, activate)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - Only admin+pending records were updated (2 records: id 1 and 3)
        # id 2 is user+pending (not updated), id 4 is already active
        v1_active = get_all_matching_v1(file_path, lambda x: x.get("status") == "active")
        assert len(v1_active) == 3  # 2 updated + 1 already active
        assert v1_updated == 2
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk update matching and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, is_admin_pending, activate)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        # Verify V2 - Only admin+pending records were updated
        index = ensure_index(file_path, id_field="id")
        v2_active = get_all_matching_v2(file_path, lambda x: x.get("status") == "active", index=index)
        assert len(v2_active) == 3  # 2 updated + 1 already active
        assert v2_updated == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_3_2_bulk_delete_matching():
    """
    Full Test Name: test_7_3_2_bulk_delete_matching
    Test: Delete all records matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        # V1: Bulk delete matching
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
        assert deleted_count == 3
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk delete matching
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
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
        assert deleted_count_v2 == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_3_3_bulk_insert_with_validation():
    """
    Full Test Name: test_7_3_3_bulk_insert_with_validation
    Test: Validate all before inserting
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        def validate_record(record):
            if not isinstance(record.get("name"), str) or not record.get("name"):
                raise ValueError("Name is required")
            if not isinstance(record.get("age"), int) or record.get("age") < 0:
                raise ValueError("Age must be non-negative integer")
            return True
        new_records = [
            {"id": "2", "name": "Bob", "age": 25},  # Valid
            {"id": "3", "name": "", "age": 30},  # Invalid name
            {"id": "4", "name": "Charlie", "age": -5}  # Invalid age
        ]
        # V1: Bulk insert with validation
        v1_start = time.perf_counter()
        valid_records = []
        for record in new_records:
            try:
                if validate_record(record):
                    valid_records.append(record)
            except ValueError:
                pass
        bulk_append_v1(file_path, valid_records)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_all = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_all) == 2  # Original + 1 valid
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk insert with validation
        v2_start = time.perf_counter()
        valid_records_v2 = []
        for record in new_records:
            try:
                if validate_record(record):
                    valid_records_v2.append(record)
            except ValueError:
                pass
        bulk_append_v2(file_path, valid_records_v2)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_all = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_all) == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_3_4_bulk_operations_with_transaction():
    """
    Full Test Name: test_7_3_4_bulk_operations_with_transaction
    Test: All-or-nothing bulk operations
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        new_records = [
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Charlie"},
            {"id": "4", "name": "David"}
        ]
        # V1: Bulk operations with transaction (simulate atomic)
        v1_start = time.perf_counter()
        initial_content = Path(file_path).read_text(encoding='utf-8')
        temp_file = create_test_file(test_data)
        try:
            bulk_append_v1(temp_file, new_records)
            # If all succeed, replace original
            shutil.copy(temp_file, file_path)
            v1_success = True
        except Exception:
            v1_success = False
        finally:
            cleanup_test_file(temp_file)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_all = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_all) == 4
        assert v1_success
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        # V2: Bulk operations with transaction
        v2_start = time.perf_counter()
        temp_file_v2 = create_test_file(test_data)
        try:
            bulk_append_v2(temp_file_v2, new_records)
            shutil.copy(temp_file_v2, file_path)
            build_index(file_path, id_field="id")
            v2_success = True
        except Exception:
            v2_success = False
        finally:
            cleanup_test_file(temp_file_v2)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_all = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_all) == 4
        assert v2_success
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 7.4 Edge Cases and Error Handling
# ============================================================================


def test_7_4_1_bulk_operations_empty_file():
    """
    Full Test Name: test_7_4_1_bulk_operations_empty_file
    Test: Bulk operations on empty file should work correctly
    """
    file_path = create_test_file([])
    try:
        new_records = [
            {"id": "1", "name": "Alice"},
            {"id": "2", "name": "Bob"}
        ]
        # V1: Bulk insert into empty file
        v1_start = time.perf_counter()
        v1_count = bulk_append_v1(file_path, new_records)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_all = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_all) == 2
        assert v1_count == 2
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file([])
        # V2: Bulk insert into empty file
        v2_start = time.perf_counter()
        v2_count = bulk_append_v2(file_path, new_records)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_all = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_all) == 2
        assert v2_count == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_4_2_bulk_operations_empty_batch():
    """
    Full Test Name: test_7_4_2_bulk_operations_empty_batch
    Test: Bulk operations handle empty batch gracefully
    """
    test_data = [{"id": "1", "name": "Existing"}]
    file_path = create_test_file(test_data)
    try:
        empty_batch = []
        # V1: Bulk insert empty batch
        v1_start = time.perf_counter()
        v1_count = bulk_append_v1(file_path, empty_batch)
        v1_time = time.perf_counter() - v1_start
        # Verify - no changes
        v1_count_check = count_records_v1(file_path)
        assert v1_count_check == 1
        assert v1_count == 0
        # V2: Bulk insert empty batch
        v2_start = time.perf_counter()
        v2_count = bulk_append_v2(file_path, empty_batch)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_count_check = count_records_v2(file_path, index=index)
        assert v2_count_check == 1
        assert v2_count == 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_7_4_3_bulk_operations_with_null_values():
    """
    Full Test Name: test_7_4_3_bulk_operations_with_null_values
    Test: Bulk operations handle null/None values correctly
    """
    file_path = create_test_file([])
    try:
        records_with_nulls = [
            {"id": "1", "name": "Alice", "age": 30},
            {"id": "2", "name": None, "age": 25},  # null name
            {"id": "3", "name": "Charlie", "age": None}  # null age
        ]
        # V1: Bulk insert with nulls
        v1_start = time.perf_counter()
        v1_count = bulk_append_v1(file_path, records_with_nulls)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_all = get_all_matching_v1(file_path, lambda x: True)
        assert len(v1_all) == 3
        assert v1_all[1]["name"] is None
        assert v1_all[2]["age"] is None
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file([])
        # V2: Bulk insert with nulls
        v2_start = time.perf_counter()
        v2_count = bulk_append_v2(file_path, records_with_nulls)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_all = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(v2_all) == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
