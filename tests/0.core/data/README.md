# SQL to XWQuery conversion test data

Fixtures for converting `.sql` inputs to `.xwquery` expected outputs under `tests/0.core/`.

## Layout

```
data/
├── inputs/     # .sql sources
├── expected/   # expected .xwquery
├── outputs/    # generated during runs (gitignored as appropriate)
└── fixtures/   # shared fixtures
```

## Files

- **test_simple_users** - basic SELECT, WHERE, ORDER BY, LIMIT, comments
- **test_ecommerce_analytics** - CTEs, JOINs, aggregates, windows, CASE

## Run conversion tests

```bash
python -m pytest tests/0.core/test_sql_to_xwquery_file_conversion.py -v
```

## Manual conversion (example)

```python
from pathlib import Path
from exonware.xwnode.strategies.queries.xwquery_strategy import XWQueryScriptStrategy

strategy = XWQueryScriptStrategy()
sql = Path("input.sql").read_text(encoding="utf-8")
xwquery = strategy.parse_script(sql)
Path("output.xwquery").write_text(xwquery, encoding="utf-8")
```

## References

- `xwnode/docs/XWQUERY_SCRIPT.md` (if present)
- `tests/0.core/test_sql_to_xwquery_file_conversion.py`
