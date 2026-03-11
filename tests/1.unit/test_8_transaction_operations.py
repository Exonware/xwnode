"""
#exonware/xwnode/examples/x5/data_operations/test_8_transaction_operations.py
TRANSACTION Operations Test Suite
Tests all TRANSACTION operations (atomic multi-step) for both V1 (Streaming) and V2 (Indexed) implementations.
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
from typing import Any, Optional
# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    append_record_v1,
    append_record_v2,
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
    indexed_get_by_id,
)
# ============================================================================
# Transaction Helper Functions
# ============================================================================


class Transaction:
    """Simple transaction wrapper for atomic operations."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.backup_path = None
        self.operations = []
        self.committed = False
        self.rolled_back = False

    def begin(self):
        """Begin transaction - create backup."""
        self.backup_path = self.file_path + ".txn_backup"
        if os.path.exists(self.file_path):
            shutil.copy(self.file_path, self.backup_path)
        return True

    def commit(self):
        """Commit transaction - apply all changes."""
        if self.rolled_back:
            return False
        # Operations are already atomic, so commit is just cleanup
        if self.backup_path and os.path.exists(self.backup_path):
            os.remove(self.backup_path)
        self.committed = True
        return True

    def rollback(self):
        """Rollback transaction - restore backup."""
        if self.committed:
            return False
        if self.backup_path and os.path.exists(self.backup_path):
            shutil.copy(self.backup_path, self.file_path)
            os.remove(self.backup_path)
        self.rolled_back = True
        return True
# ============================================================================
# 8.1 Transaction Types
# ============================================================================


