# Documentation index — xwnode

**Last Updated:** 07-Feb-2026

Navigation hub for xwnode docs. Per GUIDE_41_DOCS and GUIDE_00_MASTER.

## Requirements (source of truth)

| Document | Purpose | Producing guide |
|----------|---------|------------------|
| [REF_01_REQ.md](REF_01_REQ.md) | **Requirements source** (sponsor + codebase); feeds REF_11, REF_12, REF_13, REF_14, REF_15, REF_21, REF_22 | GUIDE_01_REQ |

## References (REF_*)

| Document | Purpose | Producing guide |
|----------|---------|------------------|
| [REF_11_COMP.md](REF_11_COMP.md) | Compliance stance and standards (from REF_01_REQ sec. 4) | GUIDE_11_COMP |
| [REF_12_IDEA.md](REF_12_IDEA.md) | Idea context and evaluation (from REF_01_REQ sec. 1–2) | GUIDE_12_IDEA |
| [REF_13_ARCH.md](REF_13_ARCH.md) | Architecture, XWQuery (no circular ref) (from REF_01_REQ) | GUIDE_13_ARCH |
| [REF_14_DX.md](REF_14_DX.md) | Developer experience, happy paths (from REF_01_REQ sec. 5–6) | GUIDE_14_DX |
| [REF_15_API.md](REF_15_API.md) | API reference, entry points (from REF_01_REQ sec. 6) | GUIDE_15_API |
| [REF_21_PLAN.md](REF_21_PLAN.md) | Milestones and roadmap (from REF_01_REQ sec. 9) | GUIDE_21_PLAN |
| [REF_22_PROJECT.md](REF_22_PROJECT.md) | Vision, goals, milestones (from REF_01_REQ) | GUIDE_22_PROJECT |
| [REF_35_REVIEW.md](REF_35_REVIEW.md) | Review summary and status | GUIDE_35_REVIEW |
| [REF_51_TEST.md](REF_51_TEST.md) | Test status and coverage (from REF_01_REQ sec. 8) | GUIDE_51_TEST |
| [REF_54_BENCH.md](REF_54_BENCH.md) | Benchmark SLAs (from REF_01_REQ sec. 8) | GUIDE_54_BENCH |

## Usage

| Document | Purpose |
|----------|---------|
| [GUIDE_01_USAGE.md](GUIDE_01_USAGE.md) | How to use xwnode (GUIDE_41_DOCS) |

## Examples

| Path | Description |
|------|--------------|
| [examples/db_example/](../../examples/db_example/) | DB-style examples and benchmarks (x1–x6 file-backed, run_all_benchmarks) |
| [examples/x5/](../../examples/x5/) | Data operations, benchmarks, and comparison (e.g. benchmark_all_tests, json_libs) |
| [examples/](../../examples/) | Other demos: enhanced_xnode_demo.py, enhanced_strategy_demo.py, sql demos |

## Other

| Path | Purpose |
|------|---------|
| [_archive/](_archive/) | Legacy docs; value moved 07-Feb-2026 to REF_*, GUIDE_01_USAGE, [logs/](logs/) (see [logs/ARCHIVE_VALUE_CAPTURE_XWNODE.md](logs/ARCHIVE_VALUE_CAPTURE_XWNODE.md)) |
| [changes/](changes/) | CHANGE_* (implementation change notes) |

## Evidence (logs)

| Location | Content |
|----------|---------|
| [logs/reviews/](logs/reviews/) | REVIEW_* (GUIDE_35_REVIEW); [REVIEW_*_REQUIREMENTS.md](logs/reviews/REVIEW_20260207_160000_000_REQUIREMENTS.md) — REF_01_REQ alignment; [REVIEW_*_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md](logs/reviews/REVIEW_20260207_120000_000_GAP_DOCS_CODE_TESTS_EXAMPLES_BENCHMARKS.md) — docs/code/tests/examples/benchmarks gap |
| [logs/benchmarks_logs/](logs/benchmarks_logs/) | BENCH_* (benchmark run logs per GUIDE_54_BENCH); [INDEX.md](logs/benchmarks_logs/INDEX.md) |
| [logs/tests/](logs/tests/) | TEST_* (test run evidence) |

## Standards

- Only `README.md` at repo root; all other Markdown under `docs/` (GUIDE_41_DOCS).
- **docs/ root:** Only standard docs: REF_* (REF_01_REQ through REF_54_BENCH), INDEX.md, MASTER_INDEX.md, GUIDE_01_USAGE.md. Everything else lives in _archive/, changes/, or logs/.

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS.*
