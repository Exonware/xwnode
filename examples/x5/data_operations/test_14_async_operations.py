"""
#exonware/xwnode/examples/x5/data_operations/test_14_async_operations.py

ASYNC Operations Test Suite

Tests all ASYNC operations (non-blocking) for both V1 (Streaming) and V2 (Indexed) implementations.
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
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Import test helpers
sys.path.insert(0, str(Path(__file__).parent))
from test_helpers import (
    create_test_file,
    cleanup_test_file,
    get_all_matching_v1,
    get_all_matching_v2,
    append_record_v1,
)

# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from json_utils import (
    match_by_id,
    stream_read,
    async_stream_read,
    async_stream_update,
)
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_id,
    async_indexed_get_by_id,
    async_get_page,
)


# ============================================================================
# 14.1 Async Read
# ============================================================================

def test_14_1_1_async_get_by_id():
    """
    Full Test Name: test_14_1_1_async_get_by_id
    Test: Non-blocking read by ID
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Async get by ID
        v1_start = time.perf_counter()
        async def async_read_v1():
            return await async_stream_read(file_path, match_by_id("id", "1"))
        
        v1_result = asyncio.run(async_read_v1())
        v1_time = time.perf_counter() - v1_start
        
        assert v1_result["id"] == "1"
        
        # V2: Async get by ID
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        v2_result = asyncio.run(async_indexed_get_by_id(file_path, "1", id_field="id", index=index))
        v2_time = time.perf_counter() - v2_start
        
        assert v2_result["id"] == "1"
        assert v1_result == v2_result
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_14_1_2_async_get_matching():
    """
    Full Test Name: test_14_1_2_async_get_matching
    Test: Non-blocking filtered read
    """
    test_data = [
        {"id": "1", "role": "admin"},
        {"id": "2", "role": "user"},
        {"id": "3", "role": "admin"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        def is_admin(obj):
            return obj.get("role") == "admin"
        
        # V1: Async get matching
        v1_start = time.perf_counter()
        async def async_get_matching_v1():
            # Get first matching
            return await async_stream_read(file_path, is_admin)
        
        v1_result = asyncio.run(async_get_matching_v1())
        v1_time = time.perf_counter() - v1_start
        
        assert v1_result.get("role") == "admin"
        
        # V2: Async get matching (simulate by getting all and filtering)
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        async def async_get_matching_v2():
            # Get all records asynchronously
            tasks = [
                async_indexed_get_by_id(file_path, str(i), id_field="id", index=index)
                for i in range(1, 4)
            ]
            results = await asyncio.gather(*tasks)
            return [r for r in results if is_admin(r)]
        
        v2_results = asyncio.run(async_get_matching_v2())
        v2_time = time.perf_counter() - v2_start
        
        assert len(v2_results) == 2
        assert all(r.get("role") == "admin" for r in v2_results)
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_14_1_3_async_stream():
    """
    Full Test Name: test_14_1_3_async_stream
    Test: Non-blocking record streaming
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(10)]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Async stream
        v1_start = time.perf_counter()
        async def async_stream_v1():
            results = []
            for i in range(10):
                result = await async_stream_read(file_path, match_by_id("id", str(i)))
                results.append(result)
            return results
        
        v1_results = asyncio.run(async_stream_v1())
        v1_time = time.perf_counter() - v1_start
        
        assert len(v1_results) == 10
        
        # V2: Async stream
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        async def async_stream_v2():
            tasks = [
                async_indexed_get_by_id(file_path, str(i), id_field="id", index=index)
                for i in range(10)
            ]
            return await asyncio.gather(*tasks)
        
        v2_results = asyncio.run(async_stream_v2())
        v2_time = time.perf_counter() - v2_start
        
        assert len(v2_results) == 10
        assert v1_results == v2_results
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_14_1_4_async_bulk_read():
    """
    Full Test Name: test_14_1_4_async_bulk_read
    Test: Non-blocking bulk retrieval
    """
    test_data = [{"id": str(i), "name": f"User{i}"} for i in range(20)]
    file_path = create_test_file(test_data)
    
    try:
        id_list = ["1", "3", "5", "7", "9"]
        
        # V1: Async bulk read
        v1_start = time.perf_counter()
        async def async_bulk_read_v1():
            tasks = [
                async_stream_read(file_path, match_by_id("id", record_id))
                for record_id in id_list
            ]
            return await asyncio.gather(*tasks)
        
        v1_results = asyncio.run(async_bulk_read_v1())
        v1_time = time.perf_counter() - v1_start
        
        assert len(v1_results) == 5
        
        # V2: Async bulk read
        index = ensure_index(file_path, id_field="id")
        v2_start = time.perf_counter()
        async def async_bulk_read_v2():
            tasks = [
                async_indexed_get_by_id(file_path, record_id, id_field="id", index=index)
                for record_id in id_list
            ]
            return await asyncio.gather(*tasks)
        
        v2_results = asyncio.run(async_bulk_read_v2())
        v2_time = time.perf_counter() - v2_start
        
        assert len(v2_results) == 5
        assert v1_results == v2_results
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


# ============================================================================
# 14.2 Async Write
# ============================================================================

def test_14_2_1_async_insert():
    """
    Full Test Name: test_14_2_1_async_insert
    Test: Non-blocking insert
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        new_record = {"id": "2", "name": "Bob"}
        
        # V1: Async insert (simulate with sync append in async context)
        v1_start = time.perf_counter()
        async def async_insert_v1():
            await asyncio.to_thread(append_record_v1, file_path, new_record)
        
        asyncio.run(async_insert_v1())
        v1_time = time.perf_counter() - v1_start
        
        result = stream_read(file_path, match_by_id("id", "2"))
        assert result == new_record
        
        # V2: Async insert
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        
        v2_start = time.perf_counter()
        async def async_insert_v2():
            await asyncio.to_thread(append_record_v1, file_path, new_record)
            await asyncio.to_thread(build_index, file_path, id_field="id")
        
        asyncio.run(async_insert_v2())
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(file_path, id_field="id")
        result_v2 = indexed_get_by_id(file_path, "2", id_field="id", index=index)
        assert result_v2 == new_record
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_14_2_2_async_update():
    """
    Full Test Name: test_14_2_2_async_update
    Test: Non-blocking update
    """
    test_data = [{"id": "1", "name": "Alice", "age": 30}]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Async update
        v1_start = time.perf_counter()
        async def async_update_v1():
            await async_stream_update(
                file_path,
                match_by_id("id", "1"),
                lambda obj: {**obj, "age": 31}
            )
        
        asyncio.run(async_update_v1())
        v1_time = time.perf_counter() - v1_start
        
        result = stream_read(file_path, match_by_id("id", "1"))
        assert result["age"] == 31
        
        # V2: Async update
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        
        v2_start = time.perf_counter()
        async def async_update_v2():
            await async_stream_update(
                file_path,
                match_by_id("id", "1"),
                lambda obj: {**obj, "age": 31}
            )
            await asyncio.to_thread(build_index, file_path, id_field="id")
        
        asyncio.run(async_update_v2())
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(file_path, id_field="id")
        result_v2 = indexed_get_by_id(file_path, "1", id_field="id", index=index)
        assert result_v2["age"] == 31
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_14_2_3_async_delete():
    """
    Full Test Name: test_14_2_3_async_delete
    Test: Non-blocking delete
    """
    test_data = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"}
    ]
    file_path = create_test_file(test_data)
    
    try:
        # V1: Async delete
        from test_helpers import delete_record_by_id_v1
        v1_start = time.perf_counter()
        async def async_delete_v1():
            await asyncio.to_thread(delete_record_by_id_v1, file_path, "2", "id")
        
        asyncio.run(async_delete_v1())
        v1_time = time.perf_counter() - v1_start
        
        records = get_all_matching_v1(file_path, lambda x: True)
        assert len(records) == 1
        assert records[0]["id"] == "1"
        
        # V2: Async delete
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        
        from test_helpers import delete_record_by_id_v2
        v2_start = time.perf_counter()
        async def async_delete_v2():
            await asyncio.to_thread(delete_record_by_id_v2, file_path, "2", "id")
        
        asyncio.run(async_delete_v2())
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(records_v2) == 1
        assert records_v2[0]["id"] == "1"
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)


