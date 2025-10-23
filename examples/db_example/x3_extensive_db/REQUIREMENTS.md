# x3_extensive_db - Requirements Specification

## Purpose
Exhaustively benchmark ALL possible combinations of NodeMode × EdgeMode to discover optimal strategy pairings.

## Scope

### In Scope
- **Exhaustive Combination Testing**: Test every NodeMode paired with every EdgeMode (including None)
- **Strategy Discovery**: Identify unexpected high-performance combinations
- **Comprehensive Coverage**: Auto-discover and test all available strategies at runtime
- **Performance Baseline**: Establish performance characteristics for all possible configurations
- **Progress Tracking**: Monitor success/failure rates across hundreds of combinations

### Out of Scope
- Graph Manager impact testing (covered by x4)
- File serialization (covered by x5/x6)
- Use-case-specific optimization (covered by x2)

## Test Configuration

### Combination Generation
- **Auto-Discovery**: Dynamically enumerate all NodeMode and EdgeMode values
- **Exhaustive Pairing**: Generate NodeMode × EdgeMode cartesian product
- **Includes None**: Test each NodeMode with edge_mode=None
- **Expected Count**: ~500-820 combinations (varies by enum size)

### Entity Distribution (Lightweight)
- **Scale Factor**: 10% of declared test size (for exhaustive testing efficiency)
- **Users**: 50% of base scale
- **Posts**: 30% of base scale
- **Comments**: 20% of base scale
- **Relationships**: 2× scaled users (only when edge_mode is not None)

### Test Sizes
- Minimal: 1 entity (actual: ~0.1)
- Small: 10 entities (actual: ~1)
- Medium: 100 entities (actual: ~10)

### Operations per Size
- **Read**: max(10, 10% of users) × 3 entity types
- **Update**: max(10, 10% of users) × 3 entity types
- **Delete**: max(10, 5% of users) progressive deletion

## Execution Strategy

### Runtime Optimization
- **Lightweight Operations**: Reduced entity counts and operations for speed
- **Conditional Relationships**: Only add relationships when edge_mode is present
- **Progress Reporting**: Status every 100 combinations (or at boundaries)
- **Error Resilience**: Continue testing on failures, track failed combinations

### Progress Indicators
- Show progress percentage at: 1st, every 100th, and final combination
- Display running success/failure counts
- Report completion summary

## Success Criteria

### Functional Requirements
- FR1: All NodeMode × EdgeMode combinations must be generated and tested
- FR2: Each combination must complete all CRUD operations
- FR3: Failures must be captured with error messages, not halt execution
- FR4: Results must include success/failure status for each combination

### Performance Requirements
- PR1: Benchmark must complete in reasonable time despite large combination count
- PR2: Each combination must measure total time and peak memory
- PR3: Top 10 performers must be identified from successful results
- PR4: Performance data must enable pattern recognition across strategies

### Data Quality Requirements
- DQ1: All combinations must have consistent test data characteristics
- DQ2: Results must be comparable across all combinations
- DQ3: Metrics must be normalized to same entity counts

## Expected Outcomes
- Complete performance matrix for all strategy combinations
- Discovery of unexpected high-performance pairings
- Identification of incompatible or failing combinations
- Evidence-based strategy selection guidance
- Top 10 fastest combinations across all possibilities

## Dependencies
- x0_common module (BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner, generate_all_combinations)
- exonware.xwnode.defs (NodeMode, EdgeMode enums)
- Test data generators (generate_user, generate_post, generate_comment, generate_relationship)

## Special Considerations
- **Long Runtime**: Expected to take significantly longer than other benchmarks
- **Error Handling**: Must gracefully handle incompatible combinations
- **Resource Usage**: May require substantial memory for large combination counts
- **Result Storage**: Generates large result sets requiring efficient storage/analysis

