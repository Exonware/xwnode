"""
#exonware/xwnode/examples/x5/data_operations/test_10_validation_operations.py
VALIDATION Operations Test Suite
Tests all VALIDATION operations (data integrity) for both V1 (Streaming) and V2 (Indexed) implementations.
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
    append_record_v1,
    append_record_v2,
    get_all_matching_v1,
    get_all_matching_v2,
    stream_read,
)
# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from json_utils import (
    match_by_id,
    stream_update,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_id,
    indexed_get_by_line,
)
# ============================================================================
# Validation Helper Functions
# ============================================================================


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))
# ============================================================================
# 10.1 Schema Validation
# ============================================================================


def test_10_1_1_validate_schema():
    """
    Full Test Name: test_10_1_1_validate_schema
    Test: Check record against schema
    """
    schema = {
        "id": str,
        "name": str,
        "age": int
    }
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        def validate_against_schema(record, schema):
            for field, expected_type in schema.items():
                if field not in record:
                    return False, f"Missing field: {field}"
                if not isinstance(record[field], expected_type):
                    return False, f"Field {field} has wrong type"
            return True, None
        # V1: Validate schema
        v1_start = time.perf_counter()
        record = stream_read(file_path, match_by_id("id", "1"))
        v1_valid, v1_error = validate_against_schema(record, schema)
        v1_time = time.perf_counter() - v1_start
        assert v1_valid
        # V2: Validate schema
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        record_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        v2_valid, v2_error = validate_against_schema(record_v2, schema)
        v2_time = time.perf_counter() - v2_start
        assert v2_valid
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_1_2_validate_required_fields():
    """
    Full Test Name: test_10_1_2_validate_required_fields
    Test: Ensure required fields present
    """
    required_fields = ["id", "name", "email"]
    test_data = [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob"}  # Missing email
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_required(record, required):
            missing = [field for field in required if field not in record]
            return len(missing) == 0, missing
        # V1: Validate required fields
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_valid_count = 0
        for record in records:
            valid, missing = validate_required(record, required_fields)
            if valid:
                v1_valid_count += 1
        v1_time = time.perf_counter() - v1_start
        assert v1_valid_count == 1
        # V2: Validate required fields
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_valid_count = 0
        for record in records_v2:
            valid, missing = validate_required(record, required_fields)
            if valid:
                v2_valid_count += 1
        v2_time = time.perf_counter() - v2_start
        assert v2_valid_count == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_1_3_validate_field_types():
    """
    Full Test Name: test_10_1_3_validate_field_types
    Test: Check field types match schema
    """
    field_types = {
        "id": str,
        "age": int,
        "score": float
    }
    test_data = [
        {"id": "1", "age": 30, "score": 85.5},
        {"id": "2", "age": "25", "score": 90.0}  # age is string, should be int
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_types(record, types):
            for field, expected_type in types.items():
                if field in record and not isinstance(record[field], expected_type):
                    return False, f"Field {field} has wrong type"
            return True, None
        # V1: Validate field types
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_valid_count = 0
        for record in records:
            valid, error = validate_types(record, field_types)
            if valid:
                v1_valid_count += 1
        v1_time = time.perf_counter() - v1_start
        assert v1_valid_count == 1
        # V2: Validate field types
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_valid_count = 0
        for record in records_v2:
            valid, error = validate_types(record, field_types)
            if valid:
                v2_valid_count += 1
        v2_time = time.perf_counter() - v2_start
        assert v2_valid_count == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_1_4_validate_field_formats():
    """
    Full Test Name: test_10_1_4_validate_field_formats
    Test: Check formats (email, date, etc.)
    """
    test_data = [
        {"id": "1", "email": "alice@example.com", "date": "2024-01-15"},
        {"id": "2", "email": "invalid-email", "date": "2024-01-15"},
        {"id": "3", "email": "bob@example.com", "date": "invalid-date"}
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_formats(record):
            errors = []
            if "email" in record and not validate_email(record["email"]):
                errors.append("Invalid email format")
            if "date" in record and not validate_date(record["date"]):
                errors.append("Invalid date format")
            return len(errors) == 0, errors
        # V1: Validate field formats
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_valid_count = 0
        for record in records:
            valid, errors = validate_formats(record)
            if valid:
                v1_valid_count += 1
        v1_time = time.perf_counter() - v1_start
        assert v1_valid_count == 1
        # V2: Validate field formats
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_valid_count = 0
        for record in records_v2:
            valid, errors = validate_formats(record)
            if valid:
                v2_valid_count += 1
        v2_time = time.perf_counter() - v2_start
        assert v2_valid_count == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_1_5_validate_constraints():
    """
    Full Test Name: test_10_1_5_validate_constraints
    Test: Check constraints (min, max, etc.)
    """
    constraints = {
        "age": {"min": 18, "max": 100},
        "score": {"min": 0, "max": 100}
    }
    test_data = [
        {"id": "1", "age": 30, "score": 85},
        {"id": "2", "age": 15, "score": 85},  # age < min
        {"id": "3", "age": 30, "score": 150}  # score > max
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_constraints(record, constraints):
            errors = []
            for field, constraint in constraints.items():
                if field in record:
                    value = record[field]
                    if "min" in constraint and value < constraint["min"]:
                        errors.append(f"{field} below minimum")
                    if "max" in constraint and value > constraint["max"]:
                        errors.append(f"{field} above maximum")
            return len(errors) == 0, errors
        # V1: Validate constraints
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_valid_count = 0
        for record in records:
            valid, errors = validate_constraints(record, constraints)
            if valid:
                v1_valid_count += 1
        v1_time = time.perf_counter() - v1_start
        assert v1_valid_count == 1
        # V2: Validate constraints
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_valid_count = 0
        for record in records_v2:
            valid, errors = validate_constraints(record, constraints)
            if valid:
                v2_valid_count += 1
        v2_time = time.perf_counter() - v2_start
        assert v2_valid_count == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 10.2 Data Validation
# ============================================================================


def test_10_2_1_validate_uniqueness():
    """
    Full Test Name: test_10_2_1_validate_uniqueness
    Test: Check ID/keys are unique
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "1", "name": "Charlie"}  # Duplicate ID
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_uniqueness(filepath, id_field="id"):
            ids = set()
            duplicates = []
            records = get_all_matching_v1(filepath, lambda x: True)
            for record in records:
                record_id = record.get(id_field)
                if record_id in ids:
                    duplicates.append(record_id)
                ids.add(record_id)
            return len(duplicates) == 0, duplicates
        # V1: Validate uniqueness
        v1_start = time.perf_counter()
        v1_valid, v1_duplicates = validate_uniqueness(file_path)
        v1_time = time.perf_counter() - v1_start
        assert not v1_valid
        assert len(v1_duplicates) > 0
        # V2: Validate uniqueness
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        # Check if index has duplicates (same ID mapping to different lines)
        id_to_lines = {}
        for i in range(len(index.line_offsets)):
            record = indexed_get_by_line(file_path, i, index=index)
            record_id = record.get("id")
            if record_id not in id_to_lines:
                id_to_lines[record_id] = []
            id_to_lines[record_id].append(i)
        v2_duplicates = [rid for rid, lines in id_to_lines.items() if len(lines) > 1]
        v2_valid = len(v2_duplicates) == 0
        v2_time = time.perf_counter() - v2_start
        assert not v2_valid
        assert len(v2_duplicates) > 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_2_2_validate_references():
    """
    Full Test Name: test_10_2_2_validate_references
    Test: Check foreign key references
    """
    users_data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    orders_data = [
        {"id": "o1", "user_id": "1", "amount": 100},
        {"id": "o2", "user_id": "3", "amount": 200}  # Invalid reference
    ]
    users_file = create_test_file(users_data)
    orders_file = create_test_file(orders_data)
    try:
        def validate_references(orders_filepath, users_filepath, foreign_key="user_id"):
            user_ids = {r.get("id") for r in get_all_matching_v1(users_filepath, lambda x: True)}
            orders = get_all_matching_v1(orders_filepath, lambda x: True)
            invalid_refs = []
            for order in orders:
                ref_id = order.get(foreign_key)
                if ref_id not in user_ids:
                    invalid_refs.append(order.get("id"))
            return len(invalid_refs) == 0, invalid_refs
        # V1: Validate references
        v1_start = time.perf_counter()
        v1_valid, v1_invalid = validate_references(orders_file, users_file)
        v1_time = time.perf_counter() - v1_start
        assert not v1_valid
        assert len(v1_invalid) > 0
        # V2: Validate references
        users_index = ensure_index(users_file, id_field="id")
        orders_index = ensure_index(orders_file, id_field="id")
        v2_start = time.perf_counter()
        user_ids = {r.get("id") for r in get_all_matching_v2(users_file, lambda x: True, index=users_index)}
        orders = get_all_matching_v2(orders_file, lambda x: True, index=orders_index)
        v2_invalid = [o.get("id") for o in orders if o.get("user_id") not in user_ids]
        v2_valid = len(v2_invalid) == 0
        v2_time = time.perf_counter() - v2_start
        assert not v2_valid
        assert len(v2_invalid) > 0
        cleanup_test_file(users_file)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(orders_file)


