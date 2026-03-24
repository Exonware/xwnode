# Proposed Codebase Actions — From Gap Reports (xwnode + Ecosystem)

**Source reports:**
- [xwnode gap report](REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md) (docs/code/tests/examples/benchmarks)
- [Ecosystem gap report](../../../../docs/logs/reviews/REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md)

**Date:** 07-Feb-2026

---

## xwnode — Concrete codebase actions

| # | Action | Target / path | Source | Status |
|---|--------|----------------|--------|--------|
| 1 | Add **Examples** section to INDEX | `docs/INDEX.md` | xwnode report (Improvements, Next steps); ecosystem (Next steps 1) | Done |
| 2 | Add **2–3 example links** to GUIDE_01_USAGE | `docs/GUIDE_01_USAGE.md` | xwnode report (Improvements, Next steps 1) | Done |
| 3 | In **REF_54_BENCH**, link to `benchmarks/` and `benchmarks/README.md` | `docs/REF_54_BENCH.md` | xwnode report (Improvements, Next steps 2); ecosystem (Next steps 4) | Done |
| 4 | Create **docs/logs/benchmarks/** and **INDEX.md** (placeholder) | `docs/logs/benchmarks/INDEX.md` + former `docs/logs/benchmarks` file → `benchmarks/.../BENCH_20251204_014728_V1_VS_V2_PERFORMANCE.md` | xwnode report (Optimizations, Next steps 3); ecosystem (Next steps 4) | Done |
| 5 | **Root .md:** Move INSTALL_DEPS.md and MIGRATE_FEATURE_VERIFICATION.md to docs/ (or document exception in INDEX/REF_35) | `docs/INSTALL_DEPS.md`, `docs/MIGRATE_FEATURE_VERIFICATION.md` | xwnode report (Critical minor, Improvements, Next steps 4); ecosystem (Compliance) | Done |
| 6 | In **REF_15_API**, add note: full reference in _archive/API_REFERENCE.md; keep in sync on API changes | `docs/REF_15_API.md` | xwnode report (Improvements, REF_15 ↔ Code); ecosystem (Docs ↔ Code) | Done |
| 7 | **(Optional)** Add one **example-as-test** or smoke test in tests/2.integration (e.g. run one db_example or enhanced_xnode_demo path) | `tests/2.integration/` | xwnode report (Missing features, Next steps 5); ecosystem (Examples ↔ Tests) | Optional |

---

## Ecosystem (other projects) — Reference only

| # | Action | Scope | Source |
|---|--------|--------|--------|
| E1 | Add “Examples” to INDEX and GUIDE_01_USAGE | Each project with `examples/` | Ecosystem Next steps 1 |
| E2 | xwchat: Add 1.unit, 2.integration, 3.advance test layers | xwchat | Ecosystem Next steps 2; Critical issues |
| E3 | Six servers: Define one-page scope; add REF_12/13/15/51 and minimal tests | xw*-server | Ecosystem Next steps 3 |
| E4 | REF_54_BENCH + docs/logs/benchmarks/ where bench scripts exist | Projects with bench_* but no REF_54/logs | Ecosystem Next steps 4 |
| E5 | REF_15 ↔ code sync pass | xwquery (post-executor refactor), xwaction, xwschema | Ecosystem Next steps 5; Improvements |

---

## Implementation notes (xwnode)

- **1–2 (Examples):** INDEX gets a new section “Examples” with a table: path, one-line description. GUIDE_01_USAGE replaces the single “Examples: repo examples/.” line with a short table (e.g. db_example, x5, enhanced_xnode_demo).
- **3 (REF_54_BENCH):** Add a “Benchmark scripts and logs” paragraph with links: repo [benchmarks/](../../../benchmarks/), [benchmarks/README.md](../../../benchmarks/README.md) for script usage and output format.
- **4 (logs/benchmarks):** Create `docs/logs/benchmarks/` and `INDEX.md` stating “Benchmark run logs (BENCH_*.md) per GUIDE_54_BENCH. Baseline runs: repo benchmarks/.”
- **5 (Root .md):** Prefer moving the two files to `docs/INSTALL_DEPS.md` and `docs/MIGRATE_FEATURE_VERIFICATION.md`; update any in-repo links. If kept at root, add one line under “Standards” in INDEX or in REF_35: “Root INSTALL_DEPS.md and MIGRATE_FEATURE_VERIFICATION.md retained by exception; see INDEX.”
- **6 (REF_15):** Append or insert after the “Core” line: “Full reference: [_archive/API_REFERENCE.md](_archive/API_REFERENCE.md). On API changes, update REF_15 and/or the archive so docs stay in sync with code.”
- **7 (Example-as-test):** New file e.g. `tests/2.integration/test_example_smoke.py` that imports and runs a minimal path from one example (e.g. XWNode.from_native + put/get) or subprocess-runs one example script; skip if fragile or env-dependent.

---

*Derived from REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md (xwnode and ecosystem).*
