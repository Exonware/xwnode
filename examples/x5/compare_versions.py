#!/usr/bin/env python3
"""
Compare Version 1 (streaming) vs Version 2 (indexed) JSON Utils
Tests performance differences for:
- First access (no index) vs subsequent accesses (with index)
- Random access by line number
- Random access by ID
- Paging operations
"""
# ============================================================================
# TEST CONFIGURATION - Main Controller
# ============================================================================
# Modify this list to control the number of operations per test run
# Each value will run all comparison tests with that many operations

OPERATION_COUNTS = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
# ============================================================================
import sys
import os
import json
import time
import tracemalloc
import random
import signal
from pathlib import Path
from contextlib import contextmanager
# Import both versions
sys.path.insert(0, str(Path(__file__).parent))
from json_utils import stream_read, match_by_id
from json_utils_indexed import (
    build_index,
    ensure_index,
    indexed_get_by_line,
    indexed_get_by_id,
    get_page,
    load_index,
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
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.2f}s"


def get_or_create_id_list(file_path: str, id_field: str = "id", max_ids: int = 20000):
    """
    Extract all IDs from the NDJSON file and save to a cache file.
    Returns list of IDs (up to max_ids).
    Args:
        file_path: Path to NDJSON file
        id_field: Field name containing the ID
        max_ids: Maximum number of IDs to extract
    Returns:
        List of ID strings
    """
    cache_file = file_path + ".ids.json"
    # Check if cache exists
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # Verify it's for the same file
                if cached_data.get('file_path') == os.path.abspath(file_path):
                    ids = cached_data.get('ids', [])
                    print(f"  ✓ Loaded {len(ids):,} IDs from cache: {cache_file}")
                    return ids[:max_ids] if max_ids else ids
        except Exception as e:
            print(f"  ⚠️  Error loading ID cache: {e}, regenerating...")
    # Extract IDs from file
    print(f"  Extracting IDs from file (this may take a while)...")
    ids = []
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    id_value = obj.get(id_field)
                    if id_value is not None:
                        ids.append(str(id_value))
                        count += 1
                        if count >= max_ids:
                            break
                    if line_no % 10000 == 0:
                        print(f"    Processed {line_no:,} lines, found {len(ids):,} IDs...", end='\r')
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"  ❌ Error extracting IDs: {e}")
        return []
    print(f"  ✓ Extracted {len(ids):,} IDs")
    # Save to cache
    try:
        cache_data = {
            'file_path': os.path.abspath(file_path),
            'id_field': id_field,
            'ids': ids
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
        print(f"  ✓ Saved ID cache to: {cache_file}")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not save ID cache: {e}")
    return ids[:max_ids] if max_ids else ids
@contextmanager


def timeout_context(seconds):
    """Context manager for timeout protection"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    # Set up signal handler for timeout (Unix only)
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows doesn't support SIGALRM, use a simpler approach
        yield


def measure_operation(name, operation_func, warmup=False, max_time=300):
    """
    Measure time and memory for an operation with timeout protection.
    Args:
        name: Name of the operation
        operation_func: Function to execute
        warmup: Whether to do a warmup run
        max_time: Maximum time in seconds before timing out (default 5 minutes)
    """
    if warmup:
        # Warmup run (not measured)
        try:
            operation_func()
        except:
            pass
    tracemalloc.start()
    start_time = time.perf_counter()
    try:
        # Check for timeout periodically (for Windows compatibility)
        result = None
        error_occurred = False
        error_message = None
        def run_with_timeout_check():
            nonlocal result, error_occurred, error_message
            try:
                result = operation_func()
            except Exception as e:
                error_occurred = True
                error_message = str(e)
                raise
        # Run the operation
        run_with_timeout_check()
        # Check if we exceeded max time
        elapsed = time.perf_counter() - start_time
        if elapsed > max_time:
            tracemalloc.stop()
            return {
                'success': False,
                'time': elapsed,
                'error': f'Operation exceeded maximum time limit of {max_time}s (took {elapsed:.2f}s)'
            }
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        elapsed = end_time - start_time
        return {
            'success': True,
            'time': elapsed,
            'memory_current': current,
            'memory_peak': peak,
            'result': result
        }
    except TimeoutError as e:
        tracemalloc.stop()
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        return {
            'success': False,
            'time': elapsed,
            'error': str(e)
        }
    except Exception as e:
        tracemalloc.stop()
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        return {
            'success': False,
            'time': elapsed,
            'error': str(e)
        }


def compare_first_access(file_path: str, skip_cold_if_indexed: bool = True, num_ops: int = 100):
    """Compare first access - V1 (stream) vs V2 (build index + access)"""
    print("\n" + "="*70)
    print(f"COMPARISON 1: First Access (Cold Start) - {num_ops} Operations")
    print("="*70)
    # Get IDs to use for testing
    print("\n📋 Loading test IDs...")
    all_ids = get_or_create_id_list(file_path, id_field="id", max_ids=20000)
    if len(all_ids) < num_ops:
        print(f"  ⚠️  Warning: Only {len(all_ids)} IDs available, using all of them")
        test_ids = all_ids
        num_ops = len(test_ids)
    else:
        test_ids = all_ids[:num_ops]
    print(f"  Using {len(test_ids)} IDs for testing")
    # Check if index exists
    idx_path = file_path + ".idx.json"
    has_index = os.path.exists(idx_path)
    if skip_cold_if_indexed and has_index:
        print("\n  ⚠️  Index already exists. Skipping cold start test.")
        print("  💡 Delete the index file to test cold start performance.")
        print(f"  💡 Index file: {idx_path}")
        v2_cold_result = None
    # V1: Stream read by ID (using test_ids)
    def v1_read_multiple():
        results = []
        for test_id in test_ids:
            try:
                result = stream_read(file_path, match_by_id("id", test_id), path=None)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 1: Build index + read by ID (cold start)
    # Note: Index will be built if it doesn't exist, otherwise uses existing index
    def v2_cold_start():
        # Check if index exists
        idx_path = file_path + ".idx.json"
        index_exists = os.path.exists(idx_path)
        if index_exists:
            print("    Using existing index (index persists across runs)")
            index = ensure_index(file_path, id_field="id", max_id_index=10000)
        else:
            # Add progress callback
            def progress_callback(line_no, estimated):
                if line_no % 50000 == 0:
                    percent = (line_no / estimated * 100) if estimated > 0 else 0
                    print(f"    Indexing progress: {line_no:,} lines ({percent:.1f}%)", end='\r')
            print("    Building index (this may take a while for large files)...")
            index = build_index(file_path, id_field="id", max_id_index=10000, progress_callback=progress_callback)
            print(f"    ✓ Index built: {len(index.line_offsets):,} records (index saved for future use)")
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 2: Use cached index (warm start)
    def v2_warm_start():
        index = ensure_index(file_path, id_field="id", max_id_index=10000)
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    print(f"\n📖 V1 (Streaming): Read first user {num_ops} times")
    v1_result = measure_operation("V1 Stream Read", v1_read_multiple)
    if v1_result['success']:
        avg_time = v1_result['time'] / num_ops
        print(f"  Total time: {format_time(v1_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v1_result['memory_peak'])}")
        print(f"  Success: {len(v1_result['result']) if isinstance(v1_result['result'], list) else 0}/{num_ops}")
    else:
        print(f"  ❌ FAILED: {v1_result.get('error', 'Unknown error')}")
    if not (skip_cold_if_indexed and has_index):
        print(f"\n📖 V2 (Indexed) - RUN 1 (Cold): Build index + read {num_ops} times")
        v2_cold_result = measure_operation("V2 Cold Start", v2_cold_start)
        if v2_cold_result and v2_cold_result['success']:
            avg_time = v2_cold_result['time'] / num_ops
            print(f"  Total time: {format_time(v2_cold_result['time'])}")
            print(f"  Avg per op: {format_time(avg_time)}")
            print(f"  Memory: {format_bytes(v2_cold_result['memory_peak'])}")
            print(f"  Success: {len(v2_cold_result['result']) if isinstance(v2_cold_result['result'], list) else 0}/{num_ops}")
    else:
        v2_cold_result = None
    print(f"\n📖 V2 (Indexed) - RUN 2 (Warm): Use cached index, read {num_ops} times")
    v2_warm_result = measure_operation("V2 Warm Start", v2_warm_start)
    if v2_warm_result['success']:
        avg_time = v2_warm_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_warm_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_warm_result['memory_peak'])}")
        print(f"  Success: {len(v2_warm_result['result']) if isinstance(v2_warm_result['result'], list) else 0}/{num_ops}")
    else:
        print(f"  ❌ FAILED: {v2_warm_result.get('error', 'Unknown error')}")
    if v1_result['success'] and v2_warm_result['success']:
        v1_avg = v1_result['time'] / num_ops
        v2_warm_avg = v2_warm_result['time'] / num_ops
        print(f"\n  📊 Average per operation:")
        print(f"     V1: {format_time(v1_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            print(f"     V2 Cold: {format_time(v2_cold_avg)}")
        print(f"     V2 Warm: {format_time(v2_warm_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            speedup_cold = v1_avg / v2_cold_avg if v2_cold_avg > 0 else float('inf')
            print(f"\n  ⚡ V2 Cold is {speedup_cold:.2f}x {'faster' if speedup_cold > 1 else 'slower'} than V1")
            print(f"  💡 V2 Warm is {v2_cold_avg / v2_warm_avg:.2f}x faster than V2 Cold (index caching benefit)")
        speedup_warm = v1_avg / v2_warm_avg if v2_warm_avg > 0 else float('inf')
        print(f"  ⚡ V2 Warm is {speedup_warm:.2f}x {'faster' if speedup_warm > 1 else 'slower'} than V1")


def compare_subsequent_access(file_path: str, skip_cold_if_indexed: bool = True, num_ops: int = 100):
    """Compare subsequent access - V1 (stream) vs V2 (use cached index)"""
    print("\n" + "="*70)
    print(f"COMPARISON 2: Random ID Access - {num_ops} Operations")
    print("="*70)
    # Get IDs to use for testing
    print("\n📋 Loading test IDs...")
    all_ids = get_or_create_id_list(file_path, id_field="id", max_ids=20000)
    if len(all_ids) < num_ops:
        print(f"  ⚠️  Warning: Only {len(all_ids)} IDs available, using all of them")
        test_ids = all_ids
        num_ops = len(test_ids)
    else:
        test_ids = all_ids[:num_ops]
    print(f"  Using {len(test_ids)} IDs for testing")
    # Check if index exists
    idx_path = file_path + ".idx.json"
    has_index = os.path.exists(idx_path)
    if skip_cold_if_indexed and has_index:
        print("\n  ⚠️  Index already exists. Skipping cold start test.")
        print("  💡 Delete the index file to test cold start performance.")
        v2_cold_result = None
    # V1: Stream read by ID (must scan from beginning each time)
    def v1_read_multiple():
        results = []
        for test_id in test_ids:
            try:
                result = stream_read(file_path, match_by_id("id", test_id), path=None)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 1: Cold start (build index if needed, index persists)
    def v2_cold_start():
        # Check if index exists - if it does, use it (index persists!)
        idx_path = file_path + ".idx.json"
        index_exists = os.path.exists(idx_path)
        if index_exists:
            print("    Using existing index (index persists across runs)")
            index = ensure_index(file_path, id_field="id", max_id_index=10000)
        else:
            # Add progress callback
            def progress_callback(line_no, estimated):
                if line_no % 50000 == 0:
                    percent = (line_no / estimated * 100) if estimated > 0 else 0
                    print(f"    Indexing progress: {line_no:,} lines ({percent:.1f}%)", end='\r')
            print("    Building index (this may take a while for large files)...")
            index = build_index(file_path, id_field="id", max_id_index=10000, progress_callback=progress_callback)
            print(f"    ✓ Index built: {len(index.line_offsets):,} records (index saved for future use)")
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 2: Warm start (use cached index)
    def v2_warm_start():
        index = ensure_index(file_path, id_field="id", max_id_index=10000)
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    print(f"\n📖 V1 (Streaming): Read {num_ops} records (each scans from start)")
    v1_result = measure_operation("V1 Stream Read", v1_read_multiple)
    if v1_result['success']:
        avg_time = v1_result['time'] / num_ops
        print(f"  Total time: {format_time(v1_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v1_result['memory_peak'])}")
        print(f"  Success: {len(v1_result['result']) if isinstance(v1_result['result'], list) else 0}/{num_ops}")
    else:
        print(f"  ❌ FAILED: {v1_result.get('error', 'Unknown error')}")
    print(f"\n📖 V2 (Indexed) - RUN 1 (Cold): Build index + {num_ops} random accesses")
    v2_cold_result = measure_operation("V2 Cold Start", v2_cold_start)
    if v2_cold_result and v2_cold_result['success']:
        avg_time = v2_cold_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_cold_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_cold_result['memory_peak'])}")
        print(f"  Success: {len(v2_cold_result['result']) if isinstance(v2_cold_result['result'], list) else 0}/{num_ops}")
    print(f"\n📖 V2 (Indexed) - RUN 2 (Warm): Use cached index, {num_ops} random accesses")
    v2_warm_result = measure_operation("V2 Warm Start", v2_warm_start)
    if v2_warm_result['success']:
        avg_time = v2_warm_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_warm_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_warm_result['memory_peak'])}")
        print(f"  Success: {len(v2_warm_result['result']) if isinstance(v2_warm_result['result'], list) else 0}/{num_ops}")
    if v1_result['success'] and v2_warm_result['success']:
        v1_avg = v1_result['time'] / num_ops
        v2_warm_avg = v2_warm_result['time'] / num_ops
        print(f"\n  📊 Average per operation:")
        print(f"     V1: {format_time(v1_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            print(f"     V2 Cold: {format_time(v2_cold_avg)}")
        print(f"     V2 Warm: {format_time(v2_warm_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            speedup_cold = v1_avg / v2_cold_avg if v2_cold_avg > 0 else float('inf')
            print(f"\n  ⚡ V2 Cold is {speedup_cold:.2f}x {'faster' if speedup_cold > 1 else 'slower'} than V1")
            print(f"  💡 V2 Warm is {v2_cold_avg / v2_warm_avg:.2f}x faster than V2 Cold (index caching benefit)")
        speedup_warm = v1_avg / v2_warm_avg if v2_warm_avg > 0 else float('inf')
        print(f"  ⚡ V2 Warm is {speedup_warm:.2f}x {'faster' if speedup_warm > 1 else 'slower'} than V1")


def compare_id_lookup(file_path: str, skip_cold_if_indexed: bool = True, num_ops: int = 100):
    """Compare ID-based lookup"""
    print("\n" + "="*70)
    print(f"COMPARISON 3: ID-Based Lookup - {num_ops} Operations")
    print("="*70)
    # Get IDs to use for testing
    print("\n📋 Loading test IDs...")
    all_ids = get_or_create_id_list(file_path, id_field="id", max_ids=20000)
    if len(all_ids) < num_ops:
        print(f"  ⚠️  Warning: Only {len(all_ids)} IDs available, using all of them")
        test_ids = all_ids
        num_ops = len(test_ids)
    else:
        test_ids = all_ids[:num_ops]
    print(f"  Using {len(test_ids)} IDs for testing")
    # Check if index exists
    idx_path = file_path + ".idx.json"
    has_index = os.path.exists(idx_path)
    if skip_cold_if_indexed and has_index:
        print("\n  ⚠️  Index already exists. Skipping cold start test.")
        print("  💡 Delete the index file to test cold start performance.")
        v2_cold_result = None
    print(f"\n🔍 Looking up {num_ops} different IDs")
    # V1: Stream read with match
    def v1_read_multiple():
        results = []
        for test_id in test_ids:
            try:
                result = stream_read(file_path, match_by_id("id", test_id), path=None)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 1: Cold start (build index if needed, index persists)
    def v2_cold_start():
        # Check if index exists - if it does, use it (index persists!)
        idx_path = file_path + ".idx.json"
        index_exists = os.path.exists(idx_path)
        if index_exists:
            print("    Using existing index (index persists across runs)")
            index = ensure_index(file_path, id_field="id", max_id_index=10000)
        else:
            # Add progress callback
            def progress_callback(line_no, estimated):
                if line_no % 50000 == 0:
                    percent = (line_no / estimated * 100) if estimated > 0 else 0
                    print(f"    Indexing progress: {line_no:,} lines ({percent:.1f}%)", end='\r')
            print("    Building index (this may take a while for large files)...")
            index = build_index(file_path, id_field="id", max_id_index=10000, progress_callback=progress_callback)
            print(f"    ✓ Index built: {len(index.line_offsets):,} records (index saved for future use)")
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 2: Warm start (use cached index)
    def v2_warm_start():
        index = ensure_index(file_path, id_field="id", max_id_index=10000)
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    print(f"\n📖 V1 (Streaming): Match by ID {num_ops} times (linear scan each)")
    v1_result = measure_operation("V1 ID Lookup", v1_read_multiple)
    if v1_result['success']:
        avg_time = v1_result['time'] / num_ops
        print(f"  Total time: {format_time(v1_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v1_result['memory_peak'])}")
        print(f"  Success: {len(v1_result['result']) if isinstance(v1_result['result'], list) else 0}/{num_ops}")
    else:
        print(f"  ❌ FAILED: {v1_result.get('error', 'Unknown error')}")
    if not (skip_cold_if_indexed and has_index):
        print(f"\n📖 V2 (Indexed) - RUN 1 (Cold): Build index + {num_ops} ID lookups")
        v2_cold_result = measure_operation("V2 Cold Start", v2_cold_start)
    else:
        v2_cold_result = None
    if v2_cold_result and v2_cold_result['success']:
        avg_time = v2_cold_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_cold_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_cold_result['memory_peak'])}")
        print(f"  Success: {len(v2_cold_result['result']) if isinstance(v2_cold_result['result'], list) else 0}/{num_ops}")
    print(f"\n📖 V2 (Indexed) - RUN 2 (Warm): Use cached index, {num_ops} ID lookups")
    v2_warm_result = measure_operation("V2 Warm Start", v2_warm_start)
    if v2_warm_result['success']:
        avg_time = v2_warm_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_warm_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_warm_result['memory_peak'])}")
        print(f"  Success: {len(v2_warm_result['result']) if isinstance(v2_warm_result['result'], list) else 0}/{num_ops}")
    if v1_result['success'] and v2_warm_result['success']:
        v1_avg = v1_result['time'] / num_ops
        v2_warm_avg = v2_warm_result['time'] / num_ops
        print(f"\n  📊 Average per operation:")
        print(f"     V1: {format_time(v1_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            print(f"     V2 Cold: {format_time(v2_cold_avg)}")
        print(f"     V2 Warm: {format_time(v2_warm_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            speedup_cold = v1_avg / v2_cold_avg if v2_cold_avg > 0 else float('inf')
            print(f"\n  ⚡ V2 Cold is {speedup_cold:.2f}x {'faster' if speedup_cold > 1 else 'slower'} than V1")
            print(f"  💡 V2 Warm is {v2_cold_avg / v2_warm_avg:.2f}x faster than V2 Cold (index caching benefit)")
        speedup_warm = v1_avg / v2_warm_avg if v2_warm_avg > 0 else float('inf')
        print(f"  ⚡ V2 Warm is {speedup_warm:.2f}x {'faster' if speedup_warm > 1 else 'slower'} than V1")


def compare_paging(file_path: str, skip_cold_if_indexed: bool = True, num_ops: int = 100):
    """Compare paging operations"""
    print("\n" + "="*70)
    print(f"COMPARISON 4: Paging (Get Multiple Records) - {num_ops} Operations")
    print("="*70)
    # Check if index exists
    idx_path = file_path + ".idx.json"
    has_index = os.path.exists(idx_path)
    if skip_cold_if_indexed and has_index:
        print("\n  ⚠️  Index already exists. Skipping cold start test.")
        print("  💡 Delete the index file to test cold start performance.")
        v2_cold_result = None
    page_size = 10  # Smaller pages for 100 operations
    # V1: Stream read multiple records (must scan sequentially)
    # Note: V1 doesn't support true paging efficiently, so we'll simulate it by reading sequentially
    def v1_read_pages():
        all_results = []
        max_iterations = page_size * 100  # Safety limit to prevent infinite loops
        for op in range(num_ops):
            results = []
            seen_ids = set()  # Track IDs we've already seen to avoid duplicates
            iteration_count = 0
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, start=1):
                        if iteration_count >= max_iterations:
                            print(f"    ⚠️  V1 paging: Reached max iterations ({max_iterations}) for operation {op+1}")
                            break
                        if not line.strip():
                            continue
                        try:
                            obj = json.loads(line)
                            # Check if it's a user record
                            if "username" in obj and "email" in obj:
                                # Use ID to avoid duplicates
                                record_id = obj.get("id")
                                if record_id is None or str(record_id) not in seen_ids:
                                    results.append(obj)
                                    if record_id is not None:
                                        seen_ids.add(str(record_id))
                                    if len(results) >= page_size:
                                        break
                        except json.JSONDecodeError:
                            continue
                        iteration_count += 1
            except Exception as e:
                print(f"    ⚠️  V1 paging error in operation {op+1}: {e}")
                pass
            all_results.append(results)
        return all_results
    # V2 Run 1: Cold start (build index if needed, index persists)
    def v2_cold_start():
        # Check if index exists - if it does, use it (index persists!)
        idx_path = file_path + ".idx.json"
        index_exists = os.path.exists(idx_path)
        if index_exists:
            print("    Using existing index (index persists across runs)")
            index = ensure_index(file_path, id_field="id", max_id_index=10000)
        else:
            # Add progress callback
            def progress_callback(line_no, estimated):
                if line_no % 50000 == 0:
                    percent = (line_no / estimated * 100) if estimated > 0 else 0
                    print(f"    Indexing progress: {line_no:,} lines ({percent:.1f}%)", end='\r')
            print("    Building index (this may take a while for large files)...")
            index = build_index(file_path, id_field="id", max_id_index=10000, progress_callback=progress_callback)
            print(f"    ✓ Index built: {len(index.line_offsets):,} records (index saved for future use)")
        all_results = []
        for page_num in range(1, num_ops + 1):
            try:
                results = get_page(file_path, page_num, page_size, index=index)
                all_results.append(results)
            except:
                pass
        return all_results
    # V2 Run 2: Warm start (use cached index)
    def v2_warm_start():
        index = ensure_index(file_path, id_field="id", max_id_index=10000)
        all_results = []
        for page_num in range(1, num_ops + 1):
            try:
                results = get_page(file_path, page_num, page_size, index=index)
                all_results.append(results)
            except:
                pass
        return all_results
    print(f"\n📖 V1 (Streaming): Get {page_size} records, {num_ops} times (sequential scan)")
    v1_result = measure_operation("V1 Paging", v1_read_pages)
    if v1_result['success']:
        total_records = sum(len(r) if isinstance(r, list) else 0 for r in v1_result['result']) if isinstance(v1_result['result'], list) else 0
        avg_time = v1_result['time'] / num_ops
        print(f"  Total time: {format_time(v1_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v1_result['memory_peak'])}")
        print(f"  Total records: {total_records}")
    else:
        print(f"  ❌ FAILED: {v1_result.get('error', 'Unknown error')}")
    if not (skip_cold_if_indexed and has_index):
        print(f"\n📖 V2 (Indexed) - RUN 1 (Cold): Build index + {num_ops} pages")
        v2_cold_result = measure_operation("V2 Cold Start", v2_cold_start)
    else:
        v2_cold_result = None
    if v2_cold_result and v2_cold_result['success']:
        total_records = sum(len(r) if isinstance(r, list) else 0 for r in v2_cold_result['result']) if isinstance(v2_cold_result['result'], list) else 0
        avg_time = v2_cold_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_cold_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_cold_result['memory_peak'])}")
        print(f"  Total records: {total_records}")
    print(f"\n📖 V2 (Indexed) - RUN 2 (Warm): Use cached index, {num_ops} pages")
    v2_warm_result = measure_operation("V2 Warm Start", v2_warm_start)
    if v2_warm_result['success']:
        total_records = sum(len(r) if isinstance(r, list) else 0 for r in v2_warm_result['result']) if isinstance(v2_warm_result['result'], list) else 0
        avg_time = v2_warm_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_warm_result['time'])}")
        print(f"  Avg per op: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_warm_result['memory_peak'])}")
        print(f"  Total records: {total_records}")
    if v1_result['success'] and v2_warm_result['success']:
        v1_avg = v1_result['time'] / num_ops
        v2_warm_avg = v2_warm_result['time'] / num_ops
        print(f"\n  📊 Average per operation:")
        print(f"     V1: {format_time(v1_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            print(f"     V2 Cold: {format_time(v2_cold_avg)}")
        print(f"     V2 Warm: {format_time(v2_warm_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            speedup_cold = v1_avg / v2_cold_avg if v2_cold_avg > 0 else float('inf')
            print(f"\n  ⚡ V2 Cold is {speedup_cold:.2f}x {'faster' if speedup_cold > 1 else 'slower'} than V1")
            print(f"  💡 V2 Warm is {v2_cold_avg / v2_warm_avg:.2f}x faster than V2 Cold (index caching benefit)")
        speedup_warm = v1_avg / v2_warm_avg if v2_warm_avg > 0 else float('inf')
        print(f"  ⚡ V2 Warm is {speedup_warm:.2f}x {'faster' if speedup_warm > 1 else 'slower'} than V1")


def compare_multiple_random_access(file_path: str, skip_cold_if_indexed: bool = True, num_ops: int = 100):
    """Compare multiple random accesses"""
    print("\n" + "="*70)
    print(f"COMPARISON 5: Multiple Random Accesses - {num_ops} Operations")
    print("="*70)
    # Get IDs to use for testing
    print("\n📋 Loading test IDs...")
    all_ids = get_or_create_id_list(file_path, id_field="id", max_ids=20000)
    if len(all_ids) < num_ops:
        print(f"  ⚠️  Warning: Only {len(all_ids)} IDs available, using all of them")
        test_ids = all_ids
        num_ops = len(test_ids)
    else:
        test_ids = all_ids[:num_ops]
    print(f"  Using {len(test_ids)} IDs for testing")
    # Check if index exists
    idx_path = file_path + ".idx.json"
    has_index = os.path.exists(idx_path)
    if skip_cold_if_indexed and has_index:
        print("\n  ⚠️  Index already exists. Skipping cold start test.")
        print("  💡 Delete the index file to test cold start performance.")
        v2_cold_result = None
    print(f"\n🔄 Accessing {num_ops} random records by ID")
    # V1: Each access scans from start
    def v1_multiple():
        results = []
        for test_id in test_ids:
            try:
                result = stream_read(file_path, match_by_id("id", test_id), path=None)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 1: Cold start (build index if needed, index persists)
    def v2_cold_start():
        # Check if index exists - if it does, use it (index persists!)
        idx_path = file_path + ".idx.json"
        index_exists = os.path.exists(idx_path)
        if index_exists:
            print("    Using existing index (index persists across runs)")
            index = ensure_index(file_path, id_field="id", max_id_index=10000)
        else:
            # Add progress callback
            def progress_callback(line_no, estimated):
                if line_no % 50000 == 0:
                    percent = (line_no / estimated * 100) if estimated > 0 else 0
                    print(f"    Indexing progress: {line_no:,} lines ({percent:.1f}%)", end='\r')
            print("    Building index (this may take a while for large files)...")
            index = build_index(file_path, id_field="id", max_id_index=10000, progress_callback=progress_callback)
            print(f"    ✓ Index built: {len(index.line_offsets):,} records (index saved for future use)")
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    # V2 Run 2: Warm start (use cached index)
    def v2_warm_start():
        index = ensure_index(file_path, id_field="id", max_id_index=10000)
        results = []
        for test_id in test_ids:
            try:
                result = indexed_get_by_id(file_path, test_id, id_field="id", index=index)
                results.append(result)
            except:
                pass
        return results
    print(f"\n📖 V1 (Streaming): {num_ops} accesses (each scans from start)")
    v1_result = measure_operation("V1 Multiple Access", v1_multiple)
    if v1_result['success']:
        count = len(v1_result['result']) if isinstance(v1_result['result'], list) else 0
        avg_time = v1_result['time'] / num_ops
        print(f"  Total time: {format_time(v1_result['time'])}")
        print(f"  Avg per access: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v1_result['memory_peak'])}")
        print(f"  Records: {count}/{num_ops}")
    else:
        print(f"  ❌ FAILED: {v1_result.get('error', 'Unknown error')}")
    print(f"\n📖 V2 (Indexed) - RUN 1 (Cold): Build index + {num_ops} random accesses")
    v2_cold_result = measure_operation("V2 Cold Start", v2_cold_start)
    if v2_cold_result and v2_cold_result['success']:
        count = len(v2_cold_result['result']) if isinstance(v2_cold_result['result'], list) else 0
        avg_time = v2_cold_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_cold_result['time'])}")
        print(f"  Avg per access: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_cold_result['memory_peak'])}")
        print(f"  Records: {count}/{num_ops}")
    print(f"\n📖 V2 (Indexed) - RUN 2 (Warm): Use cached index, {num_ops} random accesses")
    v2_warm_result = measure_operation("V2 Warm Start", v2_warm_start)
    if v2_warm_result['success']:
        count = len(v2_warm_result['result']) if isinstance(v2_warm_result['result'], list) else 0
        avg_time = v2_warm_result['time'] / num_ops
        print(f"  Total time: {format_time(v2_warm_result['time'])}")
        print(f"  Avg per access: {format_time(avg_time)}")
        print(f"  Memory: {format_bytes(v2_warm_result['memory_peak'])}")
        print(f"  Records: {count}/{num_ops}")
    if v1_result['success'] and v2_warm_result['success']:
        v1_avg = v1_result['time'] / num_ops
        v2_warm_avg = v2_warm_result['time'] / num_ops
        print(f"\n  📊 Average per operation:")
        print(f"     V1: {format_time(v1_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            print(f"     V2 Cold: {format_time(v2_cold_avg)}")
        print(f"     V2 Warm: {format_time(v2_warm_avg)}")
        if v2_cold_result and v2_cold_result['success']:
            v2_cold_avg = v2_cold_result['time'] / num_ops
            speedup_cold = v1_avg / v2_cold_avg if v2_cold_avg > 0 else float('inf')
            print(f"\n  ⚡ V2 Cold is {speedup_cold:.2f}x {'faster' if speedup_cold > 1 else 'slower'} than V1")
            print(f"  💡 V2 Warm is {v2_cold_avg / v2_warm_avg:.2f}x faster than V2 Cold (index caching benefit)")
        speedup_warm = v1_avg / v2_warm_avg if v2_warm_avg > 0 else float('inf')
        print(f"  ⚡ V2 Warm is {speedup_warm:.2f}x {'faster' if speedup_warm > 1 else 'slower'} than V1")


def main():
    """Main comparison function"""
    data_dir = Path(__file__).parent / "data"
    file_path = data_dir / "database_1gb.jsonl"
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        print("Please run generate_1gb_file.py first to create the test file.")
        return 1
    file_size = file_path.stat().st_size
    print("="*70)
    print("JSON UTILS VERSION COMPARISON")
    print("="*70)
    print(f"\nFile: {file_path}")
    print(f"Size: {file_size / (1024**3):.2f} GB ({file_size:,} bytes)")
    print("\nComparing:")
    print("  V1: Streaming (no index) - Simple, memory-efficient")
    print("  V2: Indexed (with cache) - Fast random access, paging")
    print(f"\nTest Configuration: {len(OPERATION_COUNTS)} test runs with operation counts: {OPERATION_COUNTS}")
    # Run comparisons with operation counts defined at module level
    for num_ops in OPERATION_COUNTS:
        print("\n" + "="*70)
        print(f"RUNNING ALL COMPARISONS - {num_ops} OPERATIONS")
        print("="*70)
        print(f"Using {num_ops} operations per test")
        try:
            compare_first_access(str(file_path), skip_cold_if_indexed=True, num_ops=num_ops)
        except Exception as e:
            print(f"\n❌ ERROR in compare_first_access ({num_ops} ops): {e}")
            import traceback
            traceback.print_exc()
        try:
            compare_subsequent_access(str(file_path), skip_cold_if_indexed=True, num_ops=num_ops)
        except Exception as e:
            print(f"\n❌ ERROR in compare_subsequent_access ({num_ops} ops): {e}")
            import traceback
            traceback.print_exc()
        try:
            compare_id_lookup(str(file_path), skip_cold_if_indexed=True, num_ops=num_ops)
        except Exception as e:
            print(f"\n❌ ERROR in compare_id_lookup ({num_ops} ops): {e}")
            import traceback
            traceback.print_exc()
        try:
            compare_paging(str(file_path), skip_cold_if_indexed=True, num_ops=num_ops)
        except Exception as e:
            print(f"\n❌ ERROR in compare_paging ({num_ops} ops): {e}")
            import traceback
            traceback.print_exc()
        try:
            compare_multiple_random_access(str(file_path), skip_cold_if_indexed=True, num_ops=num_ops)
        except Exception as e:
            print(f"\n❌ ERROR in compare_multiple_random_access ({num_ops} ops): {e}")
            import traceback
            traceback.print_exc()
        print(f"\n{'='*70}")
        print(f"COMPLETED TESTING WITH {num_ops} OPERATIONS")
        print(f"{'='*70}\n")
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\n✅ V1 (Streaming) - Best for:")
    print("  • Simple sequential reads")
    print("  • One-time operations")
    print("  • Minimal memory footprint")
    print("  • No index maintenance")
    print("\n✅ V2 (Indexed) - Best for:")
    print("  • Random access patterns")
    print("  • ID-based lookups")
    print("  • Paging operations")
    print("  • Multiple accesses to same file")
    print("  • When index can be reused")
    print("\n💡 Recommendation:")
    print("  • Use V1 for simple, one-off operations")
    print("  • Use V2 when you need random access or will access the file multiple times")
    print("  • V2 index is built once and cached for future fast access")
    return 0
if __name__ == "__main__":
    exit(main())
