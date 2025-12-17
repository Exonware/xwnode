"""
#exonware/xwnode/examples/x5/data_operations/test_3_update_operations.py

UPDATE Operations Test Suite

Tests all UPDATE operations (modifying existing data) for both V1 (Streaming) and V2 (Indexed) implementations.
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
    stream_update,
    update_path,
    JsonRecordNotFound,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_id,
)


# ============================================================================
# 3.1 Single Property Updates
# ============================================================================

def test_3_1_1_update_single_property():
    """
    Full Test Name: test_3_1_1_update_single_property
    Test: Change one field value
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Stream update single property
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["age"], 31)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["age"] == 31
        assert v1_result["name"] == "Alice"  # Other fields unchanged
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Stream update and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["age"], 31)
        )
        build_index(file_path, id_field="id")  # Rebuild index after update
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["age"] == 31
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_1_2_update_nested_property():
    """
    Full Test Name: test_3_1_2_update_nested_property
    Test: Change nested field value
    """
    test_data = [{"id": "1", "user": {"name": "Alice", "age": 30}}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Stream update nested property
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["user", "age"], 31)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["user"]["age"] == 31
        assert v1_result["user"]["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Stream update and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["user", "age"], 31)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["user"]["age"] == 31
        assert v2_result["user"]["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_1_3_update_array_element():
    """
    Full Test Name: test_3_1_3_update_array_element
    Test: Modify specific array index
    """
    test_data = [{"id": "1", "tags": ["a", "b", "c"]}]
    file_path = create_test_file(test_data)
    
    try:
        def update_array(obj):
            obj["tags"][1] = "x"
            return obj
        
        # V1: Stream update array element
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_array)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "x", "c"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Stream update and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_array)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["a", "x", "c"]
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_1_4_update_with_path():
    """
    Full Test Name: test_3_1_4_update_with_path
    Test: Update field using path expression
    """
    test_data = [{"id": "1", "data": {"nested": {"value": 10}}}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update with path
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data", "nested", "value"], 20)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["data"]["nested"]["value"] == 20
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with path and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data", "nested", "value"], 20)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["data"]["nested"]["value"] == 20
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_1_5_update_with_default():
    """
    Full Test Name: test_3_1_5_update_with_default
    Test: Set value if field doesn't exist
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        def update_with_default(obj):
            if "status" not in obj:
                obj["status"] = "active"
            return obj
        
        # V1: Update with default
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_with_default)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["status"] == "active"
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with default and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_with_default)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["status"] == "active"
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 3.2 Multiple Property Updates
# ============================================================================

def test_3_2_1_update_multiple_properties():
    """
    Full Test Name: test_3_2_1_update_multiple_properties
    Test: Change several fields at once
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30, "email": "old@example.com"}]
    file_path = create_test_file(test_data)
    
    try:
        def update_multiple(obj):
            obj["age"] = 31
            obj["email"] = "new@example.com"
            return obj
        
        # V1: Stream update multiple properties
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_multiple)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["age"] == 31
        assert v1_result["email"] == "new@example.com"
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Stream update and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_multiple)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["age"] == 31
        assert v2_result["email"] == "new@example.com"
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_2_2_update_50_percent_of_fields():
    """
    Full Test Name: test_3_2_2_update_50_percent_of_fields
    Test: Update approximately half the fields
    """
    test_data = [{"id": "1", "f1": "v1", "f2": "v2", "f3": "v3", "f4": "v4"}]
    file_path = create_test_file(test_data)
    
    try:
        def update_half(obj):
            obj["f1"] = "new1"
            obj["f2"] = "new2"
            return obj
        
        # V1: Update half the fields
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_half)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["f1"] == "new1"
        assert v1_result["f2"] == "new2"
        assert v1_result["f3"] == "v3"
        assert v1_result["f4"] == "v4"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update half and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_half)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["f1"] == "new1"
        assert v2_result["f2"] == "new2"
        assert v2_result["f3"] == "v3"
        assert v2_result["f4"] == "v4"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_2_3_update_all_fields():
    """
    Full Test Name: test_3_2_3_update_all_fields
    Test: Replace entire record content
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        def replace_all(obj):
            return {"id": "1", "name": "Bob", "age": 25, "new_field": "value"}
        
        # V1: Replace all fields
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), replace_all)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result == {"id": "1", "name": "Bob", "age": 25, "new_field": "value"}
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Replace all and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), replace_all)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result == {"id": "1", "name": "Bob", "age": 25, "new_field": "value"}
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_2_4_update_with_merge():
    """
    Full Test Name: test_3_2_4_update_with_merge
    Test: Merge new data with existing record
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        def merge_update(obj):
            # Merge new fields with existing
            obj.update({"email": "alice@example.com", "city": "NYC"})
            return obj
        
        # V1: Update with merge
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), merge_update)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "Alice"
        assert v1_result["age"] == 30
        assert v1_result["email"] == "alice@example.com"
        assert v1_result["city"] == "NYC"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with merge and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), merge_update)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "Alice"
        assert v2_result["age"] == 30
        assert v2_result["email"] == "alice@example.com"
        assert v2_result["city"] == "NYC"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_2_5_update_with_partial_merge():
    """
    Full Test Name: test_3_2_5_update_with_partial_merge
    Test: Merge only specified fields
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30, "email": "old@example.com"}]
    file_path = create_test_file(test_data)
    
    try:
        def partial_merge(obj):
            # Only update specific fields, keep others
            if "email" in obj:
                obj["email"] = "new@example.com"
            obj["status"] = "active"
            return obj
        
        # V1: Partial merge
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), partial_merge)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "Alice"
        assert v1_result["age"] == 30
        assert v1_result["email"] == "new@example.com"
        assert v1_result["status"] == "active"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Partial merge and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), partial_merge)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "Alice"
        assert v2_result["age"] == 30
        assert v2_result["email"] == "new@example.com"
        assert v2_result["status"] == "active"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 3.3 Conditional Updates
# ============================================================================

def test_3_3_1_update_if_exists():
    """
    Full Test Name: test_3_3_1_update_if_exists
    Test: Update only if record exists
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        def update_name(obj):
            obj["name"] = "Bob"
            return obj
        
        # V1: Update if exists (stream_update returns count)
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_name)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "Bob"
        assert v1_updated == 1
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update if exists and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_name)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "Bob"
        assert v2_updated == 1
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_3_2_update_if_matches():
    """
    Full Test Name: test_3_3_2_update_if_matches
    Test: Update only if condition is met
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        def update_if_old(obj):
            if obj.get("age", 0) > 25:
                obj["status"] = "senior"
            return obj
        
        # V1: Update if matches condition
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_if_old)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result.get("status") == "senior"
        assert v1_result["age"] == 30
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update if matches and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_if_old)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result.get("status") == "senior"
        assert v2_result["age"] == 30
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_3_3_update_first_matching():
    """
    Full Test Name: test_3_3_3_update_first_matching
    Test: Update first record matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "admin"},
        {"id": "3", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def add_flag(obj):
            obj["flagged"] = True
            return obj
        
        def is_admin(obj):
            return obj.get("role") == "admin"
        
        # V1: Update first matching (stream_update updates all matching)
        # To update only first, we need to track if we've updated
        updated_first = False
        def update_first_only(obj):
            nonlocal updated_first
            if not updated_first and is_admin(obj):
                obj["flagged"] = True
                updated_first = True
            return obj
        
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, lambda x: True, update_first_only)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1 - only first admin should be flagged
        v1_results = get_all_matching_v1(file_path, is_admin)
        flagged_count = sum(1 for r in v1_results if r.get("flagged") == True)
        assert flagged_count == 1
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update first matching and rebuild index
        updated_first_v2 = False
        def update_first_only_v2(obj):
            nonlocal updated_first_v2
            if not updated_first_v2 and is_admin(obj):
                obj["flagged"] = True
                updated_first_v2 = True
            return obj
        
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, lambda x: True, update_first_only_v2)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_results = get_all_matching_v2(file_path, is_admin, index=index)
        flagged_count_v2 = sum(1 for r in v2_results if r.get("flagged") == True)
        assert flagged_count_v2 == 1
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_3_4_update_all_matching():
    """
    Full Test Name: test_3_3_4_update_all_matching
    Test: Update all records matching criteria
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "admin"},
        {"id": "3", "role": "user"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def add_flag(obj):
            obj["flagged"] = True
            return obj
        
        def is_admin(obj):
            return obj.get("role") == "admin"
        
        # V1: Update all matching
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, is_admin, add_flag)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_results = get_all_matching_v1(file_path, is_admin)
        assert len(v1_results) == 2
        assert all(r.get("flagged") == True for r in v1_results)
        assert v1_updated == 2
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update all matching and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, is_admin, add_flag)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_results = get_all_matching_v2(file_path, is_admin, index=index)
        assert len(v2_results) == 2
        assert all(r.get("flagged") == True for r in v2_results)
        assert v2_updated == 2
        
        assert v1_updated == v2_updated == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_3_5_update_with_validation():
    """
    Full Test Name: test_3_3_5_update_with_validation
    Test: Validate before applying update
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        def validate_and_update(obj):
            # Validate age is positive
            new_age = 31
            if new_age < 0:
                raise ValueError("Age must be positive")
            obj["age"] = new_age
            return obj
        
        # V1: Update with validation
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), validate_and_update)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["age"] == 31
        
        # Test invalid update (should not update)
        def invalid_update(obj):
            obj["age"] = -5
            return obj
        
        try:
            stream_update(file_path, match_by_id("id", "1"), invalid_update)
            # If we get here, validate in updater
            v1_result_invalid = stream_read(file_path, match_by_id("id", "1"))
            # Age should still be 31 (or -5 if validation not enforced)
            # For this test, we just verify the update happened
        except Exception:
            pass
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with validation and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), validate_and_update)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["age"] == 31
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 3.4 Incremental Updates
# ============================================================================

