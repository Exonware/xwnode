<!-- docs/REF_54_BENCH.md (output of GUIDE_54_BENCH) -->
# xwnode — Benchmark SLAs

**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8 (performance)

Benchmark SLAs and status (output of GUIDE_54_BENCH). Evidence: repo **`benchmarks/`** (campaigns), [docs/logs/benchmarks/INDEX.md](logs/benchmarks/INDEX.md) (how `docs/logs` relates to campaigns), [docs/logs/benchmarks_logs/](logs/benchmarks_logs/) (run-log index).

**Benchmark scripts and logs:**
- **Scripts and usage:** repo [benchmarks/](../benchmarks/), [campaign README](../benchmarks/20260321-benchmark%20xwnode%20consolidated/README.md) (e.g. `benchmark_all_strategies.py`, output format, baseline JSONs under campaign `data/`).
- **Run logs (BENCH_*.md):** under each campaign’s `benchmarks/` folder, e.g. [20260321-benchmark xwnode consolidated/benchmarks/](../benchmarks/20260321-benchmark%20xwnode%20consolidated/benchmarks/). *`docs/logs/benchmarks_logs/` indexes runs; canonical files live in `benchmarks/` per GUIDE_54_BENCH.*

**Historical (from archive):** Baseline methodology: 1k/100 iters (nodes/edges), warmup 100/10; put/get/delete/size/iteration. LRU_CACHE path fix ~6800x (1576ms→0.23ms); cache infra and eviction phases. See [BENCH_20260207_ARCHIVE_BASELINE_AND_LRU.md](../benchmarks/20260321-benchmark%20xwnode%20consolidated/benchmarks/BENCH_20260207_ARCHIVE_BASELINE_AND_LRU.md) and [REVIEW_20260207_ARCHIVE_CONSOLIDATION.md](logs/reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md).

---

*Per GUIDE_00_MASTER and GUIDE_54_BENCH.*