def test_14_2_4_async_bulk_write():
    """
    Full Test Name: test_14_2_4_async_bulk_write
    Test: Non-blocking bulk operations
    """
    test_data = [{"id": "1", "name": "Alice"}]
    file_path = create_test_file(test_data)
    
    try:
        new_records = [
            {"id": "2", "name": "Bob"},
            {"id": "3", "name": "Charlie"}
        ]
        
        # V1: Async bulk write
        from test_helpers import bulk_append_v1
        v1_start = time.perf_counter()
        async def async_bulk_write_v1():
            await asyncio.to_thread(bulk_append_v1, file_path, new_records)
        
        asyncio.run(async_bulk_write_v1())
        v1_time = time.perf_counter() - v1_start
        
        records = get_all_matching_v1(file_path, lambda x: True)
        assert len(records) == 3
        
        # V2: Async bulk write
        cleanup_test_file(file_path)
        file_path = create_test_file(test_data)
        build_index(file_path, id_field="id")
        
        from test_helpers import bulk_append_v2
        v2_start = time.perf_counter()
        async def async_bulk_write_v2():
            await asyncio.to_thread(bulk_append_v2, file_path, new_records)
        
        asyncio.run(async_bulk_write_v2())
        v2_time = time.perf_counter() - v2_start
        
        index = ensure_index(file_path, id_field="id")
        records_v2 = get_all_matching_v2(file_path, lambda x: True, index=index)
        assert len(records_v2) == 3
        
        return True, v1_time, v2_time
    finally:
        cleanup_test_file(file_path)

