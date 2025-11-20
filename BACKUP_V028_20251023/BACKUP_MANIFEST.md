# Backup Manifest - v0.0.1.28

**Backup Date:** 23-Oct-2025  
**Purpose:** Backup before implementing async-first architecture (v0.0.1.30)  
**Source Version:** 0.0.1.28

## Backed Up Files

### Node Strategy Files (60 files)
- `nodes_strategies/contracts.py` - Core interface definitions
- `nodes_strategies/base.py` - Abstract base class
- `nodes_strategies/*.py` - All 58 concrete strategy implementations

### Edge Strategy Files (1 file)
- `edges_strategies/base.py` - Edge strategy base class

### Parent Level Files (1 file)
- `parent_contracts.py` - Parent-level contracts (copied from `src/exonware/xwnode/contracts.py`)

## Total Files Backed Up: 62

## Restoration Instructions

If rollback is needed:

```bash
# From xwnode directory
cd D:\OneDrive\DEV\exonware\xwnode

# Restore node strategies
xcopy /Y BACKUP_V028_20251023\nodes_strategies\*.py src\exonware\xwnode\nodes\strategies\

# Restore edge strategies  
xcopy /Y BACKUP_V028_20251023\edges_strategies\base.py src\exonware\xwnode\edges\strategies\

# Restore parent contracts
xcopy /Y BACKUP_V028_20251023\parent_contracts.py src\exonware\xwnode\contracts.py

# Clear Python cache
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc
```

## Verification

After restoration, verify with:
```bash
python tests/runner.py --core
```

Expected: All tests pass with v0.0.1.28 functionality restored.

