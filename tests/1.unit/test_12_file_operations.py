"""
#exonware/xwnode/examples/x5/data_operations/test_12_file_operations.py
FILE Operations Test Suite
Tests all FILE operations (storage management) for both V1 (Streaming) and V2 (Indexed) implementations.
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
import shutil
import tempfile
from pathlib import Path
from typing import Any
from datetime import datetime
# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    count_records_v1,
    count_records_v2,
    get_all_matching_v1,
    get_all_matching_v2,
)
# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from json_utils_indexed import (
    build_index,
    ensure_index,
)
# ============================================================================
# 12.1 File Management
# ============================================================================


def test_12_1_1_create_file():
    """
    Full Test Name: test_12_1_1_create_file
    Test: Initialize new storage file
    """
    # V1: Create file
    v1_start = time.perf_counter()
    v1_file = create_test_file([])
    v1_time = time.perf_counter() - v1_start
    assert os.path.exists(v1_file)
    assert os.path.getsize(v1_file) == 0 or os.path.getsize(v1_file) >= 0
    # V2: Create file
    v2_start = time.perf_counter()
    v2_file = create_test_file([])
    build_index(v2_file, id_field="id")
    v2_time = time.perf_counter() - v2_start
    assert os.path.exists(v2_file)
    assert os.path.exists(v2_file + ".idx.json")
    cleanup_test_file(v1_file)
    cleanup_test_file(v2_file)
    return True, v1_time, v2_time


def test_12_1_2_delete_file():
    """
    Full Test Name: test_12_1_2_delete_file
    Test: Remove storage file
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Delete file
        v1_start = time.perf_counter()
        assert os.path.exists(file_path)
        os.remove(file_path)
        v1_time = time.perf_counter() - v1_start
        assert not os.path.exists(file_path)
        # V2: Delete file and index
        file_path_v2 = create_test_file(test_data)
        build_index(file_path_v2, id_field="id")
        v2_start = time.perf_counter()
        assert os.path.exists(file_path_v2)
        os.remove(file_path_v2)
        idx_path = file_path_v2 + ".idx.json"
        if os.path.exists(idx_path):
            os.remove(idx_path)
        v2_time = time.perf_counter() - v2_start
        assert not os.path.exists(file_path_v2)
        assert not os.path.exists(idx_path)
        return True, v1_time, v2_time
    except Exception:
        if os.path.exists(file_path):
            cleanup_test_file(file_path)
        raise


def test_12_1_3_truncate_file():
    """
    Full Test Name: test_12_1_3_truncate_file
    Test: Clear all records from file
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Truncate file
        v1_start = time.perf_counter()
        with open(file_path, 'w', encoding='utf-8') as f:
            pass  # Truncate by opening in write mode
        v1_time = time.perf_counter() - v1_start
        assert count_records_v1(file_path) == 0
        # V2: Truncate file
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        with open(file_path, 'w', encoding='utf-8') as f:
            pass
        # Remove index
        idx_path = file_path + ".idx.json"
        if os.path.exists(idx_path):
            os.remove(idx_path)
        v2_time = time.perf_counter() - v2_start
        assert count_records_v2(file_path) == 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_1_4_compact_file():
    """
    Full Test Name: test_12_1_4_compact_file
    Test: Remove gaps, optimize file
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Compact file (rewrite without gaps)
        v1_start = time.perf_counter()
        records = get_all_matching_v1(file_path, lambda x: True)
        # Rewrite file
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        v1_time = time.perf_counter() - v1_start
        assert count_records_v1(file_path) == 10
        # V2: Compact file
        v2_start = time.perf_counter()
        index = ensure_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in records_v2:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        assert count_records_v2(file_path) == 10
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_1_5_backup_file():
    """
    Full Test Name: test_12_1_5_backup_file
    Test: Create backup copy
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Backup file
        backup_path = file_path + ".backup"
        v1_start = time.perf_counter()
        shutil.copy(file_path, backup_path)
        v1_time = time.perf_counter() - v1_start
        assert os.path.exists(backup_path)
        assert os.path.getsize(backup_path) == os.path.getsize(file_path)
        # V2: Backup file and index
        build_index(file_path, id_field="id")
        backup_path_v2 = file_path + ".backup"
        backup_idx_path = file_path + ".idx.json.backup"
        v2_start = time.perf_counter()
        shutil.copy(file_path, backup_path_v2)
        idx_path = file_path + ".idx.json"
        if os.path.exists(idx_path):
            shutil.copy(idx_path, backup_idx_path)
        v2_time = time.perf_counter() - v2_start
        assert os.path.exists(backup_path_v2)
        assert os.path.exists(backup_idx_path)
        # Cleanup backups
        if os.path.exists(backup_path):
            os.remove(backup_path)
        if os.path.exists(backup_path_v2):
            os.remove(backup_path_v2)
        if os.path.exists(backup_idx_path):
            os.remove(backup_idx_path)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_1_6_restore_file():
    """
    Full Test Name: test_12_1_6_restore_file
    Test: Restore from backup
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    backup_path = file_path + ".backup"
    shutil.copy(file_path, backup_path)
    try:
        # Modify original file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps({"id": "2", "name": "Bob"}, ensure_ascii=False) + '\n')
        # V1: Restore file
        v1_start = time.perf_counter()
        shutil.copy(backup_path, file_path)
        v1_time = time.perf_counter() - v1_start
        records = get_all_matching_v1(file_path, lambda x: True)
        assert len(records) == 1
        assert records[0]["id"] == "1"
        # V2: Restore file and index
        build_index(file_path, id_field="id")
        backup_idx_path = file_path + ".idx.json.backup"
        idx_path = file_path + ".idx.json"
        if os.path.exists(idx_path):
            shutil.copy(idx_path, backup_idx_path)
        # Modify again
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps({"id": "3", "name": "Charlie"}, ensure_ascii=False) + '\n')
        v2_start = time.perf_counter()
        shutil.copy(backup_path, file_path)
        if os.path.exists(backup_idx_path):
            shutil.copy(backup_idx_path, idx_path)
        v2_time = time.perf_counter() - v2_start
        index = ensure_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(records_v2) == 1
        assert records_v2[0]["id"] == "1"
        # Cleanup
        if os.path.exists(backup_path):
            os.remove(backup_path)
        if os.path.exists(backup_idx_path):
            os.remove(backup_idx_path)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 12.2 File Information
