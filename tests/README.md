# xwnode tests

Four layers: core (fast smoke), unit (mirrors `src`), integration (scenarios), advance (security/usability/maintainability/performance/extensibility).

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com

## Run

```bash
python tests/runner.py
python tests/runner.py --core
python tests/runner.py --unit
python tests/runner.py --integration
python tests/runner.py --advance
```

Advance filters: `--security`, `--usability`, `--maintainability`, `--performance`, `--extensibility`.

## Layout

- `0.core/` - critical path, target &lt; ~30s total for the layer
- `1.unit/` - mirrors `src/exonware/xwnode/`
- `2.integration/` - cross-module scenarios
- `3.advance/` - deeper quality gates (see markers in REF_51_TEST)

## pytest

```bash
pytest
pytest -m xwnode_core -q
pytest tests/0.core/test_all_node_strategies.py
pytest --cov=exonware.xwnode --cov-report=html
```

## Adding tests

Pick the layer, mirror paths for unit tests, add `@pytest.mark.xwnode_*` markers per [docs/REF_51_TEST.md](../docs/REF_51_TEST.md).

## References

- [docs/REF_51_TEST.md](../docs/REF_51_TEST.md)
- [https://docs.pytest.org](https://docs.pytest.org)
