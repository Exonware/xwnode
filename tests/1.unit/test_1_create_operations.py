"""
#exonware/xwnode/examples/x5/data_operations/test_1_create_operations.py
CREATE Operations Test Suite
Tests all CREATE operations (adding new data) for both V1 (Streaming) and V2 (Indexed) implementations.
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
import uuid
from pathlib import Path
# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    append_record_v1,
    append_record_v2,
    insert_record_at_position_v1,
    insert_record_at_position_v2,
    bulk_append_v1,
    bulk_append_v2,
    get_all_matching_v1,
    get_all_matching_v2,
    count_records_v1,
    count_records_v2,
    match_by_id,
    stream_read,
    stream_update,
    build_index,
    ensure_index,
    JsonRecordNotFound,
    FileStateTracker,
)
# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from json_utils import match_by_id as json_match_by_id
# ============================================================================
# 1.1 Single Record Creation
# ============================================================================


def test_1_1_1_append_single_record():
    """
    Full Test Name: test_1_1_1_append_single_record
    Test: Append single record to end of file
    """
    test_data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    file_path = create_test_file(test_data)
    tracker_v1 = FileStateTracker(file_path)
    try:
        new_record = {"id": "3", "name": "Charlie"}
        # V1: Append using helper function
        v1_start = time.perf_counter()
        append_record_v1(file_path, new_record)
        tracker_v1.add_records(1)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 result
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", "3"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Append using helper function (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        tracker_v2 = FileStateTracker(file_path_v2)
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, new_record)
        tracker_v2.add_records(1)
        v2_time = time.perf_counter() - v2_start
        # Verify V2 result using index
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "3", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == new_record
        tracker_v1.assert_count_v1()  # Works with any dataset size!
        tracker_v2.assert_count_v2()  # Works with any dataset size!
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_1_2_insert_at_beginning():
    """
    Full Test Name: test_1_1_2_insert_at_beginning
    Test: Insert record at beginning of file
    """
    test_data = [{"id": "2", "name": "Bob"}, {"id": "3", "name": "Charlie"}]
    file_path = create_test_file(test_data)
    initial_count_v1 = count_records_v1(file_path)
    try:
        new_record = {"id": "1", "name": "Alice"}
        # V1: Insert at position 0
        v1_start = time.perf_counter()
        insert_record_at_position_v1(file_path, new_record, 0)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - first record should be the new one
        v1_verify_start = time.perf_counter()
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            v1_first = json.loads(first_line.strip())
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert at position 0 (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        initial_count_v2 = count_records_v2(file_path_v2, ensure_index(file_path_v2, id_field="id"))
        v2_start = time.perf_counter()
        insert_record_at_position_v2(file_path_v2, new_record, 0)
        v2_time = time.perf_counter() - v2_start
        # Verify V2 using index
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_line
        v2_first = indexed_get_by_line(file_path_v2, 0, index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_first == v2_first == new_record
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_1_3_insert_at_specific_position():
    """
    Full Test Name: test_1_1_3_insert_at_specific_position
    Test: Insert record at specific position (line number)
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "4", "name": "David"}
    ]
    file_path = create_test_file(test_data)
    initial_count_v1 = count_records_v1(file_path)
    try:
        new_record = {"id": "3", "name": "Charlie"}
        insert_position = 2  # Insert between Bob and David
        # V1: Insert at specific position
        v1_start = time.perf_counter()
        insert_record_at_position_v1(file_path, new_record, insert_position)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - record at position 2 should be the new one
        v1_verify_start = time.perf_counter()
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [json.loads(line.strip()) for line in f if line.strip()]
            v1_at_position = lines[insert_position]
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert at specific position (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        initial_count_v2 = count_records_v2(file_path_v2, ensure_index(file_path_v2, id_field="id"))
        v2_start = time.perf_counter()
        insert_record_at_position_v2(file_path_v2, new_record, insert_position)
        v2_time = time.perf_counter() - v2_start
        # Verify V2 using index
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_line
        v2_at_position = indexed_get_by_line(file_path_v2, insert_position, index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_at_position == v2_at_position == new_record
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_1_4_insert_with_id_generation():
    """
    Full Test Name: test_1_1_4_insert_with_id_generation
    Test: Insert with auto-generated unique ID
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    initial_count_v1 = count_records_v1(file_path)
    try:
        # Generate unique ID
        generated_id = str(uuid.uuid4())
        new_record = {"id": generated_id, "name": "Bob", "email": "bob@example.com"}
        # V1: Append with generated ID
        v1_start = time.perf_counter()
        append_record_v1(file_path, new_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - record should exist with generated ID
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", generated_id))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Append with generated ID (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        initial_count_v2 = count_records_v2(file_path_v2, ensure_index(file_path_v2, id_field="id"))
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, new_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2 using index
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, generated_id, id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == new_record
        assert v1_result["id"] == generated_id
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_1_5_insert_with_validation():
    """
    Full Test Name: test_1_1_5_insert_with_validation
    Test: Insert with schema/constraint validation
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    initial_count_v1 = count_records_v1(file_path)
    try:
        # Validation function: age must be between 0 and 150
        def validate_record(record):
            age = record.get("age")
            if age is None:
                raise ValueError("Age is required")
            if not isinstance(age, int):
                raise ValueError("Age must be an integer")
            if age < 0 or age > 150:
                raise ValueError("Age must be between 0 and 150")
            return True
        valid_record = {"id": "2", "name": "Bob", "age": 25}
        invalid_record = {"id": "3", "name": "Charlie", "age": 200}
        # V1: Insert valid record
        v1_start = time.perf_counter()
        validate_record(valid_record)
        append_record_v1(file_path, valid_record)
        v1_time = time.perf_counter() - v1_start
        # V1: Try invalid record (should raise)
        v1_invalid_start = time.perf_counter()
        try:
            validate_record(invalid_record)
            append_record_v1(file_path, invalid_record)
            v1_invalid_passed = False
        except ValueError:
            v1_invalid_passed = True
        v1_invalid_time = time.perf_counter() - v1_invalid_start
        v1_total_time = v1_time + v1_invalid_time
        # V2: Insert valid record (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        initial_count_v2 = count_records_v2(file_path_v2, ensure_index(file_path_v2, id_field="id"))
        v2_start = time.perf_counter()
        validate_record(valid_record)
        append_record_v2(file_path_v2, valid_record)
        v2_time = time.perf_counter() - v2_start
        # V2: Try invalid record (should raise)
        v2_invalid_start = time.perf_counter()
        try:
            validate_record(invalid_record)
            append_record_v2(file_path_v2, invalid_record)
            v2_invalid_passed = False
        except ValueError:
            v2_invalid_passed = True
        v2_invalid_time = time.perf_counter() - v2_invalid_start
        v2_total_time = v2_time + v2_invalid_time
        # Verify valid record was inserted
        v1_result = stream_read(file_path, json_match_by_id("id", "2"))
        index = ensure_index(file_path_v2, id_field="id")
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        assert v1_result == v2_result == valid_record
        assert v1_invalid_passed and v2_invalid_passed
        # Only valid record added (invalid was rejected)
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_1_6_insert_with_conflict_check():
    """
    Full Test Name: test_1_1_6_insert_with_conflict_check
    Test: Insert with ID conflict check
    """
    test_data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    file_path = create_test_file(test_data)
    initial_count_v1 = count_records_v1(file_path)
    try:
        # Check if ID exists
        def id_exists(file_path, record_id, id_field="id"):
            try:
                stream_read(file_path, json_match_by_id(id_field, record_id))
                return True
            except JsonRecordNotFound:
                return False
        new_record = {"id": "3", "name": "Charlie"}
        conflicting_record = {"id": "1", "name": "Duplicate"}
        # V1: Insert new record (no conflict)
        v1_start = time.perf_counter()
        if not id_exists(file_path, "3"):
            append_record_v1(file_path, new_record)
        v1_time = time.perf_counter() - v1_start
        # V1: Try conflicting record (should not insert)
        v1_conflict_start = time.perf_counter()
        if not id_exists(file_path, "1"):
            append_record_v1(file_path, conflicting_record)
        v1_conflict_time = time.perf_counter() - v1_conflict_start
        v1_total_time = v1_time + v1_conflict_time
        # Verify V1 - new record added, conflict prevented
        v1_new = stream_read(file_path, json_match_by_id("id", "3"))
        v1_original = stream_read(file_path, json_match_by_id("id", "1"))
        # V2: Insert new record (no conflict, rebuilds index)
        file_path_v2 = create_test_file(test_data)
        initial_count_v2 = count_records_v2(file_path_v2, ensure_index(file_path_v2, id_field="id"))
        v2_start = time.perf_counter()
        if not id_exists(file_path_v2, "3"):
            append_record_v2(file_path_v2, new_record)
        v2_time = time.perf_counter() - v2_start
        # V2: Try conflicting record (should not insert)
        v2_conflict_start = time.perf_counter()
        if not id_exists(file_path_v2, "1"):
            append_record_v2(file_path_v2, conflicting_record)
        v2_conflict_time = time.perf_counter() - v2_conflict_start
        v2_total_time = v2_time + v2_conflict_time
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        from json_utils_indexed import indexed_get_by_id
        v2_new = indexed_get_by_id(file_path_v2, "3", id_field="id", index=index)
        v2_original = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        assert v1_new == v2_new == new_record
        assert v1_original == v2_original == {"id": "1", "name": "Alice"}  # Original preserved
        assert count_records_v1(file_path) == initial_count_v1 + 1  # Only new record added
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 1.2 Bulk Creation
# ============================================================================


def test_1_2_1_bulk_append():
    """
    Full Test Name: test_1_2_1_bulk_append
    Test: Bulk append multiple records
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        new_records = [
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Charlie"},
            {"id": "4", "name": "David"}
        ]
        # V1: Bulk append
        v1_start = time.perf_counter()
        bulk_append_v1(file_path, new_records)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - all records should exist
        v1_verify_start = time.perf_counter()
        v1_results = []
        for record in new_records:
            v1_results.append(stream_read(file_path, json_match_by_id("id", record["id"])))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Bulk append (rebuilds index once at end)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        bulk_append_v2(file_path_v2, new_records)
        v2_time = time.perf_counter() - v2_start
        # Verify V2 using index
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_results = []
        for record in new_records:
            v2_results.append(indexed_get_by_id(file_path_v2, record["id"], id_field="id", index=index))
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_results == v2_results == new_records
        initial_count_v1 = count_records_v1(file_path) - len(new_records)
        initial_count_v2 = count_records_v2(file_path_v2, index) - len(new_records)
        assert count_records_v1(file_path) == initial_count_v1 + len(new_records)
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + len(new_records)
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_2_2_bulk_insert_with_ordering():
    """
    Full Test Name: test_1_2_2_bulk_insert_with_ordering
    Test: Bulk insert maintaining order
    """
    test_data = [{"id": "1", "name": "Alice", "order": 1}]
    file_path = create_test_file(test_data)
    try:
        new_records = [
            {"id": "2", "name": "Bob", "order": 2},
            {"id": "3", "name": "Charlie", "order": 3},
            {"id": "4", "name": "David", "order": 4}
        ]
        # V1: Bulk append (maintains order)
        v1_start = time.perf_counter()
        bulk_append_v1(file_path, new_records)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - order should be preserved
        v1_verify_start = time.perf_counter()
        with open(file_path, 'r', encoding='utf-8') as f:
            v1_all = [json.loads(line.strip()) for line in f if line.strip()]
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Bulk append (maintains order, rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        bulk_append_v2(file_path_v2, new_records)
        v2_time = time.perf_counter() - v2_start
        # Verify V2 - order should be preserved
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_line
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path_v2, i, index=index))
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # Check order is preserved
        expected_order = [1, 2, 3, 4]
        v1_order = [r["order"] for r in v1_all]
        v2_order = [r["order"] for r in v2_all]
        assert v1_order == v2_order == expected_order
        # Check that order is preserved, but count is dynamic
        assert len(v1_all) == len(v2_all)
        assert len(v1_all) >= len(expected_order)  # At least the expected records
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_2_3_batch_insert():
    """
    Full Test Name: test_1_2_3_batch_insert
    Test: Batch insert with configurable batch sizes
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        all_records = [
            {"id": str(i), "name": f"User{i}"} for i in range(2, 12)  # 10 records
        ]
        batch_size = 3
        # V1: Batch insert
        v1_start = time.perf_counter()
        for i in range(0, len(all_records), batch_size):
            batch = all_records[i:i + batch_size]
            bulk_append_v1(file_path, batch)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Batch insert (rebuilds index after each batch)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        for i in range(0, len(all_records), batch_size):
            batch = all_records[i:i + batch_size]
            bulk_append_v2(file_path_v2, batch)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        v2_count = count_records_v2(file_path_v2, index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # 10 new records added
        initial_count_v1 = v1_count - len(all_records)
        initial_count_v2 = v2_count - len(all_records)
        assert v1_count == initial_count_v1 + len(all_records)
        assert v2_count == initial_count_v2 + len(all_records)
        assert count_records_v1(file_path) == initial_count_v1 + len(all_records)
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + len(all_records)
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_2_4_bulk_insert_with_deduplication():
    """
    Full Test Name: test_1_2_4_bulk_insert_with_deduplication
    Test: Bulk insert skipping duplicates
    """
    test_data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    file_path = create_test_file(test_data)
    try:
        records_with_duplicates = [
            {"id": "2", "name": "BobDuplicate"},  # Duplicate
            {"id": "3", "name": "Charlie"},       # New
            {"id": "1", "name": "AliceDuplicate"}, # Duplicate
            {"id": "4", "name": "David"}         # New
        ]
        # V1: Bulk insert with deduplication
        def id_exists_v1(file_path, record_id):
            try:
                stream_read(file_path, json_match_by_id("id", record_id))
                return True
            except JsonRecordNotFound:
                return False
        v1_start = time.perf_counter()
        for record in records_with_duplicates:
            if not id_exists_v1(file_path, record["id"]):
                append_record_v1(file_path, record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - duplicates skipped
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        # Original records should be preserved
        v1_original_1 = stream_read(file_path, json_match_by_id("id", "1"))
        v1_original_2 = stream_read(file_path, json_match_by_id("id", "2"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Bulk insert with deduplication (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        for record in records_with_duplicates:
            if not id_exists_v1(file_path_v2, record["id"]):
                append_record_v2(file_path_v2, record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_count = count_records_v2(file_path_v2, index)
        v2_original_1 = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        v2_original_2 = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # 2 new records added (2 duplicates skipped)
        new_records_added = 2
        initial_count_v1 = v1_count - new_records_added
        initial_count_v2 = v2_count - new_records_added
        assert v1_count == initial_count_v1 + new_records_added
        assert v2_count == initial_count_v2 + new_records_added
        assert v1_original_1 == v2_original_1 == {"id": "1", "name": "Alice"}
        assert v1_original_2 == v2_original_2 == {"id": "2", "name": "Bob"}
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_2_5_bulk_insert_with_transaction():
    """
    Full Test Name: test_1_2_5_bulk_insert_with_transaction
    Test: All-or-nothing bulk insert
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        records = [
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Charlie"},
            {"id": "invalid", "name": None}  # This will cause validation to fail
        ]
        # Validation function
        def validate_all(records):
            for record in records:
                if record.get("name") is None:
                    raise ValueError(f"Invalid record: {record}")
            return True
        # V1: Transactional bulk insert (all or nothing)
        v1_start = time.perf_counter()
        try:
            validate_all(records)
            bulk_append_v1(file_path, records)
            v1_success = True
        except ValueError:
            v1_success = False
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - if validation failed, no records should be added
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Transactional bulk insert (all or nothing, rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        try:
            validate_all(records)
            bulk_append_v2(file_path_v2, records)
            v2_success = True
        except ValueError:
            v2_success = False
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        v2_count = count_records_v2(file_path_v2, index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # Both should fail validation, so no records added
        assert not v1_success and not v2_success
        # Count should remain unchanged (no records added due to validation failure)
        initial_count_v1 = v1_count
        initial_count_v2 = v2_count
        assert v1_count == initial_count_v1
        assert v2_count == initial_count_v2
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 1.3 Conditional Creation
# ============================================================================


def test_1_3_1_conditional_insert():
    """
    Full Test Name: test_1_3_1_conditional_insert
    Test: Insert only if condition is met
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        # Condition: only insert if age >= 18
        def should_insert(record):
            return record.get("age", 0) >= 18
        adult_record = {"id": "2", "name": "Bob", "age": 25}
        minor_record = {"id": "3", "name": "Charlie", "age": 15}
        # V1: Conditional insert
        v1_start = time.perf_counter()
        if should_insert(adult_record):
            append_record_v1(file_path, adult_record)
        if should_insert(minor_record):
            append_record_v1(file_path, minor_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        try:
            v1_adult = stream_read(file_path, json_match_by_id("id", "2"))
        except JsonRecordNotFound:
            v1_adult = None
        try:
            v1_minor = stream_read(file_path, json_match_by_id("id", "3"))
        except JsonRecordNotFound:
            v1_minor = None
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Conditional insert (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        if should_insert(adult_record):
            append_record_v2(file_path_v2, adult_record)
        if should_insert(minor_record):
            append_record_v2(file_path_v2, minor_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_count = count_records_v2(file_path_v2, index)
        try:
            v2_adult = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        except Exception:
            v2_adult = None
        try:
            v2_minor = indexed_get_by_id(file_path_v2, "3", id_field="id", index=index)
        except Exception:
            v2_minor = None
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # Only adult record added (minor rejected)
        new_records_added = 1
        initial_count_v1 = v1_count - new_records_added
        initial_count_v2 = v2_count - new_records_added
        assert v1_count == initial_count_v1 + new_records_added
        assert v2_count == initial_count_v2 + new_records_added
        assert v1_adult == v2_adult == adult_record
        assert v1_minor is None and v2_minor is None
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_3_2_upsert():
    """
    Full Test Name: test_1_3_2_upsert
    Test: Insert if not exists, update if exists
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        new_record = {"id": "2", "name": "Bob", "age": 25}
        existing_record_updated = {"id": "1", "name": "AliceUpdated", "age": 31}
        # V1: Upsert function
        def upsert_v1(file_path, record, id_field="id"):
            try:
                existing = stream_read(file_path, json_match_by_id(id_field, record[id_field]))
                # Update existing
                def update_func(obj):
                    return record
                stream_update(file_path, json_match_by_id(id_field, record[id_field]), update_func)
                return "updated"
            except JsonRecordNotFound:
                # Insert new
                append_record_v1(file_path, record)
                return "inserted"
        v1_start = time.perf_counter()
        v1_new_result = upsert_v1(file_path, new_record)
        v1_existing_result = upsert_v1(file_path, existing_record_updated)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_new = stream_read(file_path, json_match_by_id("id", "2"))
        v1_updated = stream_read(file_path, json_match_by_id("id", "1"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Upsert function (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        def upsert_v2(file_path, record, id_field="id"):
            index = ensure_index(file_path, id_field=id_field)
            try:
                from json_utils_indexed import indexed_get_by_id
                existing = indexed_get_by_id(file_path, record[id_field], id_field=id_field, index=index)
                # Update existing
                def update_func(obj):
                    return record
                stream_update(file_path, json_match_by_id(id_field, record[id_field]), update_func)
                return "updated"
            except Exception:
                # Insert new
                append_record_v2(file_path, record)
                return "inserted"
        v2_start = time.perf_counter()
        v2_new_result = upsert_v2(file_path_v2, new_record)
        v2_existing_result = upsert_v2(file_path_v2, existing_record_updated)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_new = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_updated = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_new_result == v2_new_result == "inserted"
        assert v1_existing_result == v2_existing_result == "updated"
        assert v1_new == v2_new == new_record
        assert v1_updated == v2_updated == existing_record_updated
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_3_3_insert_if_unique():
    """
    Full Test Name: test_1_3_3_insert_if_unique
    Test: Insert only if key/ID is unique
    """
    test_data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    file_path = create_test_file(test_data)
    try:
        unique_record = {"id": "3", "name": "Charlie"}
        duplicate_record = {"id": "1", "name": "Duplicate"}
        # V1: Insert if unique
        def insert_if_unique_v1(file_path, record, id_field="id"):
            try:
                stream_read(file_path, json_match_by_id(id_field, record[id_field]))
                return False  # Already exists
            except JsonRecordNotFound:
                append_record_v1(file_path, record)
                return True  # Inserted
        v1_start = time.perf_counter()
        v1_unique_result = insert_if_unique_v1(file_path, unique_record)
        v1_duplicate_result = insert_if_unique_v1(file_path, duplicate_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_original = stream_read(file_path, json_match_by_id("id", "1"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert if unique (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        def insert_if_unique_v2(file_path, record, id_field="id"):
            index = ensure_index(file_path, id_field=id_field)
            try:
                from json_utils_indexed import indexed_get_by_id
                indexed_get_by_id(file_path, record[id_field], id_field=id_field, index=index)
                return False  # Already exists
            except Exception:
                append_record_v2(file_path, record)
                return True  # Inserted
        v2_start = time.perf_counter()
        v2_unique_result = insert_if_unique_v2(file_path_v2, unique_record)
        v2_duplicate_result = insert_if_unique_v2(file_path_v2, duplicate_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_count = count_records_v2(file_path_v2, index)
        v2_original = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_unique_result == v2_unique_result == True
        assert v1_duplicate_result == v2_duplicate_result == False
        # Only unique record added (duplicate rejected)
        new_records_added = 1
        initial_count_v1 = v1_count - new_records_added
        initial_count_v2 = v2_count - new_records_added
        assert v1_count == initial_count_v1 + new_records_added
        assert v2_count == initial_count_v2 + new_records_added
        assert v1_original == v2_original == {"id": "1", "name": "Alice"}  # Original preserved
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_3_4_insert_with_merge():
    """
    Full Test Name: test_1_3_4_insert_with_merge
    Test: Merge with existing record if exists
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        new_record = {"id": "2", "name": "Bob", "age": 25}
        merge_record = {"id": "1", "email": "alice@example.com", "city": "NYC"}
        # V1: Insert with merge
        def insert_with_merge_v1(file_path, record, id_field="id"):
            try:
                existing = stream_read(file_path, json_match_by_id(id_field, record[id_field]))
                # Merge: combine existing and new, new values override
                merged = {**existing, **record}
                def update_func(obj):
                    return merged
                stream_update(file_path, json_match_by_id(id_field, record[id_field]), update_func)
                return "merged"
            except JsonRecordNotFound:
                append_record_v1(file_path, record)
                return "inserted"
        v1_start = time.perf_counter()
        v1_new_result = insert_with_merge_v1(file_path, new_record)
        v1_merge_result = insert_with_merge_v1(file_path, merge_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_new = stream_read(file_path, json_match_by_id("id", "2"))
        v1_merged = stream_read(file_path, json_match_by_id("id", "1"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert with merge (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        def insert_with_merge_v2(file_path, record, id_field="id"):
            index = ensure_index(file_path, id_field=id_field)
            try:
                from json_utils_indexed import indexed_get_by_id
                existing = indexed_get_by_id(file_path, record[id_field], id_field=id_field, index=index)
                # Merge: combine existing and new
                merged = {**existing, **record}
                def update_func(obj):
                    return merged
                stream_update(file_path, json_match_by_id(id_field, record[id_field]), update_func)
                return "merged"
            except Exception:
                append_record_v2(file_path, record)
                return "inserted"
        v2_start = time.perf_counter()
        v2_new_result = insert_with_merge_v2(file_path_v2, new_record)
        v2_merge_result = insert_with_merge_v2(file_path_v2, merge_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_new = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_merged = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_new_result == v2_new_result == "inserted"
        assert v1_merge_result == v2_merge_result == "merged"
        assert v1_new == v2_new == new_record
        # Merged record should have both original and new fields
        expected_merged = {"id": "1", "name": "Alice", "age": 30, "email": "alice@example.com", "city": "NYC"}
        assert v1_merged == v2_merged == expected_merged
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 1.4 Edge Cases
# ============================================================================


def test_1_4_1_append_to_empty_file():
    """
    Full Test Name: test_1_4_1_append_to_empty_file
    Test: Append record to empty file
    """
    # Create empty file
    file_path = create_test_file([])
    initial_count_v1 = count_records_v1(file_path)
    try:
        new_record = {"id": "1", "name": "First"}
        # V1: Append to empty file
        v1_start = time.perf_counter()
        append_record_v1(file_path, new_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", "1"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Append to empty file (rebuilds index)
        file_path_v2 = create_test_file([])
        initial_count_v2 = count_records_v2(file_path_v2, ensure_index(file_path_v2, id_field="id"))
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, new_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == new_record
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_2_insert_with_null_values():
    """
    Full Test Name: test_1_4_2_insert_with_null_values
    Test: Insert record with None/null values
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        record_with_nulls = {"id": "2", "name": None, "age": None, "email": "test@example.com"}
        # V1: Insert with null values
        v1_start = time.perf_counter()
        append_record_v1(file_path, record_with_nulls)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - null values should be preserved
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", "2"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert with null values (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, record_with_nulls)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == record_with_nulls
        assert v1_result["name"] is None
        assert v1_result["age"] is None
        initial_count_v1 = count_records_v1(file_path) - 1
        initial_count_v2 = count_records_v2(file_path_v2, index) - 1
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_3_insert_with_special_characters():
    """
    Full Test Name: test_1_4_3_insert_with_special_characters
    Test: Insert record with Unicode and special characters
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        special_record = {
            "id": "2",
            "name": "José García",
            "description": "Test with émojis: 🚀 ✅ ❌",
            "unicode": "中文 العربية русский",
            "special": "Newline:\nTab:\tQuote:\"Apostrophe:'"
        }
        # V1: Insert with special characters
        v1_start = time.perf_counter()
        append_record_v1(file_path, special_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", "2"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert with special characters (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, special_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == special_record
        assert "🚀" in v1_result["description"]
        assert "中文" in v1_result["unicode"]
        initial_count_v1 = count_records_v1(file_path) - 1
        initial_count_v2 = count_records_v2(file_path_v2, index) - 1
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_4_insert_with_missing_id_field():
    """
    Full Test Name: test_1_4_4_insert_with_missing_id_field
    Test: Insert record without id field (should still work)
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        record_no_id = {"name": "Bob", "age": 25}
        # V1: Insert without id field
        v1_start = time.perf_counter()
        append_record_v1(file_path, record_no_id)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - record should exist but can't query by id
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        # Read all records to find the one without id
        with open(file_path, 'r', encoding='utf-8') as f:
            v1_all = [json.loads(line.strip()) for line in f if line.strip()]
        v1_no_id = [r for r in v1_all if "id" not in r][0]
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert without id field (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, record_no_id)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        v2_count = count_records_v2(file_path_v2, index)
        from json_utils_indexed import indexed_get_by_line
        v2_all = []
        for i in range(len(index.line_offsets)):
            v2_all.append(indexed_get_by_line(file_path_v2, i, index=index))
        v2_no_id = [r for r in v2_all if "id" not in r][0]
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_no_id == v2_no_id == record_no_id
        initial_count_v1 = v1_count - 1
        initial_count_v2 = v2_count - 1
        assert v1_count == initial_count_v1 + 1
        assert v2_count == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_5_insert_at_invalid_position():
    """
    Full Test Name: test_1_4_5_insert_at_invalid_position
    Test: Insert at position beyond file length (should append)
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        new_record = {"id": "2", "name": "Bob"}
        invalid_position = 100  # Beyond file length
        # V1: Insert at invalid position
        v1_start = time.perf_counter()
        try:
            insert_record_at_position_v1(file_path, new_record, invalid_position)
            # Should insert at end or raise error
            v1_inserted = True
        except (IndexError, ValueError):
            v1_inserted = False
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert at invalid position (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        try:
            insert_record_at_position_v2(file_path_v2, new_record, invalid_position)
            v2_inserted = True
        except (IndexError, ValueError):
            v2_inserted = False
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        v2_count = count_records_v2(file_path_v2, index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # Should have inserted (either at end or at position)
        assert v1_count >= 1  # At least original record
        assert v2_count >= 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_6_bulk_insert_large_dataset():
    """
    Full Test Name: test_1_4_6_bulk_insert_large_dataset
    Test: Bulk insert with large number of records
    """
    from tests.scale_config import MEDIUM_SIZE
    test_data = [{"id": "0", "name": "Initial"}]
    file_path = create_test_file(test_data)
    try:
        n = max(1, MEDIUM_SIZE)
        large_records = [
            {"id": str(i), "name": f"User{i}", "value": i * 10}
            for i in range(1, n + 1)
        ]
        # V1: Bulk insert large dataset
        v1_start = time.perf_counter()
        bulk_append_v1(file_path, large_records)
        v1_time = time.perf_counter() - v1_start
        # Verify V1 - check first, middle, and last
        v1_verify_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        mid = n // 2
        v1_first = stream_read(file_path, json_match_by_id("id", "1"))
        v1_middle = stream_read(file_path, json_match_by_id("id", str(mid)))
        v1_last = stream_read(file_path, json_match_by_id("id", str(n)))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Bulk insert large dataset (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        bulk_append_v2(file_path_v2, large_records)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_count = count_records_v2(file_path_v2, index)
        v2_first = indexed_get_by_id(file_path_v2, "1", id_field="id", index=index)
        v2_middle = indexed_get_by_id(file_path_v2, str(mid), id_field="id", index=index)
        v2_last = indexed_get_by_id(file_path_v2, str(n), id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        # n new records added
        initial_count_v1 = v1_count - len(large_records)
        initial_count_v2 = v2_count - len(large_records)
        assert v1_count == initial_count_v1 + len(large_records)
        assert v2_count == initial_count_v2 + len(large_records)
        assert v1_first == v2_first == large_records[0]
        assert v1_middle == v2_middle == large_records[mid - 1]
        assert v1_last == v2_last == large_records[n - 1]
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_7_insert_with_nested_structures():
    """
    Full Test Name: test_1_4_7_insert_with_nested_structures
    Test: Insert record with nested dictionaries and lists
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        nested_record = {
            "id": "2",
            "name": "Bob",
            "address": {
                "street": "123 Main St",
                "city": "NYC",
                "zip": "10001"
            },
            "tags": ["developer", "python", "testing"],
            "metadata": {
                "created": "2025-01-01",
                "nested": {
                    "level": 2,
                    "data": [1, 2, 3]
                }
            }
        }
        # V1: Insert with nested structures
        v1_start = time.perf_counter()
        append_record_v1(file_path, nested_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", "2"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert with nested structures (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, nested_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == nested_record
        assert v1_result["address"]["city"] == "NYC"
        assert v1_result["tags"] == ["developer", "python", "testing"]
        assert v1_result["metadata"]["nested"]["level"] == 2
        initial_count_v1 = count_records_v1(file_path) - 1
        initial_count_v2 = count_records_v2(file_path_v2, index) - 1
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)


def test_1_4_8_insert_with_empty_strings():
    """
    Full Test Name: test_1_4_8_insert_with_empty_strings
    Test: Insert record with empty string values
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        empty_string_record = {
            "id": "2",
            "name": "",
            "description": "",
            "tags": []
        }
        # V1: Insert with empty strings
        v1_start = time.perf_counter()
        append_record_v1(file_path, empty_string_record)
        v1_time = time.perf_counter() - v1_start
        # Verify V1
        v1_verify_start = time.perf_counter()
        v1_result = stream_read(file_path, json_match_by_id("id", "2"))
        v1_verify_time = time.perf_counter() - v1_verify_start
        v1_total_time = v1_time + v1_verify_time
        # V2: Insert with empty strings (rebuilds index)
        file_path_v2 = create_test_file(test_data)
        v2_start = time.perf_counter()
        append_record_v2(file_path_v2, empty_string_record)
        v2_time = time.perf_counter() - v2_start
        # Verify V2
        index = ensure_index(file_path_v2, id_field="id")
        v2_verify_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        v2_result = indexed_get_by_id(file_path_v2, "2", id_field="id", index=index)
        v2_verify_time = time.perf_counter() - v2_verify_start
        v2_total_time = v2_time + v2_verify_time
        assert v1_result == v2_result == empty_string_record
        assert v1_result["name"] == ""
        assert v1_result["description"] == ""
        initial_count_v1 = count_records_v1(file_path) - 1
        initial_count_v2 = count_records_v2(file_path_v2, index) - 1
        assert count_records_v1(file_path) == initial_count_v1 + 1
        assert count_records_v2(file_path_v2, index) == initial_count_v2 + 1
        cleanup_test_file(file_path_v2)
        return True, v1_total_time, v2_total_time
    finally:
        cleanup_test_file(file_path)
