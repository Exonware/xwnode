# XWNode Enhancement Plan - Moving Functionality from XWData

## 🎯 Objective

Move subscriptable interface functionality from **xwdata** to **xwnode** following GUIDELINES_DEV.md best practices:
- **Never reinvent the wheel** - Reuse XWNode infrastructure
- **Fix root causes** - Enhance XWNode instead of duplicating logic
- **Production-grade quality** - Clean, maintainable, extensible code
- **Comprehensive testing** - Follow GUIDELINES_TEST.md 4-layer approach

## 📋 Implementation Plan

### Phase 1: Enhance XWNode Facade (xwnode/src/exonware/xwnode/facade.py)

#### 1.1 Add `get_value()` Method ✅
```python
def get_value(self, path: str, default: Any = None) -> Any:
    """Get actual value at path (not ANode wrapper)."""
    result = self.get(path)
    return result.to_native() if result else default
```

#### 1.2 Add Static Path Navigation Helper ✅
```python
@staticmethod
def _navigate_path_from_native(data: Any, path: str, default: Any = None) -> Any:
    """Navigate path in native Python data."""
    # Implementation for handling PersistentNode flattened structures
```

#### 1.3 Add Strategy Detection Utility ✅
```python
def _is_persistent_strategy(self) -> bool:
    """Check if using PersistentNode (COW) strategy."""
    return (hasattr(self._strategy, 'get') and 
            hasattr(self._strategy, 'exists'))
```

#### 1.4 Update `__getitem__` for Value Returns ✅
```python
def __getitem__(self, key: Union[str, int]) -> Any:
    """Get item - returns actual value, not ANode."""
    # Handle both string and int keys
    # Use get_value() to return values
    # Support PersistentNode fallback
```

#### 1.5 Enhance `__contains__` ✅
```python
def __contains__(self, key: Union[str, int]) -> bool:
    """Check if key exists - handles PersistentNode flattened structures."""
    # Use _is_persistent_strategy()
    # Handle fallback to native data
```

#### 1.6 Update `__setitem__` and `__delitem__` ✅
```python
def __setitem__(self, key: Union[str, int], value: Any) -> None:
    """Set item with int/str support."""

def __delitem__(self, key: Union[str, int]) -> None:
    """Delete item with int/str support."""
```

### Phase 2: Simplify XWDataNode (xwdata/src/exonware/xwdata/data/node.py)

#### 2.1 Simplify `get_value_at_path()` ✅
```python
def get_value_at_path(self, path: str, default: Any = None) -> Any:
    """Delegate to XWNode's get_value()."""
    if self._xwnode is not None:
        return self._xwnode.get_value(path, default)
    return self._navigate_simple_path(path, default)
```

#### 2.2 Simplify `__getitem__` ✅
```python
def __getitem__(self, key: str) -> Any:
    """Simply delegate to XWNode."""
    if self._xwnode is not None:
        return self._xwnode[key]
    # Simple fallback
```

#### 2.3 Simplify `__contains__` ✅
```python
def __contains__(self, key: str) -> bool:
    """Simply delegate to XWNode."""
    if self._xwnode is not None:
        return key in self._xwnode
    # Simple fallback
```

#### 2.4 Keep `__setitem__` and `__delitem__` (XWData-specific COW) ✅
- These need to update `self._node` and `self._metadata`
- XWData-specific behavior, not moved to XWNode

### Phase 3: Comprehensive Testing

#### 3.1 XWNode Tests (xwnode/tests/)
- Test `get_value()` method
- Test `__getitem__` with str/int keys and path support
- Test `__contains__` with PersistentNode fallback
- Test `__setitem__` and `__delitem__` with int/str keys

#### 3.2 XWData Tests (xwdata/tests/)
- Test XWDataNode delegation to XWNode
- Test XWData facade integration
- Ensure existing tests still pass

#### 3.3 Integration Tests
- Test full workflow from file loading to subscriptable access
- Test path-based access across both libraries
- Test COW semantics preservation

### Phase 4: Documentation & Summary

#### 4.1 Update Documentation
- Document new XWNode methods
- Update XWDataNode delegation pattern
- Create architecture summary

#### 4.2 Clean Up Debug Files
- Remove temporary debug scripts from sandbox/

## 🏗️ Architecture Benefits

### Before (Current)
```
XWData["key"] → XWDataNode[key] → Complex strategy detection → XWNode or fallback
```

### After (Enhanced)
```
XWData["key"] → XWDataNode[key] → XWNode[key] (handles everything)
```

### Key Improvements
1. **Reusability**: XWNode can be used subscriptably by all libraries
2. **Simplicity**: XWDataNode becomes simpler, just delegates
3. **Maintainability**: Single source of truth for subscriptable logic
4. **Performance**: No duplicate code paths
5. **Extensibility**: Easy to enhance XWNode for all consumers

## 🎯 Success Criteria

- ✅ XWNode supports `node["key"]`, `node["0"]`, `node[0]`
- ✅ XWNode supports path access: `node["users.0.name"]`
- ✅ XWNode handles PersistentNode flattened structures
- ✅ XWDataNode delegates cleanly to XWNode
- ✅ All existing tests pass (100% pass rate)
- ✅ New tests added for enhanced functionality
- ✅ Documentation updated
- ✅ Follows GUIDELINES_DEV.md principles
- ✅ Follows GUIDELINES_TEST.md testing standards

## 📊 Testing Strategy (per GUIDELINES_TEST.md)

### Core Tests (0.core/)
- Basic subscriptable access (fast, high-value)
- Path navigation fundamentals
- PersistentNode fallback basics

### Unit Tests (1.unit/)
- Detailed `get_value()` method tests
- `__getitem__` with all key types
- `__contains__` with all scenarios
- Strategy detection utility tests

### Integration Tests (2.integration/)
- XWData → XWNode delegation flow
- File loading → subscriptable access
- Format conversion → path access

## 🚀 Ready to Implement

Following GUIDELINES_DEV.md:
- Think and design thoroughly ✅ (this plan)
- Production-grade quality ✅ (comprehensive approach)
- Fix root causes ✅ (moving logic to XWNode, not duplicating)
- Never reinvent the wheel ✅ (reusing XWNode)
- Comprehensive testing ✅ (4-layer approach)

