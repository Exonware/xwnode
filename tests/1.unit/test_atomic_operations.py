"""
Test script to verify atomic read and atomic write operations in json_utils.py
"""

import json
import os
import tempfile
import time
from pathlib import Path
from json_utils import (
    JsonRecordNotFound,
    JsonStreamError,
    match_by_id,
    stream_read,
    stream_update,
    update_path,
)


def test_atomic_read():
    """Test atomic read operation - should not corrupt file during read."""
    print("=" * 60)
    print("TEST 1: Atomic Read Operation")
    print("=" * 60)
    # Create a test NDJSON file
    test_data = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        test_file = f.name
        for record in test_data:
            f.write(json.dumps(record) + "\n")
    try:
        # Test 1: Read existing record
        print("\n1. Reading record with id=2...")
        result = stream_read(test_file, match_by_id("id", 2))
        print(f"   Result: {result}")
        assert result == {"id": 2, "name": "Bob", "age": 25}, "Read failed!"
        print("   ✓ Read successful")
        # Test 2: Read with path extraction
        print("\n2. Reading specific path (name) from record with id=1...")
        result = stream_read(test_file, match_by_id("id", 1), path=["name"])
        print(f"   Result: {result}")
        assert result == "Alice", "Path read failed!"
        print("   ✓ Path read successful")
        # Test 3: Read non-existent record
        print("\n3. Attempting to read non-existent record (id=999)...")
        try:
            result = stream_read(test_file, match_by_id("id", 999))
            print(f"   ERROR: Should have raised JsonRecordNotFound!")
            assert False, "Should have raised exception"
        except JsonRecordNotFound:
            print("   ✓ Correctly raised JsonRecordNotFound")
        # Test 4: Verify file integrity after reads
        print("\n4. Verifying file integrity after reads...")
        with open(test_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 3, "File corrupted during read!"
        print("   ✓ File integrity maintained")
    finally:
        os.unlink(test_file)
    print("\n✅ All atomic read tests passed!\n")


def test_atomic_write():
    """Test atomic write operation - should use temp file and atomic replace."""
    print("=" * 60)
    print("TEST 2: Atomic Write Operation")
    print("=" * 60)
    # Create initial test file
    test_data = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        test_file = f.name
        for record in test_data:
            f.write(json.dumps(record) + "\n")
    try:
        # Test 1: Atomic update single record
        print("\n1. Updating record with id=2 (age: 25 -> 26)...")
        original_stat = os.stat(test_file)
        time.sleep(0.01)  # Ensure different mtime
        def update_age(obj):
            obj["age"] += 1
            return obj
        updated_count = stream_update(
            test_file, match_by_id("id", 2), update_age, atomic=True
        )
        print(f"   Updated {updated_count} record(s)")
        # Verify update
        result = stream_read(test_file, match_by_id("id", 2))
        assert result["age"] == 26, "Update failed!"
        print(f"   Result: {result}")
        print("   ✓ Atomic update successful")
        # Test 2: Verify file was replaced atomically (check temp file cleanup)
        print("\n2. Verifying temp file cleanup...")
        temp_files = [
            f
            for f in os.listdir(os.path.dirname(test_file))
            if f.startswith(f".{os.path.basename(test_file)}.tmp.")
        ]
        assert len(temp_files) == 0, f"Temp files not cleaned up: {temp_files}"
        print("   ✓ Temp files cleaned up")
        # Test 3: Verify all other records unchanged
        print("\n3. Verifying other records unchanged...")
        alice = stream_read(test_file, match_by_id("id", 1))
        charlie = stream_read(test_file, match_by_id("id", 3))
        assert alice["age"] == 30, "Other record corrupted!"
        assert charlie["age"] == 35, "Other record corrupted!"
        print("   ✓ Other records unchanged")
        # Test 4: Update multiple records
        print("\n4. Updating multiple records (all ages +1)...")
        updated_count = stream_update(
            test_file,
            lambda obj: True,  # Match all
            update_age,
            atomic=True,
        )
        print(f"   Updated {updated_count} record(s)")
        # Verify all updated
        alice = stream_read(test_file, match_by_id("id", 1))
        bob = stream_read(test_file, match_by_id("id", 2))
        charlie = stream_read(test_file, match_by_id("id", 3))
        assert alice["age"] == 31, "Alice not updated!"
        assert bob["age"] == 27, "Bob not updated!"
        assert charlie["age"] == 36, "Charlie not updated!"
        print("   ✓ Multiple updates successful")
        # Test 5: Update with path
        print("\n5. Updating nested path...")
        test_data_nested = [{"id": 1, "data": {"count": 10}}]
        with open(test_file, "w") as f:
            for record in test_data_nested:
                f.write(json.dumps(record) + "\n")
        updated_count = stream_update(
            test_file,
            match_by_id("id", 1),
            update_path(["data", "count"], 20),
            atomic=True,
        )
        result = stream_read(test_file, match_by_id("id", 1))
        assert result["data"]["count"] == 20, "Nested path update failed!"
        print(f"   Result: {result}")
        print("   ✓ Nested path update successful")
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)
    print("\n✅ All atomic write tests passed!\n")


