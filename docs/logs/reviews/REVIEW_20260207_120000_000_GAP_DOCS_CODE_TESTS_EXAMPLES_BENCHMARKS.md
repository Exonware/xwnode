# Review: xwnode — Documentation vs Codebase vs Tests vs Examples vs Benchmarks (Gap Analysis)

**Date:** 07-Feb-2026 12:00:00.000  
**Project:** xwnode (exonware-xwnode)  
**Artifact type:** Documentation (cross-dimension alignment: Code, Testing, Benchmark, Examples)  
**Scope:** xwnode only. Five dimensions: Documentation, Codebase, Tests, Examples, Benchmarks.  
**Producing guide:** [GUIDE_35_REVIEW.md](../../../../docs/guides/GUIDE_35_REVIEW.md)

---

## Purpose

This report checks the **gap** between documentation, codebase, tests, examples, and benchmarks for **xwnode** using GUIDE_35_REVIEW’s six categories. It answers: Are docs in sync with code? Are examples linked and runnable? Are benchmarks documented and logged? Are tests aligned with REF_51 and code paths?

---

## Summary

**Pass with comments.** xwnode has strong coverage across all five dimensions: full REF set (REF_01_REQ through REF_54_BENCH), 4-layer tests (0.core–3.advance), rich `examples/` and `benchmarks/`, and a large codebase (174+ files under `src/exonware/xwnode`). **Gaps:** (1) **Documentation ↔ Examples:** INDEX and GUIDE_01_USAGE do not list or link specific examples (only “repo `examples/`”); (2) **Documentation ↔ Benchmarks:** REF_54_BENCH does not point to repo `benchmarks/` or `benchmarks/README.md`; no `docs/logs/benchmarks/` INDEX or BENCH_* logs; (3) **REF_15_API ↔ Code:** REF_15 is a short summary; full API is in `_archive/API_REFERENCE.md` — risk of drift if code changes and archive is not updated; (4) **Root .md files:** INSTALL_DEPS.md, MIGRATE_FEATURE_VERIFICATION.md at repo root (GUIDE_41_DOCS prefers only README at root). No blocking critical issues.

---

## Dimension Overview (xwnode)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Documentation** | ✅ Strong | REF_01_REQ, REF_11–22, REF_35, REF_51, REF_54; INDEX, GUIDE_01_USAGE, MASTER_INDEX; many supporting docs in docs/ and _archive/ |
| **Codebase** | ✅ Strong | src/exonware/xwnode (174+ .py); XWNode, XWEdge, XWFactory, XWGraphManager, create_with_preset, from_native in __all__; 57+ node, 28+ edge strategies |
| **Tests** | ✅ Strong | tests/0.core (105 files), 1.unit (many), 2.integration (15), 3.advance (13); REF_51_TEST describes layers and runner |
| **Examples** | ✅ Present, 🟡 Linkage | examples/ (82 files: db_example, x5, demos, SQL); GUIDE_01_USAGE says “Examples: repo examples/” with no per-example links; INDEX has no Examples section |
| **Benchmarks** | ✅ Present, 🟡 Docs/logs | benchmarks/ (benchmark_*.py, baseline JSONs, README); REF_54_BENCH exists but does not link to benchmarks/ or benchmarks/README; no docs/logs/benchmarks/ INDEX or BENCH_* run logs |

---

## Critical issues

- **None blocking.**
- **Minor:** Root-level INSTALL_DEPS.md and MIGRATE_FEATURE_VERIFICATION.md (GUIDE_41_DOCS: only README at root; other .md under docs/). Recommend move to docs/ or document as intentional exception.

---

## Improvements

- **Documentation ↔ Examples:** Add an **Examples** section to [INDEX.md](../../INDEX.md) and optionally to [GUIDE_01_USAGE.md](../../GUIDE_01_USAGE.md) listing key examples (e.g. `examples/db_example/`, `examples/x5/`, `examples/enhanced_xnode_demo.py`) with one-line descriptions and paths. This closes the discoverability gap.
- **Documentation ↔ Benchmarks:** In [REF_54_BENCH.md](../../REF_54_BENCH.md), add a line linking to repo `benchmarks/` and [benchmarks/README.md](../../../benchmarks/README.md) (script usage, output format). Optionally add `docs/logs/benchmarks/` and an INDEX.md for future BENCH_* run logs (GUIDE_54_BENCH).
- **REF_15_API ↔ Code:** Either (a) expand REF_15_API with a concise but complete list of public entry points (from `__all__` and facade), or (b) keep REF_15 as summary and add a “Full reference: _archive/API_REFERENCE.md; keep in sync on API changes” note so reviewers know to update the archive when the public API changes.
- **Root .md:** Move INSTALL_DEPS.md and MIGRATE_FEATURE_VERIFICATION.md to docs/ (e.g. docs/INSTALL_DEPS.md) and update any references, or add a one-line in REF_35 or INDEX explaining why they remain at root.