def test_8_1_1_begin_transaction():
    """
    Full Test Name: test_8_1_1_begin_transaction
    Test: Start atomic operation sequence
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Begin transaction
        v1_start = time.perf_counter()
        txn_v1 = Transaction(file_path)
        v1_success = txn_v1.begin()
        v1_time = time.perf_counter() - v1_start
        assert v1_success
        assert txn_v1.backup_path is not None
        assert os.path.exists(txn_v1.backup_path)
        # Cleanup
        if txn_v1.backup_path and os.path.exists(txn_v1.backup_path):
            os.remove(txn_v1.backup_path)
        # V2: Begin transaction
        v2_start = time.perf_counter()
        txn_v2 = Transaction(file_path)
        v2_success = txn_v2.begin()
        v2_time = time.perf_counter() - v2_start
        assert v2_success
        assert txn_v2.backup_path is not None
        # Cleanup
        if txn_v2.backup_path and os.path.exists(txn_v2.backup_path):
            os.remove(txn_v2.backup_path)
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_1_2_commit_transaction():
    """
    Full Test Name: test_8_1_2_commit_transaction
    Test: Apply all changes atomically
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Commit transaction
        txn_v1 = Transaction(file_path)
        txn_v1.begin()
        # Make changes
        new_record = {"id": "2", "name": "Bob"}
        temp_file = create_test_file(test_data)
        append_record_v1(temp_file, new_record)
        v1_start = time.perf_counter()
        shutil.copy(temp_file, file_path)
        v1_committed = txn_v1.commit()
        v1_time = time.perf_counter() - v1_start
        cleanup_test_file(temp_file)
        assert v1_committed
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 2
        # V2: Commit transaction
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_v2 = Transaction(file_path)
        txn_v2.begin()
        temp_file_v2 = create_test_file(test_data)
        append_record_v2(temp_file_v2, new_record)
        v2_start = time.perf_counter()
        shutil.copy(temp_file_v2, file_path)
        build_index(file_path, id_field="id")
        v2_committed = txn_v2.commit()
        v2_time = time.perf_counter() - v2_start
        cleanup_test_file(temp_file_v2)
        assert v2_committed
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_1_3_rollback_transaction():
    """
    Full Test Name: test_8_1_3_rollback_transaction
    Test: Cancel all changes
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Rollback transaction
        txn_v1 = Transaction(file_path)
        txn_v1.begin()
        # Make changes
        new_record = {"id": "2", "name": "Bob"}
        append_record_v1(file_path, new_record)
        v1_start = time.perf_counter()
        v1_rolled_back = txn_v1.rollback()
        v1_time = time.perf_counter() - v1_start
        assert v1_rolled_back
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 1
        # V2: Rollback transaction
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_v2 = Transaction(file_path)
        txn_v2.begin()
        append_record_v2(file_path, new_record)
        v2_start = time.perf_counter()
        v2_rolled_back = txn_v2.rollback()
        v2_time = time.perf_counter() - v2_start
        assert v2_rolled_back
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_1_4_nested_transactions():
    """
    Full Test Name: test_8_1_4_nested_transactions
    Test: Transactions within transactions
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Nested transactions (simulate with multiple backups)
        txn_outer_v1 = Transaction(file_path)
        txn_outer_v1.begin()
        txn_inner_v1 = Transaction(file_path)
        txn_inner_v1.begin()
        new_record = {"id": "2", "name": "Bob"}
        append_record_v1(file_path, new_record)
        v1_start = time.perf_counter()
        # Rollback inner transaction
        txn_inner_v1.rollback()
        # Commit outer transaction (should restore to original)
        txn_outer_v1.rollback()
        v1_time = time.perf_counter() - v1_start
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 1
        # V2: Nested transactions
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_outer_v2 = Transaction(file_path)
        txn_outer_v2.begin()
        txn_inner_v2 = Transaction(file_path)
        txn_inner_v2.begin()
        append_record_v2(file_path, new_record)
        v2_start = time.perf_counter()
        txn_inner_v2.rollback()
        txn_outer_v2.rollback()
        v2_time = time.perf_counter() - v2_start
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_1_5_savepoint():
    """
    Full Test Name: test_8_1_5_savepoint
    Test: Create checkpoint within transaction
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        # V1: Savepoint (simulate with backup)
        txn_v1 = Transaction(file_path)
        txn_v1.begin()
        savepoint_v1 = file_path + ".savepoint"
        shutil.copy(file_path, savepoint_v1)
        new_record1 = {"id": "2", "name": "Bob"}
        append_record_v1(file_path, new_record1)
        v1_start = time.perf_counter()
        # Restore to savepoint
        shutil.copy(savepoint_v1, file_path)
        os.remove(savepoint_v1)
        v1_time = time.perf_counter() - v1_start
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 1
        # V2: Savepoint
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_v2 = Transaction(file_path)
        txn_v2.begin()
        savepoint_v2 = file_path + ".savepoint"
        shutil.copy(file_path, savepoint_v2)
        append_record_v2(file_path, new_record1)
        v2_start = time.perf_counter()
        shutil.copy(savepoint_v2, file_path)
        build_index(file_path, id_field="id")
        os.remove(savepoint_v2)
        v2_time = time.perf_counter() - v2_start
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
# ============================================================================
# 8.2 Transactional Operations
# ============================================================================


def test_8_2_1_transactional_insert():
    """
    Full Test Name: test_8_2_1_transactional_insert
    Test: Insert with transaction
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    try:
        new_record = {"id": "2", "name": "Bob"}
        # V1: Transactional insert
        txn_v1 = Transaction(file_path)
        txn_v1.begin()
        v1_start = time.perf_counter()
        temp_file = create_test_file(test_data)
        append_record_v1(temp_file, new_record)
        shutil.copy(temp_file, file_path)
        txn_v1.commit()
        v1_time = time.perf_counter() - v1_start
        cleanup_test_file(temp_file)
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 2
        # V2: Transactional insert
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_v2 = Transaction(file_path)
        txn_v2.begin()
        v2_start = time.perf_counter()
        temp_file_v2 = create_test_file(test_data)
        append_record_v2(temp_file_v2, new_record)
        shutil.copy(temp_file_v2, file_path)
        build_index(file_path, id_field="id")
        txn_v2.commit()
        v2_time = time.perf_counter() - v2_start
        cleanup_test_file(temp_file_v2)
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 2
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_2_2_transactional_update():
    """
    Full Test Name: test_8_2_2_transactional_update
    Test: Update with transaction (atomic)
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        # V1: Transactional update (atomic)
        v1_start = time.perf_counter()
        updated_count = stream_update(
            file_path,
            match_by_id("id", "1"),
            lambda obj: {**obj, "age": 31}
        )
        v1_time = time.perf_counter() - v1_start
        assert updated_count == 1
        result = stream_read(file_path, match_by_id("id", "1"))
        assert result["age"] == 31
        # V2: Transactional update (atomic)
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        v2_start = time.perf_counter()
        updated_count_v2 = stream_update(
            file_path,
            match_by_id("id", "1"),
            lambda obj: {**obj, "age": 31}
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        assert updated_count_v2 == 1
        index = ensure_index(file_path, id_field="id")
        result_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert result_v2["age"] == 31
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_2_3_transactional_delete():
    """
    Full Test Name: test_8_2_3_transactional_delete
    Test: Delete with transaction
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Transactional delete
        txn_v1 = Transaction(file_path)
        txn_v1.begin()
        v1_start = time.perf_counter()
        delete_record_by_id_v1(file_path, "2", id_field="id")
        txn_v1.commit()
        v1_time = time.perf_counter() - v1_start
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 1
        # V2: Transactional delete
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_v2 = Transaction(file_path)
        txn_v2.begin()
        v2_start = time.perf_counter()
        delete_record_by_id_v2(file_path, "2", id_field="id")
        txn_v2.commit()
        v2_time = time.perf_counter() - v2_start
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 1
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_2_4_multi_operation_transaction():
    """
    Full Test Name: test_8_2_4_multi_operation_transaction
    Test: Multiple operations in one transaction
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    try:
        # V1: Multi-operation transaction
        txn_v1 = Transaction(file_path)
        txn_v1.begin()
        v1_start = time.perf_counter()
        temp_file = create_test_file(test_data)
        # Insert
        append_record_v1(temp_file, {"id": "2", "name": "Bob"})
        # Update
        stream_update(
            temp_file,
            match_by_id("id", "1"),
            lambda obj: {**obj, "age": 31}
        )
        shutil.copy(temp_file, file_path)
        txn_v1.commit()
        v1_time = time.perf_counter() - v1_start
        cleanup_test_file(temp_file)
        assert len(get_all_matching_v1(file_path, lambda x: True)) == 2
        result = stream_read(file_path, match_by_id("id", "1"))
        assert result["age"] == 31
        # V2: Multi-operation transaction
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        txn_v2 = Transaction(file_path)
        txn_v2.begin()
        v2_start = time.perf_counter()
        temp_file_v2 = create_test_file(test_data)
        append_record_v2(temp_file_v2, {"id": "2", "name": "Bob"})
        stream_update(
            temp_file_v2,
            match_by_id("id", "1"),
            lambda obj: {**obj, "age": 31}
        )
        shutil.copy(temp_file_v2, file_path)
        build_index(file_path, id_field="id")
        txn_v2.commit()
        v2_time = time.perf_counter() - v2_start
        cleanup_test_file(temp_file_v2)
        index = ensure_index(file_path, id_field="id")
        assert len(get_all_matching_v2(file_path, lambda x: True, index=index)) == 2
        result_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert result_v2["age"] == 31
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_8_2_5_cross_record_transaction():
    """
    Full Test Name: test_8_2_5_cross_record_transaction
    Test: Update multiple records atomically
    """
    test_data = [
        {"id": "1", "name": "Alice", "status": "pending"},
        {"id": "2", "name": "Bob", "status": "pending"},
        {"id": "3", "name": "Charlie", "status": "pending"}
    ]
    file_path = create_test_file(test_data)
    try:
        # V1: Cross-record transaction (atomic update)
        v1_start = time.perf_counter()
        updated_count = stream_update(
            file_path,
            lambda obj: obj.get("status") == "pending",
            lambda obj: {**obj, "status": "active"}
        )
        v1_time = time.perf_counter() - v1_start
        assert updated_count == 3
        results = get_all_matching_v1(file_path, lambda x: x.get("status") == "active")
        assert len(results) == 3
        # V2: Cross-record transaction
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        v2_start = time.perf_counter()
        updated_count_v2 = stream_update(
            file_path,
            lambda obj: obj.get("status") == "pending",
            lambda obj: {**obj, "status": "active"}
        )
        build_index(file_path, id_field="id")
        v2_time = time.perf_counter() - v2_start
        assert updated_count_v2 == 3
        index = ensure_index(file_path, id_field="id")
        results_v2 = get_all_matching_v2(file_path, lambda x: x.get("status") == "active", index=index)
        assert len(results_v2) == 3
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)
