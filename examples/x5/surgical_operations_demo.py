#!/usr/bin/env python3
"""
Demonstrate surgical read and write operations on a 1GB NDJSON file.
Shows timing and memory usage for each operation.
"""

import os
import sys
import time
import tracemalloc
from pathlib import Path
# Import json_utils
sys.path.insert(0, str(Path(__file__).parent))
from json_utils import (
    stream_read,
    stream_update,
    match_by_id,
    update_path,
    JsonRecordNotFound,
)


def format_bytes(bytes_val):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"


def format_time(seconds):
    """Format time to human-readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.2f}s"


def measure_operation(operation_name, operation_func):
    """Measure time and memory for an operation"""
    print(f"\n{'='*70}")
    print(f"OPERATION: {operation_name}")
    print(f"{'='*70}")
    # Start memory tracking
    tracemalloc.start()
    start_time = time.perf_counter()
    try:
        result = operation_func()
        # Measure
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        elapsed = end_time - start_time
        print(f"\n✓ Operation completed successfully")
        print(f"  Time: {format_time(elapsed)}")
        print(f"  Memory (current): {format_bytes(current)}")
        print(f"  Memory (peak): {format_bytes(peak)}")
        if result is not None:
            print(f"  Result: {result}")
        return {
            'success': True,
            'time': elapsed,
            'memory_current': current,
            'memory_peak': peak,
            'result': result
        }
    except Exception as e:
        tracemalloc.stop()
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"\n✗ Operation failed")
        print(f"  Time: {format_time(elapsed)}")
        print(f"  Error: {e}")
        return {
            'success': False,
            'time': elapsed,
            'error': str(e)
        }


def demo_surgical_read(file_path: str):
    """Demonstrate surgical read operations"""
    print("\n" + "="*70)
    print("SURGICAL READ OPERATIONS")
    print("="*70)
    results = []
    # Read 1: Find first user
    def read_first_user():
        # Read first record that looks like a user
        def is_user(obj):
            return "username" in obj and "email" in obj
        return stream_read(file_path, is_user, path=None)
    result1 = measure_operation(
        "Read first user record (full object)",
        read_first_user
    )
    results.append(("Read user (full)", result1))
    # Read 2: Extract specific field from user
    def read_user_email():
        def is_user(obj):
            return "username" in obj and "email" in obj
        return stream_read(file_path, is_user, path=["email"])
    result2 = measure_operation(
        "Read user email field (surgical path extraction)",
        read_user_email
    )
    results.append(("Read user email", result2))
    # Read 3: Find a post by ID
    def read_post():
        def is_post(obj):
            return "post_type" in obj and "content" in obj
        return stream_read(file_path, is_post, path=None)
    result3 = measure_operation(
        "Read first post record (full object)",
        read_post
    )
    results.append(("Read post (full)", result3))
    # Read 4: Extract post content only
    def read_post_content():
        def is_post(obj):
            return "post_type" in obj and "content" in obj
        return stream_read(file_path, is_post, path=["content"])
    result4 = measure_operation(
        "Read post content field only (surgical extraction)",
        read_post_content
    )
    results.append(("Read post content", result4))
    # Read 5: Extract nested field
    def read_post_hashtags():
        def is_post(obj):
            return "post_type" in obj and "hashtags" in obj
        return stream_read(file_path, is_post, path=["hashtags"])
    result5 = measure_operation(
        "Read post hashtags array (nested field)",
        read_post_hashtags
    )
    results.append(("Read post hashtags", result5))
    return results


def demo_surgical_write(file_path: str):
    """Demonstrate surgical write operations"""
    print("\n" + "="*70)
    print("SURGICAL WRITE OPERATIONS")
    print("="*70)
    results = []
    # Write 1: Update a single field in first user
    def update_user_email():
        class State:
            updated = False
        def is_user(obj):
            return not State.updated and "username" in obj and "email" in obj
        def update_email(obj):
            if "email" in obj:
                obj["email"] = "updated@example.com"
                State.updated = True
            return obj
        return stream_update(file_path, is_user, update_email, atomic=True)
    result1 = measure_operation(
        "Update user email field (atomic write)",
        update_user_email
    )
    results.append(("Update user email", result1))
    # Write 2: Update nested field (only first post)
    def update_post_likes():
        class State:
            updated = False
        def is_post(obj):
            return not State.updated and "post_type" in obj and "likes_count" in obj
        def increment_likes(obj):
            if "likes_count" in obj:
                obj["likes_count"] = obj.get("likes_count", 0) + 1
                State.updated = True
            return obj
        return stream_update(file_path, is_post, increment_likes, atomic=True)
    result2 = measure_operation(
        "Update post likes_count (atomic write)",
        update_post_likes
    )
    results.append(("Update post likes", result2))
    # Write 3: Update using path updater (only first post)
    def update_post_content_path():
        class State:
            updated = False
        def is_post(obj):
            return not State.updated and "post_type" in obj and "content" in obj
        def updater_func(obj):
            updater = update_path(["content"], "Updated content via surgical path operation!")
            result = updater(obj)
            State.updated = True
            return result
        return stream_update(file_path, is_post, updater_func, atomic=True)
    result3 = measure_operation(
        "Update post content using path updater (atomic write)",
        update_post_content_path
    )
    results.append(("Update post content (path)", result3))
    # Write 4: Update nested array element (only first post)
    def update_post_hashtag():
        class State:
            updated = False
        def is_post(obj):
            return not State.updated and "post_type" in obj and "hashtags" in obj
        def add_hashtag(obj):
            if "hashtags" in obj and isinstance(obj["hashtags"], list):
                if "#surgical" not in obj["hashtags"]:
                    obj["hashtags"].append("#surgical")
                    State.updated = True
            return obj
        return stream_update(file_path, is_post, add_hashtag, atomic=True)
    result4 = measure_operation(
        "Add hashtag to post (update nested array)",
        update_post_hashtag
    )
    results.append(("Update post hashtags", result4))
    return results


def print_summary(read_results, write_results):
    """Print summary of all operations"""
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\n📖 READ OPERATIONS:")
    print("-" * 70)
    for name, result in read_results:
        if result.get('success'):
            print(f"  {name:30} | Time: {format_time(result['time']):>12} | "
                  f"Memory: {format_bytes(result['memory_peak']):>10}")
        else:
            print(f"  {name:30} | FAILED: {result.get('error', 'Unknown error')}")
    print("\n✏️  WRITE OPERATIONS:")
    print("-" * 70)
    for name, result in write_results:
        if result.get('success'):
            print(f"  {name:30} | Time: {format_time(result['time']):>12} | "
                  f"Memory: {format_bytes(result['memory_peak']):>10} | "
                  f"Updated: {result.get('result', 'N/A')} records")
        else:
            print(f"  {name:30} | FAILED: {result.get('error', 'Unknown error')}")
    # Calculate totals
    total_read_time = sum(r['time'] for _, r in read_results if r.get('success'))
    total_write_time = sum(r['time'] for _, r in write_results if r.get('success'))
    max_read_memory = max((r['memory_peak'] for _, r in read_results if r.get('success')), default=0)
    max_write_memory = max((r['memory_peak'] for _, r in write_results if r.get('success')), default=0)
    print("\n📊 TOTALS:")
    print("-" * 70)
    print(f"  Total read time:  {format_time(total_read_time)}")
    print(f"  Total write time: {format_time(total_write_time)}")
    print(f"  Max read memory:  {format_bytes(max_read_memory)}")
    print(f"  Max write memory: {format_bytes(max_write_memory)}")
    print(f"  Total operations: {len(read_results) + len(write_results)}")


def main():
    """Main demo function"""
    # Check if file exists
    data_dir = Path(__file__).parent / "data"
    file_path = data_dir / "database_1gb.jsonl"
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        print("Please run generate_1gb_file.py first to create the test file.")
        return 1
    file_size = file_path.stat().st_size
    print("="*70)
    print("SURGICAL READ/WRITE OPERATIONS DEMO")
    print("="*70)
    print(f"\nFile: {file_path}")
    print(f"Size: {file_size / (1024**3):.2f} GB ({file_size:,} bytes)")
    print(f"\nThis demo shows surgical operations that only load/update")
    print(f"specific records without loading the entire 1GB file into memory.")
    # Run read operations
    read_results = demo_surgical_read(str(file_path))
    # Run write operations
    write_results = demo_surgical_write(str(file_path))
    # Print summary
    print_summary(read_results, write_results)
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    print("\nKey observations:")
    print("  • Surgical reads only load one record at a time")
    print("  • Memory usage stays low even for 1GB files")
    print("  • Atomic writes use temp files and os.replace()")
    print("  • Operations are fast and memory-efficient")
    return 0
if __name__ == "__main__":
    exit(main())
