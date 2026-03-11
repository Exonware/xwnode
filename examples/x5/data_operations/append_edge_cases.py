#!/usr/bin/env python3
"""Append edge case tests to test_4_delete_operations.py"""

edge_cases = """
# ============================================================================
# 4.5 Edge Cases
# ============================================================================
def test_4_5_1_delete_from_empty_file():
    \"\"\"
    Full Test Name: test_4_5_1_delete_from_empty_file
    Test: Delete from empty file should return False
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_2_delete_nonexistent_id
    Test: Delete non-existent ID should return False
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_3_delete_invalid_line_number
    Test: Delete with invalid line number should return False
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_4_delete_with_missing_id_field
    Test: Delete when ID field is missing from records
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_5_delete_with_duplicate_ids
    Test: Delete when multiple records have same ID (should delete first match)
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_6_delete_with_null_id
    Test: Delete when ID field is None/null
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_7_delete_with_unicode_ids
    Test: Delete with Unicode characters in ID
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_8_delete_last_record
    Test: Delete the last record in file
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_9_delete_first_record
    Test: Delete the first record in file
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_10_delete_all_records
    Test: Delete all records from file
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_11_delete_with_special_characters
    Test: Delete with special characters in ID
    \"\"\"
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
    \"\"\"
    Full Test Name: test_4_5_12_delete_with_very_large_id
    Test: Delete with very large ID value
    \"\"\"
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
"""
if __name__ == "__main__":
    with open("test_4_delete_operations.py", "a", encoding="utf-8") as f:
        f.write(edge_cases)
    print("✅ Edge case tests appended successfully")
