# x5_file_db - Requirements Specification

## Purpose
Benchmark file serialization performance across multiple formats for top-performing database configurations.

## Scope

### In Scope
- **Serialization Format Testing**: Evaluate performance across multiple file formats
- **Top Performer Selection**: Use best-performing strategies from x3 extensive benchmark
- **Multi-Format Support**: Test JSON, YAML, MsgPack, Pickle, CBOR, BSON, CSV, TOML, XML
- **File Operations**: Measure save/load performance and file size efficiency
- **Format Comparison**: Identify fastest and most space-efficient serialization formats

### Out of Scope
- Advanced serialization features (covered by x6)
- All strategy combinations (only top performers tested)
- Graph Manager comparison (focus on serialization only)

## Current Status

### Implementation State
**ENABLED - Using xwsystem Serialization**

### Integration
- Uses xwsystem serialization module with 30+ format support
- Saves files to `x5_file_db/data/` directory
- Tests 8 core formats: JSON, YAML, MsgPack, Pickle, CBOR, BSON, TOML, XML
- Measures both performance (time) and efficiency (file size)

## Test Configuration

### Model Selection
- **Top Performer**: SPARSE_MATRIX + EDGE_PROPERTY_STORE
- **Selection Criteria**: Based on x3_extensive_db benchmark results
- **Configuration**: Graph Manager OFF (focus on serialization, not graph operations)

### Serialization Formats
1. **JSON**: Human-readable, universal compatibility
2. **YAML**: Human-readable, configuration-friendly
3. **MsgPack**: Binary, compact, fast
4. **Pickle**: Python-native, object serialization
5. **CBOR**: Binary, standard (RFC 7049)
6. **BSON**: Binary, MongoDB-compatible
7. **CSV**: Tabular, spreadsheet-compatible
8. **TOML**: Configuration format
9. **XML**: Structured, widely supported

### Entity Distribution
- **Users**: 50% of entities
- **Posts**: 30% of entities
- **Comments**: 20% of entities
- **Relationships**: 2× users

### Test Sizes
- Light: 100 entities (actual: ~10)
- Medium: 1,000 entities (actual: ~100)
- Heavy: 10,000 entities (actual: ~1,000)

### Operations per Format
- **CRUD Operations**: Standard insert, read, update, delete
- **Save Operation**: Serialize entire database to file
- **Load Operation**: Deserialize database from file
- **File Size Measurement**: Track storage efficiency

## Success Criteria

### Functional Requirements
- FR1: All listed formats must be tested successfully
- FR2: Each format must complete save/load cycle without errors
- FR3: Deserialized data must match original data (round-trip integrity)
- FR4: File size must be measured for each format

### Performance Requirements
- PR1: Serialization time must be measured separately from CRUD operations
- PR2: Deserialization time must be measured separately
- PR3: File size efficiency must be compared across formats
- PR4: Top 3 formats must be identified for speed and size

### Data Integrity Requirements
- DI1: All entities must serialize without data loss
- DI2: Relationships must preserve after serialization round-trip
- DI3: Data types must be preserved (no type coercion issues)

## Expected Outcomes
- Performance ranking of serialization formats
- File size comparison across formats
- Fastest format for save operations
- Fastest format for load operations
- Most space-efficient format
- Format recommendations for different use cases

## Dependencies
- x0_common module (BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner)
- exonware.xwnode.defs (NodeMode, EdgeMode)
- exonware.xwsystem.serialization (JsonSerializer, YamlSerializer, etc.)
- Python pathlib, shutil for file operations

## Output Format
- Per-format results: Time, file size, success status
- Rankings by speed (fastest formats first)
- Rankings by size (most compact formats first)
- Files saved to `data/` directory with descriptive names

## Special Considerations
- **Production-Ready**: Uses battle-tested serialization libraries (not custom implementations)
- **Format-Specific Challenges**: Some formats may not support all data structures (e.g., TOML limitations)
- **File Cleanup**: Data directory is cleaned before each run
- **Entity Scaling**: 10% scale factor keeps tests fast while covering format capabilities
- **Two Rankings**: Speed vs Size trade-off analysis