---

## Optimizations

- **Redundant docs:** docs/ contains many status/optimization/session reports (e.g. OPTIMIZATION_*, PERFORMANCE_*, SESSION_*, FINAL_*). Consider moving historical or one-off reports to _archive/ and keeping INDEX focused on REF_*, GUIDE_01_USAGE, and current evidence (changes/, logs/) so the gap between “documented surface” and “code” stays clear.
- **Benchmark logs:** benchmarks/ produces JSON baselines; REF_54_BENCH says “Evidence: docs/logs/ (benchmarks)”. There is no docs/logs/benchmarks/ INDEX or BENCH_*.md today. Creating docs/logs/benchmarks/INDEX.md (and logging future runs there) would align with GUIDE_54_BENCH and improve traceability.

---

## Missing features / alignment

| Gap | Observation | Recommendation |
|-----|-------------|----------------|
| **Docs ↔ Examples** | Examples exist and are runnable but INDEX and GUIDE_01_USAGE do not list them. | Add Examples row/section to INDEX; add 2–3 example links to GUIDE_01_USAGE. |
| **Docs ↔ Benchmarks** | REF_54_BENCH does not reference benchmarks/ or benchmarks/README; no benchmark run logs under docs/logs/benchmarks/. | Link REF_54_BENCH to benchmarks/ and benchmarks/README; add docs/logs/benchmarks/ and INDEX when runs are logged. |
| **REF_15 ↔ Code** | REF_15 is a short summary; full API in _archive/API_REFERENCE. | Keep REF_15 as contract; ensure _archive/API_REFERENCE is updated on API changes, or fold a minimal full list into REF_15. |
| **Code ↔ Tests** | 4-layer suite present and aligned with REF_51_TEST. | No gap; maintain alignment when adding new strategies or entry points. |
| **Examples ↔ Tests** | examples/ are not systematically run as tests. | Optional: add one smoke test or “example as test” (e.g. run one db_example or x5 path) in 2.integration to guard against breakage. |

---

## Compliance & standards

- **GUIDE_41_DOCS:** Only README at root — **minor gap:** INSTALL_DEPS.md, MIGRATE_FEATURE_VERIFICATION.md at root.
- **GUIDE_51_TEST:** 0.core–3.advance present; REF_51_TEST documents layers and runner — **compliant.**
- **GUIDE_54_BENCH:** REF_54_BENCH present; benchmarks/ and README exist — **partial:** REF_54 should link to benchmarks/; docs/logs/benchmarks/ and run logs optional but recommended.
- **GUIDE_35_REVIEW:** This report follows the six-category template and is stored under docs/logs/reviews/.

---

## Traceability

- **Requirements:** [REF_01_REQ.md](../../REF_01_REQ.md) (14/14); REF_22, REF_13, REF_14, REF_15, REF_21, REF_51, REF_54 sourced from REF_01_REQ.
- **This report:** [REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md](REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md); can be linked from [REF_35_REVIEW.md](../../REF_35_REVIEW.md) under “Missing vs Guides” or “Next steps” as “Gap (docs/code/tests/examples/benchmarks) review”.
- **Ecosystem:** Repo-level gap report: [REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md](../../../../docs/logs/reviews/REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md) (covers all projects; this file is xwnode-only).

---

## Next steps (recommended order)

1. Add **Examples** section to INDEX and 2–3 example links to GUIDE_01_USAGE.
2. Update **REF_54_BENCH** to link to `benchmarks/` and `benchmarks/README.md`.
3. Create **docs/logs/benchmarks/** and INDEX.md (placeholder or first BENCH_* when next run is logged).
4. Move **root .md** (INSTALL_DEPS, MIGRATE_FEATURE_VERIFICATION) to docs/ or document exception.
5. (Optional) Add one **example-as-test** or smoke test in tests/2.integration that runs a representative example.
6. On **API changes**, update REF_15 and/or _archive/API_REFERENCE so docs stay in sync with code.

---

*Per GUIDE_35_REVIEW. Artifact type: Documentation with cross-dimension alignment (Code, Testing, Benchmark, Examples). Project: xwnode only.*
