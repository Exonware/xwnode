# xwnode Structure Refactoring Plan

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.0.1  
**Generation Date:** 08-Oct-2025

## Current Structure Analysis

### ✅ Already Organized
- `nodes/strategies/` - Node strategy implementations (28 modes)
- `edges/strategies/` - Edge strategy implementations (16 modes)
- `queries/strategies/` - Query strategy implementations (35+ formats)
- `nodes/executors/` - Empty (ready for future)
- `edges/executors/` - Empty (ready for future)
- `queries/executors/` - Empty (ready for future)

### 🔄 Needs Reorganization
- `strategies/` - Root level folder with common utilities that should move to `common/`

## Refactoring Steps

### Phase 1: Create common/ Structure

Create new folder structure:
```
common/
├── __init__.py
├── patterns/              # Design pattern implementations
│   ├── __init__.py
│   ├── flyweight.py      # FROM: strategies/flyweight.py
│   ├── registry.py       # FROM: strategies/registry.py
│   └── advisor.py        # FROM: strategies/advisor.py
├── monitoring/            # Performance and monitoring
│   ├── __init__.py
│   ├── metrics.py        # FROM: strategies/metrics.py
│   ├── performance_monitor.py  # FROM: strategies/performance_monitor.py
│   └── pattern_detector.py     # FROM: strategies/pattern_detector.py
├── management/            # Strategy management
│   ├── __init__.py
│   ├── manager.py        # FROM: strategies/manager.py
│   └── migration.py      # FROM: strategies/migration.py
└── utils/                 # Shared utilities
    ├── __init__.py
    ├── utils.py          # FROM: strategies/utils.py
    └── simple.py         # FROM: strategies/simple.py
```

### Phase 2: File Moves

#### Common Patterns
- `strategies/flyweight.py` → `common/patterns/flyweight.py`
- `strategies/registry.py` → `common/patterns/registry.py`
- `strategies/advisor.py` → `common/patterns/advisor.py`

#### Common Monitoring
- `strategies/metrics.py` → `common/monitoring/metrics.py`
- `strategies/performance_monitor.py` → `common/monitoring/performance_monitor.py`
- `strategies/pattern_detector.py` → `common/monitoring/pattern_detector.py`

#### Common Management
- `strategies/manager.py` → `common/management/manager.py`
- `strategies/migration.py` → `common/management/migration.py`

#### Common Utils
- `strategies/utils.py` → `common/utils/utils.py`
- `strategies/simple.py` → `common/utils/simple.py`

### Phase 3: Import Updates

Update imports in all files:

**Old imports:**
```python
from exonware.xwnode.strategies.flyweight import ...
from exonware.xwnode.strategies.registry import ...
from exonware.xwnode.strategies.manager import ...
```

**New imports:**
```python
from exonware.xwnode.common.patterns.flyweight import ...
from exonware.xwnode.common.patterns.registry import ...
from exonware.xwnode.common.management.manager import ...
```

### Phase 4: Update __init__.py Files

Create/update `__init__.py` in:
- `common/__init__.py`
- `common/patterns/__init__.py`
- `common/monitoring/__init__.py`
- `common/management/__init__.py`
- `common/utils/__init__.py`

### Phase 5: Cleanup

After successful refactoring:
1. Remove empty `strategies/` folder
2. Update main `__init__.py` to export from new locations
3. Run all tests to verify nothing broke
4. Update documentation

## Expected Final Structure

```
xwnode/src/exonware/xwnode/
├── __init__.py
├── base.py
├── config.py
├── contracts.py
├── errors.py
├── facade.py
├── types.py
├── version.py
├── common/                          # NEW: Shared foundation
│   ├── __init__.py
│   ├── patterns/                    # Design patterns
│   │   ├── __init__.py
│   │   ├── flyweight.py
│   │   ├── registry.py
│   │   └── advisor.py
│   ├── monitoring/                  # Monitoring & metrics
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── performance_monitor.py
│   │   └── pattern_detector.py
│   ├── management/                  # Strategy management
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   └── migration.py
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── utils.py
│       └── simple.py
├── nodes/                           # Node domain
│   ├── strategies/                  # ✅ Already organized
│   └── executors/                   # ✅ Ready for implementation
├── edges/                           # Edge domain
│   ├── strategies/                  # ✅ Already organized
│   └── executors/                   # ✅ Ready for implementation
└── queries/                         # Query domain
    ├── strategies/                  # ✅ Already organized
    └── executors/                   # ✅ Ready for implementation
```

## Benefits

1. **Clear Separation**: Domain-specific code isolated (nodes, edges, queries)
2. **Shared Foundation**: Common utilities in `common/`
3. **Easier Navigation**: Find code faster
4. **Better Testing**: Test each domain independently
5. **Scalability**: Easy to add new domains or features
6. **Maintainability**: Clear structure reduces confusion

## Rollback Plan

If issues arise:
1. Git revert to previous commit
2. Or manually reverse file moves
3. Restore old imports

## Testing Strategy

After refactoring:
1. Run all unit tests
2. Run all integration tests
3. Check import statements work
4. Verify facade still works
5. Test each domain independently

## Status

- [x] Phase 1: Analysis complete
- [ ] Phase 2: Create common/ structure
- [ ] Phase 3: Move files
- [ ] Phase 4: Update imports
- [ ] Phase 5: Update __init__.py files
- [ ] Phase 6: Cleanup
- [ ] Phase 7: Testing

---

*This refactoring follows DEV_GUIDELINES.md standards and maintains backward compatibility where possible.*