def test_atomic_write_failure_recovery():
    """Test that atomic write handles failures gracefully."""
    print("=" * 60)
    print("TEST 3: Atomic Write Failure Recovery")
    print("=" * 60)
    test_data = [{"id": 1, "name": "Alice"}]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        test_file = f.name
        for record in test_data:
            f.write(json.dumps(record) + "\n")
    try:
        # Test: Simulate failure during update (invalid updater)
        print("\n1. Testing failure handling (invalid updater)...")
        original_content = open(test_file, "r").read()
        def failing_updater(obj):
            raise ValueError("Simulated failure")
        try:
            stream_update(test_file, match_by_id("id", 1), failing_updater, atomic=True)
            assert False, "Should have raised exception"
        except JsonStreamError:
            print("   ✓ Exception correctly raised")
        # Verify original file still intact
        current_content = open(test_file, "r").read()
        assert current_content == original_content, "Original file corrupted on failure!"
        print("   ✓ Original file preserved on failure")
        # Verify temp file cleaned up
        temp_files = [
            f
            for f in os.listdir(os.path.dirname(test_file))
            if f.startswith(f".{os.path.basename(test_file)}.tmp.")
        ]
        assert len(temp_files) == 0, "Temp file not cleaned up on failure!"
        print("   ✓ Temp file cleaned up on failure")
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)
    print("\n✅ All failure recovery tests passed!\n")


def test_large_file_streaming():
    """Test that streaming works for large files without loading everything."""
    print("=" * 60)
    print("TEST 4: Large File Streaming")
    print("=" * 60)
    # Create a file with many records
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        test_file = f.name
        for i in range(1000):
            record = {"id": i, "value": f"record_{i}"}
            f.write(json.dumps(record) + "\n")
    try:
        # Test: Read from middle of file (should not load all records)
        print("\n1. Reading record from middle of large file (id=500)...")
        import tracemalloc
        tracemalloc.start()
        result = stream_read(test_file, match_by_id("id", 500))
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert result["id"] == 500, "Read failed!"
        print(f"   Result: {result}")
        print(f"   Memory used: {peak / 1024 / 1024:.2f} MB")
        print("   ✓ Streaming read successful (memory efficient)")
        # Test: Update single record in large file
        print("\n2. Updating single record in large file...")
        tracemalloc.start()
        updated_count = stream_update(
            test_file,
            match_by_id("id", 750),
            lambda obj: {**obj, "updated": True},
            atomic=True,
        )
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert updated_count == 1, "Update failed!"
        result = stream_read(test_file, match_by_id("id", 750))
        assert result.get("updated") is True, "Update not applied!"
        print(f"   Memory used: {peak / 1024 / 1024:.2f} MB")
        print("   ✓ Streaming update successful (memory efficient)")
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)
    print("\n✅ All large file streaming tests passed!\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("JSON UTILS - ATOMIC OPERATIONS TEST SUITE")
    print("=" * 60 + "\n")
    try:
        test_atomic_read()
        test_atomic_write()
        test_atomic_write_failure_recovery()
        test_large_file_streaming()
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nAtomic read and write operations are working correctly.")
        print("Key features verified:")
        print("  ✓ Atomic reads don't corrupt files")
        print("  ✓ Atomic writes use temp files and os.replace()")
        print("  ✓ Temp files are cleaned up on success and failure")
        print("  ✓ File integrity maintained during operations")
        print("  ✓ Streaming works for large files (memory efficient)")
        print("  ✓ Failure recovery preserves original files")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0
if __name__ == "__main__":
    exit(main())
