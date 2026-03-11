"""
#exonware/xwnode/examples/x5/data_operations/test_11_aggregation_operations.py
AGGREGATION Operations Test Suite
Tests all AGGREGATION operations (data analysis) for both V1 (Streaming) and V2 (Indexed) implementations.
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
import math
from pathlib import Path
from typing import Any
from collections import defaultdict
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
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_line,
)
# ============================================================================
# 11.1 Counting
# ============================================================================


def test_11_1_1_count_all():
    """
    Full Test Name: test_11_1_1_count_all
    Test: Count total records
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Count all
        v1_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_time = time.perf_counter() - v1_start
        # V2: Count all
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_count = count_records_v2(file_path, index=index)
        v2_time = time.perf_counter() - v2_start
        assert v1_count == v2_count == 10
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_1_2_count_matching():
    """
    Full Test Name: test_11_1_2_count_matching
    Test: Count records matching criteria
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
        # V1: Count matching
        v1_start = time.perf_counter()
        v1_matching = get_all_matching_v1(file_path, is_admin)
        v1_count = len(v1_matching)
        v1_time = time.perf_counter() - v1_start
        # V2: Count matching
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_matching = get_all_matching_v2(file_path, is_admin, index=index)
        v2_count = len(v2_matching)
        v2_time = time.perf_counter() - v2_start
        assert v1_count == v2_count == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_1_3_count_distinct():
    """
    Full Test Name: test_11_1_3_count_distinct
    Test: Count unique values
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"},
        {"id": "4", "role": "user"},
        {"id": "5", "role": "guest"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Count distinct
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_distinct = len(set(r.get("role") for r in records))
        v1_time = time.perf_counter() - v1_start
        # V2: Count distinct
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_distinct = len(set(r.get("role") for r in records_v2))
        v2_time = time.perf_counter() - v2_start
        assert v1_distinct == v2_distinct == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_1_4_count_by_group():
    """
    Full Test Name: test_11_1_4_count_by_group
    Test: Count records per group
    """
    test_data = [
        {"id": "1", "role": "admin", "status": "active"},
        {"id": "2", "role": "user", "status": "active"},
        {"id": "3", "role": "admin", "status": "inactive"},
        {"id": "4", "role": "user", "status": "active"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Count by group
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_groups = defaultdict(int)
        for record in records:
            role = record.get("role")
            v1_groups[role] += 1
        v1_time = time.perf_counter() - v1_start
        assert v1_groups["admin"] == 2
        assert v1_groups["user"] == 2
        # V2: Count by group
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_groups = defaultdict(int)
        for record in records_v2:
            role = record.get("role")
            v2_groups[role] += 1
        v2_time = time.perf_counter() - v2_start
        assert v2_groups["admin"] == 2
        assert v2_groups["user"] == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 11.2 Mathematical Aggregations
# ============================================================================


def test_11_2_1_sum():
    """
    Full Test Name: test_11_2_1_sum
    Test: Sum numeric field values
    """
    test_data = [
        {"id": "1", "amount": 100},
        {"id": "2", "amount": 200},
        {"id": "3", "amount": 300}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Sum
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_sum = sum(r.get("amount", 0) for r in records)
        v1_time = time.perf_counter() - v1_start
        # V2: Sum
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_sum = sum(r.get("amount", 0) for r in records_v2)
        v2_time = time.perf_counter() - v2_start
        assert v1_sum == v2_sum == 600
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_2_2_average():
    """
    Full Test Name: test_11_2_2_average
    Test: Calculate average of numeric field
    """
    test_data = [
        {"id": "1", "score": 80},
        {"id": "2", "score": 90},
        {"id": "3", "score": 100}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Average
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        scores = [r.get("score", 0) for r in records]
        v1_avg = sum(scores) / len(scores) if scores else 0
        v1_time = time.perf_counter() - v1_start
        # V2: Average
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        scores_v2 = [r.get("score", 0) for r in records_v2]
        v2_avg = sum(scores_v2) / len(scores_v2) if scores_v2 else 0
        v2_time = time.perf_counter() - v2_start
        assert v1_avg == v2_avg == 90.0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_2_3_min():
    """
    Full Test Name: test_11_2_3_min
    Test: Find minimum value
    """
    test_data = [
        {"id": "1", "value": 50},
        {"id": "2", "value": 30},
        {"id": "3", "value": 70}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Min
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_min = min(r.get("value", float('inf')) for r in records)
        v1_time = time.perf_counter() - v1_start
        # V2: Min
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_min = min(r.get("value", float('inf')) for r in records_v2)
        v2_time = time.perf_counter() - v2_start
        assert v1_min == v2_min == 30
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_2_4_max():
    """
    Full Test Name: test_11_2_4_max
    Test: Find maximum value
    """
    test_data = [
        {"id": "1", "value": 50},
        {"id": "2", "value": 30},
        {"id": "3", "value": 70}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Max
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_max = max(r.get("value", float('-inf')) for r in records)
        v1_time = time.perf_counter() - v1_start
        # V2: Max
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_max = max(r.get("value", float('-inf')) for r in records_v2)
        v2_time = time.perf_counter() - v2_start
        assert v1_max == v2_max == 70
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_2_5_median():
    """
    Full Test Name: test_11_2_5_median
    Test: Find median value
    """
    test_data = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
        {"id": "3", "value": 30},
        {"id": "4", "value": 40},
        {"id": "5", "value": 50}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Median
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        values = sorted([r.get("value", 0) for r in records])
        n = len(values)
        v1_median = values[n // 2] if n % 2 == 1 else (values[n // 2 - 1] + values[n // 2]) / 2
        v1_time = time.perf_counter() - v1_start
        # V2: Median
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        values_v2 = sorted([r.get("value", 0) for r in records_v2])
        n_v2 = len(values_v2)
        v2_median = values_v2[n_v2 // 2] if n_v2 % 2 == 1 else (values_v2[n_v2 // 2 - 1] + values_v2[n_v2 // 2]) / 2
        v2_time = time.perf_counter() - v2_start
        assert v1_median == v2_median == 30
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_2_6_standard_deviation():
    """
    Full Test Name: test_11_2_6_standard_deviation
    Test: Calculate statistical deviation
    """
    test_data = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
        {"id": "3", "value": 30},
        {"id": "4", "value": 40},
        {"id": "5", "value": 50}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Standard deviation
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        values = [r.get("value", 0) for r in records]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        v1_std = math.sqrt(variance)
        v1_time = time.perf_counter() - v1_start
        # V2: Standard deviation
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        values_v2 = [r.get("value", 0) for r in records_v2]
        mean_v2 = sum(values_v2) / len(values_v2)
        variance_v2 = sum((x - mean_v2) ** 2 for x in values_v2) / len(values_v2)
        v2_std = math.sqrt(variance_v2)
        v2_time = time.perf_counter() - v2_start
        assert abs(v1_std - v2_std) < 0.001
        assert abs(v1_std - 14.142) < 1.0  # Approximate
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 11.3 Grouping
# ============================================================================


def test_11_3_1_group_by_field():
    """
    Full Test Name: test_11_3_1_group_by_field
    Test: Group records by field value
    """
    test_data = [
        {"id": "1", "role": "admin", "score": 90},
        {"id": "2", "role": "user", "score": 80},
        {"id": "3", "role": "admin", "score": 95},
        {"id": "4", "role": "user", "score": 85}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Group by field
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_groups = defaultdict(list)
        for record in records:
            role = record.get("role")
            v1_groups[role].append(record)
        v1_time = time.perf_counter() - v1_start
        assert len(v1_groups["admin"]) == 2
        assert len(v1_groups["user"]) == 2
        # V2: Group by field
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_groups = defaultdict(list)
        for record in records_v2:
            role = record.get("role")
            v2_groups[role].append(record)
        v2_time = time.perf_counter() - v2_start
        assert len(v2_groups["admin"]) == 2
        assert len(v2_groups["user"]) == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_3_2_group_by_multiple_fields():
    """
    Full Test Name: test_11_3_2_group_by_multiple_fields
    Test: Group by multiple fields
    """
    test_data = [
        {"id": "1", "role": "admin", "status": "active"},
        {"id": "2", "role": "user", "status": "active"},
        {"id": "3", "role": "admin", "status": "inactive"},
        {"id": "4", "role": "user", "status": "active"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Group by multiple fields
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_groups = defaultdict(list)
        for record in records:
            key = (record.get("role"), record.get("status"))
            v1_groups[key].append(record)
        v1_time = time.perf_counter() - v1_start
        assert len(v1_groups[("admin", "active")]) == 1
        assert len(v1_groups[("user", "active")]) == 2
        # V2: Group by multiple fields
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_groups = defaultdict(list)
        for record in records_v2:
            key = (record.get("role"), record.get("status"))
            v2_groups[key].append(record)
        v2_time = time.perf_counter() - v2_start
        assert len(v2_groups[("admin", "active")]) == 1
        assert len(v2_groups[("user", "active")]) == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_3_3_group_with_aggregation():
    """
    Full Test Name: test_11_3_3_group_with_aggregation
    Test: Group and aggregate within groups
    """
    test_data = [
        {"id": "1", "role": "admin", "score": 90},
        {"id": "2", "role": "user", "score": 80},
        {"id": "3", "role": "admin", "score": 95},
        {"id": "4", "role": "user", "score": 85}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Group with aggregation
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_groups = defaultdict(list)
        for record in records:
            role = record.get("role")
            v1_groups[role].append(record.get("score", 0))
        v1_aggregated = {role: sum(scores) / len(scores) for role, scores in v1_groups.items()}
        v1_time = time.perf_counter() - v1_start
        assert abs(v1_aggregated["admin"] - 92.5) < 0.1
        assert abs(v1_aggregated["user"] - 82.5) < 0.1
        # V2: Group with aggregation
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_groups = defaultdict(list)
        for record in records_v2:
            role = record.get("role")
            v2_groups[role].append(record.get("score", 0))
        v2_aggregated = {role: sum(scores) / len(scores) for role, scores in v2_groups.items()}
        v2_time = time.perf_counter() - v2_start
        assert abs(v2_aggregated["admin"] - 92.5) < 0.1
        assert abs(v2_aggregated["user"] - 82.5) < 0.1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_11_3_4_group_with_filtering():
    """
    Full Test Name: test_11_3_4_group_with_filtering
    Test: Group filtered records
    """
    test_data = [
        {"id": "1", "role": "admin", "status": "active", "score": 90},
        {"id": "2", "role": "user", "status": "active", "score": 80},
        {"id": "3", "role": "admin", "status": "inactive", "score": 95},
        {"id": "4", "role": "user", "status": "active", "score": 85}
    ]
    file_path = create_test_file(test_data)
    try:
        def is_active(obj):
            return obj.get("status") == "active"
        # V1: Group with filtering
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, is_active)
        v1_groups = defaultdict(list)
        for record in records:
            role = record.get("role")
            v1_groups[role].append(record)
        v1_time = time.perf_counter() - v1_start
        assert len(v1_groups["admin"]) == 1
        assert len(v1_groups["user"]) == 2
        # V2: Group with filtering
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, is_active, index=index)
        v2_groups = defaultdict(list)
        for record in records_v2:
            role = record.get("role")
            v2_groups[role].append(record)
        v2_time = time.perf_counter() - v2_start
        assert len(v2_groups["admin"]) == 1
        assert len(v2_groups["user"]) == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
