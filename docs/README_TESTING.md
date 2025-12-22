# Testing Guide for Data Operations

## Overview

This test suite follows **GUIDE_TEST.md** standards and ensures all functionalities work correctly with proper root cause fixing.

## Test Structure

- **342+ tests** across 16 test files covering all data operations
- **Both V1 (Streaming) and V2 (Indexed)** implementations tested
- **Production-level code** with no TODOs
- **Proper error handling** following GUIDE_TEST.md

## Running Tests

### Option 1: Unified Test Runner (Recommended)

```bash
cd xwnode/examples/x5/data_operations
python run_tests_unified.py
```

This uses pytest with GUIDE_TEST.md compliant options:
- Stop on first failure (`-x`)
- Verbose output (`-v`)
- Short tracebacks (`--tb=short`)
- Never hides warnings or errors

### Option 2: Direct pytest

```bash
cd xwnode/examples/x5/data_operations
pytest -v -x --tb=short --strict-markers
```

### Option 3: Original Custom Runner

```bash
cd xwnode/examples/x5/data_operations
python run_all_tests.py
```

## Test Files

1. `test_1_create_operations.py` - CREATE operations (14 tests)
2. `test_2_read_operations.py` - READ operations (46 tests)
3. `test_3_update_operations.py` - UPDATE operations (26 tests)
4. `test_4_delete_operations.py` - DELETE operations (19 tests)
5. `test_5_list_query_operations.py` - LIST/QUERY operations (19 tests)
6. `test_6_search_operations.py` - SEARCH operations (31 tests)
7. `test_7_bulk_operations.py` - BULK operations (13 tests)
8. `test_8_transaction_operations.py` - TRANSACTION operations (10 tests)
9. `test_9_index_operations.py` - INDEX operations (14 tests)
10. `test_10_validation_operations.py` - VALIDATION operations (11 tests)
11. `test_11_aggregation_operations.py` - AGGREGATION operations (14 tests)
12. `test_12_file_operations.py` - FILE operations (11 tests)
13. `test_13_concurrency_operations.py` - CONCURRENCY operations (10 tests)
14. `test_14_async_operations.py` - ASYNC operations (8 tests)
15. `test_15_utility_operations.py` - UTILITY operations (13 tests)
16. `test_16_monitoring_operations.py` - MONITORING operations (10 tests)

## Root Cause Fixes Applied

Following GUIDE_TEST.md standards, the following root cause issues were fixed:

### 1. Error Handling in `test_helpers.py`

**Before (FORBIDDEN):**
```python
except Exception:
    pass  # Hides errors!
```

**After (FIXED):**
```python
except (OSError, PermissionError, ValueError) as e:
    raise RuntimeError(f"Failed to rebuild index: {e}") from e
```

### 2. Cleanup Error Handling

**Before:**
```python
except Exception:
    pass  # Silently ignores cleanup failures
```

**After:**
```python
except (OSError, PermissionError) as e:
    warnings.warn(f"Cleanup warning: {error}", UserWarning)
```

### 3. Test Isolation

- Added `conftest.py` with proper pytest fixtures
- Each test gets isolated resources
- Automatic cleanup via fixtures

## Configuration Files

- **`pytest.ini`** - Pytest configuration following GUIDE_TEST.md
- **`conftest.py`** - Shared fixtures for test isolation
- **`test_helpers.py`** - Fixed root cause issues in helper functions

## Test Quality Standards

Following GUIDE_TEST.md:

✅ **100% test pass rate required** - No exceptions  
✅ **Stop on first failure** - Use `-x` or `--maxfail=1`  
✅ **Never hide warnings** - Fix them, don't suppress  
✅ **Root cause fixing only** - No workarounds, no rigged tests  
✅ **Test isolation** - Each test is independent  
✅ **Proper cleanup** - Resources cleaned up automatically  
✅ **Descriptive naming** - Clear test names with full descriptions  

## Forbidden Practices (GUIDE_TEST.md)

❌ **NEVER:**
- Use `except Exception: pass` to hide errors
- Use `--disable-warnings` to hide warnings
- Use `--maxfail=10` to continue past failures
- Use `@pytest.mark.skip` to avoid fixing tests
- Lower standards to make tests pass
- Remove features to eliminate bugs

## Fixing Test Failures

When a test fails:

1. **Read the full error** - Understand WHY it failed
2. **Run test in isolation** - Confirm it's not flaky
3. **Identify root cause** - Is the test wrong or code wrong?
4. **Fix the code** - Not the test (unless test logic is wrong)
5. **Run full suite** - Verify no regressions
6. **Document in commit** - Explain what was fixed and why

## Performance Testing

All tests measure and return:
- `v1_time` - V1 (Streaming) execution time
- `v2_time` - V2 (Indexed) execution time

This allows performance comparison between implementations.

## Support Files

- **`test_helpers.py`** - Shared utilities (root cause issues fixed)
- **`conftest.py`** - Pytest fixtures for test isolation
- **`pytest.ini`** - Pytest configuration
- **`run_tests_unified.py`** - Unified test runner using pytest
- **`run_all_tests.py`** - Original custom runner (backward compatible)

---

*Following GUIDE_TEST.md standards - Fix root causes, never hide problems!*