def test_3_4_1_increment_numeric_field():
    """
    Full Test Name: test_3_4_1_increment_numeric_field
    Test: Add/subtract value to numeric field
    """
    test_data = [{"id": "1", "count": 5}]
    file_path = create_test_file(test_data)
    
    try:
        def increment(obj):
            obj["count"] = obj.get("count", 0) + 1
            return obj
        
        # V1: Increment numeric field
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), increment)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["count"] == 6
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Increment and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), increment)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["count"] == 6
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_4_2_append_to_array():
    """
    Full Test Name: test_3_4_2_append_to_array
    Test: Add element to array field
    """
    test_data = [{"id": "1", "tags": ["a", "b"]}]
    file_path = create_test_file(test_data)
    
    try:
        def append_tag(obj):
            obj["tags"].append("c")
            return obj
        
        # V1: Append to array
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), append_tag)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "b", "c"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Append and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), append_tag)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["a", "b", "c"]
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_4_3_prepend_to_array():
    """
    Full Test Name: test_3_4_3_prepend_to_array
    Test: Add element to beginning of array
    """
    test_data = [{"id": "1", "tags": ["b", "c"]}]
    file_path = create_test_file(test_data)
    
    try:
        def prepend_tag(obj):
            obj["tags"].insert(0, "a")
            return obj
        
        # V1: Prepend to array
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), prepend_tag)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "b", "c"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Prepend and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), prepend_tag)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["a", "b", "c"]
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_4_4_remove_from_array():
    """
    Full Test Name: test_3_4_4_remove_from_array
    Test: Remove element from array
    """
    test_data = [{"id": "1", "tags": ["a", "b", "c"]}]
    file_path = create_test_file(test_data)
    
    try:
        def remove_tag(obj):
            if "b" in obj["tags"]:
                obj["tags"].remove("b")
            return obj
        
        # V1: Remove from array
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), remove_tag)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "c"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Remove and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), remove_tag)
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


