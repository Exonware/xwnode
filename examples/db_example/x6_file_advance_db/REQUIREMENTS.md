# x6_file_advance_db - Requirements Specification

## Purpose
Benchmark advanced serialization features for formats supporting path-based access, streaming, and key-value operations.

## Scope

### In Scope
- **Advanced Serialization Features**: Test capabilities beyond basic save/load
- **Partial Access Operations**: Path-based get/set without full deserialization
- **Streaming Operations**: Memory-efficient data processing
- **Patch Operations**: RFC 6902 JSON Patch support
- **Key-Value Operations**: LMDB and SQLite3 database-backed serialization
- **Advanced Formats**: JSON, XML, YAML (path ops), LMDB, SQLite3 (kv ops)

### Out of Scope
- Basic serialization (covered by x5)
- Simple formats without advanced features (MsgPack, Pickle, CBOR, BSON)
- Graph Manager testing (focus on advanced serialization only)

## Current Status

### Implementation State
**ENABLED - Using xwsystem Advanced Serialization**

### Integration
- Uses xwsystem serialization module with advanced capabilities
- Saves files to `x6_file_advance_db/data/` directory
- Tests 5 advanced formats: JSON, XML, YAML (path ops), LMDB, SQLite3 (kv ops)
- Tests format-specific advanced features (streaming, path access, key-value operations)

## Advanced Operations (When Enabled)

### Path-Based Access
- **get_at**: Random path access without full deserialization
  - Use Case: Extract specific fields from large files efficiently
  - Formats: JSON, XML, YAML
  
- **set_at**: Partial updates by JSON pointer path
  - Use Case: Update specific fields without rewriting entire file
  - Formats: JSON, XML, YAML

- **iter_path**: Streaming with filtering
  - Use Case: Process large datasets incrementally with filters
  - Formats: JSON, XML, YAML

### Patch Operations
- **apply_patch**: RFC 6902 JSON Patch operations
  - Operations: add, remove, replace, move, copy, test
  - Use Case: Atomic partial updates, API-style modifications
  - Format: JSON

### Streaming Operations
- **streaming_load**: Memory-efficient streaming
  - Use Case: Process files larger than available RAM
  - Formats: JSON, XML

### Hashing Operations
- **canonical_hash**: Deterministic hashing
  - Use Case: Content-based deduplication, integrity verification
  - Formats: JSON, YAML

### Key-Value Operations
- **kv_get**: Key-based retrieval
- **kv_put**: Key-based storage
- **kv_scan_prefix**: Prefix-based range queries
- **Use Case**: Database-backed entity storage with indexing
- **Formats**: LMDB, SQLite3

## Test Configuration

### Model Selection
- **Top Performer**: SPARSE_MATRIX + EDGE_PROPERTY_STORE
- **Selection Criteria**: Based on x3_extensive_db + x5_file_db results
- **Configuration**: Graph Manager OFF, storage_smart_format ON

### Advanced Format Selection
1. **JSON**: Path ops, patch ops, streaming, hashing
2. **XML**: Path ops, streaming
3. **YAML**: Path ops, hashing
4. **LMDB**: Key-value operations, high-performance embedded DB
5. **SQLite3**: Key-value operations, SQL-backed storage

### Entity Distribution
- **Users**: 50% of entities
- **Posts**: 30% of entities
- **Comments**: 20% of entities
- **Relationships**: 2× users

### Test Sizes
- Light: 100 entities (actual: ~10)
- Medium: 1,000 entities (actual: ~100)
- Heavy: 10,000 entities (actual: ~1,000)

### Operation Scenarios
- **get_at_random**: Random path access across entities
- **set_at_scattered**: Partial updates to scattered locations
- **iter_path_filter**: Filtered streaming through entities
- **apply_patch_batch**: Batch JSON Patch operations
- **streaming_load**: Memory-efficient full load
- **canonical_hash**: Deterministic hashing for integrity
- **kv_get/put**: Entity storage/retrieval by key
- **kv_scan_prefix**: Range queries (e.g., all users)

## Success Criteria

### Functional Requirements
- FR1: All advanced operations must work on supported formats
- FR2: Path operations must succeed without full deserialization
- FR3: Streaming must handle datasets larger than memory
- FR4: Patch operations must apply correctly and atomically
- FR5: Key-value operations must maintain consistency

### Performance Requirements
- PR1: Path access must be faster than full deserialization
- PR2: Partial updates must be faster than full rewrite
- PR3: Streaming must use constant memory regardless of file size
- PR4: Key-value ops must provide sub-linear lookup times
- PR5: Each operation type must be timed independently

### Feature Completeness Requirements
- FC1: JSON must support all listed advanced operations
- FC2: LMDB/SQLite3 must support all key-value operations
- FC3: Streaming formats must handle large files (>1GB test)
- FC4: Patch operations must follow RFC 6902 specification

## Expected Outcomes
- Performance comparison of advanced features across formats
- Identification of best format for each operation type
- Validation of memory-efficient streaming capabilities
- Performance characterization of key-value backends
- Best practices for path-based vs full deserialization
- Format recommendations for advanced use cases

## Dependencies
- x0_common module (BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner)
- exonware.xwnode.defs (NodeMode, EdgeMode)
- exonware.xwsystem.serialization (JsonSerializer, XmlSerializer, YamlSerializer, Sqlite3Serializer, LmdbSerializer)
- Python pathlib, shutil for file operations

## Output Format
- Per-format results with capabilities listed
- Performance metrics including advanced operation timing
- Rankings by speed for formats with comparable capabilities
- Files saved to `data/` directory
- LMDB creates directories, SQLite3 creates .db files

## Special Considerations
- **Advanced Features**: Tests capabilities beyond basic save/load
- **Memory Efficiency Focus**: Streaming operations critical for large datasets
- **Format-Specific**: Not all formats support all operations (graceful degradation)
- **Database Integration**: LMDB/SQLite3 are embedded databases, not just file formats
- **Capability Tracking**: Each format tagged with its supported advanced operations
- **Future Expansion**: Framework ready for RFC 6902 patches, path operations when fully implemented
- **Entity Scaling**: 10% scale factor keeps advanced operation tests fast