def test_10_2_3_validate_relationships():
    """
    Full Test Name: test_10_2_3_validate_relationships
    Test: Check relationship integrity
    """
    test_data = [
        {"id": "1", "parent_id": None, "name": "Root"},
        {"id": "2", "parent_id": "1", "name": "Child1"},
        {"id": "3", "parent_id": "1", "name": "Child2"},
        {"id": "4", "parent_id": "99", "name": "Orphan"}  # Invalid parent
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_relationships(filepath):
            records = get_all_matching_v1(filepath, lambda x: True)
            ids = {r.get("id") for r in records}
            invalid = []
            for record in records:
                parent_id = record.get("parent_id")
                if parent_id is not None and parent_id not in ids:
                    invalid.append(record.get("id"))
            return len(invalid) == 0, invalid
        # V1: Validate relationships
        v1_start = time.perf_counter()
        v1_valid, v1_invalid = validate_relationships(file_path)
        v1_time = time.perf_counter() - v1_start
        assert not v1_valid
        assert len(v1_invalid) > 0
        # V2: Validate relationships
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records = get_all_matching_v2(file_path, lambda x: True, index=index)
        ids = {r.get("id") for r in records}
        v2_invalid = [r.get("id") for r in records if r.get("parent_id") is not None and r.get("parent_id") not in ids]
        v2_valid = len(v2_invalid) == 0
        v2_time = time.perf_counter() - v2_start
        assert not v2_valid
        assert len(v2_invalid) > 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_2_4_validate_business_rules():
    """
    Full Test Name: test_10_2_4_validate_business_rules
    Test: Check custom business logic
    """
    test_data = [
        {"id": "1", "type": "order", "amount": 100, "status": "pending"},
        {"id": "2", "type": "order", "amount": 0, "status": "pending"},  # Invalid: amount must be > 0
        {"id": "3", "type": "order", "amount": 200, "status": "completed"}  # Valid
    ]
    file_path = create_test_file(test_data)
    try:
        def validate_business_rules(record):
            errors = []
            if record.get("type") == "order":
                if record.get("amount", 0) <= 0:
                    errors.append("Order amount must be greater than 0")
                if record.get("status") == "completed" and record.get("amount", 0) <= 0:
                    errors.append("Completed order must have amount > 0")
            return len(errors) == 0, errors
        # V1: Validate business rules
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_valid_count = 0
        for record in records:
            valid, errors = validate_business_rules(record)
            if valid:
                v1_valid_count += 1
        v1_time = time.perf_counter() - v1_start
        assert v1_valid_count == 2
        # V2: Validate business rules
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_valid_count = 0
        for record in records_v2:
            valid, errors = validate_business_rules(record)
            if valid:
                v2_valid_count += 1
        v2_time = time.perf_counter() - v2_start
        assert v2_valid_count == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_2_5_validate_on_insert():
    """
    Full Test Name: test_10_2_5_validate_on_insert
    Test: Validate before inserting
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        def validate_record(record):
            if not isinstance(record.get("name"), str) or not record.get("name"):
                return False, "Name is required"
            if not isinstance(record.get("age"), int) or record.get("age") < 0:
                return False, "Age must be non-negative integer"
            return True, None
        valid_record = {"id": "2", "name": "Bob", "age": 25}
        invalid_record = {"id": "3", "name": "", "age": -5}
        # V1: Validate on insert
        v1_start = time.perf_counter()
        valid, error = validate_record(valid_record)
        if valid:
            append_record_v1(file_path, valid_record)
        valid2, error2 = validate_record(invalid_record)
        if not valid2:
            # Don't insert invalid record
            pass
        v1_time = time.perf_counter() - v1_start
        records = get_all_matching_v1(file_path, lambda x: True)
        assert len(records) == 2
        assert all(r.get("id") != "3" for r in records)
        # V2: Validate on insert
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        v2_start = time.perf_counter()
        valid_v2, error_v2 = validate_record(valid_record)
        if valid_v2:
            append_record_v2(file_path, valid_record)
        valid2_v2, error2_v2 = validate_record(invalid_record)
        if not valid2_v2:
            pass
        v2_time = time.perf_counter() - v2_start
        index = ensure_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(records_v2) == 2
        assert all(r.get("id") != "3" for r in records_v2)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_10_2_6_validate_on_update():
    """
    Full Test Name: test_10_2_6_validate_on_update
    Test: Validate before updating
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        def validate_update(record):
            if "age" in record and (not isinstance(record["age"], int) or record["age"] < 0):
                return False, "Age must be non-negative integer"
            return True, None
        # V1: Validate on update
        v1_start = time.perf_counter()
        update_data = {"age": 31}
        valid, error = validate_update(update_data)
        if valid:
            stream_update(
                file_path,
                match_by_id("id", "1"),
                lambda obj: {**obj, **update_data}
            )
        v1_time = time.perf_counter() - v1_start
        result = stream_read(file_path, match_by_id("id", "1"))
        assert result["age"] == 31
        # V2: Validate on update
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        v2_start = time.perf_counter()
        valid_v2, error_v2 = validate_update(update_data)
        if valid_v2:
            stream_update(
                file_path,
                match_by_id("id", "1"),
                lambda obj: {**obj, **update_data}
            )
            build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        index = ensure_index(file_path, id_field="id")
        result_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert result_v2["age"] == 31
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
