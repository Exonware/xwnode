# xwnode — Test Status and Coverage

**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8–9, [REF_22_PROJECT.md](REF_22_PROJECT.md)

Test status and coverage (output of GUIDE_51_TEST). Evidence: repo `tests/`, docs/logs/tests/. Historical: 4-layer suite (0.core–3.advance); 566/605 core tests passing (Oct 2025); coverage and status from archived TEST_*, README_TESTING consolidated here and in [logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md](logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md).

---

## Definition of done (REF_01_REQ sec. 9)

First milestone DoD: strategies + engine + XWNode facade; put/get/delete/size/iterate and at least one graph path. **Done** per REF_22. Test expectation: 4-layer suite (0.core–3.advance) in place and passing.

---

## Test layers

| Layer | Path | Purpose |
|-------|------|---------|
| 0.core | tests/0.core/ | Node/edge strategies, core COW, graph manager, indexing, analytics |
| 1.unit | tests/1.unit/ | Unit tests for strategies and components |
| 2.integration | tests/2.integration/ | Adaptive strategy, cache, event bus, spatial, xwsystem lazy |
| 3.advance | tests/3.advance/ | Extensibility, security, maintainability, performance, usability |

---

## Running tests

```bash
python tests/runner.py
python tests/runner.py --core
python tests/runner.py --unit
python tests/runner.py --integration
```

---

## Traceability

- **Requirements:** REF_01_REQ sec. 8 (maintainability, 4-layer tests); REF_22 FR-006.
- **Evidence:** [logs/reviews/](logs/reviews/), [logs/tests/](logs/tests/).

---

*Per GUIDE_00_MASTER and GUIDE_51_TEST.*