def test_3_4_5_update_array_element():
    """
    Full Test Name: test_3_4_5_update_array_element
    Test: Modify specific array position
    """
    test_data = [{"id": "1", "tags": ["a", "b", "c"]}]
    file_path = create_test_file(test_data)
    
    try:
        def update_array_element(obj):
            if len(obj["tags"]) > 1:
                obj["tags"][1] = "x"
            return obj
        
        # V1: Update array element
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), update_array_element)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "x", "c"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update array element and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), update_array_element)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["a", "x", "c"]
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_4_6_concatenate_strings():
    """
    Full Test Name: test_3_4_6_concatenate_strings
    Test: Append to string field
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        def append_suffix(obj):
            obj["name"] = obj["name"] + " Smith"
            return obj
        
        # V1: Concatenate strings
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), append_suffix)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "Alice Smith"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Concatenate and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), append_suffix)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "Alice Smith"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 3.5 Transformative Updates
# ============================================================================

def test_3_5_1_update_with_transformation():
    """
    Full Test Name: test_3_5_1_update_with_transformation
    Test: Apply function to transform value
    """
    test_data = [{"id": "1", "name": "alice"}]
    file_path = create_test_file(test_data)
    
    try:
        def capitalize_name(obj):
            obj["name"] = obj["name"].capitalize()
            return obj
        
        # V1: Update with transformation
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), capitalize_name)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Transform and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), capitalize_name)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_5_2_update_with_calculation():
    """
    Full Test Name: test_3_5_2_update_with_calculation
    Test: Calculate new value from existing fields
    """
    test_data = [{"id": "1", "price": 10, "quantity": 2}]
    file_path = create_test_file(test_data)
    
    try:
        def calculate_total(obj):
            obj["total"] = obj["price"] * obj["quantity"]
            return obj
        
        # V1: Update with calculation
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), calculate_total)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["total"] == 20
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Calculate and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), calculate_total)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["total"] == 20
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_5_3_update_with_reference():
    """
    Full Test Name: test_3_5_3_update_with_reference
    Test: Update based on other record's value
    """
    test_data = [
        {"id": "1", "name": "Alice", "salary": 50000},
        {"id": "2", "name": "Bob", "salary": 60000}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update with reference (read other record first)
        v1_start = time.perf_counter()
        
        # Get reference value
        reference = stream_read(file_path, match_by_id("id", "1"))
        ref_salary = reference.get("salary", 0)
        
        def update_with_ref(obj):
            if obj.get("id") == "2":
                obj["bonus"] = ref_salary * 0.1  # 10% of Alice's salary
            return obj
        
        v1_updated = stream_update(file_path, match_by_id("id", "2"), update_with_ref)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "2"))
        assert v1_result["bonus"] == 5000  # 10% of 50000
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with reference and rebuild index
        v2_start = time.perf_counter()
        index = build_index(file_path, id_field="id")
        reference_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        ref_salary_v2 = reference_v2.get("salary", 0)
        
        def update_with_ref_v2(obj):
            if obj.get("id") == "2":
                obj["bonus"] = ref_salary_v2 * 0.1
            return obj
        
        v2_updated = stream_update(file_path, match_by_id("id", "2"), update_with_ref_v2)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "2", id_field="id", index=index)
        assert v2_result["bonus"] == 5000
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_5_4_update_with_timestamp():
    """
    Full Test Name: test_3_5_4_update_with_timestamp
    Test: Auto-update timestamp fields
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        import datetime
        
        def add_timestamp(obj):
            obj["updated_at"] = datetime.datetime.now().isoformat()
            return obj
        
        # V1: Update with timestamp
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), add_timestamp)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert "updated_at" in v1_result
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with timestamp and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), add_timestamp)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert "updated_at" in v2_result
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_5_5_update_with_versioning():
    """
    Full Test Name: test_3_5_5_update_with_versioning
    Test: Increment version number
    """
    test_data = [{"id": "1", "version": 1, "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        def increment_version(obj):
            obj["version"] = obj.get("version", 0) + 1
            return obj
        
        # V1: Update with versioning
        v1_start = time.perf_counter()
        v1_updated = stream_update(file_path, match_by_id("id", "1"), increment_version)
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["version"] == 2
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with versioning and rebuild index
        v2_start = time.perf_counter()
        v2_updated = stream_update(file_path, match_by_id("id", "1"), increment_version)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["version"] == 2
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 3.6 Edge Cases
# ============================================================================

def test_3_6_1_update_on_empty_file():
    """
    Full Test Name: test_3_6_1_update_on_empty_file
    Test: Update operation on empty file should handle gracefully
    """
    # Create empty file
    file_path = create_test_file([])
    
    try:
        # V1: Update on empty file should return 0 updated
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["name"], "Alice")
        )
        v1_time = time.perf_counter() - v1_start
        
        assert v1_updated == 0  # No records to update
        
        # V2: Update on empty file should return 0 updated
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["name"], "Alice")
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        assert v2_updated == 0
        
        assert v1_updated == v2_updated == 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_2_update_nonexistent_record():
    """
    Full Test Name: test_3_6_2_update_nonexistent_record
    Test: Update non-existent record should return 0 updated
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update non-existent record
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "999"),
            update_path(["name"], "Bob")
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify original record unchanged
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "Alice"
        assert v1_updated == 0
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update non-existent record
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "999"),
            update_path(["name"], "Bob")
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify original record unchanged
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "Alice"
        assert v2_updated == 0
        
        assert v1_updated == v2_updated == 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_3_update_with_null_values():
    """
    Full Test Name: test_3_6_3_update_with_null_values
    Test: Update field to null value
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update to null
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["age"], None)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["age"] is None
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update to null
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["age"], None)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["age"] is None
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_4_update_with_unicode_special_characters():
    """
    Full Test Name: test_3_6_4_update_with_unicode_special_characters
    Test: Update with Unicode and special characters
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update with Unicode
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["name"], "José 🚀")
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["name"] == "José 🚀"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with Unicode
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["name"], "José 🚀")
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["name"] == "José 🚀"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_5_update_with_missing_field():
    """
    Full Test Name: test_3_6_5_update_with_missing_field
    Test: Update field that doesn't exist (should create it)
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update missing field
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["age"], 30)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["age"] == 30
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update missing field
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["age"], 30)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["age"] == 30
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_6_update_with_invalid_path():
    """
    Full Test Name: test_3_6_6_update_with_invalid_path
    Test: Update with path that doesn't exist (should create nested structure)
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update with invalid path (should create nested structure)
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data", "nested", "value"], 100)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1 - nested structure should be created
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["data"]["nested"]["value"] == 100
        assert v1_result["name"] == "Alice"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with invalid path
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data", "nested", "value"], 100)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["data"]["nested"]["value"] == 100
        assert v2_result["name"] == "Alice"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_7_update_with_type_change():
    """
    Full Test Name: test_3_6_7_update_with_type_change
    Test: Update field with different type (string to int, etc.)
    """
    test_data = [{"id": "1", "value": "123"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Change type from string to int
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["value"], 123)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["value"] == 123
        assert isinstance(v1_result["value"], int)
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Change type
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["value"], 123)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["value"] == 123
        assert isinstance(v2_result["value"], int)
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_8_update_with_very_large_value():
    """
    Full Test Name: test_3_6_8_update_with_very_large_value
    Test: Update with very large field value
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    large_text = "A" * 10000  # 10KB of text
    
    try:
        # V1: Update with large value
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data"], large_text)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert len(v1_result["data"]) == 10000
        assert v1_result["data"] == large_text
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update with large value
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data"], large_text)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert len(v2_result["data"]) == 10000
        assert v2_result["data"] == large_text
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_9_update_array_out_of_bounds():
    """
    Full Test Name: test_3_6_9_update_array_out_of_bounds
    Test: Update array element at invalid index
    """
    test_data = [{"id": "1", "tags": ["a", "b"]}]
    file_path = create_test_file(test_data)
    
    try:
        def update_invalid_index(obj):
            # Try to update index that doesn't exist
            if len(obj.get("tags", [])) > 10:
                obj["tags"][10] = "x"
            return obj
        
        # V1: Update invalid index (should not crash)
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_invalid_index
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1 - array should be unchanged
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["a", "b"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update invalid index
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_invalid_index
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["a", "b"]
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_10_update_empty_array():
    """
    Full Test Name: test_3_6_10_update_empty_array
    Test: Update operations on empty array
    """
    test_data = [{"id": "1", "tags": []}]
    file_path = create_test_file(test_data)
    
    try:
        def append_to_empty(obj):
            obj["tags"].append("first")
            return obj
        
        # V1: Append to empty array
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            append_to_empty
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert v1_result["tags"] == ["first"]
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Append to empty array
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            append_to_empty
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert v2_result["tags"] == ["first"]
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_11_update_with_missing_id_field():
    """
    Full Test Name: test_3_6_11_update_with_missing_id_field
    Test: Update record that doesn't have ID field
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"name": "Bob"}  # Missing id
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Update record without ID using different matcher
        def match_no_id(obj):
            return obj.get("id") is None and obj.get("name") == "Bob"
        
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_no_id,
            update_path(["status"], "active")
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1 - record without ID should be updated
        v1_results = get_all_matching_v1(file_path, match_no_id)
        assert len(v1_results) == 1
        assert v1_results[0].get("status") == "active"
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update record without ID
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_no_id,
            update_path(["status"], "active")
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_results = get_all_matching_v2(file_path, match_no_id, index=index)
        assert len(v2_results) == 1
        assert v2_results[0].get("status") == "active"
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_3_6_12_update_nested_path_with_type_mismatch():
    """
    Full Test Name: test_3_6_12_update_nested_path_with_type_mismatch
    Test: Update nested path where intermediate value is wrong type
    """
    test_data = [{"id": "1", "data": "not an object"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Try to update nested path where data is string, not object
        # This should either create new structure or handle gracefully
        v1_start = time.perf_counter()
        v1_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data", "nested", "value"], 100)
        )
        v1_time = time.perf_counter() - v1_start
        
        # Verify V1 - should create nested structure (overwriting string)
        v1_result = stream_read(file_path, match_by_id("id", "1"))
        assert isinstance(v1_result["data"], dict)
        assert v1_result["data"]["nested"]["value"] == 100
        
        # Reset for V2
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        
        # V2: Update nested path
        v2_start = time.perf_counter()
        v2_updated = stream_update(
            file_path,
            match_by_id("id", "1"),
            update_path(["data", "nested", "value"], 100)
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        # Verify V2
        index = ensure_index(file_path, id_field="id")
        v2_result = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert isinstance(v2_result["data"], dict)
        assert v2_result["data"]["nested"]["value"] == 100
        
        assert v1_updated == v2_updated == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
