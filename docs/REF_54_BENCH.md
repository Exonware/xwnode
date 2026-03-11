<!-- docs/REF_54_BENCH.md (output of GUIDE_54_BENCH) -->
# xwnode — Benchmark SLAs

**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8 (performance)

Benchmark SLAs and status (output of GUIDE_54_BENCH). Evidence: [docs/logs/benchmarks_logs/](logs/benchmarks_logs/) (run logs), repo **benchmarks/**.

**Benchmark scripts and logs:**
- **Scripts and usage:** repo [benchmarks/](../benchmarks/), [benchmarks/README.md](../benchmarks/README.md) (e.g. `benchmark_all_strategies.py`, output format, baseline JSONs).
- **Run logs:** [logs/benchmarks_logs/](logs/benchmarks_logs/) (BENCH_*.md when runs are logged per GUIDE_54_BENCH). *Note: `docs/logs/benchmarks` is an existing file; run logs live in `benchmarks_logs/`.*

**Historical (from archive):** Baseline methodology: 1k/100 iters (nodes/edges), warmup 100/10; put/get/delete/size/iteration. LRU_CACHE path fix ~6800x (1576ms→0.23ms); cache infra and eviction phases. See [logs/benchmarks_logs/BENCH_20260207_ARCHIVE_BASELINE_AND_LRU.md](logs/benchmarks_logs/BENCH_20260207_ARCHIVE_BASELINE_AND_LRU.md) and [REVIEW_20260207_ARCHIVE_CONSOLIDATION.md](logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md).

---

*Per GUIDE_00_MASTER and GUIDE_54_BENCH.*
