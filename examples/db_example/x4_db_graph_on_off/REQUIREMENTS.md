# x4_db_graph_on_off - Requirements Specification

## Purpose
Measure the performance impact of XWGraphManager indexing and caching by comparing identical configurations with Graph Manager ON vs OFF.

## Scope

### In Scope
- **Graph Manager Impact Analysis**: Test each NodeMode × EdgeMode combination with GraphOptimization.FULL and GraphOptimization.OFF
- **Paired Comparison**: Every configuration tested twice (Graph ON + Graph OFF)
- **Indexing Overhead**: Measure cost of graph indexing during operations
- **Query Acceleration**: Measure benefit of graph caching during traversal
- **Edge-Required Configurations**: Only test combinations with edge_mode (Graph Manager requires edges)

### Out of Scope
- Node-only configurations (Graph Manager requires edge_mode)
- File serialization testing (covered by x5/x6)
- Partial graph optimization modes (only FULL vs OFF)

## Test Configuration

### Combination Generation
- **Base Combinations**: All NodeMode × EdgeMode pairs (excluding edge_mode=None)
- **Doubling Factor**: Each combination generates 2 test cases (Graph ON + Graph OFF)
- **Expected Count**: ~300-500 combinations × 2 = 600-1000 total tests

### Graph Manager Modes
1. **GraphOptimization.OFF**: No indexing, direct edge structure queries
2. **GraphOptimization.FULL**: Full indexing, adjacency caching, optimized traversal

### Entity Distribution (Lightweight)
- **Scale Factor**: 10% of declared test size (for exhaustive testing)
- **Users**: 50% of base scale
- **Posts**: 30% of base scale
- **Comments**: 20% of base scale
- **Relationships**: 2× scaled users (always present for these tests)

### Test Sizes
- Light: 1,000 entities (actual: ~100)
- Medium: 10,000 entities (actual: ~1,000)
- Heavy: 100,000 entities (actual: ~10,000)

### Operations per Size
- **Read**: max(10, 10% of users) × 3 entity types
- **Update**: max(10, 10% of users) × 3 entity types
- **Delete**: max(10, 5% of users) progressive deletion
- **Graph Queries**: max(10, 10% of users) × 2 (followers + following)

## Operation Phases

### Phase Breakdown
1. **Insert Phase**: Create entities + relationships (measure indexing overhead)
2. **Read Phase**: Standard entity lookups
3. **Update Phase**: Entity modifications (measure index maintenance)
4. **Delete Phase**: Entity removal (measure index cleanup)
5. **Graph Queries Phase**: Relationship traversal (measure query acceleration)

### Critical Measurements
- **Phase 1 (Insert)**: Graph Manager indexing overhead during creation
- **Phase 5 (Graph Queries)**: Graph Manager acceleration benefit during traversal
- **Net Performance**: Overall time difference (Graph ON vs Graph OFF)

## Success Criteria

### Functional Requirements
- FR1: Each NodeMode × EdgeMode pair must generate exactly 2 test cases
- FR2: Graph ON and Graph OFF must use identical test data and operations
- FR3: Both modes must complete all 5 phases successfully
- FR4: Results must clearly label Graph Manager status (ON/OFF)

### Performance Requirements
- PR1: Both modes must have comparable metrics for fair comparison
- PR2: Graph queries phase must demonstrate measurable differences
- PR3: Total time and memory must be tracked independently for each mode
- PR4: Results must enable calculation of Graph Manager overhead/benefit

### Comparison Requirements
- CR1: Top 5 performers must be reported separately for Graph ON
- CR2: Top 5 performers must be reported separately for Graph OFF
- CR3: Results must enable identification of when Graph Manager is beneficial
- CR4: Results must show when Graph Manager overhead exceeds benefits

## Expected Outcomes
- Performance impact quantification for Graph Manager across all strategies
- Identification of configurations that benefit most from Graph Manager
- Identification of configurations where Graph Manager adds overhead
- Evidence-based guidance for when to enable/disable Graph Manager
- Separate rankings for Graph ON vs Graph OFF scenarios

## Dependencies
- x0_common module (BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner, generate_all_combinations)
- exonware.xwnode.defs (NodeMode, EdgeMode, GraphOptimization)
- Test data generators (generate_user, generate_post, generate_comment, generate_relationship)

## Special Considerations
- **Doubled Test Count**: Twice as many tests as x3_extensive_db
- **Paired Comparison**: Each configuration must produce 2 directly comparable results
- **Graph Queries Required**: Phase 5 is critical for measuring Graph Manager benefit
- **Resource Usage**: Graph Manager may increase memory usage, must track this

