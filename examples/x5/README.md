# JSON Utils - Atomic Read/Write Operations

This directory contains utilities for performing surgical (atomic) read and write operations on large NDJSON files without loading the entire file into memory.

## Files

- **`json_utils.py`** - Core utilities for streaming JSON operations
- **`generate_1gb_file.py`** - Script to generate a 1GB NDJSON file using x5 schema
- **`surgical_operations_demo.py`** - Demonstration of surgical read/write with timing and memory metrics
- **`test_atomic_operations.py`** - Comprehensive test suite

## Features

### Atomic Read Operations
- Stream-based reading that processes one record at a time
- Path-based extraction (read specific fields without loading full objects)
- Memory-efficient for files of any size
- No file corruption during reads
- **Async support**: Concurrent reads from the same file (multiple async operations can read simultaneously)

### Atomic Write Operations
- Uses temporary files and `os.replace()` for atomic updates
- Only matching records are loaded into memory
- Automatic cleanup of temp files on success and failure
- Preserves file integrity during updates
- **Async support**: Write operations are serialized (one at a time) to prevent corruption

### Async/Concurrent Access
- **Concurrent reads**: Multiple async read operations can run simultaneously
- **Serialized writes**: Write operations use locks to prevent concurrent writes
- **Thread-safe**: Uses asyncio for non-blocking I/O
- **Backward compatible**: Sync versions still available

## Usage

### 1. Generate 1GB Test File

```bash
python generate_1gb_file.py
```

This will create `data/database_1gb.jsonl` (~1GB) with:
- Users (10% of data)
- Posts (60% of data)  
- Comments (30% of data)

### 2. Run Surgical Operations Demo

```bash
python surgical_operations_demo.py
```

This demonstrates:
- Surgical reads (extract specific fields)
- Surgical writes (update specific records)
- Timing and memory usage for each operation

## Example Operations

### Sync Read Operations

```python
from json_utils import stream_read, match_by_id

# Read full user record
user = stream_read("database.jsonl", match_by_id("id", "user_123"))

# Read only email field
email = stream_read("database.jsonl", match_by_id("id", "user_123"), path=["email"])

# Read nested field
hashtags = stream_read("database.jsonl", match_by_id("id", "post_456"), path=["hashtags"])
```

### Async Read Operations (Concurrent)

```python
import asyncio
from json_utils import async_stream_read, match_by_id

# Concurrent async reads - multiple operations can run simultaneously
async def read_multiple_users():
    tasks = [
        async_stream_read("database.jsonl", match_by_id("id", "user_123")),
        async_stream_read("database.jsonl", match_by_id("id", "user_456")),
        async_stream_read("database.jsonl", match_by_id("id", "user_789")),
    ]
    results = await asyncio.gather(*tasks)  # All read concurrently!
    return results

# Run async operations
users = asyncio.run(read_multiple_users())
```

### Indexed Async Reads (V2)

```python
import asyncio
from json_utils_indexed import async_indexed_get_by_id, async_ensure_index

# Concurrent indexed reads
async def read_multiple_indexed():
    # Ensure index exists (shared across all reads)
    index = await async_ensure_index("database.jsonl", id_field="id")
    
    # Multiple concurrent reads using index
    tasks = [
        async_indexed_get_by_id("database.jsonl", "user_123", index=index),
        async_indexed_get_by_id("database.jsonl", "user_456", index=index),
        async_indexed_get_by_id("database.jsonl", "user_789", index=index),
    ]
    results = await asyncio.gather(*tasks)  # All read concurrently with index!
    return results
```

### Write Operations

```python
from json_utils import stream_update, match_by_id, update_path

# Update single field (sync)
def update_email(obj):
    obj["email"] = "new@example.com"
    return obj

count = stream_update("database.jsonl", match_by_id("id", "user_123"), update_email, atomic=True)

# Update using path
updater = update_path(["likes_count"], 100)
count = stream_update("database.jsonl", match_by_id("id", "post_456"), updater, atomic=True)
```

### Async Write Operations (Serialized)

```python
import asyncio
from json_utils import async_stream_update, match_by_id

# Async writes are serialized (one at a time) to prevent corruption
async def update_multiple():
    def update_email(obj):
        obj["email"] = "new@example.com"
        return obj
    
    # These will run one at a time (serialized)
    results = await asyncio.gather(
        async_stream_update("database.jsonl", match_by_id("id", "user_123"), update_email),
        async_stream_update("database.jsonl", match_by_id("id", "user_456"), update_email),
    )
    return results
```

## Performance Characteristics

For a 1GB file:
- **Read operations**: ~10-50ms per record, <1MB memory
- **Write operations**: ~100-500ms per update, <5MB memory
- **Memory efficiency**: Only loads one record at a time
- **Atomic guarantees**: Uses `os.replace()` for safe updates

## Testing

### Sync Operations Test

Run the comprehensive test suite:

```bash
python test_atomic_operations.py
```

All tests should pass, verifying:
- Atomic read operations
- Atomic write operations  
- Failure recovery
- Large file streaming
- Memory efficiency

### Async Operations Test

Test concurrent async reads:

```bash
python test_async_operations.py
```

This verifies:
- Concurrent async reads (V1 streaming)
- Concurrent async reads (V2 indexed)
- Mixed concurrent reads (V1 + V2 together)
- Multiple async operations can read simultaneously
- Write operations are serialized

