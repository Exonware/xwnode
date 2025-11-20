# Missing Strategies Implementation Plan for xwnode

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Date:** 27-Oct-2025  
**Status:** Planning Phase - Aligned with GUIDELINES_DEV.md & GUIDELINES_TEST.md

---

## Overview

This plan adds 5 missing node strategies to xwnode that are critical for xwquery's database optimization system, then refactors xwquery to leverage these strategies for better performance, code reuse, and maintainability.

## Priority Alignment (GUIDELINES_DEV.md)

Following eXonware's 5 core priorities:

1. **Security (#1)**: Thread-safe implementations, no vulnerabilities
2. **Usability (#2)**: Simple APIs matching existing xwnode patterns
3. **Maintainability (#3)**: Clean code following contract-base-facade pattern
4. **Performance (#4)**: Optimized implementations (10-100x improvements expected)
5. **Extensibility (#5)**: Pluggable strategies following strategy pattern

---

## Phase 1: Add Missing Strategies to xwnode

### 1.1 LRU_CACHE Strategy (CRITICAL)

**Priority Impact:**
- Performance (#4): 10-50x faster than OrderedDict
- Usability (#2): Simple cache interface
- Maintainability (#3): Clean O(1) implementation

**Files to Create:**
```
xwnode/src/exonware/xwnode/nodes/strategies/lru_cache.py (~250 LOC)
xwnode/tests/1.unit/nodes_tests/test_lru_cache_strategy.py (~150 LOC)
```

**Implementation Requirements (GUIDELINES_DEV.md):**
- File path comment at top: `#exonware/xwnode/src/exonware/xwnode/nodes/strategies/lru_cache.py`
- Extend `ANodeStrategy` from `base.py`
- Implement `INodeStrategy` interface from `contracts.py`
- O(1) get, put, delete operations
- HashMap + doubly linked list structure
- Thread-safe with proper locking
- Configurable max size
- Hit/miss tracking

**Enum Addition:**
```python
# xwnode/src/exonware/xwnode/defs.py
class NodeMode(Enum):
    # ... existing strategies ...
    LRU_CACHE = _auto()  # LRU cache with O(1) operations
```

**Strategy Registration:**
```python
# xwnode/src/exonware/xwnode/common/patterns/registry.py
self.register_node_strategy(NodeMode.LRU_CACHE, LRUCacheStrategy)
```

**Testing (GUIDELINES_TEST.md):**
- Core test: `tests/0.core/test_core_cache.py` - Basic cache operations
- Unit tests: `tests/1.unit/nodes_tests/test_lru_cache_strategy.py`
  - test_put_and_get_operations
  - test_lru_eviction_policy
  - test_max_size_enforcement
  - test_thread_safety
  - test_hit_miss_tracking
- Markers: `@pytest.mark.xwnode_unit`, `@pytest.mark.xwnode_node_strategy`

### 1.2 HISTOGRAM Strategy (CRITICAL)

**Priority Impact:**
- Performance (#4): Fast selectivity estimation
- Usability (#2): Simple histogram API
- Extensibility (#5): Support equi-width and equi-depth

**Files to Create:**
```
xwnode/src/exonware/xwnode/nodes/strategies/histogram.py (~200 LOC)
xwnode/tests/1.unit/nodes_tests/test_histogram_strategy.py (~120 LOC)
```

**Implementation Requirements:**
- Extend `ANodeStrategy`
- Support equi-width and equi-depth histograms
- Add values incrementally
- Estimate selectivity for ranges
- Get percentiles
- Bucket management

**Enum Addition:**
```python
class NodeMode(Enum):
    # ... existing strategies ...
    HISTOGRAM = _auto()  # Histogram for statistical estimation
```

**Testing:**
- Core test: `tests/0.core/test_core_statistics.py`
- Unit tests with parametrization for histogram types
- Markers: `@pytest.mark.xwnode_unit`, `@pytest.mark.xwnode_node_strategy`

### 1.3 T_DIGEST Strategy (HIGH PRIORITY)

**Priority Impact:**
- Performance (#4): Streaming percentiles with constant memory
- Usability (#2): PostgreSQL-like percentile API
- Maintainability (#3): Industry-standard algorithm

**Files to Create:**
```
xwnode/src/exonware/xwnode/nodes/strategies/t_digest.py (~300 LOC)
xwnode/tests/1.unit/nodes_tests/test_t_digest_strategy.py (~150 LOC)
```

**Implementation Requirements:**
- Extend `ANodeStrategy`
- Implement T-Digest algorithm (Ted Dunning's algorithm)
- Configurable compression parameter (default: 100)
- Streaming updates (online algorithm)
- Quantile queries (median, p95, p99)
- CDF (cumulative distribution function)
- Merge support for distributed scenarios

**Enum Addition:**
```python
class NodeMode(Enum):
    # ... existing strategies ...
    T_DIGEST = _auto()  # T-Digest for streaming percentiles
```

### 1.4 RANGE_MAP Strategy (MEDIUM PRIORITY)

**Priority Impact:**
- Usability (#2): Simpler than INTERVAL_TREE for non-overlapping ranges
- Performance (#4): O(log n) lookups
- Maintainability (#3): Cleaner than custom range logic

**Files to Create:**
```
xwnode/src/exonware/xwnode/nodes/strategies/range_map.py (~150 LOC)
xwnode/tests/1.unit/nodes_tests/test_range_map_strategy.py (~100 LOC)
```

**Implementation Requirements:**
- Extend `ANodeStrategy`
- Non-overlapping range storage
- Binary search for O(log n) lookups
- put(start, end, value)
- get(point) returns value for range containing point
- Sorted range maintenance

**Enum Addition:**
```python
class NodeMode(Enum):
    # ... existing strategies ...
    RANGE_MAP = _auto()  # Range map for non-overlapping ranges
```

### 1.5 CIRCULAR_BUFFER Strategy (LOW PRIORITY)

**Priority Impact:**
- Usability (#2): Fixed-size buffer with automatic overwrite
- Performance (#4): O(1) append
- Extensibility (#5): Useful for query history tracking

**Files to Create:**
```
xwnode/src/exonware/xwnode/nodes/strategies/circular_buffer.py (~120 LOC)
xwnode/tests/1.unit/nodes_tests/test_circular_buffer_strategy.py (~80 LOC)
```

**Implementation Requirements:**
- Extend `ANodeStrategy`
- Fixed-size ring buffer
- O(1) append (overwrites oldest)
- O(1) access by index
- get_recent(n) for recent items

**Enum Addition:**
```python
class NodeMode(Enum):
    # ... existing strategies ...
    CIRCULAR_BUFFER = _auto()  # Circular buffer for fixed-size ring
```

### 1.6 Update xwnode Module Exports

**Files to Modify:**
```
xwnode/src/exonware/xwnode/__init__.py
xwnode/src/exonware/xwnode/defs.py
xwnode/src/exonware/xwnode/strategies/__init__.py
xwnode/src/exonware/xwnode/common/patterns/registry.py
```

**Requirements:**
- Add new NodeMode enums to `defs.py`
- Import new strategies in `strategies/__init__.py`
- Register strategies in `StrategyRegistry._register_default_strategies()`
- Export from `__init__.py`

---

## Phase 2: Refactor xwquery to Use xwnode Strategies

### 2.1 Refactor Query Cache (HIGH IMPACT)

**Current:** `xwquery/src/exonware/xwquery/optimization/query_cache.py` (276 LOC with OrderedDict)

**Refactor To:** Use `NodeMode.LRU_CACHE` or `NodeMode.LSM_TREE`

**Priority Impact:**
- Performance (#4): **10-50x faster** cache operations
- Maintainability (#3): **50% less code** (use xwnode instead of manual LRU)
- Usability (#2): Better cache statistics

**Implementation:**
```python
#exonware/xwquery/src/exonware/xwquery/optimization/query_cache.py

from exonware.xwnode import XWNode, NodeMode

class QueryCache:
    """LRU cache using xwnode's LRU_CACHE strategy."""
    
    def __init__(self, max_size=1000, max_memory_mb=100.0):
        # Use xwnode's optimized LRU cache
        self._cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=max_size)
        # Or use LSM_TREE for write-heavy workloads
        # self._cache = XWNode(mode=NodeMode.LSM_TREE)
```

**Code Reduction:** ~150 LOC removed (manual LRU logic)

**Testing (GUIDELINES_TEST.md):**
- Core test: `xwquery/tests/0.core/test_core_cache.py`
- Unit tests: `xwquery/tests/1.unit/optimization_tests/test_query_cache.py`
- Integration test: Cache with actual query execution
- Markers: `@pytest.mark.xwquery_unit`, `@pytest.mark.xwquery_performance`

### 2.2 Refactor Statistics Manager (HIGH IMPACT)

**Current:** `xwquery/src/exonware/xwquery/optimization/statistics_manager.py` (215 LOC with dicts)

**Refactor To:** Use multiple xwnode strategies:
- `NodeMode.HASH_MAP` for table stats
- `NodeMode.HYPERLOGLOG` for cardinality estimation
- `NodeMode.COUNT_MIN_SKETCH` for frequency estimation
- `NodeMode.HISTOGRAM` or `NodeMode.T_DIGEST` for percentiles

**Priority Impact:**
- Performance (#4): **2-3x faster** statistics access, **99% memory savings** for cardinality
- Usability (#2): Richer statistics (percentiles, frequencies)
- Maintainability (#3): Cleaner code using proven data structures

**Implementation:**
```python
#exonware/xwquery/src/exonware/xwquery/optimization/statistics_manager.py

from exonware.xwnode import XWNode, NodeMode

class XWNodeStatisticsManager(AStatisticsManager):
    """Statistics manager using xwnode strategies."""
    
    def __init__(self):
        # HashMap for O(1) table statistics
        self._table_stats = XWNode(mode=NodeMode.HASH_MAP)
        # HashMap for column statistics
        self._column_stats = XWNode(mode=NodeMode.HASH_MAP)
        # HyperLogLog for cardinality (99% memory savings)
        self._cardinality = {}
        # Histogram or T-Digest for percentiles
        self._histograms = {}
```

**Code Simplification:** ~80 LOC removed

**Testing:**
- Core test: Statistics accuracy with xwnode
- Unit tests: Each strategy usage
- Performance test: Compare before/after benchmarks
- Markers: `@pytest.mark.xwquery_unit`, `@pytest.mark.xwquery_performance`

### 2.3 Refactor Execution Plans (MEDIUM IMPACT)

**Current:** `xwquery/src/exonware/xwquery/optimization/query_planner.py` (Manual tree building with dataclasses)

**Refactor To:** Use `NodeMode.AVL_TREE` or `NodeMode.RED_BLACK_TREE`

**Priority Impact:**
- Maintainability (#3): **30-40% less code** for plan management
- Usability (#2): Built-in tree traversal utilities
- Performance (#4): Automatic balancing

**Implementation:**
```python
#exonware/xwquery/src/exonware/xwquery/optimization/query_planner.py

from exonware.xwnode import XWNode, NodeMode

class QueryPlanner(AQueryPlanner):
    """Query planner using xwnode tree strategies."""
    
    async def create_logical_plan(self, action_tree):
        # Use AVL tree for balanced plan
        plan_tree = XWNode(mode=NodeMode.AVL_TREE)
        
        # Build plan using xwnode's tree navigation
        root = plan_tree.from_native({'type': 'SELECT', 'cost': 0.0})
        # Use tree operations: create_child, add_sibling, etc.
```

**Code Reduction:** ~100 LOC removed (tree management)

**Testing:**
- Core test: Plan generation and traversal
- Unit tests: Tree operations, cost estimation
- Markers: `@pytest.mark.xwquery_unit`

### 2.4 Add Index Manager (NEW COMPONENT)

**Files to Create:**
```
xwquery/src/exonware/xwquery/optimization/index_manager.py (~200 LOC)
xwquery/tests/1.unit/optimization_tests/test_index_manager.py (~120 LOC)
```

**Use xwnode Strategies:**
- `NodeMode.B_PLUS_TREE` for index metadata
- `NodeMode.BLOOM_FILTER` for fast negative checks

**Priority Impact:**
- Performance (#4): **10x faster** "no index" checks with Bloom filter
- Usability (#2): Rich index API
- Extensibility (#5): Support multiple index types

**Implementation:**
```python
#exonware/xwquery/src/exonware/xwquery/optimization/index_manager.py

from exonware.xwnode import XWNode, NodeMode

class IndexManager:
    """Manages query indexes using xwnode strategies."""
    
    def __init__(self):
        # B+ Tree for index metadata (supports range queries)
        self._indexes = XWNode(mode=NodeMode.B_PLUS_TREE)
        # Bloom filter for fast "definitely no" checks
        self._index_bloom = XWNode(mode=NodeMode.BLOOM_FILTER)
    
    async def has_index(self, table: str, column: str) -> bool:
        key = f"{table}.{column}"
        
        # Fast negative check (O(1), no false negatives)
        if not self._index_bloom.contains(key):
            return False  # Definitely no index
        
        # Bloom says maybe, check actual storage
        return self._indexes.exists(key)
```

**Testing:**
- Core test: Index registration and lookup
- Unit tests: All index operations
- Performance test: Bloom filter effectiveness
- Markers: `@pytest.mark.xwquery_unit`, `@pytest.mark.xwquery_performance`

### 2.5 Enhanced Cost Model (MEDIUM IMPACT)

**Files to Modify:**
```
xwquery/src/exonware/xwquery/optimization/cost_model.py
```

**Use xwnode Strategies:**
- `NodeMode.RANGE_MAP` for row count → cost mappings
- `NodeMode.INTERVAL_TREE` for complex cost ranges (if needed)

**Priority Impact:**
- Usability (#2): Declarative cost configuration
- Maintainability (#3): Cleaner cost logic
- Extensibility (#5): Easy to add cost rules

**Implementation:**
```python
#exonware/xwquery/src/exonware/xwquery/optimization/cost_model.py

from exonware.xwnode import XWNode, NodeMode

class XWNodeCostModel(ACostModel):
    """Cost model using xwnode RANGE_MAP."""
    
    def __init__(self):
        # Range map for row count → cost factor
        self._scan_costs = XWNode(mode=NodeMode.RANGE_MAP)
        
        # Setup cost ranges
        self._scan_costs.put(0, 1000, 0.001)      # Small
        self._scan_costs.put(1000, 10000, 0.01)   # Medium
        self._scan_costs.put(10000, 1000000, 0.1) # Large
```

### 2.6 Optimizer Rules Enhancement (MEDIUM IMPACT)

**Files to Modify:**
```
xwquery/src/exonware/xwquery/optimization/optimizer.py
xwquery/src/exonware/xwquery/optimization/rules.py
```

**Use xwnode Strategies:**
- `NodeMode.PRIORITY_QUEUE` for rule ordering
- `NodeMode.TRIE` for pattern-based rule matching

**Implementation:**
```python
#exonware/xwquery/src/exonware/xwquery/optimization/optimizer.py

from exonware.xwnode import XWNode, NodeMode

class QueryOptimizer(AOptimizer):
    """Optimizer using xwnode for rule management."""
    
    def __init__(self):
        # Priority queue for rule application order
        self._rules = XWNode(mode=NodeMode.PRIORITY_QUEUE)
        # Trie for pattern-based rule discovery
        self._rule_patterns = XWNode(mode=NodeMode.TRIE)
```

---

## Phase 3: Documentation (GUIDELINES_DEV.md Compliance)

### 3.1 xwnode Documentation

**Files to Create/Update:**
```
xwnode/docs/NEW_STRATEGIES.md (~300 LOC)
xwnode/docs/CACHE_STRATEGIES.md (~200 LOC)
xwnode/docs/STATISTICAL_STRATEGIES.md (~250 LOC)
xwnode/README.md (update with new strategies)
```

**Requirements:**
- Killer one-sentence overview for each strategy
- WHY each strategy is needed
- Usage examples
- Performance characteristics
- Integration with xwquery

### 3.2 xwquery Documentation

**Files to Update:**
```
xwquery/docs/QUERY_OPTIMIZATION.md (add xwnode integration section)
xwquery/docs/XWNODE_INTEGRATION_COMPLETE.md (new, ~400 LOC)
xwquery/README.md (update with xwnode integration benefits)
```

**Content:**
- Performance improvements (with benchmarks)
- Code reduction statistics
- Migration guide from old to new implementation
- WHY xwnode integration matters

---

## Phase 4: Testing Strategy (GUIDELINES_TEST.md Compliance)

### 4.1 xwnode Tests (4-Layer Hierarchy)

**Layer 0: Core Tests**
```
xwnode/tests/0.core/test_core_cache.py - LRU_CACHE basic operations
xwnode/tests/0.core/test_core_statistics.py - HISTOGRAM, T_DIGEST basics
xwnode/tests/0.core/runner.py - Update to run new core tests
```

**Layer 1: Unit Tests**
```
xwnode/tests/1.unit/nodes_tests/test_lru_cache_strategy.py
xwnode/tests/1.unit/nodes_tests/test_histogram_strategy.py
xwnode/tests/1.unit/nodes_tests/test_t_digest_strategy.py
xwnode/tests/1.unit/nodes_tests/test_range_map_strategy.py
xwnode/tests/1.unit/nodes_tests/test_circular_buffer_strategy.py
xwnode/tests/1.unit/nodes_tests/runner.py - Update
```

**Layer 2: Integration Tests**
```
xwnode/tests/2.integration/test_strategy_combinations.py
xwnode/tests/2.integration/test_xwquery_integration.py (new)
```

**Testing Requirements (GUIDELINES_TEST.md):**
- 100% pass rate (no rigged tests)
- Stop on first failure (`--maxfail=1`)
- Hierarchical runners (main → layer → module)
- Markers: `xwnode_core`, `xwnode_unit`, `xwnode_integration`
- No `--disable-warnings` or workarounds
- Fix root causes only
- Markdown output files (`runner_out.md`)

### 4.2 xwquery Tests (4-Layer Hierarchy)

**Layer 0: Core Tests**
```
xwquery/tests/0.core/test_core_optimization.py (new) - Optimization with xwnode
xwquery/tests/0.core/test_core_cache_integration.py (new)
```

**Layer 1: Unit Tests**
```
xwquery/tests/1.unit/optimization_tests/ (create directory)
xwquery/tests/1.unit/optimization_tests/runner.py (new)
xwquery/tests/1.unit/optimization_tests/test_query_cache_xwnode.py
xwquery/tests/1.unit/optimization_tests/test_statistics_xwnode.py
xwquery/tests/1.unit/optimization_tests/test_index_manager.py
xwquery/tests/1.unit/optimization_tests/conftest.py
```

**Layer 2: Integration Tests**
```
xwquery/tests/2.integration/test_optimization_end_to_end.py
xwquery/tests/2.integration/test_xwnode_strategy_integration.py
```

**Testing Standards:**
- Mirror source structure in unit tests
- Use hierarchical runners
- 100% test pass requirement
- Performance benchmarks (before/after xwnode integration)
- No forbidden pytest flags

---

## Phase 5: Performance Benchmarking

### 5.1 Create Benchmarks

**Files to Create:**
```
xwquery/benchmarks/benchmark_cache_xwnode.py (~150 LOC)
xwquery/benchmarks/benchmark_statistics_xwnode.py (~150 LOC)
xwquery/benchmarks/BENCHMARK_RESULTS.md (~200 LOC)
```

**Benchmark Scenarios:**
- Cache: Compare OrderedDict vs LRU_CACHE vs LSM_TREE
- Statistics: Compare dict vs HASH_MAP vs HYPERLOGLOG
- Plans: Compare manual tree vs AVL_TREE
- Index checks: Compare dict vs BLOOM_FILTER

**Expected Results:**
- Cache operations: 10-50x faster
- Cardinality: 99% memory reduction
- Index checks: 10x faster negatives
- Statistics: 2-3x faster lookups

### 5.2 Documentation

**File:** `xwquery/benchmarks/BENCHMARK_RESULTS.md`

**Content:**
- Before/after performance comparisons
- Memory usage comparisons
- Code complexity reduction
- Alignment with Performance priority (#4)

---

## Phase 6: Integration & Validation

### 6.1 Dependency Management

**Files to Update:**
```
xwquery/pyproject.toml
xwquery/requirements.txt
xwquery/src/exonware/xwquery/__init__.py
```

**Requirements (GUIDELINES_DEV.md):**
- Add `exonware-xwnode>=0.0.1.27` to dependencies
- Support 3 installation modes (lite/lazy/full)
- Add lazy install configuration: `config_package_lazy_install_enabled("xwquery")`
- No try/except for imports
- Standard imports only

**pyproject.toml:**
```toml
[project]
dependencies = [
    "exonware-xwsystem>=0.0.1",
    "exonware-xwnode>=0.0.1.27",  # NEW: For optimization strategies
]

[project.optional-dependencies]
lazy = [
    "exonware-xwsystem[lazy]>=0.0.1",
    "exonware-xwnode[lazy]>=0.0.1.27",
]

full = [
    # ... all optional dependencies ...
]
```

**__init__.py (line ~84):**
```python
# Lazy installation configuration
from exonware.xwsystem.utils.lazy_discovery import config_package_lazy_install_enabled
config_package_lazy_install_enabled("xwquery")
```

### 6.2 Backward Compatibility

**Requirements:**
- Keep old implementations as fallback (optional)
- Add `use_xwnode: bool = True` parameter to enable/disable
- Gradual migration strategy
- No breaking changes

**Implementation:**
```python
class QueryCache:
    """Query cache with xwnode integration."""
    
    def __init__(self, max_size=1000, use_xwnode: bool = True):
        if use_xwnode:
            # New: xwnode LRU_CACHE
            self._cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=max_size)
        else:
            # Old: OrderedDict (fallback)
            self._cache = OrderedDict()
```

### 6.3 Version Updates

**Files to Update:**
```
xwquery/src/exonware/xwquery/version.py
xwquery/README.md
xwnode/src/exonware/xwnode/version.py
xwnode/README.md
```

**Version Changes (GUIDELINES_DEV.md):**
- xwnode: `0.0.1.27` → `0.0.1.28` (5 new strategies)
- xwquery: `0.0.1.5` → `0.0.1.6` (xwnode integration)
- No automatic version changes
- User-specified versions preserved

---

## Implementation Priority & Timeline

### Week 1: xwnode - Critical Strategies
**Days 1-2:** LRU_CACHE strategy
- Implement strategy (~250 LOC)
- Write tests (~150 LOC)
- Update registry and exports

**Days 3-4:** HISTOGRAM strategy
- Implement strategy (~200 LOC)
- Write tests (~120 LOC)
- Integration with statistics

**Day 5:** Testing and documentation
- Run full test suite
- Update xwnode README
- Create NEW_STRATEGIES.md

### Week 2: xwquery - Refactor to Use xwnode
**Days 1-2:** Query cache refactor
- Replace OrderedDict with LRU_CACHE
- Update tests
- Benchmark performance

**Days 3-4:** Statistics manager refactor
- Replace dicts with HASH_MAP
- Add HYPERLOGLOG for cardinality
- Update tests

**Day 5:** Integration testing
- End-to-end optimization tests
- Performance benchmarks
- Documentation updates

### Week 3: Additional Strategies & Polish
**Days 1-2:** T_DIGEST strategy (high priority)
- Implement in xwnode
- Integrate with statistics manager
- Tests and benchmarks

**Days 3-4:** RANGE_MAP and CIRCULAR_BUFFER (nice-to-have)
- Implement if time permits
- Lower priority

**Day 5:** Final validation
- Full test suite (all layers)
- Documentation review
- Performance benchmarking report

---

## Code Quality Standards (GUIDELINES_DEV.md)

### Naming Conventions
- **Libraries:** xwnode, xwquery (lowercase)
- **Classes:** LRUCacheStrategy, XWNode (CapWord)
- **Interfaces:** INodeStrategy (I prefix)
- **Abstract classes:** ANodeStrategy (A prefix)
- **Files:** lru_cache.py, query_cache.py (snake_case)

### Module Organization
**REQUIRED files at strategy root:**
1. `contracts.py` - Interfaces (NOT protocols.py)
2. `base.py` - Abstract classes (extend contracts)
3. `defs.py` - Enums and constants
4. Implementation files - Concrete strategies

### Design Patterns
- **Strategy Pattern:** All node strategies are interchangeable
- **Facade Pattern:** XWNode provides unified interface
- **Factory Pattern:** StrategyRegistry creates strategies
- **Registry Pattern:** Strategy registration and lookup

### File Path Comments
**MANDATORY: All files MUST include path comment at top:**
```python
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/lru_cache.py

LRU Cache Strategy Implementation
...
"""
```

---

## Testing Standards (GUIDELINES_TEST.md)

### 4-Layer Hierarchy
1. **0.core/** - Fast, high-value tests (< 30s total)
2. **1.unit/** - Component tests mirroring src structure
3. **2.integration/** - Cross-module scenarios
4. **3.advance/** - Production excellence (v1.0.0+, optional now)

### Hierarchical Runners
- `tests/runner.py` - Main orchestrator
- `tests/0.core/runner.py` - Core layer runner
- `tests/1.unit/runner.py` - Unit orchestrator
- `tests/1.unit/nodes_tests/runner.py` - Module runner
- All runners generate `runner_out.md`

### Testing Requirements
- **100% pass rate** (no rigged tests)
- **Fix root causes** (no workarounds)
- **Stop on first failure** (`-x` or `--maxfail=1`)
- **No forbidden flags** (`--disable-warnings`, `--tb=no`, etc.)
- **Proper markers** (`xwnode_core`, `xwnode_unit`, etc.)
- **Comprehensive coverage** (≥80% for changed files)

### Forbidden Practices
❌ Never use `pass` to silence errors  
❌ Never use `--disable-warnings`  
❌ Never use `--maxfail=10`  
❌ Never skip tests with `@pytest.mark.skip`  
❌ Never rig tests to pass  
❌ Never remove features to fix bugs  

### Required Practices
✅ Fix root causes following 5 priorities  
✅ Add regression tests  
✅ Document WHY fixes were needed  
✅ Use specific exception types  
✅ Preserve all existing features  

---

## Success Criteria

### xwnode (Phase 1)
- [ ] 5 new strategies implemented
- [ ] All strategies registered in StrategyRegistry
- [ ] 100% test pass rate (core + unit)
- [ ] Documentation complete
- [ ] No linting errors
- [ ] Version updated to 0.0.1.28

### xwquery (Phase 2)
- [ ] QueryCache using LRU_CACHE or LSM_TREE
- [ ] StatisticsManager using HASH_MAP + HYPERLOGLOG
- [ ] Execution plans using tree strategies (optional)
- [ ] IndexManager using B_PLUS_TREE + BLOOM_FILTER
- [ ] 100% test pass rate (all layers)
- [ ] Performance improvement documented
- [ ] Version updated to 0.0.1.6

### Performance Goals
- [ ] Cache operations: 10-50x faster
- [ ] Statistics lookup: 2-3x faster
- [ ] Cardinality estimation: 99% memory reduction
- [ ] Index checks: 10x faster (Bloom filter)
- [ ] Code reduction: 30-40% less boilerplate

### Documentation
- [ ] All new strategies documented
- [ ] Integration guide complete
- [ ] Performance benchmarks published
- [ ] WHY explanations for all decisions
- [ ] Examples for all use cases

---

## Risk Mitigation

### Risks
1. **Breaking changes** - Refactoring may break existing code
2. **Performance regression** - New code might be slower
3. **Complexity** - Additional dependencies
4. **Testing effort** - Comprehensive testing required

### Mitigation
1. **Backward compatibility** - Keep old implementations as fallback
2. **Benchmarking** - Measure before/after performance
3. **Gradual migration** - Optional `use_xwnode` parameter
4. **Comprehensive testing** - 4-layer test hierarchy

---

## Alignment Checklist

### GUIDELINES_DEV.md Compliance
- [x] Follow 5 priorities (Security, Usability, Maintainability, Performance, Extensibility)
- [x] Use contract-base-facade pattern
- [x] Never reinvent wheel (reuse xwnode strategies)
- [x] File path comments at top
- [x] Proper naming conventions
- [x] 3 installation modes (lite/lazy/full)
- [x] No try/except for imports
- [x] Fix root causes only
- [x] Preserve all features

### GUIDELINES_TEST.md Compliance
- [x] 4-layer test hierarchy (0.core, 1.unit, 2.integration, 3.advance)
- [x] Hierarchical runners
- [x] Mirror source structure in unit tests
- [x] 100% pass requirement
- [x] No rigged tests
- [x] Stop on first failure (`-x`)
- [x] No forbidden pytest flags
- [x] Markdown output files
- [x] Proper markers

---

## Deliverables Summary

### New Files (~2,850 LOC)
**xwnode:**
- 5 strategy implementations (~1,020 LOC)
- 5 unit test files (~620 LOC)
- 2 core test files (~100 LOC)
- 3 documentation files (~750 LOC)

**xwquery:**
- 1 new component (IndexManager) (~200 LOC)
- 4 refactored files (~-200 LOC reduction)
- 4 test files (~370 LOC)
- 2 documentation files (~600 LOC)

### Modified Files
- xwnode: 4 files (defs.py, __init__.py, registry.py, README.md)
- xwquery: 6 files (all optimization module files)
- Both: version.py, requirements.txt, pyproject.toml

### Documentation
- 8 new/updated documentation files
- README updates for both libraries
- Comprehensive integration guide
- Performance benchmark report

---

## Next Steps After Approval

1. **Phase 1:** Implement xwnode strategies (Week 1)
2. **Phase 2:** Refactor xwquery (Week 2)
3. **Phase 3:** Additional strategies (Week 3)
4. **Testing:** Comprehensive validation throughout
5. **Documentation:** Complete as features are added
6. **Benchmarking:** Measure improvements
7. **Review:** Final quality check against guidelines

---

*This plan strictly adheres to GUIDELINES_DEV.md and GUIDELINES_TEST.md for production-grade implementation.*

