# x1_basic_db - Requirements Specification

## Purpose
Benchmark node-only database configurations without relationship/edge management capabilities.

## Scope

### In Scope
- **Node Storage Testing**: Evaluate all available NodeMode implementations
- **Table-Only Operations**: Test pure entity storage (users, posts, comments) without relationships
- **Group Categorization**: Compare Matrix/Array-based types (Group A) vs Other types (Group B)
- **CRUD Performance**: Measure Create, Read, Update, Delete operations on entities only

### Out of Scope
- Edge/relationship management (edge_mode = None for all configurations)
- Graph traversal operations
- Graph Manager functionality
- File serialization

## Test Configuration

### Entity Distribution
- **Users**: 50% of entities
- **Posts**: 30% of entities  
- **Comments**: 20% of entities
- **Scale**: 10% of declared test size (lighter for exhaustive testing)

### Test Sizes
- Small: 1 entity (actual: ~0.1)
- Medium: 10 entities (actual: ~1)
- Large: 100 entities (actual: ~10)

### Operations per Size
- **Read**: max(10, 10% of users) × 3 entity types
- **Update**: max(10, 10% of users) × 3 entity types
- **Delete**: max(10, 5% of users) progressive deletion

## Success Criteria

### Functional Requirements
- FR1: All NodeMode types must be auto-discovered and tested
- FR2: Each NodeMode must complete all CRUD operations without errors
- FR3: Results must be categorized into Group A (Matrix/Array) and Group B (Others)
- FR4: Metrics must include execution time and peak memory usage

### Performance Requirements
- PR1: Benchmark must complete within reasonable time for exhaustive testing
- PR2: Memory usage must be tracked throughout all operations
- PR3: Top 10 performers must be identified and reported

### Data Requirements
- DR1: Test data must include realistic entity structures (users, posts, comments)
- DR2: All entities must have proper ID generation and tracking
- DR3: Foreign key relationships (user_id, post_id) must be maintained in entity data

## Expected Outcomes
- Performance comparison matrix for all NodeMode types
- Identification of best node-only storage strategies
- Group-based performance analysis (Matrix vs Others)
- Success/failure count for each NodeMode

## Dependencies
- x0_common module (BenchmarkMetrics, BaseDatabase, BaseBenchmarkRunner)
- exonware.xwnode.defs (NodeMode enum)
- Test data generators (generate_user, generate_post, generate_comment)

