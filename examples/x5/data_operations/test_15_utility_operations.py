"""
#exonware/xwnode/examples/x5/data_operations/test_15_utility_operations.py

UTILITY Operations Test Suite

Tests all UTILITY operations (helper functions) for both V1 (Streaming) and V2 (Indexed) implementations.
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
import csv
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
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_line,
)


# ============================================================================
# 15.1 Data Transformation
# ============================================================================

def test_15_1_1_transform_record():
    """
    Full Test Name: test_15_1_1_transform_record
    Test: Apply transformation function
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        def transform(obj):
            obj["full_name"] = f"{obj.get('name', '')} (Age: {obj.get('age', 0)})"
            return obj
        
        # V1: Transform record
        v1_start = time.perf_counter()
        result = stream_read(file_path, match_by_id("id", "1"))
        transformed = transform(result.copy())
        v1_time = time.perf_counter() - v1_start
        
        assert "full_name" in transformed
        
        # V2: Transform record
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        result_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        transformed_v2 = transform(result_v2.copy())
        v2_time = time.perf_counter() - v2_start
        
        assert "full_name" in transformed_v2
        assert transformed == transformed_v2
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_1_2_map_records():
    """
    Full Test Name: test_15_1_2_map_records
    Test: Transform all records
    """
    test_data = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
        {"id": "3", "value": 30}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def map_func(obj):
            obj["doubled"] = obj.get("value", 0) * 2
            return obj
        
        # V1: Map records
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_mapped = [map_func(r.copy()) for r in records]
        v1_time = time.perf_counter() - v1_start
        
        assert all("doubled" in r for r in v1_mapped)
        assert v1_mapped[0]["doubled"] == 20
        
        # V2: Map records
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_mapped = [map_func(r.copy()) for r in records_v2]
        v2_time = time.perf_counter() - v2_start
        
        assert all("doubled" in r for r in v2_mapped)
        assert v1_mapped == v2_mapped
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_1_3_filter_records():
    """
    Full Test Name: test_15_1_3_filter_records
    Test: Remove records matching criteria
    """
    test_data = [
        {"id": "1", "status": "active"},
        {"id": "2", "status": "inactive"},
        {"id": "3", "status": "active"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def is_active(obj):
            return obj.get("status") == "active"
        
        # V1: Filter records
        v1_start = time.perf_counter()
        v1_filtered = get_all_matching_v1(file_path, is_active)
        v1_time = time.perf_counter() - v1_start
        
        assert len(v1_filtered) == 2
        assert all(r.get("status") == "active" for r in v1_filtered)
        
        # V2: Filter records
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_filtered = get_all_matching_v2(file_path, is_active, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(v2_filtered) == 2
        assert v1_filtered == v2_filtered
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_1_4_reduce_records():
    """
    Full Test Name: test_15_1_4_reduce_records
    Test: Aggregate records to single value
    """
    test_data = [
        {"id": "1", "amount": 100},
        {"id": "2", "amount": 200},
        {"id": "3", "amount": 300}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def reduce_func(accumulator, record):
            return accumulator + record.get("amount", 0)
        
        # V1: Reduce records
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_result = 0
        for record in records:
            v1_result = reduce_func(v1_result, record)
        v1_time = time.perf_counter() - v1_start
        
        assert v1_result == 600
        
        # V2: Reduce records
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_result = 0
        for record in records_v2:
            v2_result = reduce_func(v2_result, record)
        v2_time = time.perf_counter() - v2_start
        
        assert v2_result == 600
        assert v1_result == v2_result
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_1_5_flatten_nested():
    """
    Full Test Name: test_15_1_5_flatten_nested
    Test: Flatten nested structures
    """
    test_data = [
        {"id": "1", "user": {"name": "Alice", "contact": {"email": "alice@example.com"}}}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def flatten(obj, prefix=""):
            flattened = {}
            for key, value in obj.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    flattened.update(flatten(value, new_key))
                else:
                    flattened[new_key] = value
            return flattened
        
        # V1: Flatten nested
        v1_start = time.perf_counter()
        record = stream_read(file_path, match_by_id("id", "1"))
        v1_flattened = flatten(record)
        v1_time = time.perf_counter() - v1_start
        
        assert "user.name" in v1_flattened
        assert "user.contact.email" in v1_flattened
        
        # V2: Flatten nested
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        record_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        v2_flattened = flatten(record_v2)
        v2_time = time.perf_counter() - v2_start
        
        assert "user.name" in v2_flattened
        assert v1_flattened == v2_flattened
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_1_6_normalize_data():
    """
    Full Test Name: test_15_1_6_normalize_data
    Test: Normalize data structure
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30, "role": "admin"},
        {"id": "2", "name": "Bob", "age": 25}  # Missing role
    ]
    file_path = create_test_file(test_data)
    
    try:
        def normalize(record):
            # Ensure all records have same structure
            normalized = {
                "id": record.get("id", ""),
                "name": record.get("name", ""),
                "age": record.get("age", 0),
                "role": record.get("role", "user")  # Default value
            }
            return normalized
        
        # V1: Normalize data
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_normalized = [normalize(r) for r in records]
        v1_time = time.perf_counter() - v1_start
        
        assert all("role" in r for r in v1_normalized)
        assert v1_normalized[1]["role"] == "user"
        
        # V2: Normalize data
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_normalized = [normalize(r) for r in records_v2]
        v2_time = time.perf_counter() - v2_start
        
        assert all("role" in r for r in v2_normalized)
        assert v1_normalized == v2_normalized
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 15.2 Data Export/Import
# ============================================================================

def test_15_2_1_export_to_json():
    """
    Full Test Name: test_15_2_1_export_to_json
    Test: Export records to JSON format
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    export_file = file_path + ".export.json"
    
    try:
        # V1: Export to JSON
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        v1_time = time.perf_counter() - v1_start
        
        assert os.path.exists(export_file)
        with open(export_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        assert len(exported) == 2
        
        # V2: Export to JSON
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(records_v2, f, ensure_ascii=False, indent=2)
        v2_time = time.perf_counter() - v2_start
        
        assert len(records_v2) == 2
        assert exported == records_v2
        
        if os.path.exists(export_file):
            os.remove(export_file)
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_2_2_export_to_csv():
    """
    Full Test Name: test_15_2_2_export_to_csv
    Test: Export records to CSV format
    """
    test_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob", "age": 25}
    ]
    file_path = create_test_file(test_data)
    export_file = file_path + ".export.csv"
    
    try:
        # V1: Export to CSV
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        if records:
            fieldnames = records[0].keys()
            with open(export_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
        v1_time = time.perf_counter() - v1_start
        
        assert os.path.exists(export_file)
        
        # V2: Export to CSV
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        if records_v2:
            fieldnames_v2 = records_v2[0].keys()
            with open(export_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames_v2)
                writer.writeheader()
                writer.writerows(records_v2)
        v2_time = time.perf_counter() - v2_start
        
        assert len(records_v2) == 2
        
        if os.path.exists(export_file):
            os.remove(export_file)
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_2_3_import_from_json():
    """
    Full Test Name: test_15_2_3_import_from_json
    Test: Import records from JSON
    """
    import_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    import_file = create_test_file(import_data)
    target_file = create_test_file([])
    
    try:
        # V1: Import from JSON
        # Root cause fix: create_test_file creates JSONL (line-delimited JSON), not regular JSON
        # Following GUIDE_TEST.md - Fix root causes, parse JSONL line by line
        v1_start = time.perf_counter()
        data = []
        with open(import_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line.strip()))
        with open(target_file, 'w', encoding='utf-8') as f:
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        v1_time = time.perf_counter() - v1_start
        
        records = get_all_matching_v1(target_file, lambda x: True)
        assert len(records) == 2
        
        # V2: Import from JSON
        # Root cause fix: create_test_file creates JSONL (line-delimited JSON), not regular JSON
        # Following GUIDE_TEST.md - Fix root causes, parse JSONL line by line
        cleanup_test_file(target_file)
        target_file = create_test_file([])
        
        v2_start = time.perf_counter()
        data_v2 = []
        with open(import_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data_v2.append(json.loads(line.strip()))
        with open(target_file, 'w', encoding='utf-8') as f:
            for record in data_v2:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        build_index(target_file, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(target_file, id_field="id")
        records_v2 = get_all_matching_v2(target_file, lambda x: True, index=index)
        assert len(records_v2) == 2
        
        cleanup_test_file(import_file)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(target_file)


def test_15_2_4_import_from_csv():
    """
    Full Test Name: test_15_2_4_import_from_csv
    Test: Import records from CSV
    """
    import_file = create_test_file([])
    # Create CSV file
    with open(import_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "age"])
        writer.writeheader()
        writer.writerow({"id": "1", "name": "Alice", "age": "30"})
        writer.writerow({"id": "2", "name": "Bob", "age": "25"})
    
    target_file = create_test_file([])
    
    try:
        # V1: Import from CSV
        v1_start = time.perf_counter()
        with open(import_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with open(target_file, 'w', encoding='utf-8') as out:
                for row in reader:
                    # Convert age to int
                    row["age"] = int(row["age"])
                    out.write(json.dumps(row, ensure_ascii=False) + '\n')
        v1_time = time.perf_counter() - v1_start
        
        records = get_all_matching_v1(target_file, lambda x: True)
        assert len(records) == 2
        
        # V2: Import from CSV
        cleanup_test_file(target_file)
        target_file = create_test_file([])
        
        v2_start = time.perf_counter()
        with open(import_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with open(target_file, 'w', encoding='utf-8') as out:
                for row in reader:
                    row["age"] = int(row["age"])
                    out.write(json.dumps(row, ensure_ascii=False) + '\n')
        build_index(target_file, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(target_file, id_field="id")
        records_v2 = get_all_matching_v2(target_file, lambda x: True, index=index)
        assert len(records_v2) == 2
        
        cleanup_test_file(import_file)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(target_file)


def test_15_2_5_export_with_filter():
    """
    Full Test Name: test_15_2_5_export_with_filter
    Test: Export filtered subset
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    export_file = file_path + ".export.json"
    
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        
        # V1: Export with filter
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, is_admin)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        v1_time = time.perf_counter() - v1_start
        
        assert os.path.exists(export_file)
        with open(export_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        assert len(exported) == 2
        
        # V2: Export with filter
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, is_admin, index=index)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(records_v2, f, ensure_ascii=False, indent=2)
        v2_time = time.perf_counter() - v2_start
        
        assert len(records_v2) == 2
        assert exported == records_v2
        
        if os.path.exists(export_file):
            os.remove(export_file)
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_2_6_import_with_validation():
    """
    Full Test Name: test_15_2_6_import_with_validation
    Test: Import with validation
    """
    import_data = [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "", "age": -5},  # Invalid
        {"id": "3", "name": "Bob", "age": 25}
    ]
    import_file = create_test_file(import_data)
    target_file = create_test_file([])
    
    try:
        def validate_record(record):
            if not isinstance(record.get("name"), str) or not record.get("name"):
                return False, "Name is required"
            if not isinstance(record.get("age"), int) or record.get("age") < 0:
                return False, "Age must be non-negative"
            return True, None
        
        # V1: Import with validation
        v1_start = time.perf_counter()
        with open(import_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    valid, error = validate_record(record)
                    if valid:
                        with open(target_file, 'a', encoding='utf-8') as out:
                            out.write(json.dumps(record, ensure_ascii=False) + '\n')
        v1_time = time.perf_counter() - v1_start
        
        records = get_all_matching_v1(target_file, lambda x: True)
        assert len(records) == 2
        
        # V2: Import with validation
        cleanup_test_file(target_file)
        target_file = create_test_file([])
        
        v2_start = time.perf_counter()
        with open(import_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    valid, error = validate_record(record)
                    if valid:
                        with open(target_file, 'a', encoding='utf-8') as out:
                            out.write(json.dumps(record, ensure_ascii=False) + '\n')
        build_index(target_file, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(target_file, id_field="id")
        records_v2 = get_all_matching_v2(target_file, lambda x: True, index=index)
        assert len(records_v2) == 2
        
        cleanup_test_file(import_file)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(target_file)


# ============================================================================
# 15.3 Data Migration
# ============================================================================

def test_15_3_1_migrate_schema():
    """
    Full Test Name: test_15_3_1_migrate_schema
    Test: Transform records to new schema
    """
    test_data = [
        {"id": "1", "first_name": "Alice", "last_name": "Smith"},
        {"id": "2", "first_name": "Bob", "last_name": "Jones"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def migrate_schema(record):
            # Migrate from old schema to new schema
            return {
                "id": record.get("id"),
                "name": f"{record.get('first_name', '')} {record.get('last_name', '')}".strip(),
                "version": 2
            }
        
        # V1: Migrate schema
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_migrated = [migrate_schema(r) for r in records]
        v1_time = time.perf_counter() - v1_start
        
        assert all("name" in r for r in v1_migrated)
        assert v1_migrated[0]["name"] == "Alice Smith"
        
        # V2: Migrate schema
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_migrated = [migrate_schema(r) for r in records_v2]
        v2_time = time.perf_counter() - v2_start
        
        assert all("name" in r for r in v2_migrated)
        assert v1_migrated == v2_migrated
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_3_2_migrate_data():
    """
    Full Test Name: test_15_3_2_migrate_data
    Test: Move data between formats
    """
    test_data = [{"id": "1", "name": "Alice"}]
    source_file = create_test_file(test_data)
    target_file = create_test_file([])
    
    try:
        # V1: Migrate data
        v1_start = time.perf_counter()
        records = get_all_matching_v1(source_file, lambda x: True)
        with open(target_file, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        v1_time = time.perf_counter() - v1_start
        
        migrated = get_all_matching_v1(target_file, lambda x: True)
        assert len(migrated) == 1
        
        # V2: Migrate data
        cleanup_test_file(target_file)
        target_file = create_test_file([])
        
        v2_start = time.perf_counter()
        index = ensure_index(source_file, id_field="id")
        records_v2 = get_all_matching_v2(source_file, lambda x: True, index=index)
        with open(target_file, 'w', encoding='utf-8') as f:
            for record in records_v2:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        build_index(target_file, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        index_target = ensure_index(target_file, id_field="id")
        migrated_v2 = get_all_matching_v2(target_file, lambda x: True, index=index_target)
        assert len(migrated_v2) == 1
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(source_file)
        cleanup_test_file(target_file)


def test_15_3_3_version_migration():
    """
    Full Test Name: test_15_3_3_version_migration
    Test: Migrate between versions
    """
    test_data = [{"id": "1", "name": "Alice", "version": 1}]
    file_path = create_test_file(test_data)
    
    try:
        def migrate_to_v2(record):
            record["version"] = 2
            record["migrated_at"] = "2024-01-01"
            return record
        
        # V1: Version migration
        v1_start = time.perf_counter()
        record = stream_read(file_path, match_by_id("id", "1"))
        migrated = migrate_to_v2(record.copy())
        stream_update(file_path, match_by_id("id", "1"), lambda obj: migrated)
        v1_time = time.perf_counter() - v1_start
        
        result = stream_read(file_path, match_by_id("id", "1"))
        assert result["version"] == 2
        
        # V2: Version migration
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        
        v2_start = time.perf_counter()
        from json_utils_indexed import indexed_get_by_id
        index = ensure_index(file_path, id_field="id")
        record_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        migrated_v2 = migrate_to_v2(record_v2.copy())
        stream_update(file_path, match_by_id("id", "1"), lambda obj: migrated_v2)
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(file_path, id_field="id")
        result_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert result_v2["version"] == 2
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_15_3_4_data_cleanup():
    """
    Full Test Name: test_15_3_4_data_cleanup
    Test: Remove invalid/corrupted records
    """
    test_data = [
        {"id": "1", "name": "Alice", "valid": True},
        {"id": "2", "name": "Bob", "valid": False},  # Invalid
        {"id": "3", "name": "Charlie", "valid": True}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def is_valid(record):
            return record.get("valid", False)
        
        # V1: Data cleanup
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, is_valid)
        # Rewrite file with only valid records
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        v1_time = time.perf_counter() - v1_start
        
        cleaned = get_all_matching_v1(file_path, lambda x: True)
        assert len(cleaned) == 2
        assert all(r.get("valid") for r in cleaned)
        
        # V2: Data cleanup
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        
        v2_start = time.perf_counter()
        index = ensure_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, is_valid, index=index)
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in records_v2:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(file_path, id_field="id")
        cleaned_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(cleaned_v2) == 2
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)

