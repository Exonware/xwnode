# x2_classic_db - Requirements Specification

## Purpose
Benchmark predefined database configurations optimized for specific use cases and workload patterns.

## Scope

### In Scope
- **Predefined Configurations**: Test 6 carefully selected NodeMode + EdgeMode combinations
- **Use-Case Optimization**: Evaluate configurations designed for specific workloads:
  - Read-heavy workloads
  - Write-intensive operations
  - Memory-constrained environments
  - Complex graph queries
  - Persistent storage requirements
  - Data interchange scenarios
- **Full CRUD + Relationships**: Test complete database operations including graph traversal
- **Detailed Phase Reporting**: Track performance across all 5 operation phases

### Out of Scope
- Exhaustive strategy combinations (covered by x3)
- Graph Manager ON/OFF comparison (covered by x4)
- File serialization testing (covered by x5/x6)

## Predefined Models

### Model Configurations
1. **Read-Optimized**: HASH_MAP + None
   - Use Case: Fast lookups, frequent reads, minimal graph operations
   
2. **Write-Optimized**: LSM_TREE + DYNAMIC_ADJ_LIST
   - Use Case: High write throughput, continuous inserts, dynamic relationships
   
3. **Memory-Efficient**: B_TREE + CSR
   - Use Case: Large datasets, minimal RAM, compressed edge storage
   
4. **Query-Optimized**: TREE_GRAPH_HYBRID + WEIGHTED_GRAPH
   - Use Case: Complex graph traversal, weighted relationships, query-heavy workloads
   
5. **Persistence-Optimized**: B_PLUS_TREE + EDGE_PROPERTY_STORE
   - Use Case: Durability requirements, ACID compliance, rich edge properties
   
6. **XWData-Optimized**: DATA_INTERCHANGE_OPTIMIZED + None
   - Use Case: Serialization, format conversion, data exchange scenarios

## Test Configuration

### Entity Distribution
- **Users**: 50% of entities
- **Posts**: 30% of entities
- **Comments**: 20% of entities
- **Relationships**: 2× number of users (follows/friendship connections)

### Test Sizes
- Small: 1 entity
- Medium: 10 entities
- Large: 100 entities

### Operations per Size
- **Read**: max(100, 10% of users) × 3 entity types
- **Update**: 50% of each entity type
- **Delete**: max(10, 5% of users) progressive deletion
- **Relationship Queries**: Read operations × 2 (followers + following)

## Operation Phases

### Phase Breakdown
1. **Insert Phase**: Create all entities (users, posts, comments) + relationships
2. **Read Phase**: Random entity lookups across all types
3. **Update Phase**: Modify entity attributes
4. **Delete Phase**: Progressive deletion (comments → posts → users)
5. **Relationship Phase**: Graph traversal queries (get_followers, get_following)

## Success Criteria

### Functional Requirements
- FR1: All 6 predefined models must complete successfully
- FR2: Each model must execute all 5 phases without errors
- FR3: Detailed phase-by-phase metrics must be captured
- FR4: Use-case descriptions must be displayed with results

### Performance Requirements
- PR1: Total execution time must be measured across all phases
- PR2: Peak memory usage must be tracked throughout operations
- PR3: Phase-specific timing must be reported
- PR4: Results must enable use-case-specific optimization decisions

### Reporting Requirements
- RR1: Display model configuration and use case before testing
- RR2: Show phase progression during execution
- RR3: Print final results with time and memory metrics
- RR4: Handle and report errors with full stack traces

## Expected Outcomes
- Performance comparison for real-world use cases
- Identification of best configuration per workload type
- Phase-specific performance insights
- Practical guidance for production deployment

## Dependencies
- x0_common module (BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner)
- exonware.xwnode.defs (NodeMode, EdgeMode, GraphOptimization)
- Test data generators (generate_user, generate_post, generate_comment, generate_relationship)

