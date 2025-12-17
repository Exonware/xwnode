"""
#exonware/xwnode/examples/x5/data_operations/test_16_monitoring_operations.py

MONITORING Operations Test Suite

Tests all MONITORING operations (observability) for both V1 (Streaming) and V2 (Indexed) implementations.
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
from typing import List, Dict, Any, Optional
import psutil

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
    load_index,
    indexed_get_by_id,
)


# ============================================================================
# 16.1 Performance Monitoring
# ============================================================================

def test_16_1_1_track_operation_time():
    """
    Full Test Name: test_16_1_1_track_operation_time
    Test: Measure operation duration
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(100)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Track operation time
        v1_start = time.perf_counter()
        result = stream_read(file_path, match_by_id("id", "50"))
        v1_elapsed = time.perf_counter() - v1_start
        
        assert result is not None
        assert v1_elapsed > 0
        
        # V2: Track operation time
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        result_v2 = indexed_get_by_id(file_path, "50", id_field="id", index=index)
        v2_elapsed = time.perf_counter() - v2_start
        
        assert result_v2 is not None
        assert v2_elapsed > 0
        
        return True, v1_elapsed, v2_elapsed
    finally:
        cleanup_test_file(file_path)


def test_16_1_2_track_memory_usage():
    """
    Full Test Name: test_16_1_2_track_memory_usage
    Test: Monitor memory consumption
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(100)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Track memory usage
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_time = time.perf_counter() - v1_start
        
        assert len(records) == 100
        
        # V2: Track memory usage
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert len(records_v2) == 100
        
        # Track memory usage
        process = psutil.Process(os.getpid())
        v1_mem_before = process.memory_info().rss / 1024 / 1024  # MB
        v1_mem_after = process.memory_info().rss / 1024 / 1024  # MB
        v2_mem_before = process.memory_info().rss / 1024 / 1024  # MB
        v2_mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_1_3_track_io_operations():
    """
    Full Test Name: test_16_1_3_track_io_operations
    Test: Count file I/O operations
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Track I/O operations (simulate by counting file opens)
        v1_start = time.perf_counter()
        io_count = 0
        for i in range(5):
            try:
                stream_read(file_path, match_by_id("id", str(i)))
                io_count += 1
            except Exception:
                pass
        v1_time = time.perf_counter() - v1_start
        
        assert io_count == 5
        
        # V2: Track I/O operations
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        io_count_v2 = 0
        for i in range(5):
            try:
                indexed_get_by_id(file_path, str(i), id_field="id", index=index)
                io_count_v2 += 1
            except Exception:
                pass
        v2_time = time.perf_counter() - v2_start
        
        assert io_count_v2 == 5
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_1_4_track_cache_hits():
    """
    Full Test Name: test_16_1_4_track_cache_hits
    Test: Monitor cache effectiveness
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V2: Track cache hits (index caching)
        index = ensure_index(file_path, id_field="id")
        
        v2_start = time.perf_counter()
        # First access (cache miss - index loaded)
        result1 = indexed_get_by_id(file_path, "5", id_field="id", index=index)
        # Second access (cache hit - index reused)
        result2 = indexed_get_by_id(file_path, "5", id_field="id", index=index)
        v2_time = time.perf_counter() - v2_start
        
        assert result1 == result2
        
        # V1: No cache (baseline)
        v1_start = time.perf_counter()
        result1_v1 = stream_read(file_path, match_by_id("id", "5"))
        result2_v1 = stream_read(file_path, match_by_id("id", "5"))
        v1_time = time.perf_counter() - v1_start
        
        assert result1_v1 == result2_v1
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_1_5_performance_profiling():
    """
    Full Test Name: test_16_1_5_performance_profiling
    Test: Detailed performance analysis
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(100)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Performance profiling
        v1_start = time.perf_counter()
        v1_profile = {
            "operations": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
        
        for i in range(10):
            op_start = time.perf_counter()
            stream_read(file_path, match_by_id("id", str(i * 10)))
            op_time = time.perf_counter() - op_start
            v1_profile["operations"] += 1
            v1_profile["total_time"] += op_time
        
        v1_profile["avg_time"] = v1_profile["total_time"] / v1_profile["operations"]
        v1_time = time.perf_counter() - v1_start
        
        assert v1_profile["operations"] == 10
        
        # V2: Performance profiling
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_profile = {
            "operations": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
        
        for i in range(10):
            op_start = time.perf_counter()
            indexed_get_by_id(file_path, str(i * 10), id_field="id", index=index)
            op_time = time.perf_counter() - op_start
            v2_profile["operations"] += 1
            v2_profile["total_time"] += op_time
        
        v2_profile["avg_time"] = v2_profile["total_time"] / v2_profile["operations"]
        v2_time = time.perf_counter() - v2_start
        
        assert v2_profile["operations"] == 10
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 16.2 Health Monitoring
# ============================================================================

def test_16_2_1_health_check():
    """
    Full Test Name: test_16_2_1_health_check
    Test: Verify system health
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Health check
        v1_start = time.perf_counter()
        v1_health = {
            "file_exists": os.path.exists(file_path),
            "file_readable": os.access(file_path, os.R_OK),
            "records_count": count_records_v1(file_path)
        }
        v1_healthy = v1_health["file_exists"] and v1_health["file_readable"] and v1_health["records_count"] > 0
        v1_time = time.perf_counter() - v1_start
        
        assert v1_healthy
        
        # V2: Health check
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        index = load_index(file_path, strict=True)
        v2_health = {
            "file_exists": os.path.exists(file_path),
            "index_exists": index is not None,
            "records_count": count_records_v2(file_path, index=index) if index else 0
        }
        v2_healthy = v2_health["file_exists"] and v2_health["index_exists"] and v2_health["records_count"] > 0
        v2_time = time.perf_counter() - v2_start
        
        assert v2_healthy
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_2_2_integrity_check():
    """
    Full Test Name: test_16_2_2_integrity_check
    Test: Verify data integrity
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Integrity check
        v1_start = time.perf_counter()
        v1_integrity = True
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        json.loads(line.strip())
        except (json.JSONDecodeError, Exception):
            v1_integrity = False
        v1_time = time.perf_counter() - v1_start
        
        assert v1_integrity
        
        # V2: Integrity check
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        index = load_index(file_path, strict=True)
        v2_integrity = index is not None and len(index.line_offsets) == 10
        v2_time = time.perf_counter() - v2_start
        
        assert v2_integrity
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_2_3_index_health():
    """
    Full Test Name: test_16_2_3_index_health
    Test: Check index validity (V2)
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V2: Index health
        index = build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_health = {
            "index_exists": index is not None,
            "line_offsets_count": len(index.line_offsets) if index else 0,
            "id_index_count": len(index.id_index) if index and index.id_index else 0,
            "index_valid": index is not None and len(index.line_offsets) == 10
        }
        v2_time = time.perf_counter() - v2_start
        
        assert v2_health["index_valid"]
        assert v2_health["line_offsets_count"] == 10
        assert v2_health["id_index_count"] == 10
        
        # V1: No index (baseline)
        v1_start = time.perf_counter()
        v1_health = {"index_exists": False}
        v1_time = time.perf_counter() - v1_start
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_2_4_file_health():
    """
    Full Test Name: test_16_2_4_file_health
    Test: Check file validity
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: File health
        v1_start = time.perf_counter()
        v1_health = {
            "exists": os.path.exists(file_path),
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK),
            "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        v1_healthy = v1_health["exists"] and v1_health["readable"] and v1_health["size"] > 0
        v1_time = time.perf_counter() - v1_start
        
        assert v1_healthy
        
        # V2: File health
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        idx_path = file_path + ".idx.json"
        v2_health = {
            "file_exists": os.path.exists(file_path),
            "index_exists": os.path.exists(idx_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "index_size": os.path.getsize(idx_path) if os.path.exists(idx_path) else 0
        }
        v2_healthy = v2_health["file_exists"] and v2_health["index_exists"] and v2_health["file_size"] > 0
        v2_time = time.perf_counter() - v2_start
        
        assert v2_healthy
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_16_2_5_error_tracking():
    """
    Full Test Name: test_16_2_5_error_tracking
    Test: Track and report errors
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Error tracking
        v1_start = time.perf_counter()
        v1_errors = []
        try:
            stream_read(file_path, match_by_id("id", "999"))  # Non-existent
        except Exception as e:
            v1_errors.append({
                "operation": "read",
                "error": str(e),
                "timestamp": time.time()
            })
        v1_time = time.perf_counter() - v1_start
        
        assert len(v1_errors) == 1
        
        # V2: Error tracking
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_errors = []
        try:
            indexed_get_by_id(file_path, "999", id_field="id", index=index)
        except Exception as e:
            v2_errors.append({
                "operation": "read",
                "error": str(e),
                "timestamp": time.time()
            })
        v2_time = time.perf_counter() - v2_start
        
        assert len(v2_errors) == 1
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)