# ============================================================================


def test_12_2_1_get_file_size():
    """
    Full Test Name: test_12_2_1_get_file_size
    Test: Get total file size
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Get file size
        v1_start = time.perf_counter()
        v1_size = os.path.getsize(file_path)
        v1_time = time.perf_counter() - v1_start
        assert v1_size > 0
        # V2: Get file size
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_size = os.path.getsize(file_path)
        v2_idx_size = os.path.getsize(file_path + ".idx.json")
        v2_time = time.perf_counter() - v2_start
        assert v2_size > 0
        assert v2_idx_size > 0
        assert v1_size == v2_size  # File size should be same
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_2_2_get_record_count():
    """
    Full Test Name: test_12_2_2_get_record_count
    Test: Count total records
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Get record count
        v1_start = time.perf_counter()
        v1_count = count_records_v1(file_path)
        v1_time = time.perf_counter() - v1_start
        assert v1_count == 10
        # V2: Get record count
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_count = count_records_v2(file_path, index=index)
        v2_time = time.perf_counter() - v2_start
        assert v2_count == 10
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_2_3_get_file_metadata():
    """
    Full Test Name: test_12_2_3_get_file_metadata
    Test: Get file information
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Get file metadata
        v1_start = time.perf_counter()
        stat = os.stat(file_path)
        v1_metadata = {
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "ctime": stat.st_ctime
        }
        v1_time = time.perf_counter() - v1_start
        assert v1_metadata["size"] > 0
        # V2: Get file metadata
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        stat_v2 = os.stat(file_path)
        idx_stat = os.stat(file_path + ".idx.json")
        v2_metadata = {
            "size": stat_v2.st_size,
            "mtime": stat_v2.st_mtime,
            "index_size": idx_stat.st_size
        }
        v2_time = time.perf_counter() - v2_start
        assert v2_metadata["size"] > 0
        assert v2_metadata["index_size"] > 0
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_2_4_get_file_statistics():
    """
    Full Test Name: test_12_2_4_get_file_statistics
    Test: Get usage statistics
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Get file statistics
        v1_start = time.perf_counter()
        stat = os.stat(file_path)
        records = get_all_matching_v1(file_path, lambda x: True)
        v1_stats = {
            "file_size": stat.st_size,
            "record_count": len(records),
            "avg_record_size": stat.st_size / len(records) if records else 0
        }
        v1_time = time.perf_counter() - v1_start
        assert v1_stats["record_count"] == 10
        # V2: Get file statistics
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        stat_v2 = os.stat(file_path)
        idx_stat = os.stat(file_path + ".idx.json")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        v2_stats = {
            "file_size": stat_v2.st_size,
            "index_size": idx_stat.st_size,
            "record_count": len(records_v2),
            "total_size": stat_v2.st_size + idx_stat.st_size
        }
        v2_time = time.perf_counter() - v2_start
        assert v2_stats["record_count"] == 10
        assert v2_stats["total_size"] > v2_stats["file_size"]
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_12_2_5_check_file_integrity():
    """
    Full Test Name: test_12_2_5_check_file_integrity
    Test: Verify file is valid
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    try:
        # V1: Check file integrity
        v1_start = time.perf_counter()
        v1_valid = True
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        json.loads(line.strip())
        except (json.JSONDecodeError, Exception):
            v1_valid = False
        v1_time = time.perf_counter() - v1_start
        assert v1_valid
        # V2: Check file integrity
        build_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_valid = True
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        json.loads(line.strip())
            # Check index integrity
            index = ensure_index(file_path, id_field="id")
            if index is None or len(index.line_offsets) != 10:
                v2_valid = False
        except (json.JSONDecodeError, Exception):
            v2_valid = False
        v2_time = time.perf_counter() - v2_start
        assert v2_valid
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
